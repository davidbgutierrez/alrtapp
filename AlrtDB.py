#Script que s'executarà a cada trucada al F6.
import getpass
import sqlite3
import uuid
import requests
import socket
import sys
ip = str(sys.argv[1])
if str(sys.argv[2]) == 80:
    port = "http://"
if str(sys.argv[2]) == 443:
    port ="https://"
uid = str(uuid.uuid4())
username = str(getpass.getuser())
conn = sqlite3.connect("uid.db")
us_exists = conn.execute("SELECT * FROM users WHERE user LIKE ?",('{}%'.format(username),))
us = us_exists.fetchone()
if port == 80:
    requests.get(port+ip"/alrtapp.php?username="+us[0]+"&uid="+us[1]+"&hostname="+socket.gethostname())
if port == 443:
    requests.get(port+ip"/alrtapp.php?username="+us[0]+"&uid="+us[1]+"&hostname="+socket.gethostname())
conn.close()
