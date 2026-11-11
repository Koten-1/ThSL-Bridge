# Poster METHODOLOGY: material for each step

Four steps as defined in the user's own System Overview panel, with the same colours as `research/figures_v3/trackers4/` (1 pink-red, 2 peach, 3 green, 4 blue):
1 ทำท่าภาษามือผ่านกล้อง · 2 อ่านมือด้วย MediaPipe · 3 LSTM เดาคำศัพท์ · 4 ประกอบประโยคและประมวลผล
(English: 1 Sign in front of the camera · 2 Read the hands with MediaPipe · 3 LSTM guesses the word · 4 Build the sentence and output)
**Figure accent colours are from an earlier scheme and do not yet match these step colours; the tracker is what marks the step.**
Every number below is from `report_th.md` (section in brackets), `research/DATASET_CARD.md` or `research/loso_final28/summary.md`.
Figures are in `research/figures_v3/`. Thai and English versions exist where the file name ends `_th` / `_en`.

---

## Step 1  Sign in front of the camera  (pink-red)  |  how the data was collected

**One line:** deaf volunteers signed 30 words to a smartphone camera; we keep only hand-point numbers.

**Cards (a step can carry several)**
| Card | File |
|---|---|
| Recording workflow | `fig22_collection_workflow.png` (Thai) |
| What the data looks like (same word, two signers, plus the 30 × 126 numbers) | `fig17_data_look.png` |
| Folder structure and signs per signer | `fig14a.png`, `fig14b.png` |
| 7,267 videos → 6,688 signs | `fig11_data_funnel.png` |

**Facts**
- 5 deaf signers (S01–S05), adult volunteers with a signed consent form. Words chosen with the deaf club from the Thai Sign Language database; only words with one fixed sign. [3.2]
- Smartphone video, one short video per sign, median 2.4 s. S01–S03 landscape 1280×720; S04–S05 portrait and close to the camera. [3.2]
- 7,267 videos → 7,168 signs for 30 words → 6,688 signs for the 28 words used by the classifier (หมอ and ขา dropped). [3.2, DATASET_CARD]
- Signs per signer: S01 2,666 · S02 1,061 · S03 2,543 · S04 703 · S05 142 (deaf signers, 7,115 signs). S01 + S03 = 73%. [DATASET_CARD]
- Protocol (confirmed by the team, 11 Nov): the signer repeats the sign for one word about 100 times (S01–S03 about 75–105 per word, S04–S05 5–46); there was no formal script for how to sign. [3.2, team]
- Word "คุณ" has no deaf-signer data from the main signers, so it uses 4 hearing signers (53 clips) plus S04 and S05, and is reported separately. [3.2]
- Stored data are numbers only: no images, no faces; file names use signer codes; original videos stay with the team. [3.6]

**Caption lines**
- EN: "Videos become numbers: only hand points are kept, no images or faces."
- EN: "Two signers supply 73% of the signs."
- TH: "ชุดข้อมูลเก็บเฉพาะตัวเลขจุดมือ ไม่มีภาพหรือใบหน้า"
- TH: "ผู้แสดง S01 และ S03 ให้ข้อมูลราว 73% ของทั้งหมด"

**Honest limits to say yourself:** few signers per word (24 of 30 words have 3 signers; คุณ and ไอ fewer); no formal ethics-committee review before recording (DATASET_CARD section 7).

**Judge questions**
- Why only 5 signers? → Deaf volunteers were hard to reach; that is why we test on unseen signers and report each signer separately.
- Did you give signers a script or protocol? → No formal protocol: each signer repeated one word's sign about 100 times in their own way. Say so plainly; it also means the data shows each person's natural variation, which is exactly what leave-one-signer-out tests.
- Does repeating a word 100 times in a row affect the data? → Yes, repeated signs from one person in one session are very similar, which is why a random split overstates accuracy (84.8% vs 51.9%). Say it before they do.

---

## Step 2  Read the hands with MediaPipe  (peach)  |  hand points, cutting, how position is measured

**One line:** MediaPipe turns each video frame into 126 numbers, a cutting rule finds where a sign starts and ends, and we tested two ways of making the numbers comparable between people.

**Cards**
| Card | File |
|---|---|
| How a sign is cut and resampled to 30 frames | `fig15_capture_timeline.png` |
| Left–right hand handling (3 options) | `fig18_leftright_card.png` |
| Hand position relative to the face | `fig19_face_relative_card.png` |

