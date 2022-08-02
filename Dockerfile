FROM python:3.9 
WORKDIR /usr/app/src
COPY main.py ./
COPY requirements.txt ./
COPY database.py ./
RUN pip install -r requirements.txt