# setup server

# 1: start docker kernel + python
FROM python:3.10.9-slim-bullseye

# 2: ENV: show logs
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# 3: update kernel + install dependencies
RUN apt-get update -y && \
    apt-get install -y gcc libpq-dev && \
    apt-get install libreoffice -y && \
    apt-get install -y libmediainfo-dev

# 4: create project folder: kernel
WORKDIR /app

# 5: Copy requirements
COPY requirements.txt /app/requirements.txt

# 6: install requirements
RUN pip install --upgrade pip && \
    pip install -r /app/requirements.txt

# 7: copy project code --> docker
COPY . /app/
