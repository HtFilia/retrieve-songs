from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import threading
import time
from helper import UrlHelper
from pytubefix import YouTube

DEFAULT_TTL = 300

class JobStatus:
    def __init__(self, video_id, ttl=DEFAULT_TTL):
        self.status = "IN_PROGRESS"
        self.video_id = video_id
        self.expires_at = datetime.now() + timedelta(seconds=ttl)
        self.ttl = ttl
        self.url = None

    def extend_ttl(self):
        self.expires_at = datetime.now() + timedelta(seconds=self.ttl)

class JobManager:
    def __init__(self):
        self.jobs = {}
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.cleaner_thread = threading.Thread(target=self._cleanup_jobs, daemon=True)
        self.cleaner_thread.start()

    def create_job(self, request, only_audio):
        video_id = UrlHelper.fetch_youtube_id(request)
        with self.lock:
            self.jobs[video_id] = JobStatus(video_id)
        
        # Submit to thread pool
        self.executor.submit(self._process_job, video_id, only_audio)
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

    def _process_job(self, video_id, only_audio):
        try:
            path = "audio" if only_audio else "video"
            yt = YouTube(UrlHelper.youtube_url(video_id), "WEB", on_progress_callback=_progress_job)
            if only_audio:
                ys = yt.streams.get_audio_only()
            else:
                ys = yt.streams.get_highest_resolution()
            ys.download(output_path=path)
            for i in range(1, 101):
                time.sleep(0.1)  # Simulate work
                with self.lock:
                    if video_id in self.jobs:
                        self.jobs[video_id].extend_ttl()

            with self.lock:
                if video_id in self.jobs:
                    self.jobs[video_id].status = "DONE"
                    self.jobs[video_id].url = f"https://cdn.example.com/{video_id}.mp4"

        except:
            with self.lock:
                if video_id in self.jobs:
                    self.jobs[video_id].status = "ERROR"

    def _cleanup_jobs(self):
        while True:
            time.sleep(60)  # Run cleanup every minute
            now = datetime.now()
            with self.lock:
                to_delete = [job_id for job_id, job in self.jobs.items() 
                           if now > job.expires_at]
                for job_id in to_delete:
                    del self.jobs[job_id]

def _progress_job():
    pass