FROM python:3.13-slim

RUN apt-get update
WORKDIR /usr/src/app
ADD requirements.txt ./
RUN pip install -r requirements.txt
ADD auth.py ./
ADD health_check ./health_check
ADD clients/ ./clients
ADD models/ ./models
ADD proto/ ./proto
ADD repositories/ ./repositories

RUN mkdir ./grpc_build
RUN python -m grpc_tools.protoc -Igrpc_build=./proto --python_out=./ --pyi_out=./ --grpc_python_out=./ ./proto/auth.proto

EXPOSE 50051

ENTRYPOINT [ "python" , "-u", "auth.py"]