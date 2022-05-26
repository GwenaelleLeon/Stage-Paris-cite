from io import open
import conllu as co
import pandas as pd
from pyrae import dle
import argparse
from getch import getch
from playsound import playsound 

###Fonctions##################################################################

def control_number_and_gender(word):
    if word['feats'] != None:
        if 'Gender' in word['feats']:
            if 'Number' in word['feats']:
                return word['feats']['Gender'], word['feats']['Number']
            else: return word['feats']['Gender'], '_'
        else: 
            if 'Number' in word['feats']:
                if word['deprel']=='PROPN':
                    return 'MISSING', word['feats']['Number']
                else: return '_', word['feats']['Number']
            else: 
                if word['deprel']=='PROPN':
                    return 'MISSING', '_'
                else: return '_', '_'
    else: 
        if word['deprel']=='PROPN':
                    return 'MISSING', '_'
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
    word_head = sentence.filter(id=word['head'])[0]
    if word['deprel'] in ['nsubj','nsubj:pass']:
        for dep in sentence.filter(head=word_head['id']):
            if word_head['feats'] != None and 'VerbForm' in word_head['feats'] and word_head['feats']['VerbForm'] == 'Part':
                if dep['lemma'] == 'estar': 
                    return 'passif estar'
                if dep['lemma'] == 'ser': 
                    return 'passif ser' 
            if dep['form'] == 'se': 
                return 'passif se'
            if dep['deprel'] == 'obj' and word['deprel'] == 'nsubj':
                return 'actif'
        return 'non passif'
    else:
        return '_'

def filtrage(sentences, data_source):
    """
    Filter out nouns, proper nouns and pronouns relevant for the analysis and build 
    a list of dictionaries (not conLLu format) to be analyzed later on with Panda.
    """
    words = []
    for sentence in sentences:
        first_filter = sentence.filter(upos = (lambda x: x=='NOUN' or x=='PRON' or x =='PROPN'), feats__Number = lambda x: x!='Plur', deprel = (lambda x: x=='nsubj' or x=='nsubj:pass' or x =='obj'))
        
        for word in first_filter:
            word_info = dict()
            word_info['corpus'] = data_source
            word_info['new_id'] = sentence.metadata['sent_id'] + "_" + str(word['id'])
            word_info['sent_id'] = sentence.metadata['sent_id']
            word_info['Phrase'] = sentence.metadata['text']
            word_info['form'] = word['form']
            word_info['lemma'] = word['lemma']
            word_info['upos'] = word['upos']
            word_info['Gender'], word_info['Number'] = control_number_and_gender(word)
            word_info['deprel'] = word['deprel']
            word_info['clause'] = sentence.filter(id=word['head'])[0]['deprel']
            word_info['inversion'] = control_inversion(word, sentence)
            word_info['sujet actif/passif'] = control_subj_pass_act(word, sentence)
            word_info['DOM'] = control_DOM(word, sentence)
            if word['feats'] != None and 'Animacy' in word['feats']:
                word_info['Animacy'] = word['feats']['Animacy'] if word['feats']['Animacy'] != None else '_'
            else: 
                word_info['Animacy'] = "MISSING"
            
            words.append(word_info)
    return words

def find_sentence(sentences, sent_id):  
    for sentence in sentences:
        if sentence.metadata['sent_id'] == sent_id: return sentence.metadata['text']

def count_word_occurrences(words, word):
    counter = 0
    for w in words:
        if w['form'] == word['form']:
            counter = counter + 1
    return counter

def load_tags(sentences, tag):
    """
    Look in `sentences` for all words with a defined `tag` (which might be `None`!)
    and return a dictionary containing `tag` indexed by `word['form']`.
    """
    learned_dict = {}
    for sentence in sentences:
        for word in sentence:
            if word['feats'] != None and tag in word['feats']:
                learned_dict[word["form"]] = word["feats"][tag]
    return learned_dict

def update_tags(sentences, learned_dict, tag):
    for sentence in sentences:
        for word in sentence:
            if word["lemma"] != "_" and word["lemma"] in learned_dict:
                if word['feats'] ==  None: word['feats'] = dict()
                word["feats"][tag] = learned_dict[word["lemma"]]
            elif word["form"] in learned_dict:
                if word['feats'] ==  None: word['feats'] = dict()
                word["feats"][tag] = learned_dict[word["form"]]
    return sentences

####Animacy Helpers###########################################################

