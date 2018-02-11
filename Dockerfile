FROM python:3-stretch

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY crypto.py ./

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python", "./crypto.py" ]

