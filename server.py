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
import traceback

import networkx as nx
from lxml import etree

from pymongo import MongoClient
from bson.binary import Binary

import requests

from oauth2client.service_account import ServiceAccountCredentials
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from io import BytesIO
from apiclient import discovery
from apiclient.http import MediaIoBaseDownload
from httplib2 import Http

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'client_secret.json')
APPLICATION_NAME = 'Swift Poems Project Digital Edition'

class GDriveService(object):

    def __init__(self, client_secret_file, scopes):

        credentials = ServiceAccountCredentials.from_json_keyfile_name(client_secret_file, scopes)
        _http = credentials.authorize(Http())
        self._service = discovery.build('drive', 'v3', http=_http)

    def file(self, file_id):

        request = self._service.files().get_media(fileId=file_id)
        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            # print "Download %d%%." % int(status.progress() * 100)
        return fh

    def items(self, query, _fields = "nextPageToken, files(id, name)"):

        results = self._service.files().list(q=query,fields=_fields).execute()
        items = results.get('files', [])
        return items

class NotaBeneStore(object):

    def __init__(self):
        pass

class NotaBeneGDriveStore(NotaBeneStore):

    def __init__(self, client_secret_file, scopes):

        self._service = GDriveService(client_secret_file, scopes)

    def source(self, source_id):

        drive_files = []
        query = "name contains '" + source_id + "'"

        for item in self._service.items(query):
            word_doc_match = re.search('\.doc$', item['name'], flags=re.IGNORECASE)
            if not word_doc_match:
                fh = self._service.file(item['id'])
                drive_file_content = fh.getvalue()
                drive_files.append(drive_file_content)
                fh.close()

        return drive_files

    def transcript(self, transcript_id):

        drive_files = []
        query = "name = '" + transcript_id + "'"

        for item in self._service.items(query):

            fh = self._service.file(item['id'])
            drive_file_content = fh.getvalue()
            drive_files.append(drive_file_content)
            fh.close()

        try:
            return drive_files.pop()
        except:
            raise IOError("Failed to find the Google Drive File for " + transcript_id)


class NotaBeneEncoder(object):

    def __init__(self, protocol = 'http', host = 'localhost', port = 9292, url = 'http://localhost', cache_path = None):
        
        self._url = url
        if cache_path:
            self.cache_path
        else:
            self.cache_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tmp', 'tei')

    def cache_get(self, transcript_id):

        cached_file_path = os.path.join(self.cache_path, transcript_id + '.tei.xml')
        cached = None
        if os.path.isfile(cached_file_path):
            fh = open(cached_file_path, 'rb')
            cached = fh.read()
            fh.close()

        return cached

    def cache_set(self, transcript_id, cached):

        cached_file_path = os.path.join(self.cache_path, transcript_id + '.tei.xml')
        fh = open(cached_file_path, 'wb')
        fh.write(cached)
        fh.close()

    def transcript(self, source_id, transcript_id, nota_bene = None):

        tei_xml = self.cache_get(transcript_id)
        if tei_xml is None:

            if nota_bene:
                endpoint = "/".join([self._url, source_id, transcript_id, 'encode'])
                response = requests.post(endpoint, data=nota_bene)
            else:
                endpoint = "/".join([self._url, 'encode'])
                response = requests.post(endpoint, data={'transcript': transcript_id})

            response_body = response.text
            print response_body
            try:
                tei_objs = json.loads(response_body)
                tei = tei_objs.pop(0)
                tei_xml = tei['tei']
                tei_xml = tei_xml.encode('utf-8')

                self.cache_set(transcript_id, tei_xml)
            except Exception as ex:
                # raise CollationException(str(ex) + traceback.format_exc())
                print str(ex)
                print traceback.format_exc()
            
        return tei_xml

    def transcripts(self, poem = None):
        if poem:
            endpoint = "/".join([self._url, 'encode'])
            response = requests.post(endpoint, data={'poem': poem})

            transcript_ids = json.loads(response.text)
            transcripts_xml = map(lambda transcript_id: self.transcript(None, transcript_id), transcript_ids)

            # tei_docs = map(lambda tei_object: etree.fromstring(tei_object), transcripts_xml)
            tei_docs = []
            for xml in transcripts_xml:
                try:
                    tei_doc = etree.fromstring(xml)
                    tei_docs.append(tei_doc)
                except:
                    pass

