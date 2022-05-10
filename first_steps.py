from io import open 
import conllu as co

def count_gender (sentence, gender) :
    return len(sentence.filter(feats__Gender=gender))

def count_gender_restreint (sentence, gender) :
    return len(sentence.filter(upos=lambda x: x=="NOUN"or x=="PRON" or x=="PROPN", feats__Gender=gender))

data_sources = ["es_pud-ud-test.conllu", "es_ancora-ud-train.conllu", "es_gsd-ud-train.conllu"]

def analyse_data(data_source):
    with open(data_source, "r", encoding="utf-8") as data_file:
        strings = data_file.read()
        sentences = co.parse(strings)
        masc_full = 0
        fem_full = 0
        [masc_full := masc_full + count_gender_restreint(sentence, "Masc") for sentence in sentences]
        [fem_full := fem_full + count_gender_restreint(sentence, "Fem") for sentence in sentences]
        return masc_full, fem_full


for data_source in data_sources:
     genders = analyse_data(data_source)
     print(data_source, genders[0], " masc, ", genders[1], " fem.")


