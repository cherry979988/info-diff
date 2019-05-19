import argparse
from Keyword import Keyword
from SubKeyExtractor import SubKeyExtractor
from Segmentation import Segmentation
from SimilarityScore import SimilarityScore

parser = argparse.ArgumentParser()
parser.add_argument('--data_dir', type=str, default='./data')
parser.add_argument('--keyword1', type=str, default='孟晚舟')
parser.add_argument('--keyword2', type=str, default='加拿大前外交官')
args = parser.parse_args()
opt = vars(args)

def main(opt):

    k1 = Keyword(opt['keyword1'],opt['data_dir'])
    text1 = k1.get_all_context_text()
    text1_repost = k1.get_all_repost_text()

    k2 = Keyword(opt['keyword2'],opt['data_dir'])
    text2 = k2.get_all_context_text()
    text2_repost = k2.get_all_repost_text()

    seg = Segmentation()
    document = seg.segmentation([text1, text2, text1_repost, text2_repost])

    ex = SubKeyExtractor()
    ex.fit(document)
    results = ex.extract(document, 20)

    print(results)

    scorer = SimilarityScore(topn=20)
    score = scorer.score(
        k1.get_top_context_text(),
        results[0],
        results[2],
        k2.get_top_context_text(),
        results[1],
        results[3]
    )

    print(score)

    print('done')

if __name__ == "__main__":
    main(opt)