FROM node:22-alpine

RUN apk update && apk upgrade --no-cache && npm install -g npm@latest

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
