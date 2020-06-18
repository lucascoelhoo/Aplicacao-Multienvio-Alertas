################### SCRIPT DO SERVIDOR DE ENVIO DE SMS ####################################################
# Sintaxe de execucao via cmd: python Server_COMPort.py
# Resumo do funcionamento:
#   1º-Para enviar mensagens de SMS usando um modem SMS, é necessario pluga-lo no computador e inicializa-lo adequadamente.
#      Para isso, em geral, o mais recomendado é apenas abrir o software do fabricante logo depois de plugar o modem, esperar
#      sua inicializacao, e depois fechar e terminar o programa do fabricante. Em geral, apos esse procedimento, o modem estara
#      apto para receber comunicacoes via porta serial. A porta ser usada devera ser verificada via gerenciador de dispositivos
#      no OS Windows, na aba de COM PORTS. Se o modem tem suporte e foi corretamente instalado, alguma delas tera AT escrito em seu
#      nome, o que significa suporte aos comandos AT, usados nesse programa
#   2º-Esse script resolve o problema de acessos multiplos a portas seriais (no caso de muitos alarmes simultaneos), criando um servidor
#      tcp local e escutando na porta 12345. Assim, para enviar um SMS, basta conectar, via telnet, no endereço 127.0.0.1, ou "localhost"
#      na porta 12345, enviar a string, e o programa automaticamente envia o SMS para a lista de numeros contida no arquivo "Celulares.txt"
#   3º-As mensagens comecam padronizadas por "Data Center\n" (o \n é uma quebra de linha)
import socket
import serial
import time
import sys
from threading import Thread

