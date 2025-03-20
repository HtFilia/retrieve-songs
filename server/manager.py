from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import base64
import hashlib
from helper import UrlHelper
from pytubefix import YouTube, Stream

DEFAULT_TTL = 300

def create_job_id(video_title: str):
    digest = hashlib.sha256(video_title.encode()).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip('=')

class JobStatus:
    def __init__(self, job_id, ttl=DEFAULT_TTL):
        self.status = "IN_PROGRESS"
        self.job_id = job_id
        self.expires_at = datetime.now() + timedelta(seconds=ttl)
        self.ttl = ttl
        self.percent_completion = 0.0
        self.url = None
        self.error_reason = None

    def update(self, percent: float):
        self.percent_completion = percent
        self._extend_ttl()
    
    def finish(self, url: str):
        self.percent_completion = 1.0
        self.status = "DONE"
        self.url = url
        self._extend_ttl()
    
    def error(self, reason):
        self.status = "ERROR"
        self.error_reason = reason
        self._extend_ttl()

    def _extend_ttl(self):
        self.expires_at = datetime.now() + timedelta(seconds=self.ttl)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class JobManager(metaclass=Singleton):
    def __init__(self):
        self.jobs = {}
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.cleaner_thread = threading.Thread(target=self._cleanup_jobs, daemon=True)
        self.cleaner_thread.start()

    def create_job(self, request, only_audio):
        video_id = UrlHelper.fetch_youtube_id(request)
        yt = YouTube(UrlHelper.youtube_url(video_id),
                     "WEB",
                     on_progress_callback=_progress_job,
                     on_complete_callback=_complete_job,
                    )
        job_id = create_job_id(yt.title)
        with self.lock:
            self.jobs[job_id] = JobStatus(job_id)
        self.executor.submit(self._process_job, job_id, yt, only_audio)
        return video_id

    def get_job_status(self, job_id):
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                return None
            if job.status == "DONE":
                del self.jobs[job_id]
                return {"status": job.status, "url": job.url}
            return {"status": job.status, "progress": job.progress}
    
    def update_job(self, video_title: str, percent_completion: float):
        job_id = create_job_id(video_title)
        print(f"{video_title} complete at {percent_completion}")
        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id].update(percent_completion)
    
    def finish_job(self, video_title: str, file_path: str):
        job_id = create_job_id(video_title)
        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id].finish(file_path)
                del self.jobs[job_id]
        print(f"exposing file to url: {file_path}")

    def _process_job(self, job_id: str, yt: YouTube, only_audio: bool):
        try:
            path = "audio" if only_audio else "video"
            if only_audio:
                ys = yt.streams.get_audio_only()
            else:
                ys = yt.streams.get_highest_resolution()
            ys.download(output_path=path)

        except Exception as e:
            with self.lock:
                if job_id in self.jobs:
                    self.jobs[job_id].error(str(e))

    def _cleanup_jobs(self):
        while True:
            time.sleep(60)  # Run cleanup every minute
            now = datetime.now()
            with self.lock:
                to_delete = [job_id for job_id, job in self.jobs.items() 
                            if now > job.expires_at]
                for job_id in to_delete:
                    del self.jobs[job_id]

JOB_MANAGER = JobManager()

def _progress_job(stream: Stream, chunk, bytes_remaining):
    video_title = stream.default_filename
    print(f"progress for {video_title}")
    total_filesize = stream.filesize
    bytes_downloaded = total_filesize - bytes_remaining
    percent_completion = bytes_downloaded / total_filesize
    JOB_MANAGER.update_job(video_title, percent_completion)

def _complete_job(stream: Stream, file_path):
    video_title = stream.default_filename
    print(f"completed download for {video_title}")
    JOB_MANAGER.finish_job(video_title, file_path)
