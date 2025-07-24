from machine import ADC, Pin, reset, SDCard,I2C
import os
import time
import ds1307
from libreria import Perifericos
from simple import MQTTClient
import network
from random import randint
from libreria import Perifericos


perifericos = Perifericos()


pluviometro = ADC(36)
pluviometro.atten(ADC.ATTN_11DB)


flag=True
contador=0.0
segundos=0

wifi="mifiEmaV3"
clavewifi="emaMifi001"
server="ip del servidor" #ejemplo "192.168.0.1"
puerto=1234
user="usuario"
claveMqtt="contraseña"
nodo="pluviometro"


def do_connect(SSID, PASSWORD):
    import network                            # importa el módulo network
    global sta_if
    sta_if = network.WLAN(network.STA_IF)     # instancia el objeto -sta_if- para controlar la interfaz STA
    if not sta_if.isconnected():              # si no existe conexión...
        sta_if.active(True)                       # activa el interfaz STA del ESP32
        sta_if.config(dhcp_hostname="Pluviometro"+"-"+str(randint(1,10)))
        sta_if.connect(SSID, PASSWORD)            # inicia la conexión con el AP
        print('Conectando a la red', SSID +"...")
        while not sta_if.isconnected():           # ...si no se ha establecido la conexión...
            pass                                  # ...repite el bucle...
    print('Configuración de red (IP/netmask/gw/DNS):', sta_if.ifconfig())
    
do_connect(wifi,clavewifi)

cliente = MQTTClient(client_id="Pluviometro"+str(randint(1,1000)),server=str(server),port=int(puerto),user=str(user),password=str(claveMqtt),keepalive=60)
cliente.connect()


while True:
    
    fecha, hora, fechahora = perifericos.leerDS1307()
    try:
        if int(fechahora[0]) < 2025 or int(fechahora[0])>2030:
            perifericos.recuperaLocalDate()
            pass
        else:
            fecha, hora, fechahora = perifericos.leerDS1307()
            perifericos.backupLocalDate(fechahora)
    except:
        pass

    lluvia = pluviometro.read_u16()
    if lluvia > 35000:
        if flag==True:
          contador=contador+1
          flag=False
    if lluvia<35000:
        if flag==False:
            contador=contador+1
            flag=True
    
    lectura=contador*0.149
    try:
        cliente.publish(nodo,str(lectura))
    except:
        pass
    print(fecha)
    print(hora)
    print(lectura,"mm")
    time.sleep(1)
    segundos=segundos+1
    if segundos>300:
        perifericos.escribirSD(fecha,hora,lectura)
        perifericos.escrituraLocal(fecha,hora,lectura)
        segundos=0
    try:
        if fechahora[4]==23:
            if fechahora[5]==59:
                if fechahora[6]>50:
                    perifericos.escribirSD(fecha,hora,lectura)
                    perifericos.escrituraLocal(fecha,hora,lectura)
                    contador=0
    except:
        pass
    
