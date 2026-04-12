FROM node:18-bullseye

# Install Python and create python command
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    ln -sf /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Node dependencies
RUN npm install

# Expose port
EXPOSE 7860

# Start app
CMD ["node", "index.js"]
