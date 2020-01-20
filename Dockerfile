FROM jfloff/alpine-python:3.7-onbuild

COPY requirements.txt /requirements.txt
COPY server.py server.py

RUN pip install -r requirements.txt

EXPOSE 8081
CMD python server.py