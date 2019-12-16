import pandas as pd
import csv
from tqdm import tqdm

data = pd.read_csv('/home/daniel/Desktop/tw.csv', encoding='ISO 8859-1', header=None)
tweets = data[data.columns[5]]
labels = data[data.columns[0]].copy()
labels[labels==4] = 1

filtered = []
for t in tqdm(tweets):
    t = t.split()
    t = [i for i in t if not i.startswith(('@', 'http'))]    
    t = ' '.join(t)
    filtered.append(str(t))

with open('/home/daniel/Desktop/filtered_tweets.csv', 'w') as d:
    writer = csv.writer(d)
    for i in zip(filtered, labels):
        writer.writerow(i)
