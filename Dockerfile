FROM python:3.6
ENV PYTHONUNBUFFERED=1 \
    POSTGRES_PASSWORD='password'
COPY . /accounting
WORKDIR /accounting
RUN pip install -r requirements/dev.txt
