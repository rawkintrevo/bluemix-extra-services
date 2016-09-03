
from scp import SCPClient


class AbstractServiceOnBI:
    """
    AbstractService- meant to be extended per service, contains common methods such as establishing ssh connection,
    downloading, etc.
    """
    service_name = 'abstract'
    service_port = 0
    binaryLocation = ""
    install_path = ""

    config_files = {"file1" : "path/to/file1"}

    def __init__(self, server, username, password):
        self.server = server
        self.username = username
        self.password = password
        self.dirName = ""
        self.useLocal = False # Use Local Copy of interpreter.json (instead of trying to download server copy
        self.tarDownloaded = False
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
        print "installing %s" % self.service_name
        self._download()
        self._untar()

    def _findService(self, service_name= None):
        if service_name == None:
            service_name =  self.service_name
        stdin, stdout, stderr = self.ssh.exec_command("ls $HOME -p")
        lines = stdout.readlines()
        dirs = [l[:-2] for l in lines if (service_name in l) and ("/" in l)]
        if len(dirs) > 1:
            print "naughty naughty- you have multiple %s installs!"
            return dirs[0]
        elif len(dirs) == 1:
            return dirs[0]
        else:
            print "%s installation not found" % self.service_name
            return None

    def findService(self):
        if self.dirName == "":
            self.dirName = self._findService()

    def _download(self, forceRedownload= False):
        self._findDownloadedTar()
        if (not self.tarDownloaded) or forceRedownload:
            print "downloading %s" % self.binaryLocation
            stdin, stdout, stderr = self.ssh.exec_command(
                "wget %s" % self.binaryLocation)
            print stdout.read()
        else:
            print "skipping download- tar detected at %s" % self.tarName

    def _findDownloadedTar(self):
        self.tarName = self.binaryLocation.split("/")[-1]
        stdin, stdout, stderr = self.ssh.exec_command("ls %s" % self.tarName)
        if len(stdout.readlines()) == 1:
            self.tarDownloaded = True

    def _untar(self):
        if not self._findService() == None:
            print "directory already exists- skipping untar"
            return None
        try:
            print "untarring %s" % self.tarName
            stdin, stdout, stderr = self.ssh.exec_command("tar xzvf %s" % self.tarName)
            output = stdout.read()
            self.dirName = self._findService()
            print "untarred into %s" % self.dirName
        except Exception as e:
            print "unable to find tar %s, try downloading\nStacktrace:\n %s" % (self.tarName, e.message)

    def deployApp(self, prefix="", remoteAddr="127.0.0.1"):
        if prefix == "":
            print "please specify prefix. I'm not deploying with out it"
            return
        from data.webapp import deploy_app
        deploy_app(self.service_port, prefix + "-" + self.service_name, self.server, self.username, self.password, remoteAddr)

    def downloadConfig(self, config_files=None):
        """
        Method to download specified config files
        :param config:  May be a dict of form {"filename" : "location on server from project directory" }. If None (default)
        will download all relevent config files.
        :return: None
        """
        self.findService()
        if config_files == None:
            config_files = self.config_files
        for k, v in config_files.iteritems():
            self.scp.get('./%s/%s' % (self.dirName, v),
                         "./data/resources/%s/%s" % (self.service_name, k))

    def uploadConfig(self, config_files=None):
        """
        Method to download specified config files
        :param config:  May be a dict of form {"filename" : "location on server from project directory" }. If None (default)
        will download all relevent config files.
        :return: None
        """
        self.findService()
        if config_files == None:
            config_files = self.config_files
        for k, v in config_files.iteritems():
            self.scp.put(   "./data/resources/%s/%s" % (self.service_name, k),
                            './%s/%s' % (self.dirName, v),)