# def update_animacy(sentences, animacy_dict):
#     for sentence in sentences:
#         for word in sentence:
#             if word["lemma"] != "_" and word["lemma"] in animacy_dict:
#                 if word['feats'] ==  None: word['feats'] = dict()
#                 word["feats"]["Animacy"] = animacy_dict[word["lemma"]]
#             elif word["form"] in animacy_dict:
#                 if word['feats'] ==  None: word['feats'] = dict()
#                 word["feats"]["Animacy"] = animacy_dict[word["form"]]
#     return sentences

def con_animacy(words, animacy_dict):
    total = 0
    for word in words:
        if word['form'] in animacy_dict: total = total + 1
    return total

def learn_animacies(sentences, words, animacy_dict, total_des_mots_filtres_des_sources):
    """
    Given a list of filtered words (`words`) and a dictionary with partial
    animacy informations, ask the user to input new animacy information for
    `words`, by helping them with the RAE lookup function.  `sentences` is  a
    parsed ConLLu dataset from which the data originates, and is used to provide
    context for `words`.
    """
    animacy_dict["persona"] = "Hum"
    animacy_dict["acción"] = "Inan"
    animacy_dict["mamífero"] = "Anim"
    annotated_words = con_animacy(words, animacy_dict)
    print("Hay",total_des_mots_filtres_des_sources, "palabras de todo el filtre. En la fuente que estamos modificando:", 
    len(words), "palabras. Conocemos l'animacy de", len(animacy_dict), "palabras y nos hace un total de", annotated_words, 
    "que ya tienen su animacy en esta fuente.")
    words = sorted(words, key=lambda x: count_word_occurrences(words, x), reverse=True)
    print("He terminado de ordenar las palabras!")
    playsound('./628249__bloodpixelhero__notification.wav')
    for word in words:
        adivinado = False
        #guessed_animacy = "boh"
        if (word["form"] in animacy_dict): continue
        guessed_animacy = rae_lookup(word, animacy_dict)
        if guessed_animacy != 'boh':
            print("Adivinado que ", word['form'], 'es', guessed_animacy)
            confirmacion = getch()
            if confirmacion == 'y' or confirmacion == '\r':
                animacy_dict[word['form']] = guessed_animacy
                adivinado = True
            else: print("No te ha gustado? :(")
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

# def load_animacies(sentences):
#     """
#     Look in `sentences` for all words with a defined Animacy (which might be `None`!)
#     and return a dictionary containing animacies indexed by `word['form']`.
#     """
#     animacy_dict = {}
#     for sentence in sentences:
#         for word in sentence:
#             if word['feats'] != None and "Animacy" in word['feats']:
#                 animacy_dict[word["form"]] = word["feats"]["Animacy"]
#     return animacy_dict

def rae_lookup(word, animacy_dict):
    """
    Look up `word` in the RAE dictionary, and search the obtained definition for
    any word whose animacy is known from `animacy_dict`
    """
    res = dle.search_by_word(word['lemma'] if word['lemma'] != '_' else word['form'])
    descr = res.meta_description
    inicio = descr.find("1.")
    fin = descr.find('2.')
    if inicio >= 0:
        for word, anim in animacy_dict.items():
            if word in ['que', 'Que', 'QUE', 'La', 'la', 'los', 'Los'] or anim == '_':
                continue
            if descr[inicio:fin].find(word.capitalize()+ ' ') != -1:
                #print(descr[inicio:fin].find(word.capitalize()))
                print("He encontrado en ", descr, " la palabra", word, 'cuya anim es', anim)
                return anim
    return "boh"



####Gender Helpers###########################################################

def learn_gender(sentences, words, gender_dict, total_des_mots_filtres_des_sources):
    """
    Given a list of filtered words (`words`) and a dictionary with partial
    gender informations, ask the user to input new gender information for
    `words` with 'upos'='PROPN'.  `sentences` is  a parsed ConLLu dataset 
    from which the data originates, and is used to provide context for `words`.
    """
    annotated_words = con_gender(words, gender_dict)
    print("Hay",total_des_mots_filtres_des_sources, "palabras de todo el filtre. En la fuente que estamos modificando:", 
    len(words), "palabras. Conocemos el gender de", len(gender_dict), "palabras. Hay ya", annotated_words, 
    "palabras en esta fuente que ya tienen su gender.")
    words = sorted(words, key=lambda x: count_word_occurrences(words, x), reverse=True)
    print("He terminado de ordenar las palabras!")
    playsound('./628249__bloodpixelhero__notification.wav')
    for word in words:
        if (word["form"] in gender_dict): continue
        else:
            print(find_sentence(sentences, word['sent_id']))
            print("Dime el gender de", word['form'], ": ")
            in_gender = getch()
            print("in_gender", in_gender)
            if in_gender == "m":
                gender_dict[word["form"]] = "Masc"
                print("Ahora ", word['form'], 'es', gender_dict[word["form"]])
            elif in_gender == "f":
                gender_dict[word["form"]] = "Fem"
                print("Ahora ", word['form'], 'es', gender_dict[word["form"]])
            elif in_gender == "_":
                gender_dict[word["form"]] = "_"
                print("Ahora ", word['form'], 'es', gender_dict[word["form"]])
            elif in_gender == "q":
                break
            else:
                print("No he entendido. Pasapalabra.")
        new_annotated = con_gender(words, gender_dict)
        if (new_annotated - annotated_words) > 0:
            print("Ya he anotado ", new_annotated - annotated_words, "palabras.")
            annotated_words = new_annotated
    return gender_dict

