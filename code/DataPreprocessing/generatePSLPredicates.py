#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import enchant
from nltk.metrics import edit_distance
import re
import time
import io
import editdistance
from pymagnitude import *
import networkx as nx
import spacy_parser
import spacy 
import pandas as pd
import numpy as np
from multiprocessing import Pool
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn
mag_vectors = Magnitude("./magnbase/GoogleNews-vectors-negative300.magnitude")
# dependency_vectors = FeaturizerMagnitude(100, namespace = "SyntaxDependencies")

nlp = spacy.load('en')
stops_words = set(stopwords.words("english"))
wnl = WordNetLemmatizer()
_dir='test'

def penn_to_wn(tag):
    """ Convert between a Penn Treebank tag to a simplified Wordnet tag """
    if tag.startswith('N'):
        return 'n'
 
    if tag.startswith('V'):
        return 'v'
 
    if tag.startswith('J'):
        return 'a'
 
    if tag.startswith('R'):
        return 'r'
 
    return None
 
def tagged_to_synset(word, tag):
    wn_tag = penn_to_wn(tag)
    if wn_tag is None:
        return None
 
    try:
        return wn.synsets(word, wn_tag)[0]
    except:
        return None

def preprocessForSimilarScore(short_dep_path):
    sentence=''
    arr = short_dep_path.split(' ')
    cleaned_words = [w for w in arr if not w in stops_words] # Remove stop words
    cleaned_words = [w for w in cleaned_words if w!=' ' and w!=''] # Remove stop words
    corrected_words = [spellingCorrection(w) for w in cleaned_words] # words
    cleaned_words=list(set(corrected_words))
    if len(cleaned_words)>0 and len(cleaned_words)<15:
        sentence=" ".join(cleaned_words) 
        # synsets = pos_tag(word_tokenize(sentence))
        # synsets = [tagged_to_synset(*tagged_word) for tagged_word in sentence]
        # synsets = [ss for ss in synsets if ss]
    return sentence

def sentence_similarity(sentence1, sentence2):
    """ compute the sentence similarity using Wordnet """
    # # Tokenize and tag

    sentence1 = pos_tag(word_tokenize(sentence1))
    sentence2 = pos_tag(word_tokenize(sentence2))
 
    # Get the synsets for the tagged words
    synsets1 = [tagged_to_synset(*tagged_word) for tagged_word in sentence1]
    synsets2 = [tagged_to_synset(*tagged_word) for tagged_word in sentence2]
 
    # Filter out the Nones
    synsets1 = [ss for ss in synsets1 if ss]
    synsets2 = [ss for ss in synsets2 if ss]
 
    score, count = 0.0, 0
 
    # For each word in the first sentence
    for synset in synsets1:
        # Get the similarity value of the most similar word in the other sentence
        values = [synset.path_similarity(ss) for ss in synsets2]
        if values:
            best_score = max(values)
        else:
            best_score=None
 
        # Check that the similarity could have been computed
        if best_score is not None:
            score += best_score
            count += 1
 
    # Average the values
    if count!=0:
        score /= count
    return score
 
def parallelize_dataframe(df, func):
    num_partitions = 10 #number of partitions to split dataframe
    num_cores = 2 #number of cores on your machine
    df_split = np.array_split(df, num_partitions)
    pool = Pool(num_cores)
    df = pd.concat(pool.map(func, df_split))
    pool.close()
    pool.join()
    return df

def spellingCorrection(word):
#spelling correction using enchant dictionary
    dict_name='en'
    max_dist=1
    spell_dict = enchant.Dict(dict_name)
    max_dist = max_dist
    if spell_dict.check(word):
        return word
    suggestions = spell_dict.suggest(word)
    if suggestions and edit_distance(word, suggestions[0]) <= max_dist:
        return suggestions[0]
    else:
        return word

def normalize(d, target=1.0):
    #max_value = max(d.values())
    factor = 0.1 #target/max_value
    norm_d={}
    for key,value in d.iteritems():
        score=1.0-value*factor
        norm_d[key]=score
        if value>12:
            norm_d[key]=0.0
        # else:
        #     if value<6:
        #         norm_d[key]=1.0
            # else:
            #     norm_d[key]=0.0

    return norm_d

# def dependPathSimilarity(short_dep_path1, short_dep_path2):
#     short_dep_path_1 = short_dep_path1.split(' ')
#     short_dep_path_2 = short_dep_path2.split(' ')
#     sim_array = mag_vectors.similarity(short_dep_path_1,short_dep_path_2)
#     sim_value=0
#     for arr in sim_array:
#         val = np.nanmax(arr)
#         sim_value+=val
#     return sim_value

