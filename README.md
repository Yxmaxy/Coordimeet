# Coordimeet
Coordimeet is a web service that enables you to easily organise events, invite friends and track activities.

For development and production instructions please refer to the documentation in the [docs](https://github.com/Yxmaxy/Coordimeet/tree/main/docs) folder.

The code which was used as part of my thesis is located on the [diplomska](https://github.com/Yxmaxy/Coordimeet/tree/diplomska) branch.

## Frontend dependencies (GitHub Packages)

The frontend depends on the private `@yxmaxy/*` packages published to [GitHub Packages](https://docs.github.com/en/packages), which require authentication to install. Create a GitHub [personal access token](https://github.com/settings/tokens) with the `read:packages` scope and export it as `YXMAXY_NODE_TOKEN` (for example add `export YXMAXY_NODE_TOKEN=ghp_...` to your `~/.zshrc`), then run `pnpm install` in `frontend/`. The committed `frontend/.npmrc` reads this variable from the environment; note that `pnpm`/`npm` do not read `.env` files for registry auth, so the token must be a real environment variable.
