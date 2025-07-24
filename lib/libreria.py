from machine import I2C, Pin, SDCard, deepsleep, reset

import os
import ds1307
import time
#import AT24C32N
#from TFmini_I2C import TFminiI2C
#from hcsr04 import HCSR04


class Perifericos:
    SD_MOUNT = "/sd"
    SD_FILE_PATH = "/sd/temp.csv"
    SD_FILE_PATH_AJUSTES = "/sd/ema.conf"
    DATETIME_NOW = [2025, 4, 14, 1, 11, 00, 10, 0]
    ledAlert = Pin(2, Pin.OUT)
    ledAlert.value(1)
    time.sleep(1)
    ledAlert.value(0)

    def __init__(self):
        self.confI2C()
        print("i2c ok")
        #self.confEEPROM(i2c_addr=0x57, pages=128, bpp=32)
        print("epprom ok")
        self.confSD()
        print("sd ok")
        self.confDS()
        print("reloj ok")
        #self.sensorUltras = self.confUltras()
        #self.lidar = self.confLidar()
        #print("lidar ok")
        
        
    def ledAlerta(self, tiempo=0.5, repeticiones=3):
        for i in range(repeticiones):
            self.ledAlert.on()
            time.sleep(tiempo)
            self.ledAlert.off()
            time.sleep(tiempo)

    def confSD(self):
        self.sd = SDCard(slot=2, freq=1320000)
        try:
            os.mount(self.sd, self.SD_MOUNT)
        except OSError as e:
            self.ledAlerta(0.1, 5)
            print("error de memoria")

    def leerSD(self,filepath):
        try:
            if not os.stat(filepath):
                return None
            with open(filepath, "r") as logf:
                return logf.read()
        except OSError:
            self.confSD()
            return None

    def escribirSD(self, fecha ="", hora="", sensorU ="",):
        temp = "{},{},{}\r\n".format(fecha, hora, sensorU)
        try:
            with open(self.SD_FILE_PATH, "a") as logf:
                logf.write(temp)
                logf.flush()
        except OSError:
            self.ledAlerta(0.3, 3)
            print("error de escritura en SD")
            
    def escrituraLocal(self, fecha ="", hora="", sensorU ="",):
        temp = "{},{},{}\r\n".format(fecha, hora, sensorU)
        with open('/lectura.csv', "a") as logf:
            logf.write(temp)
            logf.flush()
            print("escritura local correcta")
    def backupLocalDate(self,fechahora):
        with open('/tempFechaHora.cfg', "w") as logf:
            logf.write(str(fechahora))
            print("backup hora ok")
    def recuperaLocalDate(self):
        with open('/tempFechaHora.cfg', "r") as logf:
            temp=logf.read()[1:-1].split(",")
            temp= [int(x) for x in temp]
            print((temp))
            self.ds.datetime(temp)
            print("recuperacion de hora desde memoria interna")
        

    # Configuración de I2C
    def confI2C(self):
        self.i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=50000)

    # Configuración y manejo del RTC (DS1307)
    def confDS(self):
        
        try:
            self.ds = ds1307.DS1307(self.i2c)
            self.ds.halt(False)
            """
            if self.ds.datetime()[0] < 2025 or self.ds.datetime()[0] > 2045:
                lectura = self.leerSD(self.SD_FILE_PATH_AJUSTES)
                try:
                    año = int(lectura.splitlines()[17].split(":")[1])
                    mes = int(lectura.splitlines()[18].split(":")[1])
                    dia = int(lectura.splitlines()[19].split(":")[1])
                    hora = int(lectura.splitlines()[20].split(":")[1])
                    minutos = int(lectura.splitlines()[21].split(":")[1])
                    segundos = int(lectura.splitlines()[22].split(":")[1])
                    datatime=[año,mes,dia,1,hora,minutos,segundos,0]
                    self.ds.datetime(datatime)
                    
                    with open(self.SD_FILE_PATH_AJUSTES, "w") as config:
                        try:
                            lines = lectura.splitlines()
                            lines[17] = "Año:"
                            lines[18] = "Mes:"
                            lines[19] = "Dia:"
                            lines[20] = "Hora:"
                            lines[21] = "Minutos:"
                            lines[22] = "Segundos:"
                            config.write("\n".join(lines))
                        except:
                            print("Error de ajustes")
                except:
                    print("Archivo de ajustes incorrecto en SD, usando EEPROM..")
                    try:
                        if self.synRTCfromEEPROM():
                            print("intento de lectura EEPROM ok")
                            self.ds.datetime(self.DATETIME_NOW)
                            print("hora desde EEPROM ajustada correctamente...")
                        else:
                            print("error al ajustar hora")
                    except:
                        print("error EEPROM_0")
            else:
                print("error...")
            """        
                    
                    
                
        except OSError:
            self.ledAlerta(0.1, 10)
            print("error SD")
            reset()
            pass

    def leerDS1307(self):
        try:
            fechaHora = self.ds.datetime()
            fecha = "{:02}/{:02}/{}".format(fechaHora[2], fechaHora[1], str(fechaHora[0]))
            hora = "{:02}:{:02}:{:02}".format(fechaHora[4], fechaHora[5], fechaHora[6])
            return fecha, hora, fechaHora
        except OSError:
            print("Error al leer la hora")
            return None, None, None
        
    def ajusteReloj(self,ajuste):
        self.ds.datetime(ajuste)

    # Configuración y manejo de la EEPROM
    def confEEPROM(self, i2c_addr=0x57, pages=128, bpp=32):
        self.eeprom = AT24C32N.AT24C32N(self.i2c, i2c_addr, pages, bpp)

    def leerEEPROM(self, addr, nbytes):
        try:
            return self.eeprom.read(addr, nbytes)
        except OSError:
            print("Error al leer la EEPROM")
            return None

    def escribirEEPROM(self, addr, buf):
        try:
            self.eeprom.write(addr, buf)
        except OSError:
            print("Error al escribir en la EEPROM")
            return None

    def borrarEEPROM(self):
        try:
            self.eeprom.write(0, b"\x00" * self.eeprom.capacity())
        except OSError:
            print("Error al borrar la EEPROM")
            return None
        return True

    def synRTCfromEEPROM(self):
        print("sincronizando hora... EEPROM")
        try:
            lectura = self.leerEEPROM(0, 19)
            print("Lectura de EEPROM correcta")
            print(lectura)
            if lectura != b'\x00' * 19:
                self.DATETIME_NOW = [
                    int(lectura[6:10]), int(lectura[3:5]), int(lectura[0:2]), 1,
                    int(lectura[11:13]), int(lectura[14:16]), int(lectura[17:19]), 0
                ]
                print("DATETIME_NOW: recuperado de la EEPROM: ", self.DATETIME_NOW, lectura)
                return True
            else:
                print("DATETIME_NOW: no se ha recuperado de la EEPROM")
                return False
        except OSError:
            print("Error al sincronizar el RTC desde la EEPROM")
            return False

    # Configuración y manejo de la tarjeta SD



    # Manejo de alarmas con LED
    
    # Configuración del sensor ultrasónico
    def confUltras(self):
        sensorUltras = HCSR04(trigger_pin=26, echo_pin=25)
        return sensorUltras
    
    def confLidar(self):
        lidar = TFminiI2C()
        return lidar
    
    def coeficienteVariacion(self, buf):
        """
        Calcula el coeficiente de variación a partir de un buffer de datos.
        """
        if len(buf) == 0:
            return 0
        suma = sum(buf)
        media = suma / len(buf)
        varianza = sum((x - media) ** 2 for x in buf) / len(buf)
        desviacion_estandar = varianza ** 0.5
        return (desviacion_estandar / media) * 100
    def leerSensorUltras(self):
        buf = []
        i=0
        while i < 5:
            tempLectura=self.sensorUltras.distance_cm()
            if tempLectura<200 and tempLectura>3.0:
                buf += [self.sensorUltras.distance_cm()]
                i=i+1
            time.sleep(0.5)
        co=self.coeficienteVariacion(buf)
        if co < 3.0:
            return buf, co
        else:
            return None, None
    def leerLidar(self):
        distancia=self.lidar.readDistance()
        return distancia
        
# aquí debe ir el código del GPS
time.sleep(5)
if __name__ == "__main__":
    perifericos = Perifericos()
    print(perifericos.leerEEPROM(0x57,17))

"""
    while True:
        try:
            fecha, hora = perifericos.leerDS1307()
            buf, co = perifericos.leerSensorUltras()
            perifericos.escribirSD(fecha, hora, buf)
            print("Fecha: ", fecha, "Hora: ", hora, "Sensor: ", buf, "Coeficiente de variación: ", co)
            deepsleep(600000)
        except:
            reset()
"""