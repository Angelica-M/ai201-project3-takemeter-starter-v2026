# What `baseline.py` is, why I ran it, what it produced, and what it means

A plain-language guide to the zero-shot baseline in this project (unit 6, milestone 1). It explains the idea first, then the file, the commands I ran, where every output lives, how to read the numbers, and what they tell me about my dataset and my trained model.

**The short version**
- `baseline.py` is a *control experiment*. It asks a general-purpose model, with **no training at all**, to label the same 31 held-out posts my fine-tuned model was tested on, using only my written label definitions.
- It got **4 of 31 right (accuracy 0.129, macro F1 0.060)** and mostly failed in one way: it called 19 of the 31 posts `software_vendor_sales_representative`.
- Putting my trained model next to it (accuracy 0.258) showed something more important than who "won": the trained model only ever predicted **two** labels, `industry_venting_operational_burnout` and `career_pathing_compensation_hiring`. That is a data-skew problem, not a modelling success.

---

## 1. Why a baseline exists

A single accuracy number means nothing on its own. If my trained model scores 26%, is that good? It depends on how hard the task is. A **baseline** is the answer to "what happens if I do almost nothing?" Whatever my trained model scores has to be judged against it:

- If the trained model beats the baseline by a lot, the training taught it something real.
- If it only matches the baseline, the training added nothing, which is a legitimate finding and not a failure.
- If the baseline is already very good, the task was easy and the fine-tuning wasn't needed.

`baseline.py` is the course's fair opponent. It is "fair" because it gets the same posts and the same information a human labeller would have (my label definitions), but no examples to learn from.

## 2. What `baseline.py` actually is

`baseline.py` is a script supplied with the course starter. It runs **zero-shot classification** with a model called **`facebook/bart-large-mnli`**.

**Zero-shot** means classifying into categories the model was never trained on. This particular model was trained on a different job, *natural language inference* (NLI): given a piece of text (the *premise*) and a statement (the *hypothesis*), decide whether the text supports ("entails") the statement.

The script turns my classification problem into that job:

1. For every candidate label it builds a hypothesis sentence from my definition using the template `"This post is {definition}."`, for example: *"This post is Frustration-driven posts highlighting bid-day stress, last-minute addendums, unrealistic GC deadlines, and industry friction points."*
2. For each post it asks the model how strongly the post entails each of those sentences.
3. The candidate with the highest score wins and becomes the predicted label.

Two consequences worth knowing:
- It can never invent a label or reply with a sentence. It can only pick from the list I gave it.
- It is only as good as my definitions. They are its **entire** prompt. The model has never seen one of my 204 posts.

## 3. What goes in

| Input | What it is | Where |
|---|---|---|
| The posts to score | The 31 held-out posts the notebook saved when it trained my model, so both models face the same posts | `test_split.csv` |
| The label definitions | My 21 definitions, copied word for word from the README's Label Taxonomy (the baseline's whole prompt) | `label_definitions.txt` |
| The label list | Built from the labels that actually appear in my data | `data/labels.csv` |

Because the label list comes from my data, the baseline chose among **16 labels**, not 21. Five labels have no posts at all (`division_23_full_mechanical_hvac`, `sub_trade_specialty_sheet_metal_vs_hydronics`, `mep_package_mechanical_plumbing_electrical`, `service_replacement_retrofit_bidding`, `field_tech_residential_installer_apprentice`), so they were never offered as options.

## 4. How I ran it, and in what order

The order matters for honesty, because a prediction only counts if it is written before the answer is known.

1. **Fill in `label_definitions.txt`.** It was still the course template (`analysis` / `hot_take` / `reaction`), so I replaced it with my 21 definitions (commit `044a0a4`).
2. **Run the baseline alone:**
   ```
   python baseline.py --data data/labels.csv
   ```
   `--data data/labels.csv` is needed because my labelled file lives in `data/`, while the script looks for `labels.csv` in the repo root by default. The first run downloads the model (about 1.6 GB) and takes a few minutes on a laptop CPU, because the model spends a few seconds on each post. It wrote `baseline_results.json`, also committed in `044a0a4`.
