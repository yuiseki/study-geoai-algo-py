"""Step 1B: logistic regression of whether a street has its wires underground.

One row per michiyomi street scene: the VLM's reading of one Mapillary image.
The target is undergrounded = 無電柱化済 (1) against 架空線あり (0); scenes the
VLM could not judge (不明) are dropped. Taito City first, then the 23 wards.

    uv run python src/001-B-logistic-regression/run.py
    uv run python src/001-B-logistic-regression/run.py --area taito

Two feature sets are compared. STREET describes the road and the picture.
LEAKY adds the visible poles and wire density, which describe the overhead
wires themselves: with them the model mostly reads the answer back.
"""

import argparse
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from study_geoai import aoi, michiyomi
from study_geoai.db import connect

OUT = Path(__file__).parent / "output"
STREET = ["roadway_width_m", "sidewalk_left", "sidewalk_right", "green_ratio", "colorfulness",
          "lights_road"]  # fmt: skip
LEAKY = [*STREET, "poles_visible", "wire_high"]


def load(con, name):
    area = aoi.load(name, con)
    michiyomi.scenes(con, area).create_view("s")
    rows = con.sql("""
        select (undergrounded = '無電柱化済')::int as y,
               roadway_width_m,
               (sidewalk_left = 'あり')::int as sidewalk_left,
               (sidewalk_right = 'あり')::int as sidewalk_right,
               green_ratio, colorfulness, lights_road, poles_visible,
               (wire_density = '高')::int as wire_high
        from s
        where undergrounded in ('無電柱化済', '架空線あり')
          and roadway_width_m is not null and lights_road is not null
          and poles_visible is not null and wire_density is not null
          and green_ratio is not null and colorfulness is not null and quarantined = 0
    """).fetchall()
    total = con.sql("select count(*) from s").fetchone()[0]
    judged = con.sql(
        "select count(*) from s where undergrounded in ('無電柱化済', '架空線あり')"
    ).fetchone()[0]
    print(f"\n{name}: {total:,} scenes, {judged:,} judged, {len(rows):,} with every feature")
    cols = ["y", "roadway_width_m", "sidewalk_left", "sidewalk_right", "green_ratio",
            "colorfulness", "lights_road", "poles_visible", "wire_high"]  # fmt: skip
    data = {c: np.array([r[i] for r in rows], dtype=float) for i, c in enumerate(cols)}
    return total, data


def evaluate(name, data, feats):
    X = np.column_stack([data[f] for f in feats])
    y = data["y"].astype(int)
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
    cv = StratifiedKFold(5, shuffle=True, random_state=0)
    p = cross_val_predict(model, X, y, cv=cv, method="predict_proba")[:, 1]
    auc = roc_auc_score(y, p)
    acc = ((p >= 0.5) == y).mean()
    model.fit(X, y)
    coef = model[-1].coef_[0]
    return auc, acc, dict(zip(feats, coef, strict=True))


def run(name, con):
    total, data = load(con, name)
    n, pos = len(data["y"]), data["y"].mean()
    print(f"\n## {name}: {n:,} of {total:,} scenes used, {pos:.1%} undergrounded")
    print(f"   always guessing overhead wires gives accuracy {1 - pos:.3f}")
    out = {}
    for label, feats in (("street", STREET), ("with poles and wires", LEAKY)):
        auc, acc, coef = evaluate(name, data, feats)
        out[label] = (auc, coef)
        print(f"{label:22}: AUC {auc:.3f}, accuracy {acc:.3f} (5-fold, random split)")
        for f, c in sorted(coef.items(), key=lambda kv: -abs(kv[1])):
            print(f"     {f:16} {c:+.3f}  (odds x{np.exp(c):.2f} per standard deviation)")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--area", choices=["taito", "tokyo23", "both"], default="both")
    args = ap.parse_args()
    con = connect()
    names = ["taito", "tokyo23"] if args.area == "both" else [args.area]
    for name in names:
        run(name, con)


if __name__ == "__main__":
    main()
