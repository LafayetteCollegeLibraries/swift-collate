#!/usr/bin/env python

import os.path
import string
import re
import subprocess
import os
import time
import importlib
import ConfigParser
import fnmatch
import pickle
import logging
import signal
import json

import networkx as nx
from lxml import etree

import tornado.ioloop
import tornado.web
import tornado.escape
import tornado.httpserver
import tornado.websocket
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from tornado import gen, queues
from tornado.options import define, options, parse_command_line

from pymongo import MongoClient
from bson.binary import Binary

from SwiftDiff import TextToken
from SwiftDiff.text import Line, Text
from SwiftDiff.collate import DifferenceText, Collation
from SwiftDiff.tokenize import Tokenizer, SwiftSentenceTokenizer

MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 3

# Retrieve the configuration settings
config = ConfigParser.RawConfigParser()
config.read( os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'swift_collate.cfg')  )

# Work-around for multiprocessing within Tornado
max_workers = config.getint('server', 'max_workers')
pool = ProcessPoolExecutor(max_workers=max_workers)

# Retrieve the cache configuration
host = config.get('MongoDB', 'host')
port = config.getint('MongoDB', 'port')
client = MongoClient(host, port)
db_name = config.get('MongoDB', 'db_name')

# Retrieve the server configuration
tei_dir_path = config.get('server', 'tei_dir_path')

# Set the global variables for the server
define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")
define("processes", default=max_workers, help="concurrency")
define("cache", default=True, help="caching", type=bool)

class FootnotesModule(tornado.web.UIModule):

    # @todo Refactor using MV* architecture
    def render(self, index, footnotes):

        return self.render_string("footnotes.html", index=index, footnotes=footnotes)

class LineModule(tornado.web.UIModule):

    # @todo Refactor using MV* architecture
    def render(self, line):

        line_classes = line.classes
        classes = string.join(line_classes + ['line']) if line_classes else 'line'

        distance = line.distance

        # Add the class unique to the edit distance for the line
        classes += ' line-distance-' + str(distance)

        # Add the appropriate gradient class
        gradient_class = 'gradient-'

        if distance == 0:

            gradient_class += 'none'
        elif distance is None or distance >= 5:

            gradient_class += 'severe'
        else:

            gradient_class += ['mild', 'moderate', 'warm', 'hot'][distance - 1]
        classes += ' ' + gradient_class

        line_value = line.base_line.value.encode('utf-8')

        return self.render_string("line.html", line=line_value, classes=classes)

class TokenModule(tornado.web.UIModule):

    # @todo Refactor using MV* architecture
    def render(self, token):

        token_classes = token.classes
        classes = string.join(token_classes + ['token']) if token_classes else 'token'

        distance = token.distance

        # Add the class unique to the edit distance for the token
        classes += ' token-distance-' + str(distance)

        # Add the appropriate gradient class
        gradient_class = 'gradient-'

        if distance == 0:

            gradient_class += 'none'
        elif distance is None or distance >= 5:

            gradient_class += 'severe'
        else:

            gradient_class += ['mild', 'moderate', 'warm', 'hot'][distance - 1]
        classes += ' ' + gradient_class

        token_value = token.value

        # Refactor
        for element_name, element_attr_items in token.markup.iteritems():

            element = etree.fromstring('<' + element_name + ' />')
            element.text = token.value

            for attr_name, attr_value in element_attr_items.iteritems():
            
                element.set(attr_name, attr_value)

            token_value = etree.tostring(element)
            
        return self.render_string("token.html", token=token_value, classes=classes)

def cache(collection_name, key, value=None):
    """Retrieves, creates, or updates a cached data structure into the cache store

    :param collection_name: The name of the MongoDB collection
    :type collection_name: str

    :param key: The key for the Object

    :param value: The data structure for insert and update operations
    """

    db = client[db_name]
    collection = db[collection_name]

    if value is None:
        doc = collection.find_one(key)
        if doc is None:
            return None
        cached = pickle.loads(doc['data'])
    else:
        cached = pickle.dumps(value)

        data = key.copy()
        data.update({'data': Binary(cached)})

        collection.find_one_and_replace(key, data, upsert=True)

    return cached

