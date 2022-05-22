from io import open
import conllu as co
import pandas as pd
from pyrae import dle
import argparse
from getch import getch

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
            word_info['sent_id'] = sentence.metadata['sent_id']
            word_info['form'] = word['form']
            word_info['lemma'] = word['lemma']
            word_info['upos'] = word['upos']
            word_info['Gender'], word_info['Number'] = control_number_and_gender(word)
            word_info['deprel'] = word['deprel']
            word_info['inversion'] = control_inversion(word, sentence)
            word_info['sujet actif/passif'] = control_subj_pass_act(word, sentence)
            word_info['DOM'] = control_DOM(word, sentence)
            word_info['Animacy'] = word['feats']['Animacy'] if word['feats'] != None and 'Animacy' in word['feats'] else '_'
            words.append(word_info)
    return words

# def identify_passive_ancora(sentences):
#     masc_full = 0
#     fem_full = 0
#     for sentence in sentences:
#         auxiliars_pass = sentence.filter(upos="AUX", lemma = lambda x: x =="SER" or x=="ESTAR")
#         print(auxiliars_pass, "   " , sentence)
#         for token in auxiliars_pass:
#             subj_id = token["head"]
#             if sentence[subj_id]["feats"]["gender"]== "Masc":
#                 masc_full += 1
#             elif sentence[subj_id]["feats"]["gender"]== "Fem":
#                 fem_full += 1
#         print("  ")
#     return masc_full, fem_full

####Animacy Helpers###########################################################

def find_sentence(sentences, sent_id):  
    for sentence in sentences:
        if sentence.metadata['sent_id'] == sent_id: return sentence.metadata['text']

def update_animacy(sentences, animacy_dict):
    for sentence in sentences:
        for word in sentence:
            if word["lemma"] != "_" and word["lemma"] in animacy_dict:
                if word['feats'] ==  None: word['feats'] = dict()
                word["feats"]["Animacy"] = animacy_dict[word["lemma"]]
            elif word["form"] in animacy_dict:
                if word['feats'] ==  None: word['feats'] = dict()
                word["feats"]["Animacy"] = animacy_dict[word["form"]]
    return sentences

def con_animacy(words, animacy_dict):
    total = 0
    for word in words:
        if word['form'] in animacy_dict: total = total + 1
    return total

def count_word_occurrences (words, word) :
    counter = 0
    for w in words:
        if w['form'] == word['form']:
            counter = counter + 1
    return counter

def controles_rae(sentences, words, animacy_dict):
    animacy_dict["persona"] = "Hum"
    animacy_dict["acción"] = "Inan"
    animacy_dict["mamífero"] = "Anim"
    annotated_words = con_animacy(words, animacy_dict)
    print("Hay ", len(words), "palabras, y hay ", len(animacy_dict), " palabras conocidas. Entonces, ", annotated_words, "ya tienen su animacy.")
    words = sorted(words, key=lambda x: count_word_occurrences(words, x), reverse=True)
    for word in words:
        adivinado = False
        #guessed_animacy = "boh"
        if (word["form"] in animacy_dict): continue
        guessed_animacy = check_animacy(word, animacy_dict)
        if guessed_animacy != 'boh':
            print("Adivinado que ", word['form'], 'es', guessed_animacy)
            confirmacion = getch()
            if confirmacion == 'y' or confirmacion == '\r':
                animacy_dict[word['form']] = guessed_animacy
                adivinado = True
            else: print("No te a gustao? :(")
        if not adivinado:
            res = dle.search_by_word(word['form'])
            print(find_sentence(sentences, word['sent_id']))
            print(word['form'], ": ", res.meta_description)
            print("Dime l'animacy de", word['form'], ": ")
            in_anim = getch()
            print("in_anim", in_anim)
            if in_anim == "h":
                animacy_dict[word["form"]] = "Hum"
                print("Ahora ", word['form'], 'es', animacy_dict[word["form"]])
            elif in_anim == "i":
                animacy_dict[word["form"]] = "Inan"
                print("Ahora ", word['form'], 'es', animacy_dict[word["form"]])
            elif in_anim == "a":
                animacy_dict[word["form"]] = "Anim"
                print("Ahora ", word['form'], 'es', animacy_dict[word["form"]])
            elif in_anim == "_":
                animacy_dict[word["form"]] = "_"
                print("Ahora ", word['form'], 'es', animacy_dict[word["form"]])
            elif in_anim == "q":
                break
            else:
                print("No he entendido. Pasapalabra.")
        new_annotated = con_animacy(words, animacy_dict)
        if (new_annotated - annotated_words) > 0:
            print("Ya he anotado ", new_annotated - annotated_words, "palabras.")
            annotated_words = new_annotated
    return animacy_dict

def load_animacies (sentences):
    animacy_dict = {}
    for sentence in sentences:
        for word in sentence:
            if word['feats'] != None and "Animacy" in word['feats']:
                animacy_dict[word["form"]] = word["feats"]["Animacy"]
    return animacy_dict

def check_animacy(word, animacy_dict):
    res = dle.search_by_word(word['lemma'] if word['lemma'] != '_' else word['form'])
    descr = res.meta_description
    inicio = descr.find("1.")
    fin = descr.find('2.')
    if inicio >= 0:
        for word, anim in animacy_dict.items():
            if descr[inicio:fin].find(word.capitalize()+ ' ') != -1:
                #print(descr[inicio:fin].find(word.capitalize()))
                print("He encontrado en ", descr, " la palabra", word, 'cuya anim es', anim)
                return anim
    return "boh"

####Main#####################################################################

if __name__ ==  "__main__":
    parser = argparse.ArgumentParser(description="Gweni Leon's all in one ConLLu manager", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-l', nargs='*', default=["es_pud-ud-test.conllu", "es_ancora-ud-all.conllu", "es_gsd-ud-all.conllu"], help="Load datasets and analyze")
    parser.add_argument('--anim', nargs=1, help="Edit animacy data for this dataset")
    parser.add_argument('-o', nargs=1, default=['new.conllu'], help="Output edited ConLLU dataset (only if --anim was specified)")
    parser.add_argument('-c', nargs=1, help="Output filtered CSV data from loaded datasets")
    args=vars(parser.parse_args())
    print(args)
    animacy_known = {}
    resultat = []
    print('Loading data from', len(args['l']), 'datasets')
    for data_source in args['l']:
        print('Loading', data_source, '...')
        with open(data_source, "r", encoding="utf-8") as data_file:
            strings = data_file.read()
            sentences = co.parse(strings)
            resultat = resultat + filtrage(sentences, data_source)
            animacy_known.update(load_animacies(sentences))
    if args['anim'] != None:
        for data_source in args['anim']:
            print('Editing data from', data_source)
            with open(data_source, "r", encoding="utf-8") as data_file:
                strings = data_file.read()
                sentences = co.parse(strings)
                resultat = filtrage(sentences, data_source)
                animacy_dict = controles_rae(sentences, resultat, animacy_known)
                new_corpus = update_animacy(sentences, animacy_dict)
                new_strings = [string.serialize() for string in new_corpus]
            print('Editing ended. Outputting edited data to', args['o'][0])
            with open(args['o'][0], "w", encoding="utf-8") as  out_file:
                [out_file.write(new_string) for new_string in new_strings]
    if args['c'] != None:
        print('Outputting filtered data from the loaded datasets to', args['c'][0])
        database_es = pd.DataFrame(resultat)
        database_es.to_csv(args['c'][0])