3. **Write the prediction before looking at the trained numbers**, and commit it on its own (commit `8083f71`).
4. **Run the comparison:**
   ```
   python baseline.py --data data/labels.csv --trained results.json
   ```
   This reruns the baseline and adds a **Trained** column from `results.json`, which the notebook wrote in unit 5. It prints a table ready to paste into the README.
5. **Paste the table into the README** under "Baseline vs. Trained" (commit `1b8a166`).

## 5. Where the output lives

| Output | Where to find it |
|---|---|
| Baseline numbers and every prediction | `baseline_results.json`: keys `model`, `n`, `seed`, `held_out` (true = scored on `test_split.csv`), `used_definitions`, `scores` (`accuracy`, `f1_macro`, `per_label` precision/recall/F1/support) and `predictions` (each post with its true label and the baseline's guess) |
| The Baseline vs. Trained table | README, section "Baseline vs. Trained" |
| The trained model's numbers | `results.json` (from the notebook's section 5). The comparison only *prints* its Trained column and does not store it in `baseline_results.json` |
| Terminal text | Not saved to a file. The two things it reports (the headline numbers and the table) are in the files above |

Confirmation that it was a fair comparison is in the run's output: *"Reading the held-out posts from test_split.csv — the same ones your trained model was scored on."* It did not fall back to a random sample.

## 6. What the baseline produced

**Accuracy 0.129 (4 of 31 correct) and macro F1 0.060.**

The only labels with any credit:

| Label | Baseline F1 | Test posts |
|---|---|---|
| `general_contractor_precon_coordinator` | 0.500 | 2 (1 right) |
| `industry_venting_operational_burnout` | 0.364 | 8 (2 right) |
| `software_vendor_sales_representative` | 0.100 | 1 (1 right) |
| every other label | 0.000 | |

The failure had a clear shape. The baseline predicted `software_vendor_sales_representative` for **19 of the 31** posts, although only one test post has that label. Its biggest error groups were 5 venting posts, 4 career posts and 3 general-construction posts all labelled as vendor posts. It never predicted `career_pathing_compensation_hiring` (7 test posts) or `general_construction_non_mechanical` (4) at all.

Why might that happen? One reasonable hypothesis (not something I tested): zero-shot models are sensitive to wording. A definition like "self-promotional pitches, demo offers, or vendor-driven product marketing" overlaps with the language of many estimating-software posts, so it wins the entailment score for posts that merely *talk about* software. Rewording the definitions would be the way to test that.

## 7. How to read these numbers (a short course in metrics)

- **Accuracy:** the share of posts it got right. With 31 posts, one post is worth about 3.2 points, so small differences are noise.
- **Precision:** of the posts it labelled X, how many really were X.
- **Recall:** of the posts that really were X, how many it found.
- **F1:** one number combining the two (their harmonic mean). It is 0 if either is 0.
- **Support:** how many true posts of that label are in the test set. An F1 with support 1 or 2 is almost meaningless: one lucky or unlucky guess swings it from 0 to 1.
- **Macro F1:** the plain average of the per-label F1 scores, so every label counts equally however rare. It is harsh on a model that ignores small labels.
- **Reference points:** random guessing over 21 labels gets about 0.048. The **majority-label guess** ("always say the most common label") scores **0.258** on this test set, because 8 of the 31 posts are `industry_venting_operational_burnout`. Any model has to clear that bar before it has learned anything about the content.

By that yardstick the baseline's 0.129 is well below the "always guess venting" strategy, and above random guessing. It is a *weak* opponent, which matters for how much a win over it means.

## 8. What the second command showed: baseline vs. trained

| Measure | Baseline | Trained |
|---|---|---|
| Overall accuracy | 0.129 (4/31) | 0.258 (8/31) |
| Macro F1 as printed | 0.060 | 0.061 |
| `industry_venting_operational_burnout` F1 | 0.364 | 0.364 |
| `career_pathing_compensation_hiring` F1 | 0.000 | 0.308 |
| `general_contractor_precon_coordinator` F1 | 0.500 | 0.000 |
| `software_vendor_sales_representative` F1 | 0.100 | 0.000 |
| every other label | 0.000 | 0.000 |

