import logging
from smart_open import smart_open
import sys

import gensim

logger = logging.getLogger('gensim_lda')
topics_file = 'topics_descr_gensim.out'
model_file_name = 'gensim_lda_wiki_online.model'

corpus_file_name = '/home/lev/lda_comparison/data/shootout_modified/text_out_nob20_noa10.txt.mm'
dict_file_name = '/home/lev/lda_comparison/data/shootout_modified/text_out_nob20_noa10.txt.dict'


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
    logging.root.setLevel(level=logging.INFO)
    logger.info("running %s" % ' '.join(sys.argv))

    corpus = gensim.corpora.MmCorpus(corpus_file_name)
    dictionary = gensim.corpora.Dictionary.load(dict_file_name)

    lda_model = gensim.models.LdaMulticore(corpus=corpus, id2word=dictionary,
                    num_topics=100, passes=1, chunksize=10000,
                    batch=False, #force online mode
                    alpha='symmetric', eta=None,
                    decay=0.5, offset=1.0, eval_every=0,
                    iterations=50, gamma_threshold=0.001)
    lda_model.save(model_file_name)
    topics_descr = lda_model.print_topics(-1)  # print a few most important words for each LDA topic

    with smart_open(topics_file, 'wb') as fout:
        for (topic_id, top_words) in topics_descr:
            fout.write("\n\n %s \n" % ('=====New Topic====='))
            fout.write("%s %s" % (str(topic_id), top_words))