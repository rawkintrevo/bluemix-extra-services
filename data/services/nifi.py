

from data.services.common import AbstractServiceOnBI

class NiFiServiceOnBI(AbstractServiceOnBI):
    service_name = 'nifi'
    service_port = 8084
    binaryLocation = "https://archive.apache.org/dist/nifi/0.7.0/nifi-0.7.0-bin.tar.gz"

    config_files = {
        "nifi.properties": "conf/nifi.properties",
        "bootstrap.conf": "bootstrap.conf",
        "nifi-env.sh": "bin/nifi-env.sh"
    }


    def start(self):
        """
        """
        stdin, stdout, stderr = self.ssh.exec_command("%s/bin/nifi.sh status" % self.dirName)
        nifi_status = stdout.readlines()
        if "is currently running" in "".join(nifi_status):
            print "NiFi already running."
        if "is not running" in nifi_status[6]:
            stdin, stdout, stderr = self.ssh.exec_command("nohup %s/bin/nifi.sh start &" % self.dirName)

    def stop(self):
        stdin, stdout, stderr = self.ssh.exec_command("%s/bin/nifi.sh stop" % self.dirName)
