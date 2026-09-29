"""Step 12B: the epsilon-constraint method against weighted sums.

The problem of step 12A with the number of sites fixed (K), leaving two
objectives: people within 400 m (more) and the flood rank summed over the
opened sites (lower).

- epsilon constraint: for EPS = 0, 1, 2, ... maximise the people covered with
  the flood sum at most EPS. Every Pareto-optimal point comes out this way.
- weighted sum: maximise covered - w * flood for a fine grid of w. Only the
  points on the upper convex hull of the front (supported points) can come out.

    uv run python -u src/012-B-epsilon-constraint/run.py
"""

import importlib.util
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from study_geoai import cover  # noqa: E402
from study_geoai.db import connect  # noqa: E402

OUT = Path(__file__).parent / "output"
K = 13
W_GRID = np.concatenate([np.arange(0, 2000, 50), np.arange(2000, 20001, 500)])
_spec = importlib.util.spec_from_file_location(
    "step12a", Path(__file__).parents[1] / "012-A-multi-objective-optimization" / "run.py"
)
step12a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(step12a)


def main():
    con = connect()
    OUT.mkdir(parents=True, exist_ok=True)
    pop, sets, flood, _, _ = step12a.instance(con)
    total = pop.sum()
    top = cover.solve_multi(sets, pop, flood, k=K)
    print(f"## taito, k = {K}: without the flood objective, {top['covered'] / total:.1%} covered "
          f"with flood {top['flood']:.0f} ({top['seconds']:.1f} s)")  # fmt: skip

    print("\n   epsilon   covered   share   flood used   seconds")
    eps_points = []
    for eps in range(int(top["flood"]) + 1):
        r = cover.solve_multi(sets, pop, flood, k=K, max_flood=eps)
        eps_points.append((r["covered"], r["flood"]))
        print(f"   {eps:>7}  {r['covered']:>9,.0f}  {r['covered'] / total:>6.1%}  {r['flood']:>10.0f}"
              f"  {r['seconds']:>8.1f}  {r['status']}", flush=True)  # fmt: skip
    # keep the Pareto points: an epsilon whose answer uses less flood than allowed
    # repeats a point found at a smaller epsilon
    front = sorted({(round(c), round(f)) for c, f in eps_points}, key=lambda p: p[1])
    front = [p for p in front if not any(q[0] >= p[0] and q[1] < p[1] for q in front)]

    ws_points = set()
    for w in W_GRID:
        r = cover.solve_multi(sets, pop, flood, k=K, w_flood=float(w))
        ws_points.add((round(r["covered"]), round(r["flood"])))
    print(f"\n   epsilon constraint: {len(front)} Pareto points; weighted sum over {len(W_GRID)} "
          f"weights: {len(ws_points)} distinct points")  # fmt: skip
    missed = [p for p in front if p not in ws_points]
    print(f"   Pareto points the weighted sum never returned: {len(missed)} of {len(front)}")
    for c, f in front:
        mark = "" if (c, f) in ws_points else "   <- only by epsilon constraint"
        print(f"      flood {f:>3}: {c:>8,} people ({c / total:.1%}){mark}")

    fig, ax = plt.subplots(figsize=(7, 5))
    fa = np.array(front, dtype=float)
    ax.step(fa[:, 1], fa[:, 0] / total, where="post", color="grey", linewidth=0.8)
    ax.scatter(
        fa[:, 1],
        fa[:, 0] / total,
        s=50,
        c="tab:blue",
        label="epsilon constraint (all Pareto points)",
    )
    wa = np.array(sorted(ws_points, key=lambda p: p[1]), dtype=float)
    ax.scatter(wa[:, 1], wa[:, 0] / total, s=140, facecolors="none", edgecolors="red",
               label="weighted sum")  # fmt: skip
    ax.plot(wa[:, 1], wa[:, 0] / total, color="red", linewidth=0.8, linestyle="--")
    ax.set_xlabel("flood rank summed over the 13 sites")
    ax.set_ylabel("share of people within 400 m")
    ax.set_title(f"taito, k = {K}: the Pareto front")
    ax.legend(loc="lower right")
    fig.savefig(OUT / "front-taito.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigures: {OUT}")


if __name__ == "__main__":
    main()
