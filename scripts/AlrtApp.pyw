from tkinter import *
import winsound, sqlite3, getpass, uuid, sys, requests, pkg_resources.py2_warn
from subprocess import check_output
from subprocess import DEVNULL
from socket import *
from infi.systray import SysTrayIcon
def gui(mess):
    if mess == "Error de connexió amb el servidor" or mess == "Falta introduïr paràmetres":
        w = 280
        h = 100
        back = "white"
        fore = "black"
        title = "ERROR"
    else:
        w = 500
        h = 250
        back = "firebrick3"
        fore = "ghost white"
        title = "ALERTA D'AGRESSIÓ"
    root = Tk()
    exitButton = Button(root, text="D'acord", command=root.destroy, font="verdana", bg="gold", fg="BLACK")
    exitButton.pack(side=BOTTOM)
    root.resizable(0, 0)
    root.config(bg=back)
    root.wm_title(title)
    root.wm_attributes("-topmost", 1)
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    lbl2 = Label (root, text=mess, font="verdana", bg=back, fg=fore)
    lbl2.place(relx=0.5, rely=0.5, anchor=CENTER)
    root.iconbitmap('icono.ico')
    root.mainloop()
def sortir(systray):
    systray.shutdown()
    sys.exit(1)
hostname = check_output("hostname", stdin=DEVNULL, stderr=DEVNULL, shell=True).decode('utf-8').rstrip()
if len(sys.argv) <= 2:
    gui("Falta introduïr paràmetres")
    sys.exit(1)
else:
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
try:
    requests.get(url = url)
except requests.ConnectionError:
    gui("Error de connexió amb el servidor")
    sys.exit(1)
#Abans de crear la taula, verifica que no existeix i el crea. 
#També s'afegirà l'usuari actual a la base de dades local amb la uid corresponent
tb_create = ('''CREATE TABLE users(user,uid)''')
tb_exists = ("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
#Cada vegada que es realitza un insert, s'envia els paràmetres afegits a la base de dades del servidor
if not conn.execute(tb_exists).fetchone():
    conn.execute(tb_create)
    conn.commit()
    try:
        requests.get(url = url, params=INSERT)
    except requests.ConnectionError:
        gui("Error de connexió amb el servidor")
        sys.exit(1)
    conn.execute("INSERT INTO users(user,uid) VALUES (?,?)",(username,uid,))
#Es comprova que l'usuari estigui en la base de dades local
us_exists = conn.execute("SELECT user,uid FROM users WHERE user LIKE ?",('{}%'.format(username),))
us = us_exists.fetchone()
if str(us) == 'None' :
    try:
        requests.get(url = url, params=INSERT)
    except requests.ConnectionError:
        gui("Error de connexió amb el servidor")
        sys.exit(1)
    conn.execute("INSERT INTO users(user,uid) VALUES (?,?)",(username,uid,))
    conn.commit()
#Si hi ha com paràmetre un 1, s'envia l'alerta al servidor, en cas contrari es quedarà escoltant al servidor.
if '1' in sys.argv :
    us_exists = conn.execute("SELECT user,uid FROM users WHERE user LIKE ?",('{}%'.format(username),))
    us = us_exists.fetchone()
    ALERTA = {'username':username, 'uid':us[1], 'hostname': hostname}
    try:
        requests.get(url = url, params=ALERTA)
    except requests.ConnectionError:
        gui("Error de connexió amb el servidor")
        sys.exit(1)
    conn.close()
else:
    conn.commit()
    conn.close()
    systray = SysTrayIcon("icono.ico", "AlrtApp", on_quit=sortir)
    systray.start()
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
            gui(message)
