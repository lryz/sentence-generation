from transformers import BertTokenizer, BertForMaskedLM, CamembertModel, CamembertTokenizer
from collections import defaultdict
import random
from tqdm.notebook import tqdm
import torch
import string

def load_model(model, model_name='bert'):
    try:
        if model_name.lower() == "bert":
            bert_tokenizer = BertTokenizer.from_pretrained(model)
            bert_model = BertForMaskedLM.from_pretrained(model).eval()
            return bert_tokenizer,bert_model
    except Exception as e:
        pass

def get_prediction_eos(input_text):
    try:
        input_text += ' <mask>'
        res = get_all_predictions(input_text, top_clean=int(top_k))
        return res
    except Exception as error:
        pass

    
def encode(tokenizer, text_sentence, add_special_tokens=True):
    text_sentence = text_sentence.replace('<mask>', tokenizer.mask_token)
    # if <mask> is the last token, append a "." so that models dont predict punctuation.
    input_ids = torch.tensor([tokenizer.encode(text_sentence, add_special_tokens=add_special_tokens)])
    mask_idx = torch.where(input_ids == tokenizer.mask_token_id)[1].tolist()[0]
    return input_ids, mask_idx


def decode(tokenizer, pred_idx, top_clean):
    ignore_tokens = string.punctuation + '[PAD]'
    tokens = []
    for w in pred_idx:
        token = ''.join(tokenizer.decode(w).split())
        if token not in ignore_tokens:
            tokens.append(token.replace('##', ''))
    return '\n'.join(tokens[:top_clean])

def get_all_predictions(text_sentence, top_clean=5):
    # ========================= BERT =================================
    input_ids, mask_idx = encode(bert_tokenizer, text_sentence)
    with torch.no_grad():
        predict = bert_model(input_ids)[0]
    bert = decode(bert_tokenizer, predict[0, mask_idx, :].topk(top_k).indices.tolist(), top_clean)
    return {'bert': bert}


def get_prediction_fw(input_text):
    input_text = " ".join([input_text, '<mask>'])
    res = get_all_predictions(input_text, top_clean=int(top_k))
    return res
    
def get_prediction_bw(input_text):
    input_text = " ".join(['<mask>', input_text])
    res = get_all_predictions(input_text, top_clean=int(top_k))
    return res
    
def create_sentence(input_word):
    input_text = input_word
    flag1 = True
    flag2 = True
    start = random.randint(0,1)%2
    for i in range(10):
        if flag2 == True and (i>0 or start==0): 
            test1 = get_prediction_fw(input_text)['bert'].split("\n")
            if len(test1)>0:
                word = random.choice(test1)
                if (len(word)>1 or (word=="a" or word=="A") and (not word.isnumeric())):
                    input_text = " ".join([input_text, word])
            if (word != "" and word[0]=="."):
                flag2 == False
        if flag1 == True and (i>0 or start==1):
            test2 = get_prediction_bw(input_text)['bert'].split("\n")
            if len(test2)>0:
                word = random.choice(test2)
                if (len(word)>1 or (word=="a" or word=="A") and (not word.isnumeric())):
                    input_text = " ".join([word, input_text])
            if (word != "" and word[0].isupper()):
                flag1 = False
    if input_text.find(input_word) != 0 :
        return "".join([input_text[0].capitalize(), input_text[1:], "."])
    else :
        return "".join([input_text[0], input_text[1:], "."])
    
    
def bert_create_all_sentences(model, synDict):
    global top_k
    global bert_model
    global bert_tokenizer
    top_k = 5
    
    bert_tokenizer,bert_model = load_model(model)
    finalDict = defaultdict(dict)
    with tqdm(total=len(synDict)) as pbar :
        for cui in synDict:
            for word in synDict[cui]:
                if not (word.isnumeric()) :
                    finalDict[cui][word] = create_sentence(word)
            pbar.update(1)
    return finalDict


def camembert_create_all_sentences(model, synDict):
    global top_k
    global bert_model
    global bert_tokenizer
    top_k = 5
    
    bert_model = CamembertModel.from_pretrained(model)
    bert_tokenizer = CamembertTokenizer.from_pretrained(model)
    finalDict = defaultdict(dict)
    with tqdm(total=len(synDict)) as pbar :
        for cui in synDict:
            for word in synDict[cui]:
                if not (word.isnumeric()) :
                    finalDict[cui][word] = create_sentence(word)
            pbar.update(1)
    return finalDict