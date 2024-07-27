# Repository setup
First, copy the `.env.example` file to `.env` and fill in the necessary values.

You can generate the VAPID keys for push notifications on this website: https://web-push-codelab.glitch.me/.

You can change other values however you want, but the default values should work fine for development.


# Local development
Source the `.env` file if needed by running `source .env` in the root directory.

## Backend (Postgres, Redis, Django and Celery)
1. I recommend using docker for the database and cache servers, so you don't have to spend too much time setting everything up. You can start the servers by running the following commands
    ```bash
    docker compose up db cache -d
    ```

2. Create a new [conda](https://docs.conda.io/en/latest/) environment and install the required packages:
    ```bash
    conda create -n coordimeet python=3.12
    conda activate coordimeet
    pip install -r requirements.txt
    ```

3. Change to the `backend` directory and run the Django server:
    ```bash
    cd backend
    python manage.py runserver
    ```

4. Change to the `backend` directory and run the Celery worker:
    ```bash
    celery -A coordimeet worker -l INFO -E
    ```
    If you want to clear the task queue, you can use the following command:
    ```bash
    celery -A coordimeet purge -f
    ```


## Frontend (Vue)
1. Change to the `frontend` directory and install the required packages:
    ```bash
    cd frontend
    npm ci
    ```

2. Start the development server and open the frontend at `http://localhost:3000` (so that push notifications work):
    ```bash
    npm run dev
    ```

If you want to build the application locally use `npm run build` and the files will be placed in the `frontend/dist` directory. You can then use `npm run preview` to preview the built application.

# Docker development
To use docker follow these steps:
1. Install [Docker desktop](https://www.docker.com/products/docker-desktop/)
2. To start the containers use `docker compose up`
3. To stop the containers use `docker compose down` or use the Docker desktop app

**NOTE:** If you change a variable in `.env` or add a new package to either the backend, you will have to rebuild the docker container by calling `docker compose up --build`. If you add a package to the frontend delete the node_modules volume in docker.
