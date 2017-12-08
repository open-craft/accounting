# OpenCraft Accounting (WIP)

An automated accounting system that can do the following:

1. Register company members and clients who need to bill or be billed.
1. Automatically generate invoices using **JIRA worklogs** for incoming invoices.
1. Process outgoing payments automatically through **TransferWise**.
1. Push JIRA worklogs to **Freshbooks** as line items.
1. Create invoices on Freshbooks based off of previously pushed line items.

## Developmental Setup

NOTE: The following setup assumes a Linux-like environment with Python 3.6. You may be able to use a lower version, but we stick the docker containers to Python 3.6.

The OpenCraft Accounting application can be developed using Docker containers.

In fact, to run tests or basically anything with Django management commands, you'll need docker containers running for the several services required, because of setting requirements.

### Environmental Settings

A sample development environment settings file is in `.environ/.env.dev`. You can copy this over to your root as `.env` to use if you'd like to run `make tests` outside of a Docker container, for example.

### Setting up Docker

In order to be able to get containers started, you'll need access to the `docker-compose` command.

First install it using developmental requirements:

```bash
# This assumes your `virtualenv` is on Python 3.x. If not, use the appropriate one.
$ virtualenv accounting
$ . accounting/bin/activate
(accounting) $ pip install -r requirements/dev.txt
```

If you come up with any funky issues while setting up, make sure you have the latest `python3.6-dev` and `build-essential` packages installed. You might also want to upgrade to the latest packages you install.

With `docker-compose` now available, you can simply run:

```bash
(accounting) $ docker-compose up
```

And you'll see the service logs in your terminal once the relevant containers are pulled and built.

You can now go to `localhost:1786` to see the Accounting application ready for use!

### Running Tests

With the Docker containers online, you can run any of the `Makefile` targets like `test` with `make test` to run all quality and unit tests.

## Production Setup

TBD
