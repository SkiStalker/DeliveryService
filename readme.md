# Delivery service with microservices
## Table of contents

1. [Summary](#summary)
2. [Technology Stack](#technology-stack)
3. [Structure](#structure)
4. [Usage](#usage)

## Summary
This project is designed to ensure the operation of the goods delivery service. 
A microservice architecture was chosen using gRPC as a communication between microservices and an api gateway.
Security is achieved through the use of JWT tokens.

## Technology Stack
1. Python v3.13
2. gRPC v1.74.2
3. PostgreSQL v17.5

## Structure
- __env_examples__ - examples of all required env files
- __src__ - sources folder
    - __api_gateway__ - web service api gateway with versions
    - __mongo__ - MongoDB init script
    - __postgres__ - PostgreSQL init scripts and Dockerfile
    - __services__ - microservices
- __docker-compose.yaml__ - docker compose start file
- __openapi.json__ - OpenAPI specification for all available api methods

## Usage
1. Install git
```bash
sudo apt-get update
sudo apt-get install git
```

2. Clone repository
```bash
git clone https://github.com/SkiStalker/DeliveryService
```

3. Move to project directory
```bash
cd ./DeliveryServiceGo
```

4. Copy __ALL__ env files from [env_examples](./env_examples) folder to project root and specify your own values in them
```bash
cp ./env_examples/* ./
```

5. Install docker <br>
See [how to install docker](https://docs.docker.com/desktop/setup/install/linux/)

6. Start docker compose
```bash
docker compose up
```