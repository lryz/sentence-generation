import numpy
import glob
import os
import itertools
from randomdict import RandomDict
from collections import defaultdict
from tqdm.notebook import tqdm
import random

sty_groups = {'Activity': 'ACTI', 'Behavior': 'ACTI', 'Daily or Recreational Activity': 'ACTI', 'Event': 'ACTI', 'Governmental or Regulatory Activity': 'ACTI', 'Individual Behavior': 'ACTI','Machine Activity': 'ACTI', 'Occupational Activity': 'ACTI', 'Social Behavior': 'ACTI', 'Anatomical Structure': 'ANAT', 'Body Location or Region': 'ANAT','Body Part, Organ, or Organ Component': 'ANAT', 'Body Space or Junction': 'ANAT', 'Body Substance': 'ANAT', 'Body System': 'ANAT', 'Cell': 'ANAT', 'Cell Component': 'ANAT','Embryonic Structure': 'ANAT', 'Fully Formed Anatomical Structure': 'ANAT', 'Tissue': 'ANAT', 'Amino Acid, Peptide, or Protein': 'CHEM', 'Antibiotic': 'CHEM', 'Biologically Active Substance': 'CHEM', 'Biomedical or Dental Material': 'CHEM', 'Carbohydrate': 'CHEM', 'Chemical': 'CHEM', 'Chemical Viewed Functionally': 'CHEM','Chemical Viewed Structurally': 'CHEM', 'Clinical Drug': 'CHEM', 'Eicosanoid': 'CHEM', 'Element, Ion, or Isotope': 'CHEM', 'Enzyme': 'CHEM', 'Hazardous or Poisonous Substance': 'CHEM', 'Hormone': 'CHEM', 'Immunologic Factor': 'CHEM', 'Indicator, Reagent, or Diagnostic Aid': 'CHEM', 'Inorganic Chemical': 'CHEM', 'Lipid': 'CHEM', 'Neuroreactive Substance or Biogenic Amine': 'CHEM', 'Nucleic Acid, Nucleoside, or Nucleotide': 'CHEM', 'Organic Chemical': 'CHEM', 'Organophosphorus Compound': 'CHEM','Pharmacologic Substance': 'CHEM', 'Receptor': 'CHEM', 'Steroid': 'CHEM', 'Vitamin': 'CHEM', 'Classification': 'CONC', 'Conceptual Entity': 'CONC', 'Functional Concept': 'CONC','Group Attribute': 'CONC', 'Idea or Concept': 'CONC', 'Intellectual Product': 'CONC', 'Language': 'CONC', 'Qualitative Concept': 'CONC', 'Quantitative Concept': 'CONC','Regulation or Law': 'CONC', 'Spatial Concept': 'CONC', 'Temporal Concept': 'CONC', 'Drug Delivery Device': 'DEVI', 'Medical Device': 'DEVI', 'Research Device': 'DEVI', 'Acquired Abnormality': 'DISO', 'Anatomical Abnormality': 'DISO', 'Cell or Molecular Dysfunction': 'DISO', 'Congenital Abnormality': 'DISO', 'Disease or Syndrome': 'DISO','Experimental Model of Disease': 'DISO', 'Finding': 'DISO', 'Injury or Poisoning': 'DISO', 'Mental or Behavioral Dysfunction': 'DISO', 'Neoplastic Process': 'DISO','Pathologic Function': 'DISO', 'Sign or Symptom': 'DISO', 'Amino Acid Sequence': 'GENE', 'Carbohydrate Sequence': 'GENE', 'Gene or Genome': 'GENE', 'Molecular Sequence': 'GENE','Nucleotide Sequence': 'GENE', 'Geographic Area': 'GEOG', 'Age Group': 'LIVB', 'Amphibian': 'LIVB', 'Animal': 'LIVB', 'Archaeon': 'LIVB', 'Bacterium': 'LIVB', 'Bird': 'LIVB','Eukaryote': 'LIVB', 'Family Group': 'LIVB', 'Fish': 'LIVB', 'Fungus': 'LIVB', 'Group': 'LIVB', 'Human': 'LIVB', 'Mammal': 'LIVB', 'Organism': 'LIVB', 'Patient or Disabled Group': 'LIVB', 'Plant': 'LIVB', 'Population Group': 'LIVB', 'Professional or Occupational Group': 'LIVB', 'Reptile': 'LIVB', 'Vertebrate': 'LIVB', 'Virus': 'LIVB','Entity': 'OBJC', 'Food': 'OBJC', 'Manufactured Object': 'OBJC', 'Physical Object': 'OBJC', 'Substance': 'OBJC', 'Biomedical Occupation or Discipline': 'OCCU', 'Occupation or Discipline': 'OCCU', 'Health Care Related Organization': 'ORGA', 'Organization': 'ORGA', 'Professional Society': 'ORGA', 'Self-help or Relief Organization': 'ORGA','Biologic Function': 'PHEN', 'Environmental Effect of Humans': 'PHEN', 'Human-caused Phenomenon or Process': 'PHEN', 'Laboratory or Test Result': 'PHEN','Natural Phenomenon or Process': 'PHEN', 'Phenomenon or Process': 'PHEN', 'Cell Function': 'PHYS', 'Clinical Attribute': 'PHYS', 'Genetic Function': 'PHYS', 'Mental Process': 'PHYS','Molecular Function': 'PHYS', 'Organism Attribute': 'PHYS', 'Organism Function': 'PHYS', 'Organ or Tissue Function': 'PHYS', 'Physiologic Function': 'PHYS','Diagnostic Procedure': 'PROC', 'Educational Activity': 'PROC', 'Health Care Activity': 'PROC', 'Laboratory Procedure': 'PROC', 'Molecular Biology Research Technique': 'PROC','Research Activity': 'PROC', 'Therapeutic or Preventive Procedure': 'PROC'}

