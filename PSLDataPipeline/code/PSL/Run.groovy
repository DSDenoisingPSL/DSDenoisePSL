package org.linqs.psl.examples.relations;

import org.linqs.psl.application.inference.InferenceApplication;
import org.linqs.psl.application.inference.MPEInference;
import org.linqs.psl.application.learning.weight.WeightLearningApplication;
import org.linqs.psl.application.learning.weight.maxlikelihood.MaxLikelihoodMPE;
import org.linqs.psl.application.learning.weight.maxlikelihood.LazyMaxLikelihoodMPE;
import org.linqs.psl.application.learning.weight.maxlikelihood.MaxPseudoLikelihood;
import org.linqs.psl.config.Config;
import org.linqs.psl.database.Database;
import org.linqs.psl.database.DataStore;
import org.linqs.psl.database.Partition;
import org.linqs.psl.database.loading.Inserter;
import org.linqs.psl.database.rdbms.driver.H2DatabaseDriver;
import org.linqs.psl.database.rdbms.driver.H2DatabaseDriver.Type;
import org.linqs.psl.database.rdbms.driver.PostgreSQLDriver;
import org.linqs.psl.database.rdbms.RDBMSDataStore;
import org.linqs.psl.evaluation.statistics.DiscreteEvaluator;
import org.linqs.psl.evaluation.statistics.CategoricalEvaluator;
import org.linqs.psl.evaluation.statistics.RankingEvaluator;
import org.linqs.psl.evaluation.statistics.Evaluator;
import org.linqs.psl.evaluation.statistics.ContinuousEvaluator;
import org.linqs.psl.groovy.PSLModel;
import org.linqs.psl.model.Model
import org.linqs.psl.model.atom.GroundAtom;
import org.linqs.psl.model.predicate.StandardPredicate;
import org.linqs.psl.model.term.Constant;
import org.linqs.psl.model.term.ConstantType;
import org.linqs.psl.utils.textsimilarity.LevenshteinSimilarity
import org.linqs.psl.utils.textsimilarity.SubStringSimilarity
import org.linqs.psl.utils.textsimilarity.JaccardSimilarity

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.file.Paths;

public class Run {
	private static final String PARTITION_LEARN_OBSERVATIONS = "dev_observations";
	private static final String PARTITION_LEARN_TARGETS = "dev_targets";
	private static final String PARTITION_LEARN_TRUTH = "dev_truth";

	private static final String PARTITION_EVAL_OBSERVATIONS = "test_observations";
	private static final String PARTITION_EVAL_TARGETS = "test_targets";
	private static final String PARTITION_EVAL_TRUTH = "test_truth";
	
	private static final String DATA_PATH = Paths.get("..", "data/KBP").toString();
//	private static final String DATA_PATH = Paths.get("", "data/psl/Google").toString();
//	private static final String DATA_PATH = Paths.get("", "data/psl/Hoffman").toString();
	
	private static final String OUTPUT_PATH = "inferred-predicates";

	private static Logger log = LoggerFactory.getLogger(Run.class)

	private DataStore dataStore;
	private PSLModel model;
	private String ruleType;
		
	public Run() {
		String suffix = System.getProperty("user.name") + "@" + getHostname();
		String baseDBPath = Config.getString("dbpath", System.getProperty("java.io.tmpdir"));
		String dbPath = Paths.get(baseDBPath, this.getClass().getName() + "_" + suffix).toString();
		dataStore = new RDBMSDataStore(new H2DatabaseDriver(Type.Disk, dbPath, true));
		// dataStore = new RDBMSDataStore(new PostgreSQLDriver("psl", true));
		model = new PSLModel(this, dataStore);
	}

