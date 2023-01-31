import markovify
import pickle
import time
import MeCab
'''
with open("ojidata2.txt") as file:
    text = file.read()

text_model = markovify.NewlineText(text,state_size=2,well_formed=False) 
text_model = text_model.compile()
'''
filename = 'finalized_model.sav'
loaded_model = pickle.load(open(filename, 'rb'))
input = "お早う"
wakati = MeCab.Tagger('-Owakati')
result = wakati.parse(input).rstrip().split(" ")
start = result[-1]
sentence = loaded_model.make_sentence_with_start(beginning=start, strict=False)
sentence = sentence.replace(" ","")
input = result[:-1]
input="".join(input)
print(input+sentence)