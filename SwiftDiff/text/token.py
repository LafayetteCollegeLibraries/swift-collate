import re

class Token(object):

    def __init__(self, value, index, classes=[], markup={}, pos=None):

        self.value = value
        self.index = index
        self.classes = classes
        self.markup = markup

        # Clean
        self.value = re.sub(r'_', '', self.value)
        self.value = re.sub('08\.', '', self.value)
        self.value = re.sub('8\.', '', self.value)


        self.pos = pos
