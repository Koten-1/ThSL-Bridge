# ThSL Bridge — Research

Three research questions, evaluated the way Radford et al. (2022, *Robust Speech Recognition via Large-Scale Weak Supervision* — Whisper, arXiv:2212.04356) argue robustness claims should be evaluated: decontaminated, and tested zero-shot on distributions the model never saw in training.

## RQ1 — Honest evaluation (done)

Does a naive random train/test split overstate accuracy through data leakage, compared to a group-aware split that keeps a video's augmented copies entirely on one side of the split?

**Result**: 99.6% (naive) → 98.88% (group-aware). The gap is the leakage naive evaluation was hiding.

## RQ2 — Architecture depth (done)

Single-layer vs. 2-layer stacked LSTM, both evaluated under RQ1's honest split.

**Result**: 97.75% (single) vs. 98.88% (stacked) — stacked wins.

## RQ3 — Zero-shot signer generalization + domain-adversarial training (done)

Does training on multiple signers generalize to a signer the model has *never seen*, and does explicitly training the model to ignore signer identity (domain-adversarial training; Ajakan et al., 2014; Ganin et al., 2016) improve that generalization beyond passively adding more signers?

**อัยด้า** was permanently held out — zero clips in any training condition — as the true zero-shot test set. Three model variants, all evaluated on that same held-out signer: `solo-baseline` (กร alone), `pooled-baseline` (ตะวัน+ปิ่น pooled), `pooled+DANN` (pooled + a gradient-reversal auxiliary signer classifier).

**Result**: 21% (solo-baseline) → 62% (pooled-baseline) → 60% (pooled+DANN). Signer diversity produced by far the largest generalization gain; the domain-adversarial objective did not improve on the pooled baseline in this narrow (2-signer) setting — a rigorously-tested negative result. A risk-coverage / selective-accuracy analysis (AURC) is also reported, formalizing the confidence-threshold rejection already shipped in `innovation/predict_stream.py` into a measured metric, in support of the medical-deployment framing below.

`notebooks/🧩RQ3_DANN.ipynb` reproduces this (needs `data/processed/` and `data/augmented/` synced to Drive first — these are gitignored, not in this repo). Note: model weight initialization isn't seeded, so exact re-runs will vary by a few points — the qualitative ordering (solo ≪ pooled ≈ pooled+DANN) has held consistent across runs.

## File map

- `notebooks/🧩LuckBasedModel(2).ipynb` — RQ1 + RQ2, done, do not edit (reproducibility)
- `notebooks/🧩RQ3_DANN.ipynb` — RQ3, self-contained, separate variable namespace from the above
- `check_thresholds.py` — per-class confidence threshold inspection tool
- `figures/` — confusion matrices, data-quality comparison charts
- `ThSL_Bridge_Study_Notes.md` — background study notes

## Future direction

Phase 2: extend the vocabulary from conversational words to medical terms, positioning ThSL Bridge as a clinical communication tool — the risk-coverage/selective-accuracy work above (knowing when the model is uncertain) is deliberately laying groundwork for that use case, where a wrong prediction has higher stakes than a rejected one.
