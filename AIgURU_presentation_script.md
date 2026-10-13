# Presentation Script — *Signer-Invariant Thai Sign Language Recognition under Limited Data*

**Source deck:** `AIgURU.pdf` (24 slides)
**Suggested length:** ~9–11 minutes
**Delivery notes:** numbers in **bold** are the ones to land clearly; `[click]` marks a build/animation step.

---

## Slide 1 — Title

"Good morning. Our project is **Signer-Invariant Thai Sign Language Recognition under Limited Data** — with the subtitle *Honest Evaluation and Domain-Adversarial Zero-Shot Generalization*.

I'm Kachornattapon Khumyaito, presenting the work of our team — Tawan, Supitchaya, Warintorn and Nattanun — advised by Mr. Yutthasak Sawangsamutchai.

The one-sentence version: we are not shipping a finished translator. We are building an *honest way to measure* whether a Thai Sign Language model actually works — especially on people it has never seen before."

---

## Slide 2 — Introduction: scale of the problem

"Start with why this matters. According to the Department of Empowerment of Persons with Disabilities, as of March 31, 2025, Thailand has **430,685 people** with hearing or communication impairments.

That is the **second-largest** disability group in the country — about 19 percent of all registered persons with disabilities. This is not a niche audience; it's hundreds of thousands of people who hit a communication wall every day."

---

## Slide 3 — Introduction: the gap, and the flaw in prior work

"Two problems.

First, the access gap. In a national survey of Thai pharmacists, only **6.1 percent** said they could use sign language. So a Deaf patient talking about their own medication is usually reduced to writing notes or gesturing — and that's a documented *patient-safety* risk, not just an inconvenience.

Second, the research gap. Existing Thai Sign Language recognition work mostly uses recurrent models like LSTM and reports strong accuracy — Jintanachaiwat and colleagues in 2024 reported **86 percent** real-time accuracy. But that number is almost always measured on *the same signer the model trained on*. Their own paper flags single-signer training data as a core limitation and calls for multi-signer testing as future work. That future work is what we're doing."

---

## Slide 4 — Abstract: objective and three research questions

"So our objective is an *evaluation methodology* for Thai Sign Language translation: honest accuracy, a fair architecture comparison, and generalization to unseen signers.

It breaks into three research questions:

- **RQ1 — how much does data leakage inflate accuracy?** We build a group-aware split that keeps every original recording apart from its augmented copies.
- **RQ2 — does making the LSTM deeper help?** Single-layer versus stacked, under identical conditions.
- **RQ3 — does signer diversity, or domain-adversarial training, help you generalize?** A full signer hold-out, tested zero-shot, with DANN added on top.

The contribution is the framework itself — a foundation future medical systems can build on, not a finished clinical tool."

---

## Slides 5–7 — Abstract build (RQ1 → RQ2 → RQ3)

