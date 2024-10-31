FROM python:3

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		postgresql-client netcat-openbsd \
	&& rm -rf /var/lib/apt/lists/* \
	&& useradd -ms /bin/bash mainuser

WORKDIR /usr/src/app
COPY src .

RUN chown -R mainuser:mainuser /usr/src/app && \
	pip install --no-cache-dir -r requirements.txt

USER mainuser
