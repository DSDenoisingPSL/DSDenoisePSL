import sys
import json
import re
import time

def groundTruthStatistic(inFile):
	with open(inFile, 'r') as generatedFile:
		true_positive = 0.0
		true_negative = 0.0
		total = 0.0
		false_negative = 0.0
		false_positive = 0.0
		relationTypes={}
		same=0
		for line in generatedFile:
			sentDic = json.loads(line.strip('\r\n'))
			for i, rm in enumerate(sentDic['relationMentions']):
				label = rm['label']
				if rm['true_label']!=rm['label']:
					if rm['label']=='None' and rm['true_label']!='None':
						false_negative+=1
					else:
						false_positive+=1
				else:
					if rm['label']!='None':
						true_positive+=1
					else:
						true_negative+=1
				#if rm['true_label']==rm['label'] and rm['label']!='None':
				#	same+=1
				total+=1
				if label in relationTypes:
					relationTypes[label]+=1
				else:
					relationTypes[label]=1
		precision = true_positive / (true_positive+false_positive + 1e-8)
		recall = true_positive / (true_positive+false_negative + 1e-8)
		f1 = 2 * precision * recall / (precision + recall + 1e-8)
		print "Truth: precision: %f, recall: %f, f1: %f predicted # Pos RMs:%d, #Pos RMs:%d"%(precision,recall,f1,int(true_positive+false_negative), int(true_positive+false_negative))
		for t in relationTypes:
			print t,':',relationTypes[t]
		print 'Number: ',total	 
		print "Same ",same
		generatedFile.close()

def convertPredictions2Cotype(inFile,outfile):
	with open(inFile, 'r') as generatedFile, open(outfile, 'w') as fout:
		total = 0
		relationTypes={}

		for line in generatedFile:
			sentDic = json.loads(line.strip('\r\n'))
			relationMentions=[]
			rm = sentDic['relation']
			rm['label'] = rm['predic_label']
			del rm['predic_label']
			relationMentions.append(rm)
			sentDic['relationMentions']=relationMentions
			sentDic['articleId']=sentDic['indexId']
			del sentDic['relation']
			fout.write(json.dumps(sentDic)+'\n')
		generatedFile.close()
		fout.close()

def oneLabel2Another(inFile,outfile,label_type):
	with open(inFile, 'r') as generatedFile, open(outfile, 'w') as fout:
		total = 0
		relationTypes={}

		for line in generatedFile:
			sentDic = json.loads(line.strip('\r\n'))
			for i, rm in enumerate(sentDic['relationMentions']):
				rm['label'] = rm[label_type]
				del rm[label_type]
			# del sentDic['verbs']
			fout.write(json.dumps(sentDic)+'\n')
		generatedFile.close()
		fout.close()

def convertCantidate(inFile,outfile):
	with open(inFile, 'r') as generatedFile, open(outfile, 'w') as fout:
		total = 0
		relationTypes={}
		for line in generatedFile:
			sentDic = json.loads(line.strip('\r\n'))
			rm = sentDic['relation']
			sentDic_new = {}
			sentDic_new['relationMentions']=[]
			sentDic_new['relationMentions'].append(rm)
			sentDic_new['entityMentions'] = sentDic['entityMentions']
			sentDic_new['sentText'] = sentDic['sentText']
			sentDic_new['sentId'] = sentDic['sentId']
			sentDic_new['articleId']=sentDic['articleId']
			fout.write(json.dumps(sentDic_new)+'\n')
		generatedFile.close()
		fout.close()

def cutNoneRelations(indir):
	with open(indir+'/train_gt.json', 'r') as fin, open(indir+'/train_cut.json', 'w') as fout:
		relationTypes={}
		articleId=0
		noneRel = 0
		for line in fin:
			articleId+=1
			write2Json = False
			sentDic = json.loads(line.strip('\r\n'))
			em2type={}
			for i, em in enumerate(sentDic['entityMentions']):
				em2type[em['text']]=em['label']

			relationMentions=[]
			total_num=len(sentDic['relationMentions'])
			# print 'total number of rm', total_num
			current_num=0
			for rm in sentDic['relationMentions']:
				label = rm['label']
				if label == 'None':
					noneRel+=1
					current_num+=1
					if em2type[rm['em1Text']]=='LOCATION' and em2type[rm['em2Text']]=="LOCATION":
						continue
					if em2type[rm['em1Text']]=='ORGANIZATION' and em2type[rm['em2Text']]=="ORGANIZATION":
						continue
					if em2type[rm['em1Text']]=='LOCATION' and em2type[rm['em2Text']]=="PERSON":
						continue
					if em2type[rm['em1Text']]=='ORGANIZATION' and em2type[rm['em2Text']]=="LOCATION":
						continue
					if em2type[rm['em1Text']]=='LOCATION' and em2type[rm['em2Text']]=="ORGANIZATION":
						continue
					if em2type[rm['em1Text']]=='PERSON' and em2type[rm['em2Text']]=="ORGANIZATION":
						continue
					if current_num>7:
						continue
				if em2type[rm['em1Text']]=='ORGANIZATION' and em2type[rm['em2Text']]=="PERSON":
					em2Text=rm['em2Text']
					em1Text=rm['em1Text']
					rm['em1Text']=em2Text
					rm['em2Text']=em1Text
				
				write2Json = True
				relationMentions.append(rm)
				if label in relationTypes:
					relationTypes[label]+=1
				else:
					relationTypes[label]=1         
			if write2Json:
				sentDic['relationMentions']=relationMentions
				fout.write(json.dumps(sentDic) + '\n')       
		
		for t in relationTypes:
			print t,':',relationTypes[t]
		print 'Number: ',articleId,noneRel

if __name__ == "__main__":
	if len(sys.argv) != 4:
		print 'Usage: prepareForCotype.py -DATA (Google/NYT/KBP/Hoffman/)'
		exit(-1)
	
	_data = sys.argv[1]        
	_dir = sys.argv[2]
	_type = sys.argv[3]
	directory = 'data/psl/' + _data + '/' +_dir
	inputDir = 'data/source/' + _data 
	genDir = 'data/generated/' + _data +'/cotype'
	# cutNoneRelations(inputDir)
	oneLabel2Another('data/generated/' + _data +'/test.json',genDir+'/test.json','true_label')
	convertCantidate(directory+'/candidate_rm.json',genDir+'/train.json')
	# convertPredictions2Cotype(genDir+'/brute_force_4.json',genDir+'/train_bf_4.json')
	# convertPredictions2Cotype(genDir+'/brute_force_3.json',genDir+'/train_bf_3.json')
	# convertPredictions2Cotype(genDir+'/brute_force_2.json',genDir+'/train_bf_2.json')
	convertPredictions2Cotype('data/generated/' + _data+'/brute_force.json',genDir+'/train_bf_'+str(_type)+'.json')
	convertPredictions2Cotype('data/generated/' + _data+'/prediction_mln.json',genDir+'/train_mln_'+str(_type)+'.json')
	convertPredictions2Cotype('data/generated/' + _data+'/prediction_psl.json',genDir+'/train_psl_'+str(_type)+'.json')
	# groundTruthStatistic(genDir+'/test_new.json')
	# groundTruthStatistic(inputDir+'/train_cut.json')
	# convertPredictions2Cotype(directory+'/prediction_psl_kbp_2.json',genDir+'/train_psl_wl_2.json')
	# convertPredictions2Cotype(directory+'/prediction_psl_kbp_4.json',genDir+'/train_psl_wl_4.json')


 # 