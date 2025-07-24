# Pluviómetro - Sistema de Medición de Precipitación

Sistema de medición automática de precipitación basado en ESP32 con conectividad WiFi y almacenamiento de datos.

## 📋 Descripción

Este proyecto implementa un pluviómetro digital que mide la precipitación en tiempo real utilizando un sensor conectado a un ESP32. El sistema registra las mediciones, las envía vía MQTT a un servidor remoto y almacena los datos tanto localmente como en una tarjeta SD.

## 🔧 Características

- **Medición en tiempo real**: Lectura continua del sensor de precipitación
- **Conectividad WiFi**: Conexión automática a red inalámbrica
- **Transmisión MQTT**: Envío de datos a servidor remoto
- **Almacenamiento dual**: 
  - Archivo local (`lectura.csv`)
  - Tarjeta SD (`temp.csv`)
- **Reloj en tiempo real**: Módulo DS1307 para timestamp preciso
- **Reset diario**: Contador se reinicia automáticamente a medianoche
- **Indicadores LED**: Alertas visuales para estado del sistema

## 🛠️ Hardware Requerido

- **ESP32** (microcontrolador principal)
- **Sensor de precipitación** (conectado al pin ADC 36)
- **Módulo DS1307** (reloj en tiempo real)
- **Tarjeta SD** (almacenamiento externo)
- **LED indicador** (pin 2)
- **Componentes auxiliares**: resistencias, capacitores, etc.

## 📁 Estructura del Proyecto

```
Pluviometro/
├── main.py              # Programa principal
├── lectura.csv          # Archivo de datos local
├── tempFechaHora.cfg    # Configuración de fecha/hora
├── README.md            # Este archivo
└── lib/
    ├── ds1307.py        # Driver para módulo RTC DS1307
    ├── libreria.py      # Clase Perifericos con funciones auxiliares
    └── simple.py        # Cliente MQTT simplificado
```

## ⚙️ Configuración

### Parámetros WiFi
```python
wifi = "mifiEmaV3"        # Nombre de la red WiFi
clavewifi = "emaMifi001"  # Contraseña WiFi
```

### Parámetros MQTT
```python
server = "192.168.0.1"   # Servidor MQTT
puerto = 1234             # Puerto MQTT
user = "usuario"           # Usuario MQTT
claveMqtt = "contraseña"       # Contraseña MQTT
nodo = "pluviometro"      # Nombre del nodo
```

### Calibración del Sensor
- **Factor de conversión**: 0.149 mm por pulso
- **Umbral de detección**: 35000 (valor ADC)

## 🚀 Funcionamiento

1. **Inicialización**:
   - Configuración de periféricos (I2C, SD, DS1307)
   - Conexión a WiFi
   - Establecimiento de conexión MQTT

2. **Bucle principal**:
   - Lectura del sensor de precipitación cada segundo
   - Detección de cambios de estado (lluvia/no lluvia)
   - Incremento del contador por cada evento detectado
   - Envío de datos vía MQTT en tiempo real

3. **Almacenamiento**:
   - **Cada 5 minutos**: Guardado automático en archivos local y SD
   - **A medianoche**: Reset del contador y guardado final

4. **Gestión de tiempo**:
   - Verificación y corrección automática del reloj DS1307
   - Backup de fecha/hora en archivo de configuración

## 📊 Formato de Datos

Los datos se almacenan en formato CSV con la siguiente estructura:
```
fecha,hora,precipitacion_mm
21/07/2025,14:30:31,0.745
21/07/2025,14:30:44,1.192
```

## 🔄 Funciones Principales

### Clase Perifericos (`lib/libreria.py`)
- `confI2C()`: Configuración del bus I2C
- `confSD()`: Inicialización de tarjeta SD
- `confDS()`: Configuración del módulo DS1307
- `leerDS1307()`: Lectura de fecha y hora
- `escribirSD()`: Escritura en tarjeta SD
- `escrituraLocal()`: Escritura en archivo local
- `ledAlerta()`: Control de LED de estado

### Cliente MQTT (`lib/simple.py`)
- Implementación simplificada del protocolo MQTT
- Publicación automática de mediciones

## 🔧 Instalación y Uso

1. **Preparación del hardware**:
   - Conectar el sensor al pin ADC 36
   - Conectar módulo DS1307 vía I2C
   - Insertar tarjeta SD
   - Conectar LED indicador al pin 2

2. **Configuración del software**:
   - Copiar todos los archivos al ESP32
   - Modificar parámetros de WiFi y MQTT según sea necesario
   - Ajustar factor de calibración si es requerido

3. **Ejecución**:
   - Ejecutar `main.py`
   - Verificar conexión WiFi y MQTT
   - Monitorear las mediciones en tiempo real

## 📈 Monitoreo

- **Consola serie**: Muestra fecha, hora y precipitación acumulada
- **MQTT**: Datos enviados al tópico configurado
- **Archivos**: Registros persistentes en CSV
- **LED**: Indicador visual de estado del sistema

## 🐛 Solución de Problemas

- **Error de memoria SD**: LED parpadea 5 veces rápidamente
- **Error de fecha/hora**: Sistema recupera automáticamente desde backup
- **Desconexión WiFi**: Reintento automático de conexión
- **Error MQTT**: Verificar parámetros de servidor y credenciales

## 📝 Notas Técnicas

- **Resolución temporal**: 1 segundo
- **Precisión**: 0.149 mm por evento
- **Almacenamiento**: Cada 5 minutos + eventos especiales
- **Reset diario**: Automático a las 23:59:50
- **Backup de tiempo**: Archivo `tempFechaHora.cfg`

## 🔗 Dependencias

- **MicroPython**: Firmware base para ESP32
- **machine**: Librería para control de hardware
- **network**: Gestión de conectividad WiFi
- **os**: Operaciones de sistema de archivos

## 📧 Contacto

Para dudas, sugerencias o reportes de errores, contactar al desarrollador del proyecto.

---

**Versión**: 1.0  
**Fecha**: Julio 2025  
**Plataforma**: ESP32 con MicroPython
