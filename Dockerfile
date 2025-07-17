FROM python:3.10.4-slim-bullseye

RUN apt update && apt upgrade -y && \
    apt install -y git curl python3-pip ffmpeg wget bash neofetch software-properties-common

COPY requirements.txt .

RUN pip3 install wheel
RUN pip3 install --no-cache-dir -U -r requirements.txt

WORKDIR /app
COPY . .

EXPOSE 5000

# ✅ Flask + Bot दोनों साथ में reliable चलेंगे
CMD ["bash", "-c", "flask run -h 0.0.0.0 -p 5000 & python3 -m devgagan"]
