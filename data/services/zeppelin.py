import json

from scp import SCPClient
from time import sleep

class ZeppelinServiceOnBI:
    def __init__(self, server, username, password):
        self.server = server
        self.username = username
        self.password = password
        self.binaryLocation = "https://github.com/rawkintrevo/incubator-zeppelin/releases/download/v0.7.0-NIGHTLY-2016.08.22/zeppelin-0.7.0-SNAPSHOT.tar.gz"
        self.dirName = ""
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
        self._updateSparkTerp()
        print "todo need to update interpreter.json with new server address for hive"
        self.scp.put('./data/resources/zeppelin/zeppelin_env.sh', './zeppelin-0.7.0-SNAPSHOT/conf/zeppelin-env.sh')
        self.scp.put('./data/resources/zeppelin/zeppelin-site.xml',
                     './zeppelin-0.7.0-SNAPSHOT/conf/zeppelin-site.xml')
        stdin, stdout, stderr = self.ssh.exec_command("chmod +x zeppelin-0.7.0-SNAPSHOT/conf/zeppelin-env.sh")
        print stdout.read()
        self._uploadTerpJson()
        stdin, stdout, stderr = self.ssh.exec_command("zeppelin-0.7.0-SNAPSHOT/bin/zeppelin-daemon.sh restart")
        print stdout.read()

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

    def start(self):
        stdin, stdout, stderr = self.ssh.exec_command(self.dirName + "/bin/zeppelin-daemon.sh status")
        zeppelin_status = stdout.readlines()
        if "OK" in zeppelin_status:
            print "Zeppelin already running."
        if "FAILED" in zeppelin_status:
            stdin, stdout, stderr = self.ssh.exec_command(self.dirName + "/bin/zeppelin-daemon.sh start")
            zeppelin_status = stdout.readlines()
            if not "OK" in zeppelin_status:
                print "FYI: zeppelin didn't start up correctly."
                print zeppelin_status

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

        with open('./data/resources/zeppelin/zeppelin_env.sh', 'a') as f:
            f.write("""
        export ZEPPELIN_NOTEBOOK_S3_BUCKET=%s
        export ZEPPELIN_NOTEBOOK_S3_USER=%s
        export AWS_ACCESS_KEY_ID=%s
        export AWS_SECRET_ACCESS_KEY=%s
        """ % (s3bucket, s3user, aws_access_key_id, aws_secret_access_key))


    def _downloadTerpJson(self):
        self.scp.get('/home/guest/%s/conf/interpreter.json' % self.dirName,
                "./data/resources/zeppelin/interpreter.json")


    def _uploadTerpJson(self):
        self.scp.put("./data/resources/zeppelin/interpreter.json", '/home/guest/zeppelin-0.7.0-SNAPSHOT/conf/interpreter.json')

    def _readTerpJson(self):
        self._downloadTerpJson()
        with open("./data/resources/zeppelin/interpreter.json") as f:
            self.interpreter_json = json.load(f)

    def _writeTerpJson(self):
        with open("./data/resources/zeppelin/interpreter.json", 'w') as f:
            json.dump(self.interpreter_json, f)
        self._uploadTerpJson(self)

    def _updateSparkTerp(self):
        for k, v in self.interpreter_json['interpreterSettings'].iteritems():
            if v['name'] == 'spark':
                spark_id = k
                break

        self.interpreter_json['interpreterSettings'][spark_id]['properties']['master'] = "yarn-client"












