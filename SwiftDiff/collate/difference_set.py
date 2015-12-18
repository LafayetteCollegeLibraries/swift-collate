
class DifferenceSet(object):

    def __init__(self):

        self.lines = {}

    def lines(self, line_id):

        if not line_id in self.lines:

            self.lines[line_id] = DifferenceLine()

        return self.lines[line_id]
