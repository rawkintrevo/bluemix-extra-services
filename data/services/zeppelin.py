from time import sleep

import json

from scp import SCPClient

# todo
# 1) force redownload or skip re download
# 2) abscract add terp prop / add terp dep

class ZeppelinServiceOnBI:
    def __init__(self, server, username, password):
        self.server = server
        self.username = username
        self.password = password
        self.binaryLocation = "https://github.com/rawkintrevo/incubator-zeppelin/releases/download/v0.7.0-NIGHTLY-2016.08.22/zeppelin-0.7.0-SNAPSHOT.tar.gz"
        self.dirName = None
        self.useLocal = False # Use Local Copy of interpreter.json (instead of trying to download server copy
        self.connect()

    def connect(self):
        import paramiko
        print "establishing ssh %s @ %s" % (self.username, self.server)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
        self.ssh.connect(self.server, username=self.username, password=self.password)
        self.scp = SCPClient(self.ssh.get_transport())

    def setBinaryLocation(self, newLocation):
        self.binaryLocation = newLocation

    def install(self):
        self._download()
        self._untar()

    def updateConfig(self):
        self._readTerpJson()
        self._updateTerpProp('spark', 'master', 'yarn-client')
        #todo make this optional
        self.addMahoutConfig()
        self._updateTerpProp("jdbc", "hive.url", u'jdbc:hive2://' + self.server +
                                                            ':10000/default;ssl=true;sslTrustStore=/home/' +
                                                            self.username + '/zeppelin_truststore.jks;trustStorePassword=mypassword;')
        self._updateTerpProp("jdbc", "hive.user", self.username)
        self._updateTerpProp("jdbc", "hive.password", self.password)

        self._updateTerpProp("jdbc", 'bigsql.url', 'jdbc:db2://' + self.server + \
                                                     ':51000/bigsql:sslConnection=true;sslTrustStoreLocation=/home/'
                                                     + self.username +
                                                    '/zeppelin_truststore.jks;Password;mypassword;')

        self._updateTerpProp("jdbc", 'bigsql.user', self.username)
        self._updateTerpProp("jdbc", 'bigsql.password', self.password)
        self._updateTerpProp("jdbc", 'bigsql.driver', 'com.ibm.db2.jcc.DB2Driver')

        self._addTerpDep("jdbc", "org.apache.hive:hive-jdbc:0.14.0")
        self._addTerpDep("jdbc", "org.apache.hadoop:hadoop-common:2.6.0",  exclusions=["jdk.tools:jdk.tools:jar:1.6"])

        self._addTerpDep("jdbc", "/usr/iop/4.2.0.0/sqoop/lib/db2jcc.jar")

        self._writeTerpJson()

        self.scp.put('./data/resources/zeppelin/zeppelin_env.sh', './zeppelin-0.7.0-SNAPSHOT/conf/zeppelin-env.sh')
        self.scp.put('./data/resources/zeppelin/zeppelin-site.xml',
                     './zeppelin-0.7.0-SNAPSHOT/conf/zeppelin-site.xml')
        stdin, stdout, stderr = self.ssh.exec_command("chmod +x zeppelin-0.7.0-SNAPSHOT/conf/zeppelin-env.sh")
        print stdout.read()
        self._uploadTerpJson()
        stdin, stdout, stderr = self.ssh.exec_command("zeppelin-0.7.0-SNAPSHOT/bin/zeppelin-daemon.sh restart")
        print stdout.read()

    def findInstalledZeppelin(self):
        self.dirName = self._findService("zeppelin")

    def _findService(self, service_name):
        stdin, stdout, stderr = self.ssh.exec_command("ls $HOME/%s*" % service_name)
        lines = stdout.readlines()
        dirs = [l for l in lines if ":" in l]
        if len(dirs) > 1:
            print "naughty naughty- you have multiple %s installs!"
        if len(dirs) == 1:
            return dirs[0].split(":")[0]
        if len(dirs) -- 0:
            return ""

    def addMahoutConfig(self):
        mahoutDir = self._findService("apache-mahout")
        if mahoutDir == None:
            print "tried to add mahout but it's not installed!"
            return

        configs = {
            "spark.kryo.referenceTracking":"false",
            "spark.kryo.registrator": "org.apache.mahout.sparkbindings.io.MahoutKryoRegistrator",
            "spark.kryoserializer.buffer" : "32k",
            "spark.kryoserializer.buffer.max" : "600m",
            "spark.serializer" : "org.apache.spark.serializer.KryoSerializer"
        }

        for k,v in configs.iteritems():
            self._updateTerpProp("spark", k, v)


        mahoutVersion = self._findService("apache-mahout").split('-')[-1]
        terpDeps = ['%s/mahout-spark_2.10-%s-dependency-reduced.jar' % (mahoutDir, mahoutVersion),
                    "%s/mahout-spark-shell_2.10-%s.jar" % (mahoutDir, mahoutVersion),
                    "%s/mahout-math-%s.jar" % (mahoutDir, mahoutVersion),
                    "%s/mahout-math-scala_2.10-%s.jar" % (mahoutDir, mahoutVersion),
                    "%s/mahout-spark_2.10-%s.jar" % (mahoutDir, mahoutVersion)]

        for t in terpDeps:
            self._addTerpDep("spark", t)



    def _download(self):
        print "downloading %s" % self.binaryLocation
        print "todo: check if downloaded then skip if its there"
        stdin, stdout, stderr = self.ssh.exec_command(
            "wget %s" % self.binaryLocation)
        print stdout.read()
        self.tarName = self.binaryLocation.split("/")[-1]

    def _untar(self):
        print "untarring %s" % self.tarName
        stdin, stdout, stderr = self.ssh.exec_command("tar xzvf %s" % self.tarName)
        output = stdout.read()
        self.findInstalledZeppelin()
        print "untarred into %s" % self.dirName

    def start(self):
        stdin, stdout, stderr = self.ssh.exec_command(self.dirName + "/bin/zeppelin-daemon.sh status")
        zeppelin_status = stdout.read()
        if "OK" in zeppelin_status:
            print "Zeppelin already running."
        if "FAILED" in zeppelin_status:
            stdin, stdout, stderr = self.ssh.exec_command(self.dirName + "/bin/zeppelin-daemon.sh start")
            zeppelin_status = stdout.read()
            print "Status:  " , zeppelin_status
            if not "OK" in zeppelin_status:
                print stderr.read()

    def deployApp(self, prefix="", remotePort=8081, remoteAddr="127.0.0.1"):
        if prefix == "":
            print "please specify prefix. I'm not deploying with out it"
            return
        from data.webapp import deploy_app
        deploy_app(remotePort, prefix + "-zeppelin", self.server, self.username, self.password, remoteAddr)


    ###############################################################################################################
    ### Service Specific Methods
    ###############################################################################################################

    def setS3auth(self, s3user, s3bucket, aws_access_key_id, aws_secret_access_key):

        import xml.etree.ElementTree as ET
        tree = ET.parse('./data/resources/zeppelin/zeppelin-site.xml')
        root = tree.getroot()
        root.findall("./property/[name='zeppelin.notebook.s3.user']//value")[0].text = s3user
        root.findall("./property/[name='zeppelin.notebook.s3.bucket']//value")[0].text = s3bucket
        tree.write('./data/resources/zeppelin/zeppelin-site.xml')

        with open('./data/resources/zeppelin/zeppelin_env.sh', 'w') as out, \
                open('./data/resources/zeppelin/zeppelin_env.sh.template', 'r') as input:

            out.write(input.read() +  """
export ZEPPELIN_NOTEBOOK_S3_BUCKET=%s
export ZEPPELIN_NOTEBOOK_S3_USER=%s
export AWS_ACCESS_KEY_ID=%s
export AWS_SECRET_ACCESS_KEY=%s
        """ % (s3bucket, s3user, aws_access_key_id, aws_secret_access_key))


    def _downloadTerpJson(self):
        self.scp.get('%s/conf/interpreter.json' % self.dirName,
                "./data/resources/zeppelin/interpreter.json")


    def _uploadTerpJson(self):
        self.scp.put("./data/resources/zeppelin/interpreter.json", '%s/conf/interpreter.json' % self.dirName)

    def _readTerpJson(self):
        if self.useLocal != True:
            self._downloadTerpJson()
        with open("./data/resources/zeppelin/interpreter.json") as f:
            self.interpreter_json = json.load(f)

    def _writeTerpJson(self):
        with open("./data/resources/zeppelin/interpreter.json", 'wb') as f:
            json.dump(self.interpreter_json, f, sort_keys=True, indent=4)
        self._uploadTerpJson()

    def _updateTerpProp(self, terpName, property, value):
        terp_id = self._getTerpID(terpName)
        self.interpreter_json['interpreterSettings'][terp_id]['properties'][property] = value

    def _addTerpDep(self, terpName ="", dep= "", exclusions = None):
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
        for k, v in self.interpreter_json['interpreterSettings'].iteritems():
            if v['name'] == terpName:
                terp_id = k
                break

        return terp_id








