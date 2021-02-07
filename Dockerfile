#FROM python:3
FROM ubuntu:focal
ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update
RUN apt-get install --no-install-recommends  -y mpv id3v2 python3 python3-pip
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# env BUCKET_NAME must be set and assumes a website url
# env GOOGLE_APPLICATION_CREDENTIALS must be set and pointing to a json doc
CMD [ "./run.sh" ]
