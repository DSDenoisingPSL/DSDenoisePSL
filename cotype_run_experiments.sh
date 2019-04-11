# declare -a data_name=("1_kbp_fb" "1_nyt_fb" "1_g_fb")  

declare -a data_type=("_kbp" "_nyt" "_g")  
declare -a rule_type=("2" "3" "4")  
declare -a method_type=("_psl" "_bf" "_mln" )  

for data_n in "${data_type[@]}" 
 	do
	for rule in "${rule_type[@]}" 
	do
		for method in "${method_type[@]}" 
		do

		Data=$rule$data_n$method #$data_n   
		echo $Data

		mkdir -pv data/intermediate/$Data/em
		mkdir -pv data/intermediate/$Data/rm
		mkdir -pv data/results/$Data/em
		mkdir -pv data/results/$Data/rm

		## Generate features
		### $inputDataDir $numOfProcess $ifIncludeEntityType $ratioOfNegSample
		echo 'Generate Features...'
		python code/DataProcessor/feature_generation.py $Data 10 0 1.0
		echo ' '

		### Train ReType for Relation Extraction
		### - KBP: -negative 3 -iters 400 -lr 0.02 -transWeight 1.0
		###	- NYT: -negative 5 -iters 700 -lr 0.02 -transWeight 7.0
		### - BioInfer: -negative 5 -iters 700 -lr 0.02 -transWeight 7.0
		echo 'Learn CoType embeddings...'
        if [ "$data_n" = "_nyt" ]; then
			code/Model/retype/retype -data $Data -mode j -size 50 -negative 5 -threads 3 -alpha 0.0001 -samples 1 -iters 700 -lr 0.02 -transWeight 7.0
        else
			code/Model/retype/retype -data $Data -mode j -size 50 -negative 3 -threads 3 -alpha 0.0001 -samples 1 -iters 400 -lr 0.02 -transWeight 1.0
        fi


		echo ' '

		## (NOTE: you need to remove "none" labels in the train/test JSON files when doing relation classification)
		## parameters for relation classification:
		## - KBP: -negative 7 -iters 80 -lr 0.025 -transWeight 3.0
		##	- NYT: -negative 5 -iters 100 -lr 0.025 -transWeight 9.0
		## - BioInfer: -negative 3 -iters 400 -lr 0.02 -transWeight 1.0

		# Evaluate ReType on Relation Extraction (change the mode to "classify" for relation classification)
		echo 'Evaluate on Relation Extraction...'
		python code/Evaluation/emb_test.py extract $Data retype cosine 0.2
		python code/Evaluation/convertPredictionToJson.py $Data 0.0
		python code/Evaluation/tune_threshold.py extract $Data emb retype cosine
		done
  	done
done			


