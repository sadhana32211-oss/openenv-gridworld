FROM node:18-bullseye

# Install Python properly
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app

COPY . .

RUN npm install

EXPOSE 7860

CMD ["node", "index.js"]
