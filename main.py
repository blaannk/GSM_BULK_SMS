# pyserial, colorama
import serial, time, glob, sys, os, colorama, ctypes
from colorama import init, Fore
init()

numlist = []
message = ""

def list_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
    result = []
    for port in ports:
        try:
            s = serial.Serial(str(port))
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def setupgsm(port):
    try:
        port.write(b'AT\r')
        time.sleep(1)
        output = port.read(256)
        port.write(b'AT+CMGF=1\r')
        time.sleep(0.100)
        output = port.read(256)
        port.write(b'AT+CSCS="GSM"\r')
        time.sleep(0.100)
        output = port.read(256)
        return True
    except:
        return False

def sendsms(port, number, message):
    port.write(b'AT+CMGS="+' + number.encode("utf-8") + b'"\r')
    time.sleep(0.100)
    output = port.read(256)
    if "ERROR" in output.decode("utf-8"):
        return False
    port.write(message.encode("utf-8") + chr(26).encode("utf-8"))
    output = port.read(4096)
    if "ERROR" in output.decode("utf-8"):
        return False
    output = b''
    while output.decode("utf-8")  == "":
        output = port.read(256)
        time.sleep(0.500)
    if "ERROR" in output.decode("utf-8"):
        return False
    elif "OK" in output.decode("utf-8"):
        return True
    else:
        return False
        
ctypes.windll.kernel32.SetConsoleTitleW("GSM SMS SENDER")
print("[*] GSM PRIVATE SENDER\n")
print("[*] PORTS :")
all_ports = list_ports()
for i in range(len(all_ports)):
    print("[" + str(i) + "] " + str(all_ports[i]))
while True:
    try:
        com_port = int(input("\n[+] > "))
        if com_port <= (len(all_ports) - 1) and com_port >= 0:
            break
        else:
            print("\n[!] Erreur : veuillez faire un choix valide")
    except:
        print("\n[!] Erreur : veuillez faire un choix valide")
try:
    port = serial.Serial(port=str(all_ports[com_port]), baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1, xonxoff=0, rtscts=0)
except:
    print("\n[!] Erreur : impossible de se connecter au port")
    os._exit(0)

if setupgsm(port):
    print("\n[+] GSM configuré\n")
else:
    print("[!] Erreur : impossible de configurer le GSM")
    os._exit(0)

all_files = [fn for fn in glob.glob('*.txt') if not os.path.basename(fn).startswith('message')]
print("[*] NUMLIST : ")
for i in range(len(all_files)):
    print("[" + str(i) + "] " + str(all_files[i]))
while True:
    try:
        file_index = int(input("\n[+] > "))
        if file_index <= (len(all_files) - 1) and file_index >= 0:
            break
        else:
            print("\n[!] Erreur : veuillez faire un choix valide")
    except:
        print("\n[!] Erreur : veuillez faire un choix valide")
with open(all_files[file_index], "r") as file:
    lines = file.readlines()
    for line in lines:
        line = line.strip()
        numlist.append(line)
print("\n[+] Numlist chargée : " + str(len(numlist)) + " numéros")
with open("message.txt", "r") as msgfile:
    message = msgfile.read()
print("[+] Message : " + str(message) + "\n")
start = input("[*] Appuyez sur ENTRER pour lancer le spam")
print("[+] Started")

total_spam = 0
errors = 0
for num in numlist:
    send = sendsms(port, num, message)
    if send:
        total_spam +=1
        errors = 0
        ctypes.windll.kernel32.SetConsoleTitleW("GSM SMS SENDER - SMS SENT : " + str(total_spam))
        print("[" + Fore.GREEN + num + Fore.RESET + "] Message envoyé")
    else:
        errors +=1
        print("[" + Fore.RED + num + Fore.RESET + "] Erreur dans l'envoi")
    if errors == 5:
        os._exit(0)
