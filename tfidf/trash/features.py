class AbstractFeature(object):
    def apply(self):
        raise NotImplementedError('Should have implemented this.')

class KeywordSimilarity(AbstractFeature):
    def apply(self, keyword1, keyword2, embedder):
        return embedder.get_similarity(keyword1, keyword2)

#class TopContentSimilarity(AbstractFeature):
#    def apply(self,):