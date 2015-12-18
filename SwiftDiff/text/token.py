
class Token(object):

    def __init__(self, value, index, classes=[], markup={}):

        self.value = value
        self.index = index
        self.classes = classes
        self.markup = markup
