# Install dependencies only when needed
FROM node:20

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install

COPY . .

EXPOSE 3000

RUN yarn build
CMD ["yarn", "start"]