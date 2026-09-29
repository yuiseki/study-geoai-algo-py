"""Step 9C: random placement and the current evacuation sites, as baselines for steps 8 and 9.

Case study 002 needs to know how much the optimisation of steps 8 and 9 is
worth. The setting is step 9B's: 108 small areas of Taito City (2020 census),
walks on the network of step 7, the 566 candidate sites (medical facilities
and schools). Two measures of a placement: the mean walk to the nearest open
site (the p-median objective) and the share of residents within 400 m (the
maximal covering objective).

1. For p = 5, 10, 17 and 20: 2,000 random choices of p candidate sites, against
   greedy and the exact optimum of each objective. Where does the optimum sit
   in the random distribution, and how many random draws would it take to do
   as well?
2. The 17 designated emergency evacuation sites the ward has now, against 17
   random candidates and against the optimal 17.

    uv run python -u src/009-C-random-placement/run.py
"""

import importlib.util
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from study_geoai import aoi, cover, facility, features, ksj  # noqa: E402
from study_geoai.db import connect  # noqa: E402

OUT = Path(__file__).parent / "output"
RADIUS = 400.0
PS = (5, 10, 17, 20)
DRAWS = 2000


def _load(name, sub):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).parents[1] / sub / "run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


step7a = _load("step7a", "007-A-dijkstra")
step9a = _load("step9a", "009-A-assignment")


def measures(dist, pop, open_):
    walk = dist[:, open_].min(axis=1)
    return float((walk * pop).sum() / pop.sum()), float(pop[walk <= RADIUS].sum() / pop.sum())


def main():
    con = connect()
    OUT.mkdir(parents=True, exist_ok=True)
    area = aoi.load("taito", con)
    g, nearest = step9a.network(con, area)
    names, pop, area_xy = step9a.small_areas(con, area)
    a_nodes, a_gap = nearest(area_xy)
    sites = []
    for dataset, label in (("P04", "P04_002"), ("P29", "P29_004")):
        sites += (ksj.read(con, area, dataset)
                  .query("s", f"select {label}, st_x(geometry), st_y(geometry) from s").fetchall())  # fmt: skip
    site_xy = features.to_metric(con, [s[1:] for s in sites])
    s_nodes, s_gap = nearest(site_xy)
    dist = step9a.distances(g, a_nodes, a_gap, s_nodes, s_gap).T  # area x site
    shelter_names, shelter_ll = step7a.shelters(con, area)
    h_nodes, h_gap = nearest(features.to_metric(con, shelter_ll))
    hdist = step9a.distances(g, a_nodes, a_gap, h_nodes, h_gap).T
    sets = [np.flatnonzero(dist[:, j] <= RADIUS) for j in range(len(sites))]
    print(f"## taito: {len(names)} small areas, {pop.sum():,.0f} residents, {len(sites)} candidate"
          f" sites, {len(shelter_names)} current evacuation sites")  # fmt: skip

    rng = np.random.default_rng(0)
    draws = {}
    print("\n   p   mean walk (m): random 5% / 50% / 95%   greedy   optimum   optimum beaten by")
    print("       within 400 m:  random 5% / 50% / 95%   greedy   optimum   optimum beaten by")
    for p in PS:
        picks = [rng.choice(len(sites), p, replace=False) for _ in range(DRAWS)]
        m = np.array([measures(dist, pop, list(x)) for x in picks])
        draws[p] = m
        med_open = facility.p_median(dist, pop, p)["open"]
        g_med, _ = facility.greedy_median(dist, pop, p)
        mc = cover.solve(sets, pop, p, integer=True)
        mc_open = np.flatnonzero(mc["x"] > 0.5).tolist()
        g_cov, _ = cover.greedy(sets, pop, p)
        opt_walk, _ = measures(dist, pop, med_open)
        _, opt_cov = measures(dist, pop, mc_open)
        gw, _ = measures(dist, pop, list(g_med))
        _, gc = measures(dist, pop, list(g_cov))
        q = np.percentile(m, [5, 50, 95], axis=0)
        print(f"   {p:>2}  {q[0, 0]:>30.0f} / {q[1, 0]:.0f} / {q[2, 0]:.0f}   {gw:>6.0f}   {opt_walk:>7.0f}"
              f"   {(m[:, 0] <= opt_walk).sum()} of {DRAWS}")  # fmt: skip
        print(f"   {'':>2}  {q[0, 1]:>30.1%} / {q[1, 1]:.1%} / {q[2, 1]:.1%}   {gc:>6.1%}   {opt_cov:>7.1%}"
              f"   {(m[:, 1] >= opt_cov).sum()} of {DRAWS}")  # fmt: skip

    print(f"\n## the current {len(shelter_names)} evacuation sites")
    cur_walk, cur_cov = measures(hdist, pop, list(range(len(shelter_names))))
    m = draws[17]
    opt17 = measures(dist, pop, facility.p_median(dist, pop, 17)["open"])
    mc17 = cover.solve(sets, pop, 17, integer=True)
    cov17 = measures(dist, pop, np.flatnonzero(mc17["x"] > 0.5).tolist())
    print(f"   current: mean walk {cur_walk:.0f} m, within 400 m {cur_cov:.1%}")
    print(f"   17 random candidates: mean walk median {np.median(m[:, 0]):.0f} m "
          f"(current is better than {(m[:, 0] > cur_walk).mean():.0%} of draws), within 400 m median "
          f"{np.median(m[:, 1]):.1%} (current is better than {(m[:, 1] < cur_cov).mean():.0%})")  # fmt: skip
    print(f"   optimal 17 for the mean walk: {opt17[0]:.0f} m (within 400 m {opt17[1]:.1%});"
          f" optimal 17 for 400 m: {cov17[1]:.1%} (mean walk {cov17[0]:.0f} m)")  # fmt: skip

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for ax, k, label in ((axes[0], 0, "mean walk (m)"), (axes[1], 1, "share within 400 m")):
        ax.hist(m[:, k], bins=40, color="#999999")
        ax.axvline([cur_walk, cur_cov][k], color="tab:red", label="current 17 sites")
        ax.axvline([opt17[0], cov17[1]][k], color="tab:blue", label="optimal 17")
        ax.set_xlabel(label)
        ax.set_title(f"17 random candidate sites, {DRAWS} draws")
    axes[0].legend()
    fig.savefig(OUT / "random-17.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigures: {OUT}")


if __name__ == "__main__":
    main()
