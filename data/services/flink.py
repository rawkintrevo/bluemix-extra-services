

class FlinkServiceOnBI:
    def __init__(self, server, username, password):
        self.server = server
        self.username = username
        self.password = password
        self.binaryLocation = "http://mirrors.koehn.com/apache/flink/flink-1.1.1/flink-1.1.1-bin-hadoop2-scala_2.10.tgz"
        self.dirName = ""
        self.connect()

    def connect(self):
        import paramiko
        print "establishing ssh %s @ %s" % (self.username, self.server)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
        self.ssh.connect(self.server, username= self.username, password= self.password)


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

    def updateConfig(self):
        from scp import SCPClient
        scp = SCPClient(self.ssh.get_transport())
        print "copying modified yarn-session.sh"
        scp.put("./data/resources/flink/yarn-session.sh", '/home/%s/%s/bin/yarn-session.sh' % (self.username, self.dirName))
        scp.close()

    def start(self, containers=1, otherArgs=""):
        """

        :param containers:
        :param otherArgs:  see https://ci.apache.org/projects/flink/flink-docs-master/setup/yarn_setup.html#start-flink-session
        :return:
        """
        stdin, stdout, stderr = self.ssh.exec_command(
            "%s/bin/yarn-session.sh -n %i %s" % (self.dirName, containers, otherArgs))
        self.stdout = stdout

    def deployApp(self, prefix="", remotePort=8088, remoteAddr="127.0.0.1"):
        if prefix == "":
            print "please specify prefix. I'm not deploying with out it"
            return
        from data.webapp import deploy_app
        deploy_app(remotePort, prefix+"-flink", self.server, self.username, self.password, remoteAddr)
