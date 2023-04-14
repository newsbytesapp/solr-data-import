

from modules.indexer import SolrIndexer
from dotenv import load_dotenv, find_dotenv
import os
import argparse


# if os.path.exists(os.path.dirname(__file__)+'/.env') == False:
# if os.path.exists(find_dotenv()) == False:
# 	print('Please add system .env file')
# 	exit()

# load_dotenv(find_dotenv())

argParser = argparse.ArgumentParser()
argParser.add_argument("-c", "--collection", help="The collection to index")
argParser.add_argument("-r", "--reindex", help="Reindex the collection")
argParser.add_argument("-e", "--empty", help="Empty or Clean the collection")
argParser.add_argument("-f", "--configfile", help="Custom config file for the collection")

args = argParser.parse_args()

configfile = os.path.dirname(__file__)+'/.env.%s' % args.collection
if(args.configfile is not None):
	configfile = args.configfile

if os.path.exists(configfile) == False:
	print('Please add %s file' % configfile)
	exit()

# runconfigs = os.getenv('CONFIGS_TO_RUN').split(',')
indexer = SolrIndexer(True)
indexer.setup(configfile)
indexer.delta()
