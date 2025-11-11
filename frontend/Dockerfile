FROM node:21.7.1-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production --retry=3 --timeout=60000
COPY . ./
RUN npm run build
CMD cp -r build result_build
