FROM alpine
RUN apk add --update nodejs npm
WORKDIR /app
COPY ./frontend/package*.json .
RUN npm ci
COPY ./frontend .
COPY .env .
EXPOSE 3000
CMD ["npm", "run", "dev"]
