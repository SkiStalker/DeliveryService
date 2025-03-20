FROM postgres:alpine

COPY db_scripts /docker-entrypoint-initdb.d

RUN chmod a+r /docker-entrypoint-initdb.d/*