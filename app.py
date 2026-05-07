
from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

def get_stream_url(video_url):
    try:
        # Professional options for yt-dlp
        ydl_opts = {
            'cookiefile': 'cookies.txt',  # Ye line add karni hai
            'format': 'best',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Direct URL dhoondne ka logic
            stream_url = info.get('url')
            
            # Agar direct URL nahi mila toh formats check karega
            if not stream_url:
                formats = info.get('formats', [])
                for f in formats:
                    if f.get('ext') == 'mp4' and f.get('url'):
                        stream_url = f['url']
                        break
            
            return stream_url

    except Exception as e:
        print(f"Error: {str(e)}")
        return None

@app.route('/get-video', methods=['GET'])
def get_video():
    # URL parameter browser se lega
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
            "video_title": "Fetched", 
            "stream_url": stream_url
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Failed to fetch stream URL. The video might be restricted."
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)