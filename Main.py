#Felipe Brandao Ippolito    RA: 12.01378-0
#Fabio Akira                RA: 15.03499-2
#Ronaldo Macarrao           RA: 15.01715-0

from Meter import *                 #Mostrador analogico
from Button import *                #Botoes
import time
from threading import Thread        #Biblioteca para cria segunda thread
import RPi.GPIO as GPIO             #Gpio raspberry pi
import requests

#TOKEN = "A1E-lyF6uBKNHKIT6EofUC924T8XhuvF1A"  # Put your TOKEN here
#DEVICE_LABEL = "projeto"        # Put your device label here

TOKEN = "A1E-dUZWxbf4tPzbKER9BXLzQ7jYXbyLYY"  # Put your TOKEN here
DEVICE_LABEL = "controlador-velocidade"        # Put your device label here

#motorpwm = "motorpwm"
#motorvel = "motorvel"

GPIO.setwarnings(False)         #Tira os avisos 
GPIO.setmode(GPIO.BCM)          #Modo BCM

GPIO_TRIGGER = 25               #Trigger sensor ultrasonico
GPIO_ECHO = 24                  #Echo sensor ultrassonico
GPIO_PWM = 18                   #PWM1 ponte h - sentido anti-horario
GPIO_SENSOR1 = 23               #Encoder motor
GPIO_PWMH = 12                  #PWM2 ponte h - sentido horario


# Define saida/entrada (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_PWM,GPIO.OUT)
GPIO.setup(GPIO_SENSOR1, GPIO.IN)
GPIO.setup(GPIO_PWMH, GPIO.OUT)

pwmh = GPIO.PWM(GPIO_PWMH,1000)  #Inicia o PWM horario com frequencia de 1kHz
pwmh.start(0)
pwmah = GPIO.PWM(GPIO_PWM,1000)  #Inicia o PWM anti-horario com frequencia de 1kHz
pwmah.start(0)

#Escala de funcionamento do sensor ultrassonico (cm)
sensorMax = 30                  #Max 30cm
sensorMin = 10                  #Min 10cm

def init():             #Inicia o ubidots com todos os valores em 0
    global uInterface, uLiga, uSentido, uMotorSelec, uMotorPWM, uMotorVel, dutyC
    uLiga = 0
    uSentido = 0
    uMotorSelec = 0
    uMotorPWM = 0 
    uMotorVel = 0
    dutyC = 0
    uInterface = 0
    payload = init_payload("motorpwm", "motorvel", "liga", "sentido", "controlemotor", "controle")
    post_request(payload)

def init_payload(variable_1, variable_2, variable_3, variable_4, variable_5,variable_6): #, variable_2, variable_3):
    payload = {variable_1: 0,variable_2: 0,variable_3: 0,variable_4: 0,variable_5: 0,variable_6: 0}
    return payload

def build_payload(variable_1, value_1, variable_2, value_2, variable_3, value_3, variable_4, value_4, variable_5,value_5):
    payload = {variable_1: value_1,variable_2: value_2,variable_3: value_3,variable_4: value_4,variable_5: value_5} 
    return payload

def get_var(device, variable):
    try:
        url = "http://things.ubidots.com/"
        url = url + \
            "api/v1.6/devices/{0}/{1}/".format(device, variable)
        headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}
        req = requests.get(url=url, headers=headers)
        return req.json()['last_value']['value']
    except:
        return get_var(device,variable)         #Recursividade caso erro

def post_request(payload):
    # Creates the headers for the HTTP requests
    url = "http://things.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url, DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}
    # Makes the HTTP requests
    status = 400
    attempts = 0
    while status >= 400 and attempts <= 5:
        req = requests.post(url=url, headers=headers, json=payload)
        status = req.status_code
        attempts += 1
        time.sleep(1)
    # Processes results
    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts, please check \
            your token credentials and internet connection")
        return False
    print("[INFO] request made properly, your device is updated")
    return True

def sentido(self):              #Função altera a interface grafica dependendo do sentido
    if self.sentido == 0:       #Verifica o sentido
        self.button6.configure(bg="#4ed885")        #Altera acor dos botões
        self.button5.configure(bg=self.orig_color)
    else:
        self.button5.configure(bg="#4ed885")
        self.button6.configure(bg=self.orig_color)

