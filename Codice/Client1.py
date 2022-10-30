from socket import *
from datetime import datetime
import os, platform, subprocess, re, time
import psutil #verificare funzionamento su linux e mac

serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)
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
            messaggio = clientSocket.recv(4096).decode()
            return messaggio
        except Exception as e:
            #Il server si è disconnesso nel mentre, tentiamo la riconnessione e la ricezione del messaggio
            print (str(e.errno))
            print(str(e))
            clientSocket.close()
            clientSocket = socket(AF_INET, SOCK_STREAM)
            connessione()

def getInfoSO():
    intestazione = "\n === INFORMAZIONI SUL SISTEMA === \n"
    infoSistemaOperativo = platform.uname()
    sistemaOperativo = infoSistemaOperativo.system
    nomeUtente = infoSistemaOperativo.node
    releaseSo = infoSistemaOperativo.release
    versioneSo = infoSistemaOperativo.version
    architettura = infoSistemaOperativo.machine
    sentence = "Nome utente: "+nomeUtente+"\n"+\
               "Sistema operativo: "+sistemaOperativo+"\n"+\
               "Release SO: "+releaseSo+"\n"+\
               "Versione SO: "+versioneSo+"\n"+\
               "Architettura: "+architettura+"\n"
    return intestazione+sentence

def getInfoCPU():
    intestazione = "\n === INFORMAZIONI SULLA CPU === \n"
    if platform.system() == "Windows":
        infoCpuOsWindows = platform.processor()
        return intestazione+infoCpuOsWindows
    elif platform.system() == "Darwin":
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
        comandoCpu = "sysctl -n machdep.cpu.brand_string"
        infoCpuOsDarwin = subprocess.check_output(comandoCpu).strip()
        return intestazione+infoCpuOsDarwin
    elif platform.system() == "Linux":
        comandoCpu = "cat /proc/cpuinfo"
        infoCpuOsLinux = subprocess.check_output(comandoCpu, shell=True).decode().strip()
        return intestazione+infoCpuOsLinux
    return ""

def getInfoBootTime():
    intestazione = "\n === INFORMAZIONI SUL TEMPO D'AVVIO === \n"
    boot_time_timestamp = psutil.boot_time()
    boot_time = datetime.fromtimestamp(boot_time_timestamp)
    giorno = boot_time.day
    mese = boot_time.month
    anno = boot_time.year
    ore = boot_time.hour
    minuti = boot_time.minute
    secondi = boot_time.second
    sentence = f"Il sistema è attivo dal giorno {giorno}/{mese}/{anno} dalle ore {ore}:{minuti}:{secondi} "
    return intestazione+sentence


"""
Converte i byte nel proprio formato corrispondente
Esempio:
1253656 = '1.20MB'
1253656678 = '1.17GB'

def converti_byte(byte):
    
    suffisso_byte = "B"
    fattore_byte = 1024

    for unita_byte in ["", "K", "M", "G", "T", "P"]:
        if byte < fattore_byte:
            byte_convertito = f"{byte:.2f}{unita_byte}{suffisso_byte}" #f-string
            return byte_convertito
        byte = byte/fattore_byte
"""

connessione()
while True:
    comando = ricevi_messaggio()
    print ("Ho ricevuto " + comando)

    if comando == "1":
        invia_messaggio(getInfoSO())
    elif comando == "2":
        invia_messaggio(getInfoCPU())
    elif comando == "3":
        invia_messaggio(getInfoBootTime())
    elif comando == "0":
        break
    else:
        print("errore comando")

    """
    comando match non supportato per versioni di python < 3.10
    match(comando):
        case "0":
            break
        case "1":
            invia_messaggio(getInfoSO())
        case "2":
            invia_messaggio(getInfoCPU())
        case "3":
            invia_messaggio(getInfoBootTime())
    """

print("Fine")
clientSocket.close()