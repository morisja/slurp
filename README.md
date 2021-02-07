# slurp - make podcasts of audio feeds

## why ?
I found one of my favourite radio shows does not have a podcast

## how does it work ?

runit.sh uses mpv to record a stream for a fixed period of time and apply id3 tags

post-process.py generates a json doc including those tags, and writes the file and the info to gcs, before reading all json files and generating an xml feed file.

## notes
Local

```
# setup local python env
python3 -m venv env
source env/bin/activate
pip3 install google-cloud-storage google-cloud-datastore

# docker build
docker built -t slurp .

# docker run
docker run --env GOOGLE_APPLICATION_CREDENTIALS=/usr/src/app/creds/creds.json  --mount type=bind,source=/src/dir,target=/usr/src/app/creds  slurp:latest

```

