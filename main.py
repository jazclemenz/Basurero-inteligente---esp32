import time
from machine import Pin, PWM, I2C
import config
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
from ble_service import BasureroBLE

class BasureroApp:
    def __init__(self):
        # 1. Periféricos desde config
        self.pir = Pin(config.PIN_PIR, Pin.IN)[cite: 8]
        self.trig = Pin(config.PIN_TRIG, Pin.OUT)
        self.echo = Pin(config.PIN_ECHO, Pin.IN)
        self.servo = PWM(Pin(config.PIN_SERVO), freq=50)
        self.led_verde = Pin(config.PIN_LED_VERDE, Pin.OUT)
        self.led_rojo = Pin(config.PIN_LED_ROJO, Pin.OUT)
        self.buzzer = Pin(config.PIN_BUZZER, Pin.OUT)

        # 2. Pantalla LCD
        i2c = I2C(0, scl=Pin(config.PIN_SCL), sda=Pin(config.PIN_SDA), freq=400000)[cite: 8]
        self.lcd = I2cLcd(i2c, config.LCD_ADDR, 2, 16)[cite: 8]

        # 3. Módulo Bluetooth
        self.ble = BasureroBLE()
        self.ultimo_envio_ble = 0

    def mover_servo(self, angulo):
        ancho_pulso = int(40 + (angulo / 180) * 75)
        self.servo.duty(ancho_pulso)

    def sonar_buzzer(self, veces, duracion):
        for _ in range(veces):
            self.buzzer.value(1)
            time.sleep(duracion)
            self.buzzer.value(0)
            time.sleep(duracion)

    def medir_distancia(self):
        self.trig.value(0)
        time.sleep_us(2)
        self.trig.value(1)
        time.sleep_us(10)
        self.trig.value(0)
        
        inicio = time.ticks_us()
        timeout = time.ticks_add(inicio, 30000)
        while self.echo.value() == 0:
            inicio = time.ticks_us()
            if time.ticks_diff(time.ticks_us(), timeout) > 0:
                return 999
        while self.echo.value() == 1:
            fin = time.ticks_us()
            if time.ticks_diff(time.ticks_us(), timeout) > 0:
                return 999
            
        duracion = time.ticks_diff(fin, inicio)
        return (duracion * 0.0343) / 2

    def accionar_compuerta(self, origen="Sensor"):
        self.lcd.clear()
        self.lcd.putstr(f"{origen}\nAbriendo...")
        self.led_verde.value(0)
        self.led_rojo.value(1)
        self.sonar_buzzer(1, 0.1)

        self.mover_servo(90)
        time.sleep(config.TIEMPO_TAPA_ABIERTA_S)

        self.lcd.clear()
        self.lcd.putstr("Cerrando...")
        self.mover_servo(0)
        self.led_rojo.value(0)
        self.led_verde.value(1)
        self.sonar_buzzer(2, 0.1)

        self.lcd.clear()
        self.lcd.putstr("Sistema Listo\nEsperando...")

    def run(self):
        print("Iniciando sistema de Basurero Inteligente...")
        self.mover_servo(0)
        self.led_verde.value(1)
        self.led_rojo.value(0)
        self.lcd.clear()
        self.lcd.putstr("Sistema Listo\nEsperando...")

        while True:
            ahora = time.ticks_ms()
            distancia = self.medir_distancia()

            # Enviar telemetría a la app
            if time.ticks_diff(ahora, self.ultimo_envio_ble) > config.INTERVALO_ENVIO_BLE_MS:
                self.ble.enviar_nivel(distancia)
                self.ultimo_envio_ble = ahora

            # Apertura remota desde App
            if self.ble.comando_recibido == "1":
                self.accionar_compuerta(origen="Orden App")[cite: 1, 4]
                self.ble.comando_recibido = None

            # Apertura física por proximidad
            elif distancia < config.DISTANCIA_DETECCION_CM or self.pir.value() == 1:[cite: 8]
                self.accionar_compuerta(origen="Presencia")[cite: 8]

            time.sleep(0.1)

if __name__ == "__main__":
    app = BasureroApp()
    app.run()