def medir_vel():                    #Função que mede a velocidade do encoder do motor (Thread 2)
    while True:
        global v                                #Variavél de velocidade global
        StartTime = time.time()
        tempo = 1                               #Tempo de duração para o cálculo da velocidade
        StopTime = StartTime+tempo

        aux2 = GPIO.input(GPIO_SENSOR1)
        i = 0

        while (time.time() <= StopTime):        #Conta uantas alterações do encoder acontece em 1 seg
            aux1 = GPIO.input(GPIO_SENSOR1)
            if(aux1 != aux2):
                i = i+1

            aux2 = aux1
        v = i * 60 / (23*75*tempo)      #Cálculo da velocidade (Número de alterações por minuto para um motor com redução de 76)

def pid(vmedido, setpoint):
    integradorMax = 500
    integradorMin = -500
    global velAtual
    global erroAtual
    
    Kp = 2.3
    Kd = 0
    Ki = 10000
    
    try:
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
    
    u = P + I + D
    

    if u < 0:
        u = 0
    elif u > 100:
        u = 100
        
    return u

def distance():                     #Biblioteca para o sensor ultrassonico
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

def ligar(dutyC, sentido):          #Ativa o PWM do motor dependendo do sentido selecionado
    if sentido == 1:
        pwmh.ChangeDutyCycle(0)         #Zera o PWM que não está sendo utilizado
        pwmah.ChangeDutyCycle(dutyC)    #Ativa o PWM com o dutycicly (dutyC)
            
    else:
        pwmh.ChangeDutyCycle(dutyC)
        pwmah.ChangeDutyCycle(0)

def ubidots():                      #Ubidots GET e POST - Thread 3
    global uSentido, uLiga, uMotorSelec, uMotorPWM, uMotorVel, uInterface, dutyC

    uInterface = get_var(DEVICE_LABEL,'controle')
    if uInterface == 1:                                                     #Controle web selecionado
        uLiga = get_var(DEVICE_LABEL,'liga')                                #Coleta os valores da web
        uSentido = get_var(DEVICE_LABEL,'sentido')
        uMotorSelec = get_var(DEVICE_LABEL,'controlemotor')
        uMotorPWM = get_var(DEVICE_LABEL,'motorpwm')
        uMotorVel = get_var(DEVICE_LABEL,'motorvel')
        if uLiga == 0:
            payload = {"motorpwm": 0, "motorvel": 0}
            post_request(payload)
        else:
            if uMotorSelec == 0:
                payload = {"motorvel": v}
                post_request(payload)
            else:
                payload = {"motorpwm": dutyC}
                post_request(payload)

    if uInterface == 0:
        payload = build_payload("motorpwm", dutyC, "motorvel", v, "liga", uLiga, "sentido", uSentido, "controlemotor", uMotorSelec)
        post_request(payload)

