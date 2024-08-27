# SOLR data import handler alternative

The objective of this repository is to provide an alternative to now removed data import handler from SOLR-9.x onwards. This repository provides tools to setup periodic updation of data to solr.

Currently, this is in alpha version with only mysql as the data source.


## Installation

Start with installing python dependencies.

```
pip3 install -rU requirements.txt
```

A quick install script is present for installing solr.
To get a complete list of available options, use `--help` argument

```
./solr-installer --help
```

You can now:
1. Install solr (`--install-solr`)
2. Create core (`--create-core`)
3. Initialize the index management and automate via crontab (`--initialize`)


## Import data

You can import data directly as well. Just invoke the importer.py file with necessary arguments.

`-c`,`--collection`: The collection to index
`-r`,`--reindex`: Reindex the collection
`-e`,`--empty`: Empty or Clean the collection
`-f`,`--configfile`: Custom config file for the collection
