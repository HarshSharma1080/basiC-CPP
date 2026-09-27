# Business Entity Resolution Solution

This repository now includes a complete end-to-end, dependency-free ER pipeline for the challenge.

## What it does

- Reads all train/test TSV files with tab separators
- Builds a blocking-based candidate set for each Source 1 record
- Trains a supervised pairwise logistic model (implemented in pure Python)
- Tunes a decision threshold on a validation split using **F0.5**
- Generates:
  - `output/candidate_pairs.tsv`
  - `output/matching_results.tsv`
- Validates output format/rules with a local validator

## Run

From repository root:

```bash
python3 entity_resolution/run_pipeline.py \
  --data-root /absolute/path/to/dataset \
  --output-dir /absolute/path/to/output
```

`--data-root` must contain:

- `train/train_source1.tsv`
- `train/train_source2.tsv`
- `train/train_source3.tsv`
- `train/train_ground_truth.tsv`
- `test/test_source1.tsv`
- `test/test_source2.tsv`
- `test/test_source3.tsv`

## Validate submission files

```bash
python3 utils/validate_submission.py \
  --matching /absolute/path/to/output/matching_results.tsv \
  --candidate /absolute/path/to/output/candidate_pairs.tsv \
  --test-dir /absolute/path/to/dataset/test
```

It prints `PASS` when files satisfy challenge constraints.
