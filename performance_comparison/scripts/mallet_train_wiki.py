import logging
from smart_open import smart_open
import sys

import gensim

logger = logging.getLogger('mallet_lda')
topics_file = 'topics_descr_mallet.out'
model_file_name = 'mallet_lda_wiki_online.model'

corpus_file_name = '/home/lev/lda_comparison/data/shootout_modified/text_out_nob20_noa10.txt.mm'
dict_file_name = '/home/lev/lda_comparison/data/shootout_modified/text_out_nob20_noa10.txt.dict'


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
    logging.root.setLevel(level=logging.INFO)
    logger.info("running %s" % ' '.join(sys.argv))

    corpus = gensim.corpora.MmCorpus(corpus_file_name)
    dictionary = gensim.corpora.Dictionary.load(dict_file_name)
    lda_mallet = gensim.models.wrappers.LdaMallet('/home/lev/lda_comparison/mallet/mallet-2.0.8RC3/bin/mallet',
                                                  corpus=corpus, num_topics=100, id2word=dictionary)
    lda_mallet.save(model_file_name)
    topics_descr = lda_mallet.print_topics(-1)  # print a few most important words for each LDA topic

    with smart_open(topics_file, 'wb') as fout:
        for top_words in topics_descr:
            fout.write("\n\n %s \n" % ('=====New Topic====='))
            fout.write("%s %s" % (top_words))