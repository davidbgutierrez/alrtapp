import win32ui
import winsound
import win32con
import requests
import bs4
import sqlite3
import getpass
from socket import *
import uuid
ip = str(sys.argv[1])
if str(sys.argv[2]) == 80:
    port = "http://"
if str(sys.argv[2]) == 443:
    port ="https://"
uid = str(uuid.uuid4())
username = str(getpass.getuser())
conn = sqlite3.connect("uid.db")
#Abans de crear la taula, verifica que no existeix i el crea. També s'intesertarà el usuari actual a la base de dades local
tb_create = ('''CREATE TABLE users(user,uid)''')
tb_exists = ("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
if not conn.execute(tb_exists).fetchone():
    conn.execute(tb_create)
    conn.execute("INSERT INTO users(user,uid) VALUES (?,?)",(username,uid,))
    conn.commit()
#Cada vegada que es realitza un insert, s'envia els parametres insertats a la base de dades central
    requests.get("http://192.168.1.12/sqli.php?username="+username+"&uid="+uid)
us_exists = conn.execute("SELECT * FROM users WHERE user LIKE ?",('{}%'.format(username),))
us = us_exists.fetchone()
#Es comprova que l'usuari estigui en la base de dades local
if us[0] != username:
    conn.execute("INSERT INTO users(user,uid) VALUES (?,?)",(username,uid,))
    requests.get(port+ip+"alrtapp.php?username="+us[0]+"&uid="+us[1])
conn.commit()
conn.close()
serverPort = 5555
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
while True:
    connectionSocket, addr = serverSocket.accept()
    if addr[0] == '192.168.1.12':
        connectionSocket, addr = serverSocket.accept()
        messagefromclient = connectionSocket.recv(1024)
        message = str(messagefromclient, 'utf-8')
        r = requests.get(message)
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        host = soup.select('div:nth-child(2)')[0].text.strip()
        user = soup.select('div:nth-child(3)')[0].text.strip()
        winsound.MessageBeep(winsound.MB_OK)
        win32ui.MessageBox("##ALERTA DE POSSIBLE AGRESSIÓ##\n"+host+'\n'+user,"ALERTA",0x1000)