#        tei_objects = json.loads(response.text)
#        tei_docs = map(lambda tei_object: etree.fromstring(tei_object), tei_objects)
        return [transcript_ids,tei_docs]

nota_bene_store = NotaBeneGDriveStore(CLIENT_SECRET_FILE, SCOPES)
nota_bene_encoder = NotaBeneEncoder(url = 'http://localhost:9292/transcripts')

import tornado.ioloop
import tornado.web
from tornado.web import URLSpec as URL
import tornado.escape
import tornado.httpserver
import tornado.websocket
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from tornado import gen, queues
from tornado.options import define, options, parse_command_line
from tornado_cors import CorsMixin

from SwiftDiff import TextToken
from SwiftDiff.text import Line, Text, TextJSONEncoder
from SwiftDiff.collate import DifferenceText, Collation, CollationJSONEncoder, DifferenceTextJSONEncoder, AlignmentException
from SwiftDiff.tokenize import Tokenizer, SwiftSentenceTokenizer

import scss
scss.config.STATIC_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
scss.config.ASSETS_ROOT = os.path.join(scss.config.STATIC_ROOT, 'assets/')

from scss.compiler import Compiler
compiler = Compiler()
import glob

for scss_file_path in glob.glob(scss.config.STATIC_ROOT + '/scss/**'):
    css_file_path = re.sub(r'scss', 'css', scss_file_path)
    css_file = open(css_file_path, 'wb')
    css_file.write( compiler.compile_string(open(scss_file_path).read()) )
    css_file.close()

MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 3

# Retrieve the configuration settings
config = ConfigParser.RawConfigParser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'swift_collate.cfg'))

# Work-around for multiprocessing within Tornado
max_workers = config.getint('server', 'max_workers')
pool = ProcessPoolExecutor(max_workers=max_workers)

# Retrieve the cache configuration
host = config.get('MongoDB', 'host')
port = config.getint('MongoDB', 'port')
client = MongoClient(host, port)
db_name = config.get('MongoDB', 'db_name')

# Retrieve the server configuration
TEI_DIR_PATH = config.get('server', 'tei_dir_path')
tei_dir_path = TEI_DIR_PATH
XSLT_FILE_PATH = config.get('server', 'xslt_file_path')
DEBUG = config.getboolean('server', 'debug')
SECRET = config.get('server', 'secret')

# Set the global variables for the server
define("port", default=8888, help="run on the given port", type=int)
define("debug", default=DEBUG, help="run in debug mode", type=bool)
define("processes", default=max_workers, help="concurrency", type=int)
define("secret", default=SECRET, help="secret for cookies")
define("cache", default=True, help="caching", type=bool)

clients = []

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
            
        return self.render_string("token.html", token=token_value, classes=classes, pos=token.pos)

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

        return self.render_string("line.html", witness_line=line_value, classes=classes)

class LinesModule(tornado.web.UIModule):
    def render(self, collation):
        return self.render_string("lines.html", collation=collation)
class NotaBeneLinesModule(tornado.web.UIModule):
    def render(self, collation):
        return self.render_string("lines_nb.html", collation=collation)

class LineModule(tornado.web.UIModule):
    def render(self, line_index, lines, collation):
        return self.render_string("line.html", line_index=line_index, lines=lines, collation=collation)

class TitlesModule(tornado.web.UIModule):
    def render(self, collation):
        return self.render_string("titles.html", collation=collation)
class NotaBeneTitlesModule(tornado.web.UIModule):
    def render(self, collation):
        return self.render_string("titles_nb.html", collation=collation)

class HeadnotesModule(tornado.web.UIModule):
    def render(self, collation):
        return self.render_string("headnotes.html", collation=collation)
class NotaBeneHeadnotesModule(tornado.web.UIModule):
    def render(self, collation):
        return self.render_string("headnotes_nb.html", collation=collation)

class FootnotesModule(tornado.web.UIModule):
    def render(self, collation):
        return self.render_string("footnotes.html", collation=collation)
class NotaBeneFootnotesModule(tornado.web.UIModule):
    def render(self, collation):
        return self.render_string("footnotes_nb.html", collation=collation)

class TitleFootnotesModule(tornado.web.UIModule):
    def render(self, collation):
        return self.render_string("title_footnotes.html", collation=collation)
