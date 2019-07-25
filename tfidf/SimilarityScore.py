import torch
import numpy as np
from SentEmbed import SentEmbed

class SimilarityScore:

    def __init__(self, topn=5):
        self.embedder = SentEmbed({'cuda': True})
        self.cos = torch.nn.CosineSimilarity(dim=0, eps=1e-6)
        self.topn = topn

    def score(self, text1, text1_keys, text1_repost_keys, text2, text2_keys, text2_repost_keys):
        # print(text1, text1_keys, text1_repost_keys, text2, text2_keys, text2_repost_keys)
        sim1 = self.embedder.get_similarity(text1, text2)

        text1_keys_emb = [self.embedder.get_emb(item) for item in text1_keys]
        text1_repost_keys_emb = [self.embedder.get_emb(item) for item in  text1_repost_keys]

        text2_keys_emb = [self.embedder.get_emb(item) for item in text2_keys]
        text2_repost_keys_emb = [self.embedder.get_emb(item) for item in  text2_repost_keys]

        key_sim = self._ave_cos_similarity(text1_keys_emb, text2_keys_emb)
        key_sim_cross12 = self._ave_cos_similarity(text1_keys_emb, text2_repost_keys_emb)
        key_sim_cross21 = self._ave_cos_similarity(text2_keys_emb, text1_repost_keys_emb)

        print(sim1, key_sim, key_sim_cross12, key_sim_cross21)
        return 0

    def _ave_cos_similarity(self, emb_list1, emb_list2):
        result = []
        for i in range(len(emb_list1)):
            for j in range(len(emb_list2)):
                result.append(self.cos(emb_list1[i], emb_list2[j]).item())

        np.sort(result)
        return np.mean(result[:self.topn])