	/**
	 * Defines the logical predicates used in this model
	 */ 
	private void definePredicates() {
		model.add predicate: "DSCandRel", types: [ConstantType.UniqueStringID, ConstantType.UniqueStringID];
		model.add predicate: "Similar", types: [ConstantType.UniqueStringID, ConstantType.UniqueStringID];
		model.add predicate: "SimilarVerb", types: [ConstantType.UniqueStringID,ConstantType.UniqueStringID];
		model.add predicate: "SimilarDepenPath", types: [ConstantType.UniqueStringID,ConstantType.UniqueStringID];
		model.add predicate: "SimilarDepenStructure", types: [ConstantType.UniqueStringID,ConstantType.UniqueStringID];
		model.add predicate: "HasSimilarEntityVerbs", types: [ConstantType.UniqueStringID];
		model.add predicate: "DependencyPathLength", types: [ConstantType.UniqueStringID];
		model.add predicate: "HasDirectDependency", types: [ConstantType.UniqueStringID];
		model.add predicate: "Ent1TypeSt", types: [ConstantType.UniqueStringID, ConstantType.UniqueStringID];
		model.add predicate: "Ent2TypeSt", types: [ConstantType.UniqueStringID, ConstantType.UniqueStringID];
		model.add predicate: "Ent1TypeSp", types: [ConstantType.UniqueStringID, ConstantType.UniqueStringID];
		model.add predicate: "Ent2TypeSp", types: [ConstantType.UniqueStringID, ConstantType.UniqueStringID];
		model.add predicate: "ShortDependPath", types: [ConstantType.UniqueStringID, ConstantType.String];
		model.add predicate: "HasRel", types: [ConstantType.UniqueStringID, ConstantType.UniqueStringID];
		model.add predicate: "Ent1Type", types: [ConstantType.UniqueStringID, ConstantType.UniqueStringID];
		model.add predicate: "Ent2Type", types: [ConstantType.UniqueStringID, ConstantType.UniqueStringID];
		model.add predicate: "Ent1Capital", types: [ConstantType.UniqueStringID];
		model.add predicate: "Ent2Capital", types: [ConstantType.UniqueStringID];
		model.add function:  "HasWord"	 , implementation: new SubStringContain();
		model.add function:  "SimilarStrings"	 , implementation: new LevenshteinSimilarity();
	}

