import torch
from pytorch_pretrained_bert import BertTokenizer, BertModel, BertForMaskedLM

#import logging
#logging.basicConfig(level=logging.INFO)

tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')

text = "[CLS] 马来西亚航空 [SEP]"
text2 = "[CLS] 法国航空 [SEP]"
tokenized_text = tokenizer.tokenize(text2)

print(tokenized_text)

indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
segments_ids = [0] * len(tokenized_text)

tokens_tensor = torch.tensor([indexed_tokens])
segments_tensors = torch.tensor([segments_ids])

model = BertModel.from_pretrained('/home/ubuntu/.pytorch_pretrained_bert/bert-base-chinese')
model.eval()

tokens_tensor = tokens_tensor.to('cuda')
segments_tensors = segments_tensors.to('cuda')
model.to('cuda')

with torch.no_grad():
    encoded_layers, _ = model(tokens_tensor, segments_tensors)
print(encoded_layers[-1][0][0])