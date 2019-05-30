import numpy as np
import torch
from torch import nn
from torch.nn import init
import torch.nn.functional as F
from utils import project_utils, constant
import pickle
from loader import EmbLoader

class ModelWrapper(object):
    def __init__(self, opt, weibo2embid=None, retw_dict=None, eva=False):
        self.opt = opt

        if opt['model'] == 'InfoLSTM':
            assert weibo2embid is not None
            self.model = InfoLSTM(opt, weibo2embid)
            self.criterion = nn.MSELoss()
            if opt['cuda']:
                self.criterion.cuda()
        elif opt['model'] == 'Clash':
            assert retw_dict is not None or eva
            self.model = Clash(opt, weibo2embid, retw_dict)
            self.criterion = self.model.criterion
        elif opt['model'] == 'Clash_Enhanced':
            assert retw_dict is not None or eva
            self.model = Clash_Enhanced(opt, weibo2embid, retw_dict)
            self.criterion = self.model.criterion
        else:
            print('Invalid Model Name')
            raise(NameError)

        if opt['cuda']:
            self.model.cuda()
            # self.criterion.cuda()
        if opt['model'] != 'eva':
            self.parameters = [p for p in self.model.parameters() if p.requires_grad]
            for i, param in enumerate(self.parameters):
                print('Param #{}: {}'.format(i, param.shape))
            self.optimizer = torch.optim.SGD(self.parameters, lr=opt['lr'])
            self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, 'max',
                                                                        patience=opt['patience'], factor=opt['lr_decay'])

    def update(self, batch):
        if self.opt['cuda']:
            inputs = [b.cuda() for b in batch[:-2]]
            labels = batch[-1].cuda()
            # torch.cuda.empty_cache()
        else:
            inputs = [b for b in batch[:-2]]
            labels = batch[-1]

        self.model.train()
        self.optimizer.zero_grad()
        prob, _ = self.model(inputs)
        loss = self.criterion(prob.view(-1), labels.float()) # 合理吗？

        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.opt['max_grad_norm'])
        self.optimizer.step()
        loss_val = loss.data.item()
        return loss_val

    def predict(self, batch, unsort=True, thres=0.5):
        if self.opt['cuda']:
            inputs = [b.cuda() for b in batch[:-2]]
            labels = batch[-1].cuda()
        else:
            inputs = [b for b in batch[:-2]]
            labels = batch[-1]

        orig_idx = batch[-2]

        self.model.eval()
        prob, _  = self.model(inputs)
        loss = self.criterion(prob.view(-1), labels.float())

        predictions = list(map(int, prob.data.cpu().numpy() > thres))

        if unsort:
            _, predictions = [list(t) for t in zip(*sorted(zip(orig_idx, predictions)))]
            _, prob = [list(t) for t in zip(*sorted(zip(orig_idx, prob)))]


        return predictions, torch.stack(prob).flatten().data.cpu().numpy().tolist(), loss.data.item()


    def save(self, filename, epoch):
        params = {
            'model': self.model.state_dict(),
            'config': self.opt,
            'epoch': epoch
        }
        try:
            torch.save(params, filename)
            print('model saved to {}'.format(filename))
        except BaseException:
            print('Saving failed... Continuing...')

    def load(self, filename):
        try:
            checkpoint = torch.load(filename)
        except BaseException as e:
            print('Cannot load model from {}'.format(filename))
            print(e.args)
            exit()
        self.model.load_state_dict(checkpoint['model'])
        self.opt = checkpoint['config']

