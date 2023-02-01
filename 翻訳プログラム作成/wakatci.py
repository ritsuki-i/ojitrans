#おじさん構文データを分かち書きする

import MeCab

tagger = MeCab.Tagger()  
wakati = MeCab.Tagger('-Owakati')
with open('ojidata.txt') as f:
    lines = f.readlines()
    f.close()
    f = open('ojidata.txt', 'a')
    f.truncate(0)
    for oji in lines:
        result = tagger.parse(oji)
        wakati = MeCab.Tagger('-Owakati')
        result = wakati.parse(oji)
        f.write(result)
f.close()

print("finish")
