import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt

data = pd.read_csv('/home/daniel/Desktop/filtered_tweets.csv', header=None)
tweets = data[data.columns[0]]

length_map = {}

for t in tqdm(tweets):
    t = str(t).split()
    t = len(t)
    if t not in length_map:
        length_map[t] = 1
    else:
        length_map[t] += 1

length_map = {k: v for k, v in sorted(length_map.items(), key=lambda item: item[0])}
print(length_map)
plt.bar(list(length_map.keys()),list(length_map.values()))
plt.xlabel('tweet length')
plt.ylabel('occurence')
plt.show()