(All figures are the seed-42 run only. The full per-label table is in the README.)

**What the trained model actually did.** Reading its confusion matrix in `results.json`: it made **only two kinds of prediction** on the 31 posts, `industry_venting_operational_burnout` (25 times) and `career_pathing_compensation_hiring` (6 times). Of its 8 correct answers, 6 were venting and 2 were career. Every post from the other nine labels that appear in the test set was labelled as venting or career. That is the classic result of training on skewed data: the model learned how common each label is, not what the posts say. The training set is 36 venting + 34 career out of 142, and the three most common labels hold most of the data.

**The tie with the majority guess is a coincidence of counts.** Its 8 correct matches the 8 you would get from always guessing venting, but the model is not doing that (it also predicted career 6 times).

**A fairness catch on macro F1.** The two macro F1 figures above are not computed over the same list of labels:
- `baseline.py` averages over the 16 labels in my data, so labels with no test posts count as 0.
- The notebook (scikit-learn) averages only over labels that occur in the test posts or were predicted: 11 labels for the trained model.

Putting both on the same list changes the picture:

| Macro F1 over... | Baseline | Trained |
|---|---|---|
| the 16 labels in my data | 0.060 | 0.042 |
| the 11 labels with at least one test post | 0.088 | 0.061 |

So the trained model is **better on accuracy but not on macro F1**. The two metrics disagree because accuracy rewards getting more posts right overall (8 vs 4), while macro F1 rewards getting *some* credit on many labels (the baseline scored on three labels, the trained model on two). I computed this from the two JSON files; the README table prints the numbers as the scripts produced them.

## 9. My prediction against what happened

The prediction was committed in `8083f71` before the comparison table existed (full text in Appendix A).

| Claim in the prediction | What happened |
|---|---|
| Accuracy between 0.35 and 0.45 | **Missed.** 0.258 (8/31), three posts short of the range |
| Outperforms the baseline's 0.129 | **Hit.** 0.258 vs 0.129 |
| Outperforms the majority-class guess of 0.258 | **Missed.** It tied it |
| Venting and career "learned robustly" | **Partly.** F1 0.364 and 0.308, hardly robust |
| The three zero-train labels fail completely | **Hit.** All three at 0.000 |
| 128-token truncation hurts fuzzy boundaries | **Untested.** This comparison cannot show it either way |

The prediction's reasoning (skew caps the result) was right, and its number was too optimistic. Its "LoRA adapter" wording was also inaccurate: the notebook fully fine-tunes `distilbert-base-uncased` with no LoRA.

## 10. What it means for the project

- **The baseline is a weak control.** It can be beaten on accuracy by a model that mostly says "venting". So "beat the baseline" is a low bar here, and I should lean on the majority-label guess and macro F1 as the stricter tests.
- **The main problem is the data, not the model.** 5 labels have no posts, 3 have no training posts, 3 more have exactly one training post, and two labels hold 51% of the data. With 142 training posts spread over 21 labels, the model has little to learn from for most labels.
- **Likely fixes** (for the unit 6 improvement step, not yet done): collect more posts for the thin labels, merge or drop labels that cannot be learned, make the split stratified, and rewrite the definitions that attract the wrong posts.
- **Preliminary read on my criteria** (one seed, so not a verdict): overall accuracy 0.258 is far under Criterion 1's 0.65, and all five technical labels in Criterion 2 scored 0.000 for the trained model. The three-seed run in the notebook's section 6 is what the criteria are judged on.

## 11. Limits of this result

- **31 test posts, one seed.** One post is 3.2 points of accuracy. A different seed gives a different test split and different numbers, which is why unit 6 runs three seeds.
- **The split was not stratified.** Several labels have a single post, so the notebook fell back to a plain random split. Some labels have zero test posts and cannot be measured at all.
- **The labels were assigned by Gemini, not by hand,** so both models are scored against labels that have their own noise (28% of posts had a top-two score gap of 10 points or less).
- **The baseline saw 16 labels and the trained model 21** output slots, and the two macro F1 figures use different label lists (section 8).
- **128 tokens.** The trained model reads only about the first 100 words of each post. The median post is about 116 words and 54% are longer. The baseline can read far more of each post, up to its model's much longer limit.

