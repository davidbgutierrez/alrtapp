from tkinter import *
import sqlite3, time, getpass, uuid, sys, re, requests, threading, ctypes, random, string, pkg_resources.py2_warn
from Crypto.Cipher import AES
from base64 import b64decode
from Crypto import Random
from Crypto.Util.Padding import unpad
from subprocess import check_output
from subprocess import DEVNULL
from socket import *
from infi.systray import SysTrayIcon
from pynput.keyboard import Key, Listener
from pynput import keyboard
def gui(mess,check):
    root = Tk()
    def lock():
        root.destroy()
        ctypes.windll.user32.LockWorkStation()
    if check == 1:
        w = 350
        h = 100
        back = "LIGHT CYAN"
        fore = "RED"
        title = "ERROR"
        exitButton = Button(root, text="Sortir", command=root.destroy, font="verdana", bg="KHAKI", fg="BLACK", width=20)
        exitButton.pack(side=BOTTOM)
    else:
        w = 500
        h = 250
        back = "FIREBRICK3"
        fore = "GHOST WHITE"
        title = "ALERTA D'AGRESSIÓ"
        goButton =  Button(root, text="Acudir",command=lock, font="verdana", bg="PALE GREEN", fg="BLACK", width=19)
        goButton.place(relx=1.0, rely=1.0, anchor=SE)
        exitButton = Button(root, text="Sortir", command=root.destroy, font="verdana", bg="LIGHT GOLDENROD", fg="BLACK", width=19)
        exitButton.place(relx=0, rely=1, anchor=SW)
    root.resizable(0, 0)
    root.config(bg=back)
    root.wm_title(title)
    root.wm_attributes("-topmost", 1)
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    missatge = Label (root, text=mess, font="verdana", bg=back, fg=fore)
    missatge.place(relx=0.5, rely=0.5, anchor=CENTER)
    root.iconbitmap('icono.ico')
    root.mainloop()
def switch(var):
    return{
        '80': "http://",
        '443': "https://"
    }.get(var,False)
hostname = check_output("hostname", stdin=DEVNULL, stderr=DEVNULL, shell=True).decode('utf-8').rstrip()
if len(sys.argv) <= 2:
    gui("Falta introduïr paràmetres",1)
    sys.exit(1)
ip = str(sys.argv[1])
if (switch(sys.argv[2]) == False):
    gui("Segon paràmetre no valid.",1)
    sys.exit(1)
port = switch(sys.argv[2])
uid = str(uuid.uuid4())
username = str(getpass.getuser())
INSERT = {'username':username, 'uid':uid}
url = port+ip+"/alrtapp.php"
try:
    requests.get(url = url)
except requests.ConnectionError:
    gui("Error de connexió amb el servidor",1)
    sys.exit(1)
conn = sqlite3.connect("database.db")
tb_uid = ('''CREATE TABLE users(user,uid)''')
tb_cypher= ('''CREATE TABLE cypher(key,iv,secret)''')
tb_exists = ("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
cypher_exists = ("SELECT name FROM sqlite_master WHERE type='table' AND name='cypher'")
if not conn.execute(tb_exists).fetchone():
    conn.execute(tb_uid)
    conn.commit()
if not conn.execute(cypher_exists).fetchone():
    conn.execute(tb_cypher)
    conn.commit()
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM cypher')
cur_result = cur.fetchone()
secret_1 = ''.join((random.choice(string.ascii_letters) for x in range(25))) 
secret_1 += ''.join((random.choice(string.digits) for x in range(25))) 
sam_list = list(secret_1)
random.shuffle(sam_list)
secret = ''.join(sam_list)
iv= ''.join((random.choice(string.digits) for x in range(16)))  
key = ''.join((random.choice(string.ascii_letters) for x in range(16)))
KEY = {'hostname': hostname, 'key': key, 'iv': iv, 'secret':secret}
if cur_result[0] == 0:
	try:
		requests.get(url = url, params=KEY)
	except requests.ConnectionError:
		conn.close()
		gui("Error de connexió amb el servidor",1)
		sys.exit(1)
conn.execute("INSERT INTO cypher(key,iv,secret) VALUES (?,?,?)",(key,iv,secret))
conn.commit()
us_exists = conn.execute("SELECT user,uid FROM users WHERE user LIKE ?",('{}%'.format(username),))
us = us_exists.fetchone()
if str(us) == 'None' :
    requests.get(url = url, params=INSERT)
    conn.execute("INSERT INTO users(user,uid) VALUES (?,?)",(username,uid,))
    conn.commit()
conn.close()
def on_press(key):
    if key == Key.f6:
        root = Tk()
        def no():
            root.destroy()
        def enviar():   
            conn = sqlite3.connect("uid.db")
            us_exists = conn.execute("SELECT user,uid FROM users WHERE user LIKE ?",('{}%'.format(username),))
            us = us_exists.fetchone()
            conn.close()
            root.destroy()
            ALERTA = {'username':username, 'uid':us[1], 'hostname': hostname}
            try:
                requests.get(url = url, params=ALERTA)
            except requests.ConnectionError:
                gui("Error de connexió amb el servidor",1)
        w = 250
        h = 150
        back = "dark blue"
        fore = "ghost white"
        title = "ALERTA"
        yesButton =  Button(root, text="Si",command=enviar, font="verdana", bg="green", fg="white", width=9)
        yesButton.place(relx=0, rely=1, anchor=SW)
        noButton = Button(root, text="No", command=no, font="verdana", bg="red", fg="white", width=9)
        noButton.place(relx=1.0, rely=1.0, anchor=SE)
        root.resizable(0, 0)
        root.config(bg=back)
        root.wm_title(title)
        root.wm_attributes("-topmost", 1)
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        root.geometry('%dx%d+%d+%d' % (w, h, x, y))
        missatge = Label (root, text="Enviar alerta?", font="verdana", bg=back, fg=fore)
        missatge.place(relx=0.5, rely=0.5, anchor=CENTER)
        root.iconbitmap('icono.ico')
        root.mainloop()
listener = keyboard.Listener(on_press=on_press)
serverPort = 5555
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
def sck():
    global serverSocket
    serverSocket.listen(1)
    try:
        while True:
            connectionSocket, addr = serverSocket.accept()
            if addr[0] == ip:
                connectionSocket, addr = serverSocket.accept()
                messagefromclient = connectionSocket.recv(1024)
                conn = sqlite3.connect("database.db")
                alg = conn.execute('SELECT key,iv,secret FROM cypher')
                cypher = alg.fetchone()
                key = bytes(cypher[0]+'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0', 'utf-8')
                iv = bytes(cypher[1],'utf-8')
                obj2 = AES.new(key, AES.MODE_CBC, iv)
                plaintext = obj2.decrypt(b64decode(messagefromclient))
                plaintext = unpad(plaintext, AES.block_size)
                message = str(plaintext,'utf-8')
                secret = cypher[2]+'\n'
                conn.close()
                if re.search(secret,message):
                    filtrat = message.replace(secret,"")
                    gui(filtrat,0)
    except OSError:
        sys.exit(1)
def fn():
    global listener
    listener.start()
    listener.join()
def main():
    t1 = threading.Thread(target=fn)
    t2 = threading.Thread(target=sck)
    t1.setDaemon(True)
    t2.setDaemon(True)
    t1.start()
    t2.start()
def sortir(systray):
    global listener
    global serverSocket
    listener.stop()
    serverSocket.close()
    systray.QUIT
systray = SysTrayIcon("icono.ico", "AlrtApp", on_quit=sortir)
systray.start() 
main()
