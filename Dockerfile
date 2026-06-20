# Basic Dockerfile for running Runekeeper (for advanced hosts)
FROM python:3.11-slim
WORKDIR /app

# system deps for ffmpeg are not included here; host must provide audio support
COPY . /app
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt
RUN pip install yt-dlp PyNaCl

ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "bot.core"]
