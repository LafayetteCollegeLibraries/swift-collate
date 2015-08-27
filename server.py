
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
from SwiftDiff.tokenizer import Tokenizer, TextToken, Line, Text, DifferenceText, Collation

from tornado.options import define, options, parse_command_line

define("port", default=8080, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")
define("processes", default=6, help="concurrency")

import subprocess
import os
import time
from lxml import etree

import importlib

class LineModule(tornado.web.UIModule):

    # @todo Refactor using MV* architecture
    def render(self, line, index, distance):

        line_classes = Line.classes(line)
        classes = string.join(line_classes + ['line', 'line-' + str(index)]) if line_classes else 'line line-' + str(index)

        # Add the class unique to the edit distance for the line
        classes += ' line-distance-' + str(distance)

        # Add the appropriate gradient class
        gradient_class = 'gradient-'

        if distance == 0:

            gradient_class += 'none'
        elif distance is None or distance >= 8:

            gradient_class += 'severe'
        else:

            gradient_class += ['mild', 'moderate', 'warm', 'hot'][distance / 2]
        classes += ' ' + gradient_class

        line = Line.escape(line)

        return self.render_string("line.html", line=line, classes=classes)

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
        elif distance is None or distance >= 8:

            gradient_class += 'severe'
        else:

            gradient_class += ['mild', 'moderate', 'warm', 'hot'][distance / 2]
        classes += ' ' + gradient_class

        # Refactor
        if token.markup:

            token_value = '<' + token.markup[0] + '>' + token.value + '</' + token.markup[0] + '>'
        else:

            token_value = token.value

        return self.render_string("token.html", token=token_value, classes=classes)

class Executor():

    executor = ThreadPoolExecutor(max_workers=12)

    # Blocking task for the generation of the stemma
    @run_on_executor
    def stemma(self, base_values, witnesses):

        return Tokenizer.stemma(base_values, witnesses)

    # Blocking task for the merging of stemma sub-trees
    @run_on_executor
    def stemma_merge(self, stemma_u, stemma_v):

        return nx.compose(stemma_u, stemma_v)



@gen.coroutine
def async_run(func, *args, **kwargs):
    """ Runs the given function in a subprocess.

    This wraps the given function in a gen.Task and runs it
    in a multiprocessing.Pool. It is meant to be used as a
    Tornado co-routine. Note that if func returns an Exception 
    (or an Exception sub-class), this function will raise the 
    Exception, rather than return it.

    """
    result = yield gen.Task(pool.apply_async, func, args, kwargs)
    if isinstance(result, Exception):
        raise result
    raise Return(result)

# Work-around for multiprocessing within Tornado
pool = ProcessPoolExecutor(max_workers=6)

from pymongo import MongoClient

mongo_host = '139.147.4.144'
mongo_port = 27017

# MongoDB instance
client = MongoClient(mongo_host, mongo_port)

# Retrieve swift database
cache_db = client['swift']

def get_value(value):

    time.sleep(0.5)
    output = os.getpid()
    return str(output)

def tokenize_diff(params):

    base_values = params[0]
    base_values['node'] = etree.XML(base_values['node'])

    witness_values = params[1]
    witness_values['node'] = etree.XML(witness_values['node'])

    # Attempt to retrieve the cached diff tree    
    tree = Tokenizer.diff(base_values['node'], base_values['id'], witness_values['node'], witness_values['id'])

    return tree

def tokenize(params):

    base_values = params[0]
    base_values['node'] = etree.XML(base_values['node'])

    witnesses = params[1]
    witnesses = map(lambda witness_values: { 'node': etree.XML(witness_values['node']), 'id': witness_values['id'] }, witnesses)

    # Iterate for witnesses
    # base_values = params[0]
    # base_values['node'] = etree.parse(base_values['node'])

    stemma = Tokenizer.stemma(base_values, witnesses)
    return stemma

def compare(_args, update=False):
    """Compares two <tei:text> Element trees

    :param _args: The arguments passed (within the context of invocation using a ProcessPoolExecutor instance)
    :type _args: tuple
    """

    base_text = _args[0]
    other_text = _args[1]

    # Attempt to retrieve the results from the cache
    # doc = cache_db['diff_texts'].find_one({'uri': uri})
    
    diff = DifferenceText(base_text, other_text)
    
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

    doc = cache_db['texts'].find_one({'uri': uri})

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

import fnmatch
import os

def poems(poem_id):
    """Retrieve the paths for poems within any given collection

    :param poem_id: The ID for the set of related poems (apparatus?).
    :type poem_id: str.
    """

    paths = []
    
    for f in os.listdir( os.path.dirname(os.path.abspath(__file__)) + '/tests/fixtures/' + poem_id + '/' ):

        if fnmatch.fnmatch(f, '*.tei.xml') and f[0] != '.':

            paths.append(f)

    uris = map(lambda path: os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests/fixtures/' + poem_id + '/', path), paths)
    return uris

class CollateHandler(tornado.web.RequestHandler):
    """The request handler for collation operations

    """
    
    executor = None # Work-around

    @gen.coroutine
    def get(self, apparatus = '444', base_id = '444-0201', tokenizer_name = 'PunktWordTokenizer'):
        """The GET request handler for collation
        
        Args:
           apparatus (string):   The identifier for the poem itself
           
           base_id (string):   The identifier for the poem used as a base during the collation
           
        """

        # @todo Refactor and abstract
        uris = poems(apparatus)

        ids = map(lambda path: path.split('/')[-1].split('.')[0], uris)
        ids = ids[1:]

        apparatus_file_paths = {
            apparatus: { 'uris': uris, 'ids': ids },
            }

        uris = apparatus_file_paths[apparatus]['uris']
        ids = apparatus_file_paths[apparatus]['ids']

        # Retrieve the stanzas
        texts = map(resolve, uris)

        # Set the base text
        base_text = texts[0]
        texts = texts[1:]

        # Structure the base and witness values
        base_values = { 'node': base_text, 'id': base_id }

        witnesses = []
        for node, witness_id in zip(texts, ids):

            witness_values = { 'node': node, 'id': witness_id }
            witnesses.append( witness_values )

        # Select the tokenizer
        # tokenizer = StanfordTokenizer

        # load the module, will raise ImportError if module cannot be loaded
        m = importlib.import_module('nltk.tokenize.treebank')
        # get the class, will raise AttributeError if class cannot be found
        tokenizer = getattr(m, 'TreebankWordTokenizer')

        base_text = Text(base_text, base_id)
        base_text.tokenize()

        witness_texts = map(lambda witness: Text(witness['node'], witness['id']), witnesses )

        # diffs = map(lambda witness_text: DifferenceText(base_text, witness_text), witness_texts )

        # Collate the witnesses in parallel
        diff_args = map( lambda witness_text: (base_text, witness_text), witness_texts )
        diffs = self.executor.map( compare, diff_args )

        collation = Collation(base_text, diffs)

        #         self.write("trace2")
        self.render("collate.html", collation=collation)

class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html")

def main():
    parse_command_line()
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
#            (r"/auth/login", AuthLoginHandler),
#            (r"/auth/logout", AuthLogoutHandler),
#            (r"/collate/(.+?)/(.+)", CollateHandler),
            (r"/collate/([^/]*)/([^/]*)/?", CollateHandler),
        ],
        cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        login_url="/auth/login",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
#        static_url_prefix="static/",
        xsrf_cookies=False, # @todo Enable
        debug=options.debug,
        ui_modules={ "Token": TokenModule, "Line": LineModule },
        )
    # app.listen(options.port)
    server = tornado.httpserver.HTTPServer(app)
    server.bind(options.port)
    server.start(0)
    CollateHandler.executor = ProcessPoolExecutor(max_workers=6)
    ioloop = tornado.ioloop.IOLoop.current().start()
    # ioloop = tornado.ioloop.IOLoop.instance()
    # executor = Executor()
    # ioloop.add_callback(executor.stemma)
    # ioloop.start(0)

if __name__ == "__main__":

    main()
