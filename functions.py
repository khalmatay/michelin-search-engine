import pandas as pd
import re
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords


def clener_pipeline(querry):
    stop_words = set(stopwords.words("english"))
    stemmer = PorterStemmer()
    querry = re.sub(r"[^a-zA-Z0-9]", " ", querry)
    querry = re.sub(r" +", " ", querry)
    querry = querry.lower()
    querry = [word.strip() for word in querry.split(" ") if word.lower() not in stop_words]
    processed_querry = [stemmer.stem(word) for word in querry]
    return processed_querry

def description_cleaner(descriptions):
    result = []
    
    for descript in descriptions:
        stemmed_words = clener_pipeline(descript)
        result.append(stemmed_words)
    
    return(result)

def vocabulary_creator(descriptions):
    unique_words = set(descriptions[0])
    
    for descr in descriptions[1:]:
        unique_words = unique_words | set(descr)

    counter = 0
    res = {}
    for word in unique_words:
        if word == "": continue
        res[word] = counter
        counter += 1
    

    return word_to_id(descriptions, res, counter)

def word_to_id(descriptions, vocab, counter):
    result = []
    for one_description in descriptions:
        mono_result = []
        for word in one_description:
            if word == "" : continue
            mono_result.append(vocab[word])
        result.append(mono_result)
    
    return [result, vocab, counter]

def reverse_index_creator(ID_descriptions):
    reverse_index = {}
    for doc_id, word_ids in enumerate(ID_descriptions):
        for word_id in word_ids:
            if word_id not in reverse_index:
                reverse_index[word_id] = []
            reverse_index[word_id].append(doc_id)
    
    return reverse_index

def restourants_matcher(matching_resturants):
    matches = set(matching_resturants[0])
    for restourant in matching_resturants[1:]:
        matches &= set(restourant)
    
    return list(matches)
