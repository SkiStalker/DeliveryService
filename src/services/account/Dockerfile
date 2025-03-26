FROM python:3.13-slim

RUN apt-get update
WORKDIR /usr/src/app
ADD requirements.txt ./
RUN pip install -r requirements.txt
ADD health_check ./health_check
ADD clients/ ./clients
ADD models/ ./models
ADD proto/ ./proto
ADD repositories/ ./repositories

ADD account_service.py ./

RUN mkdir ./grpc_build
RUN python -m grpc_tools.protoc -Igrpc_build=./proto --python_out=./ --pyi_out=./ --grpc_python_out=./ ./proto/account_service.proto

EXPOSE ${ACCOUNT_SERVER_PORT}

ENTRYPOINT [ "python" , "-u", "account_service.py"]