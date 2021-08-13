import subprocess
from collections import defaultdict
from randomdict import RandomDict
from tqdm.notebook import tqdm
import copy
import random
import glob 
import os

word_regex=r'(?:\w*[!"#$%&\'`\(\)*-.\/:;<=>?@[\]^_`{|}~]\w+)|(?:\w+[!"#$%&\'`\(\)*-.\/:;<=>?@[\]^_`{|}~]\w*)|(?:[\w+]+(?:[`\'])?)|<[?-]+>'

sty_groups = {'Activity': 'ACTI', 'Behavior': 'ACTI', 'Daily or Recreational Activity': 'ACTI', 'Event': 'ACTI', 'Governmental or Regulatory Activity': 'ACTI', 'Individual Behavior': 'ACTI','Machine Activity': 'ACTI', 'Occupational Activity': 'ACTI', 'Social Behavior': 'ACTI', 'Anatomical Structure': 'ANAT', 'Body Location or Region': 'ANAT','Body Part, Organ, or Organ Component': 'ANAT', 'Body Space or Junction': 'ANAT', 'Body Substance': 'ANAT', 'Body System': 'ANAT', 'Cell': 'ANAT', 'Cell Component': 'ANAT','Embryonic Structure': 'ANAT', 'Fully Formed Anatomical Structure': 'ANAT', 'Tissue': 'ANAT', 'Amino Acid, Peptide, or Protein': 'CHEM', 'Antibiotic': 'CHEM', 'Biologically Active Substance': 'CHEM', 'Biomedical or Dental Material': 'CHEM', 'Carbohydrate': 'CHEM', 'Chemical': 'CHEM', 'Chemical Viewed Functionally': 'CHEM','Chemical Viewed Structurally': 'CHEM', 'Clinical Drug': 'CHEM', 'Eicosanoid': 'CHEM', 'Element, Ion, or Isotope': 'CHEM', 'Enzyme': 'CHEM', 'Hazardous or Poisonous Substance': 'CHEM', 'Hormone': 'CHEM', 'Immunologic Factor': 'CHEM', 'Indicator, Reagent, or Diagnostic Aid': 'CHEM', 'Inorganic Chemical': 'CHEM', 'Lipid': 'CHEM', 'Neuroreactive Substance or Biogenic Amine': 'CHEM', 'Nucleic Acid, Nucleoside, or Nucleotide': 'CHEM', 'Organic Chemical': 'CHEM', 'Organophosphorus Compound': 'CHEM','Pharmacologic Substance': 'CHEM', 'Receptor': 'CHEM', 'Steroid': 'CHEM', 'Vitamin': 'CHEM', 'Classification': 'CONC', 'Conceptual Entity': 'CONC', 'Functional Concept': 'CONC','Group Attribute': 'CONC', 'Idea or Concept': 'CONC', 'Intellectual Product': 'CONC', 'Language': 'CONC', 'Qualitative Concept': 'CONC', 'Quantitative Concept': 'CONC','Regulation or Law': 'CONC', 'Spatial Concept': 'CONC', 'Temporal Concept': 'CONC', 'Drug Delivery Device': 'DEVI', 'Medical Device': 'DEVI', 'Research Device': 'DEVI', 'Acquired Abnormality': 'DISO', 'Anatomical Abnormality': 'DISO', 'Cell or Molecular Dysfunction': 'DISO', 'Congenital Abnormality': 'DISO', 'Disease or Syndrome': 'DISO','Experimental Model of Disease': 'DISO', 'Finding': 'DISO', 'Injury or Poisoning': 'DISO', 'Mental or Behavioral Dysfunction': 'DISO', 'Neoplastic Process': 'DISO','Pathologic Function': 'DISO', 'Sign or Symptom': 'DISO', 'Amino Acid Sequence': 'GENE', 'Carbohydrate Sequence': 'GENE', 'Gene or Genome': 'GENE', 'Molecular Sequence': 'GENE','Nucleotide Sequence': 'GENE', 'Geographic Area': 'GEOG', 'Age Group': 'LIVB', 'Amphibian': 'LIVB', 'Animal': 'LIVB', 'Archaeon': 'LIVB', 'Bacterium': 'LIVB', 'Bird': 'LIVB','Eukaryote': 'LIVB', 'Family Group': 'LIVB', 'Fish': 'LIVB', 'Fungus': 'LIVB', 'Group': 'LIVB', 'Human': 'LIVB', 'Mammal': 'LIVB', 'Organism': 'LIVB', 'Patient or Disabled Group': 'LIVB', 'Plant': 'LIVB', 'Population Group': 'LIVB', 'Professional or Occupational Group': 'LIVB', 'Reptile': 'LIVB', 'Vertebrate': 'LIVB', 'Virus': 'LIVB','Entity': 'OBJC', 'Food': 'OBJC', 'Manufactured Object': 'OBJC', 'Physical Object': 'OBJC', 'Substance': 'OBJC', 'Biomedical Occupation or Discipline': 'OCCU', 'Occupation or Discipline': 'OCCU', 'Health Care Related Organization': 'ORGA', 'Organization': 'ORGA', 'Professional Society': 'ORGA', 'Self-help or Relief Organization': 'ORGA','Biologic Function': 'PHEN', 'Environmental Effect of Humans': 'PHEN', 'Human-caused Phenomenon or Process': 'PHEN', 'Laboratory or Test Result': 'PHEN','Natural Phenomenon or Process': 'PHEN', 'Phenomenon or Process': 'PHEN', 'Cell Function': 'PHYS', 'Clinical Attribute': 'PHYS', 'Genetic Function': 'PHYS', 'Mental Process': 'PHYS','Molecular Function': 'PHYS', 'Organism Attribute': 'PHYS', 'Organism Function': 'PHYS', 'Organ or Tissue Function': 'PHYS', 'Physiologic Function': 'PHYS','Diagnostic Procedure': 'PROC', 'Educational Activity': 'PROC', 'Health Care Activity': 'PROC', 'Laboratory Procedure': 'PROC', 'Molecular Biology Research Technique': 'PROC','Research Activity': 'PROC', 'Therapeutic or Preventive Procedure': 'PROC'}

