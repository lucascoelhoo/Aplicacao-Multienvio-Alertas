################### SCRIPT DE AUTOMACAO DE ENVIO DE MENSAGENS VIA EMAIL, TELEGRAM E SMS ####################################################
# Exemplo de sintaxe para execucao COMPLETA DA AUTOMACAO:
#   >python Messages_Universal.py "TEXTO CAMPO BODY EMAIL" "TEXTO TELEGRAM" "TEXTO SMS"
# 
# A ideia é colocar essa linha numa arquivo .bat e alterar os textos conforme o alerta referente a cada arquivo .bat criado
#
# IMPORTANTE VERIFICAR QUE TODOS OS ARQUIVOS ABAIXO ESTAO NA MESMA PASTA
#   1º-Messages_Universal.py
#   2º-Server_COMPort.py
#   3º-Emails.txt
#   4º-Celulares.txt
#   5º-SendEmail.exe
#   6º-Send.bat (apenas exemplo, nao é essencial para a aplicacao)
#
import sys
import time

#Email documentation:
# Servidor e porta: smtp.xxx.yyy.br:587
# Username: ddd.sss
# Pass: xxxxxx
# Aplicação sendo usada: sendemail.exe
# Campo assunto dos emails é padronizado em: "Data Center"
# Campo body dos emails comeca padronizado em: "Alarme: "
# Resumo do funcionamento:
#   1º-É necessario ter baixado e instalado a aplicacao "sendEmail.exe" (http://caspian.dotconf.net/menu/Software/SendEmail/)
#   2º-O script monta os comandos de envio de emails e processa esses comandos, um por vez, com as configuracoes de servidor,
#      porta, usuario, senha, destino, etc, conforme documentado acima, e envia um só email para todos da lista
import subprocess
import os

#SMS documentation:
# AT Com port used: COM20
# Model of GSM USB Modem used: Dlink DWM-221 (foi necessário atualizar o firmware desse, download disponível no site da Dlink)
# Baud: 9600 bps
# Timeout: 5 sec
# Comeco das mensagens padronizado em: "Data Center\n"
# Resumo do funcionamento:
#   1º(Manual)-Plugue o modem gsm usb DWM-221, abra a aplicacao da Dlink para inicializar o modem, depois, sem conectar, feche a aplicacao completamente
#      Talvez seja necessario clicar com o botao direito sobre o icone da dlink ao lado do relogio e escolher sair
#   2º(Automatico)-É necessario que o script "Server_COMPort.py" tenha sido inicializado para que seja possivel enviar SMS
#      usando o modem gsm e os comandos AT. Os scripts, de forma autonoma, verificam se esse ja foi iniializado, e em caso
#      negativo, eles mesmos incializam e cuidam da conexao para conseguir realizar o envio dos SMS.
#      ENTRETANTO, O SMS NÃO É UM MEIO GARANTIDO DE CHEGADA DE MENSAGENS.
import serial
import socket
import random
from random import randint
NUMBER_TRIES = 10

#Telegram documentation:
# Dados do bot: {'first_name': 'DataCenter', 'username': 'DataCenter_bot' , 'id': 9999999}
# Dados do grupo no Telegram: 'nome': DataCenter , 'chatID': -888888
# Comeco das mensagens padronizado em: "Data Center\n"
# Resumo do funcionamento:
#   1º-O Telegram disponibiliza uma API propria para a geracao e uso de bots, que sao como aplicacoes robos
#      capazes de se comunicar usando o aplicativo. No caso desse script, usa-se o pacote "telepot" para tais
#      finalidades de envio de mensagens.
import telepot


########################## INICIO DA DECLARACAO DE FUNCOES  #########################################################################################################################

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
            file = open("logEmail.txt","a")
            file.write(log)
            file.close() 
            return
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
    file = open("logEmail.txt","a")
    file.write(log)
    file.close()
    return