def do_main():
    global uSentido, uLiga, uMotorSelec, uMotorPWM, uMotorVel, uInterface, dutyC

    root = Tk()             #Define tela root

    #root.overrideredirect(True)        #Programa inicializa em fullscreen
    #root.overrideredirect(False)
    #root.attributes('-fullscreen',True)

    #Cria os frames para a chamada da classe AnalogMeter
    frame_1 = Frame()
    frame_2 = Frame()
    frame_3 = Frame()
    frame_4 = Frame()

    #Define a posição dos frames no grid
    frame_1.grid(row=0, column=0,rowspan=2)
    frame_2.grid(row=0, column=1,rowspan=2)
    frame_3.grid(row=0, column=3)
    frame_4.grid(row=1, column=3)
    
    time.sleep(3)       #Para o programa por 1 seg

    #Cria o medidor analogico do PWM
    Element_1 = Analog_Meter(master=frame_1, side=300, start=0, end=100, grad_max=10
    , grad_min=5, lim1=10, lim2=100,value=0, text="PWM - Duty Cycle", units="%")
    
    #Cria o medidor analogico da velocidade
    Element_2 = Analog_Meter(master=frame_2, side=300, start=0, end=100, grad_max=10
    , grad_min=2, lim1=5, lim2=50,value=0, text="Velocidade", units="rpm")
    
    #Cria o medidor analogico do sensor
    Element_3 = Analog_Meter(master=frame_3, side=200, start=0, end=100, grad_max=10
    , grad_min=2, lim1=sensorMin, lim2=sensorMax,value=0, text="Sensor", units="cm")
    
    #Cria a interface de botões
    Element_4 = Button_Class(master=frame_4, height=100, width=200)

    root.resizable(width=FALSE, height=FALSE)           #Impede a alteração de tamanho da janela

    root.update_idletasks()                             #Update na interface grafica
    root.update()

    #Remove os botoes da classe AnalogMeter
    Analog_Meter.delete_entry(Element_2)
    Analog_Meter.delete_entry(Element_3)
    Analog_Meter.delete_entry(Element_1)

    #Adiciona um texto para o medidor de velocidade
    velTXT = Element_2.can_meter.create_text(Element_2.side/2, Element_2.origy+Element_2.R*1.3,text=" ")

    while True:                     #Main loop
        if uInterface == 0:
            Element_4.button1['state'] = 'normal'
            Element_4.button2['state'] = 'normal'
            Element_4.button3['state'] = 'normal'
            Element_4.button4['state'] = 'normal'
            Element_4.button5['state'] = 'normal'
            Element_4.button6['state'] = 'normal'
            text = Button_Class.GetText(Element_4)        #Olha qual botao foi selecionado na interface de botoes (PWM/Velocidade/Sensor)
            uSentido = Element_4.sentido
        else:
            Element_4.button1['state'] = 'disabled'
            Element_4.button2['state'] = 'disabled'
            Element_4.button3['state'] = 'disabled'
            Element_4.button4['state'] = 'disabled'
            Element_4.button5['state'] = 'disabled'
            Element_4.button6['state'] = 'disabled'
            Analog_Meter.delete_entry(Element_1)
            Analog_Meter.delete_entry(Element_2)
            if uLiga == 1:
                if uSentido == 1:
                    Element_4.sentido = 1
                else:
                    Element_4.sentido = 0
                
                if uMotorSelec == 1:
                    text = "Velocidade"
                    Element_2.can_meter.configure(background='#4ed885')
                    Element_4.button1.configure(bg="#4ed885")
                    Element_4.button2.configure(bg=Element_4.orig_color)
                    Element_4.button3.configure(bg=Element_4.orig_color)
                    Element_4.button4.configure(bg=Element_4.orig_color)
                else:
                    text = "PWM"
                    Element_1.can_meter.configure(background='#4ed885')
                    Element_4.button3.configure(bg="#4ed885")
                    Element_4.button2.configure(bg=Element_4.orig_color)
                    Element_4.button1.configure(bg=Element_4.orig_color)
                    Element_4.button4.configure(bg=Element_4.orig_color)
                
            else:
                text = "Desligado" 
                Element_4.button2.configure(bg=Element_4.orig_color)
                Element_4.button1.configure(bg=Element_4.orig_color)
                Element_4.button3.configure(bg=Element_4.orig_color)
                Element_4.button4.configure(bg="#770e0e")
                Element_4.button5.configure(bg=Element_4.orig_color)
                Element_4.button6.configure(bg=Element_4.orig_color)
        
        if text == "PWM":                                           #Quando PWM selecionado
            sentido(Element_4)                                      #Verifica o sentido selecionado
            Analog_Meter.delete_entry(Element_3)                    #Desativa os inputs nos outros medidores
            Analog_Meter.delete_entry(Element_2)
            if uInterface == 0:
                Analog_Meter.enable_entry(Element_1)                #Ativa o input no medidor PWM selecionado
                dutyC = Element_1.value                             #Le em qual posição o ponteiro do PWM esta selecionado
                uMotorSelec = 0
                uLiga = 1
            else:
                dutyC = uMotorPWM
                Analog_Meter.Read(Element_1, dutyC)
            Element_2.can_meter.itemconfigure(velTXT, text=" ")     #Remove o texto da velocidade medida

            Analog_Meter.Read(Element_3, 0)                         #Zera o medidor do sensor
            Analog_Meter.ChangeText(Element_3, "Desativado")        #Adiciona texto de desativado do medidor de sensor

           
            ligar(dutyC, Element_4.sentido)                         #Atualiza o sentido de rotação do motor
            Analog_Meter.Read(Element_2,round(v,2))                 #Atualiza a velocidade medida 
            

        elif text == "Velocidade":                          #Quando Velocidade selecionado
            sentido(Element_4)
            Analog_Meter.delete_entry(Element_1)            #Desativa o input nos outros medidores
            Analog_Meter.delete_entry(Element_3)
            if uInterface == 0:
                Analog_Meter.enable_entry(Element_2)            #Ativa o input no medidor Velocidade selecionado
                setpoint = Element_2.value
                uMotorSelec = 1
                uLiga = 1
            else:
                setpoint = uMotorVel
                Analog_Meter.Read(Element_2,round(setpoint,2))

            Analog_Meter.Read(Element_3, 0)                         #Zera o medidor do sensor
            Analog_Meter.ChangeText(Element_3, "Desativado")        #Adiciona texto de desativado do medidor de sensor 
            Element_2.can_meter.itemconfigure(velTXT, text="Velocidade medida: {} rpm".format(round(v,2)),font=("Purisa", 12))  #Adiciona um texto exibindo a velocidade medida pelo encoder
            
            dutyC = pid(v,setpoint)                          #Calcula o novo duty cycle usando a função PID
            ligar(dutyC, Element_4.sentido)                         #Atualiza o sentido de rotação do motor
            Analog_Meter.Read(Element_1, round(dutyC,2))            #Atualiza o PWM para a velocidade calculada pelo PID
            

        elif text == "Sensor":                                      #Quando o sensor for selecionado
            time.sleep(0.5)                                         #Diminui a frequencia de atualização
            sentido(Element_4)                                      #Chama a funçao sentido para verificar o sentido selecionado
            Analog_Meter.ChangeText(Element_3, "Sensor")            #Ativa o texto do sensor caso estivesse ''desativado''
            Element_2.can_meter.itemconfigure(velTXT, text=" ")     #Remove o texto de velocidade medida
            Analog_Meter.delete_entry(Element_1)                    #Desativa o input nos outros medidores
            Analog_Meter.delete_entry(Element_2)
            Analog_Meter.enable_entry(Element_3)                    #Ativa o input no medidor Velocidade selecionado
            Element_3.can_meter.bind("<Button-1>", '')

            Analog_Meter.Read(Element_2,round(v,2))                 #Atualiza o medidor de velocidade
            dist = round(distance(),2)                              #Calcula a distancia medida pelo sensor
            Analog_Meter.Read(Element_3,dist)                       #Atualiza o medidor do sensor
            

            if dist < sensorMin:                                    #Limita o extremos do sensor
                dist = sensorMin

            if dist > sensorMax:
                dist = sensorMax

            dutyC = round((((100-0)*(dist-sensorMin))/(sensorMax-sensorMin)+0), 1)  #Calcula um duty cycle com base na distancia do sensor ultrassonico
            Analog_Meter.Read(Element_1, dutyC)                     #Atualiza o medidor do PWM
            ligar(dutyC, Element_4.sentido)                         #Atualiza o sentido de rotação do motor

        elif text == "Desligado":                                   #Quando for selecionado o botao OFF
            if uInterface == 0:
                uLiga = 0
            Analog_Meter.delete_entry(Element_1)                    #Remove os inputs de todos os medidores
            Analog_Meter.delete_entry(Element_2)
            Analog_Meter.delete_entry(Element_3)
            Analog_Meter.Read(Element_1, 0)                         #Zera todos os medidores
            Analog_Meter.Read(Element_2, 0)
            Analog_Meter.Read(Element_3, 0)
            pwmah.ChangeDutyCycle(0)                                #Desliga o motor
            pwmh.ChangeDutyCycle(0)
            dutyC = 0
            Element_2.can_meter.itemconfigure(velTXT, text=" ")     #Remove o texto da velocidade medida

        #print(uSentido)
        root.update_idletasks()                                     #Atualiza a interface grafica
        root.update()
        time.sleep(0.001)


if __name__ == "__main__":
    init()
    t1 = Thread(target= do_main, args=[])                           #Cria Thread 1 - Interfaces graficas
    t1.start()
    t2 = Thread(target=medir_vel, args=[])                      #Cria Thread 2 (em loop) - Calculo de velocidade
    t2.start()

    #with open('valores.txt', 'w') as f:
    time.sleep(3)
    while True:
        t3 = Thread(target=ubidots , args=[])
        t3.start()
        t3.join()
        
        
#       t=time.time()
#       f.write("%d;" % v)
#       f.write("%d\n" % t)