from invoke import run, task
import ConfigParser, os
from pymongo import MongoClient
from bson.binary import Binary
import fnmatch
import pickle
from SwiftDiff import TextToken
from SwiftDiff.text import Line, Text
from SwiftDiff.collate import DifferenceText, Collation
from SwiftDiff.tokenize import Tokenizer, SwiftSentenceTokenizer

# Retrieve the database
config = ConfigParser.RawConfigParser()
config.read( os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'swift_collate.cfg')  )
    
host = config.get('MongoDB', 'host')
port = config.getint('MongoDB', 'port')
client = MongoClient(host, port)

# Retrieve the server configuration
tei_dir_path = config.get('server', 'tei_dir_path')

import sys, traceback

@task
def validate_manuscript(dir_path, file_path):
    """Validate that an encoded manuscript can be collated

    """

    tei_source_dir_path = os.path.join(os.path.dirname(os.path.abspath(tei_dir_path)), 'sources')
    text_path = os.path.join(tei_source_dir_path, dir_path, file_path + '.tei.xml')
    file_doc = Tokenizer.parse_text(text_path)

    if file_doc is None:
        print "Failed to parse " + text_path
    try:
        Text(file_doc, 'validate', SwiftSentenceTokenizer)
        print "Successfully parsed " + text_path
    except Exception as e:
        print "Failed to encode " + text_path
        print "Error: %s" % str(e)
        print "Trace: %s" % traceback.format_exc()

@task
def validate_source(dir_path):
    """Validate that all encoded manuscripts for a given source can be collated

    """

    tei_source_dir_path = os.path.join(os.path.dirname(os.path.abspath(tei_dir_path)), 'sources')

    # Iterate for each manuscript
    for file_path in os.listdir(os.path.join(os.path.abspath(tei_source_dir_path), dir_path)):

        text_path = os.path.join(tei_source_dir_path, dir_path, file_path)
        file_doc = Tokenizer.parse_text(text_path)

        if file_doc is None:
            print "Failed to parse " + text_path
        try:
            Text(file_doc, 'validate', SwiftSentenceTokenizer)
            # print "Successfully parsed " + text_path
        except Exception as e:
            print "Failed to encode " + text_path
            print "Error: %s" % str(e)
            print "Trace: %s" % traceback.format_exc()

@task
def validate_sources():
    """Validate that all encoded manuscripts for all sources can be collated

    """

    tei_source_dir_path = os.path.join(os.path.dirname(os.path.abspath(tei_dir_path)), 'sources')

    for(path, dirs, files) in os.walk(tei_source_dir_path):
        for dir_path in dirs:
            for file_path in os.listdir(os.path.join(os.path.abspath(tei_source_dir_path), dir_path)):

                text_path = os.path.join(tei_source_dir_path, dir_path, file_path)
                file_doc = Tokenizer.parse_text(text_path)

                if file_doc is None:
                    print "Failed to parse " + text_path                    
                    continue
                try:
                    Text(file_doc, 'validate', SwiftSentenceTokenizer)
                    # print "Successfully parsed " + text_path
                except Exception as e:
                    print "Failed to encode " + text_path
                    print "Error: %s" % str(e)
                    print "Trace: %s" % traceback.format_exc()

# @todo Deduplicate
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

# @todo Deduplicate
def resolve(uri, update=False):
    """Resolves resources given a URI
    
    :param uri: The URL or URI for a file-system-based resource.
    :type uri: str.
    :param update: Should the cache be repopulated?
    :type uri: bool.
    :returns:  etree._Element -- the <tei:text> Element.

    """

    # Check the cache only if this is *NOT* a file-system resource
#    if re.match(r'^file\:\/\/', uri):

#        return Tokenizer.parse_text(uri)

#    doc = cache_db['texts'].find_one({'uri': uri})
    doc = None

    if not update and doc:
        result = etree.xml(doc['text'])
    else:
        # Otherwise, a web request may be issued for the resource
        result = Tokenizer.parse_text(uri)
        
        # Cache the resource
#        cache_db['texts'].replace_one({'uri': uri}, {'text': etree.tostring(result)}, upsert=True)

    return result


def cache(collection_name, key, value=None):

    db = client['swift_collate']
    collection = db[collection_name]

    if value is None:
        print 'searching the cache with %s' % key

        doc = collection.find_one(key)
        if doc is None:
            return None
        cached = pickle.loads(doc['data'])
    else:
        print 'caching %s' % key
        cached = pickle.dumps(value)

        data = key.copy()
        data.update({'data': Binary(cached)})

        collection.find_one_and_replace(key, data, upsert=True)

    return cached

def collate(base_text, witness_texts, poem_id, base_id):

    key = {'base_text': base_id}

    # Attempt to retrieve this from the cache
    doc = cache('collation_cache', key)
    if doc is None:
        # Collate the witnesses in parallel
        diff_args = map( lambda witness_text: (base_text, witness_text), witness_texts )
        diffs = map( compare, diff_args )

        tei_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xml', poem_id)
        result = Collation(base_text, diffs, tei_dir_path)
        cache('collation_cache', key, result)

    else:
        result = doc

    return result

# @todo Deduplicate
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

@task
def seed_cache(poem_id, base_id):

    # Generate the collation
    uris = doc_uris(poem_id)

    # Retrieve the ID's
    ids = map(lambda path: path.split('/')[-1].split('.')[0], uris)
    ids = ids[1:]

    # Generate the values for the collation
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

    # Begin the tokenization
    base_text = Text(base_text, base_id, SwiftSentenceTokenizer)
    base_text.tokenize()

    witness_texts = map(lambda witness: Text(witness['node'], witness['id'], SwiftSentenceTokenizer), witnesses )

    collation = collate(base_text, witness_texts, poem_id, base_id)
    pass
