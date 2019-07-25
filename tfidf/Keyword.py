import os
import re
import pandas as pd

URL_PATTERN = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
URL_MASK = '<URL>'

class Keyword(object):
    def __init__(self, keyword, dir):
        self.keyword = keyword
        self.dir = dir
        self.weibo_list = self.get_weibos()

    def get_weibos(self):
        results = []
        csv_file = open(os.path.join(self.dir, self.keyword, 'content.csv'), 'r')
        df = pd.read_csv(csv_file)
        for i in range(len(df)):
            results.append(Weibo(df.iloc[i], self.keyword, self.dir))
        return results

    def get_all_context_text(self):
        result = ''
        for weibo in self.weibo_list:
            result += weibo.content
        return result

    def get_top_context_text(self):
        return self.weibo_list[0].content

    def get_all_repost_text(self):
        return ' '.join([item.get_all_repost_text() for item in self.weibo_list])

class Weibo(object):
    def __init__(self, info, keyword, dir):
        self.keyword = keyword
        self.dir = dir
        self.id = info[0]
        self.userID = info[1]
        self.username = info[2]
        self.content = self._replace_url(info[3])
        self.timestamp = info[4]
        self.n_repost = int(info[5])
        self.n_like = int(info[6])
        self.n_comment = int(info[7])

        # self.comments_dir = os.path.join(dir, keyword, 'comments', self.id + '.csv')
        # self.comments = self.get_comments(self.comments_dir)

        self.reposts_dir = os.path.join(dir, keyword, 'repost', self.id + '.csv')
        self.reposts = self.get_reposts(self.reposts_dir)

    def get_comments(self, filename):
        return []

    def get_reposts(self, filename):
        results = []
        if os.path.exists(filename):
            csv_file = open(filename, 'r')
            df = pd.read_csv(csv_file).fillna('')
            for i in range(len(df)):
                results.append(Repost(df.iloc[i]))
        return results

    def get_all_repost_text(self):
        return ' '.join([item.content for item in self.reposts])

    def _replace_url(self, text):
        result = re.search(URL_PATTERN, text)
        while result:
            text = text.replace(result.group(0), URL_MASK)
            result = re.match(URL_PATTERN, text)
        return text

class AbstractInteraction:
    '''Reposts and comments are both interactions :)'''
    def __init__(self, info):
        self.username = info[1]
        self.userID = info[2]
        self.content = self.cleanup(info[3]) #'' if str(info[3]) in ('nan', 'repost', '转发微博') else info[3]
        self.n_like = int(info[4])
        self.timestamp = info[5]
        if type(info[6]) != str:
            self.previous_user = []
        else:
            self.previous_users = info[6].split(',')

    def cleanup(self, repost_text):
        ir = ['nan','repost','转发','微博','轉發']
        for item in ir:
            repost_text = repost_text.replace(item, '')
        return repost_text

class Repost(AbstractInteraction):
    def __init__(self, info):
        super(Repost, self).__init__(info)

class Comment(AbstractInteraction):
    def __init__(self, info):
        super(Comment, self).__init__(info)

