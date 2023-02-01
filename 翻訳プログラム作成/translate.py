from flask import Flask, render_template, request
from my_app import app
import pyperclip
from Data import Data
import re
import nagisa
import unicodedata
import demoji
import jaconv
from googletrans import Translator
import markovify
import pickle
import MeCab
Trans = Data()


def extract_kaomoji(text):
    """ 与えられたテキストから抽出した顔文字リストを返却する。
        → ＼(^o^)／, m(_ _)m などの 手を含む顔文字があれば、それも抽出する
    """
    results = nagisa.extract(text, extract_postags=['補助記号'])
    KAOMOJI_LEN = 5
    words = results.words
    kaomoji_words = []
    kaomoji_idx = [i for i, w in enumerate(words) if len(w) >= KAOMOJI_LEN]
    kaomoji_hands = ['ノ', 'ヽ', '∑', 'm', 'O', 'o', '┐', '/', '\\', '┌','(',')',';'] 
    # 顔文字と手を検索
    for i in kaomoji_idx:
        kaomoji = words[i] # 顔文字列
        try:
            # 顔文字の左手
            if words[i-1] in kaomoji_hands and 0 < i:
                kaomoji = words[i-1] + kaomoji
            # 顔文字の右手
            if words[i+1] in kaomoji_hands:
                 kaomoji = kaomoji + words[i+1]
        except IndexError:
            pass
        finally:
            kaomoji_words.append(kaomoji)
    return kaomoji_words

def ojija(oji):
    oji = oji.replace("❗❓","?")
    oji = oji.replace("❗","!")
    oji = oji.replace("ちゃん","")
    oji = oji.replace("チャン","")
    oji = oji.replace("ﾁｬﾝ","")
    oji = demoji.replace(string=oji, repl="。")
    oji = unicodedata.normalize('NFKC', oji) 
    for emoji in extract_kaomoji(oji):
        oji = oji.replace(emoji,"")
    count = 0
    for i in range(len(oji)):
        if oji[i] == "。":
            count += 1
            if count >=2:
                oji = oji[:i]+"嘛"+oji[i+1:]
        else:
            count=0
    oji = oji.replace("嘛","")
    oji = jaconv.kata2hira(oji)
    oji = oji.replace("かな。","?")
    oji = oji.replace("( ̄Д ̄;;^^;","")
    oji = oji.replace("( ̄Д ̄;;","")
    oji = oji.replace("(^^;; ","")
    oji = oji.replace("^^","")
    oji = oji.replace("( ̄ー ̄?)","")
    oji = oji.replace("(◎ _◎;)","")
    oji = oji.replace("(-_-;)","")
    oji = oji.replace("(笑)","")
    oji = oji.replace("(笑","")
    oji = oji.replace("笑)","")
    oji = oji.replace("(# ̄З ̄)","")
    oji = oji.replace("(^_^)","")
    oji = oji.replace("( ̄▽ ̄)","")
    oji = oji.replace("。!。","。")
    oji = oji.replace("。 。","。")
    oji = oji.replace("(;;","")
    oji = oji.replace("(^o^)","")
    oji = oji.replace("(^з<)","")
    oji = oji.replace("(・_・","")
    oji = oji.replace("( ̄Д ̄","")
    oji = oji.replace("(;;","")
    count  = 0
    for i in range(len(oji)):
        if oji[i] == "。":
            count += 1
            if count >=2:
                oji = oji[:i]+"嘛"+oji[i+1:]
        else:
            count=0
    oji = oji.replace("嘛","")
    oji = oji.replace("。 。","。")
    oji = oji.replace(";","")
    oji = oji.replace("#おじさん文章ジェネレーター","")
    oji = re.sub(r'https://[\w/:%#\$&\\(\)~\.=\+\-]+', '', oji)
    oji = re.sub(r'[-/:-@[-`{-~]', r'', oji)
    oji = re.sub(u'[■-♯]', '', oji)
    translator = Translator()
    trans_en = translator.translate(oji)
    for _ in range(2):
        oji = translator.translate(trans_en.text, dest='ja', src='en')
        trans_en = translator.translate(oji.text)
    oji = translator.translate(trans_en.text, dest='ja', src='en')
    return oji.text

def jaoji(oji,name):
    filename = 'markov_model.sav'
    oji = oji.replace("おはよう","お早う")
    oji = oji.replace("おやすみ","オヤスミ")
    oji = oji.replace("くん","")
    oji = oji.replace("ちゃん","")
    oji = oji.replace("様","")
    oji = oji.replace(name,"懿ちゃん")
    loaded_model = pickle.load(open(filename, 'rb'))
    sentence = loaded_model.make_sentence_with_start(beginning="、", strict=False).replace(' ', '')
    sentence = oji + sentence
    sentence = sentence.replace("懿",name)
    return sentence

@app.route('/')
def index():
    return render_template(
        'index.html'
    )


@app.route('/home')
def home():
    return render_template(
        'index.html'
    )
    

@app.route('/ans', methods=['GET', 'POST'])
def ans():
    Trans.sentence = request.form.get("sentence")
    Trans.name = request.form.get("name")
    Trans.name = Trans.name.replace("ちゃん","")
    Trans.name = Trans.name.replace("くん","")
    Trans.name = Trans.name.replace("様","")
    Trans.mode = request.form.get("style")
    if Trans.mode == None:
        message = "選択してください"
        return render_template(
            'index.html', sentence=Trans.sentence, name=Trans.name, message=message
        )
    elif Trans.name == "" or Trans.sentence == "":
        message = "入力してください"
        return render_template(
            'index.html', sentence=Trans.sentence, name=Trans.name, message=message
        )
    else:
        if Trans.mode == "おじさん構文→日本語":
            Trans.trans = ojija(Trans.sentence)
            Trans.twitter = "「{}」\n翻訳後→\n「{}」\n".format(Trans.sentence,Trans.trans)
            return render_template(
                'index.html', sentence=Trans.sentence, trans=Trans.trans, mode=Trans.mode, name=Trans.name, twitter=Trans.twitter
            )
        elif Trans.mode == "日本語→おじさん構文":
            Trans.trans = jaoji(Trans.sentence,Trans.name)
            Trans.twitter = "「{}」\n翻訳後→\n「{}」\n".format(Trans.sentence,Trans.trans)
            return render_template(
                'index.html', sentence=Trans.sentence, trans=Trans.trans, mode=Trans.mode, name=Trans.name, twitter=Trans.twitter
            )
    
@app.route('/copy', methods=['GET', 'POST'])
def copy():
    pyperclip.copy(Trans.trans)
    if Trans.mode == None:
        message = "選択してください"
        return render_template(
            'index.html', sentence=Trans.sentence, name=Trans.name, message=message
        )
    elif Trans.name == "" or Trans.sentence == "":
        message = "入力してください"
        return render_template(
            'index.html', sentence=Trans.sentence, name=Trans.name, message=message
        )
    else:
        return render_template(
            'index.html', sentence=Trans.sentence, trans=Trans.trans, name=Trans.name, mode=Trans.mode
        )
    
    
if __name__ == "__main__":
    app.run(debug=True)