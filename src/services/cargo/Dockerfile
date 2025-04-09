FROM python:3.13-slim

RUN apt-get update
WORKDIR /usr/src/app
ADD requirements.txt ./
RUN pip install -r requirements.txt
ADD health_check ./health_check
ADD models/ ./models
ADD proto/ ./proto
ADD repositories/ ./repositories

ADD cargo_service.py ./

RUN mkdir ./grpc_build
RUN python -m grpc_tools.protoc -Igrpc_build=./proto --python_out=./ --pyi_out=./ --grpc_python_out=./ ./proto/cargo_service.proto

EXPOSE ${CARGO_SERVICE_PORT}

ENTRYPOINT [ "python" , "-u", "cargo_service.py"]