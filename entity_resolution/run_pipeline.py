#!/usr/bin/env python3
import argparse
import csv
import math
import os
import random
import re
from collections import defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher


ABBREVIATIONS = {
    "co": "company",
    "corp": "corporation",
    "inc": "incorporated",
    "ltd": "limited",
    "pvt": "private",
    "intl": "international",
    "st": "street",
    "rd": "road",
    "ave": "avenue",
    "blvd": "boulevard",
    "ctr": "center",
    "mt": "mount",
    "&": "and",
}


def read_tsv(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_tsv(path, rows, fieldnames):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def normalize_text(text):
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9\s&]", " ", text)
    tokens = []
    for tok in text.split():
        tok = ABBREVIATIONS.get(tok, tok)
        tokens.append(tok)
    return " ".join(tokens)


def tokens(text):
    t = normalize_text(text)
    return t.split() if t else []


def trigrams(text):
    s = f"  {normalize_text(text)}  "
    if not s.strip():
        return set()
    return {s[i : i + 3] for i in range(max(1, len(s) - 2))}


def jaccard(a, b):
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    sa, sb = set(a), set(b)
    inter = len(sa & sb)
    uni = len(sa | sb)
    return inter / uni if uni else 0.0


def digit_chunks(text):
    return re.findall(r"\d+", (text or ""))


def safe_ratio(a, b):
    if not a and not b:
        return 1.0
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()


@dataclass
class PairFeature:
    x: list
    y: int
    s1_id: str
    s23_id: str


class LogisticModel:
    def __init__(self):
        self.w = []
        self.b = 0.0
        self.mean = []
        self.std = []

    def _standardize_fit(self, X):
        d = len(X[0]) if X else 0
        self.mean = [0.0] * d
        self.std = [1.0] * d
        n = len(X)
        for j in range(d):
            m = sum(x[j] for x in X) / max(1, n)
            v = sum((x[j] - m) ** 2 for x in X) / max(1, n)
            s = math.sqrt(v) if v > 0 else 1.0
            self.mean[j] = m
            self.std[j] = s

    def _standardize(self, X):
        out = []
        for x in X:
            out.append([(x[j] - self.mean[j]) / self.std[j] for j in range(len(x))])
        return out

    @staticmethod
    def _sigmoid(z):
        if z >= 0:
            e = math.exp(-z)
            return 1.0 / (1.0 + e)
        e = math.exp(z)
        return e / (1.0 + e)

    def fit(self, X, y, epochs=250, lr=0.05, l2=1e-4):
        if not X:
            self.w = [0.0] * 8
            self.b = 0.0
            self.mean = [0.0] * 8
            self.std = [1.0] * 8
            return
        self._standardize_fit(X)
        Xs = self._standardize(X)
        d = len(Xs[0])
        self.w = [0.0] * d
        self.b = 0.0
        pos = sum(y)
        neg = max(1, len(y) - pos)
        pos_w = neg / max(1, pos)
        for _ in range(epochs):
            for i in range(len(Xs)):
                xi = Xs[i]
                yi = y[i]
                z = self.b + sum(self.w[j] * xi[j] for j in range(d))
                p = self._sigmoid(z)
                err = p - yi
                weight = pos_w if yi == 1 else 1.0
                for j in range(d):
                    grad = weight * err * xi[j] + l2 * self.w[j]
                    self.w[j] -= lr * grad
                self.b -= lr * weight * err

    def predict_proba(self, X):
        if not X:
            return []
        Xs = self._standardize(X)
        out = []
        for xi in Xs:
            z = self.b + sum(self.w[j] * xi[j] for j in range(len(self.w)))
            out.append(self._sigmoid(z))
        return out


def make_blocks(record):
    c = normalize_text(record.get("country", ""))
    name_toks = tokens(record.get("business_name", ""))
    addr_toks = tokens(record.get("business_address", ""))
    nums = digit_chunks(record.get("business_address", ""))
    keys = set()
    if name_toks:
        keys.add(f"{c}|n1|{name_toks[0]}")
        keys.add(f"{c}|n2|{' '.join(name_toks[:2])}")
        keys.add(f"{c}|nlast|{name_toks[-1]}")
    if addr_toks:
        keys.add(f"{c}|a1|{addr_toks[0]}")
        keys.add(f"{c}|a2|{' '.join(addr_toks[:2])}")
    for n in nums[:2]:
        keys.add(f"{c}|num|{n}")
    if name_toks and addr_toks:
        keys.add(f"{c}|mix|{name_toks[0]}|{addr_toks[0]}")
    if not keys:
        keys.add(f"{c}|fallback")
    return keys


