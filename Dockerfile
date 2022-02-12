FROM python:3.10.0-slim-buster
ENV PYTHONUNBUFFERED 1

# Replace shell with bash so we can source files
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Update repository sources list, install dependencies
RUN apt-get update \
    && apt-get install -y curl libmagic1 \
    && apt-get -y autoclean

# Django app config
RUN mkdir -p /opt/services/collabl/src
COPY requirements.txt /opt/services/collabl/src/
WORKDIR /opt/services/collabl/src
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /opt/services/collabl/src
RUN cd collabl/static

EXPOSE 8000
CMD ["gunicorn", "-c", "collabl/config/gunicorn/conf.py", "--bind", ":8000", "--chdir", "collabl", "collabl.wsgi:application"]
