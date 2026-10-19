# Run with Bash command "python build_dataset.py"
# Ensure "pip install google-generativeai requests" and "pip install python-dotenv" before use in .env file
import csv
import json
import os
import time
import requests
from dotenv import load_dotenv  # <--- ADD THIS
import google.generativeai as genai

# Load environment variables from the local .env file
load_dotenv()  # <--- ADD THIS

# 1. Configure Gemini API
# Ensure GEMINI_API_KEY is set in your environment variables
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Output file: the existing labels.csv the notebook reads (data/labels.csv), not a new file in the cwd.
OUTPUT_CSV = os.path.join("data", "labels.csv")
COLD_COUNT = 20          # first N rows get "cold" in the note column (labelled with no prior pass)
GEMINI_DELAY_SECONDS = 4 # pause between Gemini calls to stay under free-tier requests-per-minute limits
GEMINI_MAX_ATTEMPTS = 3  # retries per post before that post is skipped (never written with a made-up label)

TAXONOMY_LABELS = [
    "division_23_full_mechanical_hvac",
    "sub_trade_specialty_sheet_metal_vs_hydronics",
    "mep_package_mechanical_plumbing_electrical",
    "general_construction_non_mechanical",
    "general_pdf_cad_digitizers",
    "specialized_mechanical_estimating_databases",
    "enterprise_erp_bidding_platforms",
    "emerging_ai_automation_tools",
    "commercial_institutional_industrial",
    "multi_family_residential_tract_housing",
    "service_replacement_retrofit_bidding",
    "public_works_prevailing_wage_bidding",
    "software_benchmarking_technical_workflow",
    "bid_strategy_scope_gaps_gc_relations",
    "career_pathing_compensation_hiring",
    "industry_venting_operational_burnout",
    "senior_b2b_mechanical_estimator_chief_estimator",
    "general_contractor_precon_coordinator",
    "field_tech_residential_installer_apprentice",
    "software_vendor_sales_representative",
    "unrelated"  # 21st label: catch-all so the model is never forced into a bad fit
]

# Definitions copied (condensed) from README.md "## Label Taxonomy". Giving the model the definition of every label,
# grouped by the 6 taxonomy distinctions, is what lets it separate look-alike labels; names alone are too ambiguous.
LABEL_DEFINITIONS = f"""
Taxonomy Distinction 1 - Trade Scope & Division Boundaries:
- division_23_full_mechanical_hvac: Entire building mechanical/environmental systems under one prime mechanical quote (sheet metal + equipment schedules + hydronic piping).
- sub_trade_specialty_sheet_metal_vs_hydronics: Granular trade-specific takeoffs: duct weight/gauge, fitting counts, specialized piping materials.
- mep_package_mechanical_plumbing_electrical: Scope overlaps, omissions or coordination boundaries between mechanical, plumbing and electrical trades.
- general_construction_non_mechanical: Estimating for non-HVAC trades (concrete, framing, drywall, electrical, civil, architectural); a negative filter for non-mechanical trade talk.

Taxonomy Distinction 2 - Software Stack & Tooling Architecture:
- general_pdf_cad_digitizers: Manual 2D quantity extraction, scale calibration, markups, basic PDF takeoff tools (e.g. Bluebeam, PlanSwift) with no trade-specific assemblies.
- specialized_mechanical_estimating_databases: Database software that auto-calculates fittings, material pricing feeds and MCAA/PHCC labor units (e.g. AutoBid Mechanical, FastPIPE, QuoteSoft).
- enterprise_erp_bidding_platforms: ITB management, sub bid matrices, bid coverage tracking, ERP/accounting sync (e.g. BuildingConnected, Procore, ConstructConnect, Spectrum).
- emerging_ai_automation_tools: Experimental or analytical posts on AI, machine learning, OCR or scripts for automated plan indexing and symbol counting.

Taxonomy Distinction 3 - Project Sector & Delivery Model:
- commercial_institutional_industrial: High-value B2B plan-and-spec or design-build estimates with spec reviews, unit pricing and structured bid forms.
- multi_family_residential_tract_housing: Repetitive residential/apartment estimating priced per square foot, per unit or per door.
- service_replacement_retrofit_bidding: Quick-turnaround service bids, equipment changeouts, T&M quotes, short diagnostic-to-quote cycles.
- public_works_prevailing_wage_bidding: Government bidding with certified payroll, Davis-Bacon/prevailing wage, sealed bids, DBE/MWBE goals, bonding.

Taxonomy Distinction 4 - Operational Intent & Post Purpose:
- software_benchmarking_technical_workflow: Evaluating features, pricing tiers, stability or speed across competing estimating software.
- bid_strategy_scope_gaps_gc_relations: Protecting margins, incomplete drawings, exclusions/clarifications, handling GC bid deadlines and scope gaps.
- career_pathing_compensation_hiring: Estimator pay, bonuses, remote work, workload expectations, hiring and career advancement.
- industry_venting_operational_burnout: Frustration-driven posts about bid-day stress, last-minute addendums, unrealistic GC deadlines, industry friction.

Taxonomy Distinction 5 - Poster Role & Expertise Level:
- senior_b2b_mechanical_estimator_chief_estimator: Written by an experienced professional: deep terminology, calibrated labor multipliers, strategic risk management.
- general_contractor_precon_coordinator: Written from the GC/buyer side: how sub quotes are reviewed, leveled and combined into a prime bid.
- field_tech_residential_installer_apprentice: Entry-level or field-focused: moving into the office, learning blueprints, beginner tools.
- software_vendor_sales_representative: Self-promotional pitches, demo offers, vendor-driven marketing.

Taxonomy Distinction 6 - Unrelated:
- unrelated: Outside construction precon, bidding and estimating software entirely (personal finance, non-estimating code, jobsite safety memes, spam).

Decision rules for the hardest boundaries:
1. general_pdf_cad_digitizers vs specialized_mechanical_estimating_databases: choose specialized_mechanical_estimating_databases ONLY if the post
   describes trade-specific automation that turns measurements into mechanical components (auto fitting/elbow generation, MCAA/PHCC labor units,
   supplier pricing feeds, system-aware assemblies, pressure-class/gauge/joint rules, automatic mechanical BOMs). If the post is only about
   universal measuring, scaling, markup, PDF/CAD navigation or exporting quantities to spreadsheets, choose general_pdf_cad_digitizers EVEN IF
   the user is doing HVAC or piping takeoff (trade context alone does not make a tool specialized).
2. general_construction_non_mechanical vs unrelated: any preconstruction, takeoff, markup or pricing content for non-HVAC trades is
   general_construction_non_mechanical. Use unrelated ONLY when the post has no construction estimating, bidding, takeoff or precon content at all.
"""

