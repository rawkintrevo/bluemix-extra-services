from data.services.common import AbstractServiceOnBI

class FlinkServiceOnBI(AbstractServiceOnBI):
    service_name = 'flink'
    service_port = 8088
    binaryLocation = "http://mirrors.koehn.com/apache/flink/flink-1.1.1/flink-1.1.1-bin-hadoop2-scala_2.10.tgz"

    config_files = {
        "yarn-session.sh": "bin/yarn-session.sh"
    }

    def start(self, containers=1, otherArgs=""):
        """
        :param containers:
        :param otherArgs:  see https://ci.apache.org/projects/flink/flink-docs-master/setup/yarn_setup.html#start-flink-session
        :return:
        """
        stdin, stdout, stderr = self.ssh.exec_command(
            "%s/bin/yarn-session.sh -n %i %s" % (self.dirName, containers, otherArgs))
        self.stdout = stdout
