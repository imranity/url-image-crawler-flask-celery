FROM ubuntu:14.04


RUN apt-get update -y && \
    apt-get install -y build-essential curl python-pip python-dev vim

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true

ENV HOST 0.0.0.0
ENV PORT 5000
ENV DEBUG true
# copy source code
COPY . /flask-app
WORKDIR /flask-app

# install requirements
RUN pip install -r requirements.txt

RUN mkdir -p /var/log/supervisor

# expose the app port
EXPOSE 5000

# needs to be set else Celery gives an error (because docker runs commands inside container as root)
ENV C_FORCE_ROOT=1

# run the app server
#ENTRYPOINT ["python"]
#CMD ["app.py"]
