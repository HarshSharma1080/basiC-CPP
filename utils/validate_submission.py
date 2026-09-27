#!/usr/bin/env python3
import argparse
import csv
import os
import sys


def read_tsv(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def parse_id_list(raw):
    raw = (raw or "").strip()
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]


def validate(matching_path, candidate_path, test_dir):
    errors = []
    warnings = []

    s1 = read_tsv(os.path.join(test_dir, "test_source1.tsv"))
    s2 = read_tsv(os.path.join(test_dir, "test_source2.tsv"))
    s3 = read_tsv(os.path.join(test_dir, "test_source3.tsv"))
    s1_ids = [r["entity_id"] for r in s1]
    s1_set = set(s1_ids)
    valid_match_ids = {r["entity_id"] for r in s2 + s3}

    matching = read_tsv(matching_path)
    candidate = read_tsv(candidate_path)

    if set(matching[0].keys()) != {"source1_entity_id", "matched_entity_ids"}:
        errors.append("matching_results.tsv columns must be: source1_entity_id, matched_entity_ids")
    if set(candidate[0].keys()) != {"source1_entity_id", "candidate_entity_ids"}:
        errors.append("candidate_pairs.tsv columns must be: source1_entity_id, candidate_entity_ids")

    def check_rows(rows, list_col, file_name):
        seen = set()
        row_map = {}
        for i, r in enumerate(rows, start=2):
            s1id = (r.get("source1_entity_id") or "").strip()
            if s1id not in s1_set:
                errors.append(f"{file_name}:{i} invalid source1_entity_id '{s1id}'")
                continue
            if s1id in seen:
                errors.append(f"{file_name}:{i} duplicate row for source1_entity_id '{s1id}'")
            seen.add(s1id)
            ids = parse_id_list(r.get(list_col, ""))
            if len(ids) != len(set(ids)):
                errors.append(f"{file_name}:{i} duplicate IDs inside list for '{s1id}'")
            for cid in ids:
                if cid not in valid_match_ids:
                    errors.append(f"{file_name}:{i} invalid candidate/match ID '{cid}' (must exist in test S2/S3)")
            row_map[s1id] = set(ids)
        missing = s1_set - seen
        extra = seen - s1_set
        if missing:
            errors.append(f"{file_name} missing {len(missing)} source1 IDs")
        if extra:
            errors.append(f"{file_name} has {len(extra)} unknown source1 IDs")
        return row_map

    match_map = check_rows(matching, "matched_entity_ids", "matching_results.tsv")
    cand_map = check_rows(candidate, "candidate_entity_ids", "candidate_pairs.tsv")

    for s1id in s1_set:
        m = match_map.get(s1id, set())
        c = cand_map.get(s1id, set())
        if not m.issubset(c):
            warnings.append(
                f"Matched IDs not present in candidate list for {s1id}: {','.join(sorted(m - c))}"
            )

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate ER submission files")
    parser.add_argument("--matching", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--test-dir", required=True)
    args = parser.parse_args()

    errors, warnings = validate(args.matching, args.candidate, args.test_dir)
    if warnings:
        print("WARNINGS:")
        for i, w in enumerate(warnings, 1):
            print(f"{i}. {w}")
    if errors:
        print("FAIL")
        for i, e in enumerate(errors, 1):
            print(f"{i}. {e}")
        sys.exit(1)
    print("PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
