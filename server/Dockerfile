FROM node:22-bookworm

WORKDIR /app

RUN apt update -y && \
    apt install -y python3 && \
    apt install -y python3-pip

# Create directories for persistent storage
RUN mkdir -p /app/audio /app/video && \
    chmod -R 777 /app/audio /app/video

COPY requirements.txt .
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

COPY . .

# Create a non-root user and switch to it
RUN useradd -m appuser && chown -R appuser:appuser /app/audio /app/video

USER appuser

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

EXPOSE 12498

CMD ["flask", "run", "--host=0.0.0.0", "--port=12498"]