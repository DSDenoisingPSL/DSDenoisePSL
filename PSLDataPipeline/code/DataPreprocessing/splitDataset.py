# Script to generate psl input files
import sys
import json
from collections import  defaultdict

def splitDataSet(indir):
	with open(indir+'/ground_truth.json', 'r') as generatedFile,\
	open(indir+'/test.json','w') as outtest,\
	open(indir+'/train.json','w') as outtrain:
		relationsCount={}
		for line in generatedFile:
			sentDic = json.loads(line.strip('\r\n'))
			for i, rm in enumerate(sentDic['relationMentions']):
				if rm['true_label'] in relationsCount:
					relationsCount[rm['true_label']].append(sentDic)
				else:
					relationsCount[rm['true_label']]=[]
					relationsCount[rm['true_label']].append(sentDic)
		for item in relationsCount:
			testNum=0
			testCount = len(relationsCount[item])*0.3
			print item,': ',len(relationsCount[item]),' test:',testCount
			for sentDic in relationsCount[item]:
				if testCount>testNum:
					outtest.write(json.dumps(sentDic)+'\n')
					testNum+=1
				else:
					outtrain.write(json.dumps(sentDic)+'\n')



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: convert2Text.py -DATA (Google/Riedel/KBP/Hoffman/)'
        exit(-1)

    _data = sys.argv[1]
    indir = 'data/generated/' + _data 
    splitDataSet(indir)


# with open('./generated/sync_relation_mentions.json', 'r') as generatedFile,\
# 	open('./generated/train_nyt.json','w') as outtrain,\
# 	open('./generated/test_nyt.json','w') as outtest:
# 	sentenceArray =[]
# 	relationsCount={}
# 	for line in generatedFile:
# 		sentDic = json.loads(line.strip('\r\n'))
# 		sentenceArray.append(sentDic)
# 		for i, rm in enumerate(sentDic['relationMentions']):
# 			if rm['label'] in relationsCount:
# 				relationsCount[rm['label']]+=1
# 			else:
# 				relationsCount[rm['label']]=1
# 	testNum=0
# 	testCount = len(sentenceArray)*0.3
# 	relationsCountTest=relationsCount
# 	for sentDic in sentenceArray:
# 		#print sentDic
# 		flag = False
# 		for i, rm in enumerate(sentDic['relationMentions']):
# 			if rm['label']!='None':
# 				flag=True
# 				break
# 		if testCount>testNum:
# 			outtest.write(json.dumps(sentDic)+'\n')
# 			relationsCountTest[rm['label']]-=1
# 			testNum+=1
# 		else:
# 			outtrain.write(json.dumps(sentDic)+'\n')


# print len(sentenceArray),testCount, testNum,'\n\n'
  
