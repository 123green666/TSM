# LongMemEval_S 6 x 15 - RTX 4090 and bge-m3

This overlay is intended for branch `experiment/4090-bge-6x15`, based on upstream commit `0da3633ba8e27e9f8122872ff775587116948f5e`.

It preserves the public TSM algorithm implementation. The only declared experiment differences are:

- one OpenAI-compatible LLM served on an RTX 4090;
- `bge-m3` through an OpenAI-compatible embedding endpoint;
- embedding dimension 1024;
- a fixed LongMemEval_S stratified subset: six question types x 15 questions;
- separate experiment names, paths, group prefixes, and provenance manifests.

The original `configs/longmemeval/tsm.yaml` is not overwritten. Copy this overlay into the fork while retaining the relative `experiments/longmemeval_6x15/` directory.

## Required local-only files

Download and verify `data/longmemeval/longmemeval_s.json`. Its expected SHA256 is:

`d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`

Run the sampling script locally. It creates `data/longmemeval/longmemeval_s_6x15_seed20261116.json`, which is ignored by the upstream `.gitignore`. Never commit the raw or derived dataset.

## Hard sequencing gate

1. Run the official-reproduction track first.
2. Give all 90 fixed questions a final `passed` or `failed` status.
3. Freeze code/config/data hashes, manifests, raw result inventory, and failures.
4. Only then create or run `diagnostic/fixed-pipeline`.

Do not use diagnostic code to repair the official track after inspecting its results. Failed questions remain in the denominator.

## Validation

The public matrix remains under `configs/`. Validate it with the upstream command:

```powershell
python scripts/validate_configs.py
```

Validate this additional config without adding it to the public 2 x 5 matrix:

```powershell
python -c "from pathlib import Path; from scripts.validate_configs import validate_config; p=Path(r'experiments/longmemeval_6x15/configs/longmemeval/tsm.yaml'); e=validate_config(p); print(e); raise SystemExit(bool(e))"
```

Run the official Level 1 checks before connecting benchmark endpoints. Then use `scripts/run_experiment.py --dry-run` and manually inspect all endpoint/model identifiers before acknowledging data transmission.
