Data=Google #NYT KBP
echo $Data

inTestFile='./data/generated/'$Data'/test.json'
inTrainFile='./data/generated/'$Data'/train.json'
# mkdir data/psl/$Data
mkdir data/psl/$Data/test
mkdir data/psl/$Data/train
mkdir data/psl/$Data/dev

echo 'Test dataset. Generate PSL rules...'
python code/generatePSLPredicates.py $Data $inTestFile 'test'
echo ' '

# echo 'Training dataset. Generate PSL rules...'
# python code/generatePSLPredicates.py $Data $inTrainFile 'train'
# echo ' '


# 
# echo 'Dev dataset. Generate PSL rules...'
# python code/generatePSLPredicates.py $Data './data/generated/'$Data'/dev.json' 'dev'
# echo ' '

