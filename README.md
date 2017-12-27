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

A sample development environment settings file is in `.environ/.env.dev`. You can copy this over to your root as `.env` to use if you'd like to run `make test` outside of a Docker container, for example.

### JIRA Worklogs Integration

Invoices can be loaded with line items derived from JIRA Tempo worklogs, given that the username of the provider on the invoice is equal to a username on a JIRA instance.

Synchronization is guaranteed -- any line item that's tagged as a JIRA worklog will be checked against incoming JIRA worklogs, and a mismatch leads to deletion, whereas ones that don't exist yet always get added, thus ensuring a complete match for all relevant fields -- issue title, worklog description, worklog quantity, and so on.

You will also need a JIRA user that serves as a sort of 'service user', but it doesn't have to be -- any user that can access any other user's worklogs through the API is good to be used.

Once you fill up `.env` with the proper JIRA variables (making sure to also set `ENABLE_JIRA=true`), you can activate JIRA downloading for individual invoices, and see it work!

### Invoice PDF Generation

Invoice PDFs can be automatically generated given the existing line items.

This feature is orthogonal to other integrations -- it solely depends on what line items exist. So you could add JIRA worklogs automatically, for example, and generated invoice PDFs would contain those worklogs, too, on top of any extra line item you happen to add manually.

To use this feature, you'll need [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html). Download the binary for your development environment, and place the file either in the repository root (it's ignored by git) or somewhere that matches the `HTML_TO_PDF_BINARY_PATH` variable.

### Google Drive Integration

Integration with Google Drive currently depends upon being able to generate invoice PDFs. Once a PDF is generated, the Google Drive Integration can take the resulting file and upload it to some very specific location.

The path expected is as such, given that `year` and `month` are the invoice's billing start date year and month in numerical form, respectively:

```text
year -> invoices-in -> month -> invoice.pdf
```

For example:

```text
2017 -> invoices-in -> 09 -> invoice.pdf
```

This would mean that the integration uploaded `invoice.pdf` to folder `09`, inside folder `invoices-in`, which was inside folder `2017`. This also thus corresponds to the invoice's billing start date being `2017-09-X` where `X` is any day in September.

For your development environment to use Google Drive integration, you'll have to set up a service account on Google Console. This service account can then be associated with PKCS12 credentials, which you can download.

The PKCS12 credentials can be stored as `.p12` in the root of this repository, or anything that matches the `GOOGLE_AUTH_PKCS12_FILE_PATH` setting.

You need to let the integration know the service account's email through `GOOGLE_AUTH_CLIENT_SERVICE_EMAIL` -- this information should be obvious from the console when you create the user, or through the JSON credentials file which you have the option of downloading, akin to downloading the PKCS12 file.

Service accounts also need to be given permission to your (presumably private) Google Drive folder. Given the file path examples above, set `GOOGLE_DRIVE_ROOT` to the ID of the folder that *contains* the year folder, i.e. the one that contains `2017`. The ID for this folder is in the URL when you're actually looking at the folder in your browser.

Make sure to set `ENABLE_GOOGLE=true`!

### Setting up Docker

In order to be able to get containers started, you'll need access to the `docker-compose` command.

First install it using developmental requirements:

```bash
# This assumes your `virtualenv` is on Python 3.x. If not, use the appropriate one.
$ virtualenv accounting
$ . accounting/bin/activate
(accounting) $ pip install -r requirements.txt
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
