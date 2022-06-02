import json
import pprint
from triplestore import TripleStore
from rdflib import Graph, URIRef
from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET
import pprint 


class TripleStore:

    def __init__(self, endpoint, default_graph = None):
        self.sparql = SPARQLWrapper(endpoint)
        self.sparql.setReturnFormat(JSON)


    def select(self, query):
        self.sparql.setMethod(GET)
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
        return results["results"]["bindings"]


class Wrapper_SPARQL:

    def __init__(self, triplestore):
        self.ts = triplestore

    def get_le_ent(self, term):
        query = "SELECT ?le " \
                "WHERE { " \
                "?le a ontolex:LexicalEntry ; " \
                "rdfs:label \"" + term + "\"@es " \
                "}"
        out = self.ts.select(query)
        
        entities = list()
        for el in out:
            entities.append(el["le"]["value"])

        return entities


    def get_form_ent(self, le):
        query = "SELECT ?form " \
                "WHERE { " \
                " <" + le + "> ontolex:canonicalForm  ?form " \
                "}"
        out = self.ts.select(query)
        form = out[0]["form"]["value"]
        return form       


    def get_number(self, form):
        query = "SELECT ?number " \
                "WHERE { " \
                " <" + form + "> <http://purl.org/olia/olia.owl#hasNumber>  ?number " \
                "}"
        out = self.ts.select(query)
        if len(out) > 0:
            form = out[0]["number"]["value"]
        else:
            return None 


    def get_phonetic_rep(self, form):
        query = "SELECT ?phonetic_rep " \
                "WHERE { " \
                " <" + form + "> ontolex:phoneticRep  ?phonetic_rep " \
                "}"
        out = self.ts.select(query)
        try:
            form = out[0]["phonetic_rep"]["value"]
        except: 
            return None
        return form  


    def get_translatiosn(self, le):
        query = "SELECT ?translation " \
                "WHERE { " \
                " ?translation dbnary:isTranslationOf  <" + le + "> " \
                "}"
        out = self.ts.select(query)
        translations  = list()
        for el in out:
            translations.append(el["translation"]["value"])


        res = list()
        for translation in translations:
            query = "SELECT ?writtenForm " \
                    "WHERE { " \
                    "  <" + translation + ">  dbnary:writtenForm ?writtenForm " \
                    "}"
            out = self.ts.select(query)
            term = out[0]["writtenForm"]["value"] 
            lang = out[0]["writtenForm"]["xml:lang"]   
            term =  term + "@" + lang 
            res.append(term)        
        return res  

    def dbnary_enrichment(self, term):
        enriched = dict()
        le  = self.get_le_ent(term)
        if le:
            form = self.get_form_ent(le[0])
            number = self.get_number(form)
            enriched["source"] = le[0]
            enriched["number"] = number
            phonetic_rep = self.get_phonetic_rep(form)
            enriched["phonetic_rep"] = phonetic_rep
            trans = self.get_translatiosn(le[0])
            enriched["translations"] =trans
        return enriched

    def dbnary_enrichment_list(self, terms):
        enriched_terms = dict()
        for el in terms:
            enriched_terms[el] = self.dbnary_enrichment(el)

        return enriched_terms

