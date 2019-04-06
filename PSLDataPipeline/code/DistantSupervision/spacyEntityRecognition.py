#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import nltk
from stanza.nlp.corenlp import CoreNLPClient
import json
from distantSupervision import linkToFB,loadTargetTypes,linkJson2Freebase
import spacy
import re
import time
import pandas as pd
import editdistance

INTERESTED_EM_TYPES = ['PERSON','GPE','ORG','LOC','NORP','FAC']
INTERESTED_STANFORD_EM_TYPES = ['PERSON','LOCATION','ORGANIZATION']

nlp = spacy.load('en')

targetEMTypes = loadTargetTypes('./data/emTypeMap.txt')
targetRMTypes = loadTargetTypes('./data/rmTypeMap.txt')
dsRelations={}
#StanfordCoreNLP

class NLPParser(object):
	"""
	NLP parse, including Part-Of-Speech tagging.
	Attributes
	==========
	parser: StanfordCoreNLP
		the Staford Core NLP parser
	"""
	def __init__(self):
		self.parser = CoreNLPClient(default_annotators=['ssplit', 'tokenize', 'ner'])

	def parse(self, sent):
		result = self.parser.annotate(sent)
		type_list, ner_list = [], []
		for sent in result.sentences:
			ner_type, ner = [], []
			currNERType = 'O'
			currNER = ''
			for token in sent:
				token_ner = token.ner
				if token_ner not in INTERESTED_STANFORD_EM_TYPES:
				  token_ner = 'O'
				# ner_type += [token.word]
				if token_ner == 'O':
				  if currNER != '':
					ner.append(currNER.strip())
					ner_type.append(currNERType)
				  currNER = ''
				elif token_ner == currNERType:
				  currNER += token.word + ' '
				else:
				  if currNER != '':
					ner.append(currNER.strip())
					ner_type.append(currNERType)
				  currNERType = token_ner
				  currNER = token.word + ' '
			if currNER != '':
			  ner.append(currNER.strip())
			  ner_type.append(currNERType)
			if len(ner_type) == 0 or len(ner) == 0:
			  continue
			type_list.append(ner_type)
			ner_list.append(ner)
		return type_list, ner_list

parser = NLPParser()
#actually for doc, split into sentence and so on.
def getStanfordEntityMentions(sentText):
	doc = sentText.strip('\r\n')
	type_list, nps_list = parser.parse(doc)
	entityMentions = dict()
	for i in range(len(type_list)):
		ners = type_list[i]
		nps = nps_list[i]
		if nps:
			for j in range(len(nps)):
				entityMentions[nps[j]]=ners[j]
	return entityMentions

def getStanfordType(entText, entityMentions):
	for ent in entityMentions:
		if entText == ent:
			return ent,entityMentions[ent]
	for ent in entityMentions:
		entText_arr = entText.split(" ")
		ent_arr = ent.split(" ")
		for str_1 in entText_arr:
			for str_2 in ent_arr:
				if str_1 == str_2:
					return ent,entityMentions[ent]
	return 'None','None'

def freebaseLabels():
	key2relation = {}
	targetRMTypes = loadTargetTypes('./data/rmTypeMap.txt')
	with open('./data/source/'+_data+'/test.json', 'r') as fin:
		for line in fin:
			sentDic = json.loads(line.strip('\r\n'))
			for rm in sentDic['relationMentions']:#targetRMTypes
				if rm['label'] in ['per:religion','per:countries_of_residence',\
							'per:country_of_birth','per:country_of_death','per:children','per:nationality','per:ethnicity',\
							'org:founded_by','per:employee_or_member_of','None']:
					key = (rm['em1Text'], rm['em2Text'])
					key2relation[key] = targetRMTypes[rm['label']]
		print('finish loading relationTupleFile',len(key2relation))
	return key2relation			

	#Spacy
