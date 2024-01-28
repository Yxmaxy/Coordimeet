# Repository setup
Please refer to the [setup](setup.md) documentation for instructions on how to setup the repository. This includes:
- creating an `.env` file - **it is mandatory to change the variables from the defaults!**
- downloading the Google API PHP client

# Running the application with docker
To use docker for production use the following command: `docker compose -f docker-compose.prod.yml up`.

Because the docker setup is slightly different than the one for development, you need to specify the production file with the `-f docker-compose.prod.yml` option.

When the app needs to be rebult (whenever there is a new version available) you need to add the `--build` option to the command.

To run the application in the background use the `-d` flag.
