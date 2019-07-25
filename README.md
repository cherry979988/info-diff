# General Information

## Requirements

```
pip3 install -r requirements.txt
```

## Dataset

Link: https://pan.baidu.com/s/1c0xrCLdIwMZK8966ClxRfw

Passwd: 43t2

Dataset loading could be slow (a few minutes) when running train.py.

## Overall Usage
Please refer to argparse part in train.py for details.
```
usage: train.py [-h] [--cuda CUDA] [--model MODEL] [--data_dir DATA_DIR]
                [--emb_file EMB_FILE] [--idx_dict IDX_DICT]
                [--followee_count_file FOLLOWEE_COUNT_FILE]
                [--model_save_dir MODEL_SAVE_DIR] [--save_epoch SAVE_EPOCH]
                [--hidden_dim HIDDEN_DIM] [--num_layers NUM_LAYERS]
                [--dropout DROPOUT] [--penalty_coeff PENALTY_COEFF]
                [--num_epoch NUM_EPOCH] [--log_step LOG_STEP]
                [--window_size WINDOW_SIZE] [--no_extra_linear]
                [--use_extra_linear] [--train_emb] [--fix_emb]
                [--patience PATIENCE] [--lr_decay LR_DECAY] [--lr LR]
                [--max_grad_norm MAX_GRAD_NORM] [--emb_dim EMB_DIM]
                [--batch_size BATCH_SIZE] [--seed SEED]
```

# InfoLSTM Model

## Train
```
# Example Usage
python3 train.py --model InfoLSTM --lr 1 --dropout 0.1 --model_save_dir ./data/saved_model/InfoLSTM-final-1 --seed 1
```
## Test
You should be fine by simply replacing 'train.py' with 'dev.py' or 'test.py'. The same goes with the examples below.

```
python3 test.py --model InfoLSTM --lr 1--dropout 0.1 --model_save_dir ./data/saved_model/InfoLSTM-final-1 --seed 1
```

# Clash Enhanced Model
```
python3 train.py --model Clash_Enhanced --lr 0.001 --model_save_dir ./data/saved_model/Clash_Enhanced-fixed-emb-1 --hidden_dim 64 --seed 1
```

# Clash Original
```
python3 train.py --model Clash --lr 1 --model_save_dir ./data/saved_model/Clash-final-lr1-1 --emb_dim 256 --seed 1
```

# IP Model
```
python3 ip_model.py 
```