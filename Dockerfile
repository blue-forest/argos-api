FROM python:slim

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential cmake pkg-config \
  && rm -rf /var/lib/apt/lists/*

RUN pip install argostranslate

ADD start.py /start.py

CMD ["python", "/start.py"]
