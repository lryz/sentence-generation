
from collections import defaultdict

def create_simple_sentences(synDict, styDict):
    finalDict = defaultdict(dict)
    for cui in synDict :
        for word in synDict[cui]:
            sentence = " ".join(["The concept of", word, "is about"])
            for group in styDict[cui]:
                sentence = " ".join([sentence, group, "and"])
            sentence = sentence.rsplit(' ', 1)[0]
            finalDict[cui][word] = sentence
            
    return finalDict


def create_single_words(synDict):
    finalDict = defaultdict(dict)
    for cui in synDict :
        for word in synDict[cui]:
            finalDict[cui][word] = word
    return finalDict