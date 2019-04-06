#!/usr/bin/python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json
# from sematch.semantic.similarity import WordNetSimilarity
# from sematch.semantic.similarity import EntitySimilarity
# from nltk.corpus import wordnet as wn
# from nltk.stem import WordNetLemmatizer
# from nltk.tokenize import word_tokenize, sent_tokenize
# from nltk.corpus import stopwords
import re
import time
import io
# ruleType="lexical";
_data='KBP'
# ruleType="none";
# ruleType="syntax_type";
# ruleType="syntax_path";
# ruleType="syntax_type,syntax_path";
# ruleType="semantic";
# ruleType="simil_veb";
# ruleType="simil_path";
# ruleType="simil_struct";		
# ruleType="user_knw_fp";
# ruleType="user_knw_predic"
# ruleType="user_knw_fp,user_knw_predic"
# ruleType="user_knw_fp,user_knw_predic,syntax_type,syntax_path"
# ruleType="user_knw_fp,user_knw_predic,syntax_type,syntax_path,semantic"
# ruleType="user_knw_fp,user_knw_predic,simil_veb,syntax_type,syntax_path"
# ruleType="user_knw_fp,user_knw_predic,simil_path,syntax_type,syntax_path"
# ruleType="user_knw_fp,user_knw_predic,simil_struct,syntax_type,syntax_path"
# ruleType="user_knw_fp,user_knw_predic,syntax_type,syntax_path,simil_veb,simil_path,simil_struct"
# ruleType="user_knw_fp,user_knw_predic,syntax_type,syntax_path,simil_veb,simil_path,semantic"

def same_type(string1, string2):
	string_arr_1=string1.split(',')
	string_arr_2=string2.split(',')
	for substring_1 in string_arr_1:
		for substring_2 in string_arr_2:
			if substring_1 == substring_2:
				return True
	return False

def check_string(string1, string2):
	string_arr_1=string1.split(',')
	string_arr_2=string2.split(',')
	for substring_1 in string_arr_1:
		for substring_2 in string_arr_2:
			if substring_1 in substring_2:
				return True
	return False
def loadValues(file_name):
	neighbors={}
	with open(file_name, 'r') as file:
		for line in file:
			seg = line.strip('\r\n').split('\t')
			score = float(seg[2])
			rm_id = seg[0]
			rm_id_neigbor = seg[1]
			if rm_id not in neighbors:
				neighbors[rm_id]=[]
			neighbors[rm_id].append({'rm_id':rm_id_neigbor,'score':score})
		file.close()
	return neighbors

def findTheClosest(rm_id,neighbors,rmId2Type):
	maxScore = 0.0
	rmType=rmId2Type[rm_id]
	# rmType="None"
	neighborsType={}
	if rm_id in neighbors:
		for item in neighbors[rm_id]:
			score = float(item['score'])
			rm_id_neigbor = item['rm_id']
			if rmId2Type[rm_id_neigbor] not in neighborsType:
				neighborsType[rmId2Type[rm_id_neigbor]]=1
			else:
				neighborsType[rmId2Type[rm_id_neigbor]]+=1
			
			if maxScore<score:
				maxScore=score
				rmType=rmId2Type[rm_id_neigbor]

		rmType = max(neighborsType, key=lambda k: neighborsType[k])
	# else:
		# print rm_id
	return rmType

