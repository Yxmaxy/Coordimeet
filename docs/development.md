# Repository setup
Please refer to the [setup](setup.md) documentation for instructions on how to setup the repository. This includes:
- creating an `.env` file
- downloading the Google API PHP client

# Docker development
To use docker follow these steps:
1. Install [Docker desktop](https://www.docker.com/products/docker-desktop/)
2. `cd Coordimeet`
3. To start containers use `docker compose up` 
    - Use `docker compose up -d` to start the containers in the background
    - If you only want to run certain containers specify the name of the container after the command (eg. for only backend use `docker compose up backend`)
4. To stop the containers use `docker compose down` or use the Docker desktop app

**NOTE:** If you change a variable in `.env` you will have to rebuild the docker container by calling `docker compose up --build`


# Node modules
When adding/removing modules you have to delete the volume associated with node_modules and rebuild the image. You can do this in the Docker desktop application.

**Please do not push your package-lock.json to the repository, unless you actually add a new dependency!**
