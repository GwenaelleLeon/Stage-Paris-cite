from io import open
from unittest import result 
import conllu as co
import os
import pandas as pd
import numpy as np



###Fonctions##################################################################

def control_number_and_gender(word):
    if word['feats'] != None:
        if 'Gender' in word['feats']:
            if 'Number' in word['feats']:
                return word['feats']['Gender'], word['feats']['Number']
            else: return word['feats']['Gender'], '_'
        else: 
            if 'Number' in word['feats']:
                return '_', word['feats']['Number']
            else: return '_', '_'
    else: return '_', '_'

def control_DOM(word, sentence):
    if word['deprel'] == 'obj':
        for dep in sentence.filter(head=word['id']):
            if dep['form'] =='a' or dep['lemma'] == 'a':
                return 'a-marqué'
        else: return 'non-marqué'
    else: return '_'

def control_inversion(word, sentence):
    if word['deprel'] != 'obj':
        if word['id'] < sentence.filter(id=word['head'])[0]['id']:
            return 'non'
        else: return 'oui'
    else: return '_'

def control_subj_pass_act(word, sentence):
    if word['deprel'] in ['nsubj','nsubj:pass']:
        for dep in sentence.filter(head=sentence.filter(id=word['head'])[0]['id']):
            if dep['lemma'] == 'estar':
                return 'passif estar'
            if dep['lemma'] == 'ser':
                return 'passif ser' 
            if dep['lemma'] == 'se':
                return 'passif se'
            if dep['deprel'] == 'obj' and word['deprel'] == 'nsubj': #Si c'est passif, il ne devrait pas avoir d'obj ??
                return 'actif'
        return 'non passif'
    else:
        return '_'

def filtrage(sentences, data_source):
    words = []
    for sentence in sentences:
        first_filter = sentence.filter(upos = (lambda x: x=='NOUN' or x=='PRON' or x =='PROPN'), deprel = (lambda x: x=='nsubj' or x=='nsubj:pass' or x =='obj'))
        for word in first_filter:
            word_info = dict()
            word_info['corpus'] = data_source
            word_info['new_id'] = sentence.metadata['sent_id'] + "_" + str(word['id'])
            word_info['form'] = word['form']
            word_info['lemma'] = word['lemma']
            word_info['upos'] = word['upos']
            word_info['Gender'], word_info['Number'] = control_number_and_gender(word)
            word_info['deprel'] = word['deprel']
            word_info['inversion'] = control_inversion(word, sentence)
            word_info['sujet actif/passif'] = control_subj_pass_act(word, sentence)
            word_info['DOM'] = control_DOM(word, sentence)
            words.append(word_info)
    return words

"""
def identify_passive_ancora(sentences):
    masc_full = 0
    fem_full = 0
    for sentence in sentences:
        auxiliars_pass = sentence.filter(upos="AUX", lemma = lambda x: x =="SER" or x=="ESTAR")
        print(auxiliars_pass, "   " , sentence)
        for token in auxiliars_pass:
            subj_id = token["head"]
            if sentence[subj_id]["feats"]["gender"]== "Masc":
                masc_full += 1
            elif sentence[subj_id]["feats"]["gender"]== "Fem":
                fem_full += 1
        print("  ")
    return masc_full, fem_full
"""    
####Data sources##############################################################

data_sources = ["es_pud-ud-test.conllu"] #, "es_ancora-ud-all.conllu", "es_gsd-ud-all.conllu"]

####Main#####################################################################

if __name__ ==  "__main__":
    for data_source in data_sources:
        with open(data_source, "r", encoding="utf-8") as data_file:
            strings = data_file.read()
            sentences = co.parse(strings)
            resultat = filtrage(sentences, data_source)
            database_es = pd.DataFrame(resultat)
            print(database_es)
            database_es.to_csv('../database_es-Leon.csv')


