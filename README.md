# Trailblazer [![Coverage Status][coveralls-image]][coveralls-url]

### Monitor the progress of analysis workflows submitted to SLURM

Trailblazer is a tool that aims to provide:
- a Python interface to interact with MIP in an automated fashion
- a limited command line interface to simplify running MIP using an opinionated setup

[Here][Trailblazer-UI] you can find a simple web UI for Trailblazer that helps you keep track of the status of multiple runs

### Todo

- [ ] fetch all job ids from sacct status log and offer to kill all jobs
- [ ] display statistics like which steps most analyses fail at

### Roadmap

Trailblazer's scope will be reduced in the next months and will become SLURM+!
Meaning it will become a web UI tool that monitors pipelines to help you keep track of the status of multiple analyses.

We have chosen to have a pipeline export the SLURM job ids in the form of a file:

```
123145
123146
123147
123148
```

The plan is formulated in [issue/39](https://github.com/Clinical-Genomics/trailblazer/issues/39).

## Installation

Trailblazer written in Python 3.6+ and is available on the [Python Package Index][pypi] (PyPI).

```bash
pip install trailblazer
```

If you would like to install the latest development version:

```bash
git clone https://github.com/Clinical-Genomics/trailblazer
cd trailblazer
pip install --editable .
```

Files will be blacked automatically with each push to github. If you would like to automatically [Black][black] format your commits on your local machine:

```
pre-commit install
```

## Contributing

Trailblazer is using github flow branching model as described in our [development manual][development manual].

## Documentation

Here's a brief documentation. Trailblazer functionality can be accessed from the command line interface (CLI), the monitoring web interface, the supporting REST API, as well as using the Python API.

### Command line interface

#### Config file

Trailblazer supports a simple config file written in YAML. You can always provide the same option on the command line, however, it's recommended to store some commonly used values in the config.

The following options are supported:

```yaml
---
database: mysql+pymysql://userName:passWord@domain.com/database
script: /path/to/MIP/mip.pl
mip_config: /path/to/global/MIP_config.yaml
```

> Tip: setup a Bash alias in your `~/.bashrc` to always point to your config automatically:
> ```bash
> alias trailblazer="trailblazer --config /path/to/trailblazer/config.yaml"

#### Command: `trailblazer init`

Setup (or reset) a Trailblazer database. It will simply setup all the tables in the database. You can reset an existing database by using the `--reset` option.

```bash
trailblazer --database "sqlite:///tb.sqlite3" init --reset
Delete existing tables? [analysis, info, job, user] [y/N]: y
Success! New tables: analysis, info, job, user
```

#### Command: `trailblazer user`

This command can be used both to add a new user to the database (and give them access to the web interface) and view information about an existing user.

```bash
# add a new user
trailblazer user --name "Paul Anderson" paul.anderson@magnolia.com
New user added: paul.anderson@magnolia.com (2)

# check an existing user
trailblazer user paul.anderson@magnolia.com
{'created_at': datetime.datetime(2017, 6, 22, 8, 49, 44, 685977), 'google_id': None, 'name': 'Paul Anderson', 'email': 'paul.anderson@magnolia.com', 'avatar': None, 'id': 2}
```

#### Command: `trailblazer archive-user`

This command archives a user in the database (and removes their access to the web interface).

```bash
# archive a user
trailblazer archive-user paul.anderson@magnolia.com
User archived: paul.anderson@magnolia.com
```

#### Command: `trailblazer users`

This command can be used both to list all users in the database and get a filtered list of users.

```bash
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

```bash
trailblazer log path/to/family/analysis/family_config.yaml
```

You can point to the same analysis multiple times, Trailblazer will detect if the same analysis has been added before and skip it if no information has been updated. If an analysis has been added previously as "running" or "pending", those entries will automatically be removed as soon as the same analysis is logged as either "completed" or "failed".

Trailblazer will automatically find additional files used for logging the analysis status (`family_qc_sample_info.yaml` (sampleinfo) and `mip.pl_2017-06-17T12:11:42.log.status` (sacct)) unless you explicitly point to them using the `--sampleinfo` and `--sacct` flags. If either of the files are missing, Trailblazer will simply skip adding a status for that analysis.

#### Command: `trailblazer scan`

Convenience command to scan an entire directory structure for all analyses and update their status in one go. Assumes the base directory consists of individual family folders:

```bash
trailblazer scan /path/to/analyses/dir/
```

This command can easily be setup in a crontab to run e.g. every hour and keep the analysis statuses up-to-date!

#### Command: `trailblazer ls`

Prints the family id for the most recently completed analyses to the console. This is useful to tie in downstream tools that might want to do something with the data from completed runs.

```bash
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

```bash
trailblazer delete 4
```

#### Command: `trailblazer start`

Start MIP from Trailblazer. It's only a thin wrapper around the MIP command line. It removes some complexity like having to provide the global MIP config if it is already defined in the Trailblazer config. It also logs a started analysis as "pending" until the first job has been completed and the status can be evaluated (creates the sacct status file).

```
trailblazer start family4 --priority high
```

[black]: https://black.readthedocs.io/en/stable/
[mip]: https://github.com/clinical-genomics/MIP
[pypi]: https://pypi.python.org/pypi/trailblazer/
[Trailblazer-UI]: https://github.com/Clinical-Genomics/trailblazer-ui


[coveralls-url]: https://coveralls.io/r/Clinical-Genomics/trailblazer
[coveralls-image]: https://img.shields.io/coveralls/Clinical-Genomics/trailblazer.svg?style=flat-square
[development manual]: http://www.clinicalgenomics.se/development/dev/githubflow/