	/**
	 * Defines the rules for this model.
	 */
	private void defineRules() {
		System.out.println("Defining model rules");
		System.out.println(DATA_PATH);
		
		if(ruleType.contains('syntax_type')) {
			model.addRules("""
				2.0:DSCandRel(z,r) & !DSCandRel(z,"None") & HasDirectDependency(z)->HasRel(z,r)^2
				1.0:DSCandRel(z,r) & !HasDirectDependency(z)->HasRel(z,'None')^2
				""");
		}
		if(ruleType.contains('syntax_path')) {
			model.addRules("""
				18.0:DSCandRel(z,r) & !DSCandRel(z,"None") & DependencyPathLength(z)->HasRel(z,r)^2
				1.0:DSCandRel(z,r) & !DependencyPathLength(z)->HasRel(z,'None')^2
				""");
		}
		if(ruleType.contains('lexical')) {
			model.addRules("""
				2.0:DSCandRel(z,r) & !DSCandRel(z,"None") & HasSimilarEntityVerbs(z)->HasRel(z,r)^2
				1.0:DSCandRel(z,r) & !HasSimilarEntityVerbs(z)->HasRel(z,'None')^2
				""");
		}
		if(ruleType.contains('entity')) {
			model.addRules("""
				4.0:Ent1TypeSt(z,t) & Ent1Capital(z)->Ent1Type(z,t)^2
				4.0:Ent2TypeSt(z,t) & Ent2Capital(z)->Ent2Type(z,t)^2
				5.0:Ent1TypeSp(z,t) & Ent1Capital(z)->Ent1Type(z,t)^2
				5.0:Ent2TypeSp(z,t) & Ent2Capital(z)->Ent2Type(z,t)^2
				""");
		}else
		{
			model.addRules("""
				20.0:Ent1TypeSp(z,t)->Ent1Type(z,t)^2
				20.0:Ent2TypeSp(z,t)->Ent2Type(z,t)^2
				""");
		}
		
		if(ruleType.contains('semantic')) {
			model.addRules("""
				// remove false positive using semantic features - named entities
				6.0: DSCandRel(z,"per:place_of_death") & !Ent1Type(z,"PERSON")->!HasRel(z,"per:place_of_death")^2
				6.0: DSCandRel(z,'per:place_of_death') & !Ent2Type(z,"LOCATION")->!HasRel(z,"per:place_of_death")^2
				6.0: DSCandRel(z,'per:place_lived') & !Ent1Type(z,"PERSON") ->!HasRel(z,'per:place_lived')^2
				6.0: DSCandRel(z,'per:place_lived') & !Ent2Type(z,"LOCATION") ->!HasRel(z,'per:place_lived')^2
				6.0: DSCandRel(z,'per:place_of_birth') & !Ent1Type(z,"PERSON")->!HasRel(z,'per:place_of_birth')^2
				6.0: DSCandRel(z,'per:place_of_birth') & !Ent2Type(z,"LOCATION")->!HasRel(z,'per:place_of_birth')^2
				6.0: DSCandRel(z,'per:children') & !Ent1Type(z,"PERSON")->!HasRel(z,'per:children')^2
				6.0: DSCandRel(z,'per:children') & !Ent2Type(z,"PERSON")->!HasRel(z,'per:children')^2
				6.0: DSCandRel(z,'per:founders') & !Ent1Type(z,"PERSON") ->!HasRel(z,'per:founders')^2
				6.0: DSCandRel(z,'per:founders') & !Ent2Type(z,"ORGANIZATION")->!HasRel(z,'per:founders')^2
				6.0: DSCandRel(z,'per:company')  & !Ent1Type(z,"PERSON")->!HasRel(z,'per:company')^2
				6.0: DSCandRel(z,'per:company') & !Ent2Type(z,"ORGANIZATION")->!HasRel(z,'per:company')^2
				6.0: DSCandRel(z,'per:degree') & !Ent1Type(z,"PERSON")->!HasRel(z,'per:degree')^2
				6.0: DSCandRel(z,'per:degree') & !Ent2Type(z,"ORGANIZATION")->!HasRel(z,'per:degree')^2
				6.0: DSCandRel(z,'per:institution') & !Ent1Type(z,"PERSON")->!HasRel(z,'per:institution')^2
				6.0: DSCandRel(z,'per:institution') & !Ent2Type(z,"ORGANIZATION")->!HasRel(z,'per:institution')^2
		""");
		}
		if(ruleType.contains('user_knw_fp')) {
			model.addRules("""
			///remove false positive using userknowledge
				20.0: DSCandRel(z,'per:place_of_birth') & ShortDependPath(z,s) & !HasWord(s,'born,birth,native') -> HasRel(z,'None')^2
				20.0: DSCandRel(z,'per:place_of_death') & ShortDependPath(z,s) & !HasWord(s,'died,dead,dies,death,die') ->HasRel(z,'None')^2
				10.0: DSCandRel(z,'per:place_lived') & ShortDependPath(z,s) & !HasWord(s,'rear,raise,lived,live,move,work,home') -> HasRel(z,'None')^2
				20.0: DSCandRel(z,'per:institution') & ShortDependPath(z,s) & !HasWord(s,'enrol,study,complete,graduate,attend,studied,complete,alumni,university,institute,graduate') -> HasRel(z,'None')^2
				20.0: DSCandRel(z,'per:children') & ShortDependPath(z,s) & !HasWord(s,'son,daughter,child,mother,father,parent') -> HasRel(z,'None')^2
				10.0: DSCandRel(z,'per:founders') & ShortDependPath(z,s) & !HasWord(s,'founder,founded,found') -> HasRel(z,'None')^2
				20.0: DSCandRel(z,'per:degree') & ShortDependPath(z,s) & !HasWord(s,'bachelor,master,doctor,received') -> HasRel(z,'None')^2
		""");
		}
		if(ruleType.contains('user_knw_predic')) {
			model.addRules("""
				//false negative - user knowledge predict relations using words in sentences
				20.0: Ent1Type(z,"PERSON") & Ent2Type(z,"LOCATION") & ShortDependPath(z,s) & HasWord(s,'death,dead,died,dies') -> HasRel(z,'per:place_of_death')^2
				20.0:Ent1Type(z,"PERSON") & Ent2Type(z,"LOCATION") & ShortDependPath(z,s) & HasWord(s,'born,birth,native')-> HasRel(z,'per:place_of_birth')^2
				10.0: Ent1Type(z,"PERSON") & Ent2Type(z,"LOCATION") & ShortDependPath(z,s) & HasWord(s,'rear,raise,lived,live,moved,move,work,home,lives') -> HasRel(z,'per:place_lived')^2
				20.0: Ent1Type(z,"PERSON") & Ent2Type(z,"LOCATION") & ShortDependPath(z,s) & HasWord(s,'of') -> HasRel(z,'per:place_lived')^2
				20.0: Ent1Type(z,"PERSON") & Ent2Type(z,"PERSON") & ShortDependPath(z,s) & HasWord(s,'son,daughter,child,mother,father,parent') -> HasRel(z,'per:children')^2
//				20.0: Ent1Type(z,"PERSON") & Ent2Type(z,"ORGANIZATION") & ShortDependPath(z,s) & HasWord(s,'enrol,study,complete,graduate,attend,studied,complete,alumni,university,institute,graduate,school,received') -> HasRel(z,'per:institution')^2
//				20.0: Ent1Type(z,"PERSON") & Ent2Type(z,"ORGANIZATION") & ShortDependPath(z,s) & HasWord(s,'bachelor,master,doctor') -> HasRel(z,'per:degree')^2
				10.0: Ent1Type(z,"PERSON") & Ent2Type(z,"ORGANIZATION") & ShortDependPath(z,s) & HasWord(s,'found,founded,founder') -> HasRel(z,'per:founders')^2
				20.0: Ent1Type(z,"PERSON") & Ent2Type(z,"ORGANIZATION") & ShortDependPath(z,s) & HasWord(s,'ceo,director,chief,worker,member,corp,president,chairman') -> HasRel(z,'per:company')^2
			""");
			
//			model.addRules("""
//				1.5: DependencyPathLength(z) & Ent1Type(z,"PERSON") & Ent2Type(z,"LOCATION") -> HasRel(z,'per:place_of_death')^2
//				1.5:  DependencyPathLength(z) & Ent1Type(z,"PERSON") & Ent2Type(z,"LOCATION") -> HasRel(z,'per:place_of_birth')^2
//				1.5:  DependencyPathLength(z) & Ent1Type(z,"PERSON") & Ent2Type(z,"LOCATION") -> HasRel(z,'per:place_lived')^2
//				1.5:  DependencyPathLength(z) & Ent1Type(z,"PERSON") & Ent2Type(z,"LOCATION") -> HasRel(z,'per:nationality')^2
//				1.5:  DependencyPathLength(z) & Ent1Type(z,"PERSON") & Ent2Type(z,"PERSON") -> HasRel(z,'per:children')^2
////				1.5:  DependencyPathLength(z) & Ent1Type(z,"PERSON") & Ent2Type(z,"ORGANIZATION") -> HasRel(z,'per:institution')^2
////				1.5:  DependencyPathLength(z) & Ent1Type(z,"PERSON") & Ent2Type(z,"ORGANIZATION") -> HasRel(z,'per:degree')^2
//				1.5:  DependencyPathLength(z) & Ent1Type(z,"PERSON") & Ent2Type(z,"ORGANIZATION") -> HasRel(z,'per:ethnicity')^2
//				1.5:  DependencyPathLength(z) & Ent1Type(z,"PERSON") & Ent2Type(z,"ORGANIZATION") -> HasRel(z,'per:religion')^2
//				1.5:  DependencyPathLength(z) & Ent1Type(z,"PERSON") & Ent2Type(z,"ORGANIZATION") -> HasRel(z,'per:founders')^2
//				1.5:  DependencyPathLength(z) & Ent1Type(z,"PERSON") & Ent2Type(z,"ORGANIZATION") -> HasRel(z,'per:company')^2
//			""");
		}
		if(ruleType.contains('simil_veb')) {
			model.addRules("""
				5.0: HasRel(z,r) & r!='None' & SimilarVerb(z,z2) & (z != z2)->HasRel(z2,r)^2
				5.0: SimilarVerb(z1,z2) = SimilarVerb(z2,z1) 
				5.0: SimilarVerb(P1, P2) & SimilarVerb(P2, P3) & (P1 != P3) -> SimilarVerb(P1, P3) ^2
			""");
		}
		
		if(ruleType.contains('simil_path')) {
			model.addRules("""
				5.0: HasRel(z,r) & r!='None' & SimilarDepenPath(z,z2) & (z != z2)->HasRel(z2,r)^2
				5.0: SimilarDepenPath(z1,z2) = SimilarDepenPath(z2,z1) 
				5.0: SimilarDepenPath(P1, P2) & SimilarDepenPath(P2, P3) & (P1 != P3) -> SimilarDepenPath(P1, P3) ^2
			""");
		}
		 
		if(ruleType.contains('simil_struct')) {
			model.addRules("""
				4.0: HasRel(z,r) & r!='None' & SimilarDepenStructure(z,z2) & (z != z2)->HasRel(z2,r)^2
				4.0: SimilarDepenStructure(z1,z2) = SimilarDepenStructure(z2,z1) 
				4.0: SimilarDepenStructure(P1, P2) & SimilarDepenStructure(P2, P3) & (P1 != P3) -> SimilarDepenStructure(P1, P3) ^2
			""");
		}
	 
 		
		if(ruleType.contains('sim_clust')) {
			model.addRules("""
				5.0: SimilarDepenPath(z1,z2)->Similar(z1,z2)^2
				5.0: SimilarVerb(z1,z2)->Similar(z1,z2)^2
			    5.0: SimilarDepenStructure(z1,z2)->Similar(z1,z2)^2
				5.0: Ent1Type(z1,a) & Ent2Type(z1,b) & Ent1Type(z2,a) & Ent2Type(z2,b) & (z1!=z2)->Similar(z1,z2)^2
				5.0: ShortDependPath(z1,s1) & ShortDependPath(z2,s2) & (z1!=z2) & SimilarStrings(s1,s2)->Similar(z1,z2)^2	
				5.0: HasRel(z,r) & r!='None' & Similar(z,z2) & (z != z2)->HasRel(z2,r)^2
				5.0: Similar(z1,z2) = Similar(z2,z1) 
				5.0: !Similar(z2,z1)^2 			
			""");
	   }
	   	 
		model.addRules("""
			// Priors
			1.0:HasRel(z,+r)=1
//			0.1:!HasRel(z,r)
			0.1:!Ent1Type(z,t)
			0.1:!Ent2Type(z,t)
	 		0.5:DSCandRel(z,r)->HasRel(z,r)^2
	 """);

		log.debug("model: {}", model);
	}

