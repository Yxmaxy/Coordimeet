# Repository setup
First, copy the `.env.example` file to `.env` and fill in the necessary values. **Please change all important values from the defaults!**

Make sure to set `DJANGO_DEBUG` to `False` in the `.env` file for production!

You can generate the VAPID keys for push notifications on this website: https://web-push-codelab.glitch.me/.


# Running the application with docker
To use docker for production use the following command: `docker compose -f docker-compose.prod.yml up`.

Because the docker setup is slightly different than the one for development, you need to specify the production file with the `-f docker-compose.prod.yml` option.

When the app needs to be rebuilt (whenever there is a new version available) you need to add the `--build` option to the command.

To stop the containers use `docker compose -f docker-compose.prod.yml down`.


# Running the application on Alpine linux
- vi /etc/apk/repositories  # uncomment line
- apk update
- apk add git
- apk add postgresql

## DATABASE setup
- The postgres user is automatically created

### Create socket directory
- mkdir /run/postgresql
- chown postgres:postgres /run/postgresql/

### Start server
- service postgresql start
- su postgres
- psql

### Database setup
- create database coordimeet;
- create user coordimeet with encrypted password 'SomeUnsafePassword';
- grant postgres to coordimeet;  # UNSAFE; CHANGE ASAP! Migrations don/t work without it

### Create website user
- adduser -D website

## Python setup
- apk add --no-cache python3

### Python environment
- su website
- cd
- python -m venv /home/website/pyenv
- source pyenv/bin/activate
- chown -R website:website /home/website/pyenv

## Repo
- git clone https://github.com/Yxmaxy/Coordimeet
- cd Coordimeet/backend
- pip install -r requirements.txt
- cd ..
- cp .env.example .env
- Change the variables...

## Redis
- exit (to sudo)
- apk add redis
- service redis start

## Celery
- vi /etc/init.d/celeryd

```
#!/sbin/openrc-run

command="/usr/bin/python3"
command_args="/root/pyenv/bin/celery -A tasks worker --loglevel=info"
pidfile="/run/celeryd.pid"
name="celeryd"

depend() {
    need redis
}

start_pre() {
    checkpath --directory --mode 755 /run/celeryd
}

start() {
    ebegin "Starting $name"
    start-stop-daemon --start --make-pidfile --pidfile "$pidfile" --background --user nobody \
        --exec "$command" -- $command_args
    eend $?
}

stop() {
    ebegin "Stopping $name"
    start-stop-daemon --stop --pidfile "$pidfile"
    eend $?
}
```
- chmod +x /etc/init.d/celeryd
- rc-update add celeryd default
- service celeryd start


## Backend
- vi /etc/init.d/gunicorn

```
#!/sbin/openrc-run

name="Gunicorn Coordimeet"
description="Gunicorn application server for Coordimeet"

# Path to your project directory
directory="/home/website/Coordimeet/backend"

# Python virtual environment
export PYTHON_ENV="/home/website/pyenv"

# Load the environment variables from the .env file
if [ -f /home/website/Coordimeet/.env ]; then
  export $(grep -v '^#' /home/website/Coordimeet/.env | xargs)
fi

# Run command
command="${PYTHON_ENV}/bin/gunicorn"
command_args="--workers 3 --bind 0.0.0.0:8000 --daemon --pid /run/gunicorn/gunicorn.pid --access-logficommand_user="website"

pidfile="/run/gunicorn/gunicorn.pid"

depend() {
    need net
    use dns logger
}

start_pre() {
    checkpath --directory /run/gunicorn --owner website:website --mode 0755
}

stop() {
    ebegin "Stopping ${name}"
    start-stop-daemon --stop --pidfile ${pidfile} --retry TERM/30/KILL/5
    eend $?
}

restart() {
    ebegin "Restarting ${name}"
    svc_stop
    svc_start
    eend $?
}
```

- chmod +x /etc/init.d/gunicorn
- rc-update add gunicorn default
- chown -R website:website /run/gunicorn

- service gunicorn start
