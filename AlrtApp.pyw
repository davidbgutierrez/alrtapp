import win32ui
import winsound
import win32con
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
        winsound.MessageBeep(winsound.MB_OK)
        win32ui.MessageBox(message,"ALERTA",0x1000)
