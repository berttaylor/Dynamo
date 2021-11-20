FROM python:3.10.0-slim-buster
ENV PYTHONUNBUFFERED 1

# Replace shell with bash so we can source files
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Update repository sources list, install dependencies
RUN apt-get update \
    && apt-get install -y curl libmagic1 \
    && apt-get -y autoclean

# Django app config
RUN mkdir -p /opt/services/dynamo/src
COPY requirements.txt /opt/services/dynamo/src/
WORKDIR /opt/services/dynamo/src
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /opt/services/dynamo/src
RUN cd dynamo/static

EXPOSE 8000
CMD ["gunicorn", "-c", "dynamo/config/gunicorn/conf.py", "--bind", ":8000", "--chdir", "dynamo", "dynamo.wsgi:application"]
