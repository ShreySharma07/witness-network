# Witness Networks

**Can peer agents expose a colluding coalition's cover-up?** We tested this on an 8-agent LLM swarm.
Submission to the Apart Research **Swarm Alignment Hackathon** (Nov 6–8, 2026), Track 4: Multi-Agent Oversight & Control.

## Key results (216 episodes; 367 cover-ups vs the same 96 attack episodes untampered)

| Auditor | Tamper-detection AUROC (7B auditor / 14B auditor) |
|---|---|
| B2 exact cross-log matcher | **0.935** [0.92, 0.95] (deterministic) |
| B2, peer witnesses only | 0.929 [0.91, 0.95] |
| B0 single-log LLM monitor | 0.42 / 0.40 |
| B1 all-logs LLM monitor | 0.46 / 0.40 |
| B3 LLM cross-witness auditor | 0.51 / 0.49 |

- **Proposition.** A coordinated cover-up is detectable by cross-log consistency iff some altered record names a party outside the coalition.
- **The matcher follows it exactly.** It agrees 898/898 on scripted audits, catches 666/666 detectable cover-ups, and raises 0 false alarms on 96 untampered attack episodes.
- **LLM monitors detect the attack, not the cover-up.** Attack-detection AUROC is up to 0.998, but a competent journal scrub drives them to 0.19–0.38.
- **Honest LLM witnesses are persuadable.** They agree to falsify their own records 93% (7B) and 61% (14B) of the time. Verbatim redundancy still keeps detection at 86–100%.
- **Real data.** On the collusion.wiki agent wiki log, only 5.4% of distinctive posts are echoed on another page.

The report draft is in [`report/draft.md`](report/draft.md), with figures in `report/figs/`. Aggregate results are in `results/`.

## Layout

```
wn/env/          episode harness: graphs, simulated tools, batched agent loop, ground-truth logger
wn/redteam/      scripted tamper operators, LLM cover-ups, witness corruption
wn/blueteam/     B2 exact matcher, B0/B1/B3 LLM auditors
wn/theory/       witness-coverage proposition (tamper_coverage, effective coalition)
wn/eval/         AUROC, TPR@FPR, attribution F1, cluster bootstrap
wn/realdata/     collusion.wiki echo-coverage analysis
scripts/         pipeline.py (gen -> coverup -> tamper -> audit), analyze.py, make_figures.py,
                 competent_corruption.py
kaggle/, tools/  free-GPU launcher (Kaggle 2xT4 + vLLM) and CLI wrapper
tests/           unit tests (incl. theory == matcher on all scripted ops)
```

## Reproduce

These commands run locally on the mock backend, with no GPU or network:

```bash
pip install pytest matplotlib && python -m pytest -q tests
```

```bash
python scripts/pipeline.py --backend mock --out /tmp/wn_mock --seeds 2 --neg-seeds 3
```

```bash
python scripts/analyze.py --out /tmp/wn_mock
```

To run the real models, use a vLLM GPU box (we used free Kaggle T4s):

```bash
python scripts/pipeline.py --backend vllm --model Qwen/Qwen2.5-7B-Instruct-AWQ --tp 2 --seeds 6 --neg-seeds 10 --extra-neg 20 --out out/
```

## Ethics

Collusion is *elicited*: we measure detection, not propensity. Episode files contain cover-up and witness-persuasion
text, so only aggregates are committed; episode files are available to safety researchers on request.
The collusion.wiki data is public. We do not de-anonymize it or reproduce payloads.

## Pre-existing work

None. All code and text in this repository were written during the sprint (Nov 6–8, 2026).
