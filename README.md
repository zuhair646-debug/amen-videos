# 🛡️ آمِن - منصة الفيديوهات العائلية الآمنة

## 🎯 **الفكرة الرئيسية**

**منصة فيديوهات بدون أي اتصال خارجي**. كل فيديو **محمّل مباشرة** على خوادمنا ويُعرض بـ `<video>` tags نظيفة.

---

## ❌ ما لا نفعله:

- ❌ روابط يوتيوب embedded (`<iframe>`)
- ❌ اقتراحات مزعجة
- ❌ إعلانات أو تتبع
- ❌ أي زر يأخذ الطفل لمنصة خارجية
- ❌ جمع بيانات أو cookies

---

## ✅ ما نفعله:

```
1️⃣ الروبوت يبحث في YouTube (API فقط للبحث)
         ↓
2️⃣ يحمّل الفيديو بصيغة MP4 كاملة (yt-dlp)
         ↓
3️⃣ يرفعه على Cloudflare R2 (تخزين سحابي خاص)
         ↓
4️⃣ يضيفه للموقع: <video src="https://r2.dev/xxx.mp4">
         ↓
5️⃣ الطفل يشاهد داخل الموقع (بدون أي رابط خارجي!)
```

---

## 🏗️ البنية التقنية

| المرحلة | الأداة | الهدف |
|---------|--------|-------|
| **البحث** | YouTube Data API v3 | البحث عن محتوى آمن فقط |
| **التحميل** | yt-dlp | تحميل MP4 كامل (720p/1080p) |
| **التخزين** | Cloudflare R2 | رفع دائم + CDN عالمي |
| **العرض** | `<video>` HTML5 | تشغيل داخل الموقع بدون iframe |
| **التحديث** | GitHub API | رفع تلقائي للموقع |

---

## 🤖 الروبوت الذكي (`bot.py`)

### 📚 **القوائم الآمنة:**

```python
SEARCH_QUERIES = {
    'quran': [
        'تلاوة قرآن كريم للأطفال',
        'سورة يوسف كاملة للأطفال'
    ],
    'prophets': [
        'قصة نوح للأطفال بدون موسيقى',
        'قصة إبراهيم للأطفال'
    ],
    'seerah': [
        'السيرة النبوية للأطفال',
        'قصة مولد الرسول'
    ],
    'science': [
        'تجارب علمية للأطفال',
        'علوم الفضاء بالعربي'
    ],
    'adab': [
        'آداب إسلامية للأطفال',
        'بر الوالدين'
    ],
    'history': [
        'تاريخ إسلامي للأطفال',
        'فتح مكة للأطفال'
    ]
}
```

### 🚫 **فلترة صارمة:**

```python
banned_keywords = ['أغنية', 'موسيقى', 'music', 'dance', 'رقص']

# كل عنوان فيديو يُفحص:
if any(keyword in title.lower() for keyword in banned_keywords):
    print("⚠️ تم تخطي (يحتوي كلمة محظورة)")
    continue  # لا يُحمّل أبداً
```

---

## 🚀 النشر على Railway

### **1️⃣ أنشئ مشروع:**
🔗 https://railway.app  
→ **New Project**  
→ **Deploy from GitHub**  
→ `zuhair646-debug/amen-videos`

### **2️⃣ أضف المتغيرات البيئية:**

اذهب لـ **Variables** → **RAW Editor** → الصق:

```env
YOUTUBE_API_KEY=<مفتاحك_من_Google_Console>
R2_ACCESS_KEY=<مفتاحك_من_Cloudflare>
R2_SECRET_KEY=<المفتاح_السري>
R2_ENDPOINT=https://<account_id>.r2.cloudflarestorage.com
R2_BUCKET=amen-videos
R2_PUBLIC_URL=https://pub-<account_id>.r2.dev
GITHUB_TOKEN=<مفتاحك_الشخصي>
GITHUB_REPO=<username>/<repo>
```

