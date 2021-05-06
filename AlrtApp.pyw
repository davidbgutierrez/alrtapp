import win32ui
import winsound
import win32con
import requests
import bs4
import sqlite3
import getpass
from socket import *

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
