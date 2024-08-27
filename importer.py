#!/usr/bin/python3

from modules.indexer import SolrIndexer
from dotenv import load_dotenv
import os
import argparse

def main():
    argParser = argparse.ArgumentParser(description="Solr Indexer Utility")
    argParser.add_argument("-c", "--collection", help="The collection to index", required=True)
    argParser.add_argument("-r", "--reindex", action='store_true', help="Reindex the collection")
    argParser.add_argument("-e", "--empty", action='store_true', help="Empty or Clean the collection")
    argParser.add_argument("-f", "--configfile", help="Custom config file for the collection")

    args = argParser.parse_args()

    # Determine the configuration file path
    if args.configfile:
        configfile = args.configfile
    else:
        configfile = os.path.join(os.path.dirname(__file__), f'.env.{args.collection}')

    if not os.path.exists(configfile):
        print(f'Please add {configfile} file')
        exit()

    # Load the environment variables from the configuration file
    load_dotenv(configfile)

    indexer = SolrIndexer(True)
    indexer.setup(configfile)

    if args.reindex:
        indexer.all()  # Re-upload all documents to solr
    elif args.empty:
        indexer.clean()  # Clean the collection
    else:
        indexer.delta()  # Delta upload of documents to solr

if __name__ == "__main__":
    main()
