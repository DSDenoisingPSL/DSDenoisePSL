# Script to generate psl input files
import sys
import json
from collections import  defaultdict

candidate_rm_file =  './generated/candidate_rm.json'
_flag=1
def check_string(string1, string2):
	string_arr_1=string1.split(',')
	string_arr_2=string2.split(',')
	for substring_1 in string_arr_1:
		for substring_2 in string_arr_2:
			if substring_1 == substring_2:
				return True
	return False

def has_string(string1, string2):
	string_arr_1=string1.lower().split(',')
	string_arr_2=string2.lower().split(',')
	for substring_1 in string_arr_1:
		for substring_2 in string_arr_2:
			if substring_1 in substring_2:
				return True
	return False

def evaluatePrediction(filename,type_of_label,file_eval):
	negative = 0.0
	positive = 0.0
	pred_negative = 0.0
	pred_positive = 0.0
	true_positive = 0.0
	true_negative = 0.0
	total = 0.0
	false_negative = 0.0
	false_positive = 0.0
	false_prediction = 0.0
	true_prediction = 0.0
	false_prediction_num=0
	relationsTypes=[]
	relationTypeScores={}
		# open('./data/evaluation_result.txt', 'a') as evalFile:
	with open(filename, 'r') as generatedFile,\
		open('./data/results/'+file_eval, 'a') as evalFile:
		for line in generatedFile:
			rm = json.loads(line.strip('\r\n'))
			total+=1.0
			if True: #rm['relation']['true_label'] in ['None','per:country_of_death','per:country_of_birth','per:countries_of_residence','per:nationality','per:children','org:parents','org:founded_by']:
				if rm['relation']['true_label']=='None':
					negative+=1.0
				else:
					positive+=1.0

				if rm['relation'][type_of_label] not in relationTypeScores:
					relationTypeScores[rm['relation'][type_of_label]]={'true_positive':0,'false_negative':0,'false_positive':0,'true_prediction':0,'total':0}

				if rm['relation']['true_label'] not in relationTypeScores:
					relationTypeScores[rm['relation']['true_label']]={'true_positive':0,'false_negative':0,'false_positive':0,'true_prediction':0,'total':0}

				relationTypeScores[rm['relation']['true_label']]['total']+=1
				if rm['relation'][type_of_label]=='None':
					pred_negative+=1.0
				else:
					pred_positive+=1.0

				if check_string(rm['relation'][type_of_label],rm['relation']['true_label'])==False:
					false_prediction+=1.0
					if rm['relation'][type_of_label]=='None' and rm['relation']['true_label']!='None':
						false_negative+=1.0
						relationTypeScores[rm['relation']['true_label']]['false_negative']+=1
					else:
						if rm['relation'][type_of_label]!='None' and rm['relation']['true_label']=='None':
							relationTypeScores[rm['relation'][type_of_label]]['false_positive']+=1
						else:
							relationTypeScores[rm['relation']['true_label']]['false_negative']+=1
						if rm['relation'][type_of_label]!='None' and rm['relation']['true_label']=='None':
							false_positive+=1.0
						else:
							false_positive+=1.0
							false_prediction_num+=1
					labels = rm['relation']['true_label'].split(",")
					for label in labels:
						relationsTypes.append(label.strip('\r\n'))
				else:
					relationTypeScores[rm['relation'][type_of_label]]['true_prediction']+=1
					true_prediction+=1.0
					relationTypeScores[rm['relation'][type_of_label]]['true_positive']+=1
					if rm['relation'][type_of_label]!='None':
						true_positive+=1
					else:
						true_negative+=1
		print 'false_positive_not None',false_prediction_num
		print 'false_positive:',false_positive,'false_negative:', false_negative, 'true_positive', true_positive, 'true_negative',true_negative
		generatedFile.close()
		precision = true_positive / (false_positive+ true_positive + 1e-8)
		recall = true_positive / (true_positive+false_negative + 1e-8)
		f1 = 2 * precision * recall / (precision + recall + 1e-8)
		accuracy = true_prediction/total
		print 'Accuracy: %f'%accuracy
		print "Truth: precision: %f, recall: %f, f1: %f "%(precision,recall,f1)
		_flag = 0 ## per relation
		if _flag==1:
			for t in relationTypeScores:
				print '\n',t,':',relationTypeScores[t]
				precision = relationTypeScores[t]['true_positive'] / (relationTypeScores[t]['false_positive']+ relationTypeScores[t]['true_positive'] + 1e-8)
				recall = relationTypeScores[t]['true_positive'] / (relationTypeScores[t]['true_positive']+relationTypeScores[t]['false_negative'] + 1e-8)
				f1 = 2 * precision * recall / (precision + recall + 1e-8)
				print "Truth: precision: %f, recall: %f, f1: %f "%(precision,recall,f1)
				evalFile.write('\n'+str(t)+'\t'+str(round(precision,4))+'\t'+str(round(recall,4))+'\t'+str(round(f1,4))+'\t'+str(round(relationTypeScores[t]['false_positive'],4))+'\t'+str(round(relationTypeScores[t]['false_negative'],4))+'\t'+str(round(relationTypeScores[t]['true_positive'],4)))
		evalFile.write('\n'+str(round(accuracy,4))+'\t'+str(round(precision,4))+'\t'+str(round(recall,4))+'\t'+str(round(f1,4))+'\t'+str(round(false_positive,4))+'\t'+str(round(false_negative,4))+'\t'+str(round(true_positive,4))+'\t'+str(round(true_negative,4)))
		print '==============================================='

