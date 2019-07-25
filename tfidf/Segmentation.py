import jieba

class Segmentation:
    def __init__(self):
        jieba.load_userdict('./misc/jieba_dict.txt')

    def segmentation(self, texts):
        '''
        :param texts: a list of texts
        :return: a list of segmented text (using jieba)
        '''
        results = []
        for item in texts:
            results.append(self.dealWithSpecialCases(' '.join(jieba.cut(item))))
        return results

    def dealWithSpecialCases(self, text):
        # ‘孟晚舟’会被分割成‘孟晚 舟’
        # text = text.replace('孟晚 舟','孟晚舟')
        return text