

class MahoutServiceOnBI:
    def __init__(self, server, username, password):
        self.server = server
        self.username = username
        self.password = password
        self.binaryLocation = "wget http://mirror.reverse.net/pub/apache/mahout/0.12.2/apache-mahout-distribution-0.12.2.tar.gz"
        self.dirName = ""
        self.connect()

    def connect(self):
        import paramiko
        print "establishing ssh %s @ %s" % (self.username, self.server)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
        self.ssh.connect(self.server, username=self.username, password=self.password)

    def setBinaryLocation(self, newLocation):
        self.binaryLocation = newLocation

    def install(self):
        self._download()
        self._untar()

    def _download(self):
        print "downloading %s" % self.binaryLocation
        stdin, stdout, stderr = self.ssh.exec_command(
            "wget %s" % self.binaryLocation)
        print stdout.read()
        self.tarName = self.binaryLocation.split("/")[-1]

    def _untar(self):
        print "untarring %s" % self.tarName
        stdin, stdout, stderr = self.ssh.exec_command("tar xzvf %s" % self.tarName)
        output = stdout.read()
        self.dirName = output.split("\n")[0][:-1]
        print "untarred into %s" % self.dirName

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
