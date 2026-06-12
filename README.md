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

## 🚀 التشغيل

### **1️⃣ النشر على Railway:**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/zuhair646-debug/amen-videos)

أو يدوياً:
```bash
# 1. افتح Railway: https://railway.app
# 2. New Project → Deploy from GitHub repo
# 3. اختر: zuhair646-debug/amen-videos
# 4. Railway بيكتشف Procfile تلقائياً
```

---

### **2️⃣ إضافة المتغيرات البيئية:**

في Railway، اذهب لـ **Variables** → **RAW Editor** والصق:

```env
YOUTUBE_API_KEY=your_youtube_api_key_here
R2_ACCESS_KEY=your_r2_access_key_here
R2_SECRET_KEY=your_r2_secret_key_here
R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
R2_BUCKET=amen-videos
GITHUB_TOKEN=your_github_pat_here
GITHUB_REPO=your-username/amen-videos
```

**📝 ملاحظة:** استبدل القيم بمفاتيحك الخاصة من:
- **YouTube API:** https://console.cloud.google.com/apis/credentials
- **Cloudflare R2:** https://dash.cloudflare.com (R2 → Manage R2 API Tokens)
- **GitHub PAT:** https://github.com/settings/tokens

---

### **3️⃣ التشغيل:**

Railway بيبدأ التشغيل تلقائياً بعد ما تضيف المتغيرات!

شوف الـ Logs:
```
Railway Dashboard → Deployments → Latest → View Logs
```

---

## 📁 بنية المشروع

```
amen-videos/
├── index.html          # الموقع الرئيسي
├── bot.py              # الروبوت الذكي
├── requirements.txt    # المكتبات
├── Procfile            # إعدادات Railway
├── railway.json        # إعدادات إضافية
└── README.md           # هذا الملف
```

---

## 🔧 التخصيص

### **تعديل قوائم البحث:**

في `bot.py`، عدّل:

```python
SEARCH_QUERIES = [
    ('قصص الأنبياء للأطفال', False),  # False = فيديو عادي
    ('أذكار الصباح', True),           # True = Short
    # ... أضف المزيد
]
```

### **تعديل عدد الفيديوهات:**

```python
process_videos(query, is_short, max_videos=5)  # غيّر من 2 إلى 5
```

---

## 🛠️ الروابط المهمة

- 🌐 **الموقع:** https://zenrex.ai/s/amen-platform
- 📦 **GitHub:** https://github.com/zuhair646-debug/amen-videos
- 🚂 **Railway:** https://railway.app (بعد النشر)
- ☁️ **R2 Dashboard:** https://dash.cloudflare.com

---

## 📊 كيف يشتغل؟

```
1. الروبوت يبحث في YouTube API (SafeSearch strict)
         ↓
2. يحمّل الفيديوهات بـ yt-dlp (720p أو 1080p)
         ↓
3. يرفعها على Cloudflare R2 (تخزين دائم)
         ↓
4. يضيفها لـ index.html تلقائياً
         ↓
5. يرفع التحديث على GitHub
         ↓
6. الموقع يتحدث تلقائياً! 🎉
```

---

## 🆘 استكشاف الأخطاء

### **الروبوت ما يشتغل:**
- ✅ تأكد من إضافة **كل المتغيرات البيئية**
- ✅ شوف الـ Logs في Railway
- ✅ تأكد إن مفتاح YouTube صالح

### **الفيديوهات ما تتحمّل:**
- ✅ تأكد إن `yt-dlp` مثبّت (موجود في requirements.txt)
- ✅ جرّب تحمّل فيديو واحد أولاً

### **الرفع على R2 فاشل:**
- ✅ تأكد من مفاتيح R2
- ✅ تأكد إن الـ Bucket موجود

---

## 🔐 الأمان

**⚠️ مهم جداً:**
- ❌ **لا تشارك** مفاتيح API في الكود
- ✅ استخدم **المتغيرات البيئية** فقط (Railway Variables)
- ✅ لا ترفع `.env` على GitHub (موجود في `.gitignore`)

---

## 📞 الدعم

لأي سؤال أو مشكلة، افتح **Issue** في GitHub!

---

## 📄 الرخصة

MIT License - استخدمها بحرية! 🚀

---

**صُنع بـ ❤️ في السعودية** 🇸🇦
