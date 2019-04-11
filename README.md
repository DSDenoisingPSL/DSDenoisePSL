# Noise Reduction in Distant Supervision for Relation Extraction using Probabilistic Soft Logic
This repository contains the source code for the  *[Noise Reduction in Distant Supervision for
Relation Extraction using Probabilistic Soft Logic]*.

**Task**:




## Run Experiments

### Dependencies
* python 2.7

#### Tuffy
Postgres is needed to run experiments for MLN.
Create database  and fill tuffy.conf file.

### Data
To run experiments unzip the file *data.zip* into *data*.
The psl folder contains generated predicates for each dataset.
The results of experiments are located into 'results' folder.

### Data sets contained can be downloaded from:  
#####KBP data set: 
Download: https://github.com/shanzhenren/CoType
provided by: [Ellis et al. 2012](https://www.ldc.upenn.edu/sites/www.ldc.upenn.edu/files/tackbp-workshop2013-linguistic-resources-kbp-eval.pdf)   
			 [Ling and Weld, 2012](https://dl.acm.org/citation.cfm?id=2900742)
This data set, also used by Ren et al. [2017], contains a manually annotated set with sentences from the 2013 KBP corpus [Ellis et al. 2012] and the Wiki-KBP corpus, [Ling and Weld, 2012], which was constructed via distant supervision by aligning Freebase relations with sentences from English Wikipedia articles.  The 2013 KBP corpus is used as a testset and the WIKI-KBP is used as a training corpus for the final relation extraction task.

####New York Times news corpus (NYT):
Download: https://github.com/shanzhenren/CoType
provided by: [Riedel et al., Modeling Relations and Their Mentions without labeled text](https://dl.acm.org/citation.cfm?id=1889799)
			  
This data set, provided by Riedel et al. [2010], was generated by aligning Freebase relations with sentences from the New York Times news corpus. It includes a test set with manually annotated sentences (Hoffmann et al. [2011]). 


####Google corpus:####
Download: https://code.google.com/archive/p/relation-extraction-corpus/downloads
provided by: [Google] (https://ai.googleblog.com/2013/04/50000-lessons-on-how-to-read-relation.html)

This data set was released by Google and consists of sentences sampled from Wikipedia, aligned by Freebase and judged by humans.





### First Experiment
The file *experiment_1.sh* runs the first experiment. Nessasary for each dataset: Data, PSL_JAR, TUFFY_Path.
For each subset of rules relations are predicted using the brute-force, PSL and MLN models.
Prediction for candidate relations and results for evaluation can be found in folder *data/results*.
We use the generated .jar filse to run psl models. Priginal code can be found in /code/psl/psl_relation_groovy.zip

### Second Experiment
The file *experiment_2.sh* generates the input files for CoType to perform the second experiment.
Add Cotype folder into code directory and run the script. 30 folders will be generated in the folder CoType/data/source.
Put *cotype_run_experiments.sh* file into CoType folder to run experiments.

