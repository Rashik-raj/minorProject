from wordcloud import WordCloud,STOPWORDS
from .easyScrape import reqUrl
from PIL import Image
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
import matplotlib.pyplot as plt
import numpy as np
import os

mask_img = 'static/img/cloud.png'
masked_img = 'static/img/wordcloud.png'
masked_img_summary = 'static/img/wordcloud_summary.png'
input_graph = 'static/img/graph.png'
summary_graph = 'static/img/summary_graph.png'

def generateWordcloud(img,text,max):
    mask = np.array(Image.open(mask_img))
    stopwords = set(STOPWORDS)
    wc = WordCloud(mask=mask, max_words=max, background_color="white", stopwords=stopwords)
    wc.generate(text)
    #if the file exists remove it
    if os.path.exists(img):
        os.remove(img)

    wc.to_file(img)

def makeWordcloud(data,num=0):
    if num==0:
        generateWordcloud(masked_img,data,200)
    else:
        generateWordcloud(masked_img_summary,data,20)

def makeGraph(data,num=0):
    text = data.lower()
    stop_words = set(STOPWORDS)
    #remove punctuation
    tokenizer = RegexpTokenizer(r'\w+')
    input_words = tokenizer.tokenize(text)    
    #filter stopwords
    filtered_input_words = [w for w in input_words if not w in stop_words] 

    unique_words = list(set(filtered_input_words))

    collection_unique_words = []
    for each_word in unique_words:
        c = filtered_input_words.count(each_word)
        collection_unique_words.append([each_word,c])    
    #sort by 2nd item in a 2D list
    collection_unique_words.sort(key = lambda x: x[1],reverse=True)

    x_axis = [each_data[0] for each_data in collection_unique_words[0:20]]
    y_axis = [each_data[1] for each_data in collection_unique_words[0:20]]
    plt.barh(x_axis,y_axis)
    plt.xlabel('frequency')
    plt.ylabel('words')
    if num==0:
        plt.title('input text word frequency graph')
        plt.savefig(input_graph)
    else:
        plt.title('summary word frequency graph')
        plt.savefig(summary_graph)
    plt.clf()