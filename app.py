from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

def get_stream_url(video_url):
    try:
        # OAuth2 logic for yt-dlp
        ydl_opts = {
            # Ye line OAuth2 activate karegi
            'username': 'oauth2',
            'password': '', 
            
            'format': 'best',
            'nocheckcertificate': True,
            'quiet': False,  # Isse logs mein login code dikhega
            'no_warnings': False,
            
            # Kuch extra headers taaki verification smooth ho
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                }
            },
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            stream_url = info.get('url')
            
            if not stream_url:
                formats = info.get('formats', [])
                for f in reversed(formats):
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                        stream_url = f.get('url')
                        break
            
            return stream_url

    except Exception as e:
        # Error ko console pe print karein taaki code dikhe
        print(f"CRITICAL ERROR: {str(e)}")
        return str(e)

@app.route('/get-video', methods=['GET'])
def get_video():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "URL parameter missing"}), 400

    result = get_stream_url(video_url)

    # Agar result mein 'Sign in' ya code ki baat hai toh wo return karein
    if result and "https" in result:
        return jsonify({"status": "success", "stream_url": result})
    else:
        return jsonify({
            "status": "action_required",
            "message": "Check Render Logs to authorize OAuth2",
            "details": result
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
