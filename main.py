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
controlEnvio=0
diaActual=0
diaAuxiliar=0

wifi="mifiEmaV3"
clavewifi="emaMifi001"
server="38.242.158.7" #ejemplo "192.168.0.1"
puerto=1883
user="elheim"
claveMqtt="clave"
nodo="EMA_PLUVIOMETRO_001"


def do_connect(SSID, PASSWORD):
    global sta_if, segundos
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        sta_if.active(True)
        sta_if.config(dhcp_hostname="Pluviometro"+"-"+str(randint(1,10)))
        sta_if.connect(SSID, PASSWORD)
        print('Conectando a la red', SSID +"...")
        timeout = 10  # segundos
        start = time.time()
        while not sta_if.isconnected():
            if time.time() - start > timeout:
                print(f"No se pudo conectar a la red {SSID} en {timeout} segundos.")
                return False
            time.sleep(0.5)
            segundos += 0.5

    print('Configuración de red (IP/netmask/gw/DNS):', sta_if.ifconfig())
    return True

do_connect(wifi, clavewifi)



def reconectar_wifi_mqtt():
    # Reintenta conexión WiFi si está desconectado
    if not sta_if.isconnected():
        sta_if.active(False)
        print("WiFi desconectado. Reintentando conexión...")
        do_connect(wifi, clavewifi)
    # Reintenta conexión MQTT si está desconectado
    try:
        cliente.ping()
    except:
        print("MQTT desconectado. Reintentando conexión...")
        try:
            cliente.connect()
        except Exception as e:
            print("Error al reconectar MQTT:", e)

cliente = MQTTClient(client_id="Pluviometro"+str(randint(1,1000)),server=str(server),port=int(puerto),user=str(user),password=str(claveMqtt),keepalive=60)
try:
    cliente.connect()
except Exception as e:
    print("Error al conectar MQTT:", e)

while True:
    
    fecha, hora, fechahora = perifericos.leerDS1307()
    try:
        if int(fechahora[0]) < 2025 or int(fechahora[0])>2030:
            perifericos.recuperaLocalDate()
            pass
        else:
            fecha, hora, fechahora = perifericos.leerDS1307()
            perifericos.backupLocalDate(fechahora)
        diaActual=fechahora[2]
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
    
    lectura=(contador*0.149)*1.2
    print(fecha)
    print(hora)
    print(lectura,"mm")
    time.sleep(1)
    segundos = segundos + 1
    controlEnvio = controlEnvio + 1

    # Enviar solo si el dato es diferente del anterior y diferente de None
    if not hasattr(perifericos, 'lectura_anterior'):
        perifericos.lectura_anterior = None

    if lectura != perifericos.lectura_anterior and lectura is not None:
        try:
            cliente.publish(nodo, str(lectura))
            perifericos.lectura_anterior = lectura
            controlEnvio = 0
        except:
            reconectar_wifi_mqtt()
    if segundos>600:
        perifericos.escribirSD(fecha,hora,lectura)
        perifericos.escrituraLocal(fecha,hora,lectura)
        segundos=0
    try:
        if diaAuxiliar==0:
            diaAuxiliar=diaActual
            
        if diaAuxiliar!=diaActual:
            perifericos.escribirSD(fecha,hora,lectura)
            perifericos.escrituraLocal(fecha,hora,lectura)
            contador=0
            diaAuxiliar=diaActual

    except:
        pass
    

