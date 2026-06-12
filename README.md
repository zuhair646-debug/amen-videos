# 🤖 آمِن - منصة الفيديوهات العائلية الآمنة

منصة ذكية تجمع فيديوهات آمنة من YouTube تلقائياً، تخزّنها على Cloudflare R2، وتعرضها بتجربة TikTok-style.

---

## ✨ المزايا

### 🎬 **الموقع:**
- ✅ مشغّل TikTok Style (full screen + swipe)
- ✅ 28 فيديو جاهز (20 عادي + 8 shorts)
- ✅ بحث ذكي بالكلمات المفتاحية
- ✅ Keyboard shortcuts (↑ ↓ L ESC)
- ✅ Responsive Design

### 🤖 **الروبوت:**
- ✅ بحث تلقائي في YouTube API
- ✅ تحميل ذكي بـ yt-dlp
- ✅ رفع على Cloudflare R2
- ✅ تحديث تلقائي للموقع
- ✅ فلترة محتوى آمن (SafeSearch strict)

---

## 🚀 التشغيل السريع (خطوات مبسّطة)

### **1️⃣ افتح Railway:**
🔗 https://railway.app

### **2️⃣ أنشئ مشروع جديد:**
- اضغط **"New Project"**
- اختر **"Deploy from GitHub repo"**
- ابحث عن: `zuhair646-debug/amen-videos`
- اضغط **"Deploy Now"**

### **3️⃣ أضف المتغيرات البيئية:**
بعد ما ينشئ المشروع:
- اذهب لـ **Variables**
- اضغط **"RAW Editor"**
- **الصق المتغيرات التالية:**

```env
# 🔑 مفتاح YouTube (المحدّث الجديد)
YOUTUBE_API_KEY=AIzaSyDjjrCWNygC9yoPMBKvmb_g5V24p1K535s

# ☁️ مفاتيح Cloudflare R2 (اتصل بصاحب المشروع للحصول عليها)
R2_ACCESS_KEY=<your_r2_access_key>
R2_SECRET_KEY=<your_r2_secret_key>
R2_ENDPOINT=https://<account_id>.r2.cloudflarestorage.com
R2_BUCKET=amen-videos

# 🐙 مفتاح GitHub (للـ commits التلقائية)
GITHUB_TOKEN=<your_github_pat>
GITHUB_REPO=zuhair646-debug/amen-videos
```

**📝 ملاحظة مهمة:**
- ✅ مفتاح **YOUTUBE_API_KEY** موجود جاهز (محدّث اليوم!)
- ⚠️ باقي المفاتيح (R2 + GitHub) تحتاج تحطها بنفسك عشان الأمان
- 📧 لو تحتاج المفاتيح الكاملة، تواصل مع صاحب المشروع

### **4️⃣ احفظ وشغّل:**
- اضغط **"Update Variables"**
- Railway بيعيد النشر تلقائياً

### **5️⃣ راقب الـ Logs:**
- اذهب لـ **"Deployments"**
- اضغط على آخر Deployment
- اضغط **"View Logs"**

**✅ المفروض تشوف:**
```
✅ جاري البحث عن: قصص الأنبياء للأطفال
✅ وُجد 5 فيديوهات
✅ تم تحميل: قصة نوح عليه السلام
✅ تم الرفع على R2: https://...
✅ تم تحديث الموقع!
✅ GitHub commit: abc1234
```

---

## 🔑 كيف تحصل على المفاتيح؟

### **YouTube Data API v3:**
1. افتح: https://console.cloud.google.com/apis/credentials
2. أنشئ مشروع جديد (New Project)
3. اضغط **"+ CREATE CREDENTIALS"** → **"API Key"**
4. انسخ المفتاح والصقه في `YOUTUBE_API_KEY`

**✅ المفتاح الحالي جاهز ومُختبر!**

### **Cloudflare R2:**
1. افتح: https://dash.cloudflare.com
2. اذهب لـ **R2** → **Manage R2 API Tokens**
3. اضغط **"Create API Token"**
4. اختر **"Edit"** permissions
5. انسخ `Access Key ID` و `Secret Access Key`
6. احصل على `Account ID` من الـ Dashboard
7. كوّن الـ endpoint: `https://<account_id>.r2.cloudflarestorage.com`

### **GitHub Personal Access Token:**
1. افتح: https://github.com/settings/tokens
2. اضغط **"Generate new token (classic)"**
3. اختر scope: **`repo`** (كامل)
4. احفظ المفتاح (يظهر مرة واحدة فقط!)

---

## 📁 بنية المشروع

```
amen-videos/
├── index.html          # الموقع الرئيسي
├── bot.py              # الروبوت الذكي (400 سطر)
├── requirements.txt    # المكتبات (requests, boto3, yt-dlp)
├── Procfile            # إعدادات Railway
├── railway.json        # إعدادات إضافية
├── .env.example        # نموذج للمتغيرات
├── .gitignore          # تجاهل الملفات الحساسة
└── README.md           # هذا الملف
```

---

## 🔧 التخصيص

### **تعديل قوائم البحث:**

في `bot.py` (سطر 30 تقريباً)، عدّل:

```python
SEARCH_QUERIES = [
    ('قصص الأنبياء للأطفال', False),  # False = فيديو عادي
    ('أذكار الصباح للأطفال', True),   # True = Short
    ('تعليم الصلاة للأطفال', False),
    ('أناشيد إسلامية بدون موسيقى', False),
    # ... أضف المزيد
]
```

### **تعديل عدد الفيديوهات لكل قائمة:**

في `bot.py` (السطر الأخير من main):