def dependPathSimilarity(short_dep_path1, short_dep_path2):
    # short_dep_path_1 = short_dep_path1.split(' ')
    # short_dep_path_2 = short_dep_path2.split(' ')
    # sim_array = mag_vectors.similarity(short_dep_path_1,short_dep_path_2)
    # sim_value=0
    # for arr in sim_array:
    #     val = np.mean(arr)
    #     sim_value+=val
    return (sentence_similarity(short_dep_path1, short_dep_path2) + sentence_similarity(short_dep_path2, short_dep_path1)) / 2 

def dependPathStructureSimilarity(dep_path1, dep_path2):
    union = list(set(dep_path1+dep_path2))
    intersection = list(set(dep_path1) - (set(dep_path1)-set(dep_path2)))
    # print "Union - %s" % union
    # print "Intersection - %s" % intersection
    jaccard_coeff = float(len(intersection))/len(union)
    # print "Jaccard Coefficient is = %f " % jaccard_coeff

    # sim_array = dependency_vectors.similarity(dep_path1,dep_path2)
    # sim_value=0
    # for arr in sim_array:
    #     val = np.mean(arr)
    #     sim_value+=val
    return jaccard_coeff

def similarityScoreGloveSimilarity(word_set1,word_set2):
    word_set1=list(set(word_set1))
    word_set2=list(set(word_set2))
    word_arr_1=[]
    word_arr_2=[]
    sumScore=0
    verbSimScore=0
    for w in word_set1:
        if w  in mag_vectors:
            word_arr_1.append(w)

    for w in word_set2:
        if w  in mag_vectors:
            word_arr_2.append(w)

    if len(word_arr_2)>0 and len(word_arr_1)>0:
        for w1 in word_arr_1:
            for w2 in word_arr_2:
                if w1==w2:
                    dist=1.0
                else:
                    dist = mag_vectors.similarity(w1,w2)
                #print w1,w2,dist
                sumScore += dist
        verbSimScore = sumScore/(len(word_arr_2)*len(word_arr_1))
        #print word_set1,word_set2,verbSimScore
    return verbSimScore

def check_string(string, substring_list):
    for substring in substring_list:
        if substring in string:
            return True
    return False

def check_string_over(string1, string2):
    string_arr_1=string1.split(',')
    string_arr_2=string2.split(',')
    for substring_1 in string_arr_1:
        for substring_2 in string_arr_2:
            if substring_1 in substring_2:
                return True
    return False

def sameEntityTypes(rm1,rm2):
    return True
    ent2type={}
    ent2type_2={}
    for item in rm1['entityTypes']:
        if rm1['relation']['em1Text'] in item:
            ent2type[rm1['relation']['em1Text']]=item[rm1['relation']['em1Text']]['label']
        if rm1['relation']['em2Text'] in item:
            ent2type[rm1['relation']['em2Text']]=item[rm1['relation']['em2Text']]['label']
    
    for item in rm2['entityTypes']:
        if rm2['relation']['em1Text'] in item:
            ent2type_2[rm2['relation']['em1Text']]=item[rm2['relation']['em1Text']]['label']
        if rm2['relation']['em2Text'] in item:
            ent2type_2[rm2['relation']['em2Text']]=item[rm2['relation']['em2Text']]['label']
    
    if rm1['relation']['em1Text'] in ent2type and rm2['relation']['em1Text'] in ent2type_2 and rm1['relation']['em2Text'] in ent2type and rm2['relation']['em2Text'] in ent2type_2:
        if (ent2type[rm1['relation']['em1Text']]==ent2type_2[rm2['relation']['em1Text']] and 
        ent2type[rm1['relation']['em2Text']]==ent2type_2[rm2['relation']['em2Text']]) and ent2type[rm1['relation']['em1Text']]=='PERSON':
            return True
    return False

def findEntityType(ent1, ent2,entityMentions):
    entityType = []
    for em in entityMentions:
        for ent in [ent1,ent2]:
            if em['text']==ent:
                entityType.append({em['text']:{'label':em['label'],'st_label':em['st_label']}})
    return entityType

def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))

def getDependPath(word,depend_tree_2,dep_tree):
    path = 0
    path_tree=[]
    depend_tree={}
    word = word.split("-")[0]
    if word in depend_tree_2: # if current word already in prev dependency tree => path connected
        return path_tree,path

    while word in dep_tree and dep_tree[word][0] != 'ROOT' and word not in path_tree:
        prev_word = word
        word = dep_tree[prev_word][1]
        path_tree.append(prev_word)
        depend_tree[word] = dep_tree[prev_word][0]
        path+=1
        if word in depend_tree_2:
            break
    path_tree.append(word)
