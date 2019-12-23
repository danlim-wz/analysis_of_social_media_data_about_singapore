import pandas as pd
import matplotlib.pyplot as plt
from get_full_language import get_lan

data = pd.read_csv('/home/daniel/Desktop/social_media_data/singapore_tweets/filtered_singapore_tweets_1m.csv',header=None)

labels = data[data.columns[1]]

total = len(labels)
print(total)
length_map = {}
for i in labels:
    if i not in length_map:
        length_map[i] = 1
    else:
        length_map[i] += 1
    
length_map = {get_lan(k): v/total*100 for k, v in sorted(length_map.items(), key=lambda item: item[1])[::-1][:20]}
print(length_map)
plt.figure(figsize=(8,6))
plt.bar(list(length_map.keys()),list(length_map.values()))
plt.xticks(rotation='vertical')
plt.xlabel('language')
plt.ylabel('occurence(%)')
plt.title('top 20 languages used')
plt.show()

