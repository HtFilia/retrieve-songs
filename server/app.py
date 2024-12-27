from pathlib import Path
from flask import Flask, request, Response
from flask_cors import CORS
from pytubefix import YouTube
from concurrent.futures import ThreadPoolExecutor

app = Flask("redirect-server")
CORS(
    app=app,
    resources={
        r"/*": {"origins": "https://www.youtube.com",},
    }
)
executor = ThreadPoolExecutor()

@app.route("/audio", methods=["POST"])
def audio():
    try:
        yt = _from_youtube(request)
        ys = yt.streams.get_audio_only()
        executor.submit(_download_stream, ys, True)
        return Response()
    except:
        return Response(status=400)

@app.route("/video", methods=["POST"])
def video():
    try:
        yt = _from_youtube(request)
        ys = yt.streams.get_highest_resolution()
        executor.submit(_download_stream, ys, False)
        return Response()
    except:
        return Response(status=400)

def _download_stream(stream, is_audio: bool):
    path = "audio" if is_audio else "movie"
    Path(path).mkdir(exist_ok=True)
    stream.download(output_path=path)

def _from_youtube(request) -> YouTube:
    data = request.get_json()
    if not data:
        raise Exception()
    video_url = data.get("url")
    if not video_url:
        raise Exception()
    return YouTube(video_url)

if __name__ == "__main__":
    app.run(debug=True, port=12498)