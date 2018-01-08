FROM python:3.6

RUN rm -rf /accounting /venvs
COPY . /accounting
WORKDIR /accounting

RUN pip install virtualenv
RUN virtualenv /venvs/accounting
RUN . /venvs/accounting/bin/activate
RUN pip install -r requirements.txt
