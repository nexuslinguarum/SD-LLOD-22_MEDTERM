#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 19:39:25 2020

@author: pmchozas
"""
import requests
import json
import re

def enrich_term_stw(myterm):
    get_uri(myterm)
    get_definition(myterm)
    get_relations(myterm)
    get_synonyms(myterm)
    get_translations(myterm)
    create_intermediate_ids(myterm)
    return myterm

def get_uri(myterm): #recoge la uri del termino a buscar
    term='"^'+myterm.term+'$"'
    lang='"'+myterm.langIn+'"'
    plural='"^'+myterm.term+'s'+'$"'
    try:
        url = ("http://sparql.lynx-project.eu/")
        query = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?c ?label
        WHERE   {
        GRAPH <http://lkg.lynx-project.eu/stw> {
        ?c a skos:Concept .
        ?c ?p ?label. 
          FILTER regex(?label, """+term+""", "i" )
          FILTER (lang(?label) = """+lang+""")
          FILTER (?p IN (skos:prefLabel, skos:altLabel ) )
      
        }
        
        }
        """
        print(query)

        r=requests.get(url, params={'format': 'json', 'query': query})
        results=json.loads(r.text)
        
        
        if (len(results["results"]["bindings"])==0):
            print('CHECK PLURAL')
            try:
                url = "http://sparql.lynx-project.eu/"
                query = """
                    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                    SELECT ?c ?label ?prefEN
                    WHERE {
                    GRAPH <http://lkg.lynx-project.eu/stw> {
                    ?c a skos:Concept .
                    ?c ?p ?label. 
                    ?c skos:prefLabel ?prefEN.
                      FILTER regex(?label, """+plural+""", "i")
            
                      
                      FILTER (lang(?prefEN) = """+lang+""")
            
                      FILTER (?p IN ( skos:prefLabel, skos:altLabel ) )
                      
            
                    }  
                    }
                    """
                print(query)    
                r=requests.get(url, params={'format': 'json', 'query': query})
                results=json.loads(r.text)
                
                if('results' in results.keys()):
                    results2=results['results']
                    bindings=results2['bindings']
                    for b in range(len(bindings)):
                        myterm.stw_id=bindings[b]['c']['value']
            except: 
                print('no plural')
        else:
            for result in results["results"]["bindings"]:
                answeruri=result["c"]["value"]
                #answerl=result["label"]["value"]
                myterm.stw_id=answeruri
    except:
        print('no term')
    
    return myterm

def get_definition(myterm): #recoge la definicion de la uri de entrada si la hay
    try:
        definition=''
        url=("http://sparql.lynx-project.eu/")
        term='"^'+myterm.term+'$"'
        lang='"'+myterm.langIn+'"'
        query="""
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            SELECT ?c ?label
            WHERE {
            GRAPH <http://lkg.lynx-project.eu/stw> {
            VALUES ?c { <"""+term+"""> }
            VALUES ?searchLang { """+lang+""" undef } 
            VALUES ?relation { skos:definition  } 
            ?c a skos:Concept . 
            ?c ?relation ?label . 
            filter ( lang(?label)=?searchLang )
            }
            }
            """
        r=requests.get(url, params={'format': 'json', 'query': query})
        results=json.loads(r.text)
        if (len(results["results"]["bindings"])==0):
            definition=''
        else:
            for result in results["results"]["bindings"]:
                definition=result["label"]["value"]
                myterm.definitions_stw[myterm.langIn]=definition
                
    except json.decoder.JSONDecodeError:
        pass

    return(myterm)


def get_relations(myterm): #recoge la uri de la relacion a buscar 
    reltypes=['broader', 'narrower', 'related']
    try:
        for rel in reltypes:
            if rel not in myterm.stw_relations:
                myterm.stw_relations[rel]=[]
                url=("http://sparql.lynx-project.eu/")
                query="""
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                SELECT ?c ?label
                WHERE {
                GRAPH <http://lkg.lynx-project.eu/stw> {
                VALUES ?c {<"""+myterm.stw_id+"""> }
                VALUES ?relation { skos:"""+rel+""" } 
                ?c a skos:Concept .
                ?c ?relation ?label .    
                }  
                }
                """

                r=requests.get(url, params={'format': 'json', 'query': query})
                results=json.loads(r.text)

    
                if (len(results["results"]["bindings"])==0):
                        answerRel=''
                else:
                    for result in results["results"]["bindings"]:
                        answerRel=result["label"]["value"]
                        if rel == 'broader':                         
                            myterm.stw_relations[rel].append(answerRel)
                        elif rel == 'narrower':                         
                            myterm.stw_relations[rel].append(answerRel)
                        elif rel == 'related':                          
                            myterm.stw_relations[rel].append(answerRel)
                        else: 
                            continue
    
    
                #         name=name_term_eurovoc(answerRel,lang,'prefLabel')
                #         answer.append([answerRel, name, relation])
    except json.decoder.JSONDecodeError:
        pass
    
    return(myterm)

