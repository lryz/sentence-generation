from collections import defaultdict
import random
from tqdm.notebook import tqdm
from randomdict import RandomDict


def convert_dict_of_list_to_tuple(dictionary):
    for key in dictionary:
        dictionary[key] = tuple(dictionary[key])
    return dictionary


def remove_values_from_list(the_list, val):
    return [value for value in the_list if value != val]

def markov_chain(text):
    words = text.split(' ')
    fw_dict = defaultdict(list)
    bw_dict = defaultdict(list)
    
    words = remove_values_from_list(words, "")
    
    with tqdm(total=len(words)-1) as pbar: 
        for current_word, next_word in zip(words[0:-1], words[1:]):
            bw_dict[next_word].append(current_word)
            fw_dict[current_word].append(next_word)
            pbar.update(1)
            
    fw_dict = dict(fw_dict)
    bw_dict = dict(bw_dict)
    return fw_dict,bw_dict

def generate_sentence(chain_fw_tuple, chain_bw_tuple, word, banword_dict, count=15):
    count = random.randrange(10, 30)
    word_pos = random.randrange(count)
    local_word = word
    words = []
    word2 = local_word.replace('/', ' / ').replace(',', ' , ')
    word2 = word2.split(' ')
    if (word2[0] not in chain_bw_tuple) or (word2[-1] not in chain_fw_tuple):
        if (word2[0].lower() not in chain_bw_tuple) or (word2[-1].lower() not in chain_fw_tuple):
            return "Can't create a sentence with " + word
        else:
            local_word = local_word.lower()
            word2 = local_word.replace('/', ' / ').replace(',', ' , ')
            word2 = word2.split(' ')
    
    word2 = word2[0]
    for i in range(word_pos) :
        word1 = random.choice(chain_bw_tuple[word2])
        cpt=0
        """
        while ((word1 in banword_dict or word1=="\n") and (cpt<10)) :
            word1 = random.choice(chain_bw_tuple[word2])
            cpt+=1
        """
        word2 = word1
        words.append(word1)
    words.reverse()
    words.append(word)

    word1 = local_word.replace('/', ' / ').replace(',', ' , ')
    word1 = word1.split(' ')[-1]
    for i in range(count-word_pos) :
        word2 = random.choice(chain_fw_tuple[word1])
        cpt=0
        """
        while ((word2 in banword_dict or word2=='\n') and (cpt<10)) :
            word2 = random.choice(chain_bw_tuple[word1])
            cpt+=1
        """
        word1 = word2
        words.append(word2)
    if words[0]!=word :
        words[0] = words[0].capitalize()
    if words[-1]!=word :
        words.append(".")
    return " ".join(words)

def create_markov_sentences(text_dict_fw, text_dict_bw, keyDict, autocompletion = True) :   
    cpt=0

    finalDict = defaultdict(dict)

    with tqdm(total=len(keyDict.keys())) as pbar :
        for key in keyDict :
            flag1 = False
            flag2 = False
            for word in keyDict[key]:
                sentence = generate_sentence(text_dict_fw, text_dict_bw, word, keyDict)
                if sentence[0:5] != "Can't":
                    flag1 = True
                    finalDict[key][word] = sentence
                    cpt+=1
                else:
                    finalDict[key][word] = ""
                    flag2 = True
            if flag1 and autocompletion:
                if flag2:
                    for word in finalDict[key]:
                        if finalDict[key][word]!="":
                            WordToReplace = word
                            break
                    for word in finalDict[key]:
                        if finalDict[key][word]=="":
                            cpt+=1
                            finalDict[key][word] = generate_sentence(text_dict_fw, text_dict_bw, WordToReplace, keyDict)
                            finalDict[key][word] = finalDict[key][word].replace(WordToReplace, word)
            pbar.update(1)
        print(cpt, "mots ont une phrase")
    return finalDict

def postTreatment2(finalDict, category):
    key_list = list(finalDict.keys())
    with tqdm(total=len(key_list)) as pbar: 
        for notions in finalDict :
            for words in finalDict[notions] :
                if finalDict[notions][words] == "": #If no sentence was created for a specific word
                    #replace word in setence
                    while True :
                        random_key = random.choice(key_list)
                        if len(finalDict[random_key])>=1:
                            tmp_ranDict = RandomDict(finalDict[random_key])
                            wordRand = tmp_ranDict.random_key()
                            if finalDict[random_key][wordRand] != "":
                                rand_sentence = tmp_ranDict[wordRand]
                                finalDict[notions][words] = rand_sentence
                                finalDict[notions][words] = finalDict[notions][words].replace(wordRand, words)
                                ###Potentiel conflit pour plus tard vu que jsp si capitalize modifie la string ou pas
                                finalDict[notions][words] = finalDict[notions][words].replace(wordRand.capitalize(), words.capitalize())
                                break
            pbar.update(1)
    return dict(finalDict)



def markov_data_pretreatment(path):
    f = open(path, 'r') 
    data = f.read()
    data = data.replace("?","")
    data = data.replace("[","")
    data = data.replace("]","")
    data = data.replace("*","")
    data = data.replace("\n", " ")
    data = data.replace("\t", "")
    f.close()
    return data