def compare(_args, update=False):
    """Compares two <tei:text> Element trees

    :param _args: The arguments passed (within the context of invocation using a ProcessPoolExecutor instance)
    :type _args: tuple
    """

    base_text = _args[0]
    other_text = _args[1]

    # Attempt to retrieve the results from the cache
    # doc = cache_db['diff_texts'].find_one({'uri': uri})
    
    diff = DifferenceText(base_text, other_text, SwiftSentenceTokenizer)
    
    return diff

def collate_async(executor, base_text, witness_texts, poem_id, base_id):
    """Collates a set of texts asynchronously

    :param executor: 
    :type executor: 
    """

    key = {'base_text': base_id}

    # Attempt to retrieve this from the cache
#    doc = cache('collation_cache', key)
#    if doc is None:
    if True:
        # Collate the witnesses in parallel
        diff_args = map( lambda witness_text: (base_text, witness_text), witness_texts )
        diffs = executor.map( compare, diff_args )

        # tei_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xml', poem_id)
        
        result = Collation(base_text, diffs, tei_dir_path)
        cache('collation_cache', key, result)

    else:
        result = doc

    return result


def resolve(uri, update=False):
    """Resolves resources given a URI
    
    :param uri: The URL or URI for a file-system-based resource.
    :type uri: str.
    :param update: Should the cache be repopulated?
    :type uri: bool.
    :returns:  etree._Element -- the <tei:text> Element.

    """

    # Check the cache only if this is *NOT* a file-system resource
    if re.match(r'^file\:\/\/', uri):

        return Tokenizer.parse_text(uri)

#    doc = cache_db['texts'].find_one({'uri': uri})

#    if not update and doc:
    if False:

        result = etree.xml(doc['text'])
    else:
    
        # Otherwise, a web request may be issued for the resource
        result = Tokenizer.parse_text(uri)
        
        # Cache the resource
#        cache_db['texts'].replace_one({'uri': uri}, {'text': etree.tostring(result)}, upsert=True)

#    return result
    return Tokenizer.parse_text(uri)

def poem_ids():
    """Retrieve the ID's for poems within any given collection

    """

    poem_dir_paths = []

    for f in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xml')):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xml', f)
        if os.path.isdir(path) and len(f) == 3 and f[0] != '.':

            poem_dir_paths.append(f)

    return poem_dir_paths

