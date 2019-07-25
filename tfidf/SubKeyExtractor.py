import jieba
from sklearn.feature_extraction.text import TfidfVectorizer

class SubKeyExtractor:
    def __init__(self):
        self.stop_words = getStopWords('./misc/stopwords.txt')

    def _get_segmentation(self, texts):
        '''废除了'''
        results = []
        for item in texts:
            results.append(' '.join(jieba.cut(item)))
        return results

    def fit(self, document):
        '''
        input document: segmented documents
        no return
        '''
        self.model = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b", stop_words=self.stop_words).fit(document)
        self.word2idx = self.model.vocabulary_
        self.idx2word = {v: k for k, v in self.word2idx.items()}

    def extract(self, document, top_n=5):
        '''
        input: a list of documents, each document correspond to one keyword;
        output: (#top_n) sub-keywords of each keyword;
        '''
        result = []
        for item in document:
            arr = self.model.transform([item]).toarray()[0]
            index = sorted(range(len(arr)), key=lambda k: arr[k], reverse=True)
            result.append([self.idx2word[item] for item in index[:top_n]])
        return result

def getStopWords(filename):
    '''Stopword lists from https://github.com/yinzm/ChineseStopWords'''
    file = open(filename, 'r')
    lines = file.readlines()
    lines = [line.strip() for line in lines]
    return lines

