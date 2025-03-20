FROM python:3.12

RUN apt-get update
WORKDIR /usr/src/app
ADD requirements.txt ./
RUN pip install -r requirements.txt
ADD main.py ./

EXPOSE 8000

ENTRYPOINT [ "uvicorn" , "main:app"]