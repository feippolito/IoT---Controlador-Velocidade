#Integrantes
#Felipe Brandao Ippolito    RA: 12.01378-0
#Fabio Akira                RA: 15.03499-2
#Ronaldo Macarrao           RA: 15.01715-0

from Meter import *             #Mostrador analogico
from Button import *            #Botoes
import time
from threading import Thread    #Biblioteca para cria segunda thread
import RPi.GPIO as GPIO         #Gpio raspberry pi

GPIO.setwarnings(False)         #Tira os avisos 
GPIO.setmode(GPIO.BCM)          #Mode BCM

GPIO_TRIGGER = 25               #Trigger sensor ultrasonico
GPIO_ECHO = 24                  #Echo sensor ultrassonico
GPIO_PWM = 18                   #PWM1 ponte h -sentido anti-horario
GPIO_SENSOR1 = 23               #Encoder motor
GPIO_PWMH = 12                  #PWM2 ponte h -sentido anti


                                # Define saida/entrada (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_PWM,GPIO.OUT)
GPIO.setup(GPIO_SENSOR1, GPIO.IN)
GPIO.setup(GPIO_PWMH, GPIO.OUT)

def sentido(self):              #Função altera a interface grafica dependendo do sentido
    if self.sentido == 0:       #verifica o sentido
        self.button6.configure(bg="#4ed885")            #Altera cor dos botoes
        self.button5.configure(bg=self.orig_color)
    else:
        self.button5.configure(bg="#4ed885")
        self.button6.configure(bg=self.orig_color)


def medir_vel():                        #Função que mede a velocidade do encoder do motor (Thread separada do resto do programa)
    global vars                         #Variavel de velocidade global
    StartTime = time.time()             
    tempo = 1                           #Tempo de duração do calculo para cada velocidade
    StopTime = StartTime+tempo

    aux2 = GPIO.input(GPIO_SENSOR1)
    i = 0

    while (time.time() <= StopTime):        #Conta quantas alterações do encoder acontece em 1 seg
        aux1 = GPIO.input(GPIO_SENSOR1)
        if(aux1 != aux2):
            i = i+1

        aux2 = aux1
    v = i * 60 / (23*75*tempo)              #Calculo da velocidade (numero de alterações por minuto para um motor com reduçao de 75)


def pid(vmedido, setpoint):                 #Controlador PID
    integradorMax = 500
    integradorMin = -500
    global velAtual
    global erroAtual                        
    
    Kp = 2.3                                #Constantes do PID
    Kd = 0
    Ki = 10000
    
    try:                                    #Define as condições inicias
        integrador      
    except:
        try:
            velAtual
        except:
            velAtual=0
            erroAtual = 0
        integrador = 0
        derivador = 0
      
    erro = setpoint - velAtual
    P = Kp * erro
    
    D = Kd * ( erro - derivador)
    derivador = erro
    
    integrador  = integrador + erroAtual
    if integrador > integradorMax:
        integrador = integradorMax
    elif integrador < integradorMin:
        integrador = integradorMin
        
    I= integrador * Ki
    
    u = P + I + D                       #u - entrada PWM do motor
    

    if u < 0:                           #PWM minimo (0%)
        u = 0
    elif u > 100:                       #PWM maximo (100%)
        u = 100
        
    return u


def distance():                         #Biblioteca para o sensor ultrassonico
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    return distance


def ligar(dutyC, sentido):                  #Ativa o PWM do motor dependendo do sentido selecionado
    if sentido == 1:
        pwmh.ChangeDutyCycle(0)             #Zera o PWM que não está sendo utilizado
        pwmah.ChangeDutyCycle(dutyC)        #Ativa o PWM com o dutycicly (dutyC)
            
    else:
        pwmh.ChangeDutyCycle(dutyC)
        pwmah.ChangeDutyCycle(0)


pwmh = GPIO.PWM(GPIO_PWMH,1000)             #Inicia o PWM com frequencia de 1kHz
pwmh.start(0)
pwmah = GPIO.PWM(GPIO_PWM,1000)     
pwmah.start(0)

dutyC = 0                                   #Define duty cycle inicial
                                            #Define a escala de funcionamento do sensor ultrassonico (cm) 
sensorMax = 30                              #Maximo de 30 cm
sensorMin = 10                              #Minimo de 10 cm


