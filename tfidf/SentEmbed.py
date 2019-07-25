import torch
from pytorch_pretrained_bert import BertTokenizer, BertModel, BertForMaskedLM

class SentEmbed:
    '''A wrapper for bert model to get emb for a single sentence'''
    def __init__(self, opt):
        self.tokenizer = BertTokenizer.from_pretrained('/home/ubuntu/.pytorch_pretrained_bert/bert-base-chinese/bert-base-chinese-vocab.txt')
        self.model = BertModel.from_pretrained('/home/ubuntu/.pytorch_pretrained_bert/bert-base-chinese')
        self.cuda = opt['cuda']
        self.cos = torch.nn.CosineSimilarity(dim=0, eps=1e-6)

        if self.cuda:
            self.model.to('cuda')

    def get_emb(self, text):
        # todo: input is a list of text
        tokenized_text = self.tokenizer.tokenize(text)
        indexed_tokens = self.tokenizer.convert_tokens_to_ids(tokenized_text)
        segments_ids = [0] * len(tokenized_text)

        tokens_tensor = torch.tensor([indexed_tokens])
        segments_tensors = torch.tensor([segments_ids])

        if self.cuda:
            tokens_tensor = tokens_tensor.to('cuda')
            segments_tensors = segments_tensors.to('cuda')

        self.model.eval()

        with torch.no_grad():
            encoded_layers, _ = self.model(tokens_tensor, segments_tensors)

        return(encoded_layers[-1][0][0])

    def get_similarity(self, sent1, sent2):
        s1_emb = self.get_emb(sent1)
        s2_emb = self.get_emb(sent2)
        return self.cos(s1_emb, s2_emb).item()
