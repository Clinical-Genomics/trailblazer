# Trailblazer [![Build Status][travis-image]][travis-url] [![Coverage Status][coveralls-image]][coveralls-url]

_Trailblazer_ is a tool to keep track of analyses.

## Concerns

For now we are only concerned with the MIP pipeline even thought in the future we'd like to support additional tools.

1. keep track of analyses on the cluster and their status
2. return references to analyses to be rerun or processed downstream
3. remove data once it's no longer needed

Future concerns will include **starting up analyses** as well as **automatically restarting** failed ones under certain conditions.

### Setup

The first thing is setting up a database. It will simply setup the tables.

```bash
$ trailblazer init sqlite:///path/to/store.sqlite3
```

### Adding new analyses

You can add individual analyses by pointing to the "qc sample info" file or scan for analyses under customer directories.

```bash
$ trailblazer add /path/to/familyId_qc_sampleInfo.yaml
$ trailblazer scan /path/to/cust003
```

### Deleting an existing analysis

When you are sure you no longer need the analysis output or would like to clean up before a rerun you can remove the reference to said analysis and the actual files.

```bash
$ trailblazer delete [customer]-[family]
Are you sure? [Y/n]
```

## API structure and architecture

This section will describe the implementation.

### Store

SQL(ite) database containing references to the analyses and in which state they belong. It should have a straight-forward API.

### CLI

Likely the main entry point for accessing the API. However, it should to do the least possible. Abstract away anything that isn't directly concerning parsing command line arguments etc. Uses the Click-framework.

### Web interface

Built using the Flask-framework. Barebones. Should provide overviews for analyses in different states.


[travis-url]: https://travis-ci.org/Clinical-Genomics/analysis
[travis-image]: https://img.shields.io/travis/Clinical-Genomics/analysis.svg?style=flat-square

[coveralls-url]: https://coveralls.io/r/Clinical-Genomics/analysis
[coveralls-image]: https://img.shields.io/coveralls/Clinical-Genomics/analysis.svg?style=flat-square