class InfoLSTM(nn.Module):
    def __init__(self, opt, weibo2embid=None):
        super(InfoLSTM, self).__init__()

        emb = pickle.load(open(opt['emb_file'], 'rb'))

        self.drop = nn.Dropout(opt['dropout'])
        opt['emb_size'] = len(weibo2embid) + 1 # have 0 as unknown weiboid
        self.emb = nn.Embedding(opt['emb_size'], opt['emb_dim'], padding_idx=constant.PAD_ID)
        self.emb.weight.requires_grad = False

        input_size = opt['emb_dim']
        self.rnn = nn.LSTM(input_size, opt['hidden_dim'], opt['num_layers'],
                           batch_first=True, dropout=opt['dropout'])
        self.linear = nn.Linear(opt['hidden_dim'], 1)

        self.opt = opt
        self.use_cuda = opt['cuda']

        # self.emb_matrix = emb_matrix
        self.weibo2embid = weibo2embid

        self.emb_matrix = EmbLoader(emb, weibo2embid, opt)
        self.init_weights()

    def init_weights(self):
        if self.emb_matrix is None:
            self.emb.weight.data[1:, :].uniform_(-1.0, 1.0)  # keep padding dimension to be 0
        else:
            self.emb_matrix = torch.from_numpy(self.emb_matrix)
            self.emb.weight.data.copy_(self.emb_matrix)

    def zero_state(self, batch_size):
        state_shape = (self.opt['num_layers'], batch_size, self.opt['hidden_dim'])
        h0 = c0 = torch.zeros(*state_shape, requires_grad=False)
        if self.use_cuda:
            return h0.cuda(), c0.cuda()
        else:
            return h0, c0

    def forward(self, inputs):
        user, seen, seen_users, decision = inputs
        masks = torch.eq(seen, 0)
        seq_lens = list(masks.data.eq(constant.PAD_ID).long().sum(1).squeeze())
        batch_size = seen.size()[0]

        vecs = self.emb(seen)
        # 以后可能还要加别的
        inputs = vecs

        h0, c0 = self.zero_state(batch_size)
        inputs = nn.utils.rnn.pack_padded_sequence(inputs, seq_lens, batch_first=True)
        outputs, (ht, ct) = self.rnn(inputs, (h0, c0))
        outputs, output_lens = nn.utils.rnn.pad_packed_sequence(outputs, batch_first=True)

        hidden = self.drop(ht[-1, :, :])
        outputs = self.drop(outputs)

        # 以后可能还要加别的
        final_hidden = hidden

        logits = self.linear(final_hidden)
        return torch.sigmoid(logits), final_hidden

class IPModel(nn.Module):
    def __init__(self, retw_dict, opt):
        super(IPModel, self).__init__()
        self.retw_dict = retw_dict

    def forward(self, batch):
        inputs = [b for b in batch[:-2]]

        user, seen, seen_users, decision = inputs
        results = list(map(lambda x: project_utils.safe_retrieve(self.retw_dict, x.item(), 0), decision))
        return np.array(results)

    def predict(self, inputs, unsort=True, thres=0.5):
        prob = self.forward(inputs)
        predictions = list(map(int, prob > thres))

        orig_idx = inputs[-2]
        if unsort:
            _, predictions = [list(t) for t in zip(*sorted(zip(orig_idx, predictions)))]
            _, prob = [list(t) for t in zip(*sorted(zip(orig_idx, prob)))]

        return predictions, prob

class Clash(nn.Module):
    def __init__(self, opt, weibo2embid, retw_dict):
        super(Clash, self).__init__()
        opt['emb_size'] = len(weibo2embid) + 1
        self.opt = opt
        self.weibo2embid = weibo2embid
        self.retw_dict = retw_dict

        self.emb = nn.Embedding(opt['emb_size'], opt['emb_dim'], padding_idx=constant.PAD_ID)
        self.emb_bias = nn.Embedding(opt['emb_size'], 1, padding_idx=constant.PAD_ID)
        self.blinear = nn.Bilinear(opt['emb_dim'], opt['emb_dim'], 1, bias=False)
        self.criterion0 = nn.MSELoss()
        self.init_weights()

        if opt['cuda']:
            self.criterion0.cuda()

    def init_weights(self):
        self.emb.weight.data.uniform_(0, 0.01)
        self.blinear.weight.data.uniform_(0, 0.01)

        if self.retw_dict is not None:
            self.retw_dict[constant.PAD_ID] = 1e-10
            bias = np.array([project_utils.safe_retrieve(self.retw_dict, k, 1e-10)
                             for k in range(self.opt['emb_size'])])
            self.emb_bias_vec = torch.from_numpy(bias).view(-1, 1)
            self.emb_bias.weight.data.copy_(self.emb_bias_vec)
            self.emb_bias.weight.requires_grad = False

    def criterion(self, probs, labels):
        c1 = self.criterion0(probs, labels)
        c2 = project_utils.prob_penalty(probs)
        lam = self.opt['penalty_coeff']
        return c1 + lam * c2

    def get_probs(self, seen, decision):
        emb1 = self.emb(seen)
        emb2 = self.emb(decision)
        t = self.blinear(emb1, emb2)#.flatten()
        #t = torch.matmul(torch.matmul(emb1, self.mat_clust), emb2).diag()
        bias = self.emb_bias(decision)#.flatten()
        return project_utils.prob_clip(t + bias)

    def forward(self, inputs):
        user, seen, seen_users, decision = inputs
        seen_flatten = seen.view(-1)
        decision_flatten = decision.repeat(self.opt['window_size'], 1).t().flatten()
        assert len(seen_flatten) == len(decision_flatten)
        log_bias = torch.log(self.emb_bias(decision)).flatten()
        probs = self.get_probs(seen_flatten, decision_flatten).view(-1, self.opt['window_size'])
        log_probs = torch.log(probs).sum(dim=1) \
                    - (self.opt['window_size'] - 1) * log_bias
        return project_utils.prob_clip(torch.exp(log_probs)), None


