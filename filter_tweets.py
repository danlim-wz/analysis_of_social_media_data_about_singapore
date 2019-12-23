import pandas as pd
import csv
from tqdm import tqdm
import demoji
import fasttext
import matplotlib.pyplot as plt

model = fasttext.load_model('/home/daniel/Desktop/lid.176.bin')

data = pd.read_csv('/home/daniel/Desktop/social_media_data/singapore_tweets/singapore_tweets_1m.csv',header=None)
tweets = data[data.columns[3]]
# labels = data[data.columns[0]].copy()
# labels[labels==4] = 1

print('filtering tweets')
punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~|'''
filtered = []
for sentence in tqdm(tweets):
    sentence = demoji.replace(sentence, '')
    sentence = sentence.split()
    sentence = [word for word in sentence if not word.startswith(('@', 'http', '#', '&', '+', '(', '[')) and word not in punctuations]    
    sentence = ' '.join(sentence)
    filtered.append(str(sentence))

prediction = model.predict(filtered)
labels = [i[0].split('__')[-1] for i in prediction[0]]
confidence = [i[0] for i in prediction[1]]

print('saving tweets')
with open('/home/daniel/Desktop/social_media_data/singapore_tweets/filtered_singapore_tweets_1m.csv', 'w') as d:
    writer = csv.writer(d)
    for i in tqdm(zip(filtered, labels, confidence)):
        writer.writerow(i)

htable = {}
for label in labels:
    if label not in htable:
        htable[label] = 1
    else:
        htable[label] += 1

plt.bar(list(htable.keys()),list(htable.values()))
plt.xlabel('language')
plt.ylabel('occurence')
plt.show()