for key in list(sty_groups.values()):
    sty_groups[key] = key
    
    
def create_semantic_type_dict(path_to_umls):
    file = open(path_to_umls, mode = 'r', encoding = 'utf-8')
    styDict = defaultdict(list)
    styGroupsDict = defaultdict(list)
    cuiInSty = defaultdict(dict)
    cuiInStyGroups = defaultdict(RandomDict)

    lines = file.readlines()
    print("Generating semantic types dict...")
    with tqdm(total=len(lines), miniters=int(len(lines)-1)/100) as pbar :
        for line in lines:
            split_line = line.split("|")
            styDict[split_line[0]].append(split_line[3])
            for sty in styDict[split_line[0]]:
                if sty_groups[sty] not in styGroupsDict[split_line[0]]:
                    styGroupsDict[split_line[0]].append(sty_groups[sty])
            cuiInSty[split_line[3]][split_line[0]] = ""
            if split_line[0] not in cuiInStyGroups[sty_groups[split_line[3]]]:
                cuiInStyGroups[sty_groups[split_line[3]]][split_line[0]] = ""
            pbar.update(1)
    cuiInSty = dict(cuiInSty)
    cuiInStyGroups = RandomDict(cuiInStyGroups)
    
    return styDict, styGroupsDict, cuiInSty, cuiInStyGroups


def create_from_brat(path, styDict, styGroupsDict):
    synDict = defaultdict(dict)
    for filename in glob.glob(os.path.join(path, '*.ann')) :
        with open(os.path.join(os.getcwd(), filename), 'r') as file_ann :
            with open(os.path.join(os.getcwd(), filename.replace(".ann", ".txt")), 'r') as file_txt:
                txt_lines = file_txt.readlines()
                cpt=0
                tmp_dict={}
                for line1, line2 in itertools.zip_longest(*[file_ann]*2):
                    if line1 != None and line2 != None:
                        split1 = line1.split("\t")
                        split2 = line2.split("\t")
                        if split2[-1][0] != "C":
                            print(filename)
                        cui = split2[-1].replace("\n", "")
                        # get the context and fill synDict
                        word = split1[-1].replace("\n", "")
                        tmp_dict[word] = ""
                        synDict[cui][word] = ""
                        word_low = word[0].lower() + word[1:]
                        synDict[cui][word_low] = ""
                        word_up = word[0].upper() + word[1:]
                        synDict[cui][word_up] = ""
                        # shuffle contexts
                        #if filename.split('/')[-1].replace(".ann", "") == "345_2" :
                        #    print(word)
                        extracted_sty_group = split1[1].replace("\n", "").split(" ")[0]
                        if cui not in styDict:
                            styDict[cui].append(extracted_sty_group)
                        if cui not in styGroupsDict:
                            styGroupsDict[cui].append(extracted_sty_group)
                        cpt+=1
    return synDict, styDict, styGroupsDict 



def create_all_words_dict(synDict, styGroupsDict):
    allWordsDict = defaultdict(list)
    for key in synDict:
        for word in synDict[key]:
            for group in styGroupsDict[key]:
                if group not in allWordsDict[word]:
                    allWordsDict[word].append(group)

    return allWordsDict
    