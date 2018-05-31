from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from glove import Corpus,Glove
from glove.glove import check_random_state

from utils import (build_coocurrence_matrix,
                   generate_training_corpus)
import heapq
import numpy as np
from Hcluster import hcluster
import pickle

# real realwords(train)
def readRealWordsTrain():
    with open("corpusRealCut.txt", 'rb') as savefile:    
        corpusreal = pickle.load(savefile)
    return corpusreal

# real realwords(test)
def readRealWordsTest():
    corpus = []
    for i in range(120,150):
        if (i % 3 == 0):
            f = open("corpreal/bd"+ str(i//3)+"f.txt", 'r',encoding= 'utf-8')
        elif (i % 3 == 1):
            f = open("corpreal/mm" + str(i//3) + "f.txt", 'r', encoding='utf-8')
        else :
            f = open("corpreal/zjw" + str(i//3) + "f.txt", 'r', encoding='utf-8')
        tmp = f.read()
        corpus.append(tmp)
    return corpus

# tfidf, weight[i][j] is the tfidf of the $j$th word in $i$th doc
def tfidf(corpus):
    vectorizer = CountVectorizer()    
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(vectorizer.fit_transform(corpus)) 
    word = vectorizer.get_feature_names() #all key words
    weight = tfidf.toarray() #corresponding word weight
    #print(len(weight)), the doc number
    #print(len(weight[0])), the vocabulary number
    topn = 40
    topwords,topindex = findTopNWords(word,weight,topn)
    # save the trained tfidf model
    with open("tfidf_vecto.txt", 'wb') as savefile:    
        pickle.dump(vectorizer,savefile)
    with open("ifidf_transf.txt", 'wb') as savefile:    
        pickle.dump(transformer,savefile)
    return topwords,topindex
    
def testtfidf(corpus):
    with open("tfidf_vecto.txt", 'rb') as savefile:    
        vectorizer = pickle.load(savefile)
    with open("ifidf_transf.txt", 'rb') as savefile:    
        transformer = pickle.load(savefile)
    tfidf = transformer.transform(vectorizer.transform(corpus)) 
    word = vectorizer.get_feature_names() #all key words
    weight = tfidf.toarray() #corresponding word weight
    print(len(weight))
    print(len(weight[0]))
    print(len(word))
    topn = 40
    topwords,topindex = findTopNWords(word,weight,topn)
    # save the trained tfidf model
    
    return topwords,topindex


# find the top n words in a doc 
# topnWords is the $j$th most important word in $i$th doc (tfidf evaluation)
# topTfIdf is the corresponding ifidf
def findTopNWords(word,weight,topn):
    topnWords = []
    topnTfIdf = []
    for i in range(len(weight)):
        tmp1 = []
        tmp2 = []
        # tmp(length:topn) is the sequence of topn words 
        tmp = heapq.nlargest(topn, range(len(weight[i])), weight[i].__getitem__)
        for j in range(topn):
            tmp1.append(word[tmp[j]])
            tmp2.append(weight[i][tmp[j]])
        topnWords.append(tmp1)
        topnTfIdf.append(tmp2)
    return topnWords,topnTfIdf

# Compute the softmax of vector x
def softmax(x):
    exp_x = np.exp(x)
    softmax_x = exp_x / np.sum(exp_x)
    return list(softmax_x) 

# use the softmax of tfidf as weight
# sum the vector of top words generated by GloVe 
# wvec is the topword list
# ivec is the topword tfidf 
def getDociVec(glomodel,wvec,ivec):
    softivec = softmax(ivec)
    wordembed = []
    for i in range(len(wvec)):
        try:
            word_idx = glomodel.dictionary[wvec[i]]# the index of word
            embed = glomodel.word_vectors[word_idx]# the embed of word
            wordembed.append(embed)
        except:
            wordembed.append(len(glomodel.word_vectors[0])*[0])
    docvec = len(wordembed[0])*[0]
    for i in range(len(wvec)):
        for j in range(len(wordembed[i])):
            docvec[j] += softivec[i] * wordembed[i][j]
    return docvec    

def Doc_cluster(outcome):
    # print the topic distribution of essays
    label = []
    for n in range(len(outcome)):
        label.append(outcome[n])

    k, l = hcluster(outcome, 20)
    print(l)
    for subl in l:
        subl.sort()
    for i in range(len(l)):
        if len(l[i]) >= 1:
            for j in range(len(l[i])):
                print("doc: {}".format( l[i][j] ))
                #print("type: {} doc: {} topic: {}".format( (l[i][j] % 3),l[i][j], label[l[i][j]]))
        print('\n')

if __name__ == "__main__":
    tag = 1
    glomodel = Glove.load('gloveSave.txt')
    if tag:
        corpus = readRealWordsTrain()
        topwords,topindex = tfidf(corpus)
        docvecs = [] # list for doc embeddings
        for i in range(len(corpus)):
            docvecs.append(getDociVec(glomodel,topwords[i],topindex[i]))
        with open("realVecTrain.txt", 'wb') as savefile:    
            pickle.dump(docvecs,savefile)
    else:
        with open("realVecTrain.txt", 'rb') as savefile:    
            docvecs = pickle.load(savefile)
    # module for test
    '''testcorpus = readRealWordsTest()
    testtopwords,testtopindex = testtfidf(testcorpus)
    for i in range(len(testcorpus)):
        docvecs.append(getDociVec(glomodel,testtopwords[i],testtopindex[i]))'''
    

    with open("realVec.txt", 'wb') as savefile:    
        pickle.dump(docvecs,savefile)
    #docvecs = np.array(docvecs)
    
    print(len(docvecs))
    #print(type(docvecs[0]))
    #print(docvecs[119:121])
    
    #Doc_cluster(docvecs)
     
    
    





