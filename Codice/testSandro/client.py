# socket tcp - client
from socket import *
import os, platform, subprocess, re


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
clientSocket.connect((serverName, serverPort))
infoCPU = getInfoCPU()
clientSocket.send(infoCPU.encode())
print('Informazioni sulla CPU inviate al BotMaster correttamente')
clientSocket.close()