def bruteForceApproach(filename,psl_dir,jsonFname):
	verbNeighbors = loadValues(psl_dir+'/verbsSimilarity_obser.txt')
	pathNeighbors = loadValues(psl_dir+'/depenPathSimilarity_obser.txt')
	strNeighbors = loadValues(psl_dir+'/depenStructureSimilarity_obser.txt')
	with open(psl_dir+'/relationTypes.txt', 'r') as rel_type:
		relation_types = rel_type.readlines()

	print ruleType
	countNum=0

	with open(jsonFname, 'r') as fin, \
	open(filename, 'w') as outputFile:
		relationMentions = fin.readlines()
		num_rel= len(relationMentions)
		rmId2Type={}
		for line in relationMentions:
			rm = json.loads(line.strip('\r\n'))
			rmId2Type[rm['rm_id']]=rm['relation']['label']

		start = time.time()
		for line in relationMentions:
			rm = json.loads(line.strip('\r\n'))
			rm['relation']['predic_label'] =rm['relation']['label'] # 'None' #
			em1Type="None"
			em2Type="None"
			print rm


			for item in rm['entityTypes']:
				if rm['relation']['em1Text'] in item:
					em1Type = item[rm['relation']['em1Text']]['label']
				if rm['relation']['em2Text'] in item:
					em2Type = item[rm['relation']['em2Text']]['label']

			if same_type("entity",ruleType):
				if rm['relation']['em1Text'] in item:
					if item[rm['relation']['em1Text']]['label']!=item[rm['relation']['em1Text']]['st_label']:
						em1Type='None'
						print 'em1Type ',item[rm['relation']['em1Text']]['label'], item[rm['relation']['em1Text']]['st_label']
				if rm['relation']['em2Text'] in item:
					if item[rm['relation']['em2Text']]['label']!=item[rm['relation']['em2Text']]['st_label']:
						em2Type='None'
						print 'em2Text ',item[rm['relation']['em2Text']]['label'], item[rm['relation']['em2Text']]['st_label']
				if not (any(x.isupper() for x in em1Type)):
					em1Type='None'
				if not (any(x.isupper() for x in em2Type)):
					em2Type='None'		
# ##################
			if same_type("user_knw_predic", ruleType):
				if em1Type == 'PERSON' and em2Type == 'LOCATION': #and rm['path_length']<8:
					if check_string('death,dead,died,dies', rm['short_dep_path']):
						print 'has death words'
						rm['relation']['predic_label'] = 'per:place_of_death'
					if check_string('born,birth,native', rm['short_dep_path']):
						rm['relation']['predic_label'] = 'per:place_of_birth'
						print 'has birth words'
					if _data!="Google" and check_string('rear,raise,lived,live,moved,move,work,home,lives', rm['short_dep_path']):
						rm['relation']['predic_label'] = 'per:place_lived'
						print 'has lived words'
				if  _data!="Google" and em1Type == 'PERSON' and em2Type == 'PERSON' :# and rm['path_length']<7:
					if check_string('son,daughter,child,mother,father,parent', rm['short_dep_path']):
						rm['relation']['predic_label'] = 'per:children'
						print 'has children words'
				if em1Type == 'PERSON' and em2Type == 'ORGANIZATION': # and rm['path_length']<7:
					if  _data!="Google" and check_string('founded,found,founder', rm['short_dep_path']):
						rm['relation']['predic_label'] = 'per:founders'
						print 'has founders words'
					if  _data!="Google" and check_string('ceo,director,chief,worker,member,corp,president,chairman', rm['short_dep_path']):
						rm['relation']['predic_label'] = 'per:company'
						print 'has company words'
					if _data=="Google" and check_string('enrol,study,complete,graduate,attend,studied,received,complete,alumni,university,institute,graduate', rm['short_dep_path']):
						rm['relation']['predic_label'] = 'per:institution'
					if _data=="Google"  and check_string('bachelor,master,doctor', rm['short_dep_path']):
						rm['relation']['predic_label'] = 'per:degree'


			rmId2Type[rm['rm_id']]=rm['relation']['predic_label']
			if same_type("user_knw_fp",ruleType) and rm['short_dep_path']!='':
				if rm['relation']['label'] in ['per:place_of_birth'] and not check_string('born,birth,native', rm['short_dep_path']):
					print 'false positive do not have place_of_birth'
					rm['relation']['predic_label'] ='None'
				if rm['relation']['label'] in ['per:place_of_death'] and not check_string('died,dead,dies,death',rm['short_dep_path']):
					rm['relation']['predic_label'] ='None'
					print 'false positive do not have place_of_death'
				if rm['relation']['label'] in ['per:place_lived'] and not check_string('rear,raise,lived,live,move,work,home',rm['short_dep_path']):
					rm['relation']['predic_label'] ='None'
					print 'false positive do not have place_lived'
				if rm['relation']['label'] in ['per:founders'] and not check_string('founder,founded',rm['short_dep_path']):
					rm['relation']['predic_label'] ='None'
					print 'false positive do not have founders'
				if rm['relation']['label'] in ['per:degree'] and not check_string('bachelor,master,doctor',rm['short_dep_path']):
					rm['relation']['predic_label'] ='None'
				if rm['relation']['label'] in ['per:institution'] and not check_string('enrol,study,complete,educate,attend,studied,complete,alumni,university,institute,graduate',rm['short_dep_path']):
					rm['relation']['predic_label'] ='None'