#   path_tree = list(set(path_tree) - set(intersection_set))
    return path_tree,path

def closestVerb(entity,dep_tree,verbs):
    path_tree=[]
    word = entity.split(" ")[0]
    word = word.split("-")[0]
    while word in dep_tree and dep_tree[word][1] != 'ROOT' and word not in path_tree and word not in verbs:
        path_tree.append(word)
        word = dep_tree[word][1]
    return word
  
#  =====   PSL OBSERVATIONS ======
 
def predicateVerbSimilarity(relMention,relMention_2):
    score=0.0
    verbs_1 = relMention['verbs']
    verbs_2 = relMention_2['verbs']
    if len(relMention['depen_struct'])>0 and len(relMention_2['depen_struct'])>0 and len(relMention['depen_struct'])<11 and len(relMention_2['depen_struct'])<11:
        if len(verbs_1)>0 and len(verbs_2)>0:
            score = similarityScoreGloveSimilarity(verbs_1,verbs_2)
        if score>0.6:
            if score>1.0:
                score=1.0
            with open(outdir+'/verbsSimilarity_obser.txt', 'a') as predFile:
                predFile.write(relMention['rm_id']+'\t'+relMention_2['rm_id']+'\t'+str(score)+'\n')
        else:
            score = 0.0

        with open(outdir+'/mln_model.db', 'a') as mln_db:
            if score==0.0:
                mln_db.write('!SimilarVerb(p'+relMention['rm_id']+',p'+relMention_2['rm_id']+')\n')
            else:
                mln_db.write('SimilarVerb(p'+relMention['rm_id']+',p'+relMention_2['rm_id']+')\n')

    return score
 
def predicateDependPathSimilarity(relMention,relMention_2):
    score=0.0
    word_set_1 = relMention['short_path_cleaned']
    word_set_2 = relMention_2['short_path_cleaned']
    if len(word_set_1)>0 and len(word_set_2)>0:
        score = dependPathSimilarity(word_set_1,word_set_2)
        if score>0.4:
            if score>1.0:
                score=1.0
            with open(outdir+'/depenPathSimilarity_obser.txt', 'a') as predFile:
                predFile.write(relMention['rm_id']+'\t'+relMention_2['rm_id']+'\t'+str(score)+'\n')
        else:
            score = 0.0

        with open(outdir+'/mln_model.db', 'a') as mln_db:
            if score==0.0:
                mln_db.write('!SimilarDepenPath(p'+relMention['rm_id']+',p'+relMention_2['rm_id']+')\n')
            else:
                mln_db.write('SimilarDepenPath(p'+relMention['rm_id']+',p'+relMention_2['rm_id']+')\n')

    return score

def predicateDependPathStructureSimilarity(relMention,relMention_2):
    score=0.0
    struct_path = relMention['depen_struct']
    struct_path_2 = relMention_2['depen_struct']
    if len(struct_path)>0 and len(struct_path_2)>0 and len(struct_path)<11 and len(struct_path_2)<11:
        score = dependPathStructureSimilarity(struct_path,struct_path_2)
    if score>0.6:
        if score>1.0:
            score=1.0
        with open(outdir+'/depenStructureSimilarity_obser.txt', 'a') as predFile:
            predFile.write(relMention['rm_id']+'\t'+relMention_2['rm_id']+'\t'+str(score)+'\n')
    else:
        score = 0.0

    with open(outdir+'/mln_model.db', 'a') as mln_db:
        if score==0.0:
            mln_db.write('!SimilarDepenStructure(p'+relMention['rm_id']+',p'+relMention_2['rm_id']+')\n')
        else:
            mln_db.write('SimilarDepenStructure(p'+relMention['rm_id']+',p'+relMention_2['rm_id']+')\n')

    return score
# ===============
## create file relation_mentions simillar to original (cotype) but with relationf from freebase
## add true_label to compare generated labels against original from cotype
## add  indexId = enumeration of original sentences

def loadTargetTypes(filename):
  map = {}
  with open(filename, 'r') as fin:
    for line in fin:
      seg = line.strip('\r\n').split('\t')
      fbType = seg[0]
      cleanType = seg[1]
      map[fbType] = cleanType
  return map
 