def entityMentionsDefining(sentText):
	stEntityMentions=getStanfordEntityMentions(sentText)
	tmp_stEntityMentions=stEntityMentions
	spacy_doc = nlp(sentText)
	entityMentions=[]
	start=0
	for ent in spacy_doc.ents:
		if ent.label_ in INTERESTED_EM_TYPES:
			entDic=dict()
			entDic['label'] = targetEMTypes[ent.label_]
			entDic['st_text'],entDic['st_label'] = getStanfordType(str(ent.text),stEntityMentions)
			entDic['text'] = ent.text
			entDic['start'] = start
			if entDic['st_text'] in tmp_stEntityMentions:
				del tmp_stEntityMentions[entDic['st_text']]
			start+=1
			entityMentions.append(entDic)
			# if entDic['st_text']!=entDic['text'] :
			# 	print(ent.text, ent.label_)
			# 	print(entDic['st_text'],entDic['st_label'])
			# 	print sentText,'\n'
	for ent in tmp_stEntityMentions:
		entDic=dict()
		entDic['label'] = 'None'
		entDic['st_text'] = ent
		entDic['st_label'] = tmp_stEntityMentions[ent]
		entDic['text'] = ent
		entDic['start'] = start
		start+=1
		entityMentions.append(entDic)

	return entityMentions

def distantSupervisionFromFile(row):
	key2trueLabels = {}
	for rm in row['relationMentions']:
		key = (rm['em1Text'], rm['em2Text'])
		key2trueLabels[key] = rm['true_label']

	rms = set()
	relationMentions=[]
	entityMentions=row['entityMentions']
	for ent_1 in entityMentions:
		for ent_2 in entityMentions:
			if ent_1['text'] != ent_2['text']:
				if (ent_1['text'], ent_2['text']) not in rms:
					add2Rm=False
					newRm = dict()
					newRm['em1Text'] = ent_1['text']
					newRm['em2Text'] = ent_2['text']
					newRm['label'] = 'None'
					newRm['true_label'] = 'None'

					key = (newRm['em1Text'], newRm['em2Text'])
					keyStan = (ent_1['st_text'],ent_2['st_text'])
					if key in key2trueLabels:
						add2Rm=True
						newRm['true_label'] = key2trueLabels[key]

					if key in dsRelations:
						if dsRelations[key]!='None':
							add2Rm=True
							newRm['label']= dsRelations[key]
					else:
						if keyStan in dsRelations:
							if dsRelations[keyStan]!='None':
								add2Rm=True
								newRm['label']= dsRelations[keyStan]
					if add2Rm==True:
						relationMentions.append(newRm)
					rms.add((ent_1['text'], ent_2['text']))
	row['relationMentions']=relationMentions
	return row 

def excludeWrongLabelsGoogle(row):
	key2trueLabels = {}
	if len(row['relationMentions'])>1:
		print "More that one relation",row


	entityMentions=[]
	for ent_1 in row['entityMentions']:
		for ent_2 in row['entityMentions_1']:
			if ent_2['text'] in ent_1['text']:
				# ent_1['text']=ent_2['text']
				ent_1['st_text']=ent_2['st_text']
				# ent_1['label'] = ent_2['label']
				ent_1['st_label'] = ent_2['st_label']
			if ent_1['text'] in ent_2['text']:
				# ent_1['text']=ent_2['text']
				ent_1['st_text']=ent_2['st_text']
				ent_1['label'] = ent_2['label']
				ent_1['st_label'] = ent_2['st_label']
			if ent_1['text'] in ent_2['st_text']:
				ent_1['label'] = ent_2['label']
				ent_1['st_label'] = ent_2['st_label']
		entityMentions.append(ent_1)
	
	for ent_1 in entityMentions:
		if 'st_label' not in ent_1:
			ent_1['st_label']='None'

	row['entityMentions']=entityMentions
	return row 

def relationMentionsDefining(entityMentions):
	rms = set()
	relationMentions=[]
	for ent_1 in entityMentions:
		for ent_2 in entityMentions:
			if ent_1['text'] != ent_2['text']:
				if (ent_1['text'], ent_2['text']) not in rms:
					newRm = dict()
					newRm['em1Text'] = ent_1['text']
					newRm['em2Text'] = ent_2['text']
					newRm['label'] = 'None'
					relationMentions.append(newRm)
					rms.add((ent_1['text'], ent_2['text']))
	return relationMentions

