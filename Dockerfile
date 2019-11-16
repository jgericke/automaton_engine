FROM python:3.7
LABEL maintainer="Julian Gericke <julian@lsd.co.za>"
LABEL application="automaton-engine"
LABEL version="1.0.2"
RUN set -x \
    && pip install 'automaton-engine==1.0.2'
USER 1001
CMD automaton-engine
