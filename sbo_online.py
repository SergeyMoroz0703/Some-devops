#!/usr/bin/python3.4

import psycopg2
import paramiko
import sys
from paramiko.client import SSHClient, SSH_PORT
from time import sleep
import sys



VPN_NAME = input("Enter a client VPN name: \n")
sip_peer=input("Enter SIP PEER of gateway \n")
gate_ip=input("Enter gateway IP adress \n")
client_name=input("Enter CLIENT NAME\n")
password=VPN_NAME.replace('-','')+'pwd'


client = SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    connection = psycopg2.connect(host='172.16.0.220', user='gofraud', password='kXLILCrAPp2yjEgH3xCp', database='main')
except psycopg2.OperationalError.diag as e:
    print(e)
C = connection.cursor()
C.execute(
  "select db_name, realm.name, realm.ip, db_server.host from instance join realm on instance.realm_id = realm.id join db_server on instance.db_server_id = db_server.id where instance.name = '{client}'".format(client=client_name))
record = C.fetchone()
db_name = record[0]
realm_name = record[1]
realm_ip = record[2]
db_server_ip = record[3]
print("Client data_base: ",db_name, "\n", "Server_name: ",realm_name, "\n", "Server_IP: ",realm_ip,"\n", "Database_IP: ", db_server_ip)
sleep(2)
C.close()
connection.close()

def change_db(db_name,sip_peer, VPN_NAME):
    try:
        connection = psycopg2.connect(host=db_server_ip, user='gofraud', password='kXLILCrAPp2yjEgH3xCp', database=db_name)
    except psycopg2.OperationalError.diag as e:
        print(e)
    C = connection.cursor()
    C.execute(
      "update sip_conf set peer_name = '{peer_name}' where name like '{peer}%'".format(peer_name=VPN_NAME, peer=sip_peer))
    connection.commit()
    C.execute(
      "update gate set protocol = 'IAX2' where simserver_password = (select secret from sip_conf where name like '{peer}%' limit 1)".format(peer=sip_peer))
    connection.commit()
    C.execute(
      "update sip_conf set lastms = '50' where name like '{peer}%'".format(peer=sip_peer)) 
    connection.commit()
    C.execute(
      "select sip_conf.name as sip_peer, sip_conf.peer_name as iax_peer, gate.protocol as protocol, sip_conf.lastms as lastms from sip_conf join gate on sip_conf.secret = gate.simserver_password where sip_conf.name like '{peer}%'order by sip_conf.name".format(peer=sip_peer))
    check_result = C.fetchall()
    colnames = [desc[0] for desc in C.description]
    print(colnames,'\n') 
    for i in range(len(check_result)):   
        print(check_result[i])
    C.close()
    connection.close()

def send_sip(sip_peer, gate_ip):
    try:
        client.connect(VPN_NAME, username='root', port=SSH_PORT, key_filename='/root/.ssh/authorized_keys')
    except paramiko.BadHostKeyException as e:
        print(e)
    except paramiko.AuthenticationException as e:
        print(e)
    except paramiko.SSHException as e:
        print(e)
    client.exec_command('echo -e '
                    '\'\n[{peer}]\n'
                    'type=friend\n'
                    'host={ip}\n'
                    'allow=g729\n'
                    'allow=g723\n'
                    'allow=alaw\n'
                    'allow=ulaw\n'
                    'qualify=yes\n'
                    'context=out\n'
                    'progressinband=never\' >> /etc/asterisk/sip.conf'.format(peer=sip_peer, ip=gate_ip))
    client.exec_command('asterisk -rx \'sip reload\'')
    client.close()  
                    
