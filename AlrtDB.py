#Script que s'executarà a cada inici de sessió i cada trucada al F6.
import getpass
import sqlite3
import uuid
import requests
import socket
#Genera una clau aleatoria
uid = str(uuid.uuid4())
#Ficam l'usuari actual dins de la varible
username = str(getpass.getuser())
#Es conecta a la base de dades
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
    requests.get("http://192.168.1.12/sqli.php?username="+us[0]+"&uid="+us[1])
conn.commit()
#Si no es realitza cap insert, s'envia el nom d'usuari i la seva uid personal a l'aplicació web
requests.get("http://192.168.1.12/alrtapp.php?username="+us[0]+"&uid="+us[1]+"&hostname="+socket.gethostname())
conn.close()
