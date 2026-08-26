import ubluetooth

DEVICE_NAME = "Sistema_de_gestion_de_residuos"

# --- Pines de Sensores ---
PIN_PIR = 23         # Sensor PIR de movimiento
PIN_TRIG = 32        # Sensor Ultrasónico HC-SR04 Trigger
PIN_ECHO = 33        # Sensor Ultrasónico HC-SR04 Echo

# --- Pines I2C (Pantalla LCD) ---
PIN_SDA = 21         # Línea de datos I2C
PIN_SCL = 22         # Línea de reloj I2C
LCD_ADDR = 0x27      # Dirección I2C común (puede ser 0x3F)

# --- Pines de Actuadores e Indicadores ---
PIN_SERVO = 18       # Servomotor de la compuerta
PIN_LED_VERDE = 4    # Indicador de Sistema Listo
PIN_LED_ROJO = 5     # Indicador de Alerta / Tapa abierta
PIN_BUZZER = 19      # Alerta acústica

# --- Parámetros de Operación ---
DISTANCIA_DETECCION_CM = 20  # Distancia máxima para apertura automática
TIEMPO_TAPA_ABIERTA_S = 4    # Segundos que permanece abierta la compuerta
INTERVALO_ENVIO_BLE_MS = 1000 # Envío de telemetría a la app cada 1 segundo

# --- UUIDs Estándar BLE UART ---
UART_SERVICE_UUID = ubluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
UART_TX_UUID = ubluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")
UART_RX_UUID = ubluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")