stysPerGroup = defaultdict(list)
for key in list(sty_groups.keys()):
    stysPerGroup[sty_groups[key]].append(key)
stysPerGroup = dict(stysPerGroup)

banned_words = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                "a", "an", "is", "the", "of", "and", "to", "is", "you", "it",
                "he", "she", "for", "on", "at", "be", "or", "no", "+", "as", "in",
                "As", "To"]

def assemble(*args):
    return " ".join(args)

def assemble2(*args):
    return "\t".join(args)

def annotate_sentence(text, word, allWordsDict, styGroupsDict, cui = "C00000000", threshold = 5, nested = "all"):
    ### options:
    # 'none'   : no nesting
    # 'partial': forbid nesting between elements of the same group
    # 'all'    : complete nesting
    global id
    global text_offset
    ann_str = ""
    tokens = text.split(" ")
    allWordsSet = set(allWordsDict)
    if word != "":
        # highlight main expression (word)
        for group in styGroupsDict[cui]:
            ann_str = highlight_element(word, text, group)[0]
        
    # split subwords
    subwords_set = set()
    for i in range(len(tokens)):
        for j in range(i, i+threshold):
            if ((subword := " ".join(tokens[i:j+1])) not in subwords_set) and (subword not in banned_words) and subword != word:
                subwords_set.add(subword)
                
    #print(subwords)
    
    pos=0
    item_plus_pos = []
    inter = subwords_set.intersection(allWordsSet)
    if len(inter)>0 :
        inter = sorted(inter, key=len)[::-1]
        text_tmp = text
        #print(inter)
        tmp_dict = {}
        for elem in inter: # elem = subword
            for group in allWordsDict[elem]:
                if nested == 'partial':
                    if group not in tmp_dict:
                        tmp_dict[group] = text_tmp
                        if word != "":
                            if group in allWordsDict[word]:
                                tmp_dict[group] = tmp_dict[group].replace(word, " "*len(word))
                    ### masking in the elem's group
                    annotations, tmp_dict[group] = highlight_element(elem, tmp_dict[group], group, pos)
                elif nested == 'all':
                    ### no masking, complete nesting
                    annotations = highlight_element(elem, text_tmp, group, pos)[0]
                else : ### nested == False
                    ### full masking
                    annotations, text_tmp = highlight_element(elem, text_tmp, group, pos)
            ann_str += annotations
    return ann_str
    
def highlight_element(elem, sentence, group, pos = 0):
    # give value to pos when dealing with fragments (tmp_dict[group] in annotate_sentence)
    global text_offset
    ann_str = ""
    #print(sentence)
    #print("highlighting :", elem)
    if sentence.split('\n')[0] == elem:
        to_find = elem
    else :
        to_find = elem+" " # len -1
    if flag := sentence.find(to_find[0:len(to_find)]) == 0:##In case our word is in first position
        start_pos = text_offset+pos+flag-1
        end_pos = start_pos + len(elem)
        ann_str += write_T_line(elem, start_pos, end_pos, group)
        # mask 1st occurence of to_find in sentence
        sentence = sentence.replace(to_find, " "*len(to_find), 1)
        # check if to_find is still in the sentence
        flag = sentence.find(to_find)
        #print(sentence)
    # otherwise:
    to_find = " "+elem+" "
    flag = sentence.find(to_find)
    while (flag!=-1):
        start_pos = text_offset+pos+flag+1
        end_pos = start_pos + len(elem)
        ann_str += write_T_line(elem, start_pos, end_pos, group)
        # mask 1st occurence of to_find in sentence
        sentence = sentence.replace(to_find, " "*len(to_find), 1)
        # check if to_find is still in the sentence
        flag = sentence.find(to_find)
        #print(sentence) 
    return ann_str, sentence
    
