import newspaper
import pandas as pd
import json
import os

# --- 1. الإعدادات ---
OUTPUT_FILENAME = "latest_news.json"
SITES = {
    "FXStreet": "https://www.fxstreet.com/news",
    "Kitco": "https://www.kitco.com/news/"
}
MAX_ARTICLES_PER_SITE = 5 # جلب أهم 5 مقالات من كل موقع

all_articles = []

print("--> بدء عملية سحب الأخبار...")

for site_name, url in SITES.items():
    print(f"--- جاري الفحص في موقع: {site_name} ---")
    try:
        paper = newspaper.build(url, memoize_articles=False, fetch_images=False, request_timeout=15)

        count = 0
        for article in paper.articles:
            if count >= MAX_ARTICLES_PER_SITE:
                break
            try:
                article.download()
                article.parse()
                if article.title and len(article.text) > 100: # التأكد من وجود عنوان ونص
                    data = {
                        'site': site_name,
                        'title': article.title,
                        'link': article.url
                    }
                    all_articles.append(data)
                    print(f"  ✅ تم العثور على: {article.title}")
                    count += 1
            except Exception:
                continue # تجاهل المقالات التي تفشل في التحميل
    except Exception as e:
        print(f"!!! فشل في معالجة الموقع {site_name}. الخطأ: {e}")
        continue

# --- 2. حفظ المخرجات ---
if all_articles:
    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)
    print(f"\n✅ تم حفظ {len(all_articles)} مقال جديد بنجاح في ملف {OUTPUT_FILENAME}")
else:
    print("\n!!! لم يتم العثور على أي مقالات جديدة.")
