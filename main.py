import time
import machine
import config
from ble_service import BasureroBLE

# Importa el controlador LCD que tengas en tu ESP32 (machine_i2c_lcd o i2c_lcd)
try:
    from machine_i2c_lcd import I2cLcd
except ImportError:
    from i2c_lcd import I2cLcd


class BasureroApp:
    def __init__(self):
        print("--- INICIANDO SISTEMA: BASURERO INTELIGENTE ---")

        # 1. Configuración de Hardware
        self.led_rojo = machine.Pin(config.PIN_LED_ROJO, machine.Pin.OUT)
        self.led_verde = machine.Pin(config.PIN_LED_VERDE, machine.Pin.OUT)
        
        self.buzzer = machine.PWM(machine.Pin(config.PIN_BUZZER))
        self.buzzer.duty(0)

        self.trig = machine.Pin(config.PIN_TRIG, machine.Pin.OUT)
        self.echo = machine.Pin(config.PIN_ECHO, machine.Pin.IN)
        self.pir = machine.Pin(config.PIN_PIR, machine.Pin.IN)
        
        self.servo = machine.PWM(machine.Pin(config.PIN_SERVO), freq=50)

        # 2. Pantalla LCD con SoftI2C
        i2c = machine.SoftI2C(
            sda=machine.Pin(config.PIN_SDA), 
            scl=machine.Pin(config.PIN_SCL)
        )
        self.lcd = I2cLcd(i2c, config.LCD_ADDR, config.LCD_ROWS, config.LCD_COLS)

        # 3. Servicio Bluetooth
        self.bt = BasureroBLE()

        # Variable de control de estado (-1 = inicial, 0 = disponible, 1 = lleno)
        self.estado_actual = -1

    def mover_servo(self, angulo):
        duty = int(((angulo / 180.0) * 75) + 40)
        self.servo.duty(duty)

    def medir_distancia(self):
        self.trig.value(0)
        time.sleep_us(2)
        self.trig.value(1)
        time.sleep_us(10)
        self.trig.value(0)
        
        # Medición con time_pulse_us
        duracion = machine.time_pulse_us(self.echo, 1, 30000)
        if duracion <= 0:
            return 999
        return (duracion * 0.034) / 2

    def mostrar_disponible(self):
        self.lcd.clear()
        self.lcd.move_to(4, 0)
        self.lcd.putstr("RECICLABLES")
        self.lcd.move_to(0, 1)
        self.lcd.putstr("> Papel y Carton")
        self.lcd.move_to(0, 2)
        self.lcd.putstr("> Plastico y Vidrios")
        self.lcd.move_to(0, 3)
        self.lcd.putstr("> Latas y Metal")

    def mostrar_lleno(self):
        self.lcd.clear()
        self.lcd.move_to(0, 1)
        self.lcd.putstr("  CONTENEDOR LLENO  ")
        self.lcd.move_to(0, 2)
        self.lcd.putstr(" Dirijase a otro por favor ")

    def estado_lleno_visual(self):
        self.led_rojo.value(1)
        self.led_verde.value(0)
        self.buzzer.duty(0)

    def estado_normal(self):
        self.led_rojo.value(0)
        self.led_verde.value(1)
        self.buzzer.duty(0)

    def inicializar_sistema(self):
        self.mover_servo(0)
        print(f"Calibrando sensor PIR... Espera {config.TIEMPO_CALIBRACION_PIR_S} segundos.")
        time.sleep(config.TIEMPO_CALIBRACION_PIR_S)
        print("¡Sistema listo!")

    def run(self):
        self.inicializar_sistema()

        while True:
            distancia = self.medir_distancia()
            presencia = self.pir.value()

            # --- ESTADO 1: CONTENEDOR LLENO (< 10 cm) ---
            if distancia < config.UMBRAL_LLENO_CM:
                if self.estado_actual != 1:
                    self.estado_lleno_visual()
                    self.mostrar_lleno()
                    self.bt.enviar("1")
                    print("ESTADO: LLENO (Bluetooth: 1)")
                    self.estado_actual = 1

                self.mover_servo(0)  # Tapa bloqueada

                # Alarma si una persona intenta acercarse cuando está lleno
                if presencia == 1:
                    print("Aviso sonoro: Persona intentando usar basurero lleno")
                    self.buzzer.freq(1000)
                    self.buzzer.duty(512)
                    time.sleep(1)
                    self.buzzer.duty(0)
                    time.sleep(3)

            # --- ESTADO 0: CONTENEDOR DISPONIBLE (>= 10 cm) ---
            else:
                if self.estado_actual != 0:
                    self.estado_normal()
                    self.mostrar_disponible()
                    self.bt.enviar("0")
                    print("ESTADO: DISPONIBLE (Bluetooth: 0)")
                    self.estado_actual = 0

                # Apertura por aproximación del usuario
                if presencia == 1:
                    print("Usuario detectado - Abriendo tapa")
                    self.mover_servo(90)
                    time.sleep(config.TIEMPO_TAPA_ABIERTA_S)
                    self.mover_servo(0)

            time.sleep(0.5)


if __name__ == "__main__":
    app = BasureroApp()
    app.run()