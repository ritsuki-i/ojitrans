#マルコフ連鎖のモデル作成&モデルファイル保存

import markovify
import pickle

with open("ojidata2.txt") as file:
    text = file.read()

text_model = markovify.NewlineText(text,state_size=2,well_formed=False) 
text_model = text_model.compile()
filename = 'markov_model.sav'
pickle.dump(text_model,open(filename,'wb'))
print("finish")