def pslFeaturesGeneration(row):
    entityMentions=[]
    spacy_doc = nlp(row['sentText'])
    
    sys.stdout.write("Processed %d, Time: %d sec\r" % (row['indexId'],  time.time() - start))
    sys.stdout.flush()
##### if entities are subject or object 
    entities = row['relation']['em1Text'].split(" ")
    entities+= row['relation']['em2Text'].split(" ")
    ent_array=[]
    for entity in entities:
        ent = entity.split("-")
        ent_array+=ent
    ent_array=list(set(ent_array))
    score=0.0
    verbs=set()
    dep_path={}
    for word in spacy_doc:
        dep_path[word.text.encode('utf8')] = [word.dep_.encode('utf8'),word.head.text.encode('utf8')]
        if word.pos_=="VERB":
            verbs.add(word.text)
        if word.text in ent_array:
            if check_string(word.dep_,['subj','obj']):
                score+=0.5          
    if score>1.0:
        score=1.0
    row['nouns_type'] =score
###common words    
    em1Text = row['relation']['em1Text'].split(" ")[0]
    em2Text = row['relation']['em2Text'].split(" ")[0]
    depend_tree_1,path_len=getDependPath(em1Text,verbs,dep_path) #  
    depend_tree_2,path_len_2=getDependPath(em2Text,verbs,dep_path) #  
    depend_tree = depend_tree_1+depend_tree_2
    common_words_arr= list(set(depend_tree))
    row['common_words']=''
    if len(common_words_arr)>0:
        result=  " ".join(common_words_arr)
        row['common_words']=re.sub(","," ",result)
### if entities's verbs are similar
    score=0.0
    verb_1 = closestVerb(row['relation']['em1Text'],dep_path,verbs)
    verb_2 = closestVerb(row['relation']['em2Text'],dep_path,verbs)
    if verb_1==verb_2:
        score = 1.0
    row['ent_verbs_sim'] =score

####  the shortest dependency path
    short_dep_path, depend_structure = spacy_parser.getShortestPath(nlp,row['sentText'],row['relation']['em1Text'],row['relation']['em2Text'])
#### use verbs from the shortest depend path 
    verbs_rm = []
    for word in common_words_arr:
        if word in verbs:
            verbs_rm.append(word)
    cleaned_words = [w for w in verbs_rm if not w in stops_words] # Remove stop words
    corrected_words = [spellingCorrection(w) for w in cleaned_words] # words
    word_set = [wnl.lemmatize(w, pos='v') for w in corrected_words] # words
    cleaned_verbs=list(set(word_set))
    row['verbs']=cleaned_verbs
### depend path length
    row['path_length']=len(short_dep_path.split(' '))
### common words from dependency tree
    row['short_dep_path']=short_dep_path
    row['depen_struct'] =depend_structure

    short_dep_path = short_dep_path.replace(row['relation']['em1Text'], '')
    short_dep_path = short_dep_path.replace(row['relation']['em2Text'], '')
    words_array = short_dep_path.split(' ')
    short_path_cleaned=''
    if len(words_array)<20:
    	cleaned_words = [w for w in words_array if not w in stops_words] # Remove stop words
    	cleaned_words = [w for w in cleaned_words if w!=' ' and w!=''] # Remove stop words
    	corrected_words = [spellingCorrection(w) for w in cleaned_words] # words
    	short_path_cleaned=list(set(corrected_words))
    row['short_path_cleaned'] = " ".join(short_path_cleaned)
    # if len(short_dep_path)>0:
    #     row['short_dep_path']=  " ".join(short_dep_path)
    # print spacy_doc
    # print row['relation']['em1Text'],row['relation']['em2Text']
    # print 'short_dep_path:',row['short_dep_path']
    # print 'common words:',  row['common_words']
    # print 'depend_structure:',depend_structure
    # print 'verbs:',cleaned_verbs
    return row

def pandaFeatureGeneralization(data):
    data = data.apply(pslFeaturesGeneration, axis=1)
    return data
    #generate features
  
def parallelize_array(data, func):
    num_partitions = 10 #number of partitions to split dataframe
    num_cores = 2 #number of cores on your machine
    df_split = np.array_split(data, num_partitions)
    print len(df_split)
    pool = Pool(num_cores)
    pool.map(func, df_split)
    pool.close()
    pool.join()
    return data

