from io import open 
import conllu as co

def count_genders(sentences, tag): #Pour filtrer dans "upos"
    masc_full = 0
    fem_full = 0
    for sentence in sentences:
        number_masc = len(sentence.filter(**tag, feats__Gender="Masc"))
        number_fem = len(sentence.filter(**tag, feats__Gender="Fem"))
        masc_full += number_masc
        fem_full += number_fem
    return masc_full, fem_full


data_sources = ["es_pud-ud-test.conllu"] #"es_ancora-ud-all.conllu", "es_gsd-ud-all.conllu"

if __name__ ==  "__main__":
    upos_nouns = {"upos" : lambda x: x =="NOUN" or x=="PROPN"} #Ici on definit le filtre qu'on veut et on le rajout aussi à tags
    upos_pron = {"upos" : "PRON"}
    deprel_nsubjpass = {"deprel" : "nsubj:pass"}
    tags = {"Noun or Proper noun" : upos_nouns, "Pronoun" : upos_pron, "Deprel" : deprel_nsubjpass} 
    for data_source in data_sources:
        with open(data_source, "r", encoding="utf-8") as data_file:
            strings = data_file.read()
            sentences = co.parse(strings)
            print("Data source: ", data_source)
            for name, tag in tags.items():
                masc, fem = count_genders(sentences, tag)
                total = masc + fem
                print("Tag:", name)
                print("Masculine = ", masc, masc/total*100, "%")
                print("Feminine =", fem,  fem/total*100, "%")
                print("Total: ", total)
                