	/**
	 * Load data from text files into the DataStore.
	 * Three partitions are defined and populated: observations, targets, and truth.
	 * Observations contains evidence that we treat as background knowledge and use to condition our inferences.
	 * Targets contains the inference targets - the unknown variables we wish to infer.
	 * Truth contains the true values of the inference variables and will be used to evaluate the model's performance.
	 */
	private void loadData() {
		System.out.println("Loading data into database");
		for (String type : ["dev","test"]) { //"learn",,"dev" "test",
			Partition obsPartition = dataStore.getPartition(type + "_observations");
			Partition targetsPartition = dataStore.getPartition(type + "_targets");
			Partition truthPartition = dataStore.getPartition(type + "_truth");
			
		
			Inserter inserter = dataStore.getInserter(DSCandRel, obsPartition);
			inserter.loadDelimitedData(Paths.get(DATA_PATH, type, "CandRel_obser.txt").toString());
				
			inserter = dataStore.getInserter(HasDirectDependency, obsPartition);
			inserter.loadDelimitedDataTruth(Paths.get(DATA_PATH, type, "HasDirectDependency_obser.txt").toString());
	
			inserter = dataStore.getInserter(DependencyPathLength, obsPartition);
			inserter.loadDelimitedDataTruth(Paths.get(DATA_PATH, type, "dependPathLength_obser.txt").toString());
			
			inserter = dataStore.getInserter(HasSimilarEntityVerbs, obsPartition);
			inserter.loadDelimitedDataTruth(Paths.get(DATA_PATH, type, "HasSimilarEntityVerbs_obser.txt").toString());
				
			inserter = dataStore.getInserter(ShortDependPath, obsPartition);
			inserter.loadDelimitedData(Paths.get(DATA_PATH, type, "ShortDependPath_obser.txt").toString());
			
			inserter = dataStore.getInserter(Ent1TypeSp, obsPartition);
			inserter.loadDelimitedData(Paths.get(DATA_PATH, type, "Ent1SpaCyType.txt").toString());
			
			inserter = dataStore.getInserter(Ent2TypeSp, obsPartition);
			inserter.loadDelimitedData(Paths.get(DATA_PATH, type, "Ent2SpaCyType.txt").toString());
			
			inserter = dataStore.getInserter(Ent1TypeSt, obsPartition);
			inserter.loadDelimitedData(Paths.get(DATA_PATH, type, "Ent1StanType.txt").toString());
			
			inserter = dataStore.getInserter(Ent2TypeSt, obsPartition);
			inserter.loadDelimitedData(Paths.get(DATA_PATH, type, "Ent2StanType.txt").toString());
			
			inserter = dataStore.getInserter(Ent1Capital, obsPartition);
			inserter.loadDelimitedDataTruth(Paths.get(DATA_PATH, type, "isTitleEnt1.txt").toString());

			inserter = dataStore.getInserter(Ent2Capital, obsPartition);
			inserter.loadDelimitedDataTruth(Paths.get(DATA_PATH, type, "isTitleEnt2.txt").toString());

			inserter = dataStore.getInserter(HasRel, targetsPartition);
			inserter.loadDelimitedData(Paths.get(DATA_PATH, type, "CandRel_target.txt").toString());
			
			inserter = dataStore.getInserter(Ent1Type, targetsPartition);
			inserter.loadDelimitedData(Paths.get(DATA_PATH, type, "ent1_target.txt").toString());
			
			inserter = dataStore.getInserter(Ent2Type, targetsPartition);
			inserter.loadDelimitedData(Paths.get(DATA_PATH, type, "ent2_target.txt").toString());
			
			inserter = dataStore.getInserter(HasRel, truthPartition);
			inserter.loadDelimitedData(Paths.get(DATA_PATH, type, "HasRel_true.txt").toString());
			
			if(ruleType.contains('sim_clust')) {
				inserter = dataStore.getInserter(Similar, targetsPartition);
				inserter.loadDelimitedData(Paths.get(DATA_PATH, type, "similarity_target.txt").toString());
			}
			
			if(ruleType.contains('simil_veb')) {
				inserter = dataStore.getInserter(SimilarVerb, obsPartition);
				inserter.loadDelimitedDataTruth(Paths.get(DATA_PATH, type, "verbsSimilarity_obser.txt").toString());
			}
			
			if(ruleType.contains('simil_struct')) {
				inserter = dataStore.getInserter(SimilarDepenStructure, obsPartition);
				inserter.loadDelimitedDataTruth(Paths.get(DATA_PATH, type, "depenStructureSimilarity_obser.txt").toString());
			}
			
			if(ruleType.contains('simil_path')) {
				inserter = dataStore.getInserter(SimilarDepenPath, obsPartition);
				inserter.loadDelimitedDataTruth(Paths.get(DATA_PATH, type, "depenPathSimilarity_obser.txt").toString());
			}
		}
 	}

