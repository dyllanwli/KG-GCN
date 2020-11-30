import pandas as pd
import numpy as np
import os
import json
from tqdm import tqdm
from pandas import json_normalize

# KG
import rdflib
import networkx as nx

import matplotlib.pyplot as plt
%matplotlib inline

# spacy
import spacy
from spacy.matcher import Matcher 
from spacy.tokens import Span 
from spacy.pipeline import TextCategorizer

# neo4j
from neo4j import GraphDatabase
from neo4j.exceptions import CypherSyntaxError


def name_entity_reco(s, nlp):
    doc = nlp(s)
    entities = [x.text for x in doc.ents if x.label_ not in filter_labels]
    
    # verbose
    # entities = []
    # for ent in doc.ents: 
    
    #     print(ent.text, ent.start_char, ent.end_char, ent.label_)
    return entities

def get_entity_pairs(sentences_list, nlp):
    """
    nlp: spacy model
    """
    entity_pairs = []
    for i in tqdm(sentences_list):
        e = name_entity_reco(i, nlp)
        entity_pairs.append(e)
    return entity_pairs

def get_relation(sents, nlp):
    """
    To build a KG, we need edges to connect the nodes to one another. 
    these edges are the relations between a pair of nodes

    here I just put a simple method to predicate the verb in the sentence to test the functionality
    """
    relations = []
    nospan = 0
    with tqdm(total=len(sents)) as pbar:
        for sent in sents:
            doc = nlp(sent)

            # init matcher
            matcher = Matcher(nlp.vocab)

            pattern = [{'DEP':'ROOT'}, 
                    {'DEP':'prep','OP':"?"},
                    {'DEP':'agent','OP':"?"},  
                    {'POS':'ADJ','OP':"?"}] 
            matcher.add("matching_1", None, pattern)


            matches = matcher(doc)
            k = len(matches) - 1
            try:
                span = doc[matches[k][1]:matches[k][2]]
            except:
                nospan +=1
            
            relations.append(span.text)
            pbar.update(1)
    print("nospan sentencesd:", nospan)
    return relations

def show_relations_count(relations):
    print(pd.Series(relations).value_counts()[:50])

def build_simple_kg(sentences_extend, nlp):
    print("getting entity pairs")
    ep = get_entity_pairs(sentences_extend, nlp)
    print("getting relations")
    relations = get_relation(sentences_extend, nlp)

    # build KG
    source = []
    target = []
    kg_relation = []
    for item_index in range(len(ep)):
        if len(ep[item_index]) == 2:
            x = ep[item_index]
            source.append(x[0])
            target.append(x[1])
            kg_relation.append(relations[item_index])

    kg_df = pd.DataFrame({'source': source, 'target': target, 'edge': kg_relation})
    kg_df['edge'] = kg_df['edge'].apply(lambda x: x.upper().replace(" ", "_"))
    # remove numeric edge
    kg_df = kg_df[~kg_df['edge'].apply(lambda x: x.isnumeric())]
    return ep, relations, kg_df

# then in this library we use networkx to visualize 
def plot_full_KG(kg_df):
    """
    triples with source, target and edge
    """
    G = nx.from_pandas_edgelist(kg_df, "source", "target", edge_attr=True, create_using=nx.MultiDiGraph())
    plt.figure(figsize=(12,12))

    # dictionary
    pos = nx.spring_layout(G)
    cmap = plt.cm.Blues
    nx.draw(G, with_labels=True, node_color="skyblue", edge_cmap=cmap, pos = pos)
    plt.show()

def plot_relation_KG(kg_df, relation, distance):
    G=nx.from_pandas_edgelist(kg_df[kg_df['edge']==relation], "source", "target", 
                            edge_attr=True, create_using=nx.MultiDiGraph())

    plt.figure(figsize=(12,12))
    # k regulates the distance between nodes
    pos = nx.spring_layout(G, k = distance)
    nx.draw(G, with_labels=True, node_color='skyblue', node_size=1500, edge_cmap=plt.cm.Blues, pos = pos)
    plt.show()


# handle neo4j session 
def test_print_friends(tx, name):
    for record in tx.run("MATCH (a:Person)-[:KNOWS]->(friend) WHERE a.name = $name "
                         "RETURN friend.name ORDER BY friend.name", name=name):
        print(record["friend.name"])


def test_add_friend(tx, name, friend_name):
    tx.run("MERGE (a:Person {name: $name}) "
           "MERGE (a)-[:KNOWS]->(friend:Person {name: $friend_name})",
           name=name, friend_name=friend_name)
    
def test_session(drive, row):
    with driver.session() as session:
        session.write_transaction(add_friend, row['source'], row['target'], row['edge'])

def add_edge(tx, source, target, edge):
    merge = "MERGE (source)-[:{edge}]->(target) ".format(edge=edge)
    cmd = (
        "MERGE (source:TestInstance {name: $source}) " +
        "MERGE (target:TestInstance { name: $target }) " + 
        merge)
    print(cmd)
    tx.run(cmd, source=source, target=target)
    
def run_session(driver, df):
    error_stack = []
    with driver.session() as session:
        l = df.shape[0]
        with tqdm(total=l) as pbar:
            for i in range(l):
                row = df.iloc[i]
                source, target, edge = row['source'], row['target'], row['edge']
                if edge not in filter_edges:
                    try:
                        session.write_transaction(add_edge, source, target, edge)
                    except CypherSyntaxError as e:
                        error_stack.append(e)
                pbar.update(1)
    return error_stack


nlp = spacy.load("en_core_web_lg")
model = opennre.get_model('wiki80_cnn_softmax')


umm_normalized_path = "/content/drive/MyDrive/Archive/NASA-CMR/UMM_DATA/cmr_normalized.csv"
df_umm = pd.read_csv(umm_normalized_path)

# df_umm.head()

abstract = df_umm['umm.Abstract']
sentences = [x.strip().replace("\r", "").replace("\n", "").split(". ") for x in abstract]
# extended sentences
sentences_extend = []
for s in sentences:
    sentences_extend.extend(s)
filter_labels = ["CARDINAL", "DATE"]

# Upload it to neo4j server // random generated by sandbox
driver = GraphDatabase.driver("bolt://52.91.160.133:33808", auth=("neo4j", "carloads-rinse-resources"))
# Neo4j Test
# use merge instad of create 
# https://stackoverflow.com/questions/22773562/difference-between-merge-and-create-unique-in-neo4j#:~:text=The%20easiest%20way%20to%20think,element%20means%20any%20unbound%20identifier.

filter_edges = ["*"]


if __name__ == "__main__":
    ep, relations, kg_df = build_simple_kg(sentences_extend, nlp)
    
    # plot_relation_KG(kg_df, "include", 0.5)
    error_stack = run_session(driver, kg_df)