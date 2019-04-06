
Number=2
NLNNumber=13
data_n="user_knw_fp,user_knw_predic,semantic"
 

# Data=Hoffman 
# echo $Data

# # echo 'Brute force'
# # python code/ruleBasedApproach.py $Data 'test' '/brute_force.json' $data_n
# # echo ' '

# echo 'PSL prediction '
# java -jar -mx6g code/psl/nyt_relations_psl.jar $data_n
# echo ' '

# echo 'MLN prediction'
# java -jar  -mx6g code/tuffy/tuffy.jar -marginal -i code/tuffy/mln_relations/nyt/prog$NLNNumber.mln -e data/psl/$Data/train/mln_model.db -queryFile code/tuffy/mln_relations/query.db -r inferred-predicates/mlnHasrel.txt
# 
# echo 'Evaluate'
# python code/evaluate_prediction.py $Data 1
# echo ' '

# #for cotype
# echo 'Convert files into CoType format'
# python code/DataPreprocessing/prepareForCotype.py $Data 'train' $Number #"2"
# echo ' '

# echo $Number'_nyt'
# cp data/generated/$Data/cotype/'train_mln_'$Number.json code/Cotype/data/source/$Number'_nyt_mln'/train.json
# cp data/generated/$Data/cotype/'train_psl_'$Number.json code/Cotype/data/source/$Number'_nyt_psl'/train.json
# # cp data/generated/$Data/cotype/'train_bf_'$Number.json code/Cotype/data/source/$Number'_nyt_bf'/train.json
# cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_nyt_mln'/test.json
# cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_nyt_psl'/test.json
# cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_nyt_bf'/test.json

# Data=KBP 
# echo $Data

# echo 'Brute force'
# python code/ruleBasedApproach.py $Data 'train' '/brute_force.json' $data_n
# echo ' '

# echo 'PSL prediction '
# java -jar -mx6g code/psl/kbp_relations_psl.jar $data_n
# echo ' '

# # echo 'MLN prediction'
# # java -jar  -mx6g code/tuffy/tuffy.jar -marginal -i code/tuffy/mln_relations/prog$NLNNumber.mln -e data/psl/$Data/test/mln_model.db -queryFile code/tuffy/mln_relations/query.db -r inferred-predicates/mlnHasrel.txt

# echo 'Evaluate'
# python code/evaluate_prediction.py $Data 1
# echo ' '

# #for cotype
# echo 'Convert files into CoType format'
# python code/DataPreprocessing/prepareForCotype.py $Data 'train' $Number #"2"
# echo ' '

# echo $Number'_kbp'
# cp data/generated/$Data/cotype/'train_mln_'$Number.json code/Cotype/data/source/$Number'_kbp_mln'/train.json
# cp data/generated/$Data/cotype/'train_psl_'$Number.json code/Cotype/data/source/$Number'_kbp_psl'/train.json
# cp data/generated/$Data/cotype/'train_bf_'$Number.json code/Cotype/data/source/$Number'_kbp_bf'/train.json
# cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_kbp_mln'/test.json
# cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_kbp_psl'/test.json
# cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_kbp_bf'/test.json

 
 
Data=Google 
echo $Data

echo 'Brute force'
python code/ruleBasedApproach.py $Data 'test' '/brute_force.json' $data_n
echo ' '

echo 'PSL prediction '
java -jar -mx6g code/psl/google_relations_psl.jar $data_n
echo ' '

echo 'MLN prediction'
java -jar  -mx6g code/tuffy/tuffy.jar -marginal -i code/tuffy/mln_relations/Google/prog$NLNNumber.mln -e data/psl/$Data/test/mln_model.db -queryFile code/tuffy/mln_relations/query.db -r inferred-predicates/mlnHasrel.txt

echo 'Evaluate'
python code/evaluate_prediction.py $Data 1
echo ' '

#for cotype
echo 'Convert files into CoType format'
python code/DataPreprocessing/prepareForCotype.py $Data 'test' $Number #"2"
echo ' '

echo $Number'_g'
cp data/generated/$Data/cotype/'train_mln_'$Number.json code/Cotype/data/source/$Number'_g_mln'/train.json
cp data/generated/$Data/cotype/'train_psl_'$Number.json code/Cotype/data/source/$Number'_g_psl'/train.json
cp data/generated/$Data/cotype/'train_bf_'$Number.json code/Cotype/data/source/$Number'_g_bf'/train.json
cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_g_mln'/test.json
cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_g_psl'/test.json
cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_g_bf'/test.json
cp data/generated/$Data/cotype/train.json code/Cotype/data/source/'1_g_fb'/train.json
cp data/generated/$Data/cotype/test.json code/Cotype/data/source/'1_g_fb'/test.json

 # Number=4 #2 #3