**Facts**
- MediaPipe Hands 0.10.14, up to 2 hands, minimum confidence 0.5. 21 points × 3 values × 2 hands = 126 values per frame. A hand that is not found is all zeros. [3.2]
- Capture rule: a sign starts when the hand moves (change of at least 0.008 over 200 ms); it ends after 200 ms of stillness, or when the hand is gone for 267 ms, or when the recording ends. About 233 ms before the first movement is kept. A capture shorter than 333 ms is discarded. Then resampled to 30 frames. [3.2, DATASET_CARD]
- The same rule runs in Python (training) and JavaScript (web app) and was checked to give identical cuts. [3.2]
- Left–right (13 words): the hand that moves more is in slot 1 for S01 (79%) and S03 (88%) but slot 2 for S02 (76%). No handling: 56.8% mean, S02 only 35%. Random flip during training: 72.7%. Main hand moved to slot 1: 75.9%. The 3.2-point difference between the last two is within the uncertainty. The web app uses flipping during training. [4.5, table 3]
- Face-relative (hand position in units of face width, 13 words): S01–S03 mean 72.7% → 78.6% (+5.9). Gains for S01 +10.6 and S02 +8.3, a small loss for S03 −1.1. Per word it goes both ways (หายใจ 33→100, เวียนหัว 100→60). Not adopted; recorded as a promising preliminary result. [4.6, table 4]

**Caption lines**
- EN: "A sign starts when the hand moves and ends when it is still, then becomes 30 frames."
- EN: "Handling left and right hands lifted accuracy on new signers by about 16 points."
- EN: "Measuring the hand from the face helped some words and hurt others, so we did not adopt it."

**Judge questions (study these)**
- How does MediaPipe find a hand? (palm detector, then 21 landmarks; runs on the device)
- What if no hand is found? (zeros; the rule treats a long gap as the end of a sign)
- Why 0.008? (NOT written down anywhere I could find: confirm with your team how it was chosen, and answer honestly. What the paper does say is that this motion-based rule replaced an older fixed 0.5 s window, and that training and the web app use the same rule.)
- Why do left and right slots differ between people? (MediaPipe's labels assume a mirrored picture; they are not reliably a person's anatomical hands)

---

## Step 3  LSTM guesses the word  (green)  |  the model, how we test it, and how sure it is

**One line:** a small LSTM reads the 30 frames and names the word; we compared it with the same model plus DANN, always testing on a signer the model has never seen, and the system says "not sure" when its confidence is below a per-word threshold.