def get_synonyms(myterm): #recoge sinónimos
    try:
        nameUri=''
        label="altLabel"
        lang='"'+myterm.langIn+'"'
        url=("http://sparql.lynx-project.eu/")
        query="""
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?c ?label
        WHERE {
        GRAPH <http://lkg.lynx-project.eu/stw> {
        VALUES ?c { <"""+myterm.stw_id+"""> }
        VALUES ?searchLang { """+lang+""" undef } 
        VALUES ?relation { skos:"""+label+"""  } 
        ?c a skos:Concept . 
        ?c ?relation ?label . 
        filter ( lang(?label)=?searchLang )
        }
        }
        """
        
        r=requests.get(url, params={'format': 'json', 'query': query})
        results=json.loads(r.text)
        if (len(results["results"]["bindings"])==0):
                nameUri=''
        else:
            for result in results["results"]["bindings"]:
                nameUri=result["label"]["value"]
                if nameUri != myterm.term:
                    myterm.synonyms_stw.append(nameUri)

    except json.decoder.JSONDecodeError:
        pass
        
      
    return(nameUri)

def get_translations(myterm): #recoge traducciones
    for lang in myterm.langOut:
            if lang not in myterm.translations_stw:
                myterm.translations_stw[lang]=[]
                try:
                    lang1='"'+lang+'"'
                    url=("http://sparql.lynx-project.eu/")
                    labels=['prefLabel','altLabel']
                    for label in labels:
                        query="""
                        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                        SELECT ?c ?label
                        WHERE {
                        GRAPH <http://lkg.lynx-project.eu/stw> {
                        VALUES ?c { <"""+myterm.stw_id+"""> }
                        VALUES ?searchLang { """+lang1+""" undef} 
                        VALUES ?relation { skos:"""+label+"""  } 
                        ?c a skos:Concept . 
                        ?c ?relation ?label . 
                        filter ( lang(?label)=?searchLang )
                        }
                        }
                        """
                        r=requests.get(url, params={'format': 'json', 'query': query})
                        results=json.loads(r.text)
                        
        
                        if (len(results["results"]["bindings"])==0):
                                trans=''
                        else:
                            for result in results["results"]["bindings"]:
                                trans=result["label"]["value"]
                                myterm.translations_stw[lang].append(trans)
                           
            
                except: 
                    continue
        
      
    return(myterm)

def create_intermediate_ids(myterm):
    chars=['\'', '\"', '!', '<', '>', ',', '(', ')', '.']
    schema=myterm.schema.lower()
    if ' ' in schema:
        schema=schema.replace(' ', '-')
    for char in chars:
        schema=schema.replace(char, '')
    if len(myterm.synonyms_stw)>0:
        myterm.synonyms['stw']={}
        myterm.synonyms_ontolex['stw']={}
        myterm.synonyms['stw'][myterm.langIn]=[]   
        myterm.synonyms_ontolex['stw'][myterm.langIn]=[]
        for term in myterm.synonyms_stw:            
            syn_set = {}          
            syn = term
            if ' ' in syn:
                syn=syn.replace(' ', '-')
            for char in chars:
                syn=syn.replace(char, '')
            synid=schema+'-'+syn+'-'+myterm.langIn
            syn_set['syn-id']=synid.lower()
            syn_set['syn-value']=syn.replace('-', ' ')
            myterm.synonyms['stw'][myterm.langIn].append(syn_set)
            myterm.synonyms_ontolex['stw'][myterm.langIn].append(syn_set)
            
            
    if len(myterm.translations_stw)>0:
        myterm.translations['stw']={}
        myterm.translations_ontolex['stw']={}
        for lang in myterm.langOut:
            if lang in myterm.translations_stw.keys():
                myterm.translations['stw'][lang]=[]   
                myterm.translations_ontolex['stw'][lang]=[]
                for term in myterm.translations_stw[lang]:
                    trans_set = {}
                    if ' 'in term:
                        term=term.replace(' ', '-')
                    for char in chars:
                        term=term.replace(char, '')
                    transid=schema+'-'+term+'-'+lang
                    trans_set['trans-id']=transid.lower()
                    trans_set['trans-value']=term.replace('-', ' ')
                    myterm.translations_ontolex['stw'][lang].append(trans_set)
                    if len(myterm.translations['stw'][lang])<=0:
                        myterm.translations['stw'][lang].append(trans_set)
                    else:
                        if 'stw' in myterm.synonyms:
                            if lang in myterm.synonyms['stw']:
                                myterm.synonyms['stw'][lang].append(trans_set)
                            else:
                                myterm.synonyms['stw'][lang]=[]
                                myterm.synonyms['stw'][lang].append(trans_set)
                        else:
                            myterm.synonyms['stw']={}
                            myterm.synonyms['stw'][lang]=[]
                            myterm.synonyms['stw'][lang].append(trans_set)
    
    if len(myterm.definitions_stw)>0:
        myterm.definitions['stw']={}
        for lang in myterm.definitions_stw.keys():
            myterm.definitions['stw'][lang]=[]
            for defi in myterm.definitions_stw[lang]:
                def_set = {}
                defid=myterm.term+'-'+lang+'-def'
                def_set['def-id']=defid.lower()
                def_set['def-value']=defi
                myterm.definitions['stw'][lang].append(def_set)

    return myterm