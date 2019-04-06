# Data=KBP_psl
# echo $Data

# mkdir -pv data/psl/
# rm data/psl/*.txt
# echo 'PSL rules generation ...'
# python code/PSLModel/psl_rules_generation.py $Data

# echo 'PSL inferring ...'
# java -jar groovy/kbp_relations_psl.jar 

# echo 'convert results ...'
# python code/PSLModel/psl_convert_result.py $Data
# cp data/psl/prediction_psl.json data/source/$Data/train.json

# echo 'Cotype elation extraction: '
# ###----- generated :
# mkdir -pv data/intermediate/$Data/em
# mkdir -pv data/intermediate/$Data/rm
# mkdir -pv data/results/$Data/em
# mkdir -pv data/results/$Data/rm
# echo 'Generate Features...'
# python code/DataProcessor/feature_generation.py $Data 10 0 1.0
# echo ' '

# for num in `seq  0 30` #### !!! where 9 number of topics - 1 in file currentFile  ( 10 - 1 )
# 	do
# 		echo 'Iteration '$num
	
# 		echo 'Learn CoType embeddings...'
# 		code/Model/retype/retype -data $Data -mode j -size 50 -negative 3 -threads 3 -alpha 0.0001 -samples 1 -iters 40 -lr 0.02 -transWeight 1.0
# 		#code/Model/retype/retype -data $Data -mode j -size 50 -negative 5 -threads 3 -alpha 0.0001 -samples 1 -iters 700 -lr 0.02 -transWeight 7.0

# 		echo ' '
# 		### Evaluate ReType on Relation Extraction (change the mode to "classify" for relation classification)
# 		echo 'Evaluate on Relation Extraction...'
# 		python code/Evaluation/emb_test.py extract $Data retype cosine 0.0
# 		python code/Evaluation/convertPredictionToJson.py $Data 0.0
# 		python code/Evaluation/tune_threshold.py extract $Data emb retype cosine
# 	done


Data=KBP
echo $Data
mkdir -pv data/intermediate/$Data/em
mkdir -pv data/intermediate/$Data/rm
mkdir -pv data/results/$Data/em
mkdir -pv data/results/$Data/rm
echo 'Generate Features...'
python code/DataProcessor/feature_generation.py $Data 10 0 1.0
echo ' '
## origin
for num in `seq  0 30` #### !!! where 9 number of topics - 1 in file currentFile  ( 10 - 1 )
	do
		echo 'Iteration '$num
		### Train ReType for Relation Extraction
		echo 'Learn CoType embeddings...'
		code/Model/retype/retype -data $Data -mode j -size 50 -negative 3 -threads 3 -alpha 0.0001 -samples 1 -iters 400 -lr 0.02 -transWeight 1.0
		#code/Model/retype/retype -data $Data -mode j -size 50 -negative 5 -threads 3 -alpha 0.0001 -samples 1 -iters 700 -lr 0.02 -transWeight 7.0

		echo ' '
		### Evaluate ReType on Relation Extraction (change the mode to "classify" for relation classification)
		echo 'Evaluate on Relation Extraction...'
		python code/Evaluation/emb_test.py extract $Data retype cosine 0.0
		python code/Evaluation/convertPredictionToJson.py $Data 0.0
		python code/Evaluation/tune_threshold.py extract $Data emb retype cosine
	done

# Data=NYT_psl
# echo $Data

# mkdir -pv data/psl/
# rm data/psl/*.txt
# echo 'PSL rules generation ...'
# python code/PSLModel/psl_rules_generation.py $Data

# echo 'PSL inferring ...'
# java -jar groovy/nyt_relations_psl.jar 

# echo 'convert results ...'
# python code/PSLModel/psl_convert_result.py $Data
# cp data/psl/prediction_psl.json data/source/$Data/train.json

# echo 'Cotype elation extraction: '
# ###----- generated :
# mkdir -pv data/intermediate/$Data/em
# mkdir -pv data/intermediate/$Data/rm
# mkdir -pv data/results/$Data/em
# mkdir -pv data/results/$Data/rm
# echo 'Generate Features...'
# python code/DataProcessor/feature_generation.py $Data 10 0 1.0
# echo ' '

# for num in `seq  0 30` #### !!! where 9 number of topics - 1 in file currentFile  ( 10 - 1 )
# 	do
# 		echo 'Iteration '$num
	
# 		echo 'Learn CoType embeddings...'
# 		code/Model/retype/retype -data $Data -mode j -size 50 -negative 3 -threads 3 -alpha 0.0001 -samples 1 -iters 40 -lr 0.02 -transWeight 1.0
# 		#code/Model/retype/retype -data $Data -mode j -size 50 -negative 5 -threads 3 -alpha 0.0001 -samples 1 -iters 700 -lr 0.02 -transWeight 7.0

# 		echo ' '
# 		### Evaluate ReType on Relation Extraction (change the mode to "classify" for relation classification)
# 		echo 'Evaluate on Relation Extraction...'
# 		python code/Evaluation/emb_test.py extract $Data retype cosine 0.0
# 		python code/Evaluation/convertPredictionToJson.py $Data 0.0
# 		python code/Evaluation/tune_threshold.py extract $Data emb retype cosine
# 	done


# Data=NYT
# echo $Data
# mkdir -pv data/intermediate/$Data/em
# mkdir -pv data/intermediate/$Data/rm
# mkdir -pv data/results/$Data/em
# mkdir -pv data/results/$Data/rm
# echo 'Generate Features...'
# python code/DataProcessor/feature_generation.py $Data 10 0 1.0
# echo ' '
# ## origin
# for num in `seq  0 30` #### !!! where 9 number of topics - 1 in file currentFile  ( 10 - 1 )
# 	do
# 		echo 'Iteration '$num
# 		### Train ReType for Relation Extraction
# 		echo 'Learn CoType embeddings...'
# 		code/Model/retype/retype -data $Data -mode j -size 50 -negative 3 -threads 3 -alpha 0.0001 -samples 1 -iters 400 -lr 0.02 -transWeight 1.0
# 		#code/Model/retype/retype -data $Data -mode j -size 50 -negative 5 -threads 3 -alpha 0.0001 -samples 1 -iters 700 -lr 0.02 -transWeight 7.0

# 		echo ' '
# 		### Evaluate ReType on Relation Extraction (change the mode to "classify" for relation classification)
# 		echo 'Evaluate on Relation Extraction...'
# 		python code/Evaluation/emb_test.py extract $Data retype cosine 0.0
# 		python code/Evaluation/convertPredictionToJson.py $Data 0.0
# 		python code/Evaluation/tune_threshold.py extract $Data emb retype cosine
# 	done

 
 