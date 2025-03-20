from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from manager import JOB_MANAGER

app = Flask("youtube-download")
CORS(
    app=app,
    resources={
        r"/*": {"origins": "https://www.youtube.com",},
    }
)

@app.route("/status", methods=["GET"])
def status():
    try:
        jobId = request.args.get("jobId")
        return jsonify(JOB_MANAGER.get_job_status(jobId))
    except:
        return Response(status=404)

@app.route("/audio", methods=["POST"])
def audio():
    try:
        videoId = JOB_MANAGER.create_job(request, True)
        return jsonify({"jobId": videoId, "status": "IN_PROGRESS"})
    except:
        return Response(status=400)

@app.route("/video", methods=["POST"])
def video():
    try:
        videoId = JOB_MANAGER.create_job(request, False)
        return jsonify({"jobId": videoId, "status": "IN_PROGRESS"})
    except:
        return Response(status=400)

if __name__ == "__main__":
    app.run(debug=True, port=12498)