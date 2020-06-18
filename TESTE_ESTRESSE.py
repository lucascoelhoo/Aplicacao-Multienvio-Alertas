import subprocess
import os
from threading import Thread
import pickle

def Teste():
    comando="C:/send.bat"
    subprocess.run(comando)

flag="-"
pickle.dump( flag, open( "save.p", "wb" ) )
   
thread1=Thread(target = Teste)
thread2=Thread(target = Teste)
thread3=Thread(target = Teste)
thread4=Thread(target = Teste)
thread5=Thread(target = Teste)
thread6=Thread(target = Teste)
thread7=Thread(target = Teste)
thread8=Thread(target = Teste)
thread9=Thread(target = Teste)
thread10=Thread(target = Teste)

thread1.start()
thread2.start()
thread3.start()
thread4.start()
thread5.start()
thread6.start()
thread7.start()
thread8.start()
thread9.start()
thread10.start()