> **💡 كيف تحصل على المفاتيح؟**
> - **YouTube API**: https://console.cloud.google.com/apis/credentials
> - **Cloudflare R2**: https://dash.cloudflare.com → R2 → API Tokens
> - **GitHub Token**: https://github.com/settings/tokens

### **3️⃣ راقب التشغيل:**

**Deployments** → **View Logs**

```
[INFO] 🚀 بدء البرنامج...
[INFO] 🔍 يبحث عن: تلاوة قرآن للأطفال
[INFO] ✅ وُجد 3 فيديوهات
[INFO] ⬇️ يحمّل xyz123.mp4...
[INFO] ✅ تم التحميل (42 MB)
[INFO] ☁️ يرفع على R2...
[INFO] ✅ رابط عام: https://pub-xxx.r2.dev/videos/quran/xyz123.mp4
[INFO] 📝 يحدّث index.html...
[INFO] ✅ Commit: 94e7bbb
[INFO] 🎉 اكتمل! 12 فيديو + 3 شورتس
```

**المدة:** 10-15 دقيقة.

---

## 🔒 الأمان والخصوصية

### كيف نحمي الطفل؟

| الميزة | الشرح |
|--------|-------|
| ✅ **لا روابط خارجية** | الفيديو محمّل بالكامل، ليس embed |
| ✅ **لا iframe** | `<video>` HTML5 نظيفة |
| ✅ **لا اقتراحات يوتيوب** | المنصة لا تعرف أن الطفل يشاهد |
| ✅ **لا تتبع** | R2 لا يجمع cookies |
| ✅ **controlsList** | منع التحميل من المتصفح |
| ✅ **فلترة محتوى** | كلمات محظورة + SafeSearch |

### كود الحماية:

```html
<!-- فيديو آمن 100% -->
<video controls controlsList="nodownload">
    <source src="https://pub-xxx.r2.dev/videos/quran/abc.mp4" type="video/mp4">
</video>

<!-- ❌ ما فيه iframe يوتيوب: -->
<!-- <iframe src="youtube.com/embed/..."></iframe> -->
```

---

## 🌐 الموقع المباشر

🔗 **https://zenrex.ai/s/amen-platform**

### المزايا:
- ✅ 100% بدون روابط يوتيوب
- ✅ فيديوهات محمّلة من R2 مباشرة
- ✅ مشغّل TikTok Style للشورتس
- ✅ بحث + فلترة بالفئات
- ✅ Responsive + Keyboard shortcuts

---

## 📁 ملفات المشروع

```
amen-videos/
├── index.html       ✅ الموقع (<video> tags نظيفة)
├── bot.py           🤖 روبوت التحديث (600 سطر)
├── requirements.txt 📦 المكتبات
├── Procfile         🚂 إعدادات Railway
├── railway.json     ⚙️  إعدادات
└── README.md        📝 هذا الملف
```

---

## 🛠️ التخصيص

### أضف فئة جديدة:

في `bot.py` → `SEARCH_QUERIES`:

```python
SEARCH_QUERIES['dua'] = [
    'أدعية للأطفال',
    'دعاء النوم للأطفال'
]
```

### غيّر عدد الفيديوهات:

```python
# في main() → سطر ~450
for query in queries[:2]:  # غيّر إلى [:5] مثلاً
```

---

## 📞 الدعم

- 📧 افتح Issue على GitHub
- 🔗 الموقع: https://zenrex.ai/s/amen-platform
- 📦 الكود: https://github.com/zuhair646-debug/amen-videos

---

## 📜 الترخيص

**MIT License** — استخدمه بحرية للخير ❤️

---

## 🙏 شكر خاص

- **Cloudflare R2** للتخزين
- **yt-dlp** للتحميل
- **Railway** للنشر
- **Zenrex** للاستضافة

---

**بُني بـ ❤️ للعائلات العربية.**

🛡️ **آمِن** - محتوى نظيف، قلوب مطمئنة.
