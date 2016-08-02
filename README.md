# Analysis [![Build Status][travis-image]][travis-url] [![Coverage Status][coveralls-image]][coveralls-url]

_Analysis_ is a tool to be used to keep track of analyses.

## Concerns

???

### Setup

The first thing to do is setting up a root folder and database.

```bash
$ housekeeper init /path/to/root
```

The folder can't exist already or the tool will complain. If successful it will put a config file in the root directory. It will store the location of the root folder in the database so the only thing you need to supply is the path to the database.

### Adding new analyses

Housekeeper can store files from completed analyses. Supported pipelines include:

- MIP

```bash
$ housekeeper add mip /path/to/familyId_config.yaml
```

This command will do some pre-processing and collect assets to be linked. In the case of MIP it will pre-calculate the mapping rate since it isn't available in the main QC metrics file.

Housekeeper will use create an analysis id in the format of `[customerId]-[familyId]`.

### Deleting an existing analysis

You can of course delete an analysis you've stored in the database. It will remove the reference to the analysis along with all the links to the assets.

```bash
$ housekeeper delete customer-family
Are you sure? [Y/n]
```

### Getting files

This is where the fun starts! Since we have control over all the assets and how they relate to analyses and samples we can hand back information to you.

Say you wanted to know the path to the raw BCF file for a given analysis. Let's ask Housekeeper!

```bash
$ housekeeper get --analysis customer-family --category bcf-raw
/path/to/root/analyses/customer-family/all.variants.bcf
```

Note that it will print to console without new line so you can just as well do:

```bash
$ ls -l $(housekeeper get --analysis customer-family --category bcf-raw)
-rw-r--r--  2 robinandeer  staff    72K Jul 27 14:33 /path/to/root/analyses/customer-family/all.variants.bcf
```

And if multiple files match the query it will simply print them on one line separated by a single space.

### Archiving an analysis

When you add a new analysis you tell Housekeeper which files are eventually to be archived. We can certainly do a lot more with this functionality but for now what happens when you archive an analysis is:

1. you update the status to "archived"
2. remove all files and references that are not marked as "to_archive"

```bash
$ housekeeper archive customer-family
Are you sure? [Y/n]
```

## API structure and architecture

This section will describe the implementation.

### Store

SQL(ite) database containing references to the analyses and in which state they belong. It should have a straight-forward API to query which analyses have been completed and e.g. which are archived.

### CLI

Likely the main entry point for accessing the API. However, it should to do the least possible. Abstract away anything that isn't directly concerning parsing command line arguments etc. Uses the Click-framework.

### Web interface

Built using the Flask-framework. Barebones. Should provide overviews for analyses in different states. Could additionally provide access to manually archiving/unarchiving analyses.

## File structure

This section describes how analysis output will be stored on the file system level. It's important that this is an implementation detail that won't be exposed to third-party tools.

The goal is to create as structure that is as flat as possible while still maintaining the original file names as far as possible.

```
root/
├── housekeeper.yaml
├── store.sqlite3
└── analyses/
    ├── analysis_1/
    │   ├── alignment.sample_1.bam
    │   ├── variants.vcf
    │   └── traceback.log
    └── analysis_2/
        ├── alignment.sample_1.cram
        ├── alignment.sample_2.cram
        └── variants.vcf
```


[travis-url]: https://travis-ci.org/Clinical-Genomics/analysis
[travis-image]: https://img.shields.io/travis/Clinical-Genomics/analysis.svg?style=flat-square

[coveralls-url]: https://coveralls.io/r/Clinical-Genomics/analysis
[coveralls-image]: https://img.shields.io/coveralls/Clinical-Genomics/analysis.svg?style=flat-square
