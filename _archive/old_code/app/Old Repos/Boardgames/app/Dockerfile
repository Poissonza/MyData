FROM python:3.9-slim

RUN mkdir app
WORKDIR /app
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt



#COPY /python .