LABELING_PROMPT = f"""
You are an expert HVAC estimator for bids and takeoffs and an expert in the MEP (mechanical, electrical, plumbing) construction industry.
You are also an expert NLP data annotator for construction estimating posts on r/estimators, a Reddit community of estimators,
preconstruction managers, trade contractors and software vendors.
Select the single best-fit label for the following Reddit post from this taxonomy of 21 labels:
{json.dumps(TAXONOMY_LABELS, indent=2)}

The labels are organised into 6 taxonomy distinctions that describe DIFFERENT dimensions of a post (trade scope, software, project sector,
post purpose, poster role, unrelated). A post usually touches several. Pick the ONE label whose definition the post's meaning matches most
strongly overall, by comparing the post's semantic meaning against every definition below.
{LABEL_DEFINITIONS}
Score each label's semantic match from 0 to 100 and report the highest-scoring label and the runner-up. The two labels MUST be different.
Provide your output ONLY as a JSON object matching this structure:
{{
  "chosen_label": "<label_name>",
  "highest_score": <integer_0_to_100>,
  "second_label": "<second_best_label_name>",
  "second_score": <integer_0_to_100>,
  "reason": "<one sentence justification comparing top 2 labels>"
}}
"""

# Single sweep r/Estimators subreddit must use exact search " self:true (guide OR megathread OR analysis OR "deep dive") " and have
# native filters set to sort by "Top" and time to "All Time" (prioritizes high-detail quality and recency).
# This filters out the brief, low-quality questions that dominate daily feeds; if you do not use it, your results will be flooded
# with simple, one-sentence posts or unanswered threads instead of the comprehensive, long-form estimation guides and deeply analyzed
# industry discussions you are looking for. Because r/Estimators is a highly specialized, fast-growing professional community, sorting
# by Top (All Time) inside that specific sandbox will naturally front-load the absolute highest quality, most heavily engaged professional
# insights from the last 1 to 3 years anyway, successfully completing your search in a single action.
# Design: this is now a GENERATOR. It yields one post at a time so main() can label and write each row before the next
# post is processed (row-by-row), and it halts itself (with a printed reason) instead of ever returning duplicates.
def fetch_reddit_posts(subreddit="estimators", limit=210):
    """Scrapes public posts from Reddit using JSON endpoints, yielding one cleaned post at a time."""
    headers = {'User-Agent': 'TakeMeter-Dataset-Scraper/1.0'}
    yielded = 0
    after = None
    seen_ids = set()  # Reddit fullnames (e.g. t3_abc123) already yielded; the guard against duplicate rows

    print(f"Fetching posts from r/{subreddit}...")
    while yielded < limit:
        # Fixed URL: needs www + "/r/" before the subreddit. raw_json=1 stops Reddit HTML-escaping (&amp; etc.)
        # so the post text is stored exactly as the author wrote it.
        url = f"https://www.reddit.com/r/{subreddit}/search.json?q=self:true+(guide+OR+megathread+OR+analysis+OR+%22deep+dive%22)&sort=top&t=all&restrict_sr=1&limit=100&raw_json=1"
        if after:
            url += f"&after={after}"

        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f"STOPPED: Reddit returned HTTP {res.status_code}. Posts obtained before this: {yielded}.")
            return

        data = res.json()
        children = data.get('data', {}).get('children', [])
        if not children:
            print(f"STOPPED: Reddit returned an empty page (no more search results). Posts obtained before this: {yielded}.")
            return

        new_on_page = 0
        for child in children:
            pdata = child['data']
            post_id = pdata.get('name')
            if post_id in seen_ids:
                continue  # never emit a repeat; page-level duplicate handling is below
            seen_ids.add(post_id)
            new_on_page += 1

            title = pdata.get('title', '')
            selftext = pdata.get('selftext', '')  # search.json returns the FULL selftext for self posts (no truncation)
            if selftext in ('[removed]', '[deleted]'):
                continue  # body is gone, so there is no whole post to label
            full_post = f"{title}\n\n{selftext}".strip()

            # Clean newlines and quotes for clean CSV handling
            clean_text = full_post.replace('\r\n', ' ').replace('\n', ' ')
            if len(clean_text) > 30: # Filter empty/short posts
                yielded += 1
                yield clean_text
                if yielded >= limit:
                    return

        after = data.get('data', {}).get('after')
        # Pagination wall: Reddit repeating results (nothing new) or giving no next cursor means looping again would
        # only re-fetch page 1 and create duplicate rows, so halt and report instead.
        if new_on_page == 0:
            print(f"STOPPED: Reddit pagination returned only already-seen posts (would create duplicates). Posts obtained before this: {yielded}.")
            return
        if not after:
            print(f"STOPPED: Reddit gave no 'after' cursor, i.e. the end of the search results was reached. Posts obtained before this: {yielded}.")
            return
        time.sleep(1) # Respect rate limits

