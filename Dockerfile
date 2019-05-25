FROM python:3.7
LABEL maintainer="Julian Gericke <julian@lsd.co.za>"
LABEL application="automaton"
LABEL version="1.0.0"
WORKDIR /opt/automaton
ADD actions /opt/automaton/actions
ADD automaton /opt/automaton/automaton
ADD bin /opt/automaton/bin
COPY setup.cfg setup.py LICENSE ./
RUN set -x \
    && python setup.py build \
    && python setup.py install
RUN set -x \
    && useradd -u 1001 -M -g root -r automaton \
    && chown -R 1001:0 /opt/automaton \
    && chmod -R ug+rwx /opt/automaton 
USER 1001
CMD python /opt/automaton/bin/auto.py