def do_main():
    root = Tk()                             #Define a tela root

    root.overrideredirect(True)             #Programa inicializa em fullscreen
    root.overrideredirect(False)
    root.attributes('-fullscreen',True)

    frame_1 = Frame()                       #Cria os frames para a chamada da classe AnalogMeter
    frame_2 = Frame()
    frame_3 = Frame()
    frame_4 = Frame()

    frame_1.grid(row=0, column=0,rowspan=2) #Define a posição dos frames no grid
    frame_2.grid(row=0, column=1,rowspan=2)
    frame_3.grid(row=0, column=3)
    frame_4.grid(row=1, column=3)
    
    time.sleep(1)                           #Para o programa por 1 seg
    
                                                     #Cria o medidor analogico do PWM
    Element_1 = Analog_Meter(master=frame_1, side=300, start=0, end=100, grad_max=10, grad_min=5, lim1=10, lim2=100,value=0, text="PWM - Duty Cycle", units="%")
                                                    #Cria o medidor analogico da velocidade
    Element_2 = Analog_Meter(master=frame_2, side=300, start=0, end=100, grad_max=10, grad_min=2, lim1=5, lim2=50,value=0, text="Velocidade", units="rpm")
                                                    #Cria o medidor analogico do sensor ultrassonico
    Element_3 = Analog_Meter(master=frame_3, side=200, start=0, end=100, grad_max=10, grad_min=2, lim1=sensorMin, lim2=sensorMax,value=0, text="Sensor", units="cm")
                                                    #Cria a interface de botoes
    Element_4 = Button_Class(master=frame_4, height=100, width=200)

    root.resizable(width=FALSE, height=FALSE)       #Impede a alteração de tamanho da janela

    root.update_idletasks()                         #Update na interface grafica
    root.update()

    Analog_Meter.delete_entry(Element_2)            #Remove os botoes da classe AnalogMeter
    Analog_Meter.delete_entry(Element_3)
    Analog_Meter.delete_entry(Element_1)
    velTXT = Element_2.can_meter.create_text(Element_2.side/2, Element_2.origy+Element_2.R*1.3,text=" ")    #Adiciona um texto para o medidor de velocidade
    global text
    while True:                                     #Mainloop
        text = Button_Class.GetText(Element_4)      #Olha qual botao foi selecionado na interface de botoes (PWM/Velocidade/Sensor)
        
        if text == "PWM":                           #Quando PWM selecionado
            sentido(Element_4)                      #Chama a funçao sentido para verificar o sentido selecionado
            Analog_Meter.delete_entry(Element_3)    #Desativa o input nos outros medidores
            Analog_Meter.delete_entry(Element_2)
            Analog_Meter.enable_entry(Element_1)    #Ativa o input no medidor PWM selecionado
            Element_2.can_meter.itemconfigure(velTXT, text=" ")     #Remove o texto da velocidade medida

            Analog_Meter.Read(Element_3, 0)         #Zera o medidor do sensor
            Analog_Meter.ChangeText(Element_3, "Desativado")    #Adiciona texto de desativado do medidor de sensor 

            dutyC = Element_1.value                 #Le em qual posição o ponteiro do PWM esta selecionado
            ligar(dutyC, Element_4.sentido)         #Atualiza o sentido de rotação do motor
            Analog_Meter.Read(Element_2,round(v,2)) #Atualiza a velocidade medida 

        elif text == "Velocidade":                  #Quando Velocidade selecionado
            sentido(Element_4)
            Analog_Meter.delete_entry(Element_1)    #Desativa o input nos outros medidores
            Analog_Meter.delete_entry(Element_3)
            Analog_Meter.enable_entry(Element_2)    #Ativa o input no medidor Velocidade selecionado
            Analog_Meter.Read(Element_3, 0)         #Zera o medidor do sensor
            Analog_Meter.ChangeText(Element_3, "Desativado")    #Adiciona texto de desativado do medidor de sensor 
            Element_2.can_meter.itemconfigure(velTXT, text="Velocidade medida: {} rpm".format(round(v,2)),font=("Purisa", 12)) #Adiciona um texto exibindo a velocidade medida pelo encoder
            dutyC = pid(v,Element_2.value)          #Calcula o novo duty cycle usando a função PID
            ligar(dutyC, Element_4.sentido)         #Atualiza o sentido de rotação do motor
            Analog_Meter.Read(Element_1, round(dutyC,2))    #Atualiza o PWM para a velocidade calculada pelo PID

        elif text == "Sensor":                      #Quando o sensor for selecionado
            time.sleep(0.5)                         #Diminui a frequencia de atualização 
            sentido(Element_4)                      #Chama a funçao sentido para verificar o sentido selecionado
            Analog_Meter.ChangeText(Element_3, "Sensor")        #Ativa o texto do sensor caso estivesse ''desativado''
            Element_2.can_meter.itemconfigure(velTXT, text=" ") #Remove o texto de velocidade medida
            Analog_Meter.delete_entry(Element_1)            #Desativa o input nos outros medidores
            Analog_Meter.delete_entry(Element_2)
            Analog_Meter.enable_entry(Element_3)            #Ativa o input no medidor Velocidade selecionado
            Element_3.can_meter.bind("<Button-1>", '')

            Analog_Meter.Read(Element_2,round(v,2))         #Atualiza o medidor de velocidade
            dist = round(distance(),2)                      #Calcula a distancia medida pelo sensor
            Analog_Meter.Read(Element_3,dist)               #Atualiza o medidor do sensor

            if dist < sensorMin:                            #Limita o extremos do sensor
                dist = sensorMin

            if dist > sensorMax:
                dist = sensorMax

            dutyC = round((((100-0)*(dist-sensorMin))/(sensorMax-sensorMin)+0), 1)      #Calcula um duty cycle com base na distancia do sensor ultrassonico
            Analog_Meter.Read(Element_1, dutyC)             #Atualiza o medidor do PWM
            ligar(dutyC, Element_4.sentido)                 #Atualiza o sentido de rotação do motor

        elif text == "Desligado":                           #Quando for selecionado o botao OFF
            Analog_Meter.delete_entry(Element_1)            #Remove os inputs de todos os medidores
            Analog_Meter.delete_entry(Element_2)
            Analog_Meter.delete_entry(Element_3)
            Analog_Meter.Read(Element_1, 0)                 #Zera todos os medidores
            Analog_Meter.Read(Element_2, 0)
            Analog_Meter.Read(Element_3, 0)
            pwmah.ChangeDutyCycle(0)                        #Desliga o motor
            pwmh.ChangeDutyCycle(0)

        root.update_idletasks()                             #Atualiza a interface grafica
        root.update()                                       
        time.sleep(0.0001)


if __name__ == "__main__":                          
    t1 = Thread(target= do_main, args=[])                   #Cria Thread 1 - Interfaces graficas
    t1.start()
#   with open('valores.txt', 'w') as f:
    while True:
        t2 = Thread(target=medir_vel, args=[])              #Cria Thread 2 (em loop) - Calculo de velocidade
        t2.start()
        t2.join()
#       t=time.time()
#       f.write("%d;" % v)
#       f.write("%d\n" % t)