def compareTruth2Freebase():
	negative = 0.0
	positive = 0.0
	pred_negative = 0.0
	pred_positive = 0.0
	true_positive = 0.0
	true_negative = 0.0
	total = 0.0
	false_negative = 0.0
	false_positive = 0.0
	false_prediction = 0.0
	true_prediction = 0.0

	with open(candidate_rm_file, 'r') as generatedFile,\
		open('./data/evaluation_result.txt', 'a') as evalFile:
		for line in generatedFile:
			rm = json.loads(line.strip('\r\n'))
			total+=1

			# if 'true_label' not in rm['relation']:
			#     rm['relation']['true_label']='None'

			if rm['relation']['true_label']=='None':
				negative+=1.0
			else:
				positive+=1.0

			if rm['relation']['label']=='None':
				pred_negative+=1.0
			else:
				pred_positive+=1.0

			if not check_string(rm['relation']['label'],rm['relation']['true_label']):
				false_prediction+=1.0
				if rm['relation']['label']=='None' and rm['relation']['true_label']!='None':
					false_negative+=1
				else:
					false_positive+=1
					# print rm['sentText']
					# print rm['relation']['em1Text'],rm['relation']['em2Text']
					# print rm['relation']['label'],rm['relation']['true_label']
					# input_var = raw_input("Continue: ")
			else:
				true_prediction+=1.0
				if rm['relation']['label']!='None':
					true_positive+=1
				else:
					true_negative+=1

		print '--------- \ntotal: ',total,'negative ', negative, 'positive ',positive
		print 'pred_negative ', pred_negative, 'pred_positive ',pred_positive
		print 'false_prediction: ',false_prediction,'true_prediction: ',true_prediction
		print 'false_positive:',false_positive,'false_negative:', false_negative, 'true_positive', true_positive, 'true_negative',true_negative
		generatedFile.close()
		precision = true_positive / (true_positive+false_positive + 1e-8)
		recall = true_positive / (true_positive+false_negative + 1e-8)
		f1 = 2 * precision * recall / (precision + recall + 1e-8)
		accuracy = true_prediction/total
		print 'Accuracy: %f'%accuracy
		print "Truth: precision: %f, recall: %f, f1: %f predicted # Pos RMs:%d, #Pos RMs:%d"%(precision,recall,f1,int(true_positive+false_positive), int(true_positive+false_negative))
		print '------------'
		evalFile.write('\n'+str(round(accuracy,4))+'\t\t'+str(round(precision,4))+'\t\t'+str(round(recall,2))+'\t\t'+str(round(f1,4))+'\t\t'+str(round(false_positive,4))+'\t\t'+str(round(false_negative,4))+'\t\t'+str(round(true_positive,4))+'\t\t'+str(round(true_negative,4)))

def between(left,right,s):
	before,_,a = s.partition(left)
	a,_,after = a.partition(right)
	return a

