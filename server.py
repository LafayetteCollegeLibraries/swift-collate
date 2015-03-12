
import os.path
import tornado.ioloop
import tornado.web

from collation import Collation
from tokenizer import Tokenizer

from tornado.options import define, options, parse_command_line

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")

class CollateHandler(tornado.web.RequestHandler):

    def post(self):

        witnesses = self.get_argument("witnesses")

        uris = map(lambda witness: witness['uri'], witnesses)
        ids = map(lambda witness: witness['id'], witnesses)

        # Retrieve the stanzas
        tei_stanza_u, tei_stanza_v = map(Tokenizer.parse_stanza, uris)
        id_u, id_v = ids

        # Tokenize the stanzas
        tokenizer= Tokenizer()

        # diff_tree = Tokenizer.diff(tei_stanza_u, id_u, tei_stanza_v, id_v)
        diff_tree = Tokenizer.diff(tei_stanza_u, id_u, tei_stanza_v, id_v)

        # Generate the collation
        collated_set = Collation(diff_tree)

        self.render("collate.html", collation=collated_set.values())

    # For testing, remove for integration with Fedora Commons
    def get(self):

        uris = map(lambda path: os.path.join(os.path.dirname(os.path.abspath(__file__)), path), ['tests/fixtures/test_swift_36629.xml',
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
                                                                                                 ])
        ids = map(str, range(1, len(uris)))

        # Retrieve the stanzas
        texts = map(Tokenizer.parse_text, uris)

        base_text = texts[0]
        texts = texts[1:]

        # base_text = { 'node': tei_stanza_u, 'id': 'u' }
        # witnesses = [ { 'node': tei_stanza_v, 'id': 'v' }, { 'node': tei_stanza_w, 'id': 'w' } ]
        witnesses = []
        for node, _id in zip(texts, ids):

            witnesses.append( { 'node': node, 'id': _id } )

        stemma = Tokenizer.stemma({ 'node': base_text, 'id': 'base' }, witnesses)

        # Generate the collation
        collated_set = Collation(stemma)
        
#        for row,values in collation['lines'].iteritems():

#            if 'line' in values and 'ngram' in values:

#                for i, token in enumerate(values['ngram'][values['ngram'].keys()[0]]):

#                    print i

#                for line_ngram_witness, line_ngrams in values['ngram'].iteritems():

#                    print line_ngram_witness

        self.render("collate.html", collation=collated_set.values())

        pass

class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html")

application = tornado.web.Application([
    (r"/", MainHandler),
])

def main():
    parse_command_line()
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
#            (r"/auth/login", AuthLoginHandler),
#            (r"/auth/logout", AuthLogoutHandler),
            (r"/collate", CollateHandler),
            ],
        cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        login_url="/auth/login",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=True,
        debug=options.debug,
        )
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":

    main()
