from .easyScrape import reqUrl
from .test_predict import getSummary
import re
import nltk
import heapq
#importing for abstractive
from sumy.utils import get_stop_words
from sumy.nlp.stemmers import Stemmer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer as sumytoken
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer

def checkTextType(data):
    text = data
    #check if its url or text
    text_type = "text"    
    if data[0:5] == "https" or data[0:4] == "http":
        text_type = "URL"

    #this section is performed only if provided data is URL
    if text_type == "URL":
        page = reqUrl(data)
        text = ""
        for paragraph in page.find_all('p'):
            text += paragraph.text
    
    return text

def extractiveSummarizer(data):
    #checks for URL else simply returns text
    text = checkTextType(data)

    text = re.sub(r'\[[0-9]*\]',' ',text)            
    text = re.sub(r'\s+',' ',text)    
    clean_text = text.lower()
    clean_text = re.sub(r'\W',' ',clean_text)
    clean_text = re.sub(r'\d',' ',clean_text)
    clean_text = re.sub(r'\s+',' ',clean_text)
    sentences = nltk.sent_tokenize(text)
    stop_words = nltk.corpus.stopwords.words('english')

    word2count = {}  
    for word in nltk.word_tokenize(clean_text):     
        if word not in stop_words:                 
            if word not in word2count.keys():
                word2count[word]=1
            else:
                word2count[word]+=1

    for key in word2count.keys():                  
        word2count[key]=word2count[key]/max(word2count.values())

    sent2score = {}
    for sentence in sentences:
        for word in nltk.word_tokenize(sentence.lower()):
            if word in word2count.keys():
                if len(sentence.split(' '))<30:
                    if sentence not in sent2score.keys():
                        sent2score[sentence]=word2count[word]
                    else:
                        sent2score[sentence]+=word2count[word]


    best_sentences = heapq.nlargest(20,sent2score,key=sent2score.get)
    result = []
    for sentences in best_sentences:
        result.append(sentences)

    return result

def abstractiveSummarizer(data):
    LANGUAGE = "english"

    #checks for URL else simply returns text
    text = checkTextType(data)
    
    SENTENCES_COUNT = 2
    parser = PlaintextParser.from_string((text), sumytoken(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    def lexrank_summarizer():
        summarizer_LexRank = LexRankSummarizer(stemmer)
        summarizer_LexRank.stop_words = get_stop_words(LANGUAGE)
        shortText = []
        for sentence in summarizer_LexRank(parser.document, SENTENCES_COUNT):
             shortText.append(str(sentence))
        return shortText
            
    def lsa_summarizer():
        summarizer_lsa = Summarizer(stemmer)
        summarizer_lsa.stop_words = get_stop_words(LANGUAGE)
        shortText = []
        for sentence in summarizer_lsa(parser.document, SENTENCES_COUNT-1):
            shortText.append(str(sentence))
        return shortText
    #----Call above functions to get short summaries, they will be returned as a list
    temp1 = lexrank_summarizer()
    temp2 = lsa_summarizer()
    for data in temp2:
        if data not in temp1:
            temp1.append(data)
    shortText = ''
    for sentence in temp1:
        shortText += sentence
    result = getSummary(shortText)
    # return final summary
    return result
