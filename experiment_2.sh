#!/bin/bash
#We run experiments using three combination of rulesets.
declare -a datasets=("KBP" "Hoffman" "Google")
declare -a psl_jars=("code/psl/kbp_relations_psl.jar" "code/psl/nyt_relations_psl.jar" "code/psl/google_relations_psl.jar")
declare -a tuffy_paths=("code/tuffy/mln_relations" "code/tuffy/mln_relations/nyt" "code/tuffy/mln_relations/Google")

declare -a number_type=("2" "3" "4")
declare -a mln_folders=("12" "13" "16")
declare -a data_types=("user_knw_fp,user_knw_predic,semantic" "user_knw_fp,user_knw_predic,semantic,entity" "user_knw_fp,user_knw_predic,semantic,entity,lexical,syntax_path")
declare -a datasets_folders=("_kbp" "_nyt" "_g")

for Number in "${number_type[@]}" 
 	do
	for i in "${!datasets_folders[@]}"; do 
	Data=${datasets[$i]} 
	echo $Data
	echo ${datasets[$i]}' | '${psl_jars[$i]}' | '${tuffy_paths[$i]}
	echo $Number' | ' ${mln_folders[$i]}' | '${data_types[$i]}
	echo ' '
	mkdir data/generated/$Data/cotype

	echo 'Brute force'
	python code/ruleBasedApproach.py $Data 'train' '/brute_force.json' ${data_types[$i]}
	echo ' '

	echo 'PSL prediction '
	java -jar -mx6g ${psl_jars[$i]} 'train' ${data_types[$i]}
	echo ' '

	echo 'MLN prediction'
	java -jar  -mx6g code/tuffy/tuffy.jar -marginal -i ${tuffy_paths[$i]}/prog${mln_folders[$i]}.mln -e data/psl/$Data/train/mln_model.db -queryFile code/tuffy/mln_relations/query.db -r inferred-predicates/mlnHasrel.txt

	echo 'Evaluate'
	python code/evaluate_prediction.py $Data
	echo ' '

	#for cotype
	echo 'Convert files into CoType format'
	python code/DataPreprocessing/prepareForCotype.py $Data 'train' $Number 
	echo ' '

	echo $Number${datasets_folders[$i]}
	mkdir code/Cotype/data/source/$Number${datasets_folders[$i]}'_mln'
	mkdir code/Cotype/data/source/$Number${datasets_folders[$i]}'_psl'
	mkdir code/Cotype/data/source/$Number${datasets_folders[$i]}'_bf'
	mkdir code/Cotype/data/source/'1'${datasets_folders[$i]}'_fb'

	cp data/generated/$Data/cotype/'train_mln_'$Number.json code/Cotype/data/source/$Number${datasets_folders[$i]}'_mln'/train.json
	cp data/generated/$Data/cotype/'train_psl_'$Number.json code/Cotype/data/source/$Number${datasets_folders[$i]}'_psl'/train.json
	cp data/generated/$Data/cotype/'train_bf_'$Number.json code/Cotype/data/source/$Number${datasets_folders[$i]}'_bf'/train.json
	cp data/generated/$Data/cotype/train.json code/Cotype/data/source/'1'${datasets_folders[$i]}'_fb'/train.json
	cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number${datasets_folders[$i]}'_mln'/test.json
	cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number${datasets_folders[$i]}'_psl'/test.json
	cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number${datasets_folders[$i]}'_bf'/test.json
	cp data/generated/$Data/cotype/test.json code/Cotype/data/source/'1'${datasets_folders[$i]}'_fb'/test.json

	cp data/psl/$Data/brown code/Cotype/data/source/$Number${datasets_folders[$i]}'_mln'/brown
	cp data/psl/$Data/brown code/Cotype/data/source/$Number${datasets_folders[$i]}'_psl'/brown
	cp data/psl/$Data/brown code/Cotype/data/source/$Number${datasets_folders[$i]}'_bf'/brown
	cp data/psl/$Data/brown code/Cotype/data/source/$Number${datasets_folders[$i]}'_mln'/brown
	cp data/psl/$Data/brown code/Cotype/data/source/$Number${datasets_folders[$i]}'_psl'/brown
	cp data/psl/$Data/brown code/Cotype/data/source/$Number${datasets_folders[$i]}'_bf'/brown
	cp data/psl/$Data/brown code/Cotype/data/source/'1'${datasets_folders[$i]}'_fb'/brown
	echo '---------------------'
	done
done