```python
# غيّر من 2 إلى 5 (أو أي رقم تبيه)
process_videos(query, is_short, max_videos=5)
```

---

## 📊 كيف يشتغل الروبوت؟

```
1️⃣ البحث في YouTube API
   → SafeSearch: strict
   → فلترة: محتوى عائلي فقط
   → نتائج: حسب الكلمات المفتاحية
         ↓
2️⃣ التحميل بـ yt-dlp
   → جودة: 720p (افتراضي، سريع)
   → صيغة: MP4
   → دقة: تلقائية حسب المصدر
         ↓
3️⃣ الرفع على Cloudflare R2
   → تخزين دائم (رخيص جداً)
   → روابط عامة (CDN عالمي)
   → سرعة عالية
         ↓
4️⃣ التحديث التلقائي للموقع
   → يولّد كود HTML للفيديوهات
   → يضيفها لـ index.html
   → يحفظ البيانات الوصفية
         ↓
5️⃣ الـ Commit على GitHub
   → رفع تلقائي
   → الموقع يتحدث فوراً! 🎉
```

---

## 🛠️ الروابط المهمة

- 🌐 **الموقع المباشر:** https://zenrex.ai/s/amen-platform
- 📦 **GitHub Repo:** https://github.com/zuhair646-debug/amen-videos
- 🚂 **Railway:** https://railway.app (بعد النشر)
- ☁️ **Cloudflare R2:** https://dash.cloudflare.com
- 🎥 **YouTube API Console:** https://console.cloud.google.com/apis/credentials

---

## 🆘 استكشاف الأخطاء الشائعة

### ❌ **`yt-dlp: error: You must provide at least one URL`**
**السبب:** مفتاح YouTube API غير صالح أو منتهي.
**الحل:**
```bash
# 1. افتح: https://console.cloud.google.com/apis/credentials
# 2. أنشئ API Key جديد
# 3. حدّث YOUTUBE_API_KEY في Railway Variables
# 4. اضغط Update Variables
```

### ❌ **`boto3.exceptions.NoCredentialsError`**
**السبب:** مفاتيح R2 مفقودة أو خاطئة.
**الحل:**
```bash
# 1. تأكد من نسخ R2_ACCESS_KEY و R2_SECRET_KEY بالضبط
# 2. تأكد من R2_ENDPOINT صحيح (فيه account ID)
# 3. تأكد من R2_BUCKET = "amen-videos" بالضبط
```

### ❌ **`GitHub push failed: 401 Unauthorized`**
**السبب:** GitHub Token منتهي أو ما عنده صلاحيات.
**الحل:**
```bash
# 1. افتح: https://github.com/settings/tokens
# 2. أنشئ Personal Access Token جديد
# 3. اختر scope: repo (كامل)
# 4. حدّث GITHUB_TOKEN في Railway
```

### ❌ **`GitHub push failed: 409 Secret detected`**
**السبب:** GitHub كشف مفتاح API في المحتوى.
**الحل:**
```bash
# ✅ هذا طبيعي! GitHub يحمي مفاتيحك تلقائياً
# ✅ استخدم Railway Variables بدلاً من رفع المفاتيح
# ✅ الروبوت بيقدر يرفع التحديثات بدون مشاكل
```

### ❌ **الروبوت يشتغل بس ما يحمّل شي**
**السبب:** البحث ما رجع نتائج، أو الفيديوهات محمية.
**الحل:**
```bash
# 1. شوف الـ Logs بالتفصيل (Railway → View Logs)
# 2. جرّب كلمات بحث مختلفة في bot.py
# 3. تأكد من SafeSearch مو يحجب كل شي
# 4. جرّب تحمّل فيديو واحد يدوياً كاختبار
```

---

## 🔐 ملاحظات الأمان

**⚠️ مهم جداً:**
- ❌ **لا تشارك** مفاتيح API على GitHub / Slack / Discord
- ✅ استخدم **Railway Variables** فقط (مشفّرة وآمنة)
- ✅ لا ترفع `.env` على GitHub (موجود في `.gitignore`)
- ✅ لو تبي تشارك الكود: استخدم `.env.example` (بدون قيم حقيقية)
- 🔒 GitHub عنده نظام كشف تلقائي للمفاتيح (Secret Scanning)

---

## 📈 خطة التطوير المستقبلية

- [ ] إضافة واجهة Admin لإدارة الفيديوهات
- [ ] نظام تصويت/إعجاب للأطفال (بدون حساب)
- [ ] Playlists ديناميكية حسب العمر
- [ ] دعم لغات إضافية (إنجليزي، فرنسي، أردو...)
- [ ] تطبيق Mobile (Flutter/React Native)
- [ ] إحصائيات مشاهدة (بدون tracking شخصي)
- [ ] وضع Offline (PWA)

---

## 📞 الدعم

لأي سؤال أو مشكلة:
- افتح **Issue** في GitHub: https://github.com/zuhair646-debug/amen-videos/issues
- أو تواصل عبر: zuhair646.debug@gmail.com

---

## 📄 الرخصة

MIT License - استخدمها بحرية! 🚀

---

## 🙏 شكر خاص

- **Zenrex.ai** - منصة البناء والنشر السحرية
- **Railway.app** - استضافة Backend مجانية وسهلة
- **Cloudflare R2** - تخزين فيديوهات قوي ورخيص (أرخص من S3 بـ 10x)
- **yt-dlp** - أقوى أداة تحميل فيديوهات (Open Source)
- **YouTube Data API** - بحث ذكي وآمن

---

**صُنع بـ ❤️ في السعودية** 🇸🇦