Cel_Numbers_Stack=[]
Messages_SMS_Stack=[]
mark=0
COM_Port="COM20"
Baud = 9600
Timeout = 5
Cel_Numbers = []
TCP_IP = '127.0.0.1'
TCP_PORT = 12345
BUFFER_SIZE = 200  # Normally 1024, but we want fast response
Message_SMS = ""
########################## INICIO DA DECLARACAO DE FUNCOES  #########################################################################################################################
def SMS():
    global Cel_Numbers_Stack
    global Messages_SMS_Stack
    global mark
    timeout = time.time() + 3 #medido em seg
    while(1):
        time.sleep(0.2)
        if(mark):
            timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
            log="DATA/HORA:"
            log+=timestr
            log+="---->"
            log+="Fila surgiu!   Mensagem responsavel:"
            log+=Messages_SMS_Stack[0]
            log+="\n"
            file = open("logSMS-Server.txt","a")
            file.write(log)
            file.close()
            
            try:
                phone = serial.Serial(COM_Port, Baud, timeout=Timeout)
                timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
                log="DATA/HORA:"
                log+=timestr
                log+="---->"
                log+="Porta serial aberta com sucesso!"
                log+="\n"
                file = open("logSMS-Server.txt","a")
                file.write(log)
                file.close()
                while(mark):
                    print("SMS Server: Ainda tem numeros na pilha!")
                    try:
                        time.sleep(0.5)
                        phone.write(b'AT\r')
                        time.sleep(0.5)
                        phone.write(b'AT+CMGF=1\r')
                        time.sleep(0.5)
                        phone.write(b'AT+CMGS=\"' + Cel_Numbers_Stack[0].encode() + b'\"\r')
                        time.sleep(0.5)
                        phone.write(Messages_SMS_Stack[0].encode() + b"\r")
                        time.sleep(0.5)
                        phone.write(bytes([26]))
                        time.sleep(2)
                        print("\nSMS Server: SMS enviado para: "+ Cel_Numbers_Stack[0])
                        timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
                        log="DATA/HORA:"
                        log+=timestr
                        log+="---->"
                        log+="Envio de novo SMS: "
                        log+=Messages_SMS_Stack[0]
                        log+="    Para:"
                        log+=Cel_Numbers_Stack[0]
                        log+="\n"
                        file = open("logSMS-Server.txt","a")
                        file.write(log)
                        file.close()
                        del Cel_Numbers_Stack[0]
                        del Messages_SMS_Stack[0]
                        mark-=1
                    except:
                        if(time.time()>timeout):
                            #EMAIL SOBRE FALHA DO MODEM GSM
                            try:
                                file=open("Emails.txt")
                                AddressesTo = file.read().splitlines()
                                file.close()
                                Message_Email_subject="Data Center: MODEM GSM"
                                Message_Email_body="Problemas no modem GSM ou falta do arquivo logSMS-Server.txt. No caso do modem GSM, por favor, reiniciar:\nPlugue o modem gsm usb DWM-221, abra a aplicacao da Dlink para inicializar o modem, depois, feche a aplicacao completamente. Talvez seja necessario clicar com o botao direito sobre o icone da dlink ao lado do relogio e escolher sair. Não existe impedimento sobre ter conectado usando o software, porém, é necessário fechá-lo para liberar a porta Serial. Isso não irá fechar a conexão de internet, caso tenha sido ativada."
                                SMTP_server="smtp.xxx.yyy.br"
                                Port="587"
                                Username="aaaa.ssss"
                                Password="xxxxxxx"
                                AddressFrom="alarme.datacenter@xxx.yyy.br"
                                Email(SMTP_server, Port, Username, Password, AddressFrom, AddressesTo, Message_Email_subject, Message_Email_body)
                                timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
                                log="DATA/HORA:"
                                log+=timestr
                                log+="---->"
                                log+="Envio de email para REINICIALIZACAO DO MODEM GSM"
                                log+="\n"
                                file = open("logSMS-Server.txt","a")
                                file.write(log)
                                file.close()
                                mark=0
                            except:{}
                            print("\nSMS Server: Timeout de 1 hora de tentativas de envio de SMS, fim.")
                            timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
                            log="DATA/HORA:"
                            log+=timestr
                            log+="---->"
                            log+="Timeout de 1 hora de tentativas de envio de SMS, todos com excecoes, fim da thread."
                            log+="\n"
                            file = open("logSMS-Server.txt","a")
                            file.write(log)
                            file.close()
                            mark=0
                        else:
                            continue
                phone.close()
                timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
                log="DATA/HORA:"
                log+=timestr
                log+="---->"
                log+="Porta serial fechada com sucesso!"
                log+="\n"
                file = open("logSMS-Server.txt","a")
                file.write(log)
                file.close()
            except:
                if(time.time()>timeout):
                    #EMAIL SOBRE FALHA DO MODEM GSM
                    try:
                        file=open("Emails.txt")
                        AddressesTo = file.read().splitlines()
                        file.close()
                        Message_Email_subject="Data Center: MODEM GSM"
                        Message_Email_body="Problemas no modem GSM ou falta do arquivo logSMS-Server.txt. No caso do modem GSM, por favor, reiniciar:\nPlugue o modem gsm usb DWM-221, abra a aplicacao da Dlink para inicializar o modem, depois, feche a aplicacao completamente. Talvez seja necessario clicar com o botao direito sobre o icone da dlink ao lado do relogio e escolher sair. Não existe impedimento sobre ter conectado usando o software, porém, é necessário fechá-lo para liberar a porta Serial. Isso não irá fechar a conexão de internet, caso tenha sido ativada."
                        SMTP_server="smtp.xxxx.yyyy.br"
                        Port="587"
                        Username="alarme.datacenter"
                        Password="xxxxx"
                        AddressFrom="alarme.datacenter@xxx.yyyy.br"
                        Email(SMTP_server, Port, Username, Password, AddressFrom, AddressesTo, Message_Email_subject, Message_Email_body)
                        timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
                        log="DATA/HORA:"
                        log+=timestr
                        log+="---->"
                        log+="Envio de email para REINICIALIZACAO DO MODEM GSM"
                        log+="\n"
                        file = open("logSMS-Server.txt","a")
                        file.write(log)
                        file.close()
                        mark=0
                    except:
                        print("\nSMS Server: Timeout de 1 hora de tentativas de envio de SMS, fim.")
                        timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
                        log="DATA/HORA:"
                        log+=timestr
                        log+="---->"
                        log+="Timeout de 1 hora de tentativas de envio de SMS, todos com excecoes, fim da thread."
                        log+="\n"
                        file = open("logSMS-Server.txt","a")
                        file.write(log)
                        file.close()
                        mark=0
                else:
                    continue
                
            continue
        else:{}



