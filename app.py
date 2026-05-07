from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

def get_stream_url(video_url):
    try:
        # Professional options for cloud hosting
        ydl_opts = {
            'cookiefile': 'cookies.txt',
            'format': 'best',
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
            # 'youtube_include_dash_manifest': False, # Kabhi kabhi manifest block hota hai
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Connection': 'keep-alive',
            },
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # extract_info calls YouTube
            info = ydl.extract_info(video_url, download=False)
            
            stream_url = info.get('url')
            
            if not stream_url:
                formats = info.get('formats', [])
                for f in reversed(formats):
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                        stream_url = f.get('url')
                        break
            
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
            "message": "Missing 'url' parameter."
        }), 400

    stream_url = get_stream_url(video_url)

    if stream_url:
        return jsonify({
            "status": "success",
            "stream_url": stream_url
        })
    else:
        # Yahan hum detailed error bhej sakte hain logs dekhne ke liye
        return jsonify({
            "status": "error",
            "message": "Failed to fetch stream URL. YouTube might be blocking Render's IP."
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
