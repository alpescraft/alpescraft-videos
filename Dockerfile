FROM python:3.10

RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    exiftool \
    && rm -rf /var/lib/apt/lists/*

#RUN pip install --upgrade pip
ADD pyproject.toml poetry.lock src /
RUN pip install poetry && poetry install