#Funcao que realiza o envio dos alertas para os emails listados no arquivo Emails.txt
def Email(SMTP_server, Port, Username, Password, AddressFrom, AddressesTo, Message_subject, Message_body):
    Address_completo=""
    for number,AddressTo in enumerate(AddressesTo):
        Address_completo+=(AddressTo+"; ")
    timeout = time.time() + 10 #medido em seg
    while(time.time() < timeout):
        try:
            time.sleep(random.uniform(1, 5))
            comando=""
            comando+="sendemail.exe -f "
            comando+=AddressFrom
            comando+=" -t "
            comando+=Address_completo
            comando+=" -s "
            comando+=SMTP_server
            comando+=":"
            comando+=Port
            comando+=" -xu "
            comando+=Username
            comando+=" -xp "
            comando+=Password
            comando+=" -o tls=auto -u \""
            comando+=Message_subject
            comando+="\" -m \""
            comando+=Message_body
            comando+="\""
            subprocess.run(comando, shell=True)
            print("\nEmail: Email enviado!")
            timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
            log="DATA/HORA:"
            log+=timestr
            log+="---->"
            log+="Email enviado:   Subject:"
            log+=Message_subject
            log+=" /   Body:"
            log+=Message_body
            log+="\n"
            file = open("logSMS-Server.txt","a")
            file.write(log)
            file.close() 
            break
        except:
            print("\nEmail: Erro, repetindo...")
            continue
    timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
    log="DATA/HORA:"
    log+=timestr
    log+="---->"
    log+="FALHA> email nao enviado:   Subject:"
    log+=Message_subject
    log+="   Body:"
    log+=Message_body
    log+="\n"
    file = open("logSMS-Server.txt","a")
    file.write(log)
    file.close()
    return
########################## FIM DA DECLARACAO DE FUNCOES  #########################################################################################################################


########################## INICIO DO PROGRAMA PRINCIPAL  ########################################################################################################################
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)
    #phone = serial.Serial(COM_Port, Baud, timeout=Timeout)
    th=Thread(target=SMS , args = [] )
    while(1):
        conn, addr = s.accept()
        print ('\nSMS Server:   Connection address:', addr)
        timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
        log="DATA/HORA:"
        log+=timestr
        log+="---->"
        log+="Nova conexao recebida, endereco: "
        log+=str(addr)
        log+="\n"
        file = open("logSMS-Server.txt","a")
        file.write(log)
        file.close()
        data = conn.recv(BUFFER_SIZE)
        if(data and str(data).find("b\'\'") == -1):
            print ("\nSMS Server:   Received data:", data)
            conn.send(data)  # echo
            timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
            log="DATA/HORA:"
            log+=timestr
            log+="---->"
            log+="Nova mensagem ainda nao processada recebida: "
            log+=str(data)
            log+="\n"
            file = open("logSMS-Server.txt","a")
            file.write(log)
            file.close()
            message=str(data)
            message=str(message[2:-1])
            #print(message)
            Message_SMS = message
            file=open("Celulares.txt")
            Cel_Numbers = file.read().splitlines()
            file.close()
            if (not th.isAlive()):
                for colocacao,Celphone in enumerate(Cel_Numbers):
                    mark+=1
                    Cel_Numbers_Stack.append(Celphone)
                    Messages_SMS_Stack.append(Message_SMS)
                th.daemon=True
                th.start()
                timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
                log="DATA/HORA:"
                log+=timestr
                log+="---->"
                log+="Nova thread iniciada! Mensagem que deu inicio: "
                log+=Message_SMS
                log+="\n"
                file = open("logSMS-Server.txt","a")
                file.write(log)
                file.close()
            else:
                for colocacao,Celphone in enumerate(Cel_Numbers):
                    mark+=1
                    Cel_Numbers_Stack.append(Celphone)
                    Messages_SMS_Stack.append(Message_SMS)
                timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
                log="DATA/HORA:"
                log+=timestr
                log+="---->"
                log+="Thread ja estava ativa! Mensagem adicionada à pilha de envio: "
                log+=Message_SMS
                log+="\n"
                file = open("logSMS-Server.txt","a")
                file.write(log)
                file.close()
                
except:
    print("Excecao, fim do SMS Server.")
    timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
    log="DATA/HORA:"
    log+=timestr
    log+="---->"
    log+="FALHA> Excecao detectada, fim do SMS Server."
    log+="\n"
    file = open("logSMS-Server.txt","a")
    file.write(log)
    file.close()
    sys.exit()
########################## FIM DO PROGRAMA PRINCIPAL  #########################################################################################################################