def build_index(records):
    idx = defaultdict(set)
    by_country = defaultdict(set)
    for r in records:
        rid = r["entity_id"]
        c = normalize_text(r.get("country", ""))
        by_country[c].add(rid)
        for k in make_blocks(r):
            idx[k].add(rid)
    return idx, by_country


def generate_candidates(source1, source23):
    s23_by_id = {r["entity_id"]: r for r in source23}
    idx, by_country = build_index(source23)
    out = {}
    for s1 in source1:
        cand = set()
        for k in make_blocks(s1):
            cand |= idx.get(k, set())
        if not cand:
            c = normalize_text(s1.get("country", ""))
            cand |= by_country.get(c, set())
        if not cand:
            cand = set(s23_by_id.keys())
        out[s1["entity_id"]] = sorted(cand)
    return out


def pair_features(a, b):
    name_toks_a = tokens(a.get("business_name", ""))
    name_toks_b = tokens(b.get("business_name", ""))
    addr_toks_a = tokens(a.get("business_address", ""))
    addr_toks_b = tokens(b.get("business_address", ""))
    name_tri_a = trigrams(a.get("business_name", ""))
    name_tri_b = trigrams(b.get("business_name", ""))
    addr_tri_a = trigrams(a.get("business_address", ""))
    addr_tri_b = trigrams(b.get("business_address", ""))
    nums_a = set(digit_chunks(a.get("business_address", "")))
    nums_b = set(digit_chunks(b.get("business_address", "")))
    country_same = 1.0 if normalize_text(a.get("country", "")) == normalize_text(b.get("country", "")) else 0.0
    num_overlap = 1.0 if nums_a and nums_b and (nums_a & nums_b) else 0.0
    return [
        jaccard(name_toks_a, name_toks_b),
        jaccard(addr_toks_a, addr_toks_b),
        jaccard(name_tri_a, name_tri_b),
        jaccard(addr_tri_a, addr_tri_b),
        safe_ratio(a.get("business_name", ""), b.get("business_name", "")),
        safe_ratio(a.get("business_address", ""), b.get("business_address", "")),
        country_same,
        num_overlap,
    ]


def parse_ground_truth(path):
    rows = read_tsv(path)
    gt = {}
    for r in rows:
        s1 = r["source1_entity_id"].strip()
        ids = []
        raw = (r.get("matched_entity_ids") or "").strip()
        if raw:
            ids = [x.strip() for x in raw.split(",") if x.strip()]
        gt[s1] = set(ids)
    return gt


def fbeta_score(beta, y_true, y_pred):
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    if tp == 0:
        return 0.0
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    b2 = beta * beta
    den = b2 * prec + rec
    if den == 0:
        return 0.0
    return (1 + b2) * prec * rec / den


def evaluate_threshold(prob_rows, gt, threshold):
    y_true = []
    y_pred = []
    for s1_id, items in prob_rows.items():
        true_ids = gt.get(s1_id, set())
        pred_ids = {cid for cid, p in items if p >= threshold}
        universe = set(cid for cid, _ in items) | true_ids
        for cid in universe:
            y_true.append(1 if cid in true_ids else 0)
            y_pred.append(1 if cid in pred_ids else 0)
    return fbeta_score(0.5, y_true, y_pred)


