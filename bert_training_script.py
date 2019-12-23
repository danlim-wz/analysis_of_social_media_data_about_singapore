import torch
from pytorch_transformers import *
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler, IterableDataset
from keras.preprocessing.sequence import pad_sequences
from tqdm import tqdm, trange
import numpy as np
import os
import pandas as pd
import sklearn
import torch.nn as nn
import boto3

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#tunable parameters
MAX_LEN = 32
batch_size = 16
epochs = 4
learning_rate = 2e-5

#tokenizer and model objects
tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased', do_lower_case=False)
model = BertForSequenceClassification.from_pretrained('bert-base-multilingual-cased', num_labels=2)
if torch.cuda.device_count() > 1:
    model = nn.DataParallel(model)
model.eval().to(device)
# model.to(device)

#import data
print('Importing data')
data = pd.read_csv('/home/daniel/Desktop/social_media_data/training_tweets/filtered_tweets_1_6m.csv',header=None)
# data = pd.read_csv('s3://s3-bucket-for-twitter-analysis/training/filtered_tweets_1_6m.csv',header=None)
data = sklearn.utils.shuffle(data)
tweets = list(data[data.columns[0]])
labels = data[data.columns[1]]
labels = list(labels)

#split into train/validation sets
split = int(0.8*len(data))
train_data = tweets[:split]
train_label = labels[:split]
validation_data = tweets[split:]
validation_label = labels[split:]


class Iterate_Dataset(IterableDataset):

    def __init__(self, data, labels):
        self.data = data
        self.labels = labels
    
    def process_data(self, data, labels):
        for words, l in zip(data, labels):
            words = "[CLS] "+ str(words) +" [SEP]"
            words = tokenizer.tokenize(words)
            words = pad_sequences([tokenizer.convert_tokens_to_ids(words)],
                        maxlen=MAX_LEN, dtype="long", truncating="post", padding="post")
            for w in words:
                if w[MAX_LEN-1] != 0:
                    w[MAX_LEN-1] = 102
            mask = words.copy()
            mask[mask>0] = 1
            yield words[0], mask[0], l

    # def get_stream(self, data, labels):
    #     return self.process_data(data, labels)

    def __iter__(self):
        return self.process_data(self.data, self.labels)


tloader = Iterate_Dataset(train_data,train_label)
train_dataloader = DataLoader(tloader, batch_size=batch_size, num_workers=0)
vloader = Iterate_Dataset(validation_data,validation_label)
validation_dataloader = DataLoader(vloader, batch_size=batch_size, num_workers=0)

#create optimizer
param_optimizer = list(model.named_parameters())
optimizer_grouped_parameters = [
    {'params': [p for n, p in param_optimizer]}
]
optimizer = AdamW(optimizer_grouped_parameters,lr=learning_rate)

#train/validation loop
best_val_acc = 0
for k in trange(epochs, desc="Epoch"):
    model.train()
    tr_loss = 0
    tr_steps = 0

    #train loop
    print('training on epoch %d'%k)
    for step, batch in enumerate(tqdm(train_dataloader)):
        batch = tuple(t.to(device) for t in batch)
        b_input, b_input_mask, b_labels = batch
        optimizer.zero_grad()
        loss, _ = model(b_input, token_type_ids=None, attention_mask=b_input_mask,
                    labels=b_labels)
        loss.backward()
        optimizer.step()
        tr_loss += loss.item()
        tr_steps += 1
    print("Training loss: {}".format(tr_loss/tr_steps))

    #validation loop
    model.eval()
    val_steps = 0
    val_acc = 0
    print('validating on epoch %d'%k)
    for batch in tqdm(validation_dataloader):
        batch = tuple(t.to(device) for t in batch)
        b_input, b_input_mask, b_labels = batch
        with torch.no_grad():
            logits = model(b_input, token_type_ids=None, attention_mask=b_input_mask)
        logits = [p.cpu().numpy().squeeze() for p in logits]
        label_ids = b_labels.cpu().numpy()
        logits = np.argmax(logits[0], axis=1).flatten()
        label_ids = label_ids.flatten()
        val_acc += np.sum(logits == label_ids)/len(label_ids) 
        val_steps += 1
    print("Validation Accuracy: {}".format(val_acc/val_steps))
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save(model.state_dict(),'sentiment_1_6m.pth')
    # torch.save(model, '/home/daniel/Desktop/bert.pth')
boto3.Session().resource('s3').Bucket('s3-bucket-for-twitter-analysis').Object('bert.pth').upload_file('/models/sentiment_1_6m.pth')