def similarityVerbCalculation(new_relationMentions_verbs):
    num_rel= len(new_relationMentions_verbs)
    number_of_neigbors_verb=0
    start = time.time()
    for i, rm1 in enumerate(new_relationMentions_verbs):
        for j, rm2 in enumerate(new_relationMentions_verbs):
            if j>i:
                if rm1['rm_id'] != rm2['rm_id']:
                    if sameEntityTypes(rm1,rm2):
                        verb_score = predicateVerbSimilarity(rm1,rm2)
                        if verb_score>0.0:
                            number_of_neigbors_verb+=1
                        if number_of_neigbors_verb>25:
                            number_of_neigbors_verb=0
                            break
                sys.stdout.write("Compare %d and %d / %d, Time: %d sec\r" % (i,j,num_rel,  time.time() - start))
                sys.stdout.flush()
    print '\n'

def similarityCalculation(new_relationMentions):
    start = time.time()
    number_of_neigbors_depen=0
    number_of_neigbors_struct=0
    stop_struc = False
    stop_depen =False
    num_rel= len(new_relationMentions)
    for i, rm1 in enumerate(new_relationMentions):
        stop_depen=False
        stop_struc=False
        for j, rm2 in enumerate(new_relationMentions):
            depen_score=0
            struc_score=0
            if j>i:
                if rm1['rm_id'] != rm2['rm_id']:
                    if sameEntityTypes(rm1,rm2):  
                        if stop_depen==False:
                       		depen_score=predicateDependPathSimilarity(rm1,rm2)
                        if stop_struc==False:
                            struc_score=predicateDependPathStructureSimilarity(rm1,rm2)                                

                        if struc_score>0.0:
                            number_of_neigbors_struct+=1
                        if number_of_neigbors_struct>25:
                            number_of_neigbors_struct=0
                            stop_struc=True
                        
                        if depen_score>0.0:
                            number_of_neigbors_depen+=1
                        if number_of_neigbors_depen>10:
                            number_of_neigbors_depen=0
                            stop_depen=True

                        if stop_depen and stop_struc: #stop_depen  and stop_struc:
                            break
                        sys.stdout.write("Compare %d and %d / %d, Time: %d sec\r" % (i,j,num_rel,  time.time() - start))
                        sys.stdout.flush()
    print '\n'

def MLNPredicates(value,text):
    if float(value)==1.0:
        return text
    else:
        return '!'+text