def train_and_select_threshold(train_s1, train_s23, gt, seed=42):
    rnd = random.Random(seed)
    s1_ids = [r["entity_id"] for r in train_s1]
    rnd.shuffle(s1_ids)
    cut = max(1, int(len(s1_ids) * 0.8))
    train_ids = set(s1_ids[:cut])
    val_ids = set(s1_ids[cut:])
    cands = generate_candidates(train_s1, train_s23)
    s1_by_id = {r["entity_id"]: r for r in train_s1}
    s23_by_id = {r["entity_id"]: r for r in train_s23}
    train_pairs = []
    val_pairs = defaultdict(list)
    for s1_id, cand_ids in cands.items():
        true_ids = gt.get(s1_id, set())
        s1_rec = s1_by_id[s1_id]
        feats = []
        for cid in cand_ids:
            x = pair_features(s1_rec, s23_by_id[cid])
            y = 1 if cid in true_ids else 0
            feats.append(PairFeature(x=x, y=y, s1_id=s1_id, s23_id=cid))
        if s1_id in train_ids:
            pos = [f for f in feats if f.y == 1]
            neg = [f for f in feats if f.y == 0]
            rnd.shuffle(neg)
            keep_neg = neg[: max(5 * len(pos), 50)] if pos else neg[:80]
            train_pairs.extend(pos + keep_neg)
        else:
            for f in feats:
                val_pairs[s1_id].append((f.s23_id, f.x))
    rnd.shuffle(train_pairs)
    X = [p.x for p in train_pairs]
    y = [p.y for p in train_pairs]
    model = LogisticModel()
    model.fit(X, y)
    val_prob_rows = defaultdict(list)
    for s1_id, items in val_pairs.items():
        Xv = [x for _, x in items]
        pv = model.predict_proba(Xv)
        for (cid, _), p in zip(items, pv):
            val_prob_rows[s1_id].append((cid, p))
    best_t = 0.5
    best_s = -1.0
    for t in [i / 100 for i in range(20, 96, 3)]:
        score = evaluate_threshold(val_prob_rows, gt, t)
        if score > best_s:
            best_s = score
            best_t = t
    return model, best_t, cands


def run_pipeline(data_root, out_dir, seed=42):
    train_dir = os.path.join(data_root, "train")
    test_dir = os.path.join(data_root, "test")
    train_s1 = read_tsv(os.path.join(train_dir, "train_source1.tsv"))
    train_s2 = read_tsv(os.path.join(train_dir, "train_source2.tsv"))
    train_s3 = read_tsv(os.path.join(train_dir, "train_source3.tsv"))
    gt = parse_ground_truth(os.path.join(train_dir, "train_ground_truth.tsv"))
    train_s23 = train_s2 + train_s3
    model, threshold, _ = train_and_select_threshold(train_s1, train_s23, gt, seed=seed)
    test_s1 = read_tsv(os.path.join(test_dir, "test_source1.tsv"))
    test_s2 = read_tsv(os.path.join(test_dir, "test_source2.tsv"))
    test_s3 = read_tsv(os.path.join(test_dir, "test_source3.tsv"))
    test_s23 = test_s2 + test_s3
    test_cands = generate_candidates(test_s1, test_s23)
    s23_by_id = {r["entity_id"]: r for r in test_s23}
    candidate_rows = []
    match_rows = []
    for s1 in test_s1:
        s1_id = s1["entity_id"]
        cids = test_cands.get(s1_id, [])
        candidate_rows.append(
            {
                "source1_entity_id": s1_id,
                "candidate_entity_ids": ",".join(cids),
            }
        )
        feats = [pair_features(s1, s23_by_id[cid]) for cid in cids]
        probs = model.predict_proba(feats)
        matched = [cid for cid, p in sorted(zip(cids, probs), key=lambda x: x[1], reverse=True) if p >= threshold]
        match_rows.append(
            {
                "source1_entity_id": s1_id,
                "matched_entity_ids": ",".join(matched),
            }
        )
    write_tsv(
        os.path.join(out_dir, "candidate_pairs.tsv"),
        candidate_rows,
        ["source1_entity_id", "candidate_entity_ids"],
    )
    write_tsv(
        os.path.join(out_dir, "matching_results.tsv"),
        match_rows,
        ["source1_entity_id", "matched_entity_ids"],
    )
    return threshold


def main():
    parser = argparse.ArgumentParser(description="Business Entity Resolution pipeline")
    parser.add_argument(
        "--data-root",
        required=True,
        help="Path containing train/ and test/ directories",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory where candidate_pairs.tsv and matching_results.tsv will be written",
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    threshold = run_pipeline(args.data_root, args.output_dir, seed=args.seed)
    print(f"Pipeline complete. Selected threshold={threshold:.2f}")


if __name__ == "__main__":
    main()
