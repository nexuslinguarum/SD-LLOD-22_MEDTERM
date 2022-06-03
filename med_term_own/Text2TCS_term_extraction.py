from elg import Service
from elg.model import *
import os
import spacy
import pysbd

path = "PATH/TO/FILE/"
output = "PATH/TO/OUTPUT"

"""
Extracting terms using the local deployment of the Text2TCS service 
"""
def obtain_terms_from_text2TCS():
    #Instructions on how to run the service locally:
    # https://european-language-grid.readthedocs.io/en/stable/all/A1_PythonSDK/DeployServicesLocally.html
    service = Service.from_id(8122, local=True)
    output_file = open("Text2TCS_results.txt", 'w')

    for filename in os.listdir(path):
        with open(os.path.join(path, filename)) as f:
                req = TextRequest(params={"only_terms": True},
                              content=f.read())
                res = service(req)
                for ann in res["annotations"]:
                    output_file.write(filename+"\t"+ann+"\n")


"""
POS tagging of extracted terms 
"""
def pos_tag_terms():
    nlp = spacy.load('es_core_news_md')
    extracted_terms = open("Text2TCS_results.txt")
    output = open("Text2TCS_results_pos.txt", "w")

    for line in extracted_terms:
        id = line.split("\t")[0]
        term = line.split("\t")[1].strip()
        pos = nlp(term)
        pos_tag = ""
        for token in pos:
            pos_tag += token.pos_ + " "
        output.write(id + "\t" + term + "\t" + str(pos_tag.strip() + "\n"))

if __name__ == "__main__":
    obtain_terms_from_text2TCS()