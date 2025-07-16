from machine import ADC, Pin, reset
from time import sleep
from ulora import LoRa, ModemConfig, SPIConfig
from machine import WDT
import random

tony = WDT(timeout=7000)

#Pic Ahorro
led=Pin(25,Pin.OUT)
led.on()
Res=Pin(28,Pin.OUT,Pin.PULL_UP)
Res.off()


# Lora Parameters
RFM95_RST = 9
RFM95_SPIBUS = SPIConfig.rp2_1
RFM95_CS = 13
RFM95_INT = 8
RF95_FREQ = 433.0
RF95_POW = 20
CLIENT_ADDRESS = 1
SERVER_ADDRESS = 2




pot = ADC(Pin(26))
flag=True
contador=0
contador2=0
contador3=0

tony.feed()
sleep(1)
lora = LoRa(RFM95_SPIBUS, RFM95_INT, CLIENT_ADDRESS, RFM95_CS, reset_pin=RFM95_RST, freq=RF95_FREQ, tx_power=RF95_POW, acks=False)
sleep(1)
tony.feed()
while True:
    pot_value = pot.read_u16() # read value, 0-65535 across voltage range 0.0v - 3.3v
    if pot_value > 42000:
        if flag==True:
          contador=contador+1
          contador2=contador
          flag=False
    if pot_value<42000:
        if flag==False:
            contador=contador+1
            contador2=contador
            flag=True

    if contador>=20: 
        lora.send("P"+chr(random.randint(0, 255))+str(contador), SERVER_ADDRESS)
        sleep(1)
        lora.send("P"+chr(random.randint(0, 255))+str(contador), SERVER_ADDRESS)
        sleep(1)
        lora.send("P"+chr(random.randint(0, 255))+str(contador), SERVER_ADDRESS)
        contador=0
    if contador2 != contador:
        contador3=contador3+1
    else:
        contador3=0
    contador2=contador2+1
    if contador3==40:
        if contador != 0:
            lora.send("P"+chr(random.randint(0, 255))+str(contador), SERVER_ADDRESS)
            sleep(1)
            lora.send("P"+chr(random.randint(0, 255))+str(contador), SERVER_ADDRESS)
            sleep(1)
            lora.send("P"+chr(random.randint(0, 255))+str(contador), SERVER_ADDRESS)
            print('mimir')
            contador3=0
            contador=0
            contador2=0
            Res.on()
    
    print(contador)
    tony.feed()
    sleep(0.5)
