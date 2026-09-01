import ubluetooth

# --- Identificación Bluetooth ---
DEVICE_NAME = "Basurero_UNRaf"

# --- Pines de Sensores ---
PIN_PIR = 19         # Sensor PIR
PIN_TRIG = 5         # HC-SR04 Trigger
PIN_ECHO = 18        # HC-SR04 Echo

# --- Pines I2C (Pantalla LCD 20x4) ---
PIN_SDA = 21         # Línea SDA
PIN_SCL = 22         # Línea SCL
LCD_ADDR = 0x27      # Dirección I2C
LCD_ROWS = 4         # 4 Filas
LCD_COLS = 20        # 20 Columnas

# --- Pines de Actuadores y Señalización ---
PIN_SERVO = 15       # Servomotor
PIN_LED_VERDE = 12   # LED Verde
PIN_LED_ROJO = 13    # LED Rojo
PIN_BUZZER = 14      # Buzzer con PWM

# --- Parámetros de Operación ---
UMBRAL_LLENO_CM = 10         # Si la distancia es menor a 10 cm, está lleno
TIEMPO_TAPA_ABIERTA_S = 6    # Segundos que la tapa queda abierta
TIEMPO_CALIBRACION_PIR_S = 30 # Calibración al inicio

# --- UUIDs BLE SPP ---
UART_SERVICE_UUID = ubluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
UART_TX_UUID = ubluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")