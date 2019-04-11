

Data=KBP # Google #|  Hoffman
PSL_JAR='code/psl/kbp_relations_psl.jar' # 'code/psl/google_relations_psl.jar' # | 'code/psl/nyt_relations_psl.jar' #  | 
TUFFY_Path='code/tuffy/mln_relations' # 'code/tuffy/mln_relations/Google' # | 'code/tuffy/mln_relations/nyt'
echo $Data

declare -a data_name=("syntax_type" "syntax_path" "lexical" "simil_veb" "simil_path" "semantic" "user_knw_fp" "user_knw_predic" "syntax_path,syntax_type,lexical" "simil_veb,simil_path" "user_knw_fp,user_knw_predic" "user_knw_fp,user_knw_predic,semantic" "user_knw_fp,user_knw_predic,semantic,entity" "user_knw_fp,user_knw_predic,semantic,entity,syntax_path" "user_knw_fp,user_knw_predic,semantic,entity,syntax_type" "user_knw_fp,user_knw_predic,semantic,entity,lexical,syntax_path" "user_knw_fp,user_knw_predic,semantic,entity,lexical,syntax_path,simil_veb" "user_knw_fp,user_knw_predic,semantic,entity,lexical,syntax_path,simil_path" "user_knw_fp,user_knw_predic,semantic,entity,lexical,syntax_path,simil_veb,simil_path")
# declare -a data_name=( "lexical" )
COUNTER=0
for data_n in "${data_name[@]}" 
do
	((COUNTER++))
	echo $data_n
	echo $COUNTER
	echo ' '

	echo 'Brute force'
	python code/ruleBasedApproach.py $Data 'test' '/brute_force.json' $data_n
	echo ' '

	echo 'PSL prediction '
	java -jar -mx6g $PSL_JAR 'test' $data_n

	echo 'MLN prediction'
	java -jar  -mx6g code/tuffy/tuffy.jar -marginal -i $TUFFY_Path'/'prog$COUNTER.mln -e data/psl/$Data/test/mln_model.db -queryFile code/tuffy/mln_relations/query.db -r inferred-predicates/mlnHasrel.txt

	echo 'Evaluate'
	python code/evaluate_prediction.py $Data
	echo ' '
done 


 