def send_iax(VPN_NAME, password, realm_ip):
    try:
        client.connect(VPN_NAME, username='root', port=SSH_PORT, key_filename='/root/.ssh/authorized_keys')
    except paramiko.BadHostKeyException as e:
        print(e)
    except paramiko.AuthenticationException as e:
        print(e)
    except paramiko.SSHException as e:
        print(e)
    client.exec_command('cp /etc/asterisk/iax.conf /etc/asterisk/iax_backup.conf')
    client.exec_command('rm /etc/asterisk/iax.conf')
    client.exec_command('echo -e '
                    '\'\n[general]\n'
                    'bindport=4571\n'
                    'disallow=all\n'
                    'allow=g729\n'
                    'bandwidth=low\n'
                    'jitterbuffer=yes\n'
                    'forcejitterbuffer=no\n\' >> /etc/asterisk/iax.conf')
    client.exec_command('echo -e '
                    '\'\nregister => {peer}:{sec}@{server_ip}\' >> /etc/asterisk/iax.conf'.format(peer=VPN_NAME, sec=password,server_ip=realm_ip))
    client.exec_command('echo -e '
                    '\'\n[{peer}]\n'
                    'type=friend\n'
                    'secret={sec}\n'
                    'trunk=yes\n'
                    'username={peer}\n'
                    'host={server_ip}\n'
                    'disallow=all\n'
                    'allow=g729\n'
                    'allow=g723\n'
                    'allow=alaw\n'
                    'allow=ulaw\n'                   
                    'autokill=no\n'
                    'requirecalltoken=no\n'
                    'context=out\n'
                    'qualify=yes\'  >> /etc/asterisk/iax.conf'.format(peer=VPN_NAME, sec=password, server_ip=realm_ip))
    client.exec_command('asterisk -rx \'iax2 reload\'')
    client.close()
    try:
        client.connect(realm_ip, username='root', port=SSH_PORT, key_filename='/root/.ssh/id_rsa')
    except paramiko.BadHostKeyException as e:
        print(e)
    except paramiko.AuthenticationException as e:
        print(e)
    except paramiko.SSHException as e:
        print(e)
    client.exec_command('echo -e '
                    '\'\n[{peer}]\n'
                    'type=friend\n'
                    'secret={sec}\n'
                    'trunk=yes\n'
                    'username={peer}\n'
                    'host=dynamic\n'
                    'disallow=all\n'
                    'allow=g729\n'
                    'allow=g723\n'
                    'allow=alaw\n'
                    'allow=ulaw\n'
                    'autokill=no\n'
                    'requirecalltoken=no\n'
                    'context=out\n'
                    'directmedia=no\n'
                    'jitterbuffer=no\n'
                    'qualify=yes\'  >> /etc/asterisk/iax.conf'.format(peer=VPN_NAME, sec=password))

    
    client.exec_command('asterisk -rx \'iax2 reload\'')
    client.close()

def send_dialplan(VPN_NAME, sip_peer):
    try:
        client.connect(VPN_NAME, username='root', port=SSH_PORT, key_filename='/root/.ssh/authorized_keys')
    except paramiko.BadHostKeyException as e:
        print(e)
    except paramiko.AuthenticationException as e:
        print(e)
    except paramiko.SSHException as e:
        print(e)
    client.exec_command('echo -e '
                    '\'\n[out]\n'
                    'exten => _{sip}.,1,Dial(SIP/{sip}/${{EXTEN}})\n'
                    '        same => 2, NoOp(DIALSTATUS=${{DIALSTATUS}})\n'
                    '        same => 3, NoOp(HANGUPCAUSE=${{HANGUPCAUSE}})\n'
                    '        same => 4, NoOP(DIALEDTIME=${{DIALEDTIME}})\n'
                    '        same => 5, NoOP(ANSWEREDTIME=${{ANSWEREDTIME}})\n\n'
                    
                    'exten => _RX.,1,Dial(IAX2/{peer_name}/${{EXTEN}})\n'
                    'exten => _RX.,n,Hangup()\n'
                    'exten => _GX.,n,Hangup()\' >> /etc/asterisk/extensions.conf'.format(sip=sip_peer, peer_name=VPN_NAME))
                                            
    client.exec_command('asterisk -rx \'dialplan reload\'')
    client.close()


def main():
    change_db(db_name,sip_peer, VPN_NAME)
    send_sip(sip_peer, gate_ip)
    send_iax(VPN_NAME, password, realm_ip)
    send_dialplan(VPN_NAME, sip_peer)

try:
    choice = sys.argv[1]
except IndexError:
    main()
try:
    if choice.lower() == 'sip':
       send_sip(sip_peer, gate_ip)
       change_db(db_name,sip_peer, VPN_NAME)
    elif choice.lower() == 'iax':
        send_iax(VPN_NAME, password, realm_ip)
    else:
        main()
except:
    pass
