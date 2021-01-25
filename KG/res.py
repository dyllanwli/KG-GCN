import pandas as pd
import numpy as np
import os
import json
from tqdm import tqdm
from pandas import json_normalize

# KG
import rdflib
import networkx as nx

# spacy
import spacy
from spacy.matcher import Matcher 
from spacy.tokens import Span 
from spacy.pipeline import TextCategorizer

import matplotlib.pyplot as plt

import opennre

class OPENREKG:

    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        self.model = opennre.get_model('wiki80_cnn_softmax')
        self.umm_normalized_path = "/content/drive/MyDrive/Archive/NASA-CMR/UMM_DATA/cmr_normalized.csv"
        self.df_umm = pd.read_csv(umm_normalized_path)
        self.sentences_extend = []
        self.filter_entity_labels = ["CARDINAL", "DATE"]

    def get_extended_sentence(self):
        abstract = self.df_umm['umm.Abstract']
        sentences = [x.strip().replace("\r", "").replace("\n", "").split(". ") for x in abstract]
        # extended sentences
        for s in sentences:
            self.sentences_extend.extend(s)

    def get_relation_opennre(self):
        print("Getting relation using opennre")

    
    def ner_spacy(self, s):
        doc = self.nlp(s)
        entities = [x.text for x in doc.ents if x.label_ not in filter_labels]
        
        # verbose
        # entities = []
        # for ent in doc.ents: 
        
        #     print(ent.text, ent.start_char, ent.end_char, ent.label_)
        return entities



def main():
    print("starting")
    openkg = OPENREKG()
    openkg.get_extended_sentence()

if __name__ == "__main__":
    main()