###################
			if same_type("semantic",ruleType):
				if rm['relation']['label'] in ['per:place_of_birth','per:place_lived','per:place_of_death','per:nationality']:
					if em1Type !='PERSON' and em2Type  != 'LOCATION':
						rm['relation']['predic_label'] = 'None'
						print 'semantic worng'
				if rm['relation']['label'] in ['per:children', 'per:parents']:
					if em1Type  !='PERSON' and em2Type != 'PERSON':
						print 'fsemantic worng'
						rm['relation']['predic_label'] = 'None'
				if rm['relation']['label'] in ['per:religion', 'per:ethnicity','per:founders','per:company','per:degree','per:institution']:
					if em1Type !='PERSON' and em2Type  != 'ORGANIZATION':
						rm['relation']['predic_label'] = 'None'
						print 'fsemantic worng'

###################
			if same_type("simil_veb",ruleType):
				rmType = findTheClosest(rm['rm_id'],verbNeighbors,rmId2Type)
				rm['relation']['predic_label']=rmType
##############

			if same_type("simil_path",ruleType):
				rmType = findTheClosest(rm['rm_id'],pathNeighbors,rmId2Type)
				rm['relation']['predic_label']=rmType
##############
			if same_type("simil_struct",ruleType):
				rmType = findTheClosest(rm['rm_id'],strNeighbors,rmId2Type)
				rm['relation']['predic_label']=rmType
##############

			if same_type("syntax_type",ruleType):
				if rm['nouns_type']!=1.0: # and rm['relation']['label']!='None':
					rm['relation']['predic_label'] = 'None' #rm['relation']['label']
					print 'nouns_type==0'
				# if rm['nouns_type']==0.0:
				# 	rm['relation']['predic_label'] = 'None'
			if same_type("syntax_path",ruleType):
				if rm['path_length']>7.0:#and rm['relation']['label']!='None':
					rm['relation']['predic_label'] = 'None'#rm['relation']['label']
					print 'path_length==0'
				# if  rm['path_length']>10:
				# 	rm['relation']['predic_label'] = 'None'
			if same_type("lexical",ruleType):
				# if rm['ent_verbs_sim']>0.0 and rm['relation']['label']!='None':
				# 	rm['relation']['predic_label'] = rm['relation']['label']
				if rm['ent_verbs_sim']==0.0:
					rm['relation']['predic_label'] = 'None'
					print 'ent_verbs_sim==0'
###################
			if rm['relation']['predic_label']!=rm['relation']['true_label']:
				print rm['relation']['predic_label'], rm['relation']['label'], rm['relation']['true_label'] # 'None' #
				input_var = raw_input("Continue: ")

			sentDic={}
			sentDic['rm_id'] = rm['rm_id']
			sentDic['sentText'] = rm['sentText']
			sentDic['indexId'] = rm['indexId']
			sentDic['sentId'] = rm['sentId']
			sentDic['entityMentions'] = rm['entityMentions']
			sentDic['articleId'] = rm['articleId']
			sentDic['relation'] = rm['relation']
			sentDic['relation']['predic_label']=rm['relation']['predic_label']
			outputFile.write(json.dumps(sentDic)+'\n')

if __name__ == "__main__":
	if len(sys.argv) != 5:
		print 'Usage: ruleBasedApproach.py -DATA (Google/Riedel/KBP/Hoffman/) -DIR (eval/learn)'
		exit(-1)

	_data = sys.argv[1]
	_dir = sys.argv[2]
	_file_name= sys.argv[3]
	_ruleType = sys.argv[4]
	ruleType = _ruleType
	psl_dir = 'data/psl/' + _data + '/' +_dir
	indir = 'data/generated/' + _data
	# if _file_name=='/brute_force_4.json':
	# 	ruleType="user_knw_predic"
	# if _file_name=='/brute_force_3.json':
	# 	ruleType="user_knw_fp,user_knw_predic,semantic,simil_veb"
	# if _file_name=='/brute_force_2.json':
	# 	ruleType="syntax_type,syntax_path,user_knw_fp,user_knw_predic,semantic,simil_veb"
	# bruteForceApproach(indir+_file_name,psl_dir,psl_dir+'/candidate_rm.json')
	bruteForceApproach(psl_dir+'/brute_force.json',psl_dir,psl_dir+'/candidate_rm.json')
  