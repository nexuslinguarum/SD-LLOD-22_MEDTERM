from sparql_enrichment import Wrapper_SPARQL
from sparql_enrichment import TripleStore


dbnary_endpoint = "http://kaiko.getalp.org/sparql"
wrapper = Wrapper_SPARQL(TripleStore(dbnary_endpoint))


def serializer(term, data):
    if data != {}:
        triples = list()
        id = "http://sd-llod-22.org/medterm/" + "es_" +  term

        triples.append("<" + id + ">  <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2004/02/skos/core#Concept> .")
        triples.append("<" + id + "> <http://www.w3.org/2004/02/skos/core#inScheme> \"disease\" .")
        triples.append("<" + id + "> <http://www.w3.org/2004/02/skos/core#closeMatch> " +  data["source"] + " .")

        for translation in data["translations"]:
            triples.append("<" + id + "> <http://www.w3.org/2004/02/skos/core#SKOS:prefLabel>  \"" +  translation  + "\" . ")
        return triples
    return []


def parse(data):
    terms = list()
    return terms


terms = parse()
terms = ["viruela", "alzheimer", "sdf"]
KB = list()

for term in terms:
    enrichment_dbnary = wrapper.dbnary_enrichment(term)
    triples = serializer(term, enrichment_dbnary)
    KB.extend(triples)

for triple in KB:
    print(triple)
    with open('KB.nt', 'a') as f:
        f.write(triple)