class NotaBeneTitleFootnotesModule(tornado.web.UIModule):
    def render(self, collation):
        return self.render_string("title_footnotes.html", collation=collation)

class FootnoteModule(tornado.web.UIModule):
    def render(self, line_values):
        return self.render_string("footnote.html", line_values=line_values)

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

    diff = DifferenceText(base_text, [other_text], SwiftSentenceTokenizer)
    diff.tokenize()
    
    return diff

def collate_async(executor, base_text, witness_texts, poem_id, base_id, stream, stream_messages, socket=True):
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
        # diff_args = map( lambda witness_text: (base_text, witness_text, stream), witness_texts )
        diff_args = map( lambda witness_text: (base_text, witness_text), witness_texts )

        # Log to stream
        # @todo Open a pipe to the processes and block until the stream is updated?
        for base_text, other_text in diff_args:

            if socket:
                #stream_output += "<div>Comparing " + other_text.id + " to " + base_text.id + "...</div>"
                #stream.write_message(stream_output)
                stream_messages.append("Comparing " + other_text.id + " to " + base_text.id + "...")
                stream.write_message(json.dumps({'status': "\n".join(stream_messages)}))

        diff_texts = executor.map( compare, diff_args )

        # Log to stream
#        for base_text, other_text in diff_args:
#            if socket:
                #stream_output += "<div>Collating " + other_text.id + "...</div>"
                #stream.write_message(stream_output)
#                stream_messages.append("Collating " + other_text.id + "...")
#                stream.write_message(json.dumps({'status': "\n".join(stream_messages)}))

        base_diff_text = DifferenceText(base_text, [], SwiftSentenceTokenizer)

        for diff_text in diff_texts:
            if socket:
                diff_text_ids = map(lambda other_text: other_text.id, diff_text.other_texts)
                stream_messages.append("Collating " + ",".join(diff_text_ids) + "...")
                stream.write_message(json.dumps({'status': "\n".join(stream_messages)}))

            base_diff_text.merge(diff_text)

        result = base_diff_text
        # cache('collation_cache', key, result)
    else:
        result = doc

    return result

class TeiParser(object):

    @staticmethod
    def parse(content):

        return Tokenizer.parse_content(content)

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

    return result

excluded_file_names = [
    'UNDERDOT',
    '4DOS.COM',
    'TILDEOUT',
    'TILDEGEN',
    'FILENAME',
    'NICPRINT',
    'PRINTTST',
    'PCOLLBAT',
    'MODEDUPE',
    'SRCHMAKE',
    '4DOS.INI',
    'SUPERSCR',
    'RAWP.BAT',
    'TAIL.EXE',
    'S926BLNK',
    'HIDIDDLY',
    'INVINTRO',
    'INVGUIDE',
    'CASEDIDD',
    'JAMSDIDD'
]

def poem_ids():
    """Retrieve the ID's for poems within any given collection

    """

    poem_dir_paths = set()

    for f in os.listdir(tei_dir_path):
        path = os.path.join(tei_dir_path, f)

        if os.path.isdir(path) and f[0] != '.' and len(os.listdir(tei_dir_path)) > 1:

            poem_dir_paths.add(f)

    return sorted(poem_dir_paths)

def transcript_ids(poem_id):
    """Retrieve all transcripts ID's for any given poem

    """

    transcript_paths = []

    for f in os.listdir(os.path.join(tei_dir_path, poem_id)):
        if fnmatch.fnmatch(f, '*.tei.xml') and f[0] != '.':
            transcript_id = re.sub(r'\.tei\.xml$', '', f)
            transcript_paths.append(transcript_id)

    return sorted(transcript_paths)



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

    for f in os.listdir(os.path.join(tei_dir_path, poem_id)):

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

    uris = map(lambda path: os.path.join(tei_dir_path, poem_id, path), transcript_paths)
    return uris


tokenizer_modules = {'SwiftSentenceTokenizer': 'SwiftDiff.tokenize',
                     'PunktSentenceTokenizer': 'SwiftDiff.tokenize',
                     'TreebankWordTokenizer': 'nltk.tokenize.treebank',
                     'StanfordTokenizer': 'nltk.tokenize.stanford'}
def tokenizer_module(tokenizer_class_name):

    if tokenizer_class_name in tokenizer_modules:
        module = tokenizer_modules[tokenizer_class_name]
    else:
        raise Exception("Failed to locate the tokenizer Module for %s" % tokenizer_class_name)

    return module