def createTrainingSet(inFile, outFile):
	start = time.time()
	data_pd = pd.read_json(inFile, lines=True, encoding = 'utf8')
	data_pd["entityMentions_1"] = data_pd["sentText"].apply(entityMentionsDefining)
	# data_pd["relationMentions"] = data_pd["entityMentions"].apply(relationMentionsDefining)
	data_pd=data_pd.apply(excludeWrongLabelsGoogle, axis=1)
	data_pd=data_pd.drop(['entityMentions_1'], axis=1)
	data_pd.reset_index().to_json(outFile,orient='records', lines=True,default_handler=str)


				
def writeToJson(inFile, outFile,entityTypesFname,relationTypesFname):
	start = time.time()
	#nlp = spacy.load('en')
	targetEMTypes = loadTargetTypes(entityTypesFname)
	targetRMTypes = loadTargetTypes(relationTypesFname)
	with open(inFile, 'r') as fin, open(outFile, 'w') as fout:
		articleId = 0
		for line in fin:
			jsonLine = json.loads(line.strip('\r\n'))
			spacy_doc = nlp(jsonLine['sentText'])

			#dep_path = {}
			verbs = set()
			for token in spacy_doc:
				#dep_path[token.text.encode('utf8')] = [token.dep_.encode('utf8'),token.head.text.encode('utf8')]
				if token.pos_=="VERB":
					verbs.add(token.text)

			for ent in spacy_doc.ents:
				ent_text = ent.lower_ #re.sub('[^a-zA-Z]+', '', ent.lower_)  
				if ent.label_ in INTERESTED_EM_TYPES:
					for i, item in enumerate(jsonLine['entityMentions']):
						for token in nlp(item['text']):
							emText=token.lower_
							#emText= re.sub('[^a-zA-Z]+', '', emText)    
							break
						if editdistance.eval(ent_text,emText)<1:
							jsonLine['entityMentions'][i]['label'] = targetEMTypes[ent.label_]
			for i, item in enumerate(jsonLine['relationMentions']):
				jsonLine['relationMentions'][i]['label'] = targetRMTypes[jsonLine['relationMentions'][i]['label']]
			articleId+=1
			#jsonLine['dep_path']=dep_path
			jsonLine['verbs']=list(verbs)
			# intnum = 0
			# for sent in spacy_doc.sents:
			#   intnum+=1
			# if intnum>1:
			#   for sent in spacy_doc.sents:
			#     print sent
			#   print jsonLine
			#   input_var = raw_input("Continue: ")
			fout.write(json.dumps(jsonLine) + '\n')
			sys.stdout.write("Parsed %d sentences, Time: %d sec\r" % (articleId, time.time() - start) )
			sys.stdout.flush()



if __name__ == "__main__":
	if len(sys.argv) != 2:
		print 'Usage: generateAnnotatedData.py -DATA (Google/Riedel/KBP/Hoffman/)'
		exit(-1)
	
	_data = sys.argv[1]        
	inFile = './data/generated/'+_data+'/old/train_gt.json'
	outFile = './data/generated/'+_data+'/train.json'
	# dsRelations=freebaseLabels()
	# with open(inFile, 'r') as fin,\
	# open(outFile,'w') as outfile:
	# 	cunt=0
	# 	count_n=0
	# 	for line in fin:
	# 		flag=True
	# 		relMention = json.loads(line.strip('\r\n'))
	# 		relationMentions=[]
	# 		for rm in relMention['relationMentions']:
	# 			if cunt <800 and rm['true_label']==rm['label'] and rm['true_label']=='per:place_of_birth':
	# 				rm['label']='None'
	# 				cunt+=1
	# 			if count_n <800 and rm['true_label']==rm['label'] and rm['true_label']=='per:institution':
	# 				count_n+=1
	# 				rm['label']='None'
	# 				#rm['label']='per:place_of_birth'
	# 				# print relMention['sentText']
	# 				# print rm
	# 				# input_var = raw_input("Continue: ")
					
	# 			relationMentions.append(rm)
	# 		relMention['relationMentions']=relationMentions
	# 			# if rm['label']=='per:nationality' or rm['true_label']=='per:nationality':
	# 				# flag=False
	# 		# print cunt
	# 		# if flag==True:
	# 		outfile.write(json.dumps(relMention)+'\n')  


	createTrainingSet(inFile, outFile)
	
