import newspaper
import json

# --- 1. Settings ---
OUTPUT_FILENAME = "latest_news.json"
SITES = {
    "FXStreet": "https://www.fxstreet.com/news",
    "Kitco": "https://www.kitco.com/news/"
}
MAX_ARTICLES_PER_SITE = 5

all_articles = []
print("--> Starting news scraping process...")

for site_name, url in SITES.items():
    print(f"--- Scanning site: {site_name} ---")
    try:
        paper = newspaper.build(url, memoize_articles=False, fetch_images=False, request_timeout=15)
        count = 0
        for article in paper.articles:
            if count >= MAX_ARTICLES_PER_SITE:
                break
            try:
                article.download()
                article.parse()
                if article.title and len(article.text) > 100:
                    data = {'site': site_name, 'title': article.title, 'link': article.url}
                    all_articles.append(data)
                    print(f"  ✅ Found: {article.title}")
                    count += 1
            except Exception:
                continue
    except Exception as e:
        print(f"!!! Failed to process site {site_name}. Error: {e}")
        continue

# --- 2. Save Output ---
if all_articles:
    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)
    print(f"\n✅ Successfully saved {len(all_articles)} new articles to {OUTPUT_FILENAME}")
else:
    print("\n!!! No new articles were found.")
