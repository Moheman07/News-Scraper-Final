import scrapy
import newspaper
import pandas as pd
import nltk
from datetime import datetime

class NewspaperSpider(scrapy.Spider):
    # اسم العنكبوت الذي سنستخدمه لتشغيله
    name = 'news_aggregator'

    # ------------------ الإعدادات ------------------
    # قائمة المواقع النهائية التي سنقوم باستخراج الأخبار منها
    sites = {
        "FXStreet": "https://www.fxstreet.com/news",
        "IG_News": "https://www.ig.com/uk/news-and-trade-ideas",
        "Kitco": "https://www.kitco.com/news/"
    }

    # هذه الدالة هي نقطة البداية للعنكبوت
    def start_requests(self):
        # تنزيل حزمة "punkt" الضرورية
        nltk.download('punkt', quiet=True)
        
        # لا نحتاج لإرسال طلبات Scrapy، سنقوم بكل العمل هنا
        # المرور على كل موقع في القائمة
        for site_name, url in self.sites.items():
            self.logger.info(f"--- بدء عملية الاستخراج من موقع: {site_name} ---")
            
            try:
                # بناء كائن "جريدة" من الرابط
                paper = newspaper.build(url, memoize_articles=False, fetch_images=False)
            except Exception as e:
                self.logger.error(f"فشل بناء الجريدة للموقع {site_name}. الخطأ: {e}")
                continue

            # قائمة ومُعدِّد لتخزين المقالات
            all_articles = []
            articles_found_count = 0 
            self.logger.info(f"تم العثور على {len(paper.articles)} رابط محتمل. جارٍ التحليل...")

            # المرور على كل مقال تم العثور عليه
            for article in paper.articles:
                # التوقف إذا وصلنا إلى 10 مقالات
                if articles_found_count >= 5:
                    self.logger.info("تم العثور على 5 مقالات، سيتم الانتقال إلى الموقع التالي.")
                    break

                try:
                    article.download()
                    article.parse()
                    
                    # التأكد من وجود عنوان للمقال قبل إضافته
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
                    # نتجاهل المقالات التي تفشل في التحميل أو التحليل بهدوء
                    pass

            # التأكد من وجود مقالات قبل محاولة الحفظ
            if not all_articles:
                self.logger.warning(f"لم يتم العثور على أي مقالات قابلة للتحليل في {site_name}.")
                continue

            # تحويل القائمة إلى إطار بيانات باستخدام Pandas
            df = pd.DataFrame(all_articles)
            
            # إنشاء اسم ملف ديناميكي
            today_date = datetime.now().strftime("%Y-%m-%d")
            file_name = f"{site_name}_articles_{today_date}.json"
            
            # حفظ النتائج في ملف JSON خاص بهذا الموقع
            df.to_json(file_name, orient='records', indent=4, force_ascii=False)
            self.logger.info(f"✅ تم الانتهاء! تم حفظ بيانات {site_name} في ملف {file_name}\n")

        self.logger.info("--- انتهت جميع العمليات ---")
        # بما أن Scrapy يتوقع yield لشيء ما، يمكننا عدم إرجاع أي شيء
        # أو إرجاع طلب فارغ للإشارة إلى الانتهاء
        return []

    def parse(self, response):
        # هذه الدالة لن يتم استخدامها لأن كل العمل يحدث في start_requests
        pass