# NLNNumber=15 #11 #12
# data_n="user_knw_fp,user_knw_predic,semantic,entity,lexical,syntax_path"

Number=3
NLNNumber=14
data_n="user_knw_fp,user_knw_predic,semantic,entity"

# Number=2
# NLNNumber=11
# data_n="user_knw_fp,user_knw_predic,semantic"


# "user_knw_fp,user_knw_predic,semantic,entity,lexical,syntax_path" | 4 |  15 | PSL_contex_ent_syn
# "user_knw_fp,user_knw_predic,semantic,entity" | 3 |  12 | PSL_contex_ent
# "user_knw_fp,user_knw_predic,semantic" | 2 | 11 | PSL_contex 

# Data=Hoffman 
# echo $Data

# # echo 'Brute force'
# # python code/ruleBasedApproach.py $Data 'test' '/brute_force.json' $data_n
# # echo ' '

# echo 'PSL prediction '
# java -jar -mx6g code/psl/nyt_relations_psl.jar $data_n
# echo ' '

# echo 'MLN prediction'
# java -jar  -mx6g code/tuffy/tuffy.jar -marginal -i code/tuffy/mln_relations/nyt/prog$NLNNumber.mln -e data/psl/$Data/train/mln_model.db -queryFile code/tuffy/mln_relations/query.db -r inferred-predicates/mlnHasrel.txt

# echo 'Evaluate'
# python code/evaluate_prediction.py $Data 1
# echo ' '

# # #for cotype
# echo 'Convert files into CoType format'
# python code/DataPreprocessing/prepareForCotype.py $Data 'train' $Number #"2"
# # echo ' '

# echo $Number'_nyt'
# cp data/generated/$Data/cotype/'train_mln_'$Number.json code/Cotype/data/source/$Number'_nyt_mln'/train.json
# cp data/generated/$Data/cotype/'train_psl_'$Number.json code/Cotype/data/source/$Number'_nyt_psl'/train.json
# cp data/generated/$Data/cotype/'train_bf_'$Number.json code/Cotype/data/source/$Number'_nyt_bf'/train.json
# cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_nyt_mln'/test.json
# cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_nyt_psl'/test.json
# cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_nyt_bf'/test.json

# Data=KBP 
# echo $Data

# echo 'Brute force'
# python code/ruleBasedApproach.py $Data 'train' '/brute_force.json' $data_n
# echo ' '

# echo 'PSL prediction '
# java -jar -mx6g code/psl/kbp_relations_psl.jar $data_n
# echo ' '

# echo 'MLN prediction'
# # java -jar  -mx6g code/tuffy/tuffy.jar -marginal -i code/tuffy/mln_relations/prog$NLNNumber.mln -e data/psl/$Data/test/mln_model.db -queryFile code/tuffy/mln_relations/query.db -r inferred-predicates/mlnHasrel.txt

# echo 'Evaluate'
# python code/evaluate_prediction.py $Data 1
# echo ' '

# #for cotype
# echo 'Convert files into CoType format'
# python code/DataPreprocessing/prepareForCotype.py $Data 'train' $Number #"2"
# echo ' '

# echo $Number'_kbp'
# cp data/generated/$Data/cotype/'train_mln_'$Number.json code/Cotype/data/source/$Number'_kbp_mln'/train.json
# cp data/generated/$Data/cotype/'train_psl_'$Number.json code/Cotype/data/source/$Number'_kbp_psl'/train.json
# cp data/generated/$Data/cotype/'train_bf_'$Number.json code/Cotype/data/source/$Number'_kbp_bf'/train.json
# cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_kbp_mln'/test.json
# cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_kbp_psl'/test.json
# cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_kbp_bf'/test.json

 
 
Data=Google 
echo $Data

echo 'Brute force'
python code/ruleBasedApproach.py $Data 'test' '/brute_force.json' $data_n
echo ' '

echo 'PSL prediction '
java -jar -mx6g code/psl/google_relations_psl.jar $data_n
echo ' '

echo 'MLN prediction'
java -jar  -mx6g code/tuffy/tuffy.jar -marginal -i code/tuffy/mln_relations/Google/prog$NLNNumber.mln -e data/psl/$Data/test/mln_model.db -queryFile code/tuffy/mln_relations/query.db -r inferred-predicates/mlnHasrel.txt

echo 'Evaluate'
python code/evaluate_prediction.py $Data 1
echo ' '

#for cotype
echo 'Convert files into CoType format'
python code/DataPreprocessing/prepareForCotype.py $Data 'test' $Number #"2"
echo ' '

echo $Number'_g'
cp data/generated/$Data/cotype/'train_mln_'$Number.json code/Cotype/data/source/$Number'_g_mln'/train.json
cp data/generated/$Data/cotype/'train_psl_'$Number.json code/Cotype/data/source/$Number'_g_psl'/train.json
cp data/generated/$Data/cotype/'train_bf_'$Number.json code/Cotype/data/source/$Number'_g_bf'/train.json
cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_g_mln'/test.json
cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_g_psl'/test.json
cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_g_bf'/test.json

 

