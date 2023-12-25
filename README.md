This application set up an SMTP server that forwards all attachments in the emails to a Paperless-ngx server.
It's particularly useful for all-in-one machines with SMTP support.

## Features:
* Tag document by recipient address. For example, if `EMAIL_DOMAIN` is set to `local`, then recipient address `electronic.receipt@local` will tag the document with these two tags: `electronic` and `receipt`. If the tag does not already exist in the Paperless-ngx server, they'll be created automatically.

## Getting started:

### Running directly:

I use Python 3.12 for this project, but 3.11 should work too.
```shell
# clone the repo, then cd into the project root

# create virtual environment
$ python -m venv .venv

# activate venv
$ source .venv/bin/activate

# install dependencies
$ pip install -r requirements.txt

# run from src folder
$ cd src

$ EMAIL_DOMAIN=local \
LOG_LEVEL=INFO \
PAPERLESS_PASSWORD=mypassword \
PAPERLESS_URL=http://mypaperless-ngx.com:8000 \
PAPERLESS_USERNAME=myusername \
SMTP_HOST=0.0.0.0 \
SMTP_PORT=1025 \
python main.py
```

### Docker:

The image is built for `linux/amd64` `linux/386` `linux/arm64/v8` `linux/arm/v7` `linux/arm/v5`

```shell
$ docker run --rm \
    -p "1025:1025" \
    -e EMAIL_DOMAIN=local \
    -e LOG_LEVEL=INFO \
    -e PAPERLESS_PASSWORD=mypassword \
    -e PAPERLESS_URL=http://mypaperless-ngx.com:8000 \
    -e PAPERLESS_USERNAME=myusername \
    -e SMTP_HOST=0.0.0.0 \
    -e SMTP_PORT=1025 \
rabbitaaron/paperless-smtp:latest
```

### Docker compose:

See `docker-compose.yml` for an example, if you already run Paperless-ngx in docker-compose, this service could be added into the same compose file.