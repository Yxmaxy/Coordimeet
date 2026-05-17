FROM node:22-alpine

RUN apk add --no-cache git openssh-client && \
    npm install -g pnpm@10

WORKDIR /app

COPY ./package.json ./pnpm-lock.yaml ./.npmrc ./
RUN pnpm install --frozen-lockfile

COPY . .

EXPOSE 3000
CMD ["pnpm", "dev"]
