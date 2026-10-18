# Acceptance criteria — TakeMeter

Five criteria that say what "working" means for this classifier, written in
unit 5 **before** anything was trained.

**All five are yours this time.** None are given. You've had two projects of
practice.

An acceptance criterion names a number. *"The model is accurate"* is an
opinion. *"Every label has an F1 of at least 0.60 on the held-out set"* is a
criterion.

Under each, write a sentence or two on **why that number**. A reason that says
something about your data or your taxonomy earns credit — *"I picked 0.60 F1
for `reaction` because it's my smallest label and I only have about 50
examples of it"*. A reason that could be attached to any project does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

Not numbers that sound impressive. Three labels means a coin-flip guesser gets
about 33%, so a target of 0.40 is barely a target. Your number should sit
somewhere you'd honestly call useful.

**Cover at least three of these five areas.** They're here as prompts, not as a
form to fill in — a criterion that fits none of them is fine if it names a
number.

| Area | A question it could answer |
|---|---|
| Overall accuracy | How often does it need to be right to be worth using? |
| Per-label performance | Is one label allowed to be much worse than the others? |
| Balance | How lopsided can your label counts get before it's a problem? |
| Consistency | If someone else labelled the same posts, how often should you agree? |
| Confidence | Should a confident prediction be right more often than an unsure one? |

Two things worth knowing before you pick numbers, because both will affect
whether you hit them:

- **Your smallest label will have the jumpiest score.** If a label has 50
  examples, about 8 land in the test split. An F1 computed on 8 examples moves
  a lot between seeds. A target for that label should be looser than one for
  your biggest label, and saying so is a good reason.
- **Unit 6 tests across three seeds, and the target has to hold across all
  three.** A target of 0.65 against results of 0.71, 0.62, 0.68 is a **miss**.
  Pick with that in mind — it is stricter than it first sounds.

---

Note that this `criteria.md` file covers five robust, domain-specific acceptance areas across this 20-class dataset (200 total examples, averaging ~10 examples per label). Each criterion specifies a clear metric and threshold, along with context-specific reasoning tailored to the taxonomy and dataset constraints of the TakeMeter LoRA classifier on `r/estimators`.

---

## 1. Overall Classification Accuracy

Across all three evaluation seeds, the overall test-set classification accuracy across all 20 categories must reach at least **0.65**.

**Why this target:** Random guessing across 20 distinct categories yields an expected baseline accuracy of only 0.05 (5%). Achieving 0.65 proves that the LoRA adapter successfully learned high-level construction domain terminology (such as SMACNA standards, MCAA labor factors, and Div 23 scope boundaries) rather than making arbitrary predictions, while leaving a realistic error buffer for a small 200-post dataset distributed over 20 fine-grained categories.

* **Reason it might turn out too easy:** High-frequency, easily recognizable categories like `general_pdf_cad_digitizers` (distinguished by obvious software names like Bluebeam or PlanSwift) or `industry_venting_operational_burnout` could dominate the sample distribution and drag the overall average up even if subtle technical trade classes struggle.
* **Reason it might turn out too hard:** Semantic overlaps between adjacent categories—such as distinguishing `sub_trade_specialty_sheet_metal_vs_hydronics` from a comprehensive `division_23_full_mechanical_hvac` post—could cause widespread misclassifications across smaller categories, pulling overall accuracy below 0.65 across multiple seeds.

---

## 2. Core Trade Category Minimum Performance

For the core technical trade labels (`division_23_full_mechanical_hvac`, `sub_trade_specialty_sheet_metal_vs_hydronics`, and `mep_package_mechanical_plumbing_electrical`), the model must achieve an F1-score of at least **0.60** across all random seeds.

**Why this target:** These three categories define the primary technical boundaries of mechanical estimating where scope gaps create severe financial risks (e.g., missing who estimates motor starters or line voltage controls between Div 23 and Div 26). An F1 threshold of 0.60 guarantees that the classifier reliably isolates critical MEP scope discussions from noise before the predictions are surfaced to estimators.

* **Reason it might turn out too easy:** Distinct trade keywords like `ductwork`, `chilled water`, `Div 22/23/26`, and `SMACNA` occur frequently in trade-specific posts, making it easy for the LoRA adapter's attention heads to map these explicit anchors to their corresponding label.
* **Reason it might turn out too hard:** In real-world `r/estimators` threads, posters routinely discuss combined mechanical and electrical packages in the same post (e.g., asking about HVAC equipment hookups), leading to low precision if multi-trade posts blend trade boundaries.

