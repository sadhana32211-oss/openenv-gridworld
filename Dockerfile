FROM node:18

WORKDIR /app
COPY . .

# Install Python
RUN apt-get update && apt-get install -y python3 python3-pip

# Optional: make "python" command available
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN npm install

# If you have requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 7860

CMD ["python3", "inference.py"]
