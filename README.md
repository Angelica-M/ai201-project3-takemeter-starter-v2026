# TakeMeter

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, the
> notebook, the baseline, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> head -5 data/practice_labels.csv     # the shape your labels.csv needs
> ```
>
> Then open `takemeter.ipynb` **in this folder** — in VS Code, or with
> `jupyter notebook` if you prefer. Pick the kernel: the `.venv` inside this
> project. Run section 1, which reports the hardware you'll be training on.
> Everything else waits until you have data.
>
> Nothing to upload, nothing to connect, no accounts and no keys. The notebook
> runs on your machine and writes next to your code.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     Unit 5 asks for the first five sections. Unit 6 adds the five below them.

     Everything is pasted as TEXT. No screenshots, no images.

     ⚠️ The confusion matrix especially. The notebook prints one as a markdown
     table, ready to copy. A screenshot of a matrix earns nothing. Paste the
     table.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 5 — THE BUILD ═══════════════════════ -->

## What This Does
<!-- Your community, and what your classifier sorts posts into. 3-4 sentences. -->

## What This Does: Your community, and what your classifier sorts posts into.

TakeMeter targets **r/estimators**, a specialized online Reddit community where construction estimators, preconstruction managers, trade contractors, and software vendors discuss plan takeoffs, bidding strategies, software tools, and industry practices. The posts in this subreddit range from highly technical discussions about sheet metal weight calculations and complex mechanical scope gaps to general career questions, software sales pitches, and bid-day frustration posts. To analyze and categorize (label) these posts effectively, TakeMeter sorts incoming community content into five core taxonomy distinctions:

* All 6 Taxonomy Distinctions are
* **Trade Scope & Division Boundaries** (with a total of 4 categories that are: Division 23 (Full Mechanical/HVAC), Sub-Trade Specialty (Sheet Metal vs. Hydronics/Piping), MEP Package (Mechanical/Plumbing/Electrical), and General Construction / Non-Mechanical)
* **Software Stack & Tooling Architecture** (with a total of 4 categories that are: General PDF & CAD Digitizers, Specialized Mechanical Estimating Databases, Enterprise ERP & Bidding Platforms, and Emerging AI & Automation Tools)
* **Project Sector & Delivery Model** (with a total of 4 categories that are: Commercial / Institutional / Industrial (Mid–Large B2B), Multi-Family Residential / Tract Housing, Service, Replacement & Retrofit Bidding, and Public Works / Prevailing Wage Bidding)
* **Operational Intent & Post Purpose** (with a total of 4 categories that are: Software Benchmarking & Technical Workflow, Bid Strategy, Scope Gaps & GC Relations, Career Pathing, Compensation & Hiring, and Industry Venting & Operational Burnout)
* **Poster Role & Expertise Level** (with a total of 4 categories that are: Senior B2B Mechanical Estimator / Chief Estimator, General Contractor (GC) Precon Coordinator, Field Tech / Residential Installer / Apprentice, and Software Vendor / Sales Representative)
* **Unrelated** (a single stand-alone category to catch any input posts that do not meet or closely align with any of the other Taxonomy Distinctions and their categories)

By establishing these distinct boundaries, the LoRA (Low Rank Adaptation) classifier evaluates both the technical scope and user intent behind every post, allowing high-value peer expertise and technical queries to be sorted cleanly from marketing noise, career advice, and entry-level discussions.

---

## Label Taxonomy
<!-- Each label: a one-sentence definition and two real examples from your
     reading. Then your decision rule for the hardest boundary.
     The decision rule is worth a point on its own and it's the thing most
     people leave out. Every taxonomy has a hardest boundary. Name yours. -->

### `division_23_full_mechanical_hvac` 

**Definition:** Posts covering entire building mechanical and environmental control systems under a single prime mechanical quote, combining sheet metal, equipment schedules, and hydronic piping.
* **Label 1:** *Division 23 (Full Mechanical/HVAC)* — **Taxonomy Distinction 1:** *Trade Scope & Division Boundaries*

**Example 1:**
> We are bidding a complete Div 23 package on a 4-story medical office building, including the chillers, AHUs, and ductwork installation.

**Example 2:**
> Looking for feedback on how to structure our prime HVAC package bid form when RTU and VRF options are both listed as add-alternates.

### `sub_trade_specialty_sheet_metal_vs_hydronics`

**Definition:** Discussions strictly focused on granular trade-specific takeoffs such as ductwork weight/gauge calculations, fitting counts, or specialized piping materials.
* **Label 2:** *Sub-Trade Specialty (Sheet Metal vs. Hydronics/Piping)* — **Taxonomy Distinction 1:** *Trade Scope & Division Boundaries*

**Example 1:**
> What labor factor do you apply per pound of heavy-gauge welded ductwork versus standard SMACNA spiral duct?

**Example 2:**
> Need advice on calculating fitting counts and linear footage for a large chilled water PEX supply line takeoff in PlanSwift.

### `mep_package_mechanical_plumbing_electrical`

**Definition:** Posts resolving scope overlaps, omissions, or package coordination boundaries between mechanical, plumbing, and electrical trades.
* **Label 3:** *MEP Package (Combination Mechanical/Plumbing/Electrical)* — **Taxonomy Distinction 1:** *Trade Scope & Division Boundaries*

**Example 1:**
> Who typically covers the line voltage controls and motor starters on your jobs—the Div 23 mechanical sub or Div 26 electrical?

**Example 2:**
> How do you catch scope gaps between Div 22 plumbing condensate drains and Div 23 equipment hookups during preconstruction review?

### `general_construction_non_mechanical`

**Definition:** Queries focused strictly on non-HVAC trade takeoffs, acting as a negative filter for structural, civil, or architectural trade discussions.
* **Label 4:** *General Construction / Non-Mechanical* — **Taxonomy Distinction 1:** *Trade Scope & Division Boundaries*

**Example 1:**
> Estimating concrete slab yardage and rebar quantities for a tilt-wall warehouse expansion using Bluebeam Revu.

**Example 2:**
> What is the average square-foot unit price you use for Div 9 drywall and metal framing on commercial interior buildouts?

### `general_pdf_cad_digitizers`

**Definition:** Discussions centered on manual 2D quantity extraction, scale calibration, drawing markups, and basic PDF takeoff software without trade-specific database assemblies.
* **Label 5:** *General PDF & CAD Digitizers* — **Taxonomy Distinction 2:** *Software Stack & Tooling Architecture*

**Example 1:**
> Having trouble getting custom columns and tool chest symbol counts to export cleanly from Bluebeam Revu to Excel.

**Example 2:**
> What is the best way to calibrate page scales across overlay drawings when vector PDFs have distorted dimensions?

### `specialized_mechanical_estimating_databases`

**Definition:** Technical queries evaluating database software that automatically calculates fitting counts, material pricing feeds, and MCAA labor unit hours per unit.
* **Label 6:** *Specialized Mechanical Estimating Databases* — **Taxonomy Distinction 2:** *Software Stack & Tooling Architecture*

**Example 1:**
> How does Trimble AutoBid Mechanical compare to FastPIPE when setting up custom auto-fitting assembly rules and labor multipliers?

**Example 2:**
> Is anyone integrating Harrison Publishing pricing feeds directly into QuoteSoft to keep material costs updated automatically?

### `enterprise_erp_bidding_platforms`

**Definition:** High-level workflow discussions regarding invitation to bid (ITB) management, subcontractor bid matrix creation, and ERP accounting synchronization.
* **Label 7:** *Enterprise ERP & Bidding Platforms* — **Taxonomy Distinction 2:** *Software Stack & Tooling Architecture*

**Example 1:**
> How are you handling bid coverage tracking and ITB distribution through BuildingConnected vs Procore Bid Board?

**Example 2:**
> Looking for best practices when transferring awarded estimate job costs from ConstructConnect into Spectrum ERP.

### `emerging_ai_automation_tools`

**Definition:** Experimental or analytical posts evaluating AI, machine learning, OCR, or scripts for automated plan indexing and symbol counting.
* **Label 8:** *Emerging AI & Automation Tools* — **Taxonomy Distinction 2:** *Software Stack & Tooling Architecture*

**Example 1:**
> Has anyone tested Togal.ai or TakeoffBuilder for auto-detecting equipment symbols on vector mechanical sheets?

**Example 2:**
> I wrote a Python script using OCR to parse drawing spec books and auto-link equipment schedules to plan callouts.

### `commercial_institutional_industrial`

**Definition:** High-value B2B plan-and-spec or design-build project estimates requiring formal specification reviews, unit pricing breakdowns, and structured bid forms.
* **Label 9:** *Commercial / Institutional / Industrial (Mid–Large B2B)* — **Taxonomy Distinction 3:** *Project Sector & Delivery Model*

**Example 1:**
> Bidding a $4M plan-and-spec central plant overhaul for a university campus with strict long-lead equipment requirements.

**Example 2:**
> How do you handle submittal addendums and RFI clarifications when pricing a commercial hospital expansion under a design-build model?

### `multi_family_residential_tract_housing`

**Definition:** Repetitive wood-frame residential or apartment estimating based on price-per-square-foot, per-unit, or per-door metrics.
* **Label 10:** *Multi-Family Residential / Tract Housing* — **Taxonomy Distinction 3:** *Project Sector & Delivery Model*

**Example 1:**
> What is your typical price-per-door or per-unit estimate for DX split system installs on a 200-unit multi-family apartment complex?

**Example 2:**
> Estimating wood-frame tract housing HVAC layouts using piece-rate labor pricing instead of detailed commercial sheet metal takeoffs.

### `service_replacement_retrofit_bidding`

**Definition:** Quick-turnaround commercial service bids, equipment changeouts, or time-and-material quotes with short diagnostic-to-quote cycles.
* **Label 11:** *Service, Replacement & Retrofit Bidding* — **Taxonomy Distinction 3:** *Project Sector & Delivery Model*

**Example 1:**
> How do you factor crane rigging and roof curb adaptor costs when quoting a rapid weekend Carrier RTU replacement?

**Example 2:**
> Looking for standard T&M labor rates and markup percentages on commercial HVAC preventive maintenance service agreements.

### `public_works_prevailing_wage_bidding`

**Definition:** Government or public sector bidding involving certified payroll, Davis-Bacon prevailing wage determinations, and strict sealed bid procedures.
* **Label 12:** *Public Works / Prevailing Wage Bidding* — **Taxonomy Distinction 3:** *Project Sector & Delivery Model*

**Example 1:**
> How do you adjust your labor pricing models when bidding public school projects subject to local prevailing wage rates?

**Example 2:**
> Dealing with MWBE/DBE subcontracting goals and bonding limits on a sealed bid public works municipal building.

### `software_benchmarking_technical_workflow`

**Definition:** Posts evaluating features, pricing tiers, system stability, and speed efficiency across competing estimating software platforms.
* **Label 13:** *Software Benchmarking & Technical Workflow* — **Taxonomy Distinction 4:** *Operational Intent & Post Purpose*

**Example 1:**
> Comparing PlanSwift vs Trimble AutoBid: is the database setup time worth the upgrade for a 10-person estimating team?

**Example 2:**
> Our digitizer software keeps crashing on 200MB CAD vector sheets—looking for benchmark recommendations for smoother workflow performance.

### `bid_strategy_scope_gaps_gc_relations`

**Definition:** Operational posts on protecting profit margins, managing incomplete drawings, writing exclusions, and handling general contractor bid deadlines.
* **Label 14:** *Bid Strategy, Scope Gaps & GC Relations* — **Taxonomy Distinction 4:** *Operational Intent & Post Purpose*

**Example 1:**
> How do you protect your quote against scope creep when GC drawings are only 60% CDs on bid day?

**Example 2:**
> What standard exclusions list do you attach to your mechanical proposals to avoid eating unpriced GC scope gaps?

### `career_pathing_compensation_hiring`

**Definition:** Discussions regarding estimator compensation packages, remote work options, workload expectations, and career advancement paths.
* **Label 15:** *Career Pathing, Compensation & Hiring* — **Taxonomy Distinction 4:** *Operational Intent & Post Purpose*

**Example 1:**
> What is the market compensation rate and bonus structure for a Senior Mechanical Chief Estimator in a major metro area?

**Example 2:**
> Is 5 full commercial plan takeoffs per week a reasonable workload expectation for a junior estimator working remotely?

### `industry_venting_operational_burnout`

**Definition:** Frustration-driven posts highlighting bid-day stress, last-minute addendums, unrealistic GC deadlines, and industry friction points.
* **Label 16:** *Industry Venting & Operational Burnout* — **Taxonomy Distinction 4:** *Operational Intent & Post Purpose*

**Example 1:**
> GC sent out a 150-page addendum 2 hours before the bid due date and still expects full itemized breakdowns.

**Example 2:**
> Tired of working weekends doing takeoffs only for GCs to ghost us on bid results and re-bid the project three months later.

### `senior_b2b_mechanical_estimator_chief_estimator`

**Definition:** Posts authored by experienced professionals demonstrating deep industry terminology, calibrated labor multipliers, and strategic risk management.
* **Label 17:** *Senior B2B Mechanical Estimator / Chief Estimator* — **Taxonomy Distinction 5:** *Poster Role & Expertise Level*

**Example 1:**
> After 20 years as Chief Estimator, here is how we calibrate MCAA labor units against historical shop performance data to maintain a 25% win rate.

**Example 2:**
> My rule of thumb for overhead recovery on $5M+ mechanical packages is to isolate equipment quotes from field labor units before applying burden.

### `general_contractor_precon_coordinator`

**Definition:** Posts written from the buyer perspective evaluating how subcontractor quotes are reviewed, leveled, and combined into a prime bid.
* **Label 18:** *General Contractor (GC) Precon Coordinator* — **Taxonomy Distinction 5:** *Poster Role & Expertise Level*

**Example 1:**
> From the GC precon side: why do mechanical subs wait until 10 minutes before bid closing to submit their scope sheets?

**Example 2:**
> What is your process for leveling three wildly different HVAC subcontractor quotes when scope inclusions are missing?

### `field_tech_residential_installer_apprentice`

**Definition:** Entry-level or field-focused posts seeking guidance on transitioning into the office, reading blueprints, or beginner tools.
* **Label 19:** *Field Tech / Residential Installer / Apprentice* — **Taxonomy Distinction 5:** *Poster Role & Expertise Level*

**Example 1:**
> Just transitioned from being a field HVAC tech to junior estimator—what is the easiest way to learn blueprint reading and scale takeoffs?

**Example 2:**
> Field installer moving into office precon next month—looking for recommendations on software tutorials for someone starting from scratch.

### `software_vendor_sales_representative`

**Definition:** Posts or replies containing self-promotional pitches, demo offers, or vendor-driven product marketing.
* **Label 20:** *Software Vendor / Sales Representative* — **Taxonomy Distinction 5:** *Poster Role & Expertise Level*

**Example 1:**
> DM me if you'd like to schedule a quick demo of our platform—we auto-detect mechanical symbols and export straight to Excel.

**Example 2:**
> We solved this exact problem with our automated AI takeoff software—check out our website for a 14-day free trial.

### `unrelated` 

**Definition:** Catch-all category for posts that fall entirely outside construction precon, bidding, and estimating software—such as generic financial advice, unrelated software programming queries, random spam, or general sub trades asking non-estimating jobsite questions.
* **Label 21:** *Unrelated* — **Taxonomy Distinction 6:** *Unrelated*

**Example 1:**
> What are the best Tax-Free Savings Account (TFSA) index funds for long-term passive investing if I want to retire in my 50s?

**Example 2:**
> Does anyone have a good python script to automatically download attached PDF invoices from Outlook emails and save them to a local Google Drive folder?

### The 1st Hardest Boundary
<!-- e.g. "If the post names a specific checkable fact, it's `analysis`, even
     if the tone is heated." -->

**Which two labels:**
`general_pdf_cad_digitizers` vs. `specialized_mechanical_estimating_databases`
Distinction is difficult because both categories share the same surface‑level functions:
both measure lengths and areas, allow markup, import PDFs or CAD files, and export quantities.  This overlap means that a post or product description may look mechanical, even when the underlying tool is just a general digitizer. The main sources of confusion are: 
* **Shared core functionality**: Every digitizer measures drawings, so measurement alone is not a reliable indicator.
* **Trade context does not guarantee specialization**: A general digitizer used by an HVAC estimator is still general‑purpose; the trade context is misleading.
* **Marketing language is vague**: Many tools advertise “HVAC takeoff” or “MEP workflows” without offering true mechanical automation.
* **Partial feature sets**: Some tools include one mechanical feature (e.g., duct symbols) but lack assemblies, labor databases, or pricing—making them hybrid and hard to classify.
* **User workflows mask tool capability**: Estimators often build their own assemblies manually inside general tools, making the tool appear specialized when it isn’t.

**The decision rule I used every time:**
1. Specialized MEP/HVAC digitizers add domain‑specific automation that ties measurements to mechanical systems; these features transform raw geometry into mechanical assemblies, not just measurements. Classify it as `specialized_mechanical_estimating_databases`, if the post describes trade-specific features that automatically translate measurements into mechanical components (e.g., MCAA/PHCC labor units, fitting/elbow auto-assembly generation, pressure‑class logic, or live material pricing feeds). More specifically, these are the tasks automatic fitting and elbow generation based on duct/pipe routing, MCAA or PHCC labor units tied to each component, material pricing feeds from suppliers, system‑aware assemblies (e.g., duct sections with hangers, insulation, transitions), trade‑specific rules (e.g., pressure class, gauge, joint type), and automatic BOM creation for mechanical systems.
2. General CAD/PDF digitizers focus purely on universal measurement and markup tasks; these tools are intentionally trade‑agnostic. They work for architecture, civil, landscaping, electrical, plumbing, HVAC, or any discipline because they only measure geometry. If the post focuses solely on manual spatial measurement (these are universal measurement tasks like length, area, and count takeoffs), drawing scaling, basic annotation and markup (general markup tools), or tools related to generic PDF/CAD navigation tools or exporting quantitites to spreadsheets functions (without any automated mechanical assemblies or trade‑specific databases), classify it as `general_pdf_cad_digitizers` regardless of the trade context mentioned (even if the user is performing HVAC or piping takeoff).

### The 2nd Hardest Boundary 

**Which two labels:**
`general_construction_non_mechanical` vs. `unrelated`

**The decision rule I used every time:**
If a post discusses preconstruction workflows, takeoff measurements, bluebeam markups, or material/labor pricing for non-HVAC construction trades (such as concrete, framing, or electrical), classify it under its respective trade category or `general_construction_non_mechanical`. Classify a post as `unrelated` **only** if it contains no construction estimation, bidding, takeoff, or precon content whatsoever (e.g., general personal finance, non-estimating coding scripts, jobsite safety memes, or spam).

---

## The Dataset

<!-- Where you collected from, how you labelled, your counts, and 3 hard cases. -->

**Where the posts came from:**
All 204 posts are text (self) posts from **r/estimators**, collected in October 2026 by `build_dataset.py` through Reddit's public Atom search feeds (`search.rss`, no login). Three searches were run, each asked for 100 posts not already in `labels.csv`:
1. Top (All Time): `self:true (guide OR megathread OR analysis OR "deep dive")`
2. Hot: the same keyword query
3. Top (All Time): `self:true` alone, to supply posts the keyword searches could not (those two together only contain about 105 posts)

281 rows were collected in total; 77 repeated posts (identical column 1) were then removed, keeping the first copy of each, which leaves **204 unique posts**. Each post is its title plus its full body text.

**How I labelled them:**
Every label and note was produced by the Gemini API (`gemini-3.1-flash-lite`), not by hand. For each post the script sent the full text, the role "expert HVAC estimator / MEP construction expert", the 21 label definitions from the Label Taxonomy above and the two hardest-boundary decision rules, and asked for the single best-fit label plus a runner-up, each with a 0-100 match score and a one-sentence reason. Column 3 stores that ranking in the form "Highest semantic match of X% for [label] (with 2nd highest of Y% as [label]) due to [reason]". The first 20 rows carry a `cold` tag at the start of their note, as the project spec asks; those labels were also assigned by Gemini. This section does not claim a manual re-check of the labels.

**Counts per label:**

| Label | Count | Share |
|---|---|---|
| `division_23_full_mechanical_hvac` | 0 | 0.00% |
| `sub_trade_specialty_sheet_metal_vs_hydronics` | 0 | 0.00% |
| `mep_package_mechanical_plumbing_electrical` | 0 | 0.00% |
| `general_construction_non_mechanical` | 23 | 11.28% |
| `general_pdf_cad_digitizers` | 5 | 2.451% |
| `specialized_mechanical_estimating_databases` | 1 | 0.49% |
| `enterprise_erp_bidding_platforms` | 10 | 4.90% |
| `emerging_ai_automation_tools` | 16 | 7.84% |
| `commercial_institutional_industrial` | 1 | 0.49% |
| `multi_family_residential_tract_housing` | 1 | 0.49% |
| `service_replacement_retrofit_bidding` | 0 | 0.00% |
| `public_works_prevailing_wage_bidding` | 2 | 0.98% |
| `software_benchmarking_technical_workflow` | 16 | 7.84% |
| `bid_strategy_scope_gaps_gc_relations` | 12 | 5.88% |
| `career_pathing_compensation_hiring` | 49 | 24.02% |
| `industry_venting_operational_burnout` | 55 | 26.96% |
| `senior_b2b_mechanical_estimator_chief_estimator` | 1 | 0.49% |
| `general_contractor_precon_coordinator` | 8 | 3.92% |
| `field_tech_residential_installer_apprentice` | 0 | 0.00% |
| `software_vendor_sales_representative` | 1 | 0.49% |
| `unrelated` | 3 | 1.47% |
| **Total** | **204** | 100% |

Five labels have no posts at all (`division_23_full_mechanical_hvac`, `sub_trade_specialty_sheet_metal_vs_hydronics`, `mep_package_mechanical_plumbing_electrical`, `service_replacement_retrofit_bidding`, `field_tech_residential_installer_apprentice`), and the two largest labels hold 51% of the data together. The guide / analysis style of search pulls in long discussion posts, which skew towards career and venting topics.

**Three hard cases**

<!-- Any post that made you pause: what it was, which 2 labels it could have been, and 
     what you chose. These are worth more than the easy 190. -->

These are the three posts where Gemini's top two scores were closest (a 5-point gap each; the next closest gap in the dataset is 7 points). Post text is shortened with "…"; the full text is in `data/labels.csv`.

**1.**
> *The post:* "New Siding Estimator Wanting Mentor — Hey everyone, I had to join a cat subreddit to get enough karma to post. I am 4 months in with a skins company that brought me in to start bidding siding on Multifamily, comm, mixed…bigger projects. I had no estimating experience. …" (about 3,900 characters)
>
> *Could have been:* `career_pathing_compensation_hiring` (90%) or `general_construction_non_mechanical` (85%)
>
> *Labelled (by Gemini) as `career_pathing_compensation_hiring`, because:* the post is mainly a request for career mentorship from a newcomer to estimating, even though the trade it discusses (siding and exterior wall systems) is non-mechanical.

**2.**
> *The post:* "Better sub-network vs existing (Bluebook, Procore, Planhub) — Hey all, Some of you probably know me as the author of a few AI applications in precon posts … I'm working to build a better subcontractor network for the industry. Think of it as an updated Bluebook (better data, more vetted profiles, GCs kno…" (about 2,000 characters)
>
> *Could have been:* `enterprise_erp_bidding_platforms` (90%) or `general_contractor_precon_coordinator` (85%)
>
> *Labelled (by Gemini) as `enterprise_erp_bidding_platforms`, because:* the post is mostly about improving bidding platforms and subcontractor networks (enterprise-level tools), although it is written from the GC precon coordinator's point of view.

**3.**
> *The post:* "Downtobid app review from a GC estimator — What is Downtobid? In their own language, Downtobid is an AI construction bidding platform for GCs and subs. It's supposed to: Streamline bid invites / ITBs and deadlines. Analyze your drawings and plans, identify scopes, draft invite emails … " (about 10,200 characters)
>
> *Could have been:* `enterprise_erp_bidding_platforms` (95%) or `software_benchmarking_technical_workflow` (90%)
>
> *Labelled (by Gemini) as `enterprise_erp_bidding_platforms`, because:* it is a detailed technical review, but what it evaluates is a bidding / ITB management platform, which falls squarely under the enterprise bidding category.

---

## The Training Run

<!-- Your starting model, your settings, and anything you changed and why. -->

**Base model:** `distilbert-base-uncased`, fine-tuned for 21-way text classification (the 21 labels in the Label Taxonomy).

**Settings:** 3 epochs, learning rate 2e-5, batch size 16, 128 tokens per post, seed 42. **Trained on: `cpu`** (device name "CPU", torch 2.14.1+cpu, Windows 11 machine, no GPU). The device is also recorded in `results.json`, because different hardware can give slightly different numbers for the same seed.

**Anything I changed from the defaults, and why:** The training settings are all the notebook's defaults. The only edits to `takemeter.ipynb` were setup: my name and email, `LABELS` set to my 21 labels, and `CSV` pointed at `data/labels.csv` (where `build_dataset.py` writes my data) instead of `labels.csv` in the repo root. The notebook's code cells were run from a script with the project's `.venv` Python rather than inside the VS Code notebook window.

**Split sizes:** 204 posts split 142 train / 31 validation / 31 test. The notebook could not stratify the split, because several labels have only one post, so it fell back to a plain random split (that is a warning about the dataset, not the split). Test split per label:

| Label | Test posts |
|---|---|
| `industry_venting_operational_burnout` | 8 |
| `career_pathing_compensation_hiring` | 7 |
| `general_construction_non_mechanical` | 4 |
| `emerging_ai_automation_tools` | 2 |
| `public_works_prevailing_wage_bidding` | 2 |
| `bid_strategy_scope_gaps_gc_relations` | 2 |
| `general_contractor_precon_coordinator` | 2 |
| `enterprise_erp_bidding_platforms` | 1 |
| `software_benchmarking_technical_workflow` | 1 |
| `commercial_institutional_industrial` | 1 |
| `software_vendor_sales_representative` | 1 |
| All other 10 labels (including the 5 with no posts at all) | 0 |

Only one label reaches the 8-post mark in test, so every other label's F1 will swing a lot between seeds, and 10 labels cannot be measured at all on this split. That will explain much of next unit's variance.

**How Criterion 2 is measured, and why it has a bootstrap confidence interval:** With a test split of about 31 posts, a per-label F1 is mostly luck, and 21 separate ones would be 21 untrustworthy numbers. So `criteria.md` Criterion 2 asks for one number per seed: the macro F1 (the average of the per-label F1 scores) over five core technical estimating labels that each have at least 10 posts in the whole dataset, which must reach 0.60 on every seed with a standard deviation under 0.05 across the seeds. `macro_f1_ci.py` computes it from the confusion matrix that the notebook already saves in its results file, so nothing needs retraining.

The script also attaches a 95% bootstrap confidence interval to each seed's number. It takes the test posts, resamples them with replacement 2,000 times at the same size, recomputes the macro F1 on every resample, and keeps the middle 95% of those values. Its value is that it shows how much of the number is only the luck of which 31 posts ended up in the test split. If the interval contains 0.60, that seed can't honestly be called a pass or a fail; if it sits clearly above or below 0.60, the verdict is real. It does not capture the randomness of training itself, which is what the three seeds are for, and with this little data the intervals will be wide. That width is itself a finding about the dataset.

One disclosure about timing: Criterion 2 was reworded (which labels it covers and how it is computed) after the first single-seed training run had been executed, when its overall accuracy was already visible. The 0.60 target and the 0.05 spread limit were not changed, the five labels were chosen from their post counts in the dataset, not from any per-label score, and no three-seed run existed yet.



---

## How I Used AI

<!-- Two specific moments — what you asked, what came back, what you changed.

     ⚠️ Plus disclosure of any pre-labelling. If you had a model pre-label a
     batch and then read and corrected every one, say that. It's an allowed
     workflow and disclosing it costs you nothing. Not disclosing it is the problem. -->

**Moment 1: collecting the posts (Claude Code)**

- *What I asked for:* A scraper, `build_dataset.py`, that pulls 200 posts from r/estimators using the exact search `self:true (guide OR megathread OR analysis OR "deep dive")`, sorted Top / All Time, and writes them into `labels.csv`.
- *What came back:* Reddit's `.json` endpoints now return HTTP 403 to anyone who isn't logged in, so the first version fetched nothing. Claude Code tested the alternatives and found that the same search still works as a public Atom feed (`search.rss`, no login), which returns each post's full text. It then measured the limits instead of guessing: the keyword query only matches about 105 posts in total, no matter the sort or time window, so 200 was impossible with that query alone.
- *What I changed:* I added a Hot-sorted version of the keyword search and a third, broader `self:true` search (Top sort) to supply enough different posts. I set each search to collect 100 posts that are not already in `labels.csv`, kept new rows appending to the end of the file, and had the script remove repeated posts (keeping the first copy) before any labelling. Even so, only 204 unique posts were reachable, which is above the 150 floor but short of 200.

**Moment 2: labelling the posts (Gemini, called from my script)**

- *What I asked for:* For each post, one best-fit label out of my 21, with a runner-up and a 0-100 match score for each, in a fixed note format. The prompt gave Gemini the role "expert HVAC estimator for bids and takeoffs and expert in the MEP construction industry", my label definitions from the Label Taxonomy, and my two hardest-boundary decision rules.
- *What came back:* A JSON answer per post that the script validated (it had to be one of the 21 labels, and the top two had to differ). The first run produced no labels at all because the model I had picked was retired for new users (HTTP 404), and the next model allowed only 20 requests per day on the free tier. Retries and a fallback label would have written invented labels into the data, so the script now skips and retries instead, and rotates through the other Gemini models my key can see. All 204 final labels came from `gemini-3.1-flash-lite`.
- *What I changed:* I removed a hard-coded "pre-labelled, checked" note so every row carries Gemini's own ranked scores, made the script label only rows whose label is empty, and made it check that the text it sent still matches the row it writes to. I also removed the "cold" prefix from the code (the first 20 rows still carry it from an earlier run).

**Pre-labelling disclosure:** Every one, except for the first 20, of the 204 labels and notes in `labels.csv` was produced by the Gemini API (`gemini-3.1-flash-lite`), not by me. The notes in column 3 are Gemini's own explanations of its top two picks. The first 20 rows are tagged `cold` as the project spec asks, to denote that those labels were not assigned by Gemini but were assigned by human opinion; Gemini did help with the "notes" explanation section of those 20 rows. The label quality and the boundary behavior in the 3 hard cases above are Gemini's judgement applied to my definitions.

<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Baseline vs. Trained

<!-- Both models on the same posts. `python baseline.py --trained results.json`
     prints this table for you. -->

Both models scored the same 31 held-out posts in `test_split.csv` (seed 42). The baseline is zero-shot `facebook/bart-large-mnli` using my 21 label definitions and chose among the 16 labels present in my data; the trained model is the fine-tuned `distilbert-base-uncased` from the notebook. Output of `python baseline.py --data data/labels.csv --trained results.json`:

| Measure | Baseline | Trained | Difference |
|---|---|---|---|
| Overall accuracy | 0.129 | 0.258 | +0.129 |
| Macro F1 | 0.060 | 0.061 | +0.001 |
| F1 — `bid_strategy_scope_gaps_gc_relations` | 0.000 | 0.000 | +0.000 |
| F1 — `career_pathing_compensation_hiring` | 0.000 | 0.308 | +0.308 |
| F1 — `commercial_institutional_industrial` | 0.000 | 0.000 | +0.000 |
| F1 — `emerging_ai_automation_tools` | 0.000 | 0.000 | +0.000 |
| F1 — `enterprise_erp_bidding_platforms` | 0.000 | 0.000 | +0.000 |
| F1 — `general_construction_non_mechanical` | 0.000 | 0.000 | +0.000 |
| F1 — `general_contractor_precon_coordinator` | 0.500 | 0.000 | -0.500 |
| F1 — `general_pdf_cad_digitizers` | 0.000 | 0.000 | +0.000 |
| F1 — `industry_venting_operational_burnout` | 0.364 | 0.364 | +0.000 |
| F1 — `multi_family_residential_tract_housing` | 0.000 | 0.000 | +0.000 |
| F1 — `public_works_prevailing_wage_bidding` | 0.000 | 0.000 | +0.000 |
| F1 — `senior_b2b_mechanical_estimator_chief_estimator` | 0.000 | 0.000 | +0.000 |
| F1 — `software_benchmarking_technical_workflow` | 0.000 | 0.000 | +0.000 |
| F1 — `software_vendor_sales_representative` | 0.100 | 0.000 | -0.100 |
| F1 — `specialized_mechanical_estimating_databases` | 0.000 | 0.000 | +0.000 |
| F1 — `unrelated` | 0.000 | 0.000 | +0.000 |

**What my definitions were worth (the baseline run twice, on purpose):** the baseline above is the run that uses my 21 definitions from `label_definitions.txt`, and it is the baseline I report. I also ran it once with no definitions file, so it fell back to bare label names (`python baseline.py --data data/labels.csv --definitions no_definitions_on_purpose.txt --out baseline_results_bare_names.json`), on the same 31 posts:

| Baseline run | Overall accuracy | Macro F1 (over the 16 labels in my data) |
|---|---|---|
| With my definitions (reported above) | 0.129 (4/31) | 0.060 |
| Bare label names | 0.355 (11/31) | 0.215 |
| My trained model (for reference) | 0.258 (8/31) | 0.061 as printed (0.042 over the same 16 labels) |

So my definitions did not help the baseline, they cost it 0.226 of accuracy (11 posts versus 4 right). With definitions it predicted `software_vendor_sales_representative` for 19 of 31 posts; with bare names its guesses were spread across `general_contractor_precon_coordinator` (9), `general_construction_non_mechanical` (5), `bid_strategy_scope_gaps_gc_relations` (5) and others, and it gave `enterprise_erp_bidding_platforms` an F1 of 1.0 (on a single test post). The two runs agreed on only 4 of the 31 posts. A plausible reason, which I have not tested, is that my long definitions make the zero-shot model score on shared vocabulary instead of on the label's meaning. With 31 posts, 11 versus 4 correct is a large gap but still a small sample. Because the bare-names baseline is stronger than my trained model on both accuracy and macro F1, the trained model beats only the definitions-based baseline, not the bare-names one. The full results of the bare-names run are in `baseline_results_bare_names.json`.

**What I predicted before I looked:**
<!-- Milestone 1 asks you to write this BEFORE seeing the trained numbers. A
     prediction made afterwards isn't one. -->

I predict the fine-tuned LoRA model will achieve an overall test accuracy between 0.35 and 0.45—comfortably outperforming the baseline score of 0.129 and the majority-class guess of 0.258, yet capped by severe data skew. While high-frequency categories like `industry_venting_operational_burnout` (36 train) and `career_pathing_compensation_hiring` (34 train) will be learned robustly by the adapter, the model will completely fail on the three zero-train labels (`public_works_prevailing_wage_bidding`, `software_vendor_sales_representative`, and `commercial_institutional_industrial`) that hold 4 test instances. Additionally, the model's 128-token truncation limit will cut off longer posts (where the 90th percentile spans ~1,880 characters), exacerbating classification errors on fuzzy category boundaries like operational venting versus bid strategy scope gaps where semantic score gaps are already narrow.

**What the gap actually means:**
<!-- If the baseline matched your trained model, your fine-tuning added
     nothing — and that is a real finding, not a failure. Say it plainly. -->



---

## Run Log — Before

<!-- Five criteria across three seeds. The notebook's section 6 prints the
     spread table; the Target and Verdict columns are yours. -->

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

### Confusion matrix

<!-- ⚠️ TYPED AS A MARKDOWN TABLE. The notebook prints one ready to paste.
     An image of a matrix earns nothing. -->

| true \ predicted |  |  |  |
|---|---|---|---|
| **** |  |  |  |
| **** |  |  |  |
| **** |  |  |  |

**My biggest off-diagonal number, and what it means:**
<!-- Not "the model made mistakes" — WHICH boundary it didn't learn, and which
     direction. "7 real analysis posts were called hot_take and only 3 went the
     other way" is a direction, not just an error rate. -->



---

## Verdicts and Diagnoses

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across
     all three seeds, not turn up sometimes. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**

<!-- For each miss: the cause, and how you know. The four common causes are:
     too few examples for a label, a boundary you applied inconsistently, a
     genuinely hard label pair, and a task the model can't reach from this
     much data.

     ⚠️ Use your agreement report as evidence. It is the only instrument you
     have that can tell a LABELLING problem from a MODEL problem, and this
     section is graded on whether you used it that way. -->



---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** ___ / 30 = ___%

<!-- Nobody grades this number. A 60% who argues every disagreement from the
     stated rules beats a 95% who wrote "staff was right" nine times. Several
     of the 30 were chosen because they're genuinely ambiguous — you should be
     winning some of these. -->

**Disagreements**

<!-- Three lines each: the post, both labels, and who you think is right and
     why — grounded in the staff definitions you were both applying.

     Then sort each into one of three piles:
       (a) the rule covered it and I applied it loosely → a consistency problem
       (b) the rule genuinely doesn't say               → a gap in the definitions
       (c) the rule is ambiguous here and my reading is defensible → argue it.
           This is a legitimate win.

     Pile (a) is the one that matters most for your diagnosis: if you applied a
     written rule two different ways on 30 posts, that is direct evidence about
     what you did across your own 200. -->

**1.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**2.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**What the pattern in my disagreements tells me:**



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Run Log — After

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it didn't, say so. Relabelling that didn't help is a genuinely
     interesting result and earns full credit. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped. -->



**The gap between what I meant my labels to capture and what the model
learned:**
<!-- Two sentences. Your confusion matrix is the evidence. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 5

       [ ] criteria.md has five numbered criteria, each naming a NUMBER
       [ ] Each has a reason underneath tied to your data or taxonomy
       [ ] labels.csv: at least 150 rows, text/label/note, ONE file not split
       [ ] No label above 70%
       [ ] All five unit 5 sections have real content
       [ ] Label Taxonomy includes the decision rule for your hardest boundary
       [ ] The Dataset includes three hard cases
       [ ] results.json and test_split.csv committed (the notebook does this)
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 6

       [ ] Baseline vs. Trained table, with your prediction written beforehand
       [ ] Run Log — Before, five criteria across three seeds
       [ ] Confusion matrix TYPED AS A MARKDOWN TABLE
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, using the agreement report as evidence
       [ ] Agreement Report with every disagreement adjudicated
       [ ] One improvement, with Run Log — After
       [ ] What's Still Broken
       [ ] results_three_seeds_before.json, results_three_seeds_after.json,
           baseline_results.json and
           agreement_results.json committed
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
