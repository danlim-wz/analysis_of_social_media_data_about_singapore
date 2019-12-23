import fasttext
import pandas as pd

#load model, support 176 languages
model = fasttext.load_model('/home/daniel/Desktop/lid.176.bin')

to_predict = ['this is a beautiful day', '这是美好的一天', 'これは美しい日です']
prediction = model.predict(to_predict)
labels = [i[0].split('__')[-1] for i in prediction[0]]
confidence = [i[0] for i in prediction[1]]
print(labels)
print(confidence)