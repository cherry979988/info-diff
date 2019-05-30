from utils.metrics import metrics
import torch

def safe_retrieve(dict, key, default=0):
    if key in dict:
        return dict[key]
    else:
        return default

def prob_penalty(probs):
    '''
    to make sure probability is in [0,1], a punishment term is added to loss function
    '''
    mask = (probs > 1) + (probs < 0) # by default, requires_grad = False
    mask = mask.float()
    penalty = probs * (probs - 1)
    return torch.sum(mask * penalty)

def prob_clip(t):
    ones = torch.ones_like(t)
    zeros = torch.ones_like(t) * 1e-10
    return torch.max(torch.min(t, ones), zeros)