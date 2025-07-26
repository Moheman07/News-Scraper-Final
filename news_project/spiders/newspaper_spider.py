import scrapy
import newspaper
import pandas as pd
import nltk
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
            
            try:
                paper = newspaper.build(url, memoize_articles=False, fetch_images=False)
            except Exception as e:
                self.logger.error(f"فشل بناء الجريدة للموقع {site_name}. الخطأ: {e}")
                continue

            all_articles = []
            articles_found_count = 0 
            self.logger.info(f"تم العثور على {len(paper.articles)} رابط محتمل. جارٍ التحليل...")

            for article in paper.articles:
                if articles_found_count >= 10:
                    self.logger.info("تم العثور على 10 مقالات، سيتم الانتقال إلى الموقع التالي.")
                    break

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
                        all_articles.append(data)
                        articles_found_count += 1 
                        self.logger.info(f"  ({articles_found_count}/10) ADDED: {article.title}")

                except Exception as e:
                    pass

            if not all_articles:
                self.logger.warning(f"لم يتم العثور على أي مقالات قابلة للتحليل في {site_name}.")
                continue

            df = pd.DataFrame(all_articles)
            
            # ✅ التعديل هنا: اسم ملف ثابت لكل موقع
            file_name = f"{site_name}_articles.json"
            
            df.to_json(file_name, orient='records', indent=4, force_ascii=False)
            self.logger.info(f"✅ تم الانتهاء! تم حفظ بيانات {site_name} في ملف {file_name}\n")

        return []

    def parse(self, response):
        pass