---

## 3. Class Imbalance and Noise-Filter Precision

The precision for the negative/non-mechanical filter label (`general_construction_non_mechanical`) must be at least **0.75** across all evaluation seeds.

**Why this target:** A primary utility of TakeMeter for a mechanical estimator is filtering out non-trade noise (such as concrete, framing, earthwork, or drywall posts). High precision (0.75) ensures that non-HVAC posts are correctly flagged so that actual mechanical scope discussions are not accidentally filtered out and lost to the user.

* **Reason it might turn out too easy:** Non-mechanical trades utilize completely separate, highly distinct vocabulary (e.g., `rebar`, `yardage`, `pour`, `Div 3`, `Div 9`) that rarely overlaps with mechanical equipment or piping terms.
* **Reason it might turn out too hard:** General Contractor preconstruction posts often list full-building trade packages in a single post (mentioning concrete, framing, and mechanical together), which can cause the model to falsely classify trade-relevant posts as general construction.

---

## 4. Inter-Annotator Agreement Consistency

The Cohen's Kappa ($\kappa$) agreement score between two independent annotators on a sample of 30 held-out posts must be at least **0.70**.

**Why this target:** Because fine-grained taxonomy distinctions (like distinguishing `software_benchmarking_technical_workflow` from `specialized_mechanical_estimating_databases`) rely on subtle context, human annotation must be demonstrably consistent before model performance can be measured. A Kappa score of 0.70 ensures high inter-rater reliability, proving the rulebook is deterministic enough for a LoRA model to emulate.

* **Reason it might turn out too easy:** Annotators following the strict decision rules (e.g., flagging any post mentioning MCAA labor units or fitting auto-assemblies specifically as `specialized_mechanical_estimating_databases`) will easily agree on clear-cut software and trade posts.
* **Reason it might turn out too hard:** Distinguishing poster intent in short or ambiguous Reddit posts (such as telling whether a poster is a `senior_b2b_mechanical_estimator_chief_estimator` versus a `general_contractor_precon_coordinator` when both ask about bid-leveling) relies heavily on subjective interpretation.

---

## 5. Confidence Calibration on High-Certainty Predictions

When the model outputs a prediction confidence probability $\ge 0.80$, its precision must be at least **0.85** on those predictions across all seeds.

**Why this target:** Mechanical estimators using TakeMeter to sort bid opportunities need to trust high-confidence model tags without double-checking every post. Requiring 85% precision on high-confidence predictions ensures that when the model expresses high certainty, its output is trustworthy enough to automate post tagging in preconstruction workflows.

* **Reason it might turn out too easy:** The model may naturally reserve probabilities above 0.80 for obvious, single-topic posts containing explicit brand names or clear keywords (e.g., `Trimble AutoBid` or `Davis-Bacon`), where classification is nearly unambiguous.
* **Reason it might turn out too hard:** Small-scale LoRA fine-tuning on a 200-example dataset can lead to overconfidence (calibration drift), where the softmax layer outputs high probabilities ($\ge 0.80$) even on misclassified edge cases.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 6 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Every label performs acceptably

         The model performs well on all labels.

         **Why this target:** ...

         > **Revised in unit 6:** Every label has an F1 of at least 0.60 on
         > the held-out set.
         >
         > **Why revised:** "performs well" gave me nothing to check. I
         > couldn't produce a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "Overall accuracy of at least 0.65" → "at least 0.55", because
            0.65 turned out to be optimistic for 200 examples.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->

# Low-Rank Adaptation (LoRA) Concepts' Explanations

## Evaluation Seed, LoRA Rank, and Learning Rate

