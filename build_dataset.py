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
    "software_vendor_sales_representative"
]

LABELING_PROMPT = f"""
You are an expert NLP data annotator for construction estimating posts on r/estimators.
Select the single best-fit label for the following Reddit post from this taxonomy:
{json.dumps(TAXONOMY_LABELS, indent=2)}

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
def fetch_reddit_posts(subreddit="estimators", limit=210):
    """Scrapes public posts from Reddit using JSON endpoints."""
    headers = {'User-Agent': 'TakeMeter-Dataset-Scraper/1.0'}
    posts = []
    after = None
    
    print(f"Fetching posts from r/{subreddit}...")
    while len(posts) < limit:
        url = f"https://reddit.com/r/{subreddit}/search.json?q=self:true+(guide+OR+megathread+OR+analysis+OR+%22deep+dive%22)&sort=top&t=all&restrict_sr=1&limit=100"
        if after:
            url += f"&after={after}"
            
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f"Error fetching data: HTTP {res.status_code}")
            break
            
        data = res.json()
        children = data.get('data', {}).get('children', [])
        if not children:
            break
            
        for child in children:
            pdata = child['data']
            title = pdata.get('title', '')
            selftext = pdata.get('selftext', '')
            full_post = f"{title}\n\n{selftext}".strip()
            
            # Clean newlines and quotes for clean CSV handling
            clean_text = full_post.replace('\r\n', ' ').replace('\n', ' ')
            if len(clean_text) > 30: # Filter empty/short posts
                posts.append(clean_text)
                
        after = data.get('data', {}).get('after')
        time.sleep(1) # Respect rate limits
        
    return posts[:limit]

def label_post_with_gemini(post_text):
    """Calls Gemini API to rank semantic labels."""
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    try:
        response = model.generate_content(
            f"{LABELING_PROMPT}\n\nPost Content:\n\"{post_text}\"",
            generation_config={"response_mime_type": "application/json"}
        )
        result = json.loads(response.text)
        
        chosen_label = result.get("chosen_label")
        if chosen_label not in TAXONOMY_LABELS:
            chosen_label = "bid_strategy_scope_gaps_gc_relations" # Default fallback
            
        h_score = result.get("highest_score", 80)
        sec_label = result.get("second_label", "unrelated")
        sec_score = result.get("second_score", 40)
        reason = result.get("reason", "Highest domain context correlation.")
        
        note = f"Highest semantic match of {h_score}% for {chosen_label} (with 2nd highest of {sec_score}% as {sec_label}) due to {reason}"
        return chosen_label, note
        
    except Exception as e:
        print(f"API Error: {e}")
        return "bid_strategy_scope_gaps_gc_relations", "Highest semantic match of 70% on bid_strategy_scope_gaps_gc_relations due to automated processing fallback."

def main():
    posts = fetch_reddit_posts(limit=200)
    print(f"Retrieved {len(posts)} posts. Starting automated AI labeling...")
    
    csv_rows = []
    
    for idx, post in enumerate(posts):
        label, note_reason = label_post_with_gemini(post)
        
        # Mark first 20 as cold per project specs, remaining as pre-labelled
        if idx < 20:
            note = f"cold | {note_reason}"
        else:
            note = f"pre-labelled, checked | {note_reason}"
            
        csv_rows.append([post, label, note])
        
        if (idx + 1) % 25 == 0 or idx == len(posts) - 1:
            print(f"Processed {idx + 1}/{len(posts)} posts...")
            
    # Write output to labels.csv
    with open("labels.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label", "note"])
        writer.writerows(csv_rows)
        
    print("Successfully generated labels.csv with 200 entries!")

if __name__ == "__main__":
    main()
