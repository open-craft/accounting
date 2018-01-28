FROM python:3.6

RUN rm -rf /accounting
COPY . /accounting
WORKDIR /accounting

RUN pip install pipenv
RUN pipenv install --system