def doc_uris(poem_id, transcript_ids = []):
    """Retrieve the transcript file URI's for any given poem

    :param poem_id: The ID for the poem.
    :type poem_id: str.

    :param transcript_ids: The ID's for the transcript documents.
    :type transcript_ids: list.
    """

    # Initialize for only the requested transcripts
    if len(transcript_ids) > 0:
        transcript_paths = [None] * len(transcript_ids)
    else:
        transcript_paths = []

    for f in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xml', poem_id + '/')):

        if fnmatch.fnmatch(f, '*.tei.xml') and f[0] != '.':
            # Filter and sort for only the requested transcripts
            if len(transcript_ids) > 0:
                path = re.sub(r'\.tei\.xml$', '', f)
                if path in transcript_ids:
                    i = transcript_ids.index( path )
                    transcript_paths[i] = f
            else:
                transcript_paths.append(f)

    # Provide a default ordering for the transcripts
    if len(transcript_ids) == 0:

        transcript_paths.sort()

    uris = map(lambda path: os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xml', poem_id + '/', path), transcript_paths)
    return uris

class StreamHandler(tornado.websocket.WebSocketHandler):

    executor = None # Work-around

    # Here, the polling takes place between the thread and server
    def open(self):
        pass

    def on_message(self, message):

        # Condition on the message sent

        # The request
        
        # 1. Request the document set, parse each document
        # Return the message "Retrieving the documents"

        # 2. Retrieve the titles
        # Return the message "Collating the titles"
        # Iterate

        # Render a set of collated titles
        # Iterate

        # Tokenize for two lines
        
        ####
        # @todo Refactor and abstract
        tokenizer_name = 'PunktWordTokenizer'

        # Parse the arguments from the message
        request = json.loads(message)
        poem_id = request['poem']
        base_texts = request['baseText']
        transcript_ids = request['variants'].keys()

        try:
            base_id = base_texts.keys().pop()
        except:
            raise "Could not identify the base text for the collation"

        self.write_message("Loading the Documents...")

        # Retrieve the URI's and docs for the variants
        uris = doc_uris(poem_id, transcript_ids)

        # Retrieve the URI and doc for the base text
        base_uris = doc_uris(poem_id, [base_id])

        self.write_message("Parsing the Documents...")

        base_docs = map(resolve, base_uris)
        base_ids = map(lambda path: path.split('/')[-1].split('.')[0], base_uris)
        base_doc = base_docs.pop()
        base_id = base_ids.pop()

        # Structure the base and witness values
        base_values = { 'node': base_doc, 'id': base_id }

        ids = map(lambda path: path.split('/')[-1].split('.')[0], uris)
        docs = map(resolve, uris)

        variant_texts = []
        for node, witness_id in zip(docs, ids):

            # Ensure that Nodes which could not be parsed are logged as server errors
            # Resolves SPP-529
            if node is not None:
                witness_values = { 'node': node, 'id': witness_id }
                variant_texts.append( witness_values )
            else:
                logging.warn("Failed to parse the XML for the transcript %s", witness_id)

        self.write_message("Tokenizing the Documents...")

        # Retrieve the base Text
        base_text = Text(base_doc, base_id, SwiftSentenceTokenizer)
        base_text.tokenize()

        # Retrieve the variant Texts
        witness_texts = map(lambda witness: Text(witness['node'], witness['id'], SwiftSentenceTokenizer), variant_texts)

        self.write_message("Collating the Documents...")

        collation = collate_async(self.executor, base_text, witness_texts, poem_id, base_id)

        # Collate the witnesses in parallel
#        diff_args = map( lambda witness_text: (base_text, witness_text), witness_texts )
#        diffs = self.executor.map( compare, diff_args )

#        tei_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xml', poem_id)
#        collation = Collation(base_text, diffs, tei_dir_path)

        self.write_message(self.render_string("collate.html", collation=collation))

    def on_close(self):
        pass

class TranscriptsHandler(tornado.web.StaticFileHandler):
    """The request handler for collation operations

    """

    def get(self, transcript_id):

        uri = ''

        for dirName, subdirList, fileList in os.walk(self.root):

            for f in fileList:
                if fnmatch.fnmatch(f, transcript_id + '.tei.xml'):
                    uri = f
                    uri = os.path.join(dirName, uri)

        super(TranscriptsHandler, self).get(uri)

class CollateHandler(tornado.web.RequestHandler):
    """The request handler for collation operations

    """
    
    executor = None # Work-around

    @gen.coroutine
    def post(self, poem_id = '425'):
        """The POST request handler for collation
        
        Args:
           poem_id (string):   The identifier for the poem itself
           
           base_id (string):   The identifier for the poem used as a base during the collation

        """

        # @todo Refactor and abstract
        tokenizer_name = 'PunktWordTokenizer'
        transcript_ids = self.get_body_arguments("variants")
        base_id = self.get_body_argument("base_text")

        # Retrieve the URI's and docs for the variants
        uris = doc_uris(poem_id, transcript_ids)

        # Retrieve the URI and doc for the base text
        base_uris = doc_uris(poem_id, [base_id])
        base_docs = map(resolve, base_uris)
        base_ids = map(lambda path: path.split('/')[-1].split('.')[0], base_uris)
        base_doc = base_docs.pop()
        base_id = base_ids.pop()

        # Structure the base and witness values
        base_values = { 'node': base_doc, 'id': base_id }

        ids = map(lambda path: path.split('/')[-1].split('.')[0], uris)
        docs = map(resolve, uris)

        variant_texts = []
        for node, witness_id in zip(docs, ids):

            # Ensure that Nodes which could not be parsed are logged as server errors
            # Resolves SPP-529
            if node is not None:
                witness_values = { 'node': node, 'id': witness_id }
                variant_texts.append( witness_values )
            else:
                logging.warn("Failed to parse the XML for the transcript %s", witness_id)

        # Retrieve the base Text
        base_text = Text(base_doc, base_id, SwiftSentenceTokenizer)
        base_text.tokenize()

        # Retrieve the variant Texts
        witness_texts = map(lambda witness: Text(witness['node'], witness['id'], SwiftSentenceTokenizer), variant_texts)

        collation = collate_async(self.executor, base_text, witness_texts, poem_id, base_id)

        # Collate the witnesses in parallel
#        diff_args = map( lambda witness_text: (base_text, witness_text), witness_texts )
#        diffs = self.executor.map( compare, diff_args )

#        tei_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xml', poem_id)
#        collation = Collation(base_text, diffs, tei_dir_path)

        self.render("collate.html", collation=collation)

    @gen.coroutine
    def get(self, poem_id = '425', base_id = '425-001B'):
        """The GET request handler for collation
        
        Args:
           poem_id (string):   The identifier for the poem itself
           
           base_id (string):   The identifier for the poem used as a base during the collation
           
        """

        # @todo Refactor and abstract
        tokenizer_name = 'PunktWordTokenizer'

        uris = doc_uris(poem_id)
        ids = map(lambda path: path.split('/')[-1].split('.')[0], uris)
        ids = ids[1:]

        poem_file_paths = {
            poem_id: { 'uris': uris, 'ids': ids },
        }

        uris = poem_file_paths[poem_id]['uris']
        ids = poem_file_paths[poem_id]['ids']

        # Retrieve the stanzas
        texts = map(resolve, uris)

        # Set the base text
        base_text = texts[0]
        texts = texts[1:]

        # Structure the base and witness values
        base_values = { 'node': base_text, 'id': base_id }

        witnesses = []
        for node, witness_id in zip(texts, ids):

            # Ensure that Nodes which could not be parsed are logged as server errors
            # Resolves SPP-529
            if node is not None:
                witness_values = { 'node': node, 'id': witness_id }
                witnesses.append( witness_values )

        # Select the tokenizer
        # tokenizer = StanfordTokenizer

        # load the module, will raise ImportError if module cannot be loaded
        m = importlib.import_module('nltk.tokenize.treebank')
        # get the class, will raise AttributeError if class cannot be found
        tokenizer = getattr(m, 'TreebankWordTokenizer')

        base_text = Text(base_text, base_id, SwiftSentenceTokenizer)
        base_text.tokenize()

        witness_texts = map(lambda witness: Text(witness['node'], witness['id'], SwiftSentenceTokenizer), witnesses )

        # Collate the witnesses in parallel
        collation = collate_async(self.executor, base_text, witness_texts, poem_id, base_id)

#        diff_args = map( lambda witness_text: (base_text, witness_text), witness_texts )
#        diffs = self.executor.map( compare, diff_args )

#        tei_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xml', poem_id)
#        collation = Collation(base_text, diffs, tei_dir_path)

        self.render("collate.html", collation=collation)

class PoemsIndexHandler(tornado.web.RequestHandler):
    """The request handler for viewing all poems

    """

    def get(self):

        poem_texts = {}

        for poem_id in poem_ids():

            # @todo Refactor and abstract
            # Retrieve the URI's for a given poem
            uris = doc_uris(poem_id)
            ids = map(lambda path: path.split('/')[-1].split('.')[0], uris)
            slugs = map(lambda transcript_id: '/transcripts/' + transcript_id, ids)

            # poem_text = {'ids': ids, 'uris': slugs}
            # poem_texts[poem_id] = poem_text
            poem_texts[poem_id] = ids

        self.render("poems.html", poem_texts=poem_texts)

    def get_broken(self):

        # poem_texts = []
        poem_texts = {}

        for poem_id in poem_ids():

            # @todo Refactor and abstract
            uris = doc_uris(poem_id)
            ids = map(lambda path: path.split('/')[-1].split('.')[0], uris)
            
            poem_file_paths = {
                poem_id: { 'uris': uris, 'ids': ids },
            }

            uris = poem_file_paths[poem_id]['uris']
            ids = poem_file_paths[poem_id]['ids']

            # Retrieve the stanzas
            poem_docs = map(resolve, uris)

            witnesses = []
            for node, witness_id in zip(poem_docs, ids):
                if node is not None:
                    witness_values = { 'node': node, 'id': witness_id }
                    witnesses.append( witness_values )

            # Construct the poem objects
            # poem_texts.extend(map(lambda poem_text: Text(poem_text['node'], poem_text['id'], SwiftSentenceTokenizer), witnesses))
            try:
                # poem_texts[poem_id] = map(lambda poem_text: Text(poem_text['node'], poem_text['id'], SwiftSentenceTokenizer), witnesses)
                poem_texts[poem_id] = map(lambda poem_text: poem_text['id'], witnesses)
            except:
                pass

        self.render("poems.html", poem_id=poem_id, poem_texts=poem_texts)

class PoemsIndexHandlerDepr(tornado.web.RequestHandler):
    """The request handler for viewing all poems

    """

    def get(self):

        poem_texts = {}

        for poem_id in poem_ids():

            # @todo Refactor and abstract
            # Retrieve the URI's for a given poem
            uris = doc_uris(poem_id)
            ids = map(lambda path: path.split('/')[-1].split('.')[0], uris)
            slugs = map(lambda transcript_id: '/transcripts/' + transcript_id, ids)

            # diff_line.uri = '/transcripts/' + self.transcript_path(diff.other_text.id)

            poem_text = {'ids': ids, 'uris': slugs}
            poem_texts[poem_id] = poem_text

        self.render("poems.html", poem_texts=poem_texts)

class PoemsHandler(tornado.web.RequestHandler):
    """The request handler for viewing poem variants

    """

    executor = None # Work-around

    @gen.coroutine
    def get(self, poem_id):
        """The GET request handler for poems
        
        Args:
           poem_id (string):   The identifier for the poem set

        """

        poem_texts = []

        # @todo Refactor and abstract
        uris = doc_uris(poem_id)
        ids = map(lambda path: path.split('/')[-1].split('.')[0], uris)
            
        poem_file_paths = {
            poem_id: { 'uris': uris, 'ids': ids },
        }

        uris = poem_file_paths[poem_id]['uris']
        ids = poem_file_paths[poem_id]['ids']

        # Retrieve the stanzas
        poem_docs = map(resolve, uris)

        witnesses = []
        for node, witness_id in zip(poem_docs, ids):
            if node is not None:
                witness_values = { 'node': node, 'id': witness_id }
                witnesses.append( witness_values )

        # Construct the poem objects
        poem_texts.extend(map(lambda poem_text: Text(poem_text['node'], poem_text['id'], SwiftSentenceTokenizer), witnesses))

        self.render("poem.html", poem_id=poem_id, poem_texts=poem_texts)

class SearchHandler(tornado.web.RequestHandler):
    """The request handler for searching for poems

    """

    def get(self):
        query = self.get_argument("q", "")

        poems = poem_ids()
        poems = map(lambda poem: poem + '-', poems)

        items = filter(lambda poem: re.search('^' + query, poem), poems)

        self.write(tornado.escape.json_encode({'items': items }))

class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html")

# Please see https://gist.github.com/mywaiting/4643396
def sig_handler(sig, frame):
    logging.warning('Caught signal: %s', sig)
    tornado.ioloop.IOLoop.instance().add_callback(shutdown)

def shutdown():
    logging.info('Stopping http server')
    server.stop()

    logging.info('Will shutdown in %s seconds ...', MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
    io_loop = tornado.ioloop.IOLoop.instance()

    deadline = time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN

    def stop_loop():
        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
            logging.info('Shutdown')
    stop_loop()

def main():

    # tei_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xml')

    parse_command_line()
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/search/poems/?", SearchHandler),
#            (r"/auth/login", AuthLoginHandler),
#            (r"/auth/logout", AuthLogoutHandler),
            (r"/stream/?", StreamHandler),
#            (r"/collate/(.+?)/(.+)", CollateHandler),
            (r"/collate/([^/]*)/([^/]*)/?", CollateHandler),
            (r"/collate/([^/]*)/?", CollateHandler),
            (r"/poems/([^/]+)/?", PoemsHandler),
            (r"/poems/?", PoemsIndexHandler),
            (r"/transcripts/([^/]+)/?", TranscriptsHandler, { 'path': tei_dir_path }),
        ],
        cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        login_url="/auth/login",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
#        static_url_prefix="/collate/static/",
        xsrf_cookies=False, # @todo Enable
        debug=options.debug,
        ui_modules={ "Token": TokenModule, "Line": LineModule, "Footnotes": FootnotesModule },
        )

    # https://gist.github.com/mywaiting/4643396
    global server
    server = tornado.httpserver.HTTPServer(app)
    server.bind(options.port)
    server.start(max_workers)

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    StreamHandler.executor = ProcessPoolExecutor(max_workers=max_workers)
    CollateHandler.executor = ProcessPoolExecutor(max_workers=max_workers)
    ioloop = tornado.ioloop.IOLoop.current().start()
    # ioloop = tornado.ioloop.IOLoop.instance()
    # executor = Executor()
    # ioloop.add_callback(executor.stemma)
    # ioloop.start(0)

if __name__ == "__main__":
    main()