	 /**
	  * Use the training data to learn weights for our rules and store them back in the model object.
	  */
	 private void learnWeights() {
		 System.out.println("Starting weight learning");
 
		Partition obsPartition = dataStore.getPartition(PARTITION_LEARN_OBSERVATIONS);
		Partition targetsPartition = dataStore.getPartition(PARTITION_LEARN_TARGETS);
		Partition truthPartition = dataStore.getPartition(PARTITION_LEARN_TRUTH);
		
		Set<StandardPredicate> closedPredicates = [
			DSCandRel,ShortDependPath,HasDirectDependency,DependencyPathLength,HasSimilarEntityVerbs,Ent1TypeSp,Ent2TypeSp,Ent1TypeSt,Ent2TypeSt,Ent1Capital,Ent2Capital,SimilarVerb,SimilarDepenPath,SimilarDepenStructure
		] as Set;
		
		// This database contains all the ground atoms (targets) that we want to infer.
		// It also includes the observed data (because we will run inference over this db).
		Database randomVariableDatabase = dataStore.getDatabase(targetsPartition, closedPredicates, obsPartition);

		// This database only contains the true ground atoms.
		Database observedTruthDatabase = dataStore.getDatabase(truthPartition, dataStore.getRegisteredPredicates());

		WeightLearningApplication wla = new MaxLikelihoodMPE(model, randomVariableDatabase, observedTruthDatabase);
		wla.learn();
		

		randomVariableDatabase.close();
		observedTruthDatabase.close();

		log.info("Weight learning complete");		 
		println "Learned model:"
		println model

	 }
	 
