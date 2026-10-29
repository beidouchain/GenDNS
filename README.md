# GenDNS Minimal Experiment

## Goal
Verify the core hypothesis: dual-track + satisfiability check (group C)
achieves lower constraint violation rate than single-track + violation-set
check (group B).

## Groups
- A: single track, no validation
- B: single track + A_B (violation-set) check
- C: dual track + Omega satisfiability check

## Run
python run_experiment.py

## Output
results/metrics.json
Console summary table

## Metrics
- VER: violation execution rate
- task_completion_rate: fraction of tasks with at least one executed action
- avg_rollbacks: average rollback attempts per task

## Note
The Phi track uses a deterministic mock. To use a real LLM, replace
MockPhi with LocalLLMPhi in run_experiment.py.