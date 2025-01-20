FROM node:22-slim
WORKDIR /app
COPY web_app_2/package.json /app/package.json
COPY web_app_2/package-lock.json /app/package-lock.json
RUN npm ci
CMD ["npm", "run", "dev"]
