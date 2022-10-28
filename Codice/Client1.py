from socket import *
import os, platform, subprocess, re
import time

def connessione():
    connesso = False
    tempo_attesa = 5
    
    while connesso == False :
        try:
            clientSocket.connect((serverName,serverPort))
        except Exception as e:
            # Server inattivo, si ritenta la connessione dopo un tempo sempre maggiore
            print("Attendo " + str(tempo_attesa))
            print(str(e.errno))
            print(str(e))
            time.sleep(tempo_attesa)
            tempo_attesa*=2
        else:
            connesso = True
            
def invia_messaggio(messaggio):
    global clientSocket
    while True:
        try:
            clientSocket.send(messaggio.encode())
            break
        except Exception as e:
            #Il server si è disconnesso nel mentre, tentiamo la riconnessione e rimandiamo il messaggio
            print (str(e.errno))
            print(str(e))
            clientSocket.close()
            clientSocket = socket(AF_INET, SOCK_STREAM)
            connessione()

def ricevi_messaggio():
    global clientSocket
    while True:
        try:
            messaggio = clientSocket.recv(1024).decode()
            return messaggio
        except Exception as e:
            #Il server si è disconnesso nel mentre, tentiamo la riconnessione e la ricezione del messaggio
            print (str(e.errno))
            print(str(e))
            clientSocket.close()
            clientSocket = socket(AF_INET, SOCK_STREAM)
            connessione()

def getInfoSO():
    sistema = platform.system()
    if (sistema == "Windows") :
        release, version, csd, ptype = platform.win32_ver()
        sentence = sistema + ", " + release + ", " + version + ", " + csd + ", " + ptype
        return sentence
    else:
        return ""

def getInfoCPU():
    if platform.system() == "Windows":
        infoCpuOsWindows = platform.processor()
        return infoCpuOsWindows
    elif platform.system() == "Darwin":
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
        comandoCpu = "sysctl -n machdep.cpu.brand_string"
        infoCpuOsDarwin = subprocess.check_output(comandoCpu).strip()
        return infoCpuOsDarwin
    elif platform.system() == "Linux":
        comandoCpu = "cat /proc/cpuinfo"
        infoCpuOsLinux = subprocess.check_output(comandoCpu, shell=True).decode().strip()
        return infoCpuOsLinux
    return ""

serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)
            
connessione()
while True:
    comando = ricevi_messaggio()
    print ("Ho ricevuto " + comando)
    match (comando):
        case "0":
            break
        case "1":
            invia_messaggio(getInfoSO())
        case "2":
            invia_messaggio(getInfoCPU())

print("Fine")
clientSocket.close()