Number=4 #2 #3
NLNNumber=17 #11 #12
data_n="user_knw_fp,user_knw_predic,semantic,entity,lexical,syntax_path"

# Data=Hoffman 
# echo $Data

# # echo 'Brute force'
# # python code/ruleBasedApproach.py $Data 'test' '/brute_force.json' $data_n
# # echo ' '

# echo 'PSL prediction '
# java -jar -mx6g code/psl/nyt_relations_psl.jar $data_n
# echo ' '

# echo 'MLN prediction'
# java -jar  -mx6g code/tuffy/tuffy.jar -marginal -i code/tuffy/mln_relations/nyt/prog$NLNNumber.mln -e data/psl/$Data/train/mln_model.db -queryFile code/tuffy/mln_relations/query.db -r inferred-predicates/mlnHasrel.txt

# echo 'Evaluate'
# python code/evaluate_prediction.py $Data 1
# echo ' '

# #for cotype
# echo 'Convert files into CoType format'
# python code/DataPreprocessing/prepareForCotype.py $Data 'train' $Number #"2"
# echo ' '

# echo $Number'_nyt'
# cp data/generated/$Data/cotype/'train_mln_'$Number.json code/Cotype/data/source/$Number'_nyt_mln'/train.json
# cp data/generated/$Data/cotype/'train_psl_'$Number.json code/Cotype/data/source/$Number'_nyt_psl'/train.json
# cp data/generated/$Data/cotype/'train_bf_'$Number.json code/Cotype/data/source/$Number'_nyt_bf'/train.json
# cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_nyt_mln'/test.json
# cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_nyt_psl'/test.json
# cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_nyt_bf'/test.json

# Data=KBP 
# echo $Data

# echo 'Brute force'
# python code/ruleBasedApproach.py $Data 'train' '/brute_force.json' $data_n
# echo ' '

# echo 'PSL prediction '
# java -jar -mx6g code/psl/kbp_relations_psl.jar $data_n
# echo ' '

# # echo 'MLN prediction'
# # java -jar  -mx6g code/tuffy/tuffy.jar -marginal -i code/tuffy/mln_relations/prog$NLNNumber.mln -e data/psl/$Data/test/mln_model.db -queryFile code/tuffy/mln_relations/query.db -r inferred-predicates/mlnHasrel.txt

# echo 'Evaluate'
# python code/evaluate_prediction.py $Data 1
# echo ' '

# #for cotype
# echo 'Convert files into CoType format'
# python code/DataPreprocessing/prepareForCotype.py $Data 'train' $Number #"2"
# echo ' '

# echo $Number'_kbp'
# cp data/generated/$Data/cotype/'train_mln_'$Number.json code/Cotype/data/source/$Number'_kbp_mln'/train.json
# cp data/generated/$Data/cotype/'train_psl_'$Number.json code/Cotype/data/source/$Number'_kbp_psl'/train.json
# cp data/generated/$Data/cotype/'train_bf_'$Number.json code/Cotype/data/source/$Number'_kbp_bf'/train.json
# cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_kbp_mln'/test.json
# cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_kbp_psl'/test.json
# cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_kbp_bf'/test.json

 
 
Data=Google 
echo $Data

echo 'Brute force'
python code/ruleBasedApproach.py $Data 'test' '/brute_force.json' $data_n
echo ' '

echo 'PSL prediction '
java -jar -mx6g code/psl/google_relations_psl.jar $data_n
echo ' '

echo 'MLN prediction'
java -jar  -mx6g code/tuffy/tuffy.jar -marginal -i code/tuffy/mln_relations/Google/prog$NLNNumber.mln -e data/psl/$Data/test/mln_model.db -queryFile code/tuffy/mln_relations/query.db -r inferred-predicates/mlnHasrel.txt

echo 'Evaluate'
python code/evaluate_prediction.py $Data 1
echo ' '

#for cotype
echo 'Convert files into CoType format'
python code/DataPreprocessing/prepareForCotype.py $Data 'test' $Number #"2"
echo ' '

echo $Number'_g'
cp data/generated/$Data/cotype/'train_mln_'$Number.json code/Cotype/data/source/$Number'_g_mln'/train.json
cp data/generated/$Data/cotype/'train_psl_'$Number.json code/Cotype/data/source/$Number'_g_psl'/train.json
cp data/generated/$Data/cotype/'train_bf_'$Number.json code/Cotype/data/source/$Number'_g_bf'/train.json
cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_g_mln'/test.json
cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_g_psl'/test.json
cp data/generated/$Data/cotype/test.json code/Cotype/data/source/$Number'_g_bf'/test.json

 



