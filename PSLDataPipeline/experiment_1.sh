	Data=KBP 
	echo 'Brute force'
	python code/ruleBasedApproach.py $Data 'test' '/brute_force.json'  "user_knw_fp,user_knw_predic,lexical,syntax_path,semantic,entity" 
	echo ' '

	# echo 'PSL prediction '
	# java -jar -mx6g code/psl/kbp_relations_psl.jar "user_knw_fp,user_knw_predic,semantic"

	# echo 'MLN prediction'
	# java -jar  -mx6g code/tuffy/tuffy.jar -marginal -i code/tuffy/mln_relations/prog21.mln -e data/psl/$Data/test/mln_model.db -queryFile code/tuffy/mln_relations/query.db -r inferred-predicates/mlnHasrel.txt

	echo 'Evaluate'
	python code/evaluate_prediction.py $Data 1
	echo ' '



# Data=KBP 
# echo $Data
# # # #"user_knw_fp,user_knw_predic,lexical,syntax_path,semantic,sim_clust,entity" 
declare -a data_name=("syntax_type" "syntax_path" "lexical" "simil_veb" "simil_path" "simil_struct" "semantic" "user_knw_fp" "user_knw_predic"  "syntax_path,syntax_type,lexical" "simil_veb,simil_struct,simil_path" "user_knw_fp,user_knw_predic" "user_knw_fp,user_knw_predic,semantic" "user_knw_fp,user_knw_predic,semantic,entity" "user_knw_fp,user_knw_predic,semantic,syntax_path,entity" "user_knw_fp,user_knw_predic,semantic,syntax_type,entity" "user_knw_fp,user_knw_predic,lexical,syntax_path,semantic,entity" "user_knw_fp,user_knw_predic,lexical,syntax_path,semantic,simil_veb,entity" "user_knw_fp,user_knw_predic,lexical,syntax_path,semantic,simil_path,entity" "user_knw_fp,user_knw_predic,lexical,syntax_path,semantic,simil_struct,entity" "user_knw_fp,user_knw_predic,lexical,syntax_path,semantic,simil_veb,simil_path,entity" "user_knw_fp,user_knw_predic,lexical,syntax_path,semantic,simil_veb,simil_path,simil_struct,entity") 
# COUNTER=0
# for data_n in "${data_name[@]}" 
# do
# 	((COUNTER++))
# 	echo $data_n
# 	echo $COUNTER
# 	echo ' '

# 	echo 'Brute force'
# 	python code/ruleBasedApproach.py $Data 'test' '/brute_force.json' $data_n
# 	echo ' '

# 	echo 'PSL prediction '
# 	java -jar -mx6g code/psl/kbp_relations_psl.jar $data_n

# 	echo 'MLN prediction'
# 	java -jar  -mx6g code/tuffy/tuffy.jar -marginal -i code/tuffy/mln_relations/prog$COUNTER.mln -e data/psl/$Data/test/mln_model.db -queryFile code/tuffy/mln_relations/query.db -r inferred-predicates/mlnHasrel.txt

# 	echo 'Evaluate'
# 	python code/evaluate_prediction.py $Data 1
# 	echo ' '
# done 

# Data=Hoffman 
# echo $Data
# COUNTER=0
# for data_n in "${data_name[@]}" 
# do
# 	((COUNTER++))
# 	echo $data_n
# 	echo $COUNTER
# 	echo ' '

# 	echo 'Brute force'
# 	python code/ruleBasedApproach.py $Data 'test' '/brute_force.json' $data_n
# 	echo ' '

# 	echo 'PSL prediction '
# 	java -jar -mx6g code/psl/nyt_relations_psl.jar $data_n

# 	echo 'MLN prediction'
# 	java -jar  -mx6g code/tuffy/tuffy.jar -marginal -i code/tuffy/mln_relations/nyt/prog$COUNTER.mln -e data/psl/$Data/test/mln_model.db -queryFile code/tuffy/mln_relations/query.db -r inferred-predicates/mlnHasrel.txt

# 	echo 'Evaluate'
# 	python code/evaluate_prediction.py $Data 1
# 	echo ' '
# done 




# Data=Google 
# echo $Data
# #"user_knw_fp,user_knw_predic,lexical,syntax_path,semantic,sim_clust,entity" 
# COUNTER=0
# for data_n in "${data_name[@]}" 
# do
# 	((COUNTER++))
# 	echo $data_n
# 	echo $COUNTER
# 	echo ' '

# 	echo 'Brute force'
# 	python code/ruleBasedApproach.py $Data 'test' '/brute_force.json' $data_n
# 	echo ' '

# 	echo 'PSL prediction '
# 	java -jar -mx6g code/psl/google_relations_psl.jar $data_n

# 	echo 'MLN prediction'
# 	java -jar  -mx6g code/tuffy/tuffy.jar -marginal -i code/tuffy/mln_relations/Google/prog$COUNTER.mln -e data/psl/$Data/test/mln_model.db -queryFile code/tuffy/mln_relations/query.db -r inferred-predicates/mlnHasrel.txt

# 	echo 'Evaluate'
# 	python code/evaluate_prediction.py $Data 1
# 	echo ' '
# done 

#  # java -jar code/tuffy/tuffy.jar -marginal -i code/tuffy/mln_relations/prog.mln -e data/psl/KBP/dev/mln_model.db -queryFile code/tuffy/mln_relations/query.db -r inferred-predicates/mlnHasrel.txt


# # ("syntax_type" 
# # "syntax_path"
# # "lexical"
# # "simil_veb"
# # "simil_path"
# # "simil_struct"
# # "semantic"
# # "user_knw_fp"
# # "user_knw_predic"
# # "user_knw_fp,user_knw_predic"
# # "user_knw_fp,user_knw_predic,semantic" | PSL_context
# # "user_knw_fp,user_knw_predic,semantic,entity"	| PSL_context + PSL_ent
# # "user_knw_fp,user_knw_predic,semantic,syntax_path,entity"
# # "user_knw_fp,user_knw_predic,semantic,syntax_type,entity"
# # "user_knw_fp,user_knw_predic,lexical,syntax_path,semantic,entity" | PSL_context + PSL_ent + PSL_syntx
# # "user_knw_fp,user_knw_predic,lexical,syntax_path,semantic,simil_veb,entity"
# # "user_knw_fp,user_knw_predic,lexical,syntax_path,semantic,simil_path,entity"
# # "user_knw_fp,user_knw_predic,lexical,syntax_path,semantic,simil_struct,entity"
# # "user_knw_fp,user_knw_predic,lexical,syntax_path,semantic,simil_veb,simil_path,entity" | PSL_context + PSL_ent + PSL_syntx + PSL_sim
# # "user_knw_fp,user_knw_predic,lexical,syntax_path,semantic,simil_veb,simil_path,simil_struct,entity"
# # "user_knw_fp,user_knw_predic,lexical,syntax_path,semantic,sim_clust,entity") 
# # "syntax_path,syntax_type,lexical" || PSL_syntx
# # "simil_veb,simil_struct,simil_path" || PSL_sim

