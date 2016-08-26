

## Template:
# def startFoo(ssh):
#     check if foo is running
#     if foo isnt running:
#         start foo

def startNiFi(ssh):
    stdin, stdout, stderr = ssh.exec_command("nifi-0.7.0/bin/nifi.sh status")
    nifi_status = stdout.readlines()
    if "is currently running" in nifi_status[6]:
        print "NiFi already running."
    if "is not running" in nifi_status[6]:
        stdin, stdout, stderr = ssh.exec_command("nohup nifi-0.7.0/bin/nifi.sh start &")
