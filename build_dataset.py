# Run with Bash command "python build_dataset.py"
# Ensure "pip install google-generativeai requests" and "pip install python-dotenv" before use in .env file
import csv
import json
import os
import re
import time
import requests
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from dotenv import load_dotenv  
import google.generativeai as genai

# Load environment variables from the local .env file
load_dotenv(override=True)  # override: a stale GEMINI_API_KEY in the OS environment must not shadow the key in .env  

# 1. Configure Gemini API
# Ensure GEMINI_API_KEY is set in your environment variables
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# MACRO (tune by hand): how many NEW unique posts (not already in labels.csv) each of the 3 Reddit searches must collect.
UNIQUE_POSTS_PER_SEARCH = 100
# Output file: the existing labels.csv the notebook reads (data/labels.csv), not a new file in the cwd.
OUTPUT_CSV = os.path.join("data", "labels.csv")
# The header line. It is written exactly once, as line 1, when labels.csv is created (or when the file is rewritten); the
# Reddit searches never write a header of their own. Kept as "note" to match labels_template.csv and the notebook.
CSV_HEADER = ["text", "label", "note"]
# Models to try, in order; filtered to those the API key can actually see. Lite models first: they accepted requests
# when probed and have the roomiest free-tier daily quota. See ModelPool for how rotation works.
GEMINI_MODEL_PREFERENCE = [
    "gemini-3.1-flash-lite", "gemini-3.5-flash-lite", "gemini-flash-lite-latest",
    "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-flash-latest",
    "gemini-3-flash-preview", "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro",
    "gemini-3.1-pro-preview", "gemini-pro-latest",
]
GEMINI_DELAY_SECONDS = 4# pause between Gemini calls to stay under free-tier requests-per-minute limits
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
# ---------------------------------------------------------------------------------------------------------------------
# HOW THE SCRAPER WORKS (high level)
#   * Reddit blocks anonymous .json requests (HTTP 403 / login redirect) but still serves every search as an Atom feed
#     (search.rss) with no login or key. Each <entry> holds the FULL post body as HTML (tested up to ~12k chars, no
#     truncation), so we parse that.
#   * Three searches run in order (see SEARCHES below). The keyword searches alone only contain ~105 posts in total, so
#     the third, broader "self:true" search (every text post, sorted Top) supplies the rest.
#   * Each search keeps going until it has found UNIQUE_POSTS_PER_SEARCH posts that are NEW, i.e. whose text is not already
#     in column 1 of labels.csv and was not added by an earlier search in this run. Posts that are already there are passed
#     over and do not count towards the quota. If a search runs out of results first, it stops with a printed reason.
#   * Every new post is appended to labels.csv (column 1, empty label/note) the moment it is found, so a crash loses nothing.
#   * Only after ALL scraping is finished does Phase 2 start sending the unlabelled rows to Gemini one by one.
# ---------------------------------------------------------------------------------------------------------------------
RSS_NS = {'a': 'http://www.w3.org/2005/Atom'}
# Only "all" (All Time) is searched: tests showed the narrower windows (year/month/week/day) never returned a post that
# t=all had not, and every extra window costs a rate-limited request. Add "year" etc. back here to widen a search.
RSS_TIME_WINDOWS = ["all"]
RSS_MIN_WAIT_SECONDS = 60  # anonymous RSS allows ~1 request per window (x-ratelimit-remaining was always 0)
RSS_PAGE_SIZE = 100        # `limit=100` in the URL: the most entries Reddit returns per page; a shorter page means "last page"

