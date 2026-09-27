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

## Is the model already trained?

No. There is no pre-trained model file in this project.

`entity_resolution/run_pipeline.py` trains the model every time you run it by using:

- `train/train_source1.tsv`
- `train/train_source2.tsv`
- `train/train_source3.tsv`
- `train/train_ground_truth.tsv`

Then it applies that trained model to the test set and writes output files.

## Step-by-step: run everything from scratch

### 1) Prepare your dataset folder

Create a folder that contains this structure:

```text
<DATA_ROOT>/
  train/
    train_source1.tsv
    train_source2.tsv
    train_source3.tsv
    train_ground_truth.tsv
  test/
    test_source1.tsv
    test_source2.tsv
    test_source3.tsv
```

### 2) Go to repository root

```bash
cd /absolute/path/to/basiC-CPP
```

### 3) Run the pipeline (this includes training)

```bash
python3 entity_resolution/run_pipeline.py \
  --data-root /absolute/path/to/<DATA_ROOT> \
  --output-dir /absolute/path/to/output
```

Optional (for reproducibility):

```bash
python3 entity_resolution/run_pipeline.py \
  --data-root /absolute/path/to/<DATA_ROOT> \
  --output-dir /absolute/path/to/output \
  --seed 42
```

When complete, you should see:

```text
Pipeline complete. Selected threshold=<value>
```

### 4) Check generated files

The run creates:

- `/absolute/path/to/output/candidate_pairs.tsv`
- `/absolute/path/to/output/matching_results.tsv`

## Validate submission files

```bash
python3 utils/validate_submission.py \
  --matching /absolute/path/to/output/matching_results.tsv \
  --candidate /absolute/path/to/output/candidate_pairs.tsv \
  --test-dir /absolute/path/to/dataset/test
```

It prints `PASS` when files satisfy challenge constraints.

## Do I need to train manually?

No extra training command is needed.

Training is built into the same `run_pipeline.py` command, so just run that once with the correct `--data-root` and `--output-dir`.
