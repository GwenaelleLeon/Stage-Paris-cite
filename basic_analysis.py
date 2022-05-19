####Librairies#############################################################
from io import open 
import conllu as co
import os

####Fonctions##############################################################

def count_genders(sentences, tag):
    masc_full = 0
    fem_full = 0 
    for sentence in sentences:
        number_masc = len(sentence.filter(**tag, feats__Gender="Masc"))
        number_fem = len(sentence.filter(**tag, feats__Gender="Fem"))
        masc_full += number_masc
        fem_full += number_fem
    return masc_full, fem_full

####Data sources##############################################################

data_sources = ["es_pud-ud-test.conllu"] #, "es_ancora-ud-all.conllu", "es_gsd-ud-all.conllu"]


####Main#####################################################################

if __name__ ==  "__main__":
    tags = {
        "Noun or Proper noun" : {"upos" : lambda x: x =="NOUN" or x=="PROPN"}, 
        "Pronoun" : {"upos" : "PRON"}, "Deprel subpass" : {"deprel" : "nsubj:pass"}, 
        "Deprel sub act" : {"deprel" : "nsubj"}, "Deprel obj" : {"deprel" : "obj"}
        } 
    for data_source in data_sources:
        with open(data_source, "r", encoding="utf-8") as data_file:
            strings = data_file.read()
            sentences = co.parse(strings)
            print("---------------------------------------------------------------------")
            print("Data source: ", data_source)
            print("Size of the corpus: ", os.stat(data_source).st_size, " bytes")
            print(" ")
            for name, tag in tags.items():
                masc, fem = count_genders(sentences, tag)
                total = masc + fem
                print("Tag:", name)
                print("Masculine = ", masc, masc/total*100, "%")
                print("Feminine =", fem,  fem/total*100, "%")
                print("Total: ", total)
                print("---------------------------------------------------------------------")