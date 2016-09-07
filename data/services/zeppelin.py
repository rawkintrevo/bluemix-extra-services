# /**
#  * Licensed to the Apache Software Foundation (ASF) under one
#  * or more contributor license agreements.  See the NOTICE file
#  * distributed with this work for additional information
#  * regarding copyright ownership.  The ASF licenses this file
#  * to you under the Apache License, Version 2.0 (the
#  * "License"); you may not use this file except in compliance
#  * with the License.  You may obtain a copy of the License at
#  *
#  *     http://www.apache.org/licenses/LICENSE-2.0
#  *
#  * Unless required by applicable law or agreed to in writing, software
#  * distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.
#  */
import json

from data.services.common import AbstractServiceOnBI


class ZeppelinServiceOnBI(AbstractServiceOnBI):
    service_name = 'zeppelin'
    service_port = 8081
    binaryLocation = "https://github.com/rawkintrevo/incubator-zeppelin/releases/download/v0.7.0-NIGHTLY-2016.09.06/zeppelin-0.7.0-SNAPSHOT.tar.gz"
    interpreter_json = {}

    config_files = {
        "interpreter.json"  : "conf/interpreter.json",
        "zeppelin-site.xml" : "conf/zeppelin-site.xml",
        "zeppelin-env.sh"    : "conf/zeppelin-env.sh"
    }

    def start(self):
        print "starting zeppelin"
        stdin, stdout, stderr = self.ssh.exec_command(self.dirName + "/bin/zeppelin-daemon.sh status")
        zeppelin_status = stdout.read()
        if "OK" in zeppelin_status:
            print "Zeppelin already running. Restarting instead"
            stdin, stdout, stderr = self.ssh.exec_command("zeppelin-0.7.0-SNAPSHOT/bin/zeppelin-daemon.sh restart")
            print stdout.read()
        if "FAILED" in zeppelin_status:
            stdin, stdout, stderr = self.ssh.exec_command(self.dirName + "/bin/zeppelin-daemon.sh start")
            zeppelin_status = stdout.read()
            print "Status:  ", zeppelin_status
            if not "OK" in zeppelin_status:
                print stderr.read()

    def _updateMulitpleProps(self, propsList):
        for u in propsList:
            self._updateTerpProp(u[0], u[1], u[2])

    def _updateMultipleDeps(self, depsList):
        for u in depsList:
            self._addTerpDep(u[0], u[1], u[2])

    def updateConfig(self):
        self._readTerpJson()

        basicTerpPropUpdates = [
            ['spark', 'master', 'yarn-client'],
            ["jdbc", "hive.url", 'jdbc:hive2://' + self.server +
             ':10000/default;ssl=true;sslTrustStore=/home/' +
             self.username + '/zeppelin_truststore.jks;trustStorePassword=mypassword;'],
            ["jdbc", "hive.user", self.username],
            ["jdbc", "hive.password", self.password],
            ["jdbc", 'bigsql.url', 'jdbc:db2://' + self.server + \
             ':51000/bigsql:sslConnection=true;sslTrustStoreLocation=/home/'
             + self.username +
             '/zeppelin_truststore.jks;Password;mypassword;'],
            ["jdbc", 'bigsql.user', self.username],
            ["jdbc", 'bigsql.password', self.password],
            ["jdbc", 'bigsql.driver', 'com.ibm.db2.jcc.DB2Driver']
        ]

        basicTerpDeps = [
            ["jdbc", "org.apache.hive:hive-jdbc:0.14.0", [""]],
            ["jdbc", "org.apache.hadoop:hadoop-common:2.6.0",  ["jdk.tools:jdk.tools:jar:1.6"]],
            ["jdbc", "/usr/iop/4.2.0.0/sqoop/lib/db2jcc.jar", [""]]
        ]
        self._updateMulitpleProps(basicTerpPropUpdates)
        self._updateMultipleDeps(basicTerpDeps)

    def addMahoutConfig(self, terpName = None):

        if terpName == None:
            terpName = 'spark'

        print "updating '%s' with Apache Mahout dependencies and settings" % terpName

        configs = {
            "spark.kryo.referenceTracking":"false",
            "spark.kryo.registrator": "org.apache.mahout.sparkbindings.io.MahoutKryoRegistrator",
            "spark.kryoserializer.buffer" : "32k",
            "spark.kryoserializer.buffer.max" : "600m",
            "spark.serializer" : "org.apache.spark.serializer.KryoSerializer"
        }

        for k,v in configs.iteritems():
            self._updateTerpProp(terpName, k, v)

        mahoutDir = self._findService("apache-mahout")
        mahoutVersion = self._findService("apache-mahout").split('-')[-1]
        terpDeps = ['/home/%s/%s/mahout-spark_2.10-%s-dependency-reduced.jar' % (self.username, mahoutDir, mahoutVersion),
                    "/home/%s/%s/mahout-spark-shell_2.10-%s.jar" % (self.username, mahoutDir, mahoutVersion),
                    "/home/%s/%s/mahout-math-%s.jar" % (self.username, mahoutDir, mahoutVersion),
                    "/home/%s/%s/mahout-math-scala_2.10-%s.jar" % (self.username, mahoutDir, mahoutVersion),
                    "/home/%s/%s/mahout-spark_2.10-%s.jar" % (self.username, mahoutDir, mahoutVersion)]

        for t in terpDeps:
            self._addTerpDep(terpName, t)

    def setS3auth(self, s3user, s3bucket, root_key_path = "data/resources/aws/rootkey.csv"):
        aws_keys = open(root_key_path).readlines()
        aws_access_key_id = aws_keys[0].split("=")[1].replace("\n", "").replace("\r", "")
        aws_secret_access_key = aws_keys[1].split("=")[1].replace("\n", "").replace("\r", "")
        import xml.etree.ElementTree as ET
        tree = ET.parse('./data/resources/zeppelin/zeppelin-site.xml')
        root = tree.getroot()
        root.findall("./property/[name='zeppelin.notebook.s3.user']//value")[0].text = s3user
        root.findall("./property/[name='zeppelin.notebook.s3.bucket']//value")[0].text = s3bucket
        tree.write('./data/resources/zeppelin/zeppelin-site.xml')

        with open('./data/resources/zeppelin/zeppelin-env.sh', 'w') as out, \
                open('./data/resources/zeppelin/zeppelin-env.sh.template', 'r') as input:

            out.write(input.read() +  """
export ZEPPELIN_NOTEBOOK_S3_BUCKET=%s
export ZEPPELIN_NOTEBOOK_S3_USER=%s
export AWS_ACCESS_KEY_ID=%s
export AWS_SECRET_ACCESS_KEY=%s
        """ % (s3bucket, s3user, aws_access_key_id, aws_secret_access_key))

    def _readTerpJson(self):
        with open("./data/resources/zeppelin/interpreter.json") as f:
            self.interpreter_json = json.load(f)

    def _writeTerpJson(self):
        with open("./data/resources/zeppelin/interpreter.json", 'wb') as f:
            json.dump(self.interpreter_json, f, sort_keys=True, indent=4)

    def _updateTerpProp(self, terpName, property, value):
        terp_id = self._getTerpID(terpName)
        self.interpreter_json['interpreterSettings'][terp_id]['properties'][property] = value

    def _addTerpDep(self, terpName ="", dep= "", exclusions = None):
        if self.interpreter_json == {}:
            print "no interpreter.json loaded, reading last one downloaded"
            self._readTerpJson()
        terp_id = self._getTerpID(terpName)
        deps = self.interpreter_json['interpreterSettings'][terp_id]['dependencies']

        dep_dict = {
                u'groupArtifactVersion': dep,
                u'local': False

            }
        if exclusions != None:
            dep_dict["exclusions"] = exclusions
        deps.append(dep_dict)

        ## Remove Duplicate Dependencies
        seen = set()
        new_deps = list()
        for d in deps:
            t = d.items()
            if t[0] not in seen:
                seen.add(t[0])
                new_deps.append(d)

        self.interpreter_json['interpreterSettings'][terp_id]['dependencies'] = new_deps

    def _getTerpID(self, terpName):
        terp_id = None
        for k, v in self.interpreter_json['interpreterSettings'].iteritems():
            if v['name'] == terpName:
                terp_id = k
                break

        return terp_id

    def createTerp(self, original_terp_name, new_terp_name ):

        new_terp_id = new_terp_name
        orig_terp_id = self._getTerpID(original_terp_name)

        from copy import deepcopy
        self.interpreter_json['interpreterSettings'][new_terp_id] = deepcopy(
            self.interpreter_json['interpreterSettings'][orig_terp_id])
        self.interpreter_json['interpreterSettings'][new_terp_id]['name'] = new_terp_name
        self.interpreter_json['interpreterSettings'][new_terp_id]['id'] = new_terp_id
        print "created new terp '%s' from terp '%s" % (new_terp_name, original_terp_name)









