
import networkx as nx
import re
import numpy
#parser = English()

def find_all_element(words,word):
    return [i for i,a in enumerate(words) if a == word]

def find_closest_index(locations,pl_e):
    distance = -1
    target = -1
    for index,value in enumerate(locations):
        if distance < 0 :
            distance = abs(value - pl_e)
            target = value
        elif abs(value-pl_e) < distance :
            distance = abs(value-pl_e)
            target = value

    return target


def get_entity_index(words,entity_e,pl_e):
    locations = find_all_element(words,entity_e[0])
    return find_closest_index(locations,pl_e)


# parse sentence
def  parse_sent(parser,sentence,entity_e1,pl_e1,entity_e2,pl_e2):
    # print(entity_e1)
    # print(pl_e1)
    # print(entity_e2)
    # print(pl_e2)
    parsedEx = parser(sentence)
    edges = []
    words = [None for i in range(100)]
    depend_path_struct={}
    for token in parsedEx:
        if words[token.head.i] is None:
            words[token.head.i] = token.head.orth_
        if words[token.i] is None:
            words[token.i] = token.orth_
        # print((token.head.orth_+'-'+str(token.head.i),token.head.dep_,token.orth_+'-'+str(token.i),token.dep_))
        depend_path_struct[token.head.orth_+'-'+str(token.head.i)]=token.head.dep_
        depend_path_struct[token.orth_+'-'+str(token.i)]=token.dep_
        edges.append((token.head.orth_+'-'+str(token.head.i),token.orth_+'-'+str(token.i)))

    # compute e1 , e2
    e1 = get_entity_index(words,entity_e1,pl_e1)
    # print(e1)
    e2 = get_entity_index(words,entity_e2,pl_e2)
    # print(e2)
    e1_item = entity_e1[0]+'-'+str(e1)
    e2_item = entity_e2[0]+'-'+str(e2)
    graph = nx.Graph(edges)
    path = nx.shortest_path(graph,source=e1_item,target=e2_item)
    dep_structure  = [depend_path_struct[item] for item in path if depend_path_struct[item] != 'compound']    
    path2 = [item.split('-')[0] for item in path]
    # sort entity_e2
    path3 = []
    for word in path2:
        if word not in entity_e2:
            path3.append(word)
    for word in entity_e2:
        path3.append(word)

    e1 = path3.index(entity_e1[0])
    e2 = path3.index(entity_e2[0])
    sent = ' '.join(path3)
    return sent,dep_structure

def preprocess_sent(sentence):
    # ' 's 't
    strip_list = ['\n','\"','.']
    replace_list = [',',';','\'']
    delete_list = ['-','\"',':','%','(',')','.','\'t','!','$']
    # delete_list = ['-','\"',':','%','(',')','\'t','!','$']
    for strip in strip_list:
        sentence = sentence.strip(strip)
    for replace in replace_list:
        sentence = sentence.replace(replace,' '+replace)
    for delete in delete_list:
        sentence = sentence.replace(delete,' ')

    return ' '.join(sentence.split())


# get e1,e2 position
def  getShortestPath(parser,sentence,ent1,ent2):
    sent = preprocess_sent(sentence)
    ent1=preprocess_sent(ent1)
    ent2=preprocess_sent(ent2)
    entity_e1 = ent1.split()
    entity_e2 = ent2.split()
    words = sent.split()
    try:
        e1 = words.index(entity_e1[0])
        e2 = words.index(entity_e2[0])
    except Exception as e:
        e1=-1
        e2=-1
        # print "Error:",e
        # print(sent)
        # print entity_e1,entity_e2
        # print "\n"

    # dependency path
    path = sentence.strip('\n').strip('.').strip('\"')
    dep_structure = []
    try:
        path,dep_structure = parse_sent(parser,sent,entity_e1,e1,entity_e2,e2)
        path = re.sub(ent1, '', path)
        path = re.sub(ent2, '', path)
    except Exception as e:
        dep_structure = []
        # print "Error:",e
        # print(sent)
        # print entity_e1,entity_e2
        # print "\n"
        # pass
    return  path,dep_structure


