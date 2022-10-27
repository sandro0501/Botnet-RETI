#socket tcp - server
from socket import *

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverName = gethostbyname(gethostname())
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print('Il BotMaster con indirizzo IP:',serverName, 'è pronto a ricevere le informazioni dalla Botnet client...')
while True:
    connectionSocket, addr = serverSocket.accept()
    print('\nNuova Botnet client connessa al BotMaster', addr)
    infoCPU = connectionSocket.recv(4096).decode()
    print('\nEcco alcune informazioni relative alla CPU dell\' host su cui è attiva la Botnet connessa...\n', infoCPU)
    connectionSocket.close()