# (label for the log, search query, sort). The query text is already URL-encoded.
SEARCHES = [
    # How to use "Top" (Most total upvote) Reddit sort: url = f"https://www.reddit.com/r/{subreddit}/search.rss?q=self:true+(guide+OR+megathread+OR+analysis+OR+%22deep+dive%22)&sort=top&t={window}&restrict_sr=1&limit=100"
    ("Top, text posts matching guide/megathread/analysis/deep dive", "self:true+(guide+OR+megathread+OR+analysis+OR+%22deep+dive%22)", "top"),
    # How to use "Hot" (Fastest recent traction) Reddit sort: url = f"https://www.reddit.com/r/{subreddit}/search.rss?q=self:true+(guide+OR+megathread+OR+analysis+OR+%22deep+dive%22)&sort=hot&t={window}&restrict_sr=1&limit=100"
    ("Hot, text posts matching guide/megathread/analysis/deep dive", "self:true+(guide+OR+megathread+OR+analysis+OR+%22deep+dive%22)", "hot"),
    # Third search: every text (self) post in the subreddit, Top sort. This is what supplies enough unique posts.
    # (Reddit's search feed only returns posts: adding type=comment returned the identical post list, so comments are not available.)
    ("Top, all text posts (self:true)", "self:true", "top"),
]