	/**
	 * Run inference to infer the unknown targets.
	 */
	private void runInference() {
		System.out.println("Starting inference");
		
		Partition obsPartition = dataStore.getPartition(PARTITION_EVAL_OBSERVATIONS);
		Partition targetsPartition = dataStore.getPartition(PARTITION_EVAL_TARGETS);

		Set<StandardPredicate> closedPredicates = [
			DSCandRel,ShortDependPath,HasDirectDependency,DependencyPathLength,HasSimilarEntityVerbs,Ent1TypeSp,Ent2TypeSp,Ent1TypeSt,Ent2TypeSt,Ent1Capital,Ent2Capital,SimilarVerb,SimilarDepenPath,SimilarDepenStructure
		] as Set;

		Database inferDB = dataStore.getDatabase(targetsPartition, closedPredicates, obsPartition);

		InferenceApplication inference = new MPEInference(model, inferDB);
		inference.inference();

		inference.close();
		inferDB.close();

		System.out.println("Inference complete");
	}

	/**
	 * Writes the output of the model into a file
	 */
	private void writeOutput(String file_name) {
		Database resultsDB = dataStore.getDatabase(dataStore.getPartition(PARTITION_EVAL_TARGETS));

		(new File(OUTPUT_PATH)).mkdirs();
		FileWriter writer = new FileWriter(Paths.get(OUTPUT_PATH, file_name).toString());

		for (GroundAtom atom : resultsDB.getAllGroundAtoms(HasRel)) {
			for (Constant argument : atom.getArguments()) {
				writer.write(argument.toString() + "\t");
			}
			writer.write("" + atom.getValue() + "\n");
		}
		writer.close();
		resultsDB.close();
		System.out.println(ruleType);
	}

