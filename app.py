from flask import Flask, request, jsonify
import yt_dlp
import os
import tempfile

app = Flask(__name__)

def get_cookies_file():
    cookie_data = os.environ.get("YOUTUBE_COOKIES")
    if cookie_data:
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        tmp.write(cookie_data)
        tmp.flush()
        tmp.close()
        print(f"DEBUG: Using cookies from ENV, length={len(cookie_data)}")
        return tmp.name, True

    local_path = os.path.join(os.path.dirname(__file__), "youtube_cookies.txt")
    if os.path.exists(local_path):
        print(f"DEBUG: Using cookies from FILE: {local_path}")
        return local_path, False

    print("DEBUG: No cookies found!")
    return None, False

def get_stream_url(video_url):
    cookies_file, is_temp = get_cookies_file()
    try:
        # Attempt 1: Cookies ke saath web clients
        ydl_opts = {
            'format': 'best/bestvideo+bestaudio',
            'nocheckcertificate': True,
            'quiet': False,
            'extractor_args': {
                'youtube': {
                    'player_client': ['web_creator', 'web_embedded', 'web'],
                }
            },
        }

        if cookies_file:
            ydl_opts['cookiefile'] = cookies_file
            print(f"DEBUG: cookiefile set to {cookies_file}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            stream_url = info.get('url')

            if not stream_url:
                formats = info.get('formats', [])
                for f in reversed(formats):
                    if f.get('url'):
                        stream_url = f.get('url')
                        break

            return stream_url

    except Exception as e:
        # Attempt 2: Cookies ke bina android_vr
        print(f"Attempt 1 failed: {str(e)}, trying android_vr without cookies...")
        try:
            ydl_opts2 = {
                'format': 'best/bestvideo+bestaudio',
                'nocheckcertificate': True,
                'quiet': False,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android_vr'],
                    }
                },
            }

            with yt_dlp.YoutubeDL(ydl_opts2) as ydl:
                info = ydl.extract_info(video_url, download=False)
                stream_url = info.get('url')

                if not stream_url:
                    formats = info.get('formats', [])
                    for f in reversed(formats):
                        if f.get('url'):
                            stream_url = f.get('url')
                            break

                return stream_url

        except Exception as e2:
            print(f"Attempt 2 failed: {str(e2)}")
            return str(e2)

    finally:
        if cookies_file and is_temp and os.path.exists(cookies_file):
            os.unlink(cookies_file)

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

# ========== DEBUG ENDPOINT ==========
@app.route('/list-formats', methods=['GET'])
def list_formats():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "URL parameter missing"}), 400

    cookies_file, is_temp = get_cookies_file()
    try:
        ydl_opts = {
            'nocheckcertificate': True,
            'quiet': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android_vr'],
                }
            },
        }
        if cookies_file:
            ydl_opts['cookiefile'] = cookies_file

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = []
            for f in info.get('formats', []):
                formats.append({
                    'format_id': f.get('format_id'),
                    'ext': f.get('ext'),
                    'vcodec': f.get('vcodec'),
                    'acodec': f.get('acodec'),
                    'url_exists': bool(f.get('url')),
                })
            return jsonify({"formats": formats})
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        if cookies_file and is_temp and os.path.exists(cookies_file):
            os.unlink(cookies_file)
# ========== DEBUG ENDPOINT END ==========

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)