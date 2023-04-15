from pysolr import Solr, SolrCoreAdmin
import pymysql
import os
from modules.logger import set_logger
from dotenv import load_dotenv
from pathlib import Path
import json
import datetime, pytz

class SolrIndexer():
    def __init__(self, debug: bool=False, **kwargs):
        super().__init__(**kwargs)
        self.logger = set_logger(self.__class__.__name__, verbose=debug)
        self.availableFormatTypes = ['article', 'word']

    def setup(self, configPath: str):
        if(configPath == ''):
            self.logger.info('No config file path is given.')
            self.logger.info('Please use setupSolr, setupDb, setFullImportQuery and setDeltaImportQuery funnctions.')
            raise Exception
        load_dotenv(dotenv_path=Path(configPath))
        self.setupSolr(
            os.getenv('SOLR_COLLECTION'), 
            os.getenv('SOLR_HOST'),
            os.getenv('SOLR_PORT'),
            int(os.getenv('SOLR_IMPORT_BATCHSIZE')),
            int(os.getenv('SOLR_SHARDS'))
        )
        self.setupDb(
            os.getenv('MYSQL_HOST'),
            os.getenv('MYSQL_USER'),
            os.getenv('MYSQL_PASSWORD'),
            os.getenv('MYSQL_DATABASE')
        )
        self.setFullImportQuery(
            os.getenv('FULL_IMPORT_QUERY'),
            os.getenv('FULL_IMPORT_COUNT_QUERY')
        )
        self.setDeltaImportQuery(
            os.getenv('DELTA_IMPORT_QUERY'),
            os.getenv('DELTA_IMPORT_COUNT_QUERY')
        )
        self.formatType = os.getenv('DATA_FORMAT_TYPE')
        self.deltaFile = os.path.dirname(__file__) + '/../' +'delta.json'
        self.deltaObj = {
            'delta': {
                'last_index_time': '',
                'timezone': os.getenv('DELTA_IMPORT_TIMEZONE')
            }
        }
        self.deltaItemKey = os.getenv('DELTA_IMPORT_QUERY_ITEM_KEY')
        if(self.formatType not in self.availableFormatTypes):
            raise Exception

    def setupSolr(self, collection: str, host: str = 'localhost', port: int = 8983, batchsize: int = 5000, shards: int = 1, **kwargs):
        self.logger.info('Setting up Solr index...')
        self.shards = shards
        self.collection = collection
        self.batchsize = batchsize
        self.solr = Solr("http://{0}:{1}/solr/{2}/".format(host, port, self.collection), timeout=10000)
    
    def setupDb(self, host: str, user: str, password: str, database: str):
        self.db = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def setFullImportQuery(self, query: str, countQuery: str):
        self.fullImportQuery = query
        self.fullImportCountQuery = countQuery

    def setDeltaImportQuery(self, query: str, countQuery: str):
        self.deltaImportQuery = query
        self.deltaImportCountQuery = countQuery

    def format(self, obj: dict):
        """Format a passage for indexing"""
        if(self.formatType == 'article'):
            body = {
                'id': obj['id'],
                'category': obj['category'],
                'createdAt': obj['createdAt'].strftime("%Y-%m-%d %H:%M:%S"),
                'description': obj['eventDescription'],
                'eventDescription': obj['eventDescription'],
                'eventId': obj['eventId'],
                'eventImage': obj['eventImage'],
                'eventName': obj['eventName'],
                'eventSentiment': 0.0,
                'eventTimestamp': obj['eventTimestamp'].strftime("%Y-%m-%d %H:%M:%S"),
                'image': obj['eventImage'],
                'name': obj['name'],
                'timelineId': obj['timelineId'],
                'timestamp': obj['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
                'updatedAt': obj['updatedAt'].strftime("%Y-%m-%d %H:%M:%S"),
                'visibletimestamp': obj['visibletimestamp']
            }

        elif(self.formatType == 'word'):
            body = {
                'id': obj['id'],
                'word': obj['word'],
                'createdAt': obj['created_at'].strftime("%Y-%m-%d %H:%M:%S")
            }

        return body

    def index(self, query, batchStart):
        self.logger.info( 'Indexing {1} data items starting from {0} ...'.format(batchStart, self.batchsize) )
        cursor = self.db.cursor()
        cursor.execute(query + (" limit {0},{1}".format(batchStart, self.batchsize)))
        act = [self.format(row) for row in cursor.fetchall()]
        self.solr.add(act)

    def clean(self):
        self.solr.delete(q='*:*')
        self.solr.optimize()

    def all(self):
        self.clean()
        cursor = self.db.cursor()
        cursor.execute(self.fullImportCountQuery)
        recordCount = cursor.fetchone()
        for start in range(0, recordCount['c'], self.batchsize):
            self.index(self.fullImportQuery, start)
        self.solr.optimize()
        self.logdelta()

    def delta(self):
        self.loaddelta()
        cursor = self.db.cursor()
        cursor.execute(self.deltaImportCountQuery.replace("""{delta.last_index_time}""", self.deltaObj['delta']['last_index_time']))
        for obj in cursor.fetchall():
            self.index(self.deltaImportQuery.replace("""{delta.item}""", str(obj[self.deltaItemKey])), 0)
        self.solr.optimize()
        self.logdelta()

    def logdelta(self):
        self.deltaObj['delta']['last_index_time'] = datetime.datetime.now(pytz.timezone(self.deltaObj['delta']['timezone'])).strftime("%Y-%m-%d %H:%M:%S")
        with open(self.deltaFile, "w") as outfile:
            json.dump(self.deltaObj, outfile)

    def loaddelta(self):
        with open(self.deltaFile, "r") as outfile:
            self.deltaObj = json.load(outfile)