def label_post_with_gemini(post_text):
    """Calls Gemini API to rank semantic labels. Returns (label, note) or None if every attempt failed."""
    model = genai.GenerativeModel('gemini-2.5-flash')

    # Retry instead of the old silent fallback label: a made-up label would be written as real data and silently
    # pollute the dataset. If all attempts fail, the caller skips the post.
    for attempt in range(1, GEMINI_MAX_ATTEMPTS + 1):
        try:
            response = model.generate_content(
                f"{LABELING_PROMPT}\n\nPost Content:\n\"{post_text}\"",
                generation_config={"response_mime_type": "application/json"}
            )
            result = json.loads(response.text)  # parse Gemini's JSON reply into label/scores/reason

            chosen_label = result.get("chosen_label")
            sec_label = result.get("second_label")
            # Validate against the 21 allowed labels; anything else (typo, invented label) triggers a retry.
            if chosen_label not in TAXONOMY_LABELS or sec_label not in TAXONOMY_LABELS or chosen_label == sec_label:
                raise ValueError(f"Invalid labels returned: {chosen_label!r}, {sec_label!r}")

            h_score = int(result["highest_score"])
            sec_score = int(result["second_score"])
            reason = str(result["reason"]).strip()

            note = f"Highest semantic match of {h_score}% for {chosen_label} (with 2nd highest of {sec_score}% as {sec_label}) due to {reason}"
            return chosen_label, note

        except Exception as e:
            print(f"API Error (attempt {attempt}/{GEMINI_MAX_ATTEMPTS}): {e}")
            time.sleep(10 * attempt)  # linear backoff; also rides out rate-limit (429) errors
    return None

def main():
    print("Starting row-by-row scrape + AI labeling...")

    written = 0
    skipped = 0
    # Header is written once up front, then every row is appended and flushed immediately. Crash-safety design:
    # if the run dies at post 130, rows 1-129 are already saved in labels.csv rather than lost in memory.
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label", "note"])
        f.flush()

        for idx, post in enumerate(fetch_reddit_posts(limit=200)):
            result = label_post_with_gemini(post)
            if result is None:
                skipped += 1
                print(f"Skipped post {idx + 1}: Gemini failed {GEMINI_MAX_ATTEMPTS} times.")
                continue
            label, note_reason = result

            # Mark first 20 as cold per project specs, remaining as pre-labelled
            # (the hard-coded "pre-labelled, checked" text is gone: every row now carries Gemini's own ranked note)
            # "written" (not idx) drives this so skipped posts cannot shift which rows count as the first 20.
            if written < COLD_COUNT:
                note = f"cold | {note_reason}"
            else:
                note = note_reason

            writer.writerow([post, label, note])
            f.flush()
            written += 1

            if written % 25 == 0:
                print(f"Processed {written} posts...")
            time.sleep(GEMINI_DELAY_SECONDS)

    print(f"Done. Wrote {written} rows to {OUTPUT_CSV} ({skipped} skipped after Gemini failures).")

if __name__ == "__main__":
    main()