class Clash_Enhanced(nn.Module):
    def __init__(self, opt, weibo2embid, retw_dict):
        super(Clash_Enhanced, self).__init__()
        opt['emb_size'] = len(weibo2embid) + 1
        self.opt = opt
        self.weibo2embid = weibo2embid
        self.retw_dict = retw_dict

        self.emb = nn.Embedding(opt['emb_size'], opt['emb_dim'], padding_idx=constant.PAD_ID)
        self.emb_bias = nn.Embedding(opt['emb_size'], 1, padding_idx=constant.PAD_ID)
        if opt['use_extra_linear']:
            self.linear = nn.Linear(opt['emb_dim'], opt['hidden_dim'])
        else:
            opt['hidden_dim'] = opt['emb_dim']
        self.blinear = nn.Bilinear(opt['hidden_dim'], opt['hidden_dim'], 1, bias=False)
        self.criterion0 = nn.MSELoss()

        emb = pickle.load(open(opt['emb_file'], 'rb'))
        self.emb_matrix = EmbLoader(emb, weibo2embid, opt)
        self.init_weights()

        if opt['cuda']:
            self.criterion0.cuda()

    def init_weights(self):
        self.blinear.weight.data.uniform_(0, 0.01)
        if self.opt['use_extra_linear']:
            self.linear.weight.data.uniform_(0, 0.01)
            self.linear.bias.data.uniform_(0, 0.01)

        if self.emb_matrix is None:
            self.emb.weight.data.zero_()
        else:
            self.emb_matrix = torch.from_numpy(self.emb_matrix)
            self.emb.weight.data.copy_(self.emb_matrix)
            # self.emb.weight.requires_grad = False

        if self.retw_dict is not None:
            self.retw_dict[constant.PAD_ID] = 1e-10
            bias = np.array([project_utils.safe_retrieve(self.retw_dict, k, 1e-10)
                             for k in range(self.opt['emb_size'])])
            self.emb_bias_vec = torch.from_numpy(bias).view(-1, 1)
            self.emb_bias.weight.data.copy_(self.emb_bias_vec)
            self.emb_bias.weight.requires_grad = False


    def criterion(self, probs, labels):
        c1 = self.criterion0(probs, labels)
        c2 = project_utils.prob_penalty(probs)
        lam = self.opt['penalty_coeff']
        return c1 + lam * c2

    def get_probs(self, seen, decision):
        emb1 = self.emb(seen)
        emb2 = self.emb(decision)
        if self.opt['use_extra_linear']:
            reduced1 = self.linear(emb1)
            reduced2 = self.linear(emb2)
            t = self.blinear(reduced1, reduced2)
        else:
            t = self.blinear(emb1, emb2)

        bias = self.emb_bias(decision)
        return project_utils.prob_clip(t + bias)

    def forward(self, inputs):
        user, seen, seen_users, decision = inputs
        seen_flatten = seen.view(-1)
        decision_flatten = decision.repeat(self.opt['window_size'], 1).t().flatten()
        assert len(seen_flatten) == len(decision_flatten)
        log_bias = torch.log(self.emb_bias(decision)).flatten()
        probs = self.get_probs(seen_flatten, decision_flatten).view(-1, self.opt['window_size'])
        log_probs = torch.log(probs).sum(dim=1) \
                    - (self.opt['window_size'] - 1) * log_bias
        return project_utils.prob_clip(torch.exp(log_probs)), None