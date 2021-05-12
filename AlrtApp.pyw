import win32ui, winsound, win32con, sqlite3, getpass, uuid, sys, requests
from subprocess import check_output
from socket import *
hostname = check_output("hostname", shell=True).decode().rstrip()
ip = str(sys.argv[1])
if str(sys.argv[2]) == '80':
    port = "http://"
if str(sys.argv[2]) == '443':
    port = "https://"
uid = str(uuid.uuid4())
username = str(getpass.getuser())
INSERT = {'username':username, 'uid':uid}
url = port+ip+"/alrtapp.php"
conn = sqlite3.connect("uid.db")
#Abans de crear la taula, verifica que no existeix i el crea. 
#També s'afegirà l'usuari actual a la base de dades local amb la uid corresponent
tb_create = ('''CREATE TABLE users(user,uid)''')
tb_exists = ("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
#Cada vegada que es realitza un insert, s'envia els paràmetres afegits a la base de dades del servidor
if not conn.execute(tb_exists).fetchone():
    conn.execute(tb_create)
    conn.execute("INSERT INTO users(user,uid) VALUES (?,?)",(username,uid,))
    conn.commit()
    requests.get(url = url, params=INSERT)
#Es comprova que l'usuari estigui en la base de dades local
us_exists = conn.execute("SELECT * FROM users WHERE user LIKE ?",('{}%'.format(username),))
us = us_exists.fetchone()
if us[0] != username:
    conn.execute("INSERT INTO users(user,uid) VALUES (?,?)",(username,uid,))
    requests.get(url = url, params=INSERT)
    conn.commit()
if '1' in sys.argv :
    us_exists = conn.execute("SELECT * FROM users WHERE user LIKE ?",('{}%'.format(username),))
    us = us_exists.fetchone()
    ALERTA = {'username':username, 'uid':us[1], 'hostname': hostname}
    requests.get(url = url, params= ALERTA)
    conn.close()
else:
    conn.close()
    serverPort = 5555
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', serverPort))
    serverSocket.listen(1)
    while True:
        connectionSocket, addr = serverSocket.accept()
        #Acceptarà solament els missatges del servidor
        if addr[0] == ip:
            connectionSocket, addr = serverSocket.accept()
            messagefromclient = connectionSocket.recv(1024)
            message = str(messagefromclient, 'utf-8')
            winsound.MessageBeep(winsound.MB_OK)
            win32ui.MessageBox(message,"ALERTA",0x1000)
