FROM node:12-slim
WORKDIR ../github-app/
COPY package.json package-lock.json ./
RUN npm ci --production
RUN npm cache clean --force
ENV NODE_ENV="production"
COPY . .
CMD [ "npm", "start" ]
