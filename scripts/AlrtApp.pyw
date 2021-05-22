from tkinter import *
import winsound, sqlite3, getpass, uuid, sys, requests, ctypes, pkg_resources.py2_warn
from subprocess import check_output
from subprocess import DEVNULL
from socket import *
from infi.systray import SysTrayIcon
def gui(mess,check):
    root = Tk()
    def lock():
        root.destroy()
        ctypes.windll.user32.LockWorkStation()
    if check == 1:
        w = 350
        h = 100
        back = "LIGHT cyan"
        fore = "RED"
        title = "ERROR"
        exitButton = Button(root, text="Sortir", command=root.destroy, font="verdana", bg="KHAKI", fg="BLACK", width=20)
        exitButton.pack(side=BOTTOM)
    else:
        w = 500
        h = 250
        back = "firebrick3"
        fore = "ghost white"
        title = "ALERTA D'AGRESSIÓ"
        goButton =  Button(root, text="Acudir",command=lock, font="verdana", bg="pale green", fg="black", width=19)
        goButton.place(relx=1.0, rely=1.0, anchor=SE)
        exitButton = Button(root, text="Sortir", command=root.destroy, font="verdana", bg="gold", fg="BLACK", width=19)
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
    lbl2 = Label (root, text=mess, font="verdana", bg=back, fg=fore)
    lbl2.place(relx=0.5, rely=0.5, anchor=CENTER)
    root.iconbitmap('icono.ico')
    root.mainloop()
def sortir(systray):
    systray.shutdown()
    sys.exit(1)
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
if (switch(sys.argv[2]) != False):
    port = switch(sys.argv[2])
else:
    gui("Segon paràmetre no valid.",1)
    sys.exit(1)
uid = str(uuid.uuid4())
username = str(getpass.getuser())
INSERT = {'username':username, 'uid':uid}
url = port+ip+"/alrtapp.php"
try:
    requests.get(url = url)
except requests.ConnectionError:
    gui("Error de connexió amb el servidor",1)
    sys.exit(1)
conn = sqlite3.connect("uid.db")
#Abans de crear la taula, verifica que no existeix i el crea. 
#També s'afegirà l'usuari actual a la base de dades local amb la uid corresponent
tb_create = ('''CREATE TABLE users(user,uid)''')
tb_exists = ("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
#Cada vegada que es realitza un insert, s'envia els paràmetres afegits a la base de dades del servidor
if not conn.execute(tb_exists).fetchone():
    conn.execute(tb_create)
    conn.commit()
    requests.get(url = url, params=INSERT)
conn.execute("INSERT INTO users(user,uid) VALUES (?,?)",(username,uid,))
#Es comprova que l'usuari estigui en la base de dades local
us_exists = conn.execute("SELECT user,uid FROM users WHERE user LIKE ?",('{}%'.format(username),))
us = us_exists.fetchone()
if str(us) == 'None' :
    requests.get(url = url, params=INSERT)
    conn.execute("INSERT INTO users(user,uid) VALUES (?,?)",(username,uid,))
    conn.commit()
#Si hi ha com paràmetre un 1, s'envia l'alerta al servidor, en cas contrari es quedarà escoltant al servidor.
if '1' in sys.argv :
    us_exists = conn.execute("SELECT user,uid FROM users WHERE user LIKE ?",('{}%'.format(username),))
    us = us_exists.fetchone()
    ALERTA = {'username':username, 'uid':us[1], 'hostname': hostname}
    requests.get(url = url, params=ALERTA)
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
            gui(message,0)
