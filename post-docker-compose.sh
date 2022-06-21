#!/usr/bin/env bash

# Expose Admin API service
curl -X POST http://localhost:8001/services \
  --data name=admin-api \
  --data host=127.0.0.1 \
  --data port=8001

curl -X POST http://localhost:8001/services/admin-api/routes \
  --data paths\[\]=/admin-api

# Add API gateway as a service for django application
host_ip=$(ifconfig | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p')
curl -X POST http://localhost:8001/services \
    --data name=web-api \
    --data host=$host_ip \
    --data port=8002

curl -X POST http://localhost:8001/services/web-api/routes \
    --data paths\[\]=/web-api

# Add static files for routes
curl -X POST http://localhost:8001/services \
  --data name=web-api-static \
  --data "url=http://$host_ip:8002/static/"

curl -X POST http://localhost:8001/services/web-api-static/routes \
    --data paths\[\]=/static
