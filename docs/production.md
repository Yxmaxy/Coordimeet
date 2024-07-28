# Repository setup
First, copy the `.env.example` file to `.env` and fill in the necessary values. **Please change all important values from the defaults!**

Make sure to set `DJANGO_DEBUG` to `False` in the `.env` file for production!

You can generate the VAPID keys for push notifications on this website: https://web-push-codelab.glitch.me/.


# Running the application with docker
To use docker for production use the following command: `docker compose -f docker-compose.prod.yml up`.

Because the docker setup is slightly different than the one for development, you need to specify the production file with the `-f docker-compose.prod.yml` option.

When the app needs to be rebuilt (whenever there is a new version available) you need to add the `--build` option to the command.

To stop the containers use `docker compose -f docker-compose.prod.yml down`.
