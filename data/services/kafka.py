
from scp import SCPClient
from subprocess import call
from time import sleep

def installKafka(ssh):
    stdin, stdout, stderr = ssh.exec_command("wget http://apache.mesi.com.ar/kafka/0.8.2.2/kafka_2.10-0.8.2.2.tgz")
    stdin, stdout, stderr = ssh.exec_command("tar xzf kafka_2.10-0.8.2.2.tgz")
    sleep(1)  ## Give it a second before you try pushing the conf file.
    scp = SCPClient(ssh.get_transport())
    scp.put('./data/resources/kafka/server.properties', './kafka_2.10-0.8.2.2/config/server.properties')


def startKafka(ssh):
    stdin, stdout, stderr = ssh.exec_command("nohup kafka_2.10-0.8.2.2/bin/kafka-server-start.sh kafka_2.10-0.8.2.2/config/server.properties &")

def stopKafka(ssh):
    stdin, stdout, stderr = ssh.exec_command("kafka_2.10-0.8.2.2/bin/kafka-server-stop.sh")

def createServerProps(server):
    call(['cp', 'data/resources/kafka/server.properties.template', 'data/resources/kafka/server.properties'])
    f = open('data/resources/kafka/server.properties', 'ab')
    f.write("zookeeper.connect=%s:2181" % server)
    f.close()

def clearKafkaLogs(ssh):
    stdin, stdout, stderr = ssh.exec_command("rm -rf /tmp/kafka-logs")