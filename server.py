
import os.path
import string

import tornado.ioloop
import tornado.web
import tornado.escape

from SwiftDiff.collation import Collation
from SwiftDiff.tokenizer import Tokenizer, TextToken, Line

from tornado.options import define, options, parse_command_line

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")

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

class CollateHandler(tornado.web.RequestHandler):

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

    # For testing, remove for integration with Fedora Commons
    def get(self, apparatus = 'R565', base = 'R56503P1'):

        # @todo Refactor and abstract
        #
        R565_uris = map(lambda path: os.path.join(os.path.dirname(os.path.abspath(__file__)), path), ['tests/fixtures/test_swift_36629.xml',
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

        R565_ids = [
            # "R56503P1",
               "R56503P2",
               "R56503P3",
               "R56503P4",
               "R56503P5",
               "R56503P7",
               "R56504M1",
               "R56504M2",
               "R56506E2",
               "R56506H1",
               "R56528D-",
               "R56532D-",
               "R56539D-",
               "R565760L",
               "R565ROGP"]

        zero11_uris = map(lambda path: os.path.join(os.path.dirname(os.path.abspath(__file__)), path), [
                'tests/fixtures/011/swift_35715.tei.xml',
                'tests/fixtures/011/swift_38903.tei.xml',
                'tests/fixtures/011/swift_40636.tei.xml',
                ])

        zero11_ids = [ 
            # '011-002D',
            '011-14W2',
            '011-HW37'
            ]

        apparatus_file_paths = { 'R565': { 'uris': R565_uris, 'ids': R565_ids },
                                 '011': { 'uris': zero11_uris, 'ids': zero11_ids },
                                 }

        uris = apparatus_file_paths[apparatus]['uris']
        ids = apparatus_file_paths[apparatus]['ids']

        # Retrieve the stanzas
        texts = map(Tokenizer.parse_text, uris)

        base_text = texts[0]
        texts = texts[1:]

        # base_text = { 'node': tei_stanza_u, 'id': 'u' }
        # witnesses = [ { 'node': tei_stanza_v, 'id': 'v' }, { 'node': tei_stanza_w, 'id': 'w' } ]
        witnesses = []
        for node, _id in zip(texts, ids):

            witnesses.append( { 'node': node, 'id': _id } )

        stemma = Tokenizer.stemma({ 'node': base_text, 'id': base }, witnesses)

        # Generate the collation
        collated_set = Collation(stemma)
        
        self.render("collate.html", collation=collated_set.values())

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
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":

    main()
