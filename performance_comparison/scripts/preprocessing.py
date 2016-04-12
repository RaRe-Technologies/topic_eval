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

class ShootoutCorpus(gensim.corpora.TextCorpus):
    def get_texts(self):
        length = 0
        lines = getstream(self.input)  # open file/reset stream to its start
        for lineno, line in enumerate(lines):
            length += 1
            yield line.split('\t')[1].split()  # return tokens (ignore the title before the tab)
        self.length = length

    def corpus2text(self, docs, fname):
        """
        Write out `corpus` in a file format that anything understands: one document per line:
          whitespace delimited utf8-encoded tokens[NEWLINE]
        At the same time, create a word=>id mapping of all tokens present in the corpus.
        """
        logger.info("serializing temporary corpus to %s", fname)
        fout = smart_open(fname, 'wb') if isinstance(fname, basestring) else fname
        if self.dictionary is None:
            # this is the first pass: we have no dictionary
            id2word = gensim.corpora.Dictionary()
            for docno, tokens in enumerate(docs):
                id2word.doc2bow(tokens, allow_update=True)
                fout.write(to_utf8("%s\n" % (' '.join(tokens))))
            self.dictionary = id2word
        else:
            logger.info('Already have dictionary')
            # we already have a dictionary: ignore all tokens not in it
            for docno, tokens in enumerate(docs):
                tokens = [token for token in tokens if token in self.dictionary.token2id]
                fout.write(to_utf8("%s\n" % (' '.join(tokens))))
        fout.close()



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

    # Remove titles and filter vocabulary from shoot-out corpus
    shootout_file = 'title_tokens.txt'
    line_corpus_file = 'text_out_nob20_noa10.txt'

    corpus = ShootoutCorpus(smart_open(shootout_file))
    corpus.dictionary.filter_extremes(no_below=10, no_above=0.3, keep_n=100000)  # remove too rare/too common words
    corpus.corpus2text(corpus.get_texts(), line_corpus_file)


    # Save the text corpus in MM format for Gensim itself and Gensim wrappers for Mallet and VW
    # Read it again because dictionary was filtered on write
    corpus = LineCorpus(smart_open(line_corpus_file))
    corpus.dictionary.save(line_corpus_file+'.dict')
    gensim.corpora.MmCorpus.serialize( line_corpus_file+'.mm', corpus)

