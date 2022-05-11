from io import open 
import conllu as co

def count_genders(sentences, tag): #Pour filtrer dans "upos"
    masc_full = 0
    fem_full = 0
    for sentence in sentences:
        number_masc = len(sentence.filter(upos=tag, feats__Gender="Masc"))
        number_fem = len(sentence.filter(upos=tag, feats__Gender="Fem"))
        masc_full += number_masc
        fem_full += number_fem
    return masc_full, fem_full

def count_gender_pronoun(sentence, gender):
     return len(sentence.filter(upos="PRON", feats__Gender=gender))

data_sources = ["es_pud-ud-test.conllu"] #"es_ancora-ud-all.conllu", "es_gsd-ud-all.conllu"

if __name__ ==  "__main__":
    for data_source in data_sources:
        with open(data_source, "r", encoding="utf-8") as data_file:
            strings = data_file.read()
            sentences = co.parse(strings)
            print("Data source: ", data_source)
            tags = {"Noun or Proper noun" : lambda x: x=="NOUN" or x=="PROPN", "Pronoun" : "PRON"}
            for name, tag in tags:
                masc, fem = count_genders(sentences, tag)
                total = masc + fem
                print("Tag:", name)
                print("Masculine = ", masc)
                print("Feminine =", fem)
                print("Total: ", total)

                






