from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

def get_stream_url(video_url):
    try:
        # Professional options for cloud hosting (Render/Heroku)
        ydl_opts = {
            'cookiefile': 'cookies.txt',  # Ensure this file exists in your root folder
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'nocheckcertificate': True,  # Cloud servers ke SSL issues fix karne ke liye
            'extract_flat': False,
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # extract_info calls YouTube
            info = ydl.extract_info(video_url, download=False)
            
            # 1. Sabse pehle seedha URL check karein
            stream_url = info.get('url')
            
            # 2. Agar seedha nahi mila, toh formats list mein dhoondein
            if not stream_url:
                formats = info.get('formats', [])
                # Reverse loop taaki best quality pehle mile
                for f in reversed(formats):
                    # Humein wo link chahiye jisme video aur audio dono ho (acodec aur vcodec != none)
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                        stream_url = f.get('url')
                        break
            
            # 3. Agar ab bhi nahi mila, toh koi bhi valid URL le lo
            if not stream_url and formats:
                stream_url = formats[0].get('url')
                
            return stream_url

    except Exception as e:
        print(f"Error details: {str(e)}")
        return None

@app.route('/get-video', methods=['GET'])
def get_video():
    video_url = request.args.get('url')

    if not video_url:
        return jsonify({
            "status": "error",
            "message": "Missing 'url' parameter. Usage: /get-video?url=YOUR_LINK"
        }), 400

    stream_url = get_stream_url(video_url)

    if stream_url:
        return jsonify({
            "status": "success",
            "stream_url": stream_url
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Failed to fetch stream URL. Check logs for details."
        }), 500

if __name__ == '__main__':
    # Render automatically sets PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)