
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
    def render(self, token, index, distance):

        token_classes = TextToken.classes(token)
        classes = string.join(token_classes + ['token', 'token-' + str(index)]) if token_classes else 'token token-' + str(index)

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

        token = TextToken.escape(token)

        return self.render_string("token.html", token=token, classes=classes)

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

# from pymongo import MongoClient

# mongo_host = 'localhost'
# mongo_port = 27017

# MongoDB cache collection
# client = MongoClient(mongo_host, mongo_port)

# Retrieve Cache collection
# cache_db = client['swift']

# Retrieve Cache collection
# cache = cache_db['diff']

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

class OldCollateHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def post(self):

        # Work-around (given that Tornado does not parse the POST parameters)
        params = tornado.escape.json_decode(self.request.body)

        # witnesses = self.get_argument("witnesses")
        witnesses = params['witnesses']

        uris = map(lambda witness: witness['uri'], witnesses)
        # ids = map(lambda witness: witness['id'], witnesses)

        # Retrieve the stanzas
        texts = filter(lambda stanza: stanza is not None, map(Tokenizer.parse_text, uris))
        # texts = map(Tokenizer.parse_text, uris)

        ids = []
        for text in texts:

            id_elems = text.xpath('//tei:div[@type="poem" or @type="book"]/@n', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

            if len(id_elems) > 0:
                ids.append(id_elems[0])

        # tei_stanza_u, tei_stanza_v = map(Tokenizer.parse_stanza, uris)
        # id_u, id_v = ids

        base_text = texts[0]
        texts = texts[1:]

        base_id = ids[0]
        ids = ids[1:]

        witnesses = []
        for node, _id in zip(texts, ids):

            witnesses.append( { 'node': node, 'id': _id } )

        # Tokenize the stanzas
        tokenizer= Tokenizer()
        stemma = Tokenizer.stemma({ 'node': base_text, 'id': base_id }, witnesses)

        # Generate the collation
        collated_set = Collation(stemma)
        
        self.render("collate.html", collation=collated_set.values())

#    @gen.coroutine
#    def get_value(self, value):

#        time.sleep(0.5)

#        output = os.getpid()

#        return str(output)

    @gen.coroutine
    def diff(self, node_u, text_u_id, node_v, text_v_id):

        diff_u_v_tree = Tokenizer.diff(node_u, text_u_id, node_v, text_v_id)
        raise gen.Return(diff_u_v_tree)

    @gen.coroutine
    def stemma(self, base_values, witness_values):
        
        stemma = Tokenizer.stemma(base_values, witness_values)
        raise gen.Return(stemma)

    # For testing, remove for integration with Fedora Commons
    @gen.coroutine
    def get(self, apparatus = '444', base = '444-0201'):

        # @todo Refactor and abstract
        #
        paths = [
                'tests/fixtures/test_swift_36629.xml',
                'tests/fixtures/test_swift_36670.xml',
                'tests/fixtures/test_swift_36711.tei.xml',
                'tests/fixtures/test_swift_36752.tei.xml',
                'tests/fixtures/test_swift_36793.tei.xml',
                'tests/fixtures/test_swift_40916.tei.xml',
                'tests/fixtures/test_swift_40267.tei.xml',
                'tests/fixtures/test_swift_39876.tei.xml',
                'tests/fixtures/test_swift_39573.tei.xml',
                'tests/fixtures/test_swift_39477.tei.xml',
                'tests/fixtures/test_swift_37660.tei.xml',
                'tests/fixtures/test_swift_37602.tei.xml',
                'tests/fixtures/test_swift_36992.tei.xml',
                'tests/fixtures/test_swift_36940.tei.xml',
                'tests/fixtures/test_swift_36834.tei.xml',
                ]

        paths = [
            '444-0201.tei.xml',
            '444-0251.tei.xml',
            '444-0271.tei.xml',
            '444-04P1.tei.xml',
            '444-060Y.tei.xml',
            '444-14W2.tei.xml',
            '444-33D1.tei.xml',
            '444-422R.tei.xml',
            '444-51L1.tei.xml',
            '444-902A.tei.xml',
            '444-S865.tei.xml',
            '444-T160.tei.xml',
            '444-0202.tei.xml',
            '444-0252.tei.xml',
            '444-04M1.tei.xml',
            '444-04P3.tei.xml',
            '444-06E2.tei.xml',
            '444-29L2.tei.xml',
            '444-33D2.tei.xml',
            '444-44L6.tei.xml',
            '444-600I.tei.xml',
            '444-ROGP.tei.xml',
            '444-S866.tei.xml',
            '444-T161.tei.xml',
            '444-0203.tei.xml',
            '444-0253.tei.xml',
            '444-04M2.tei.xml',
            '444-04P4.tei.xml',
            '444-06H1.tei.xml',
            '444-29MB.tei.xml',
            '444-33D-.tei.xml',
            '444-45L9.tei.xml',
            '444-700B.tei.xml',
            '444-S863.tei.xml',
            '444-S867.tei.xml',
            '444-T163.tei.xml',
            '444-0204.tei.xml',
            '444-0254.tei.xml',
            '444-04M4.tei.xml',
            '444-04P6.tei.xml',
            '444-070B.tei.xml',
            '444-31L1.tei.xml',
            '444-36L-.tei.xml',
            '444-46L1.tei.xml',
            '444-79L2.tei.xml',
            '444-S864.tei.xml',
            '444-T159.tei.xml',
            '444-WILH.tei.xml',            
            ]

        uris = map(lambda path: os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests/fixtures', path), paths)

        ids = map(lambda path: path.split('.')[0], paths)
        ids = ids[1:]

        apparatus_file_paths = {
            '444': { 'uris': uris, 'ids': ids },
            }

        uris = apparatus_file_paths[apparatus]['uris']
        ids = apparatus_file_paths[apparatus]['ids']

        # Retrieve the stanzas
        texts = map(Tokenizer.parse_text, uris)

        # Set the base text
        base_text = texts[0]
        texts = texts[1:]

        # Structure the base and witness values
        base_values = { 'node': base_text, 'id': base }
        base_values['node'] = etree.tostring(base_values['node'])

        witnesses = []
        for node, witness_id in zip(texts, ids):

            witness_values = { 'node': node, 'id': witness_id }
            witness_values['node'] = etree.tostring(witness_values['node'])

            # witnesses.append( { 'node': node, 'id': witness_id } )
            witnesses.append( witness_values )

        # Initialize the stemmatic tree
        diff_tree = nx.Graph()

        stemma = nx.Graph()
        stemmata = []

        # results = yield [ self.stemma(base_values, witnesses[j-1:j]) for j in range(1, len(witnesses)) ]
        # results = yield [ self.stemma(base_values, witnesses[j-1:j]) for j in range(1, 2) ]

        for i in range(3, len(witnesses), 3):

            # witnesses = witnesses[i-3:i]

            roots = [ base_values ] * len(witnesses)
            tokenize_diff_args = []

            for text_u, text_v in zip(roots, witnesses[i-3:i]):

                # tokenize_diff_args.append( (text_u['node'], text_u['id'], text_v['node'], text_v['id']) )
                tokenize_diff_args.append( (text_u, text_v) )

            diff_results = pool.map( tokenize_diff, tokenize_diff_args )
            # diff_results = []

            # Reduce the output
            for diff_result in diff_results:

                diff_tree = nx.compose(diff_tree, diff_result)

        # stemma_results = pool.map( tokenize, [ (base_values, witnesses[0:1]) ] )
        stemma_results = []

        # Reduce the output
        for sub_tree in iter(stemma_results):

            stemma = nx.compose(stemma, sub_tree)

        # Generate the collation
#        collated_set = Collation(stemma)

        # futures = pool.map( get_value, ['trace3'] * 5 )
        # values = futures

        # self.write(", ".join(values))
        # pool.shutdown()
        # self.render("collate.html", collation=collated_set.values())

        self.write("trace")

def diff_text(_args):

    diff = DifferenceText(_args[0], _args[1])
    
    return diff

class CollateHandler(tornado.web.RequestHandler):
    
    executor = None # Work-around

    @gen.coroutine
    def get(self, apparatus = '444', base_id = '444-0201'):

        # @todo Refactor and abstract
        paths = [
            '444-0201.tei.xml',
            '444-0251.tei.xml',
            '444-0271.tei.xml',
            '444-04P1.tei.xml',
            '444-060Y.tei.xml',
            '444-14W2.tei.xml',
            '444-33D1.tei.xml',
            '444-422R.tei.xml',
            '444-51L1.tei.xml',
            '444-902A.tei.xml',
            '444-S865.tei.xml',
            '444-T160.tei.xml',
            '444-0202.tei.xml',
            '444-0252.tei.xml',
            '444-04M1.tei.xml',
            '444-04P3.tei.xml',
            '444-06E2.tei.xml',
            '444-29L2.tei.xml',
            '444-33D2.tei.xml',
            '444-44L6.tei.xml',
            '444-600I.tei.xml',
            '444-ROGP.tei.xml',
            '444-S866.tei.xml',
            '444-T161.tei.xml',
            '444-0203.tei.xml',
            '444-0253.tei.xml',
            '444-04M2.tei.xml',
            '444-04P4.tei.xml',
            '444-06H1.tei.xml',
            '444-29MB.tei.xml',
            '444-33D-.tei.xml',
            '444-45L9.tei.xml',
            '444-700B.tei.xml',
            '444-S863.tei.xml',
            '444-S867.tei.xml',
            '444-T163.tei.xml',
            '444-0204.tei.xml',
            '444-0254.tei.xml',
            '444-04M4.tei.xml',
            '444-04P6.tei.xml',
            '444-070B.tei.xml',
            '444-31L1.tei.xml',
            '444-36L-.tei.xml',
            '444-46L1.tei.xml',
            '444-79L2.tei.xml',
            '444-S864.tei.xml',
            '444-T159.tei.xml',
            '444-WILH.tei.xml',            
            ]

        uris = map(lambda path: os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests/fixtures', path), paths)

        ids = map(lambda path: path.split('.')[0], paths)
        ids = ids[1:]

        apparatus_file_paths = {
            '444': { 'uris': uris, 'ids': ids },
            }

        uris = apparatus_file_paths[apparatus]['uris']
        ids = apparatus_file_paths[apparatus]['ids']

        # Retrieve the stanzas
        texts = map(Tokenizer.parse_text, uris)

        # Set the base text
        base_text = texts[0]
        texts = texts[1:]

        # Structure the base and witness values
        base_values = { 'node': base_text, 'id': base_id }
        # base_values['node'] = etree.tostring(base_values['node'])

        witnesses = []
        for node, witness_id in zip(texts, ids):

            witness_values = { 'node': node, 'id': witness_id }
            # witness_values['node'] = etree.tostring(witness_values['node'])
            witnesses.append( witness_values )

        base_text = Text(base_text, base_id)
        base_text.tokenize()

        witness_texts = map(lambda witness: Text(witness['node'], witness['id']), witnesses )
        # witness_texts = map(lambda witness: Text(witness['node'], witness['id']), witnesses[0:4] )

        # diffs = map(lambda witness_text: DifferenceText(base_text, witness_text), witness_texts )

        # Parallelize
        diff_args = map( lambda witness_text: (base_text, witness_text), witness_texts )
        diffs = self.executor.map( diff_text, diff_args )

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
            (r"/collate", CollateHandler),
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