def write_T_line(word, start_pos, end_pos, group):
    global id
    out_str = ""
    word_loc = group + " " + str(start_pos) + " " + str(end_pos)
    out_str += assemble2("T" + str(id),
                         word_loc,
                         word)
    out_str += "\n"
    id += 1
    return out_str

def annotation(path):
    outfile = open(path+"annotation.conf", 'w')

    annotation_text = "[entities]\n\n"
    for group in list(stysPerGroup.keys()):
        annotation_text += group + "\n"    
        
    annotation_text += "\n[attributes]\n\n"
    for group in list(stysPerGroup.keys()):
        sub_groups = stysPerGroup[group]
        # Category Arg:CHEM, Value:SpecificDisease|Modifier|DiseaseClass|CompositeMention
        annotation_text += "Category Arg:" + group + ", Value:" + sub_groups[0].replace(" ", "_")
        for sub in sub_groups[1:]:
            annotation_text += "|" + sub.replace(" ", "_")
        annotation_text += "\n"
        
    annotation_text += "\n[relations]\n\n"
    annotation_text += "\n[events]\n\n"
    
    #print(annotation_text)
    
    outfile.write(annotation_text)
    outfile.close()

    
def prepare_sentences(finalDict, synDict):
    words_for_training = defaultdict(list) # dict format : 'id': ['(CUI, word)']
    markov_sentences = defaultdict(list)
    syn_copy = RandomDict(copy.deepcopy(synDict))
    cpt = 0
    file_index = 0
    while len(syn_copy) != 0:
        #print(cpt)
        try:
            nb_of_sentences = random.randint(31, 40)
            for i in range(nb_of_sentences):
                # pick the cui
                cui = syn_copy.random_key()
                words_for_training[file_index].append((cui, tmp_key := list(syn_copy[cui].keys())[0]))
                rng = random.randint(1, 10)
                if rng > 0 and tmp_key in finalDict[cui]: # 50% rng
                    markov_sentences[file_index].append(finalDict[cui][tmp_key])
                else:
                    markov_sentences[file_index].append(synDict[cui][tmp_key])
                syn_copy[cui].pop(tmp_key)
                if len(syn_copy[cui]) == 0:
                    syn_copy.pop(cui)
            file_index += 1
        except KeyError: # all words parsed, nb_of_sentences > nb of words left
            pass
        except IndexError:
            print(syn_copy[cui], len(syn_copy[cui]))
        cpt += nb_of_sentences
    return markov_sentences, words_for_training

def create_annotated_files(sentences, path, words_for_training, allWordsDict, styGroupsDict, nested = "all"):
    vowels = ["a", "A", "e", "E", "i", "I", "o", "O", "u", "U"]
    global text_offset
    global id
    #write annotation.conf files
    annotation(path)

    with tqdm(total=len(words_for_training), miniters = int(len(words_for_training)/100)) as pbar :
        #for index in list(words_for_training.keys())[:1]:
        for index in words_for_training.keys():
            try:
                CUIs = []
                words = []
                texts = []
                for new_word in words_for_training[index]:
                    words.append(new_word[1])
                    CUIs.append(new_word[0])
                for sentence in sentences[index]:
                    texts.append(sentence)
                id = 1
                #print("saving file to", path)
                name = str(index)
                for i in range(7-len(str(index))):
                    name = "0" + name
                name = "file" + name
                outfileNameTXT = path + name + ".txt"
                outfileNameANN = path + name + ".ann"
                outfileTXT = open(outfileNameTXT, 'w')
                outfileANN = open(outfileNameANN, 'w')

                text_offset = 0
                for text, word, cui in zip(texts, words, CUIs):
                    # text designates a single sentence
                    #print(text, word)
                    hs = annotate_sentence(text, word,allWordsDict, styGroupsDict, cui, nested = nested)
                    # threshold : change how many words in sub-elements
                    outfileANN.write(hs)
                    outfileTXT.write(text + "\n")
                    text_offset += len(text) + 1
                    #print(hs)
                outfileANN.close()
                outfileTXT.close()
            except KeyError:
                print("Error for", cui, index)
            pbar.update(1)
            
def delete_all_files_in_folder(path):
    files = glob.glob(path+'*')
    for f in files:
        os.remove(f)