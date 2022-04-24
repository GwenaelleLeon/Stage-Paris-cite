from io import open 
from conllu import parse_incr, parse
from numpy import datetime_as_string 

data_file_pud = open("es_pud-ud-test.conllu", "r", encoding="utf-8")
data_file_ancora = open("es_ancora-ud-train.conllu", "r", encoding="utf-8")
data_file_gsd = open("es_gsd-ud-train.conllu", "r", encoding="utf-8")

sentences_generator_pud = parse_incr(data_file_pud) # Generator for list of sentences 
sentences_generator_ancora = parse_incr(data_file_ancora) # Generator for list of sentences 
sentences_generator_gsd = parse_incr(data_file_gsd) # Generator for list of sentences 

for tokenlist in sentences_generator_pud:
    for word in tokenlist:
        print(word["feats"]['Gender'])