	/**
	 * Run statistical evaluation scripts to determine the quality of the inferences
	 * relative to the defined truth.
	 */
	
	
	private void evalResults() {
		Set<StandardPredicate> closedPredicates = [
			DSCandRel,ShortDependPath,HasDirectDependency,DependencyPathLength,HasSimilarEntityVerbs,Ent1TypeSp,Ent2TypeSp,Ent1TypeSt,Ent2TypeSt,Ent1Capital,Ent2Capital,SimilarVerb,SimilarDepenPath,SimilarDepenStructure
		] as Set;
		
		Database resultsDB = dataStore.getDatabase(dataStore.getPartition(PARTITION_EVAL_TARGETS),
				closedPredicates, dataStore.getPartition(PARTITION_EVAL_OBSERVATIONS));
		Database truthDB = dataStore.getDatabase(dataStore.getPartition(PARTITION_EVAL_TRUTH),
				dataStore.getRegisteredPredicates());

		Evaluator eval = new CategoricalEvaluator(1);
		eval.compute(resultsDB, truthDB, HasRel);
		System.out.println(eval.getAllStats());

		resultsDB.close();
		truthDB.close();
	}

	public void run() {
		definePredicates();
		defineRules();
		loadData();
		runInference();
		writeOutput("HASREL.txt");
		evalResults();
		dataStore.close();
	}
	