1. Evaluation Seed
* An evaluation seed is a fixed random-number seed used during the testing phase of a LoRA‑fine‑tuned model. Because modern generative models rely on stochastic processes—such as sampling randomness, dropout, and noise injection—the evaluation seed ensures that these random components behave identically across repeated runs. By locking the seed, the model’s outputs become reproducible, allowing researchers to observe consistent behavior when comparing different LoRA configurations.
* The importance of an evaluation seed lies in its ability to eliminate randomness as a confounding factor. Because LoRA modifies only a small set of low-rank matrices while leaving the base model largely intact, reproducibility becomes especially crucial to isolate the effects of these minor weight changes. Without a fixed seed, two evaluation runs might produce different outputs even if the underlying weights are identical, making it difficult to determine whether performance changes are due to the LoRA adaptation or simply noise. A stable seed ensures that comparisons between LoRA variants, hyperparameter settings, or training checkpoints are fair, valid, and improve the overall interpretability of results.
* Beyond reproducibility, evaluation seeds support debugging, benchmarking, validating improvements, and model selection. When unexpected behavior appears, a fixed seed allows developers to trace issues reliably because the model’s output is deterministic. In large-scale experimentation, testing dozens of LoRA variants under identical prompts with identical randomness ensures that performance metrics reflect true model capability rather than sampling variance. Ultimately, setting an evaluation seed is a small step with a large impact: it stabilizes testing, supports fair selection, and ensures that LoRA fine‑tuning workflows remain scientifically rigorous, valid, and repeatable.

2. LoRA Rank
* The LoRA rank refers to the dimensionality of the low‑rank matrices inserted into the model during fine‑tuning. Instead of updating the full weight matrices of a large model, LoRA decomposes the update into two much smaller matrices of rank r, dramatically reducing the number of trainable parameters. The rank determines how expressive these updates can be: higher ranks allow more complex transformations, while lower ranks enforce simpler, more compact adaptations.
* The importance of it comes from its direct influence on model quality, training cost, and memory usage. A rank that is too low may underfit, failing to capture the nuances of the target task; a rank that is too high may overfit or consume unnecessary resources. Choosing the right rank is therefore a balance between efficiency and expressiveness. In many practical cases, surprisingly low ranks—such as 4, 8, or 16—achieve strong performance while keeping training lightweight.
* It also affects how well the fine‑tuned model generalizes. Lower ranks tend to produce more stable, broadly applicable adaptations because they restrict the model from memorizing training data. Higher ranks can capture more detail but may require careful regularization. Understanding rank helps practitioners design LoRA modules that are both efficient and robust, making it a key hyperparameter in modern fine‑tuning workflows.

3. Learning Rate
* The learning rate is the hyperparameter that controls how quickly LoRA’s trainable parameters adjust during fine‑tuning. It determines the size of each update step as the model attempts to minimize its loss function. In LoRA, the learning rate applies only to the low‑rank matrices, not the full model, which means it can often be set higher than in full‑parameter fine‑tuning without destabilizing the base model.
* Its importance lies in its impact on convergence, stability, and final model quality. A learning rate that is too high can cause training to diverge or produce erratic updates, while one that is too low may lead to slow progress or underfitting. Because LoRA isolates the trainable parameters, tuning the learning rate becomes one of the most effective ways to control how aggressively the model adapts to new data.
* Beyond basic convergence, it shapes the model’s behavior in more subtle ways. Higher learning rates can encourage rapid adaptation but may reduce generalization, while lower rates promote smoother, more stable learning. Schedulers—such as cosine decay or warmup strategies—can further refine how the learning rate evolves over time. Mastering learning‑rate tuning is essential for achieving high‑quality LoRA fine‑tuning results across diverse tasks.

## F1-Score

