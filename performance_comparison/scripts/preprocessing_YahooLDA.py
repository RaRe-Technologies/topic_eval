import logging
import sys
from smart_open import smart_open

import gensim
from six import string_types

logger = logging.getLogger('prepare_wiki')


def getstream(input):
    """
    If input is a filename (string), return `open(input)`.
    If input is a file-like object, reset it to the beginning with `input.seek(0)`.
    """
    assert input is not None
    if isinstance(input, string_types):
        # input was a filename: open as text file
        result = open(input)
    else:
        # input was a file-like object (BZ2, Gzip etc.); reset the stream to its beginning
        result = input
        result.seek(0)
    return result

class LineCorpus(gensim.corpora.TextCorpus):
    def get_texts(self):
        length = 0
        lines = getstream(self.input)  # open file/reset stream to its start
        for lineno, line in enumerate(lines):
            length += 1
            yield line.split() # return entire line. One doc per line
        self.length = length


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
    logging.root.setLevel(level=logging.INFO)
    logger.info("running %s" % ' '.join(sys.argv))

    line_corpus_file = 'text_out_nob20_noa10.txt'

    # add document_id and site_id to comply with YahooLDA format
    aux_id = 'wiki'
    doc_id = 0
    with smart_open(line_corpus_file+'_yahoo_lda', 'wb') as fout:
        with smart_open(line_corpus_file) as fin:
            for line in fin:
                fout.write(str(doc_id) + ' ' + aux_id + ' ' + line)
                doc_id = doc_id + 1
