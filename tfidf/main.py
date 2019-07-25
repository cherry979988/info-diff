import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from SubKeyExtractor import SubKeyExtractor

def segmentation(texts):
    results = []
    for item in texts:
        results.append(' '.join(jieba.cut(item)))
    return results


if __name__ == '__main__':
    texts = ["2014年3月8日00:42航班在马来西亚吉隆坡国际机场起飞，计划06:30在北京降落。01:20，航班在马来西亚和越南的交接处与胡志明管控区失去联系，且并未收到失踪飞机的求救信号。", "法国航空447号班机原定由巴西里约热内卢加利昂国际机场飞往法国巴黎戴高乐机场。2009年6月1日，该航班一架空中客车A330-203客机，格林尼治时间2009年5月30日从巴西里约热内卢起飞，飞往法国巴黎途中遭遇恶劣天气，6月1日凌晨在大西洋上空神秘失踪，乘客216人、机组成员12人无一生还。", "2018年12月6日，媒体报道，日前加拿大应美国当局要求逮捕了华为公司首席财务孟晚舟。 同日，外交部发言人耿爽主持例行记者会。"]
    document = segmentation(texts)

    ex = SubKeyExtractor()
    ex.fit(document)
    results = ex.extract(document, 10)
    print(results)