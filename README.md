# slurp - make podcasts of audio feeds

## Why ?
I found one of my favourite radio shows does not have a podcast

## How does it work ?

mpv records a stream for a fixed period of time, id3 tags are applied

post-process.py generates a json doc of the tags, writes the recording and tags to gcs

post-process.py reads all the json files and to generate a full xml feed file.

## Notes
Local

```
# setup local python env
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
./run.sh
```
Docker
```
# docker build
docker built -t slurp .

# docker run
docker run --env FEED_NAME=<name> --env RECORD_MINS=<mins> --env STREAM_URL=<url> --env BUCKET_NAME=<website-name> --env GOOGLE_APPLICATION_CREDENTIALS=/usr/src/app/creds/creds.json  --mount type=bind,source=/path-to-creds,target=/usr/src/app/creds  slurp:latest
```
