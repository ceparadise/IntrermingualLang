import subprocess, os
from time import sleep

import common
from model import Model


class CL_ESA(Model):
    def __init__(self, en_ntf_path, fo_ntf_path, fo_lang_code):
        """
        Github https://github.com/kasooja/cl-esa
        :param en_ntf_path:
        :param fo_ntf_path:
        :param fo_lang_code:
        """
        super().__init__(fo_lang_code)
        self.en_ntf_path = en_ntf_path
        self.fo_ntf_path = fo_ntf_path
        self.project_root = os.path.join(common.ALG_DIR, 'cl-esa')
        self.output_dir = os.path.join(common.OUTPUT_DIR, self.get_model_name(), self.fo_lang_code)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.en_OTDFXML_path = os.path.join(self.output_dir, "OTDFXml_en.xml")
        self.fo_OTDFXML_path = os.path.join(self.output_dir, "OTDFXml_" + self.fo_lang_code + ".xml")
        self.en_index_path = os.path.join(self.output_dir, "OTDFIndex_en")
        self.fo_index_path = os.path.join(self.output_dir, "OTDFIndex_" + self.fo_lang_code)

        self.multi_lang_OTDFXml = os.path.join(self.output_dir, "multiLingual_OTDF.xml")
        self.new_multi_lang_OTDFXml = os.path.join(self.output_dir, "new_multiLingual_OTDF.xml")
        self.filtered_multiLingual_OTDF = os.path.join(self.output_dir, "filtered_multiLingual_OTDF.xml")
        self.final_multi_lingual_OTDFIndex = os.path.join(self.output_dir, "final_multi_lingual_OTDFIndex")
        self.model_config = os.path.join(self.project_root, "ds.clesa/load/eu.monnetproject.clesa.CLESA.properties")
        self.set_model(self.final_multi_lingual_OTDFIndex)

    def step1(self):
        config_path = os.path.join(self.project_root,
                                   "processor/processor.wiki.abstracts/load/eu.monnetproject.clesa.processor.wiki.abstracts.AbstractsOTDFProcessor.properties")
        config = self.readConfig(config_path)

        config["DBpediaNTFilePathToRead"] = self.en_ntf_path
        config['AbstractLanguageISOCode'] = "en"
        config['OTDFXmlToWrite'] = self.en_OTDFXML_path
        self.write_config(config_path, config)
        command = 'java -classpath "G:/Projects/InterLingualTrace/algorithms/cl-esa/processor/processor.wiki.abstracts/target/classes;G:/Projects/InterLingualTrace/algorithms/cl-esa/core/target/classes;G:/Projects/InterLingualTrace/algorithms/cl-esa/core/lib/trove-3.0.3.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/lucene.basic/target/classes;C:/Users/ljfnw/.m2/repository/org/apache/lucene/lucene-core/3.6.1/lucene-core-3.6.1.jar;C:/Users/ljfnw/.m2/repository/org/apache/lucene/lucene-analyzers/3.6.1/lucene-analyzers-3.6.1.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/reader/reader.rdf/target/classes;C:/Users/ljfnw/.m2/repository/junit/junit/4.10/junit-4.10.jar;C:/Users/ljfnw/.m2/repository/org/hamcrest/hamcrest-core/1.1/hamcrest-core-1.1.jar" eu.monnetproject.clesa.processor.wiki.abstracts.AbstractsOTDFProcessor'
        res = subprocess.Popen(command, cwd=os.path.join(common.ALG_DIR, "cl-esa"))
        res.wait()
        config["DBpediaNTFilePathToRead"] = self.fo_ntf_path
        config['AbstractLanguageISOCode'] = self.fo_lang_code
        config['OTDFXmlToWrite'] = self.fo_OTDFXML_path
        self.write_config(config_path, config)
        res = subprocess.Popen(command, cwd=self.project_root)
        res.wait()

    def step2(self):
        config_path = os.path.join(self.project_root,
                                   "processor/processor.wiki.abstracts/load/eu.monnetproject.clesa.processor.wiki.abstracts.AbstractsOTDFIndexer.properties")
        command = 'java -classpath "C:/Program Files/Java/jdk1.8.0_131/jre/lib/charsets.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/deploy.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/access-bridge-64.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/cldrdata.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/dnsns.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/jaccess.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/jfxrt.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/localedata.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/nashorn.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/sunec.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/sunjce_provider.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/sunmscapi.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/sunpkcs11.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/zipfs.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/javaws.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/jce.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/jfr.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/jfxswt.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/jsse.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/management-agent.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/plugin.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/resources.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/rt.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/processor/processor.wiki.abstracts/target/classes;G:/Projects/InterLingualTrace/algorithms/cl-esa/core/target/classes;C:/Users/ljfnw/.m2/repository/org/jblas/jblas/1.2.3/jblas-1.2.3.jar;C:/Users/ljfnw/.m2/repository/com/googlecode/efficient-java-matrix-library/ejml/0.23/ejml-0.23.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/core/lib/trove-3.0.3.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/lucene.basic/target/classes;C:/Users/ljfnw/.m2/repository/org/apache/lucene/lucene-core/3.6.1/lucene-core-3.6.1.jar;C:/Users/ljfnw/.m2/repository/org/apache/lucene/lucene-analyzers/3.6.1/lucene-analyzers-3.6.1.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/reader/reader.rdf/target/classes;C:/Users/ljfnw/.m2/repository/junit/junit/4.10/junit-4.10.jar;C:/Users/ljfnw/.m2/repository/org/hamcrest/hamcrest-core/1.1/hamcrest-core-1.1.jar" eu.monnetproject.clesa.processor.wiki.abstracts.AbstractsOTDFIndexer'

        config = self.readConfig(config_path)
        config['indexDirPathToWrite'] = self.fo_index_path
        config['LanguageISOCodeForIndexer'] = self.fo_lang_code
        config['OTDFXmlToRead'] = self.fo_OTDFXML_path
        self.write_config(config_path, config)
        res = subprocess.Popen(command, cwd=self.project_root)
        res.wait()
        config['indexDirPathToWrite'] = self.en_index_path
        config['LanguageISOCodeForIndexer'] = 'en'
        config['OTDFXmlToRead'] = self.en_OTDFXML_path
        self.write_config(config_path, config)
        res = subprocess.Popen(command, cwd=self.project_root)
        res.wait()

    def step3(self):
        config_path = os.path.join(self.project_root,
                                   "processor/processor.wiki.abstracts/load/eu.monnetproject.clesa.processor.wiki.abstracts.MultiLingualAbstractsOTDFProcessor.properties")
        command = 'java -classpath "C:/Program Files/Java/jdk1.8.0_131/jre/lib/charsets.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/deploy.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/access-bridge-64.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/cldrdata.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/dnsns.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/jaccess.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/jfxrt.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/localedata.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/nashorn.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/sunec.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/sunjce_provider.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/sunmscapi.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/sunpkcs11.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/zipfs.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/javaws.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/jce.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/jfr.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/jfxswt.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/jsse.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/management-agent.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/plugin.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/resources.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/rt.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/processor/processor.wiki.abstracts/target/classes;G:/Projects/InterLingualTrace/algorithms/cl-esa/core/target/classes;C:/Users/ljfnw/.m2/repository/org/jblas/jblas/1.2.3/jblas-1.2.3.jar;C:/Users/ljfnw/.m2/repository/com/googlecode/efficient-java-matrix-library/ejml/0.23/ejml-0.23.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/core/lib/trove-3.0.3.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/lucene.basic/target/classes;C:/Users/ljfnw/.m2/repository/org/apache/lucene/lucene-core/3.6.1/lucene-core-3.6.1.jar;C:/Users/ljfnw/.m2/repository/org/apache/lucene/lucene-analyzers/3.6.1/lucene-analyzers-3.6.1.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/reader/reader.rdf/target/classes;C:/Users/ljfnw/.m2/repository/junit/junit/4.10/junit-4.10.jar;C:/Users/ljfnw/.m2/repository/org/hamcrest/hamcrest-core/1.1/hamcrest-core-1.1.jar" eu.monnetproject.clesa.processor.wiki.abstracts.MultiLingualAbstractsOTDFProcessor'

        config = self.readConfig(config_path)
        config['englishOTDFIndexDirPathToRead'] = self.en_index_path
        config['abstractLanguageISOCodeThisTime'] = 'en'
        config['multiLingualOTDFXmlToWrite'] = self.multi_lang_OTDFXml
        self.write_config(config_path, config)
        print(self.readConfig(config_path))
        res = subprocess.Popen(command, cwd=self.project_root)
        res.wait()
        config['multiLingualOTDFXmlToWrite'] = self.new_multi_lang_OTDFXml
        config['otherLanguageOTDFIndexDirPathToRead'] = self.fo_index_path
        config['abstractLanguageISOCodeThisTime'] = self.fo_lang_code
        config['multiLingualOTDFXmlToRead'] = self.multi_lang_OTDFXml
        self.write_config(config_path, config)
        print(self.readConfig(config_path))
        res = subprocess.Popen(command, cwd=self.project_root)
        res.wait()

    def step4(self):
        config_path = os.path.join(self.project_root,
                                   'processor/processor.wiki.abstracts/load/eu.monnetproject.clesa.processor.wiki.abstracts.MinNoOfWordsInAllFilter.properties')
        command = 'java -classpath "C:/Program Files/Java/jdk1.8.0_131/jre/lib/charsets.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/deploy.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/access-bridge-64.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/cldrdata.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/dnsns.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/jaccess.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/jfxrt.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/localedata.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/nashorn.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/sunec.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/sunjce_provider.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/sunmscapi.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/sunpkcs11.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/zipfs.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/javaws.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/jce.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/jfr.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/jfxswt.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/jsse.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/management-agent.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/plugin.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/resources.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/rt.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/processor/processor.wiki.abstracts/target/classes;G:/Projects/InterLingualTrace/algorithms/cl-esa/core/target/classes;C:/Users/ljfnw/.m2/repository/org/jblas/jblas/1.2.3/jblas-1.2.3.jar;C:/Users/ljfnw/.m2/repository/com/googlecode/efficient-java-matrix-library/ejml/0.23/ejml-0.23.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/core/lib/trove-3.0.3.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/lucene.basic/target/classes;C:/Users/ljfnw/.m2/repository/org/apache/lucene/lucene-core/3.6.1/lucene-core-3.6.1.jar;C:/Users/ljfnw/.m2/repository/org/apache/lucene/lucene-analyzers/3.6.1/lucene-analyzers-3.6.1.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/reader/reader.rdf/target/classes;C:/Users/ljfnw/.m2/repository/junit/junit/4.10/junit-4.10.jar;C:/Users/ljfnw/.m2/repository/org/hamcrest/hamcrest-core/1.1/hamcrest-core-1.1.jar" eu.monnetproject.clesa.processor.wiki.abstracts.MinNoOfWordsInAllFilter'

        config = self.readConfig(config_path)
        config['minNoOfWordsInAll'] = '4'
        config['multiLingualOTDFXmlToRead'] = self.new_multi_lang_OTDFXml
        config['multiLingualOTDFXmlToWrite'] = self.filtered_multiLingual_OTDF
        config['maxHowManyDocs'] = '4000000'
        config["languages"] = "en;" + self.fo_lang_code
        self.write_config(config_path, config)
        res = subprocess.Popen(command, cwd=self.project_root)
        res.wait()

    def step5(self):
        config_path = os.path.join(self.project_root,
                                   "processor/processor.wiki.abstracts/load/eu.monnetproject.clesa.processor.wiki.abstracts.MultiLingualAbstractsOTDFIndexer.properties")
        command = 'java -classpath "C:/Program Files/Java/jdk1.8.0_131/jre/lib/charsets.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/deploy.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/access-bridge-64.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/cldrdata.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/dnsns.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/jaccess.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/jfxrt.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/localedata.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/nashorn.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/sunec.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/sunjce_provider.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/sunmscapi.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/sunpkcs11.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/zipfs.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/javaws.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/jce.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/jfr.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/jfxswt.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/jsse.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/management-agent.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/plugin.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/resources.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/rt.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/processor/processor.wiki.abstracts/target/classes;G:/Projects/InterLingualTrace/algorithms/cl-esa/core/target/classes;C:/Users/ljfnw/.m2/repository/org/jblas/jblas/1.2.3/jblas-1.2.3.jar;C:/Users/ljfnw/.m2/repository/com/googlecode/efficient-java-matrix-library/ejml/0.23/ejml-0.23.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/core/lib/trove-3.0.3.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/lucene.basic/target/classes;C:/Users/ljfnw/.m2/repository/org/apache/lucene/lucene-core/3.6.1/lucene-core-3.6.1.jar;C:/Users/ljfnw/.m2/repository/org/apache/lucene/lucene-analyzers/3.6.1/lucene-analyzers-3.6.1.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/reader/reader.rdf/target/classes;C:/Users/ljfnw/.m2/repository/junit/junit/4.10/junit-4.10.jar;C:/Users/ljfnw/.m2/repository/org/hamcrest/hamcrest-core/1.1/hamcrest-core-1.1.jar" eu.monnetproject.clesa.processor.wiki.abstracts.MultiLingualAbstractsOTDFIndexer'
        config = self.readConfig(config_path)
        config['indexDirPathToWrite'] = self.final_multi_lingual_OTDFIndex
        config['OTDFXmlFileToRead'] = self.filtered_multiLingual_OTDF
        config['languages'] = "en;" + self.fo_lang_code
        self.write_config(config_path, config)
        res = subprocess.Popen(command, cwd=self.project_root)
        res.wait()

    def readConfig(self, path):
        dict = {}
        with open(path) as fin:
            for line in fin:
                if line.startswith("#") or line.strip("\n\t\r ") == "":
                    continue
                line = line.strip("\n\t\r ")
                line = line.split("=")
                prop_name = line[0]
                prop_value = line[1]
                dict[prop_name] = prop_value
        return dict

    def write_config(self, path, config_dict):
        with open(path, 'w', encoding='utf8') as fout:
            for prop_name in config_dict:
                prop_value = config_dict[prop_name]
                prop_value = prop_value.replace("\\", "/")
                fout.write("{}={}\n".format(prop_name, prop_value))
                fout.flush()

    def build_model(self):
        self.step1()
        self.step2()
        self.step3()
        self.step4()
        self.step5()
        print("Finished building model for cl-esa en-{}".format(self.fo_lang_code))

    def get_cl_doc_similarity(self, doc1, doc2, doc1_lang_code, doc2_lang_code):
        command = 'java -classpath "C:/Program Files/Java/jdk1.8.0_131/jre/lib/charsets.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/deploy.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/access-bridge-64.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/cldrdata.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/dnsns.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/jaccess.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/jfxrt.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/localedata.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/nashorn.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/sunec.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/sunjce_provider.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/sunmscapi.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/sunpkcs11.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/ext/zipfs.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/javaws.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/jce.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/jfr.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/jfxswt.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/jsse.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/management-agent.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/plugin.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/resources.jar;C:/Program Files/Java/jdk1.8.0_131/jre/lib/rt.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/ds.clesa/target/classes;G:/Projects/InterLingualTrace/algorithms/cl-esa/core/target/classes;C:/Users/ljfnw/.m2/repository/org/jblas/jblas/1.2.3/jblas-1.2.3.jar;C:/Users/ljfnw/.m2/repository/com/googlecode/efficient-java-matrix-library/ejml/0.23/ejml-0.23.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/lucene.basic/target/classes;C:/Users/ljfnw/.m2/repository/org/apache/lucene/lucene-core/3.6.1/lucene-core-3.6.1.jar;C:/Users/ljfnw/.m2/repository/org/apache/lucene/lucene-analyzers/3.6.1/lucene-analyzers-3.6.1.jar;G:/Projects/InterLingualTrace/algorithms/cl-esa/core/lib/trove-3.0.3.jar;C:/Users/ljfnw/.m2/repository/junit/junit/4.10/junit-4.10.jar;C:/Users/ljfnw/.m2/repository/org/hamcrest/hamcrest-core/1.1/hamcrest-core-1.1.jar" eu.monnetproject.clesa.ds.clesa.CLESA \"{}\" \"{}\" {} {}'.format(
            doc1, doc2, doc1_lang_code, doc2_lang_code)
        res = subprocess.Popen(command, cwd=self.project_root, stdout=subprocess.PIPE)
        res.wait()
        score = res.stdout.readline()
        return (float)(score)

    def get_doc_similarity(self, doc1, doc2):
        doc1_tk = self.get_tokens(doc1)
        doc2_tk = self.get_tokens(doc2)
        doc1_lang_dict = self.split_tokens_by_lang(doc1_tk)
        doc2_lang_dict = self.split_tokens_by_lang(doc2_tk)
        sum_score = 0
        cnt = 0
        for d1_lang_code in doc1_lang_dict.keys():
            for d2_lang_code in doc2_lang_dict.keys():
                d1_doc = " ".join(doc1_lang_dict[d1_lang_code])
                d2_doc = " ".join(doc2_lang_dict[d2_lang_code])
                score = self.get_cl_doc_similarity(d1_doc, d2_doc, d1_lang_code, d2_lang_code)
                if score > 0.01:
                    sum_score += score
                    cnt += 1
        if cnt == 0:
            return 0
        else:
            return sum_score / cnt

    def get_model_name(self):
        return "CL_ESA"

    def set_model(self, model_path):
        config = self.readConfig(self.model_config)
        config['multiLingualIndexPathToRead'] = model_path
        self.write_config(self.model_config, config)


if __name__ == "__main__":
    corpus_dir = os.path.join(common.ALG_DIR, "cl-esa", "wiki_corpus")
    en_ntf = os.path.join(corpus_dir, "short-abstracts_en.nt")
    fr_ntf = os.path.join(corpus_dir, "short-abstracts-en-uris_it.nt")
    cl_esa = CL_ESA(en_ntf_path=en_ntf, fo_ntf_path=fr_ntf, fo_lang_code='it')
    cl_esa.build_model()
    cl_esa.set_model(os.path.join(cl_esa.output_dir, "final_multi_lingual_OTDFIndex"))
    text1 = "software engineering can build applications to support various activities"
    # text3 = "github can manage source code and is useful to software engineering"
    text3 = "github può gestire il codice sorgente ed è utile per l'ingegneria del software"

    print(cl_esa.get_doc_similarity(text1, text3))
