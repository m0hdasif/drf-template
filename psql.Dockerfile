FROM postgres:13
COPY create-multiple-psql-db.sh /docker-entrypoint-initdb.d/