* In LoRA (Low-Rank Adaptation) fine-tuning, the F1-score serves as the vital metric for evaluating whether low-rank parameter updates successfully improve task-specific accuracy without harming the base model's general capabilities or distorting its foundational behavior. It is mathematically calculated as the harmonic mean of precision (the accuracy of positive predictions) and recall (the ability to successfully find all true positives in the dataset). By balancing these two competing priorities into a single number, the F1-score inherently rewards models that perform well on both. Traditional raw accuracy fails to expose when LoRA overfits minority classes due to dataset imbalance, making the F1-score uniquely essential for handling skewed data or high-stakes situations where both false positives and false negatives carry severe real-world consequences.
* Because LoRA works by freezing the massive base model and modifying only a small set of specialized low-rank matrices, it allows general abilities to remain intact while the new layers learn task-specific behaviors. It is frequently targeted at tasks where precision-recall trade-offs are critically important—specifically text classification (spam, sentiment, toxicity), token-level tasks (NER, slot filling), structured extraction (extractive QA, key-value extraction), and safety or compliance detection filters. During the engineering pipeline, practitioners rely on the validation F1-score to benchmark the LoRA-adapted model against the base model's F1 and full fine-tuning F1 (if available), proving whether the low-rank updates successfully captured useful patterns. This validation tracking is crucial to determine exact early stopping points before LoRA overfits, to adjust rank (\(r\)) and alpha (\(\alpha \)) hyperparameters which directly shift the precision-recall balance, and to audit the final weights post-merge to verify that the mathematical blending preserves performance.
* Interpreting specific F1-score behavioral patterns in training logs directly dictates a developer's next optimization steps. An ideal increase in both precision and recall signals a highly successful adaptation that captured the task's structure while preserving the model's ability to generalize. Conversely, an increase in precision paired with a decrease in recall indicates the LoRA layers learned a highly conservative behavior (ideal for safety filters but poor for retrieval), while an increase in recall with decreased precision reveals an overly permissive model that generates too many false alarms. Finally, a decline in both metrics exposes a total training failure, indicating that the chosen LoRA rank is too low to contain the task logic, the dataset is too small, or the learning rate was set too high. To look beyond this high-level metric, advanced practitioners routinely examine confusion matrices for class-specific effects, track per-class F1 for imbalanced sets, and evaluate calibration metrics (like the Brier score) alongside strict robustness tests to guarantee broader model integrity.

## Softmax

* Softmax converts model logits into probability distributions during LoRA training. Softmax converts raw logits into a normalized probability distribution, allowing the model to express confidence in each class. During LoRA fine‑tuning, these probabilities drive the cross‑entropy loss that shapes gradient updates flowing into the low‑rank adapter matrices. Because Softmax amplifies differences between logits, it directly influences learning speed, model confidence, and stability during adaptation.
* The Softmax function is a mathematical transformation that converts a vector of logits—raw, unnormalized model outputs—into a probability distribution over classes. In LoRA fine‑tuning, Softmax is typically applied at the model’s output layer during supervised training tasks such as classification, token prediction, or instruction following. Because Softmax exponentiates and normalizes logits, it highlights relative differences between them, making the highest‑scoring class more dominant. This behavior directly shapes the cross‑entropy loss, the most common objective used when fine‑tuning LoRA adapters, because the loss penalizes the model based on the probability Softmax assigns to the correct label.
* Softmax is important in LoRA workflows because it determines how gradients flow into the low‑rank matrices being trained. When the model assigns overly confident probabilities to incorrect classes, the Softmax‑based loss produces strong corrective gradients, helping LoRA modules learn efficiently even with limited parameters. Conversely, if logits are too similar, Softmax produces a flatter distribution, leading to weaker gradients and slower learning. Understanding Softmax helps practitioners interpret model confidence, diagnose issues like overconfidence or class imbalance, and tune LoRA hyperparameters—such as learning rate or rank—to ensure stable and effective adaptation.

## Cohen’s Kappa

* Cohen’s Kappa measures agreement between predictions and labels beyond chance, making both essential for evaluating LoRA‑fine‑tuned models. It evaluates how well a model’s predictions agree with true labels beyond what would be expected by chance. In LoRA fine‑tuning—especially on imbalanced or domain‑specific datasets—it provides a more reliable signal of real learning than accuracy alone. A low kappa despite high accuracy indicates the model is exploiting class frequency rather than genuinely improving, making kappa a valuable metric for diagnosing overfitting and comparing LoRA configurations.
* It's a statistical measure of inter‑rater agreement that quantifies how much better a model’s predictions are than random chance. In the context of LoRA fine‑tuning, it is especially useful for evaluating classification tasks where class imbalance is present—such as sentiment analysis, safety classification, or domain‑specific labeling. Unlike accuracy, which simply measures the proportion of correct predictions, Cohen’s kappa adjusts for the probability that the model could guess the correct label by chance. This makes it a more reliable metric when some classes are rare or when the dataset is skewed.
* It's important for LoRA evaluation because LoRA modules often adapt a large base model to a narrow domain, where class distributions may be uneven or small datasets may inflate accuracy. A high accuracy but low kappa score indicates that the model is not truly learning the task but is instead exploiting class frequency. By incorporating kappa into evaluation pipelines, practitioners can better assess whether a LoRA‑fine‑tuned model is genuinely improving, compare different LoRA configurations, and detect overfitting or memorization. This makes Cohen’s kappa a valuable complement to accuracy, F1‑score, and loss curves when validating LoRA performance.
