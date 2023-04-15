# SOLR data import handler alternative

The objective of this repository is to provide an alternative to now removed data import handler from SOLR-9.x onwards. This repository provides tools to setup periodic updation of data to solr.

Currently, this is in alpha version with only mysql as the data source.

## Installation

A quick install script is present for installing solr which can be invoked as follows:
```
./solr-installer 9.2.0 mycoll1
```

post that create env files and follow instructions