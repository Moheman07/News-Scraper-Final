import scrapy
import newspaper
import pandas as pd
import nltk
import os
from datetime import datetime

class NewspaperSpider(scrapy.Spider):
    name = 'news_aggregator'

    sites = {
        "FXStreet": "https://www.fxstreet.com/news",
        "IG_News": "https://www.ig.com/uk/news-and-trade-ideas",
        "Kitco": "https://www.kitco.com/news/"
    }

    def start_requests(self):
        nltk.download('punkt', quiet=True)
        
        for site_name, url in self.sites.items():
            self.logger.info(f"--- بدء عملية الاستخراج من موقع: {site_name} ---")
            
            file_name = f"{site_name}_articles.json"
            seen_links = set()

            # الخطوة 1: قراءة الملف القديم (إذا كان موجودًا)
            if os.path.exists(file_name):
                try:
                    old_df = pd.read_json(file_name)
                    seen_links.update(old_df['link'].tolist())
                    self.logger.info(f"تم العثور على {len(seen_links)} رابط محفوظ سابقًا لـ {site_name}.")
                except Exception as e:
                    self.logger.error(f"فشل في قراءة الملف القديم {file_name}. الخطأ: {e}")
                    old_df = pd.DataFrame()
            else:
                old_df = pd.DataFrame()

            # الخطوة 2: جلب الروابط الحالية من الموقع
            try:
                paper = newspaper.build(url, memoize_articles=False, fetch_images=False)
            except Exception as e:
                self.logger.error(f"فشل بناء الجريدة للموقع {site_name}. الخطأ: {e}")
                continue

            new_articles = []
            
            # الخطوة 3 و 4: معالجة المقالات الجديدة فقط
            for article in paper.articles:
                if article.url not in seen_links:
                    try:
                        article.download()
                        article.parse()
                        
                        if article.title:
                            data = {
                                'site': site_name,
                                'title': article.title,
                                'authors': ', '.join(article.authors),
                                'publish_date': str(article.publish_date) if article.publish_date else "N/A",
                                'text': article.text,
                                'link': article.url
                            }
                            new_articles.append(data)
                            self.logger.info(f"  ✅ FOUND NEW: {article.title}")
                    except Exception:
                        pass
            
            # الخطوة 5: تحديث الملف إذا تم العثور على مقالات جديدة
            if not new_articles:
                self.logger.info(f"لا توجد مقالات جديدة في {site_name}.")
                continue

            new_df = pd.DataFrame(new_articles)
            
            # دمج الجديد مع القديم، وإزالة التكرار، والإبقاء على أحدث 10
            combined_df = pd.concat([new_df, old_df], ignore_index=True)
            combined_df.drop_duplicates(subset=['link'], keep='first', inplace=True)
            final_df = combined_df.head(10)

            final_df.to_json(file_name, orient='records', indent=4, force_ascii=False)
            self.logger.info(f"✅ تم تحديث الملف! تم حفظ {len(new_articles)} مقال جديد في {file_name}\n")

        return []

    def parse(self, response):
        pass