## ganerate predicates and /data/candidate_rm.json with all relations separatelly
def pslPredicateGeneration(outdir,jsonFname,featuresFile):
    # print "Generate features ...."
    # start=time.time()
    # data_pd = pd.read_json(jsonFname, lines=True)
    # data_pd = data_pd.apply(pslFeaturesGeneration, axis=1)
    # # data_pd = parallelize_dataframe(data_pd, pandaFeatureGeneralization)
    # data_pd.reset_index().to_json(featuresFile,orient='records', lines=True, default_handler=str)
    # # # count = 0
    # # with open(featuresFile, 'r') as fin:
    # #     for line in fin:
    # #         relMention = json.loads(line.strip('\r\n'))
    # #         if relMention['relation']['true_label']!='None':
    # #             pslFeaturesGeneration(relMention)
    # #             count+=1
    # #             if count>10:
    # #                 exit()
    # print("Finished. Time: %d sec\r" % (time.time() - start) )
    print "Write to files...."
    start=time.time()

    with open(outdir+'/relationTypes.txt', 'r') as rel_type:
        relationTypes = rel_type.readlines()
    #write to files 
    new_relationMentions=[]
    new_relationMentions_verbs=[]
    rmDependPath = {}
    relation_arr = []
    index = 0
    with open(outdir+'/verbsSimilarity_obser.txt', 'w') as sim1,\
    open(outdir+'/depenPathSimilarity_obser.txt', 'w') as sim2,\
    open(outdir+'/depenStructureSimilarity_obser.txt', 'w') as sim3:
        sim1.close()
        sim2.close()
        sim3.close()

    with open(outdir+'/commonWords_obser.txt', 'w') as commonWordsFile,\
    open(outdir+'/HasDirectDependency_obser.txt', 'w') as hasDirectDependencyFile,\
    open(outdir+'/HasSimilarEntityVerbs_obser.txt', 'w') as hasSimilarEntityVerbsFile,\
    open(outdir+'/ShortDependPath_obser.txt', 'w') as shortDependPathFile,\
    open(outdir+'/HasRel_true.txt', 'w') as trueFile,\
    open(outdir+'/CandRel_obser.txt', 'w') as candRelFile,\
    open(outdir+'/CandRel_target.txt', 'w') as targetFile,\
    open(outdir+'/Ent1SpaCyType.txt', 'w') as ent1type, \
    open(outdir+'/Ent2SpaCyType.txt', 'w') as ent2type,\
    open(outdir+'/Ent1StanType.txt', 'w') as ent1type_st, \
    open(outdir+'/Ent2StanType.txt', 'w') as ent2type_st,\
    open(outdir+'/isTitleEnt1.txt', 'w') as ent1cap, \
    open(outdir+'/isTitleEnt2.txt', 'w') as ent2cap,\
    open(outdir+'/mln_model.db', 'w') as mln_db,\
    open(featuresFile, 'r') as fin:
        start = time.time()
        for line in fin:
            relMention = json.loads(line.strip('\r\n'))
            relation_arr.append(relMention)
            rmDependPath[relMention['rm_id']]=relMention['path_length']
            commonWordsFile.write(relMention['rm_id']+'\t'+str(relMention['common_words'])+'\n')
            hasDirectDependencyFile.write(relMention['rm_id']+'\t'+str(relMention['nouns_type'])+'\n')
            hasSimilarEntityVerbsFile.write(relMention['rm_id']+'\t'+str(relMention['ent_verbs_sim'])+'\n')


            mln_db.write(MLNPredicates(relMention['nouns_type'],'HasDirectDependency(p'+relMention['rm_id']+')\n'))
            mln_db.write(MLNPredicates(relMention['ent_verbs_sim'],'HasSimilarEntityVerbs(p'+relMention['rm_id']+')\n'))

            if relMention['path_length']>8:
                mln_db.write('!DependencyPathLength(p'+relMention['rm_id']+')\n')
            else:
                if len(relMention['depen_struct'])>0:
                    mln_db.write('DependencyPathLength(p'+relMention['rm_id']+')\n')
                else:
                    mln_db.write('!DependencyPathLength(p'+relMention['rm_id']+')\n')

            if len(relMention['short_dep_path'])>0 and len(relMention['depen_struct'])>0:
                sentence=str(relMention['short_dep_path']).replace(" ", "")
                if sentence!='':
                    shortDependPathFile.write(relMention['rm_id']+'\t'+str(relMention['short_dep_path'])+'\n')


                    if not check_string_over('died,dead,dies,death,die', relMention['short_dep_path']):
                        mln_db.write('!HasWordsShortDependPath(p'+relMention['rm_id']+',death_words)\n')
                    if not check_string_over('born,birth,native', relMention['short_dep_path']):
                        mln_db.write('!HasWordsShortDependPath(p'+relMention['rm_id']+',birth_words)\n')
                    if check_string_over('rear,raise,lived,live,moved,move,work,home,lives', relMention['short_dep_path']):
                        mln_db.write('!HasWordsShortDependPath(p'+relMention['rm_id']+',lived_words)\n')
                    if not check_string_over('son,daughter,child,mother,father,parent', relMention['short_dep_path']):
                        mln_db.write('!HasWordsShortDependPath(p'+relMention['rm_id']+',children_words)\n')
                    if not check_string_over('found,founded,founde', relMention['short_dep_path']):
                        mln_db.write('!HasWordsShortDependPath(p'+relMention['rm_id']+',founders_words)\n')
                    if not check_string('enrol,study,complete,graduate,attend,studied,complete,alumni,university,institute,graduate,school', relMention['short_dep_path']):
                        mln_db.write('!HasWordsShortDependPath(p'+relMention['rm_id']+',institution_words)\n')
                    if not check_string('bachelor,master,doctor,received', relMention['short_dep_path']):
                        mln_db.write('!HasWordsShortDependPath(p'+relMention['rm_id']+',degree_words)\n')


                    if check_string_over('died,dead,dies,death,die', relMention['short_dep_path']):
                        mln_db.write('HasWordsShortDependPath(p'+relMention['rm_id']+',death_words)\n')
                    if check_string_over('born,birth,native', relMention['short_dep_path']):
                        mln_db.write('HasWordsShortDependPath(p'+relMention['rm_id']+',birth_words)\n')
                    if check_string_over('rear,raise,lived,live,moved,move,work,home,lives', relMention['short_dep_path']):
                        mln_db.write('HasWordsShortDependPath(p'+relMention['rm_id']+',lived_words)\n')
                    if check_string_over('of', relMention['short_dep_path']):
                        mln_db.write('HasWordsShortDependPath(p'+relMention['rm_id']+',lived_words_of)\n')
                    if check_string_over('son,daughter,child,mother,father,parent', relMention['short_dep_path']):
                        mln_db.write('HasWordsShortDependPath(p'+relMention['rm_id']+',children_words)\n')
                    if check_string_over('found,founded,founde', relMention['short_dep_path']):
                        mln_db.write('HasWordsShortDependPath(p'+relMention['rm_id']+',founders_words)\n')
                    if check_string_over('ceo,director,chief,worker,member,corp,president,chairman', relMention['short_dep_path']):
                        mln_db.write('HasWordsShortDependPath(p'+relMention['rm_id']+',company_words)\n')
                    if check_string('enrol,study,complete,graduate,attend,studied,complete,alumni,university,institute,graduate,school,received', relMention['short_dep_path']):
                        mln_db.write('HasWordsShortDependPath(p'+relMention['rm_id']+',institution_words)\n')
                    if check_string('bachelor,master,doctor', relMention['short_dep_path']):
                        mln_db.write('HasWordsShortDependPath(p'+relMention['rm_id']+',degree_words)\n')
                    

            labels = relMention['relation']['label'].split(",")
            for label in labels:
                candRelFile.write(relMention['rm_id']+'\t'+label+'\n')
                mln_db.write('DSCandRel(p'+relMention['rm_id']+','+label.replace(":", "1")+')\n')
            
            for relt in relationTypes:
                relt=relt.strip('\r\n')
                targetFile.write(relMention['rm_id']+'\t'+relt+'\n')
                if relt not in labels:
                    mln_db.write('!DSCandRel(p'+relMention['rm_id']+','+relt.replace(":", "1")+')\n')


            labels = relMention['relation']['true_label'].split(",")
            trueFile.write(relMention['rm_id']+'\t'+labels[0]+'\n')
            
            index+=1
            if len(relMention['depen_struct'])>0:
                relMention['index'] = index
                if len(relMention['verbs'])>0: 
                    new_relationMentions_verbs.append(relMention)
                sentence=str(relMention['short_path_cleaned']).replace(" ", "")
                if len(sentence)>0:
                    new_relationMentions.append(relMention)
          
            ##Ent1Type and Ent2Type predicates
            ent1TypeSet=set()
            ent2TypeSet=set()
            for item in relMention['entityTypes']:
                if relMention['relation']['em1Text'] in item:
                    if (relMention['rm_id'],item[relMention['relation']['em1Text']]['label']) not in ent1TypeSet:
                        ent1TypeSet.add((relMention['rm_id'],item[relMention['relation']['em1Text']]['label']))
                        ent1type.write(relMention['rm_id']+'\t'+item[relMention['relation']['em1Text']]['label']+'\n')
                        ent1type_st.write(relMention['rm_id']+'\t'+item[relMention['relation']['em1Text']]['st_label']+'\n')
                        mln_db.write('Ent1TypeSp(p'+relMention['rm_id']+','+item[relMention['relation']['em1Text']]['label']+')\n')
                        mln_db.write('Ent1TypeSt(p'+relMention['rm_id']+','+item[relMention['relation']['em1Text']]['st_label']+')\n')
                        if(any(x.isupper() for x in relMention['relation']['em1Text'])):
                            val = 1
                            mln_db.write('Ent1Capital(p'+relMention['rm_id']+')\n')
                        else:
                            val = 0
                            mln_db.write('!Ent1Capital(p'+relMention['rm_id']+')\n')
                        ent1cap.write(relMention['rm_id']+'\t'+str(val)+'\n')

                if relMention['relation']['em2Text'] in item:
                    if (relMention['rm_id'],item[relMention['relation']['em2Text']]['label']) not in ent2TypeSet:
                        ent2TypeSet.add((relMention['rm_id'],item[relMention['relation']['em2Text']]['label']))
                        ent2type.write(relMention['rm_id']+'\t'+item[relMention['relation']['em2Text']]['label']+'\n')
                        ent2type_st.write(relMention['rm_id']+'\t'+item[relMention['relation']['em2Text']]['st_label']+'\n')
                        mln_db.write('Ent2TypeSp(p'+relMention['rm_id']+','+item[relMention['relation']['em2Text']]['label']+')\n')
                        mln_db.write('Ent2TypeSt(p'+relMention['rm_id']+','+item[relMention['relation']['em2Text']]['st_label']+')\n')
                        if(any(x.isupper() for x in relMention['relation']['em2Text'])):
                            val = 1
                            mln_db.write('Ent2Capital(p'+relMention['rm_id']+')\n')
                        else:
                            val = 0
                            mln_db.write('!Ent2Capital(p'+relMention['rm_id']+')\n')
                        ent2cap.write(relMention['rm_id']+'\t'+str(val)+'\n')
            sys.stdout.write("Processed %d, Time: %d sec\r" % (relMention['indexId'],  time.time() - start))
            sys.stdout.flush()

        ent1type.close()
        ent2type.close()
        ent1type_st.close()
        ent2type_st.close()
        commonWordsFile.close()
        hasDirectDependencyFile.close()
        hasSimilarEntityVerbsFile.close()
        shortDependPathFile.close()
        trueFile.close()
        candRelFile.close()
        targetFile.close()
        mln_db.close()
        print '\n'

        if _dir=='test':
            with open(outdir+'/similarity_target.txt', 'w') as predFile:
               for i, rm1 in enumerate(relation_arr):
                   for j, rm2 in enumerate(relation_arr):
                       if rm1['rm_id'] != rm2['rm_id']:
                           predFile.write(rm1['rm_id']+'\t'+rm2['rm_id']+'\n')
               predFile.close()
            # ##similarity
             ## parallelize_array(new_relationMentions, similarityCalculation)
            similarityVerbCalculation(new_relationMentions_verbs)
            similarityCalculation(new_relationMentions)

        with open(outdir+'/ent1_target.txt', 'w') as ent1_target,\
        open(outdir+'/ent2_target.txt', 'w') as ent2_target:
            for i, rm1 in enumerate(relation_arr):
                for entType in ['PERSON','ORGANIZATION','LOCATION','None']:
                    ent1_target.write(rm1['rm_id']+'\t'+entType+'\n')
                    ent2_target.write(rm1['rm_id']+'\t'+entType+'\n')
            ent1_target.close()
            ent2_target.close()

