# Repository setup
First, copy the `.env.example` file to `.env` and fill in the necessary values. **Please change all important values from the defaults!**

Make sure to set `DJANGO_DEBUG` to `False` in the `.env` file for production!

You can generate the VAPID keys for push notifications on this website: https://tools.reactpwa.com/vapid.

After that also copy the `frontend/.env.example` file and copy the public notification key.


# Running the application on Alpine linux (Example)
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

- python manage.py collectstatic
- python manage.py migrate

- service gunicorn start


### Celery
```
#!/sbin/openrc-run

name="Celery Coordimeet"
description="Celery worker for Coordimeet"

# Path to your project directory
directory="/home/website/Coordimeet/backend"

# Python virtual environment
export PYTHON_ENV="/home/website/pyenv"

# Load the environment variables from the .env file
if [ -f /home/website/Coordimeet/.env ]; then
  export $(grep -v '^#' /home/website/Coordimeet/.env | xargs)
fi

pidfile="/run/celeryd/celeryd.pid"

# Run command
command="${PYTHON_ENV}/bin/celery"
command_args="-A coordimeet worker -l INFO -E --pidfile ${pidfile} -D"


depend() {
    need net
    use redis
}

start_pre() {
    checkpath --directory /run/celeryd --owner website:website --mode 0755
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


## Frontend
- apk add --update npm
- su website
- cd /home/website/Coordimeet/frontende
- npx npm-check-updates -u  # update if needed (if newer node version was installed)
- npm run build

### nginx
- apk add nginx
- mkdir sites-enabled
- vi /etc/nginx/nginx.conf
    - add include /etc/nginx/sites-enabled/* to http
- vi /etc/sites-enabled/coordimeet
    ```
    server {
        listen 3000;
        server_name coordimeet.eu;

        location / {
            root /home/website/Coordimeet/frontend/dist;
            index index.html;
            try_files $uri $uri/ /index.html;
        }
    }
    ```
- nginx -t
- service nginx start