class _TextExtractor(HTMLParser):
    """Turns the feed's HTML post body into plain text (block tags become spaces, entities are decoded)."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)
    def handle_starttag(self, tag, attrs):
        if tag in ('p', 'br', 'li', 'div', 'tr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'pre'):
            self.parts.append(' ')
    def handle_endtag(self, tag):
        if tag in ('p', 'li', 'div', 'tr', 'blockquote', 'pre'):
            self.parts.append(' ')

def _html_to_text(content_html):
    # The post body sits between <!-- SC_OFF --> and <!-- SC_ON -->; everything after SC_ON is Reddit's
    # "submitted by /u/x [link] [comments]" footer, which is not part of the post, so cut it off first.
    body = content_html.split('<!-- SC_ON -->')[0].replace('<!-- SC_OFF -->', '')
    extractor = _TextExtractor()
    extractor.feed(body)
    return ' '.join(''.join(extractor.parts).split())  # collapse all whitespace/newlines to single spaces

_last_request_at = 0.0  # time of the previous Reddit request, used to enforce RSS_MIN_WAIT_SECONDS between requests

def _get_feed_page(url, headers):
    """GET one feed page, honoring Reddit's rate limit. Spaces requests >= RSS_MIN_WAIT_SECONDS apart (so callers never
    need their own sleeps) and retries 429s a few times. Returns the last response."""
    global _last_request_at
    for _ in range(4):
        wait_more = RSS_MIN_WAIT_SECONDS - (time.time() - _last_request_at)
        if wait_more > 0:
            time.sleep(wait_more)
        res = requests.get(url, headers=headers)
        _last_request_at = time.time()
        if res.status_code != 429:
            return res
        # 429 = rate limited; x-ratelimit-reset says how many seconds until the window reopens
        wait = int(float(res.headers.get('x-ratelimit-reset', RSS_MIN_WAIT_SECONDS))) + 2
        print(f"Rate limited by Reddit (HTTP 429); waiting {wait}s...")
        time.sleep(wait)
    return res

def _normalize(text):
    return " ".join(text.split())  # whitespace-insensitive key so "same post, different spacing" still counts as a duplicate

def fetch_reddit_posts(existing_texts, subreddit="estimators"):
    """Runs every search in SEARCHES and yields NEW post texts one at a time (generator), so main() can write each one to
    labels.csv immediately. `existing_texts` = column 1 of the current labels.csv; anything already there is skipped."""
    headers = {'User-Agent': 'TakeMeter-Dataset-Scraper/1.0'}
    seen_texts = {_normalize(t) for t in existing_texts}  # duplicate guard: the file's posts + everything added this run
    seen_ids = set()  # Reddit fullnames (e.g. t3_abc123) already looked at; skips repeats across pages and searches
    total_new = 0

    print(f"Fetching posts from r/{subreddit}: {len(SEARCHES)} searches, up to {UNIQUE_POSTS_PER_SEARCH} NEW unique posts each...")
    for name, query, sort in SEARCHES:
        found = 0           # new unique posts this search has contributed (counts towards UNIQUE_POSTS_PER_SEARCH)
        skipped_dupes = 0   # posts already in labels.csv (or added earlier); passed over, NOT counted
        end_reason = "reached the quota"
        for window in RSS_TIME_WINDOWS:
            after = None  # pagination cursor: the id of the last entry on the previous page
            while found < UNIQUE_POSTS_PER_SEARCH:
                url = f"https://www.reddit.com/r/{subreddit}/search.rss?q={query}&sort={sort}&t={window}&restrict_sr=1&limit={RSS_PAGE_SIZE}"
                if after:
                    url += f"&after={after}"

                res = _get_feed_page(url, headers)
                if res.status_code != 200:
                    print(f"STOPPED: Reddit returned HTTP {res.status_code} during '{name}'. New posts obtained in total: {total_new}.")
                    return

                entries = ET.fromstring(res.content).findall('a:entry', RSS_NS)
                if not entries:
                    end_reason = "Reddit has no more results for it"
                    break  # this window is exhausted

                unseen_on_page = 0
                for entry in entries:
                    post_id = entry.find('a:id', RSS_NS).text  # fullname, e.g. t3_1qdjxpo; also the `after` cursor
                    after = post_id
                    if post_id in seen_ids:
                        continue
                    seen_ids.add(post_id)
                    unseen_on_page += 1

                    title = entry.find('a:title', RSS_NS).text or ''
                    content_el = entry.find('a:content', RSS_NS)
                    selftext = _html_to_text(content_el.text) if content_el is not None and content_el.text else ''
                    if selftext in ('[removed]', '[deleted]'):
                        continue  # body is gone, so there is no whole post to label
                    full_post = f"{title}\n\n{selftext}".strip()

                    # Clean newlines and quotes for clean CSV handling
                    clean_text = full_post.replace('\r\n', ' ').replace('\n', ' ')
                    if len(clean_text) <= 30:  # Filter empty/short posts
                        continue

                    # THE UNIQUENESS CHECK: already in column 1 of labels.csv (or added earlier this run)? Then pass it
                    # and keep looking: it does not count towards this search's quota.
                    key = _normalize(clean_text)
                    if key in seen_texts:
                        skipped_dupes += 1
                        continue
                    seen_texts.add(key)
                    found += 1
                    total_new += 1
                    yield clean_text
                    if found >= UNIQUE_POSTS_PER_SEARCH:
                        break

                print(f"  [{sort}] page done: {found}/{UNIQUE_POSTS_PER_SEARCH} new unique so far, {skipped_dupes} already-present posts passed over.")
                if found >= UNIQUE_POSTS_PER_SEARCH:
                    break
                if unseen_on_page == 0:
                    end_reason = "paging only returned posts it had already seen"
                    break
                if len(entries) < RSS_PAGE_SIZE:
                    end_reason = "Reddit returned its last (short) page"
                    break  # a page shorter than the page size is the end of the results; saves one wasted request
            if found >= UNIQUE_POSTS_PER_SEARCH:
                break
        status = "complete" if found >= UNIQUE_POSTS_PER_SEARCH else f"STOPPED EARLY ({end_reason})"
        print(f"Search '{name}': {found}/{UNIQUE_POSTS_PER_SEARCH} new unique posts, {skipped_dupes} already-present posts passed over -> {status}.")

    print(f"All searches finished. New unique posts obtained in total: {total_new}.")

class AllModelsExhausted(Exception):
    """Raised when every candidate Gemini model has failed in this run (message = full per-model report)."""

class ModelPool:
    """Tracks which Gemini models are still usable. Design: stay on ONE model until it fails for good, then rotate to the
    next, so most rows are labelled by the same model (consistency) while a dead/over-quota model never stops the run."""
    def __init__(self, candidates):
        self.candidates = candidates
        self.dead = {}  # model name -> (error code, reason); filled as models fail
        self.uses = {name: 0 for name in candidates}  # rows labelled per model, printed at the end

    def current(self):
        for name in self.candidates:
            if name not in self.dead:
                return name
        raise AllModelsExhausted(self.report())

    def mark_dead(self, name, code, reason):
        self.dead[name] = (code, reason)
        print(f"MODEL ROTATION: '{name}' unusable (error {code}: {reason}). Remaining: {[m for m in self.candidates if m not in self.dead]}")

    def report(self):
        lines = ["ALL GEMINI MODELS FAILED - no models left to rotate to. Models tried and why each failed:"]
        for name in self.candidates:
            code, reason = self.dead.get(name, ("-", "not tried"))
            lines.append(f"  - {name}: error {code} - {reason}")
        lines.append("No usable model remains (every model available to this API key returned an error). Quotas reset daily; "
                     "add a new key to .env or rerun later - rows already labelled in labels.csv are kept and the run resumes from them.")
        return "\n".join(lines)

def discover_models():
    """Lists models this API key can call, preferred ones first, then any other plain text Gemini flash/pro model."""
    # list_models() reflects the free-tier account's real access, so we never try ids the key cannot see at all.
    available = {m.name.replace("models/", "") for m in genai.list_models() if "generateContent" in m.supported_generation_methods}
    ordered = [m for m in GEMINI_MODEL_PREFERENCE if m in available]
    # Extras: only text flash/pro ids (regex skips tts/image/robotics/computer-use/deep-research variants that cannot do this task)
    pattern = re.compile(r"gemini-[\d.]+-(flash|pro)(-lite)?(-preview)?|gemini-(flash|pro)(-lite)?-latest")
    ordered += sorted(m for m in available if pattern.fullmatch(m) and m not in ordered)
    return ordered

def _error_code(e):
    code = getattr(e, "code", None)  # google.api_core exceptions carry the HTTP status as .code
    try:
        return int(code)
    except (TypeError, ValueError):
        found = re.search(r"\b([45]\d\d)\b", str(e))
        return int(found.group(1)) if found else "unknown"

def _short_reason(e):
    return " ".join(str(e).split())[:220]  # one line, capped, so the terminal log stays readable

def label_post_with_gemini(post_text, pool):
    """Calls Gemini API to rank semantic labels. Returns (label, note, model_name), or None if this post cannot be
    labelled. Raises AllModelsExhausted when no model is left."""
    # Model-choice history: 'gemini-2.5-flash' returns 404 for this key, and 'gemini-3.8-flash' allows only 20 requests/day
    # on the free tier. Hence a rotating pool (see ModelPool) instead of one hard-coded model.
    # Retry instead of the old silent fallback label: a made-up label would be written as real data and silently
    # pollute the dataset. If a post cannot be labelled it stays unlabelled for a later run.
    bad_output_attempts = 0
    transient_attempts = {}  # per-model count of transient failures (rate limit / 5xx) for THIS post
    while True:
        model_name = pool.current()  # raises AllModelsExhausted when every model is dead
        model = genai.GenerativeModel(model_name)
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
            pool.uses[model_name] += 1
            return chosen_label, note, model_name

        except (json.JSONDecodeError, ValueError, KeyError, TypeError, AttributeError) as e:
            # Model answered but with unusable output (bad JSON, invented label, blocked response): a POST problem, not
            # a model problem, so retry the same model and never mark it dead.
            bad_output_attempts += 1
            print(f"Bad output from {model_name} (attempt {bad_output_attempts}/{GEMINI_MAX_ATTEMPTS}): {_short_reason(e)}")
            if bad_output_attempts >= GEMINI_MAX_ATTEMPTS:
                return None
            time.sleep(2)

        except Exception as e:
            code, msg = _error_code(e), str(e)
            # Permanent for this run -> rotate immediately: 404 (model retired / not available to this key), 403/401
            # (no permission or bad key), and any per-DAY quota 429 (reset is hours away, retrying is pointless).
            if "PerDay" in msg or code in (401, 403, 404):
                pool.mark_dead(model_name, code, _short_reason(e))
                continue
            # Transient (per-minute 429, 5xx, network): wait and retry the same model a few times, then rotate.
            transient_attempts[model_name] = transient_attempts.get(model_name, 0) + 1
            if transient_attempts[model_name] >= GEMINI_MAX_ATTEMPTS:
                pool.mark_dead(model_name, code, f"failed {GEMINI_MAX_ATTEMPTS} times in a row: {_short_reason(e)}")
                continue
            hint = re.search(r"retry in ([\d.]+)s|seconds:\s*(\d+)", msg)  # Google states how long to wait on 429s
            wait = min(float(hint.group(1) or hint.group(2)), 65) if hint else 10 * transient_attempts[model_name]
            print(f"Transient error {code} from {model_name} (attempt {transient_attempts[model_name]}/{GEMINI_MAX_ATTEMPTS}); waiting {wait:.0f}s: {_short_reason(e)}")
            time.sleep(wait)

def read_rows():
    """Loads existing labels.csv rows as [text, label, note] lists (empty list if the file is missing/empty)."""
    if not os.path.exists(OUTPUT_CSV):
        return []
    with open(OUTPUT_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    return [(r + ["", "", ""])[:3] for r in rows[1:] if r and r[0].strip()]  # skip header; pad short rows

def write_rows(rows):
    """Rewrites the whole CSV via a temp file + os.replace, so a crash mid-write can never leave a half-written labels.csv."""
    tmp_path = OUTPUT_CSV + ".tmp"
    with open(tmp_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)
        writer.writerows(rows)
    os.replace(tmp_path, OUTPUT_CSV)

def append_rows(new_rows):
    """Adds rows at the END of labels.csv without touching what is already there; creates the file (with header) if it
    does not exist or is empty. This is how a second run extends an existing dataset instead of overwriting it."""
    needs_header = not os.path.exists(OUTPUT_CSV) or os.path.getsize(OUTPUT_CSV) == 0
    if not needs_header:
        with open(OUTPUT_CSV, "rb") as f:  # make sure the last existing line is terminated so our first row starts on its own line
            f.seek(-1, os.SEEK_END)
            last_byte = f.read(1)
        if last_byte not in (b"\n", b"\r"):
            with open(OUTPUT_CSV, "ab") as f:
                f.write(b"\r\n")
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if needs_header:
            writer.writerow(CSV_HEADER)
        writer.writerows(new_rows)

def remove_duplicate_rows(rows):
    """Step between scraping and labelling: if several rows share the same column 1, keep the FIRST one and delete the later
    repeats. Rewrites labels.csv only when something was actually removed. Returns the de-duplicated rows (the header row
    is never part of `rows`, so it is never touched or sent to Gemini)."""
    seen = set()
    kept = []
    for row in rows:
        key = _normalize(row[0])  # same whitespace-insensitive key the scraper uses
        if key in seen:
            continue
        seen.add(key)
        kept.append(row)
    removed = len(rows) - len(kept)
    if removed:
        write_rows(kept)
    print(f"Duplicate check: removed {removed} repeated row(s) (first appearance kept); {len(kept)} unique rows remain.")
    return kept

def main():
    # Two-phase design (replaces the old interleaved fetch+label loop):
    #   Phase 1 - scrape ALL posts first (the slow, rate-limited Reddit part) and save them in column 1 with empty label/note.
    #   Phase 2 - label them one by one, saving the file after every row.
    # Why: Reddit is slow (~60s/request) and Gemini is the flaky part (quotas). Splitting them means a Gemini outage
    # never costs a re-scrape: the posts are already on disk and the next run resumes at the first unlabelled row.
    # Append-only behaviour: an existing labels.csv is never replaced. Its rows stay as they are and newly scraped posts
    # are added after the last one (a missing/empty file is simply created). Duplicates are allowed to enter the file while
    # scraping; they are removed in one pass right after scraping (see remove_duplicate_rows), keeping the first appearance.
    # Only a run that was interrupted mid-labelling (rows still missing a label) resumes instead of scraping again.
    rows = read_rows()
    # "Unlabelled" is judged by column 2 (the label): a row whose label is empty still needs Gemini, a filled one never does.
    if rows and any(not r[1].strip() for r in rows):
        print(f"Resuming: {len(rows)} posts already in {OUTPUT_CSV}, {sum(1 for r in rows if not r[1].strip())} still unlabelled. Skipping Reddit scrape.")
    else:
        print(f"Phase 1: scraping posts from Reddit... ({len(rows)} rows already in {OUTPUT_CSV} will be kept; new rows go after them)")
        # Phase 1 loop: the generator already skips posts found in column 1, and each new post is appended to the file the
        # moment it arrives (crash-safe). `rows` mirrors the file so Phase 2 sees every row.
        added = 0
        for post in fetch_reddit_posts([r[0] for r in rows]):
            new_row = [post, "", ""]
            append_rows([new_row])
            rows.append(new_row)
            added += 1
        print(f"Phase 1 done: appended {added} new unique posts to column 1 of {OUTPUT_CSV} (file now has {len(rows)} rows).")

    # Scraping is finished: make sure every column-1 value in the file is unique BEFORE anything is sent to Gemini.
    if not rows:
        print("labels.csv has no posts, nothing to do.")
        return
    rows = remove_duplicate_rows(rows)

    print("Phase 2: labelling posts with Gemini, one by one...")
    try:
        pool = ModelPool(discover_models())
    except Exception as e:
        print(f"ERROR: could not list Gemini models with this API key ({_error_code(e)}): {_short_reason(e)}")
        return
    print(f"Gemini models to try, in order: {pool.candidates}")

    skipped = 0
    for idx in range(len(rows)):  # index-based on purpose: `rows` is replaced by the on-disk copy after each write
        if idx >= len(rows):
            break  # the file got shorter during the run
        row = rows[idx]
        # CHECK 1 (before sending): only rows whose second column (label) is empty go to Gemini. A filled label means the
        # row was already labelled, so it is skipped (saves quota and never overwrites an existing label/note).
        if row[1].strip():
            continue
        sent_text = row[0]  # exactly what is sent to Gemini; compared against the file again before writing
        try:
            result = label_post_with_gemini(sent_text, pool)
        except AllModelsExhausted as e:
            print(f"\nSTOPPED: {e}\nRows labelled so far: {sum(1 for r in rows if r[1].strip())}/{len(rows)}.")
            return
        if result is None:
            skipped += 1
            print(f"Skipped post {idx + 1}: Gemini returned unusable output {GEMINI_MAX_ATTEMPTS} times (left unlabelled).")
            continue
        label, note, model_name = result  # columns 2 and 3 of this row

        # CHECK 2 (before writing): re-read the file as it is on disk NOW and confirm that row idx still holds the very
        # text we sent to Gemini and still has an empty label. Gemini calls take seconds and the CSV can change meanwhile
        # (rows edited/inserted/removed by hand, another run), so this guarantees the label/note land on the row they belong to.
        # Writing starts from the on-disk rows (not our stale in-memory copy) so any outside edits are preserved.
        disk_rows = read_rows()
        if idx >= len(disk_rows) or disk_rows[idx][0] != sent_text:
            skipped += 1
            print(f"Skipped writing row {idx + 1}: column 1 in {OUTPUT_CSV} no longer matches the post sent to Gemini (file changed during the run). Nothing written.")
            continue
        if disk_rows[idx][1].strip():
            print(f"Skipped writing row {idx + 1}: its label was filled in while Gemini was working. Existing label kept.")
            continue

        disk_rows[idx] = [sent_text, label, note]
        write_rows(disk_rows)  # save after EVERY row (crash safety)
        rows = disk_rows  # keep the in-memory view in sync with the file for the next iterations
        labelled = sum(1 for r in rows if r[1].strip())
        print(f"Labelled {labelled}/{len(rows)} (row {idx + 1}, model {model_name}): {label}")
        time.sleep(GEMINI_DELAY_SECONDS)

    print(f"Done. {sum(1 for r in rows if r[1].strip())}/{len(rows)} rows labelled in {OUTPUT_CSV} ({skipped} skipped). Rows per model: {pool.uses}")

if __name__ == "__main__":
    main()
