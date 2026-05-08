from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

def get_stream_url(video_url):
    try:
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'nocheckcertificate': True,
            'quiet': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android_vr'],
                }
            },
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            stream_url = info.get('url')

            if not stream_url:
                formats = info.get('formats', [])
                for f in reversed(formats):
                    if (f.get('vcodec') != 'none' and
                        f.get('acodec') != 'none' and
                        f.get('url')):
                        stream_url = f.get('url')
                        break

            return stream_url

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return str(e)

@app.route('/get-video', methods=['GET'])
def get_video():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "URL parameter missing"}), 400

    result = get_stream_url(video_url)

    if result and result.startswith("https"):
        return jsonify({"status": "success", "stream_url": result})
    else:
        return jsonify({
            "status": "error",
            "message": "Failed to extract stream URL",
            "details": result
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)