
import os.path
import string

import tornado.ioloop
import tornado.web
import tornado.escape
import tornado.httpserver
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from tornado import gen, queues

import networkx as nx
import re

# from SwiftDiff.collation import Collation
# from SwiftDiff import TextToken, Line, Text, DifferenceText, Collation
# from SwiftDiff.tokenizer import Tokenizer
from SwiftDiff import TextToken
from SwiftDiff.text import Line, Text
from SwiftDiff.collate import DifferenceText, Collation
from SwiftDiff.tokenize import Tokenizer, SwiftSentenceTokenizer

from tornado.options import define, options, parse_command_line

MAX_WORKERS=18

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")
define("processes", default=MAX_WORKERS, help="concurrency")

import subprocess
import os
import time
from lxml import etree

import importlib

from pymongo import MongoClient
from bson.binary import Binary
import ConfigParser
import fnmatch
import pickle

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

        line_value = line.other_line.value.encode('utf-8')

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

# Work-around for multiprocessing within Tornado
pool = ProcessPoolExecutor(max_workers=MAX_WORKERS)

# Retrieve the database
config = ConfigParser.RawConfigParser()
config.read( os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'swift_collate.cfg')  )
    
host = config.get('MongoDB', 'host')
port = config.getint('MongoDB', 'port')
client = MongoClient(host, port)

def cache(collection_name, key, value=None):

    db = client['swift_collate']
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

def collate_async(executor, base_text, witness_texts, poem_id, base_id):
    """Collates a set of texts asynchronously

    :param executor: 
    :type executor: 
    """

    key = {'base_text': base_id}

    # Attempt to retrieve this from the cache
    doc = cache('collation_cache', key)
    if doc is None:
        # Collate the witnesses in parallel
        diff_args = map( lambda witness_text: (base_text, witness_text), witness_texts )
        diffs = executor.map( compare, diff_args )

        tei_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xml', poem_id)
        result = Collation(base_text, diffs, tei_dir_path)
        cache('collation_cache', key, result)

    else:
        result = doc

    return result

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

class TranscriptsHandler(tornado.web.StaticFileHandler):
    """The request handler for collation operations

    """

    def get(self, transcript_id):

        uri = ''

        for dirName, subdirList, fileList in os.walk(self.root):
            for f in fileList:
                if fnmatch.fnmatch(f, transcript_id):

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
                print "Failed to parse the XML for %s" % witness_id

        # Retrieve the base Text
        base_text = Text(base_doc, base_id, SwiftSentenceTokenizer)
        base_text.tokenize()

        # Retrieve the variant Texts
        witness_texts = map(lambda witness: Text(witness['node'], witness['id'], SwiftSentenceTokenizer), variant_texts )

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
            uris = doc_uris(poem_id)
            ids = map(lambda path: path.split('/')[-1].split('.')[0], uris)

            poem_texts[poem_id] = ids

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

class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html")

def main():

    tei_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xml')

    parse_command_line()
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
#            (r"/auth/login", AuthLoginHandler),
#            (r"/auth/logout", AuthLogoutHandler),
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
#        static_url_prefix="static/",
        xsrf_cookies=False, # @todo Enable
        debug=options.debug,
        ui_modules={ "Token": TokenModule, "Line": LineModule, "Footnotes": FootnotesModule },
        )
    # app.listen(options.port)
    server = tornado.httpserver.HTTPServer(app)
    server.bind(options.port)
    server.start(MAX_WORKERS)
    CollateHandler.executor = ProcessPoolExecutor(max_workers=MAX_WORKERS)
    ioloop = tornado.ioloop.IOLoop.current().start()
    # ioloop = tornado.ioloop.IOLoop.instance()
    # executor = Executor()
    # ioloop.add_callback(executor.stemma)
    # ioloop.start(0)

if __name__ == "__main__":

    main()
