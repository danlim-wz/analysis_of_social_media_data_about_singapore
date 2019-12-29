import torch
from pytorch_transformers import *
import numpy as np
import os
import pandas as pd
from keras.preprocessing.sequence import pad_sequences
from tqdm import tqdm
import matplotlib.pyplot as plt

#load model and tokenizer
# state_dict = torch.load("/home/daniel/Desktop/social_media_data/sentiment_1_6m.pth")
# model = BertForSequenceClassification.from_pretrained('bert-base-multilingual-cased',state_dict=torch.load("/home/daniel/Desktop/social_media_data/sentiment_1_6m.pth"), num_labels=2)
# model.cuda().eval()
# tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased', do_lower_case=False)

config = BertConfig()
model = BertForSequenceClassification(config)
model_state_dict = "/home/daniel/Desktop/bertweight.pth"
model.load_state_dict(torch.load(model_state_dict))
model.cuda().eval()
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)

tweets = pd.read_csv('/home/daniel/Desktop/en_tweets.csv')
tweets = tweets[tweets.columns[1]]
number_of_tweets = len(tweets)
batch_size = 1800
progress = tqdm(total = int(number_of_tweets/batch_size))
sentiment = 0

spread = {}

def create_batch():
    counter = 0
    batch = []
    for t in tweets:
        batch.append(t)
        if counter != 0 and counter % batch_size == 0 or counter == number_of_tweets -1:
            yield batch
            batch = []
        counter += 1

for b in create_batch():
    progress.update(1)
    token_text = []
    for tweet in b:
        tweet = "[CLS] " + tweet + " [SEP]"   
        #tokenize and slice input data
        tokenized_text = tokenizer.tokenize(tweet)
        token_text.append(tokenized_text)

    indexed_text = pad_sequences([tokenizer.convert_tokens_to_ids(text) for text in token_text],
                    maxlen=32, dtype="long", truncating="post", padding="post")

    #manually change last token to [SEP] since sentences may be longer than MAX_LEN
    for sentence in indexed_text:
        if sentence[31] != 0:
            sentence[31] = 102 #sep_index is 102

    #convert to indices and send to GPU memory
    indexed_text = torch.tensor(indexed_text).cuda()


    with torch.no_grad():
        logits = model(indexed_text)
   
    logits = [p.cpu().squeeze() for p in logits]
    softmax = torch.nn.Softmax(dim=1)
    logits = softmax(logits[0]).numpy()

    for i in logits:
        sentiment += i[1]
#         spread.append(round(i[1],4))
        i = round(i[0],3)
        if i not in spread:
            spread[i] = 1
        else:
            spread[i] += 1
progress.close()
overall_sentiment = sentiment/number_of_tweets

print(overall_sentiment)

x = list(spread.values())
y = list(spread.keys())
plt.scatter(y,x)
plt.xlabel('polarity')
plt.ylabel('occurence')
plt.show()