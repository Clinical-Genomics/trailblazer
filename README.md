# Trailblazer [![Build Status][travis-image]][travis-url] [![Coverage Status][coveralls-image]][coveralls-url]

_Trailblazer_ is a tool to keep track of analyses.

## Background

We are running a pipeline ([MIP][mip]) and needed:

1. a way to overview currently running jobs
2. a way to be notified about failures in an intuitive way
3. a way to track runs of the same samples across time

For this we built a tool that will read information from the file system and determine which state any given analysis run i in (running, completed, failed, etc.). We are also providing a web interface to overview the information and add further annotations.

The tool is also an entry point to manage analyses and e.g. start and restart them in a simple way.

We are currently only focusing on supporting MIP but the plan is to expand to additional pipelines once we take them into production.

## Documentation

A brief documentation of intended usage. You will find some additional features and I will document them as they mature.

### Installation

You can install Trailblazer from source:

```bash
$ git clone https://github.com/Clinical-Genomics/trailblazer && cd trailblazer
$ pip install --editable .
```

If you need to connect to a MySQL database you also need a connector package:

```bash
$ pip install pymysql
```

### Setup

The first thing is setting up a database. It will create the database tables.

```bash
$ trailblazer init sqlite:///path/to/store.sqlite3
```

### Adding new analyses

You can add individual analyses by pointing to the "QC sample info" file or scan for analyses under customer directories. The `scan` command can be run in a crontab e.g. every hour to keep the database up-to-date.

> The web interface will display the date when the database was last updated so you can tell if you are looking at fresh information!

```bash
$ trailblazer add /path/to/familyId_qc_sampleInfo.yaml
$ trailblazer scan /path/to/cust003
```

The tool will pick up in what state an analysis is in:

1. if an analysis is currently running
2. if a run has failed and will then report which step FIRST was not successful
3. if a run is complete and will then calculate the runtime

Whenever a run updates from "running" to either "completed" or "failed", the previous entry for the "running" analysis will be deleted. This is also why in the web interface you are not allowed to change anything about these entries since this information would be lost once the analysis ends.

### Running analyses

Trailblazer simplifies starting a new analysis. When a run has started it is tracked in the database with a "pending" status tag until the first Sacct output is generated.

```bash
trailblazer analyze start [customer] [family]
```

The command will pick up email from the environment if you have have sudo:ed to "hiseq.clinical" from your user. It will determine the correct cluster constant path automatically. It can guess the analysis type based on existing folder structure.

> Before starting a run you need to generate a pedigree or YAML pedigree and place it in the correct location! 

### Web interface

The web interface is a simple Flask app that can be run locally or deployed to the cloud. We provide some of the necessary settings in the repository to deploy it to AWS Elastic Beanstalk.

#### Starting it up

Since we are talking about a simple service I would use the built-in `flask` CLI to run the server locally for development and production:

```bash
$ FLASK_APP=trailblazer.server.app SQLALCHEMY_DATABASE_URI=<DATABASE URI> FLASK_DEBUG=1 flask run
```

This command will start the development server on port 5000. By adding the option `--host 0.0.0.0` you will expose the server to the network.

#### Description

From the web interface you can interact with the data in several ways. First you get an overview of analysis that are grouped by their status. You can then make comments on runs that have failed or completed. When you make a comment on a failed run it will be hidden from the overview dashboard.

You can also manually edit the status for runs. Say e.g. that you decide that you started an analysis with the wrong input and it completed; you can then manually set the status to "error" and it will no longer be treated as a successful run.

An exhaustive list of all runs is available as well. This view let's just search for analyses and see everything which has been added to the database.


[travis-url]: https://travis-ci.org/Clinical-Genomics/trailblazer
[travis-image]: https://img.shields.io/travis/Clinical-Genomics/trailblazer.svg?style=flat-square

[coveralls-url]: https://coveralls.io/r/Clinical-Genomics/trailblazer
[coveralls-image]: https://img.shields.io/coveralls/Clinical-Genomics/trailblazer.svg?style=flat-square

[mip]: https://github.com/henrikstranneheim/MIP
