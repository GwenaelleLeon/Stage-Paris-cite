from io import open 
import conllu as co 
from numpy import datetime_as_string 

data_file_pud = open("es_pud-ud-test.conllu", "r", encoding="utf-8")
data_file_ancora = open("es_ancora-ud-train.conllu", "r", encoding="utf-8")
data_file_gsd = open("es_gsd-ud-train.conllu", "r", encoding="utf-8")

sentences_generator_pud = co.parse_incr(data_file_pud) # Generator for list of sentences 
sentences_generator_ancora = co.parse_incr(data_file_ancora)  
sentences_generator_gsd = co.parse_incr(data_file_gsd)

for tokenlist in sentences_generator_pud:
    print(tokenlist.filter(feats__Gender = "Masc"))

map(lambda tokenlist: tokenlist.filter(feats__Gender = "Masc" ),sentences_generator_pud)


#Questo è un test per vedere se funziona github
 
"""
for tokenlist in sentences_generator_pud:
    for word in tokenlist:
        if word["feats"] != None and "Gender" in word["feats"] :
            if word["feats"]['Gender'] == "Masc":
"""

