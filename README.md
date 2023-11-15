# Trailblazer [![Coverage Status][coveralls-image]][coveralls-url]

### Monitor the progress of analysis workflows submitted to SLURM

Trailblazer is a tool that aims to provide:
- Monitoring of processes that require submission to a workflow manager
- Display metadata for each analysis within a web based user interface

[Here][Trailblazer-UI] you can find a simple web UI for Trailblazer that helps you keep track of the status of multiple runs

## Installation

Trailblazer is written in Python 3.11 and is available on the [Python Package Index][pypi] (PyPI).

```bash
pip install trailblazer
```

If you would like to install the latest development version:

```bash
git clone https://github.com/Clinical-Genomics/trailblazer
cd trailblazer
pip install --editable .
```

With each push to GitHub your files will be automatically verified using [Black] . If you would like to automatically [Black] format your commits on your local machine:

```
pre-commit install
```

## Contributing

Trailblazer uses the GitHub flow branching model as described in Atlas [GitHub Flow].

## Documentation

Here's a brief documentation. Trailblazer functionality can be accessed from the command line interface (CLI), the monitoring web interface, the supporting REST API, as well as using the Python API.

### Command line interface

#### Command: `trailblazer init`

Setup (or reset) a Trailblazer database. The command will set up all the tables in the database. You can reset an existing database by using the `--reset` option.

```shell
trailblazer --database "sqlite:///tb.sqlite3" init --reset
Delete existing tables? [analysis, info, job, user] [y/N]: y
Success! New tables: analysis, info, job, user
```

#### Command: `trailblazer user`

This command can be used both to add a new user to the database (and give them access to the web interface) and view information about an existing user.

```shell
# add a new user
trailblazer user --name "Paul Anderson" paul.anderson@magnolia.com
New user added: paul.anderson@magnolia.com (2)

# check an existing user
trailblazer user paul.anderson@magnolia.com
{'created_at': datetime.datetime(2017, 6, 22, 8, 49, 44, 685977), 'google_id': None, 'name': 'Paul Anderson', 'email': 'paul.anderson@magnolia.com', 'avatar': None, 'id': 2}
```

#### Command: `trailblazer archive-user`

This command archives a user in the database (and removes their access to the web interface).

```shell
# archive a user
trailblazer archive-user paul.anderson@magnolia.com
User archived: paul.anderson@magnolia.com
```

#### Command: `trailblazer users`

This command can be used both to list all users in the database and get a filtered list of users.

```shell
# list all users
trailblazer users
Listing users in database:
{'created_at': datetime.datetime(2017, 6, 22, 8, 49, 44, 685977), 'google_id': None, 'name': 'Paul Anderson', 'email': 'paul.anderson@magnolia.com', 'avatar': None, 'id': 2}

# list all users named 'Anderson' that has an email with 'magnolia' in it
trailblazer users --name Anderson --email magnolia
Listing users in database:
{'created_at': datetime.datetime(2017, 6, 22, 8, 49, 44, 685977), 'google_id': None, 'name': 'Paul Anderson', 'email': 'paul.anderson@magnolia.com', 'avatar': None, 'id': 2}
```


#### Command: `trailblazer log`

Logs the status of a run to the supporting database. You need to point to the analysis config of a specific run.

```shell
trailblazer log path/to/case/analysis/case_config.yaml
```

You can point to the same analysis multiple times, Trailblazer will detect if the same analysis has been added before and skip it if no information has been updated. If an analysis has been added previously as "running" or "pending", those entries will automatically be removed as soon as the same analysis is logged as either "completed" or "failed".

#### Command: `trailblazer scan`

Convenience command to scan an entire directory structure for all analyses and update their status in one go. Assumes the base directory consists of individual case folders:

```shell
trailblazer scan /path/to/analyses/dir/
```

This command can easily be setup in a crontab to run e.g. every hour and keep the analysis statuses up-to-date!

#### Command: `trailblazer ls`

Prints the case id for the most recently completed analyses to the console.

```shell
trailblazer ls
F0013487
F0013362
F0006106
17083
F0013469
17085
```

#### Command: `trailblazer delete`

Deletes an analysis log from the database. The input is the unique analysis id which is printed ones the analysis is initially logged. It's also displayed in the web interface.

```shell
trailblazer delete 4
```

[black]: https://black.readthedocs.io/en/stable/
[coveralls-url]: https://coveralls.io/r/Clinical-Genomics/trailblazer
[coveralls-image]: https://img.shields.io/coveralls/Clinical-Genomics/trailblazer.svg?style=flat-square
[GitHub Flow]: https://atlas.scilifelab.se/infrastructure/github/branching_models/githubflow/
[pypi]: https://pypi.python.org/pypi/trailblazer/
[Trailblazer-UI]: https://github.com/Clinical-Genomics/trailblazer-ui
