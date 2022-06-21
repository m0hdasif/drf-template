FROM kong:latest

USER root

ENV KONG_PLUGINS=bundled,kong-spec-expose
RUN luarocks install kong-spec-expose

USER kong