def convert_psl_prediction_to_json(predictionPslFile, output, isPsl):
	prediction_arr = defaultdict(list)
	generatedDataset={}
	false_prediction = 0.0
	true_prediction = 0.0
	# open('data/psl/Google/test/test.json', 'w') as testOut,\
	with open(predictionPslFile, 'r') as predFile,\
	open(candidate_rm_file, 'r') as generatedFile,\
	open(output, 'w') as outputFile:
	#open('./psl/CandRel_obser_2.txt', 'w') as fout,\

		# how many positive labels in original dataset and generated by freebase
		for line in generatedFile:
			rm = json.loads(line.strip('\r\n'))
			generatedDataset[rm['rm_id']] = rm

		if isPsl==True:
			for line in predFile:
				seg = line.strip('\r\n').split('\t')
				rm_id = seg[0]
				rm_id=rm_id.replace("'", '') 
				relation_type = seg[1]
				relation_type=relation_type.replace("'", '') 
				score = seg[2]
				prediction_arr[rm_id].append({'rm_id':rm_id,'relation_type':relation_type,'score':score})
		else:
			for line in predFile:
				seg = line.strip('\r\n').split('\t')
				score = seg[0]
				score=score.replace(",", '.') 
				predicateString=seg[1]
				argumentsP = predicateString.split(',')
				rm_id=between('HasRel("','"',argumentsP[0])
				relation_type=between(' "','")',argumentsP[1])
				rm_id=rm_id.replace("'", '') 
				rm_id=rm_id.replace("p", '') 
				relation_type=relation_type.replace("'", '') 
				relation_type=relation_type.replace("1", ":")
				prediction_arr[rm_id].append({'rm_id':rm_id,'relation_type':relation_type,'score':float(score)})
			
		for key, item in prediction_arr.iteritems():
			max_index = -1
			max_score = -sys.maxint
			prev_value = float(item[0]['score'])
			all_equal = True
			for i,j in enumerate(item):
				if  float(j['score']) > max_score:
					max_index = i
					max_score = float(j['score'])
				if prev_value!=float(j['score']):
					all_equal=False

			# if max_score<0.35:
			if all_equal and len(item)>1:
				# print 'set it to None', isPsl
				item[max_index]['relation_type']='None'

			sentDic = {}
			sentDic['relationMentions']=[]
			sentDic['sentText']=generatedDataset[key]['sentText']
			sentDic['index']=generatedDataset[key]['index']
			sentDic['sentId']=generatedDataset[key]['sentId']
			sentDic['articleId']=generatedDataset[key]['articleId']
			sentDic['entityMentions']=generatedDataset[key]['entityMentions']
			sentDic['relationMentions'].append(generatedDataset[key]['relation'])

			if check_string(item[max_index]['relation_type'],generatedDataset[key]['relation']['true_label'])==False:
				false_prediction+=1.0
				# if generatedDataset[key]['path_length']<15:
					# print key,max_score
					# print generatedDataset[key]['sentText']
					# print 'short_dep_path: ',generatedDataset[key]['short_dep_path']
					# print 'common_words: ',generatedDataset[key]['common_words']
					# print 'depen_struct: ',generatedDataset[key]['depen_struct']
					# print 'nouns_type:',generatedDataset[key]['nouns_type'],' path_length:',generatedDataset[key]['path_length'],' ent_verbs_sim:',generatedDataset[key]['ent_verbs_sim']
					# print generatedDataset[key]['relation']['em1Text'],generatedDataset[key]['relation']['em2Text']
					# print 'predic_label:',item[max_index]['relation_type'],' true_label:',generatedDataset[key]['relation']['true_label'],' label: ',generatedDataset[key]['relation']['label']

					# if item[max_index]['relation_type']=='per:place_of_birth' and has_string('born,birth,native', generatedDataset[key]['short_dep_path'])==True:
						# sentDic['relationMentions'][0]['true_label']=item[max_index]['relation_type']
					# input_var = raw_input("Continue: ")
					# if int(input_var)==1:
						# sentDic['relationMentions'][0]['true_label']=item[max_index]['relation_type']
					# else:
					#     if int(input_var)==2:
					#         sentDic['relationMentions'][0]['true_label']=generatedDataset[key]['relation']['label']     
					# print sentDic['relationMentions']
			else:
				true_prediction+=1.0


			# testOut.write(json.dumps(sentDic)+'\n') 
			sentDic={}
			sentDic['rm_id'] = item[max_index]['rm_id']
			sentDic['sentText'] = generatedDataset[item[max_index]['rm_id']]['sentText']
			sentDic['indexId'] = generatedDataset[item[max_index]['rm_id']]['indexId']
			sentDic['entityMentions'] = generatedDataset[item[max_index]['rm_id']]['entityMentions']
			sentDic['sentId'] = generatedDataset[item[max_index]['rm_id']]['sentId']
			sentDic['articleId'] = generatedDataset[item[max_index]['rm_id']]['articleId']
			sentDic['relation'] = generatedDataset[item[max_index]['rm_id']]['relation']
			sentDic['relation']['predic_label']=item[max_index]['relation_type']
			outputFile.write(json.dumps(sentDic)+'\n')
			#fout.write(sentDic['rm_id']+'\t'+sentDic['relation']['predic_label']+'\n')
		print 'false_prediction', false_prediction,'true_prediction',true_prediction,'\n=========='

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print 'Usage: evaluate_prediction.py -DATA (/KBP/NYT/Google)'
		exit(-1)

	_data = sys.argv[1]
	psl_dir = 'data/psl/' + _data + '/test'
	indir = 'data/generated/' + _data
	candidate_rm_file = psl_dir+'/candidate_rm.json'
	print '1 step. Convert psl model: '
	convert_psl_prediction_to_json('./inferred-predicates/mlnHasrel.txt', indir+'/prediction_mln.json',False)
	convert_psl_prediction_to_json('./inferred-predicates/HASREL.txt', indir+'/prediction_psl.json',True)
	print '2 step. Compare freebase to ground truth: '
	evaluatePrediction(candidate_rm_file, 'label','freebase_eval.txt')
	print '3 step. Compare psl to ground truth: '
	evaluatePrediction(indir+'/prediction_psl.json','predic_label','psl_eval.txt')
	print '4 step. Compare brute force to ground truth: '
	evaluatePrediction(indir+'/brute_force.json','predic_label','brute_force_eval.txt')
	print '5 step. Compare MLN to ground truth: '
	evaluatePrediction(indir+'/prediction_mln.json','predic_label','mln_eval.txt')
