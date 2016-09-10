from data.services.common import AbstractServiceOnBI

class MahoutServiceOnBI(AbstractServiceOnBI):
    service_name = 'apache-mahout'

    config_files = {
        "flink-config.yaml": "conf/flink-config.yaml",
        "guava-14.0.1.jar" : "guava-14.0.1.jar"
    }


    binaryLocation = "http://apache.osuosl.org/mahout/0.12.2/apache-mahout-distribution-0.12.2.tar.gz"

    def getVersion(self):
        self.version = self.dirName.split("-")[-1]

    def updateSparkTerpWithMahoutDeps(self):
        import json
        self.getVersion()
        with open("./data/resources/zeppelin/interpreter.json") as f:
            interpreter_json = json.load(f)

        for k, v in interpreter_json['interpreterSettings'].iteritems():
            if v['name'] == 'spark':
                spark_id = k
                break

        interpreter_json['interpreterSettings'][spark_id]['dependencies'] = \
            [{
                 u'groupArtifactVersion': u'/home/%s/%s/mahout-spark_2.10-%s-dependency-reduced.jar' % (self.username, self.dirName, self.version),
                 u'local': False},
             {u'groupArtifactVersion': u'/home/%s/%s/mahout-spark-shell_2.10-%s.jar' % (self.username, self.dirName, self.version),
              u'local': False},
             {u'groupArtifactVersion': u'/home/%s/%s/mahout-math-%s.jar' % (self.username, self.dirName, self.version),
              u'local': False},
             {u'groupArtifactVersion': u'/home/%s/%s/mahout-math-scala_2.10-%s.jar' % (self.username, self.dirName, self.version),
              u'local': False, u'exclusions': []},
             {u'groupArtifactVersion': u'/home/%s/%s/mahout-spark_2.10-%s.jar' % (self.username, self.dirName, self.version),
              u'local': False}]

        with open("./data/resources/zeppelin/interpreter.json", 'w') as f:
            json.dump(interpreter_json, f)