#Funcao que realiza o envio dos alertas para os numeros listados no arquivo Celulares.txt
# IMPORTANTE: Na verdade, é o script "Server_COMPort.py" que le o arquivo "Celulares.txt"
#De preferencia, coloque os numeros com o codigo de area (61, no caso do DF)
def SMS(Message_SMS, flag_repetitions):
    TCP_IP = '127.0.0.1'
    TCP_PORT = 12345
    BUFFER_SIZE = 200
    #flag_SMS_Server_criado_aqui=0
    try:
        if(flag_repetitions>=2):
            timeout = time.time() + 20 #medido em seg
            while(time.time() < timeout):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((TCP_IP, TCP_PORT))
                    s.send(Message_SMS.encode())
                    data = s.recv(BUFFER_SIZE)
                    s.close()
                    print("\nSMS: Mensagem_SMS enviada ao SMS Server depois de repetir!")
                    timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
                    log="DATA/HORA:"
                    log+=timestr
                    log+="---->"
                    log+="Sms enviado ao sms server:   Mensagem:"
                    log+=Message_SMS
                    log+="\n"
                    file = open("logSMS.txt","a")
                    file.write(log)
                    file.close()
                    return
                except:
                    continue
            timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
            log="DATA/HORA:"
            log+=timestr
            log+="---->"
            log+="FALHA> Sms nao enviado ao sms server:   Mensagem:"
            log+=Message_SMS
            log+="\n"
            file = open("logSMS.txt","a")
            file.write(log)
            file.close()
            return
        else:
            time.sleep(random.uniform(1, 5))
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TCP_IP, TCP_PORT))
            s.send(Message_SMS.encode())
            data = s.recv(BUFFER_SIZE)
            s.close()
            print("\nSMS: Mensagem_SMS enviada ao SMS Server de primeira!")
            timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
            log="DATA/HORA:"
            log+=timestr
            log+="---->"
            log+="Sms enviado ao Sms server:   Mensagem:"
            log+=Message_SMS
            log+="\n"
            file = open("logSMS.txt","a")
            file.write(log)
            file.close()
            return
    except:
        try:
            comando="python Server_COMPort.py"
            subprocess.Popen(comando, shell=True)
            print("\nSMS: Tentativa de criacao do SMS Server aqui!")
            timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
            log="DATA/HORA:"
            log+=timestr
            log+="---->"
            log+="ATENCAO> Tentativa de criacao do Sms server"
            log+="\n"
            file = open("logSMS.txt","a")
            file.write(log)
            file.close()
            time.sleep(5)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TCP_IP, TCP_PORT))
            s.send(Message_SMS.encode())
            data = s.recv(BUFFER_SIZE)
            s.close()
            print("\nSMS: Mensagem_SMS enviada ao SMS Server e SMS Server criado.")
            timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
            log="DATA/HORA:"
            log+=timestr
            log+="---->"
            log+="Sms enviado ao Sms server e Sms Server criado aqui:   Mensagem:"
            log+=Message_SMS
            log+="\n"
            file = open("logSMS.txt","a")
            file.write(log)
            file.close()
            #flag_SMS_Server_criado_aqui=1
            #while(flag_SMS_Server_criado_aqui):{}
            return
        except:
            time.sleep(random.uniform(1, 9))
            if(flag_repetitions<NUMBER_TRIES):
                flag_repetitions+=1
                print("\nSMS: Repetindo!")
                SMS(COM_Port, Baud, Timeout, Message_SMS, Cel_Numbers, flag_repetitions)
            else:
                print("\nSMS: Nenhuma tentativa deu certo, fim.")
                timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
                log="DATA/HORA:"
                log+=timestr
                log+="---->"
                log+="FALHA> Sms nao enviado:   Mensagem:"
                log+=Message_SMS
                log+="\n"
                file = open("logSMS.txt","a")
                file.write(log)
                file.close()
                return

#Funcao que realiza o envio das mensagens para o grupo do telegram, cujos dados estao documentados no inicio desse script
def Telegram(token_Bot, chatID, Message):
    timeout = time.time() + 10 #medido em seg
    while(time.time() < timeout):
        try:
            bot = telepot.Bot(token_Bot)
            bot.getMe()
            bot.sendMessage(chatID, Message)
            print("\nTelegram: Mensagem enviada!")
            timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
            log="DATA/HORA:"
            log+=timestr
            log+="---->"
            log+="Telegram enviado:   Mensagem:"
            log+=Message
            log+="\n"
            file = open("logTelegram.txt","a")
            file.write(log)
            file.close()
            return
        except:
            print("\nTelegram: Erro, repetindo...")
            continue
    timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
    log="DATA/HORA:"
    log+=timestr
    log+="---->"
    log+="FALHA> telegram nao enviado:   Mensagem:"
    log+=Message
    log+="\n"
    file = open("logTelegram.txt","a")
    file.write(log)
    file.close()
    return
########################## FIM DA DECLARACAO DE FUNCOES  #########################################################################################################################



########################## INICIO DO PROGRAMA PRINCIPAL  ########################################################################################################################
    
try:
    #EMAIL 
    try:
        file=open("Emails.txt")
        AddressesTo = file.read().splitlines()
        file.close()
        #AddressesTo=["fulano@gmail.com", "ciclano@hotmail.com"]
        Message_Email_subject="Data Center"
        #Message_Email_subject=str(sys.argv[1])
        Message_Email_body="Alarme: "
        Message_Email_body+=str(sys.argv[1])

        SMTP_server="smtp.xxx.yyy.br"
        Port="587"
        Username="ssss.aaaa"
        Password="xxxxxx"
        AddressFrom="alarme.datacenter@xxx.yyyy.br"
        Email(SMTP_server, Port, Username, Password, AddressFrom, AddressesTo, Message_Email_subject, Message_Email_body)
    except:
        timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
        log="DATA/HORA:"
        log+=timestr
        log+="---->"
        log+="FALHA> Execucao Email, provavelmente problema no arquivo Emails.txt"
        log+="\n"
        file = open("logMessages-Universal.txt","a")
        file.write(log)
        file.close()

    #TELEGRAM
    try:
        Message_Telegram = "Data Center\n"
        Message_Telegram += str(sys.argv[2])

        chatID=-270287439
        token_PRF_DataCenter_bot='9999999999:MMMMMMMMMMMMMMMMMM'
        Telegram( token_PRF_DataCenter_bot , chatID , Message_Telegram )
    except:
        timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
        log="DATA/HORA:"
        log+=timestr
        log+="---->"
        log+="FALHA> Execucao Telegram"
        log+="\n"
        file = open("logMessages-Universal.txt","a")
        file.write(log)
        file.close()

    #SMS
    try:
        Message_SMS = "Alarme - Data Center: "
        Message_SMS += str(sys.argv[3])
        COM_Port="COM22"
        Baud = 9600
        Timeout = 5
        SMS(Message_SMS, flag_repetitions=0)
    except:
        timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
        log="DATA/HORA:"
        log+=timestr
        log+="---->"
        log+="FALHA> Execucao SMS"
        log+="\n"
        file = open("logMessages-Universal.txt","a")
        file.write(log)
        file.close()
except:
    timestr = time.strftime("%d/%m/%Y-%H:%M:%S")
    log="DATA/HORA:"
    log+=timestr
    log+="---->"
    log+="FALHA> Execucao GERAL"
    log+="\n"
    file = open("logMessages-Universal.txt","a")
    file.write(log)
    file.close()
    sys.exit()
sys.exit()
########################## FIM DO PROGRAMA PRINCIPAL  #########################################################################################################################

