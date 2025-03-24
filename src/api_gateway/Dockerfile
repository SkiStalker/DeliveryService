FROM python:3.13-slim

RUN apt-get update
WORKDIR /usr/src/app
ADD api_gateway/requirements.txt ./
RUN pip install -r requirements.txt
ADD api_gateway/main.py ./
RUN mkdir ./proto
COPY services/auth/proto/ ./proto/

RUN python -m grpc_tools.protoc -Igrpc_build=./proto --python_out=./ --pyi_out=./ --grpc_python_out=./ ./proto/auth.proto

EXPOSE 8000

ENTRYPOINT [ "uvicorn" , "main:app"]