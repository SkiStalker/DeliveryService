FROM python:3.13-slim

RUN apt-get update
WORKDIR /usr/src/app
ADD api_gateway/requirements.txt ./
RUN pip install -r requirements.txt

ADD api_gateway/context.py ./
ADD api_gateway/main.py ./

ADD api_gateway/models ./models
ADD api_gateway/routes ./routes
ADD api_gateway/lib ./lib

COPY services/account/proto/ ./proto/
RUN python -m grpc_tools.protoc -Igrpc_build=./proto --python_out=./ --pyi_out=./ --grpc_python_out=./ ./proto/account_service.proto

COPY services/user/proto/ ./proto/
RUN python -m grpc_tools.protoc -Igrpc_build=./proto --python_out=./ --pyi_out=./ --grpc_python_out=./ ./proto/user_service.proto

EXPOSE ${API_PORT}

ENTRYPOINT [ "uvicorn" , "main:app"]