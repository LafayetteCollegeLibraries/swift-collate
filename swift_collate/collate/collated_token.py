from nltk.metrics import distance as nltk_distance

class CollatedToken(object):

    def __init__(self, base_token, token):

        self.base_token = base_token
        self.token = token
        self.distance = self.find_distance()

    def find_distance(self):

        self.distance = nltk_distance.edit_distance(self.base_token['value'], self.token['value'])
        return self.distance

    def values(self):
        return {
            'base_token': self.base_token,
            'value': self.token['value'],
            'index': self.token['index'],
            'classes': self.token['classes'],
            'markup': self.token['markup'],
            'distance': self.distance
        }