#dependency path length
        normRmDependPath=normalize(rmDependPath)
        with open(outdir+'/dependPathLength_obser.txt', 'w') as predFile:
            for rm_id in normRmDependPath:
                predFile.write(rm_id+'\t'+str(normRmDependPath[rm_id])+'\n')
            predFile.close()


    

## ganerate predicates and /data/candidate_rm.json with all relations separatelly
def candidateRelMentionsGeneration(outdir,jsonFname,cand_file):
    print "Generate candidate relation mentions...."
    with open(jsonFname, 'r') as fin, open(outdir+'/relationTypes.txt', 'w') as relType,open(cand_file, 'w') as outfile:
        rmDependPath = {}
        relationsTypes = []
        start = time.time()
        indexId=0
        for line in fin:
            indexId+=1
            sentDic = json.loads(line.strip('\r\n'))
            for i, rm in enumerate(sentDic['relationMentions']):
                if i>0:
                    indexId+=1
                rm_item={}
                rm_item['relation'] = rm
                rm_item['indexId']=indexId
                rm_item['articleId']=sentDic['articleId']
                rm_item['entityMentions']=sentDic['entityMentions']
                rm_item['sentId']=sentDic['sentId']
                rm_item['sentText'] = sentDic['sentText']
                rm_item['entityTypes'] = findEntityType(rm['em1Text'], rm['em2Text'], sentDic['entityMentions'])
                rm_item['rm_id'] = '%s_%s_%s'%(sentDic['articleId'], sentDic['sentId'], indexId)
                
                outfile.write(json.dumps(rm_item)+'\n')    
                sys.stdout.write("Processed %d  rm, Time: %d sec\r" % (indexId,  time.time() - start))
                sys.stdout.flush() 
                #write relation types
                labels = rm['true_label'].split(",")
                for label in labels:
                    relationsTypes.append(label.strip('\r\n'))
                labels = rm['label'].split(",")
                for label in labels:
                    relationsTypes.append(label.strip('\r\n'))
        outfile.close()
        #write all relations type to file       
        rm = list(set(relationsTypes))
        relType.write("\n".join(rm))
        relType.close()
        print '\n'

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print 'Usage: generatePSLPredicates.py -DATA (Google/Riedel/KBP/Hoffman/) -FILE (/test.json/train.json) -DIR (test/train/dev)'
        exit(-1)

    _data = sys.argv[1]
    _file = sys.argv[2]
    _dir = sys.argv[3]
    outdir = 'data/psl/' + _data + '/' +_dir
    start=time.time()
    # candidateRelMentionsGeneration(outdir, _file, outdir+'/candidate_tmp.json')
    pslPredicateGeneration(outdir,outdir+'/candidate_tmp.json',outdir+'/candidate_rm.json')
    print("Done. Common Time: %d sec\r" % (time.time() - start) )

    mag_vectors.close()
