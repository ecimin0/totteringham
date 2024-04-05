FROM python:3.10-slim

WORKDIR /usr/src/app
COPY requirements.txt ./

RUN apt-get update && apt-get install --no-install-recommends gcc g++ libc-dev make git libffi-dev openssl python3-dev libxml2-dev libxslt-dev musl-dev libpq-dev -y && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --default-timeout=100 --no-cache-dir -r requirements.txt && \
    apt-get purge --auto-remove && \
    apt-get clean

COPY ./ .
EXPOSE 5000
ENTRYPOINT ["gunicorn", "--workers", "1", "--timeout=60", "--preload", "--worker-class", "gevent", "-b", "0.0.0.0:5000", "totteringham:create_app()"]