**Cards**
| Card | File |
|---|---|
| ~~The 5 rounds~~ moved to RESULT (user's decision, 11 Nov): `fig16_loso_rounds.png` (method view) and `fig16r_loso_result.png` (each test cell with an arrow to its accuracy, plain LSTM vs DANN) | |
| Plain LSTM vs LSTM + DANN | `fig20_dann_card.png` |
| The DANN idea (explanatory, not our result) | `fig21_dann_idea.png`, or your own drawing |
| Concept: a confidence threshold per word (moved here from the old step 4) | `fig25_threshold_th.png` / `fig25_threshold_en.png` |
| Evidence: promised vs actual accuracy | `fig26_threshold_evidence_th.png` / `fig26_threshold_evidence_en.png` |
| Where the model gets confused (RESULT) | `fig13_confusion_final28.png` |

**Facts**
- Plain model: LSTM 2 layers × 32 units, dropout 0.5, dense 16 (ReLU), softmax over the words. [3.3]
- DANN adds a signer-classifier head (dense 16, softmax over the training signers) behind a gradient reversal layer; weight λ is 0 for the first 10 epochs, then 0.5. The extra head is used only in training. [3.3]
- Settings fixed before testing: 60 epochs, learning rate 0.001, batch 16, no early stopping, 3 random seeds; nothing is tuned on the test signer. [3.4]
- Leave-one-signer-out: 5 rounds; signs tested per held-out signer 2,464 / 993 / 2,409 / 643 / 126. [summary.md]
- Random split 84.8 ± 6.8% against 51.9% for unseen signers on 28 words: a gap of 33 points. [4.3]
- Plain LSTM per signer: S01 59.1 · S02 64.3 · S03 51.5 · S04 37.0 · S05 47.6 (mean 51.9). [summary.md]
- DANN: mean 46.3% against 51.9%, a difference of −5.6 points (95% interval −8.1 to −3.0), worse for all 5 signers. The rule was set beforehand: DANN counts only if it gains at least 2.0 points, wins in at least two thirds of signers, and the interval excludes zero. [4.4]
- The signer head reached only 31–45% on training clips (chance 25%), so the signer was only partly hidden. Even when it saw unlabelled clips of the new signer, DANN stayed 5.5–5.8 points worse. [4.4]
- Averaging 3 models lifts the mean from 51.9% to 57.9%; the web app uses a single model. [4.7]

**Caption lines**
- EN: "Below the threshold the system says \"not sure\" instead of guessing."
- EN: "A threshold set on seen signers promised 95.4% but delivered 66.2% on a new signer."
- TH: "เกณฑ์ที่ตั้งจากผู้แสดงที่เคยเห็นสัญญา 95.4% แต่ได้จริงกับผู้แสดงใหม่ 66.2%"
- EN: "Each round holds out one signer the model has never seen."
- EN: "DANN tries to make the model forget who is signing. In our test it did not help."
- EN: "Settings were fixed before testing, so nothing was tuned on the test signer."

**Judge questions (study these)**
- What is DANN and why did you try it? (see the 20-second script in the chat; student-and-detective analogy)
- Why did it not help? (few training signers make the signer easy to tell apart; hiding the signer did not improve word recognition; 3 or 5 signers is a small test)
- Why a plain LSTM and not BiLSTM or attention? (My suggested answer, please confirm it is true for your team: it is small enough to run in the browser, and DANN does not depend on the network type. The paper cites Thai work with LSTM, GRU and BiLSTM on 10 words reaching 99%, but that was on a small word set.)

### Confidence threshold (part of step 3)
**Facts** (table 6, section 4.7; unseen signers, 6,635 signs, average of 3 models)
| How the threshold was set | Accuracy of accepted answers | Share of signs answered |
|---|---|---|
| From a random split (measured on its own test set) | 95.4% | 92% |
| Same threshold on the held-out signer | 66.2% | 72% |
| From other signers only | 76.7% | 47% |
| From the same signer (reference, not usable in practice) | 91.4% | 54% |
- Target was 90% accuracy of accepted answers. Per signer with the "other signers" method: S01 81.6, S02 83.6, S03 74.4, S04 57.5, S05 52.6; S04 and S05 (portrait, close to the camera) are furthest from target.
- A single threshold set from 10 / 20 / 40 / 80 labelled clips of the new signer gives 74.1 / 78.9 / 82.1 / 89.1% (answering 15–23% of signs): about 80 clips are needed to approach the target, which is not practical.
- Biggest confusions (plain LSTM, fig13): ไอ → น้ำมูกไหล 55% (82 signs), ยา → แพ้ยา 41%, ตา → น้ำมูกไหล 41%, รอ → แพ้ยา 41%, ฉัน ↔ ต้องการ 37% / 36%.
- Exploratory only: a "variant" flag from pre-training data flags pairs that fail more often (55% vs 26%, p = 0.009), but this comes mainly from S04 and S05; without them it is 31% vs 27%.

(Caption lines for these cards are in the list above.)

**Judge questions**
- Does it work well enough to use? → Not yet: 76.7% with the best setting, and it answers only 47% of signs. We report this instead of hiding it; the next step is calibration with the club's members.
- Why say "not sure"? → A wrong confident answer is worse than asking the signer to repeat.

---

## Step 4  Build the sentence and output  (blue)  |  PROTOTYPE, not evaluated

**One line:** the predicted words are put into a sentence and shown as text and speech; the face is read only as numbers to tell questions and negation. This part has not been evaluated with volunteers, so label it as a prototype.

**Cards**
| Card | File |
|---|---|
| Words to sentence and voice (prototype) | **to draw** |

**Facts** (all from the paper, which marks this as a prototype)
- After the LSTM names the words, sentence rules add "ไหม" for a question and "ไม่" for a negation; the result is shown as text and spoken by the browser's text-to-speech. [3.1]
- Question versus statement, and yes versus no, are carried by facial expression in Thai Sign Language, according to the deaf club. [2.1]
- Face reading uses MediaPipe Face Landmarker: eyebrow raise, eyebrow furrow and head angle relative to the user's neutral face, kept as numbers (no face images). Rules: shaking the head 2 or more times = negation; eyebrows raised or furrowed beyond a threshold = question. [3.5]
- "This part has not yet been evaluated with volunteers." [3.5]
- An optional online language model (Typhoon) can arrange a sentence, but only on a machine with a key set; it is not part of the published system and not described in the paper. Do not present it.
- Speech output: the browser's own voice; the app's privacy page says that if the device has no Thai voice and the user allows it, the sentence text is sent to Google for speech. [app, privacy page]

**Do not show a sentence the system cannot produce.** The old poster's example ("ขอใช้แลกเบอร์โทรได้ไหมครับ?") uses words that are not in our 28-word list. A sentence that uses our words: คุณ + ต้องการ + ยา + raised eyebrows → "คุณต้องการยาไหม?" (an example, not a measured result).

**Caption lines**
- EN: "Prototype: words become a sentence, shown as text and speech. Not yet evaluated with users."
- TH: "ต้นแบบ: คำถูกเรียบเรียงเป็นประโยค แสดงเป็นข้อความและเสียง ยังไม่ได้ประเมินกับผู้ใช้"

**Judge questions**
- Did you test the sentence step? → No. It is a prototype; the paper says it has not been evaluated with volunteers. The tested parts are steps 1–3.
- Why use the face? → The club told us that facial expression separates questions from statements and yes from no; we only read it as numbers.

---

## Still missing / to confirm
1. ~~Recording protocol~~ answered: ~100 repeats per word, no formal script. (Whether signers lowered their hands between repeats is still not recorded.)
2. English versions still to do: fig15, fig16, fig18, fig19, fig20 (step 1 is done: fig11, fig14a/b, fig17, fig22 have `_en`).
3. Whether the club agrees to be named on the poster and in the footnote.
4. Study list: MediaPipe and keypoints, LSTM, DANN, selective classification, and the full limitations list (saved in memory).