---

## Appendix A: the prediction, as committed in `8083f71`

> I predict the fine-tuned LoRA model will achieve an overall test accuracy between 0.35 and 0.45—comfortably outperforming the baseline score of 0.129 and the majority-class guess of 0.258, yet capped by severe data skew. While high-frequency categories like `industry_venting_operational_burnout` (36 train) and `career_pathing_compensation_hiring` (34 train) will be learned robustly by the adapter, the model will completely fail on the three zero-train labels (`public_works_prevailing_wage_bidding`, `software_vendor_sales_representative`, and `commercial_institutional_industrial`) that hold 4 test instances. Additionally, the model's 128-token truncation limit will cut off longer posts (where the 90th percentile spans ~1,880 characters), exacerbating classification errors on fuzzy category boundaries like operational venting versus bid strategy scope gaps where semantic score gaps are already narrow.

The prediction is my own. It was written from the data analysis in Appendix B, and that analysis (the tables and counts) was generated by Claude Code from my files.

## Appendix B: the data analysis the prediction was based on (seed-42 split)

**What the trained model learns from** (204 posts: 142 train, 31 validation, 31 test)

| Label | All | Train | Test |
|---|---|---|---|
| `industry_venting_operational_burnout` | 55 | 36 | 8 |
| `career_pathing_compensation_hiring` | 49 | 34 | 7 |
| `general_construction_non_mechanical` | 23 | 15 | 4 |
| `software_benchmarking_technical_workflow` | 16 | 15 | 1 |
| `emerging_ai_automation_tools` | 16 | 10 | 2 |
| `bid_strategy_scope_gaps_gc_relations` | 12 | 8 | 2 |
| `enterprise_erp_bidding_platforms` | 10 | 7 | 1 |
| `general_contractor_precon_coordinator` | 8 | 6 | 2 |
| `general_pdf_cad_digitizers` | 5 | 5 | 0 |
| `unrelated` | 3 | 3 | 0 |
| `public_works_prevailing_wage_bidding` | 2 | **0** | 2 |
| `software_vendor_sales_representative` | 1 | **0** | 1 |
| `commercial_institutional_industrial` | 1 | **0** | 1 |
| 3 labels with 1 post each (`specialized_mechanical_estimating_databases`, `multi_family_residential_tract_housing`, `senior_b2b_mechanical_estimator_chief_estimator`) | 1 each | 1 each | 0 |
| 5 labels with no posts | 0 | 0 | 0 |

The three labels with 0 train posts have 4 test posts between them. A model cannot learn a label it never saw in training.

**How much of each post a model reads.** The median post is 633 characters (about 116 words) and the 90th percentile is about 1,880 characters. The trained DistilBERT reads only the first 128 tokens, so it mostly sees the opening of each post.

**How clear the labels are** (Gemini's score gap between its top two choices when it labelled the data; a small gap means a fuzzy boundary). The mean gap overall is 22.7 points. The fuzziest labels are `general_contractor_precon_coordinator` (10.8), `enterprise_erp_bidding_platforms` (10.9), `bid_strategy_scope_gaps_gc_relations` (13.3) and `software_benchmarking_technical_workflow` (15.2). The clearest are `general_construction_non_mechanical` (27.4), `career_pathing_compensation_hiring` (26.2) and `unrelated` (71.7, only 3 posts). Common mix-ups: venting vs `bid_strategy_scope_gaps_gc_relations`, career vs venting, and software benchmarking vs `general_pdf_cad_digitizers` or `emerging_ai_automation_tools`.

**Reference accuracies:** random guessing over 21 labels 0.048; baseline 0.129; always guessing `industry_venting_operational_burnout` 0.258.

## Appendix C: how this file was produced

The figures come from `data/labels.csv`, `test_split.csv`, `baseline_results.json` and `results.json`, computed with small scripts (not typed by hand). The explanatory text, the data analysis in Appendix B and the macro-F1 cross-check were written with AI assistance (Claude Code); the prediction in Appendix A was not. Re-derive any number here by re-running `python baseline.py --data data/labels.csv --trained results.json` and reading `baseline_results.json` and `results.json`.
