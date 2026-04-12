FROM node:18

# Install Python
RUN apt-get update && apt-get install -y python3 python3-pip

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install Node dependencies
RUN npm install

# Expose port
EXPOSE 7860

# Start server
CMD ["node", "index.js"]
COPY . .

# Expose port
EXPOSE 7860

# Set environment variables
ENV NODE_ENV=production
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/api/env/info || exit 1

# Start command
CMD ["python", "inference.py"]