def con_gender(words, gender_dict):
    total = 0
    for word in words:
        if word['form'] in gender_dict: total = total + 1
    return total

####Main#####################################################################

if __name__ ==  "__main__":
    parser = argparse.ArgumentParser(description="Gweni Leon's all in one ConLLu manager", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-l', nargs='*', default=["es_pud-ud-test.conllu", "es_ancora-ud-all.conllu", "es_gsd-ud-all.conllu"], help="Load datasets and analyze")

    parser.add_argument('OBJ', nargs=1, help="Object of action")
    actions = parser.add_mutually_exclusive_group(required = True)
    actions.add_argument('--anim', action='store_true', help="Edit animacy data for this dataset")
    actions.add_argument('--gender', action='store_true', help="Edit gender data for proper names in this dataset")
    #actions.add_argument('-o', nargs=1, default=['new.conllu'], action='store_true', help="Output edited ConLLU dataset (only if --anim was specified)")
    actions.add_argument('--csv', action = 'store_true', help="Output filtered CSV data from loaded datasets")

    args=vars(parser.parse_args())
    print(args)
    object_file = args['OBJ'][0]
    animacy_known = {}
    gender_known = {}
    resultat = []
    total_des_mots_filtres_des_sources = 0
    print('Loading data from', len(args['l']), 'datasets')
    for data_source in args['l']:
        print('Loading', data_source, '...')
        with open(data_source, "r", encoding="utf-8") as data_file:
            strings = data_file.read()
            sentences = co.parse(strings)
            filtr = filtrage(sentences, data_source)
            print(len(filtr),"palabras filtradas en esta fuente." )
            resultat = resultat + filtr
            if args['anim']: animacy_known.update(load_tags(sentences, 'Animacy'))
            elif args['gender']: gender_known.update(load_tags(sentences, 'Gender'))
    total_des_mots_filtres_des_sources = len(resultat)
    if args['csv']:
        print('Outputting filtered data from the loaded datasets to', object_file)
        database_es = pd.DataFrame(resultat)
        database_es.to_csv(object_file)
    if args['anim']:
        print('Editing animacy data from', object_file)
        with open(object_file, "r", encoding="utf-8") as data_file:
            strings = data_file.read()
            sentences = co.parse(strings)
            local_resultat = filtrage(sentences, object_file)
            animacy_dict = learn_animacies(sentences, local_resultat, animacy_known, total_des_mots_filtres_des_sources)
            new_corpus = update_tags(sentences, animacy_dict, 'Animacy')
            new_strings = [string.serialize() for string in new_corpus]
        print('Editing ended. Outputting edited data to', object_file)
        with open(object_file, "w", encoding="utf-8") as  out_file:
            [out_file.write(new_string) for new_string in new_strings]
    if args['gender']:
        print('Editing gender data from', object_file)
        with open(object_file, "r", encoding="utf-8") as data_file:
            strings = data_file.read()
            sentences = co.parse(strings)
            local_resultat = filtrage(sentences, object_file)
            local_resultat = [word for word in local_resultat if word['upos'] == 'PROPN']
            gender_dict = learn_gender(sentences, local_resultat, gender_known, total_des_mots_filtres_des_sources)
            gender_dict['Guilbeault']='Masc' #Erreur
            gender_dict['Rodríguez']='_'
            gender_dict['Britney']='Fem'
            new_corpus = update_tags(sentences, gender_dict, 'Gender')
            new_strings = [string.serialize() for string in new_corpus]
        print('Editing ended. Outputting edited data to', object_file)
        with open(object_file, "w", encoding="utf-8") as  out_file:
            [out_file.write(new_string) for new_string in new_strings]