tagger_modules = {'AveragedPerceptron': 'nltk.tag.perceptron.AveragedPerceptron',
                  'UnigramTagger': 'nltk.tag.sequential.UnigramTagger'}
def tagger_module(tagger_class_name):

    if tagger_class_name == 'disabled':
        module = None
    elif tagger_class_name in tagger_modules:
        module = tagger_modules[tagger_class_name]
    else:
        raise Exception("Failed to locate the tagger Module for %s" % tagger_class_name)

    return module

class TokenizerFactory:

    def __init__(self, tokenizer_class_name):
        try:
            module_name = tokenizer_module(tokenizer_class_name)
            m = importlib.import_module(module_name)
            self.klass = getattr(m, tokenizer_class_name)
        except:
            raise "Could not load the selected tokenizer"

class TaggerFactory:

    def __init__(self, tagger_class_name):

        if tagger_class_name == 'disabled':
            self.tagger = None
        else:
            try:
                module_name = tagger_module(tagger_class_name)
                m = importlib.import_module(module_name)
                tagger_class = getattr(m, tagger_class_name)
                self.tagger = tagger_class()
            except Exception as tagger_ex:
                raise Exception("Could not load the selected part-of-speech tagger %s" % tagger_ex)

class TranscriptException(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class CollationException(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class BaseCollateHandler(object):

    def load(self):

        # Parse the documents
        self.variant_texts = []
        message = 'ok'

        base_transcript = nota_bene_encoder.transcript('001A', self.base_id)

        # Work-around for lxml2
        # <?xml version="1.0" encoding="utf-8"?>
        base_transcript = base_transcript.replace('<?xml version="1.0" encoding="utf-8"?>', '')

        base_docs = map(TeiParser.parse, [base_transcript])
        self.base_doc = base_docs.pop()

        if self.base_doc is None:
            raise TranscriptException("Failed to retrieve the TEI-XML Document for " + self.base_id)

        # Structure the base and witness values
        base_values = { 'node': self.base_doc, 'id': self.base_id }

        docs = []
        print self.transcript_ids
        for transcript_id in self.transcript_ids:

            transcript = nota_bene_encoder.transcript('001A', transcript_id)
            if transcript is not None:
                transcript = transcript.replace('<?xml version="1.0" encoding="utf-8"?>', '')

                docs.append(TeiParser.parse(transcript))

        for node, witness_id in zip(docs, self.transcript_ids):
            # Ensure that Nodes which could not be parsed are logged as server errors
            # Resolves SPP-529
            if node is not None:
                witness_values = { 'node': node, 'id': witness_id, 'message': message }
            else:
                witness_values = { 'node': node, 'id': witness_id, 'message': 'Failed to parse the XML for the transcript ' + witness_id }
                logging.warn("Failed to parse the XML for the transcript %s", witness_id)

            self.variant_texts.append( witness_values )

        # Update the response body

        # self.response_body = map(lambda item: { 'node': etree.tostring(item['node']), 'id': item['id'], 'message': item['message'] }, self.variant_texts)
        variants = []

        for item in self.variant_texts:
            if 'node' in item and item['node'] is not None:
                variants.append({ 'node': etree.tostring(item['node']), 'id': item['id'], 'message': item['message'] })

        # self.variants = variants
        self.response_body = variants

    def tokenize(self):

        # Retrieve the base Text
        self.base_text = Text(self.base_doc, self.base_id, self.tokenizer, self.tagger)
        self.base_text.tokenize()

        # Retrieve the variant Texts
        #self.witness_texts = map(lambda witness: Text(witness['node'], witness['id'], self.tokenizer, self.tagger), self.variants)

        # Filter for errors in the parsing of the XML Documents
        self.witness_texts = []
        for witness in self.variant_texts:
            if 'node' in witness and witness['node'] is not None:
                self.witness_texts.append( Text(witness['node'], witness['id'], self.tokenizer, self.tagger) )

        # Update the response body
        self.response_body = map(lambda witness_text: TextJSONEncoder().encode(witness_text), self.witness_texts)

    def collate(self):
        try:
            collation = collate_async(self.executor, self.base_text, self.witness_texts, self.poem_id, self.base_id, None, None, False)
            # collation.collate()
            for diff_set in collation.body:
                
                for line in diff_set.variant_lines:
                    # print map(lambda token: token, line.tokens)
                    pass

            results = DifferenceTextJSONEncoder().encode(collation)

            self.response_body = results

        except AlignmentException as alignEx:
            print "Failed to align: " + alignEx
        except Exception as ex:
            raise CollationException(str(ex) + traceback.format_exc())

class CollateHandler(CorsMixin, tornado.web.RequestHandler, BaseCollateHandler):
    CORS_ORIGIN = '*'
    CORS_HEADERS = 'Content-Type'

    def send_error(self, status_code=500, **kwargs):

        if self.request.headers.get('Accept') == 'application/json':
            self.clear()
            self.set_header('Content-Type', 'application/json')

            reason = kwargs.get('reason')
            self.set_status(status_code)
            self.finish(json.dumps({'message': reason}))
        else:
            super(CollateHandler, self).send_error(self, status_code, **kwargs)

    @tornado.web.asynchronous
    def post(self):

        if self.request.headers.get('Accept') == 'application/json':
            self.set_header('Content-Type', 'application/json')
            self.json_args = json.loads(self.request.body)

            self.poem_id = self.json_args.get('poemId', None)
            base_text = self.json_args.get('baseText', None)
            self.transcript_ids = self.json_args.get('variantTexts', [])
            mode = self.json_args.get('mode', 'notaBene')
            tokenizer_class_name = self.json_args.get('tokenizer', 'SwiftSentenceTokenizer')
            tagger_class_name = self.json_args.get('tagger', 'disabled')

            tokenizer_factory = TokenizerFactory(tokenizer_class_name)
            self.tokenizer = tokenizer_factory.klass

            # Retrieve the POS tagger
            tagger_factory = TaggerFactory(tagger_class_name)
            self.tagger = tagger_factory.tagger
            
            # Load the documents
            self.base_id = base_text

            try:
                self.load()
                self.tokenize()
                self.collate()
                self.write(self.response_body)
            except CollationException as collateEx:
                print "Failed to collate: " + str(collateEx)
                self.write(self.response_body)
            except Exception as ex:
                print "Failed to collate: " + str(ex) + str(traceback.format_exc())
                self.send_error(500, reason = json.dumps(str(ex)))
        else:
            self.send_error(500, reason = json.dumps("Content-Type not supported"))


from tornado.log import gen_log, access_log
class CollateSocketHandler(tornado.websocket.WebSocketHandler, BaseCollateHandler):

    def initialize(self):
        self.messages = []

    def log(self, message):
        self.messages.append(message)
        self.write_message(json.dumps({'status': "\n".join(self.messages)}))

    def load(self):
        # Parse the documents
        self.variant_texts = []
        message = 'ok'

        base_transcript = nota_bene_encoder.transcript('001A', self.base_id)

        # Work-around for lxml2
        # <?xml version="1.0" encoding="utf-8"?>
        base_transcript = base_transcript.replace('<?xml version="1.0" encoding="utf-8"?>', '')

        base_docs = map(TeiParser.parse, [base_transcript])
        self.base_doc = base_docs.pop()

        if self.base_doc is None:
            # raise TranscriptException("Failed to retrieve the TEI-XML Document for " + self.base_id)
            # self.client.write_message("Failed to retrieve the TEI-XML Document for " + self.base_id)
            self.log("Failed to retrieve the TEI-XML Document for the base text " + self.base_id)
        else:
            self.log("Retrieved the TEI-XML Document for the base text " + self.base_id)

        # Structure the base and witness values
        base_values = { 'node': self.base_doc, 'id': self.base_id }

        docs = []

        for transcript_id in self.transcript_ids:

            transcript = nota_bene_encoder.transcript('001A', transcript_id)
            if transcript is not None:
                transcript = transcript.replace('<?xml version="1.0" encoding="utf-8"?>', '')
                docs.append(TeiParser.parse(transcript))
                self.log("Retrieved the TEI-XML Document for the variant text " + transcript_id)
            else:
                self.log("Failed to retrieve the TEI-XML Document for the variant text " + transcript_id)

        for node, witness_id in zip(docs, self.transcript_ids):
            # Ensure that Nodes which could not be parsed are logged as server errors
            # Resolves SPP-529
            if node is not None:
                witness_values = { 'node': node, 'id': witness_id, 'message': message }
            else:
                witness_values = { 'node': node, 'id': witness_id, 'message': 'Failed to parse the XML for the transcript ' + witness_id }
                # logging.warn("Failed to parse the XML for the transcript %s", witness_id)
                self.log("Failed to parse the XML for the transcript %s", witness_id)

            self.variant_texts.append( witness_values )

        # Update the response body

        # self.response_body = map(lambda item: { 'node': etree.tostring(item['node']), 'id': item['id'], 'message': item['message'] }, self.variant_texts)
        variants = []

        for item in self.variant_texts:
            if 'node' in item and item['node'] is not None:
                variants.append({ 'node': etree.tostring(item['node']), 'id': item['id'], 'message': item['message'] })

        # self.variants = variants
        self.response_body = variants

    def tokenize(self):

        # Retrieve the base Text
        self.base_text = Text(self.base_doc, self.base_id, self.tokenizer, self.tagger)
        self.base_text.tokenize()

        # Retrieve the variant Texts
        #self.witness_texts = map(lambda witness: Text(witness['node'], witness['id'], self.tokenizer, self.tagger), self.variants)

        # Filter for errors in the parsing of the XML Documents
        self.witness_texts = []
        for witness in self.variant_texts:
            if 'node' in witness and witness['node'] is not None:
                self.witness_texts.append( Text(witness['node'], witness['id'], self.tokenizer, self.tagger) )
                self.log("Tokenizing the TEI-XML Document for the variant text " + witness['id'])

        # Update the response body
        self.response_body = map(lambda witness_text: TextJSONEncoder().encode(witness_text), self.witness_texts)

    def collate(self):
        try:
            collation = collate_async(self.executor, self.base_text, self.witness_texts, self.poem_id, self.base_id, self, self.messages, True)
            # collation.collate()
#            for diff_set in collation.body:                
#                for line in diff_set.variant_lines:
                    # print map(lambda token: token, line.tokens)
#                    pass

            results = DifferenceTextJSONEncoder().encode(collation)

            self.response_body = results
            self.log("Collation completed")

        except AlignmentException as alignEx:
#            print "Failed to align: " + alignEx
            self.log("Failed to align: " + alignEx)

        except Exception as ex:
            raise CollationException(str(ex) + traceback.format_exc())
            self.log("Failed to collate: " + str(ex) + traceback.format_exc())

    @tornado.web.asynchronous
    def get(self, *args, **kwargs):
#        origin = self.request.headers.set("Origin", 'https://swift.stage.lafayette.edu/api/stream')
#        super(CollateSocketHandler, self).get(self, *args, **kwargs)
        self.open_args = args
        self.open_kwargs = kwargs

        # Upgrade header should be present and should be equal to WebSocket
        if self.request.headers.get("Upgrade", "").lower() != 'websocket':
            self.set_status(400)
            log_msg = "Can \"Upgrade\" only to \"WebSocket\"."
            self.finish(log_msg)
            gen_log.debug(log_msg)
            return

        # Connection header should be upgrade.
        # Some proxy servers/load balancers
        # might mess with it.
        headers = self.request.headers
        connection = map(lambda s: s.strip().lower(),
                         headers.get("Connection", "").split(","))
        if 'upgrade' not in connection:
            self.set_status(400)
            log_msg = "\"Connection\" must be \"Upgrade\"."
            self.finish(log_msg)
            gen_log.debug(log_msg)
            return

        # Handle WebSocket Origin naming convention differences
        # The difference between version 8 and 13 is that in 8 the
        # client sends a "Sec-Websocket-Origin" header and in 13 it's
        # simply "Origin".
        if "Origin" in self.request.headers:
            origin = self.request.headers.get("Origin")
        else:
            origin = self.request.headers.get("Sec-Websocket-Origin", None)

        # If there was an origin header, check to make sure it matches
        # according to check_origin. When the origin is None, we assume it
        # did not come from a browser and that it can be passed on.
#        if origin is not None and not self.check_origin(origin):
#            self.set_status(403)
#            log_msg = "Cross origin websockets not allowed"
#            self.finish(log_msg)
#            gen_log.debug(log_msg)
#            return

        self.stream = self.request.connection.detach()
        self.stream.set_close_callback(self.on_connection_close)

        self.ws_connection = self.get_websocket_protocol()
        if self.ws_connection:
            self.ws_connection.accept_connection()
        else:
            if not self.stream.closed():
                self.stream.write(tornado.escape.utf8(
                    "HTTP/1.1 426 Upgrade Required\r\n"
                    "Sec-WebSocket-Version: 7, 8, 13\r\n\r\n"))
                self.stream.close()

    def open(self):
        access_log.info("Collation client connected")
        self.write_message(json.dumps({'status': "Collation engine ready"}))
        if self not in clients:
            clients.append(self)

    def on_message(self, message):
        print message
        if message == '9':
            access_log.info("Collation client pinged")
            return

        self.messages = []

        # Parse the arguments from the message
        self.json_args = json.loads(message)

        self.poem_id = self.json_args.get('poem', None)

        base_text = self.json_args.get('baseText', None)
#        base_text = base_text.keys().pop()

        # transcript_ids = self.json_args['variants'].keys()
 #       self.transcript_ids = self.json_args.get('variants', {})
#        self.transcript_ids = self.transcript_ids.keys()
        self.transcript_ids = self.json_args.get('variantTexts', {})

        # mode = self.json_args['mode']
        self.mode = self.json_args.get('mode', 'notaBene')
        
        # tokenizer_class_name = self.json_args['tokenizer']
        tokenizer_class_name = self.json_args.get('tokenizer', 'SwiftSentenceTokenizer')

        # module_name = tokenizer_module(tokenizer_class_name)
        # m = importlib.import_module(module_name)
        # tokenizer = getattr(m, tokenizer_class_name)

        tokenizer_factory = TokenizerFactory(tokenizer_class_name)
        self.tokenizer = tokenizer_factory.klass

        tagger_class_name = self.json_args.get('tagger', 'disabled')

        # Retrieve the POS tagger
        tagger_factory = TaggerFactory(tagger_class_name)
        self.tagger = tagger_factory.tagger
            
        # Load the documents
        self.base_id = base_text
        access_log.info("Collation request for %s using %s as the base text", self.poem_id, self.base_id)

        self.load()
        self.tokenize()
        self.collate()

        # self.set_header('Content-Type', 'application/json')
        # self.write_message(self.response_body)
        self.write_message(json.dumps({'status': "\n".join(self.messages),'collation': self.response_body}))
        # self.write_message({'status': json.dumps("\n".join(self.messages)),'collation': self.response_body})

    def on_close(self):
        if self in clients:
            clients.remove(self)
        access_log.info("Collation client disconnected")



class TeiHandler(CorsMixin, tornado.web.RequestHandler):
    CORS_ORIGIN = '*'

    def get(self, transcript_id):
        tei_xml = nota_bene_encoder.transcript('001A', transcript_id)
        self.write(tei_xml)

class TranscriptsHandler(CorsMixin, tornado.web.RequestHandler):
    """The request handler for collation operations

    """

    def get(self, transcript_id):

        # Retrieve the TEI-XML from the data store
#        uri = ''
#        for dirName, subdirList, fileList in os.walk(TEI_DIR_PATH):
#            for f in fileList:
#                if fnmatch.fnmatch(f, transcript_id + '.tei.xml'):
#                    uri = f
#                    uri = os.path.join(dirName, uri)
        
#        super(TranscriptsHandler, self).get(uri)
#        xslt_doc = etree.parse(XSLT_FILE_PATH)
#        transform = etree.XSLT(xslt_doc)
#        doc = etree.parse(uri)
#        transcript_html_raw = transform(doc)
#        transcript_html_raw = etree.tostring(transcript_html_raw)
#        transcript_html = tornado.escape.xhtml_unescape(transcript_html_raw)
        transcript_html = ''
        self.render("transcript.html", transcript_html=transcript_html, transcript_id=transcript_id)

class PoemsHandler(CorsMixin, tornado.web.RequestHandler):
    """The request handler for viewing poem variants

    """

    CORS_ORIGIN = '*'

    executor = None # Work-around

    @gen.coroutine
    def get(self, poem_id):
        """The GET request handler for poems
        
        Args:
           poem_id (string):   The identifier for the poem set

        """

        poem_texts = []

        # Retrieve the stanzas
        # poem_docs = nota_bene_encoder.transcripts(poem=poem_id)
        # ids = map(lambda poem_doc: poem_doc.id, poem_docs)
        ids, poem_docs = nota_bene_encoder.transcripts(poem=poem_id)

        witnesses = []
        for node, witness_id in zip(poem_docs, ids):
            if node is not None:
                witness_values = { 'node': node, 'id': witness_id }
                witnesses.append( witness_values )

        # Construct the poem objects
        poem_texts.extend(map(lambda poem_text: Text(poem_text['node'], poem_text['id'], SwiftSentenceTokenizer), witnesses))

        if self.request.headers.get('Accept') == 'application/json':
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(poem_texts, cls=TextJSONEncoder))
        else:
            self.render("poem.html", poem_id=poem_id, poem_texts=poem_texts)

class TranscriptSearchHandler(tornado.web.RequestHandler):
    CORS_ORIGIN = '*'

    """The request handler for searching for transcripts

    """

    def get(self, poem_id):
        query = self.get_argument("q", "")
        poems = transcript_ids(poem_id)

        items = filter(lambda poem: re.search('^' + query, poem), poems)

        self.write(tornado.escape.json_encode({'items': items }))

class PoemAutocompleteHandler(CorsMixin, tornado.web.RequestHandler):
    CORS_ORIGIN = '*'

    """The request handler for autocompletion

    """

    def get(self):
        query = self.get_argument("q", "")
        poems = poem_ids()

        items = filter(lambda poem: re.search('^' + query, poem), poems)

        self.write(tornado.escape.json_encode({'items': items }))

class SearchHandler(tornado.web.RequestHandler):
    """The request handler for searching within transcripts

    """

    def get(self):
        query = self.get_argument("q", "")

        docs = [
            {'poem_id': '001A',
             'source_id': '100',
             'title': 'Sample Poem A',
             'first_line': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
             'publisher': '',
             'city': 'Dublin',
             'estc':'',
             'ecco': '',
             'teerink_scouten': '',
             'foxon': '',
             'lindsay': '',
             'date':'01/01/1800'
             },
            {'poem_id': '001B',
             'source_id': '101',
             'title': 'Sample Poem B',
             'first_line': 'Proin vel erat in libero volutpat euismod quis eget ante.',
             'publisher': '',
             'city': 'Cork',
             'estc':'',
             'ecco': '',
             'teerink_scouten': '',
             'foxon': '',
             'lindsay': '',
             'date':'02/01/1800'
             }
            ]

        self.render("results.html", docs=docs)

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

    parse_command_line()
    app = tornado.web.Application(
        [
            URL(r"/", MainHandler, name='index'),
            URL(r"/suggest/poems/?", PoemAutocompleteHandler),
            URL(r"/autocomplete/transcripts/([^/]+)/?", TranscriptSearchHandler),
            URL(r"/stream/?", CollateSocketHandler, name='stream'),
            URL(r"/collate/?", CollateHandler),
            URL(r"/poems/([^/]+)/?", PoemsHandler, name='poems'),
            URL(r"/transcripts/([^/]+)/?", TranscriptsHandler, name='transcripts'),
            URL(r"/tei/([^/]+)/?", TeiHandler, name='tei'),
            URL(r"/search/?", SearchHandler)
        ],
        cookie_secret=options.secret,
        login_url="/auth/login",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=False, # @todo Enable
#        debug=options.debug, # See http://stackoverflow.com/questions/22641015/run-multiple-tornado-processess
        ui_modules={ "Token": TokenModule,
                     "Line": LineModule,
                     "Titles": TitlesModule,
                     "NotaBeneTitles": NotaBeneTitlesModule,
                     "Headnotes": HeadnotesModule,
                     "NotaBeneHeadnotes": NotaBeneHeadnotesModule,
                     "Lines": LinesModule,
                     "NotaBeneLines": NotaBeneLinesModule,
                     "Footnotes": FootnotesModule,
                     "NotaBeneFootnotes": NotaBeneFootnotesModule,
                     "TitleFootnotes": TitleFootnotesModule,
                     "NotaBeneTitleFootnotes": NotaBeneTitleFootnotesModule,
                     "Footnote": FootnoteModule }
        )

    # https://gist.github.com/mywaiting/4643396
    global server
    server = tornado.httpserver.HTTPServer(app)
    server.bind(options.port)
    server.start(options.processes)

    # Extending the cleaning for individual threads
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    CollateSocketHandler.executor = ProcessPoolExecutor(max_workers=options.processes)
    CollateHandler.executor = ProcessPoolExecutor(max_workers=options.processes)
    ioloop = tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