	public void runWithWL() {
		definePredicates();
		defineRules();
		loadData();
		
		learnWeights();
		
		runInference();
		writeOutput("HASREL_wl.txt");
		evalResults();
		dataStore.close();
	}
	/**
	 * Run this model from the command line
	 * @param args - the command line arguments
	 */
	public static void main(String[] args) {
		String s =''
		for (int i = 0; i < args.length; i++){
			s = s.concat(args[i]+' ')
		}
		Run run = new Run();
		run.ruleType=s
//		run.ruleType='none' ///0.378698
//		run.ruleType="syntax_type";
//		run.ruleType="syntax_path";
//		run.ruleType="lexical";
//		run.ruleType="syntax_type syntax_path lexical";
//		run.ruleType="semantic";
//		run.ruleType="simil_veb";
//		run.ruleType="simil_path";
//		run.ruleType="sim_clust";		
//		run.ruleType="user_knw_fp";
//		run.ruleType="user_knw_predic"
		run.ruleType="user_knw_fp user_knw_predic entity" 
//		run.ruleType="user_knw_fp user_knw_predic semantic syntax_type lexical syntax_path entity simil_veb syntax_path"
//		run.ruleType="user_knw_fp user_knw_predic syntax_type lexical semantic"
//		run.ruleType="user_knw_fp user_knw_predic syntax_type syntax_path simil_veb"
//		run.ruleType="user_knw_fp user_knw_predic syntax_type syntax_path simil_path"
//		run.ruleType="user_knw_fp user_knw_predic syntax_type syntax_path simil_struct"
//		run.ruleType="user_knw_fp user_knw_predic syntax_type syntax_path semantic simil_veb simil_path sim_clust"
//		run.ruleType="syntax_type syntax_path lexical semantic user_knw_fp user_knw_predic simil_veb simil_path" 
//		run.ruleType="user_knw_fp user_knw_predic lexical syntax_type syntax_path semantic simil_veb simil_path entity"
		
		long startTime = System.currentTimeMillis();
		run.run();
//		run.runWithWL();
		long endTime = System.currentTimeMillis();
		System.out.println("That took " + (endTime - startTime)/1000 + " seconds");
	}

	private static String getHostname() {
		String hostname = "unknown";

		try {
			hostname = InetAddress.getLocalHost().getHostName();
		} catch (UnknownHostException ex) {
			log.warn("Hostname can not be resolved, using '" + hostname + "'.");
		}

		return hostname;
	}
}
