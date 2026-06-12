#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 آمِن - روبوت التحديث التلقائي
يبحث في YouTube، يحمّل فيديوهات آمنة، يرفعها على R2، ويحدّث الموقع
"""

import os
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path
import boto3
from botocore.client import Config
import re
import base64

# ═══════════════════════════════════════════════════════════
# ⚙️ الإعدادات (من المتغيرات البيئية)
# ═══════════════════════════════════════════════════════════

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
R2_ACCESS_KEY = os.getenv('R2_ACCESS_KEY')
R2_SECRET_KEY = os.getenv('R2_SECRET_KEY')
R2_ENDPOINT = os.getenv('R2_ENDPOINT', 'https://4b90df683b9a565b655148c1d090ddb1.r2.cloudflarestorage.com')
R2_BUCKET = os.getenv('R2_BUCKET', 'amen-videos')
R2_PUBLIC_URL = os.getenv('R2_PUBLIC_URL', 'https://pub-4b90df683b9a565b655148c1d090ddb1.r2.dev')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'zuhair646-debug/amen-videos')

# ═══════════════════════════════════════════════════════════
# 📚 قوائم البحث الآمنة (محتوى نظيف 100%)
# ═══════════════════════════════════════════════════════════

SEARCH_QUERIES = {
    'quran': [
        'تلاوة قرآن كريم للأطفال',
        'سورة البقرة بصوت جميل',
        'سورة يوسف كاملة للأطفال',
        'تعليم القرآن للصغار'
    ],
    'prophets': [
        'قصة نوح عليه السلام للأطفال',
        'قصة إبراهيم عليه السلام بدون موسيقى',
        'قصة موسى عليه السلام للأطفال',
        'قصة يوسف عليه السلام كرتون إسلامي'
    ],
    'seerah': [
        'السيرة النبوية للأطفال',
        'قصة مولد الرسول للأطفال',
        'غزوات الرسول للأطفال بدون موسيقى',
        'صفات النبي محمد للأطفال'
    ],
    'science': [
        'تجارب علمية للأطفال',
        'كيف تعمل الأشياء للأطفال',
        'علوم الفضاء للأطفال بالعربي',
        'حيوانات وطيور تعليمية للأطفال'
    ],
    'adab': [
        'آداب إسلامية للأطفال',
        'آداب الطعام للأطفال بدون موسيقى',
        'بر الوالدين للأطفال',
        'الصدق والأمانة للأطفال'
    ],
    'history': [
        'تاريخ إسلامي للأطفال',
        'قصة فتح مكة للأطفال',
        'الخلفاء الراشدون للأطفال',
        'صلاح الدين الأيوبي للأطفال'
    ]
}

# قوائم البحث للشورتس (فيديوهات قصيرة < 4 دقائق)
SHORTS_QUERIES = [
    'دعاء قصير للأطفال',
    'ذكر يومي للأطفال',
    'آية قرآنية مع التفسير',
    'حديث نبوي شريف للأطفال',
    'معلومة إسلامية سريعة للأطفال'
]

# ═══════════════════════════════════════════════════════════
# 🔍 البحث في YouTube
# ═══════════════════════════════════════════════════════════

def search_youtube(query, max_results=3, duration='medium'):
    """
    يبحث عن فيديوهات آمنة في YouTube
    duration: 'short' (< 4 دقائق)، 'medium' (4-20 دقيقة)، 'long' (> 20 دقيقة)
    """
    url = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'videoEmbeddable': 'true',
        'videoSyndicated': 'true',
        'safeSearch': 'strict',
        'maxResults': max_results,
        'videoDuration': duration,
        'key': YOUTUBE_API_KEY,
        'relevanceLanguage': 'ar',
        'order': 'relevance',
        'regionCode': 'SA'
    }
    
    try:
        print(f"🔍 يبحث عن: {query}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        videos = []
        for item in data.get('items', []):
            video_id = item['id']['videoId']
            snippet = item['snippet']
            
            # تصفية عناوين غير مرغوبة
            title_lower = snippet['title'].lower()
            banned_keywords = ['أغنية', 'أغاني', 'موسيقى', 'music', 'song', 'dance', 'رقص']
            if any(keyword in title_lower for keyword in banned_keywords):
                print(f"⚠️ تم تخطي: {snippet['title']} (يحتوي كلمة محظورة)")
                continue
            
            videos.append({
                'id': video_id,
                'title': snippet['title'],
                'description': snippet['description'][:150],
                'thumbnail': snippet['thumbnails']['high']['url'],
                'channel': snippet['channelTitle'],
                'published': snippet['publishedAt']
            })
        
        print(f"✅ وُجد {len(videos)} فيديو مناسب لـ '{query}'")
        return videos
        
    except Exception as e:
        print(f"❌ خطأ في البحث '{query}': {e}")
        return []

# ═══════════════════════════════════════════════════════════
# ⬇️ تحميل الفيديو بـ yt-dlp
# ═══════════════════════════════════════════════════════════

def download_video(video_id, is_short=False):
    """
    يحمّل فيديو من YouTube بصيغة MP4
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_dir = Path("downloads")
    output_dir.mkdir(exist_ok=True)
    
    # جودة مناسبة: 720p للفيديوهات العادية، 1080p للشورتس
    format_option = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]' if is_short else 'bestvideo[height<=720]+bestaudio/best[height<=720]'
    output_template = str(output_dir / f"{video_id}.%(ext)s")
    
    cmd = [
        'yt-dlp',
        '--format', format_option,
        '--merge-output-format', 'mp4',
        '--output', output_template,
        '--no-playlist',
        '--quiet',
        '--no-warnings',
        '--no-check-certificate',
        url
    ]
    
    try:
        print(f"⬇️ يحمّل الفيديو: {video_id}...")
        result = subprocess.run(cmd, check=True, timeout=300, capture_output=True, text=True)
        
        # ابحث عن الملف المحمّل
        video_file = output_dir / f"{video_id}.mp4"
        if video_file.exists():
            size_mb = video_file.stat().st_size / (1024 * 1024)
            print(f"✅ تم التحميل: {video_file.name} ({size_mb:.1f} MB)")
            return str(video_file)
        else:
            print(f"❌ الملف غير موجود بعد التحميل: {video_file}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"⏱️ انتهى وقت التحميل (5 دقائق) لـ {video_id}")
        return None
    except subprocess.CalledProcessError as e:
        print(f"❌ خطأ في yt-dlp: {e.stderr}")
        return None
    except Exception as e:
        print(f"❌ خطأ غير متوقع في التحميل: {e}")
        return None

# ═══════════════════════════════════════════════════════════
# ☁️ رفع على Cloudflare R2
# ═══════════════════════════════════════════════════════════

def upload_to_r2(file_path, video_id, category='general'):
    """
    يرفع ملف MP4 على Cloudflare R2 ويرجع الرابط العام
    """
    try:
        # إنشاء S3 client لـ Cloudflare R2
        s3 = boto3.client(
            's3',
            endpoint_url=R2_ENDPOINT,
            aws_access_key_id=R2_ACCESS_KEY,
            aws_secret_access_key=R2_SECRET_KEY,
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )
        
        # اسم الملف في R2: videos/category/video_id.mp4
        object_name = f"videos/{category}/{video_id}.mp4"
        
        print(f"☁️ يرفع على R2: {object_name}...")
        
        # رفع الملف
        with open(file_path, 'rb') as f:
            s3.upload_fileobj(
                f,
                R2_BUCKET,
                object_name,
                ExtraArgs={
                    'ContentType': 'video/mp4',
                    'CacheControl': 'public, max-age=31536000'
                }
            )
        
        # بناء الـ URL العام
        public_url = f"{R2_PUBLIC_URL}/{object_name}"
        
        print(f"✅ تم الرفع: {public_url}")
        return public_url
        
    except Exception as e:
        print(f"❌ خطأ في الرفع على R2: {e}")
        return None

# ═══════════════════════════════════════════════════════════
# 📝 تحديث الموقع (index.html)
# ═══════════════════════════════════════════════════════════

def get_github_file(path='index.html'):
    """يحمّل ملف من GitHub"""
    try:
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        content = base64.b64decode(data['content']).decode('utf-8')
        
        return content, data['sha']
        
    except Exception as e:
        print(f"❌ خطأ في تحميل {path} من GitHub: {e}")
        return None, None

def update_github_file(path, content, message, sha):
    """يحدّث ملف على GitHub"""
    try:
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
        
        payload = {
            'message': message,
            'content': base64.b64encode(content.encode('utf-8')).decode('utf-8'),
            'sha': sha
        }
        
        response = requests.put(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        
        print(f"✅ تم تحديث {path} على GitHub")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تحديث {path}: {e}")
        return False

def inject_videos_into_html(html_content, videos_data, shorts_data):
    """
    يضيف الفيديوهات والشورتس للموقع
    """
    # بناء HTML للفيديوهات (حسب الفئات)
    videos_by_category = {}
    for v in videos_data:
        cat = v.get('category', 'general')
        if cat not in videos_by_category:
            videos_by_category[cat] = []
        videos_by_category[cat].append(v)
    
    # إنشاء كروت الفيديوهات
    videos_html = ""
    category_names = {
        'quran': '📖 القرآن الكريم',
        'prophets': '🕌 قصص الأنبياء',
        'seerah': '☪️ السيرة النبوية',
        'science': '🔬 علوم وتجارب',
        'adab': '🤲 آداب إسلامية',
        'history': '📜 تاريخ إسلامي'
    }
    
    for cat, vids in videos_by_category.items():
        cat_name = category_names.get(cat, cat)
        for v in vids:
            videos_html += f'''
                <div class="video-card" data-category="{cat}">
                    <div class="relative rounded-xl overflow-hidden shadow-lg group">
                        <video 
                            class="w-full h-48 object-cover cursor-pointer"
                            poster="{v.get('thumbnail', '')}"
                            onclick="playVideoInModal('{v['url']}')"
                            preload="metadata"
                        >
                            <source src="{v['url']}" type="video/mp4">
                        </video>
                        <div class="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                            <button onclick="playVideoInModal('{v['url']}')" class="bg-white/90 text-purple-600 rounded-full p-4 transform scale-0 group-hover:scale-100 transition-transform">
                                ▶️
                            </button>
                        </div>
                    </div>
                    <div class="p-4">
                        <span class="inline-block px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-bold mb-2">{cat_name}</span>
                        <h3 class="font-bold text-gray-800 mb-2 line-clamp-2">{v['title']}</h3>
                        <button onclick="playVideoInModal('{v['url']}')" class="w-full bg-purple-500 hover:bg-purple-600 text-white font-bold py-2 px-4 rounded-lg transition-colors">
                            ▶️ شاهد الآن
                        </button>
                    </div>
                </div>
            '''
    
    # إنشاء قائمة الشورتس
    shorts_array = ', '.join([f"'{s['url']}'" for s in shorts_data])
    
    # حقن الفيديوهات في HTML
    # استبدال قسم الفيديوهات
    pattern_videos = r'(<div class="grid[^>]*grid-cols[^>]*>)(.*?)(</div>\s*</section>)'
    html_content = re.sub(
        pattern_videos,
        f'\\1\n{videos_html}\n\\3',
        html_content,
        flags=re.DOTALL
    )
    
    # استبدال قائمة الشورتس في الـ JavaScript
    pattern_shorts = r"const shortsData = \[[^\]]*\]"
    html_content = re.sub(
        pattern_shorts,
        f"const shortsData = [{shorts_array}]",
        html_content
    )
    
    # استبدال دالة playVideo بـ playVideoInModal (تشغيل <video> بدلاً من iframe)
    play_function = '''
        function playVideoInModal(videoUrl) {
            const modal = document.getElementById('videoModal');
            const videoFrame = document.getElementById('videoFrame');
            
            // تحويل iframe إلى <video>
            if (videoFrame.tagName === 'IFRAME') {
                const videoElement = document.createElement('video');
                videoElement.id = 'videoFrame';
                videoElement.className = 'w-full h-full';
                videoElement.controls = true;
                videoElement.autoplay = true;
                videoFrame.parentNode.replaceChild(videoElement, videoFrame);
            }
            
            const videoElement = document.getElementById('videoFrame');
            videoElement.src = videoUrl;
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            videoElement.play();
        }
        
        function closeVideo() {
            const modal = document.getElementById('videoModal');
            const videoFrame = document.getElementById('videoFrame');
            modal.classList.add('hidden');
            modal.classList.remove('flex');
            if (videoFrame.pause) videoFrame.pause();
            videoFrame.src = '';
        }
    '''
    
    # استبدال دالة playVideo القديمة
    html_content = re.sub(
        r'function playVideo\([^}]+\}',
        play_function,
        html_content,
        flags=re.DOTALL
    )
    
    return html_content

# ═══════════════════════════════════════════════════════════
# 🚀 البرنامج الرئيسي
# ═══════════════════════════════════════════════════════════

def main():
    print("\n" + "="*60)
    print("🤖 آمِن - روبوت التحديث التلقائي")
    print("="*60 + "\n")
    
    # التحقق من المتغيرات البيئية
    required_vars = {
        'YOUTUBE_API_KEY': YOUTUBE_API_KEY,
        'R2_ACCESS_KEY': R2_ACCESS_KEY,
        'R2_SECRET_KEY': R2_SECRET_KEY,
        'GITHUB_TOKEN': GITHUB_TOKEN
    }
    
    missing = [k for k, v in required_vars.items() if not v]
    if missing:
        print(f"❌ متغيرات بيئية مفقودة: {', '.join(missing)}")
        return
    
    print("✅ جميع المتغيرات البيئية موجودة\n")
    
    all_videos = []
    all_shorts = []
    
    # ═══════════════════════════════════════════════════════════
    # 1️⃣ البحث وتحميل الفيديوهات العادية
    # ═══════════════════════════════════════════════════════════
    print("📹 مرحلة 1: الفيديوهات العادية")
    print("-" * 60)
    
    for category, queries in SEARCH_QUERIES.items():
        print(f"\n🏷️ فئة: {category}")
        for query in queries[:2]:  # أول 2 استعلام من كل فئة
            results = search_youtube(query, max_results=2, duration='medium')
            
            for video in results[:1]:  # فيديو واحد فقط من كل استعلام
                video_id = video['id']
                
                # تحميل
                local_file = download_video(video_id, is_short=False)
                if not local_file:
                    continue
                
                # رفع على R2
                public_url = upload_to_r2(local_file, video_id, category)
                if not public_url:
                    continue
                
                # حذف الملف المحلي
                Path(local_file).unlink()
                
                all_videos.append({
                    'id': video_id,
                    'title': video['title'],
                    'url': public_url,
                    'thumbnail': video['thumbnail'],
                    'category': category
                })
                
                print(f"✅ تمت إضافة: {video['title'][:50]}...\n")
    
    # ═══════════════════════════════════════════════════════════
    # 2️⃣ البحث وتحميل الشورتس
    # ═══════════════════════════════════════════════════════════
    print("\n📱 مرحلة 2: الشورتس")
    print("-" * 60)
    
    for query in SHORTS_QUERIES[:3]:  # أول 3 استعلامات
        results = search_youtube(query, max_results=2, duration='short')
        
        for video in results[:1]:  # شورت واحد من كل استعلام
            video_id = video['id']
            
            local_file = download_video(video_id, is_short=True)
            if not local_file:
                continue
            
            public_url = upload_to_r2(local_file, video_id, 'shorts')
            if not public_url:
                continue
            
            Path(local_file).unlink()
            
            all_shorts.append({
                'id': video_id,
                'title': video['title'],
                'url': public_url
            })
            
            print(f"✅ تمت إضافة شورت: {video['title'][:50]}...\n")
    
    # ═══════════════════════════════════════════════════════════
    # 3️⃣ تحديث الموقع
    # ═══════════════════════════════════════════════════════════
    print("\n📝 مرحلة 3: تحديث الموقع")
    print("-" * 60)
    
    if not all_videos and not all_shorts:
        print("⚠️ لا توجد فيديوهات جديدة للإضافة")
        return
    
    # تحميل index.html
    html_content, sha = get_github_file('index.html')
    if not html_content:
        print("❌ فشل تحميل index.html")
        return
    
    # حقن الفيديوهات
    updated_html = inject_videos_into_html(html_content, all_videos, all_shorts)
    
    # رفع التحديث
    commit_msg = f"🤖 تحديث تلقائي: {len(all_videos)} فيديو + {len(all_shorts)} شورت ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
    
    success = update_github_file('index.html', updated_html, commit_msg, sha)
    
    if success:
        print(f"\n🎉 انتهى بنجاح!")
        print(f"   📹 فيديوهات: {len(all_videos)}")
        print(f"   📱 شورتس: {len(all_shorts)}")
        print(f"   🔗 الموقع: https://zenrex.ai/s/amen-platform")
    else:
        print("\n❌ فشل التحديث")

if __name__ == "__main__":
    main()
