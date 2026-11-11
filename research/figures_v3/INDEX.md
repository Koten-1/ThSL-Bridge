# ThSL Bridge figures, by step

Final set in `research/figures_v3/`. Superseded versions are in `_superseded/`. TH = Thai text, EN = English text.

## Overview
_Your own Canva System Overview panel is the main one. fig24 is an alternative whose step 4 does not match your definition (it shows answer-or-not-sure, now part of step 3)._

| Figure | TH | EN |
|---|---|---|
| Alternative 4-step overview (not your definition) | `fig24_overview4_th.png` | `fig24_overview4_en.png` |
| Visual abstract | `fig10_graphical_abstract.png` | to do |
| Both directions of the system (spare) | `fig23_system_overview.png` | `fig23_system_overview_en.png` |
| Research design chart, 5 groups (spare: repeats the left pipeline) | `fig12_research_design.png` | `fig12_research_design_en.png` |

## Step 1  ทำท่าภาษามือผ่านกล้อง (Sign in front of the camera)
_Tracker: trackers4/tracker4_1.png_

| Figure | TH | EN |
|---|---|---|
| Recording workflow | `fig22_collection_workflow.png` | `fig22_collection_workflow_en.png` |
| What the data looks like | `fig17_data_look.png` | `fig17_data_look_en.png` |
| How the dataset is organised | `fig14a.png` | `fig14a_en.png` |
| Signs per signer (S01 + S03 = 73%) | `fig14b.png` | `fig14b_en.png` |
| 7,267 videos to 6,688 signs | `fig11_data_funnel.png` | `fig11_data_funnel_en.png` |

## Step 2  อ่านมือด้วย MediaPipe (Read the hands with MediaPipe)
_Tracker: trackers4/tracker4_2.png_

| Figure | TH | EN |
|---|---|---|
| How a sign is cut to 30 frames | `fig15_capture_timeline.png` | `fig15_capture_timeline_en.png` |
| Left-right hand handling | `fig18_leftright_card.png` | to do |
| Hand position relative to the face | `fig19_face_relative_card.png` | to do |

## Step 3  LSTM เดาคำศัพท์ (LSTM guesses the word)
_Tracker: trackers4/tracker4_3.png. Includes the confidence threshold (moved from the old step 4)._

| Figure | TH | EN |
|---|---|---|
| Plain LSTM vs LSTM + DANN | `fig20_dann_card.png` | `fig20_dann_card_en.png` |
| The DANN idea (backup: you are drawing your own) | `fig21_dann_idea.png` | to do |
| Confidence threshold per word | `fig25_threshold_th.png` | `fig25_threshold_en.png` |
| Promised vs actual accuracy | `fig26_threshold_evidence_th.png` | `fig26_threshold_evidence_en.png` |

## Step 4  ประกอบประโยคและประมวลผล (Build the sentence and output)
_Tracker: trackers4/tracker4_4.png. PROTOTYPE, not evaluated with volunteers (paper 3.5)._

| Figure | TH | EN |
|---|---|---|
| Step 4 on the real demo: words + face become a sentence (prototype) | `fig27_demo.png` | `fig27_demo_en.png` |

## RESULT panel
_New first-glance cards (r = result version), all with TH and EN._

| Figure | TH | EN |
|---|---|---|
| Random split vs unseen signer: 84.8 vs 51.9 (hero) | `fig6r_random_vs_unseen.png` | `fig6r_random_vs_unseen_en.png` |
| 5 rounds with results: plain LSTM vs DANN per signer | `fig16r_loso_result.png` | `fig16r_loso_result_en.png` |
| Left-right handling: +16 points | `fig3r_handedness.png` | `fig3r_handedness_en.png` |
| Per-word accuracy in three buckets | `fig2r_per_word.png` | `fig2r_per_word_en.png` |
| Which words get confused (matrix + top mix-ups) | `fig13r_confusion.png` | `fig13r_confusion_en.png` |
| Face-relative per word: 6 better, 3 worse | `fig4r_face_relative.png` | `fig4r_face_relative_en.png` |
| The 5 rounds, method view (no results) | `fig16_loso_rounds.png` | `fig16_loso_rounds_en.png` |

## Older versions and spares
_fig1, fig2, fig3, fig6 are kept in place because the report and slide builders read these file names_

| Figure | TH | EN |
|---|---|---|
| OLD per signer, plain vs DANN (same data as fig16r) | `fig1_per_signer_plain_vs_dann.png` | to do |
| OLD per-word bars (replaced by fig2r) | `fig2_per_word_heldout.png` | `../figures_v4_thai/fig2_per_word_heldout.png` |
| OLD left-right bars (replaced by fig3r) | `fig3_handedness.png` | to do |
| OLD random vs signer split (replaced by fig6r) | `fig6_random_vs_signer_split.png` | to do |
| OLD confusion matrix (replaced by fig13r) | `fig13_confusion_final28.png` | to do |
| OLD face-relative (replaced by fig4r) | `fig4_face_relative.png` | `../figures_v4_thai/fig4_face_relative.png` |
| Data growth | `fig5_growth.png` | to do |
| Same word, different signers | `fig7_chan_tongkan_handshape.png` | to do |
| One hand vs two hands | `fig8_pawdhua_one_vs_two_hands.png` | to do |