*(These slides just re-reveal the three RQs one at a time. Don't re-read them — use them as a transition.)*

"To say that once more, quickly, because these three questions structure the whole talk — `[click]` leakage, `[click]` depth, `[click]` diversity and DANN. Keep those three in mind."

---

## Slide 8 — Section divider: METHODOLOGY

"Let's walk through how the data and models were built."

---

## Slide 9 — ⚠️ Stray template slide

**This slide is a leftover Canva/Borcelle marketing template ("พรีเซนเทชั่น การวางแผนตลาดออนไลน์"). Delete it before presenting.** If it's still there on the day, skip past it without comment.

---

## Slide 10 — Data preparation

"Data collection first. Each signer set up their own camera and recorded one long continuous take. For every word they signed it, held still for a couple of seconds, and repeated — ten times per word, ten words. We then cut the clips by hand in CapCut.

That gives **745 original records** from **4 signers**, **10 vocabulary items** — all conversational medical-context words: *Deaf person, you, help, thank you, I, want, understand, no, ask, tell*. Footage is deliberately messy: mixed mp4 and mov, 30 fps, resolution from 720p up to 4K — because real users won't have identical cameras.

Processing: we run MediaPipe and keep **hands only** — 21 landmarks per hand, x-y-z, two hands, so **126 features per frame**. No pose, no face, anywhere in the pipeline.

Then augmentation — scale, translate, and rotate the keypoints by up to 15 degrees — which expands the training material to **2,980 augmented records**."

---

## Slide 11 — Group-aware split

"Here's the heart of RQ1. We split **80/20**, but the split is made on the **original recordings before augmentation** — and every clip plus all of its augmented copies stay on the same side of the line.

So the training side has 596 originals and 2,980 augmented versions; the test side has 149 originals and nothing derived from training data. The test set contains *no near-duplicates* of anything the model trained on.

We also, on purpose, ran the naive version — a plain random split that lets augmented copies leak across — so we could measure exactly how much that dishonest setup inflates the score. That comparison is RQ1's answer."

---

## Slide 12 — Model architecture: RQ2

"RQ2 — does depth help under limited data? We compare a **single LSTM** against a **stacked, two-layer LSTM**. Everything else is held constant: same input shape 30 by 126, same dropout, same 12-class softmax output. Only depth changes.

The motivation, from Krichen and Mihoub 2025, is that stacked layers can capture longer time-scale patterns — layer one reads local motion, layer two composes it into full sign-level patterns. That's the theory we're testing, not a result yet."

---

## Slide 13 — Model architecture: RQ3, the three paths

"RQ3 uses three training conditions:

- **Path A, Solo-Baseline** — train on one signer, the stacked LSTM.
- **Path B, Pooled-Baseline** — same architecture, but train on two *different* signers.
- **Path C, Pooled plus DANN** — add a domain-adversarial branch: a shared LSTM feature extractor, a gradient reversal layer, and an auxiliary head that tries to guess *which signer* it is. Reversing that gradient pushes the features to become signer-invariant.

Key design choice: the solo signer and the pooled signers are **completely disjoint** — Korn versus Tawan-plus-Pin. If the pooled set were 'Korn plus one more,' any gain could just be memorizing Korn. Disjoint sets make the claim clean: does training on a *more varied population* generalize better?"

---

## Slide 14 — Model architecture: RQ3 evaluation setup

"And all three paths are evaluated the same way — zero-shot on a completely held-out signer that appears in none of the training conditions. Nobody has seen this person before test time."

---

## Slide 15 — Section divider: RESULTS AND DISCUSSION

"Now the results."

---

## Slide 16 — RQ1: naive vs group-aware split

"RQ1. With the naive, leaky split the model scores **99.60 percent**. With the honest group-aware split it scores **99.88** — on that particular held-in test.

The headline is the **1.67 percent inflation difference** that leakage produces when you measure it properly across the comparison. It's a modest gap here, and I want to be honest about why: our dataset is still small and low in variety, so leakage has limited room to help. On a bigger, messier dataset this gap typically grows. The point is methodological — if you don't control for it, your reported number is not trustworthy."

---

## Slide 17 — RQ2: single vs stacked LSTM

"RQ2. Both architectures reach **exactly the same accuracy — 97.32 percent**.

Validation loss looks different — single LSTM sits stably around 0.13, stacked swings from 0.05 to 0.15, nearly a 3x range across runs — but we didn't fix the random seed, so loss isn't a fair comparison here. Accuracy is the trusted metric, and on accuracy, depth bought us nothing.

Takeaway: under limited data, the extra LSTM layer added cost without measurable benefit. Next step is fixing seeds so loss becomes comparable too."

---

## Slide 18 — RQ3: zero-shot signer generalization

"RQ3, and this is the most important slide. Accuracy on a signer the model has *never seen*:

- Solo-Baseline: **20 percent**.
- Pooled-Baseline: **66 percent**.
- Pooled plus DANN: **61 percent**.

Training on one person collapses completely on a new person — 20 percent, barely above chance for 10 classes. Just adding *one more signer* to training triples that, to 66 percent. Within the small scope of this dataset the ranking is Pooled-Baseline first, then DANN, then Solo."

---

## Slide 19 — RQ3: DANN invariance sanity check

"Why did DANN come in slightly *below* the plain pooled model? This chart is the sanity check.

During the 10-epoch warm-up the auxiliary classifier's accuracy climbs — it's easily telling the two signers apart. Once gradient reversal switches on, it declines, which is what we want. But it **never reaches chance level** — 50 percent for two signers — it plateaus around 60.

So the features are only *partially* signer-invariant. The signer-distinguishing information — plausibly physiological signing style, though recording conditions also varied by signer and we can't fully separate those — is still partly present. With only two pooled signers, the adversarial signal is just too narrow for DANN to fully do its job."

---

## Slide 20 — Section divider: CONCLUSION

"To wrap up."

---

## Slide 21 — Conclusion: the three answers

"Our three answers:

- **RQ1** — naive evaluation overestimated accuracy by **1.67 percent**; you must control for leakage or your number is inflated.
- **RQ2** — LSTM depth added no measurable benefit; loss was too unstable across runs to compare, so accuracy did the deciding.
- **RQ3** — **signer diversity, not DANN, drove generalization** — from 20 percent up to 66. DANN landed slightly lower at 61, explained by incomplete signer-invariance under a narrow two-signer adversarial signal."

---

## Slide 22 — Closing quote

"So I'll leave you with this:

*The contribution here is not a finished Thai Sign Language translation tool. It's an evaluation methodology — honest accuracy, architecture testing, and generalization to unseen signers — that a future medical system would need to inherit before it could be trusted.*

Thank you. Happy to take questions."

---

## Slide 23 — Section divider: EXTRA

*(Backup / Q&A only — don't present unless asked.)*

"We have some extra material if there are questions about the data."

---

## Slide 24 — EXTRA: self-recorded vs scraped clips

*(Use if asked "why not use the national Thai Sign Language database?")*

"We tried two data sources: our own recordings, and scraping the national Thai Sign Language database. We kept the self-recorded clips and rejected the scraped ones.

Reason: MediaPipe hand-detection rate. On scraped clips, hand detection was **29, 33, and 62 percent** for the words we tested — below the roughly 70 percent we need. On our own clips the same words hit **100, 67, and 91 percent**. The scraped footage — compression, framing, motion blur — just doesn't survive keypoint extraction reliably enough to train on. The right-hand panel shows the frame-level check: our pipeline confirms which frames actually contain hands versus the saved `.npy` used for training."

---

### Optional 30-second version (if you're cut for time)

"Thai Sign Language models report high accuracy but test on the same signer they trained on. We built an honest evaluation: a leakage-free data split, a fair single-vs-stacked LSTM comparison, and a zero-shot test on an unseen signer. Findings — leakage inflates accuracy by 1.67%; depth doesn't help under limited data; and training on even one extra signer lifts unseen-signer accuracy from 20% to 66%, while domain-adversarial training slightly underperforms because two signers give too narrow an adversarial signal. The deliverable is the evaluation framework, not a finished tool."
