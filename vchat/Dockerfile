FROM python:3.10

EXPOSE 8888

WORKDIR /usr/local/voice-chat

COPY server/*.py ./server/
COPY *.py ./
COPY requirements.txt ./

RUN apt update \
    && apt install -y portaudio19-dev \
    && apt install -y python3-pyaudio \
    && pip install -r requirements.txt

CMD python3 server/server.py
