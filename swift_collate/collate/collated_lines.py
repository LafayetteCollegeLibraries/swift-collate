import json
from collatex import collate_pretokenized_json, Collation, collate, AlignmentTable, Row, Witness, display_alignment_table_as_json
from collated_line import CollatedLine
from ..text import Token
from ..text.token import TokenJSONEncoder

class CollatedLines(object):

    def __init__(self, base_line, variant_lines=[]):
        self.base_line = base_line
        self.variant_lines = variant_lines

    def add_variant_line(self, line):
        collated_line = CollatedLine(self.base_line, line)
        self.variant_lines.append(collated_line)

    def transform_alignment(self, alignment):
        table = alignment['table']
        base_row_tokens = []

        base_row = table[0]
        if len(base_row) > 0:
            base_line_row = base_row[0]
            for tlist in base_row:
                if len(tlist) > 0:
                    row_token = tlist.pop()
                    base_row_tokens.append(row_token['t'])

            # Clear the current tokens for the base line
            self.base_line['tokens'] = []

            for token_index, token_value in enumerate(base_row_tokens):
                base_token = Token(token_value, token_index)
                base_token_data = json.loads(TokenJSONEncoder().encode(base_token))

                self.base_line['tokens'].append( base_token_data )

        variant_rows = table[1:]
        for line_index, variant_row in enumerate(variant_rows):

            variant_row_tokens = []

            if len(variant_row) > 0:
                variant_line_row = variant_row[0]
                for tlist in variant_row:
                    if len(tlist) > 0:
                        row_token = tlist.pop()
                        variant_row_tokens.append(row_token['t'])

            variant_line = self.variant_lines[line_index]
            variant_line.tokens = []

            for token_index, token_value in enumerate(variant_row_tokens):
                variant_line.tokens.append(Token(token_value, token_index))

#            variant_line.tokenize()

    def align_witnesses(self, witnesses):
        normalized_witnesses = []
        tokenized_witnesses = []
        for witness in witnesses:
            normalized_tokens = []
            tokenized_witness = []
            sigil = witness["id"]
            for token in witness["tokens"]:
                tokenized_witness.append(token)
                if "n" in token:
                    normalized_tokens.append(token["n"])
                else:
                    normalized_tokens.append(token["t"])
            normalized_witnesses.append(Witness(sigil, " ".join(normalized_tokens)))
            tokenized_witnesses.append(tokenized_witness)
        collation = Collation()
        for normalized_witness in normalized_witnesses:
            if normalized_witness.content:
                collation.add_witness(normalized_witness.sigil, normalized_witness.content)

        results = {
            "witnesses": [],
            "table": [[]],
            "status": []
        }

        if len(collation.witnesses) > 0:
            at = collate(collation, output="novisualization", segmentation=False)
            tokenized_at = AlignmentTable(collation)
            for row, tokenized_witness in zip(at.rows, tokenized_witnesses):

                new_row = Row(row.header)
                tokenized_at.rows.append(new_row)
                token_counter = 0

                for cell in row.cells:
                    if cell != "-":
                        if token_counter <= len(tokenized_witness) - 1:
                            new_row.cells.append(tokenized_witness[token_counter])
                            token_counter+=1
                    else:
                        # TODO: should probably be null or None instead, but that would break the rendering at the moment
                        new_row.cells.append({"t":"^"})

            alignment = json.loads(display_alignment_table_as_json(tokenized_at))
            self.transform_alignment(alignment)

    def align(self):

        collated_body = []
        witnesses = []

        base_tokens = map(lambda token: { 't': token['value'], 'n': token['normal_value'] }, self.base_line['unaligned_tokens'])
        base_witness = { 'id': 'base', 'tokens': base_tokens }
        
        witnesses.append(base_witness)

        for line_index, other_line in enumerate(self.variant_lines):
            other_tokens = []

            other_line.tokenize()
            other_tokens = map(lambda collation_token: { 't': collation_token.token['value'], 'n': collation_token.token['normal_value'] }, other_line.unaligned_tokens)
            other_witness = { 'id': str(line_index), 'tokens': other_tokens }
            witnesses.append(other_witness)

            collated_body.append(self.align_witnesses(witnesses))

#            try:
#                collated_body.append(self.align_witnesses(witnesses))
#            except Exception as e:
                # raise AlignmentException("Failed to align witnesses in a set: " + e)
#                print("Failed to align witnesses in a set: " + str(e))

#        return collated_body

    def tokenize(self):
        for variant_line in self.variant_lines:
            variant_line.tokenize()

    def values(self):
        return {
            'base_line': self.base_line,
            'variant_lines': map(lambda variant_line: variant_line.values(), self.variant_lines)
        }
