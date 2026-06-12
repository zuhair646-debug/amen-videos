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

# ═══════════════════════════════════════════════════════════
# ⚙️ الإعدادات (من المتغيرات البيئية)
# ═══════════════════════════════════════════════════════════

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
R2_ACCESS_KEY = os.getenv('R2_ACCESS_KEY')
R2_SECRET_KEY = os.getenv('R2_SECRET_KEY')
R2_ENDPOINT = os.getenv('R2_ENDPOINT', 'https://4b90df683b9a565b655148c1d090ddb1.r2.cloudflarestorage.com')
R2_BUCKET = os.getenv('R2_BUCKET', 'amen-videos')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'zuhair646-debug/amen-videos')

# ═══════════════════════════════════════════════════════════
# 🔍 البحث في YouTube
# ═══════════════════════════════════════════════════════════

def search_youtube(query, max_results=5, duration='short'):
    """
    يبحث عن فيديوهات آمنة في YouTube
    duration: 'short' (< 4 دقائق) أو 'medium' (4-20 دقيقة)
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
        'order': 'viewCount'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        videos = []
        for item in data.get('items', []):
            video_id = item['id']['videoId']
            snippet = item['snippet']
            videos.append({
                'id': video_id,
                'title': snippet['title'],
                'description': snippet['description'][:200],
                'thumbnail': snippet['thumbnails']['high']['url'],
                'channel': snippet['channelTitle'],
                'published': snippet['publishedAt']
            })
        
        print(f"✅ وجدت {len(videos)} فيديو لـ '{query}'")
        return videos
        
    except Exception as e:
        print(f"❌ خطأ في البحث: {e}")
        return []

# ═══════════════════════════════════════════════════════════
# ⬇️ تحميل الفيديو
# ═══════════════════════════════════════════════════════════

def download_video(video_id, is_short=False):
    """
    يحمّل فيديو من YouTube بـ yt-dlp
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_dir = Path("downloads")
    output_dir.mkdir(exist_ok=True)
    
    # إعدادات التحميل
    format_option = 'bestvideo[height<=720]+bestaudio/best[height<=720]' if not is_short else 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
    output_template = str(output_dir / f"{video_id}.%(ext)s")
    
    cmd = [
        'yt-dlp',
        '--format', format_option,
        '--merge-output-format', 'mp4',
        '--output', output_template,
        '--no-playlist',
        '--quiet',
        '--no-warnings',
        url
    ]
    
    try:
        print(f"⬇️ يحمّل: {video_id}...")
        subprocess.run(cmd, check=True, timeout=300)
        
        # ابحث عن الملف المحمّل
        video_file = output_dir / f"{video_id}.mp4"
        if video_file.exists():
            print(f"✅ تم التحميل: {video_file}")
            return str(video_file)
        else:
            print(f"❌ الملف غير موجود: {video_file}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"⏱️ انتهى وقت التحميل لـ {video_id}")
        return None
    except Exception as e:
        print(f"❌ خطأ في التحميل: {e}")
        return None

# ═══════════════════════════════════════════════════════════
# ☁️ رفع على Cloudflare R2
# ═══════════════════════════════════════════════════════════

def upload_to_r2(file_path, video_id):
    """
    يرفع ملف على Cloudflare R2
    """
    try:
        # إنشاء S3 client لـ R2
        s3 = boto3.client(
            's3',
            endpoint_url=R2_ENDPOINT,
            aws_access_key_id=R2_ACCESS_KEY,
            aws_secret_access_key=R2_SECRET_KEY,
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )
        
        # اسم الملف في R2
        object_name = f"videos/{video_id}.mp4"
        
        print(f"☁️ يرفع على R2: {object_name}...")
        
        # رفع الملف
        with open(file_path, 'rb') as f:
            s3.upload_fileobj(
                f,
                R2_BUCKET,
                object_name,
                ExtraArgs={'ContentType': 'video/mp4'}
            )
        
        # بناء الـ URL العام
        public_url = f"{R2_ENDPOINT}/{R2_BUCKET}/{object_name}"
        
        print(f"✅ تم الرفع: {public_url}")
        return public_url
        
    except Exception as e:
        print(f"❌ خطأ في الرفع على R2: {e}")
        return None

# ═══════════════════════════════════════════════════════════
# 📝 تحديث الموقع (index.html)
# ═══════════════════════════════════════════════════════════

def update_website(new_videos, is_short=False):
    """
    يضيف الفيديوهات الجديدة للموقع ويرفع التحديث على GitHub
    """
    try:
        # تحميل index.html الحالي من GitHub
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/index.html"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        file_data = response.json()
        import base64
        html_content = base64.b64decode(file_data['content']).decode('utf-8')
        
        # بناء كود HTML للفيديوهات الجديدة
        section_id = 'shortsGrid' if is_short else 'videosGrid'
        
        video_cards = []
        for video in new_videos:
            if is_short:
                card = f"""
                <div class="bg-gray-800 rounded-xl overflow-hidden hover:scale-105 transition cursor-pointer" 
                     onclick="openShortPlayer('{video['url']}', '{video['title'].replace("'", "\\'")}')">
                  <div class="relative aspect-[9/16]">
                    <img src="{video['thumbnail']}" alt="{video['title']}" class="w-full h-full object-cover">
                    <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent"></div>
                    <div class="absolute bottom-0 left-0 right-0 p-4">
                      <h3 class="font-bold text-white mb-1 line-clamp-2">{video['title']}</h3>
                      <p class="text-sm text-gray-300">{video['channel']}</p>
                    </div>
                  </div>
                </div>"""
            else:
                card = f"""
                <div class="bg-gray-800 rounded-xl overflow-hidden hover:scale-105 transition">
                  <img src="{video['thumbnail']}" alt="{video['title']}" class="w-full h-48 object-cover">
                  <div class="p-4">
                    <h3 class="font-bold mb-2 line-clamp-2">{video['title']}</h3>
                    <p class="text-sm text-gray-400 mb-3 line-clamp-2">{video['description']}</p>
                    <span class="inline-block bg-emerald-500/20 text-emerald-400 text-xs px-3 py-1 rounded-full">
                      {video['channel']}
                    </span>
                  </div>
                </div>"""
            
            video_cards.append(card)
        
        # إضافة الفيديوهات الجديدة
        insert_marker = f'id="{section_id}"'
        if insert_marker in html_content:
            # ابحث عن نهاية div الأول بعد المحدد
            start_pos = html_content.find(insert_marker)
            grid_start = html_content.find('>', start_pos) + 1
            
            # أضف الفيديوهات الجديدة في البداية
            html_content = (
                html_content[:grid_start] +
                '\n          ' + '\n          '.join(video_cards) +
                html_content[grid_start:]
            )
        
        # رفع التحديث على GitHub
        update_data = {
            'message': f'🤖 إضافة {len(new_videos)} فيديو جديد تلقائياً - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            'content': base64.b64encode(html_content.encode()).decode(),
            'sha': file_data['sha']
        }
        
        response = requests.put(url, headers=headers, json=update_data, timeout=15)
        response.raise_for_status()
        
        print(f"✅ تم تحديث الموقع بـ {len(new_videos)} فيديو!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تحديث الموقع: {e}")
        return False

# ═══════════════════════════════════════════════════════════
# 🎬 العملية الكاملة
# ═══════════════════════════════════════════════════════════

def process_videos(query, is_short=False, max_videos=3):
    """
    العملية الكاملة: بحث → تحميل → رفع → تحديث
    """
    print(f"\n{'='*60}")
    print(f"🎬 بدء المعالجة: {query}")
    print(f"📊 النوع: {'Shorts' if is_short else 'فيديوهات عادية'}")
    print(f"{'='*60}\n")
    
    # 1. البحث
    videos = search_youtube(query, max_results=max_videos, duration='short' if is_short else 'medium')
    if not videos:
        print("❌ لم يتم العثور على فيديوهات")
        return
    
    # 2. معالجة كل فيديو
    processed_videos = []
    for video in videos[:max_videos]:
        video_id = video['id']
        
        # تحميل
        file_path = download_video(video_id, is_short)
        if not file_path:
            continue
        
        # رفع على R2
        r2_url = upload_to_r2(file_path, video_id)
        if not r2_url:
            continue
        
        # حذف الملف المحلي
        try:
            os.remove(file_path)
            print(f"🗑️ تم حذف الملف المحلي")
        except:
            pass
        
        # إضافة للقائمة
        processed_videos.append({
            'title': video['title'],
            'description': video['description'],
            'thumbnail': video['thumbnail'],
            'channel': video['channel'],
            'url': r2_url
        })
    
    # 3. تحديث الموقع
    if processed_videos:
        update_website(processed_videos, is_short)
        print(f"\n✅ تمت معالجة {len(processed_videos)} فيديو بنجاح!\n")
    else:
        print("\n❌ لم تتم معالجة أي فيديو\n")

# ═══════════════════════════════════════════════════════════
# 🚀 نقطة البداية
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        🤖 آمِن - روبوت التحديث التلقائي 🤖              ║
    ║                                                           ║
    ║   منصة الفيديوهات العائلية الآمنة                        ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # فحص المتغيرات البيئية
    missing = []
    if not YOUTUBE_API_KEY: missing.append('YOUTUBE_API_KEY')
    if not R2_ACCESS_KEY: missing.append('R2_ACCESS_KEY')
    if not R2_SECRET_KEY: missing.append('R2_SECRET_KEY')
    if not GITHUB_TOKEN: missing.append('GITHUB_TOKEN')
    
    if missing:
        print(f"❌ متغيرات بيئية ناقصة: {', '.join(missing)}")
        print("\nأضف المتغيرات في Railway:")
        print("  Variables → RAW Editor → الصق المفاتيح\n")
        exit(1)
    
    print("✅ كل المتغيرات البيئية موجودة!\n")
    
    # قوائم البحث
    SEARCH_QUERIES = [
        # فيديوهات عادية (تعليمية/عائلية)
        ('قصص الأنبياء للأطفال', False),
        ('تعليم القرآن للصغار', False),
        ('أناشيد إسلامية بدون موسيقى', False),
        ('حكايات قبل النوم للأطفال', False),
        
        # Shorts
        ('أذكار الصباح', True),
        ('آداب إسلامية للأطفال', True),
        ('فوائد علمية سريعة', True),
    ]
    
    # معالجة كل قائمة
    for query, is_short in SEARCH_QUERIES:
        try:
            process_videos(query, is_short, max_videos=2)
        except KeyboardInterrupt:
            print("\n\n⏹️ تم الإيقاف يدوياً")
            break
        except Exception as e:
            print(f"\n❌ خطأ عام: {e}\n")
            continue
    
    print("\n✅ انتهت العملية!\n")
