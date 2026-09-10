import time
import machine
import config
from ble_service import BasureroBLE

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

        # 2. Pantalla LCD con Hardware I2C (con fallback a SoftI2C)
        try:
            i2c = machine.I2C(0, scl=machine.Pin(config.PIN_SCL), sda=machine.Pin(config.PIN_SDA), freq=400000)
        except Exception:
            i2c = machine.SoftI2C(sda=machine.Pin(config.PIN_SDA), scl=machine.Pin(config.PIN_SCL), freq=100000)
        self.lcd = I2cLcd(i2c, config.LCD_ADDR, config.LCD_ROWS, config.LCD_COLS)
        self.lcd.backlight_on()

        # 3. Servicio Bluetooth
        self.bt = BasureroBLE(callback_comando=self.ordenar_apertura_desde_app)

        # Variable de control de estado (-1 = inicial, 0 = disponible, 1 = lleno)
        self.estado_actual = -1
        # NUEVA VARIABLE AGREGADA: Controla si un administrador está vaciando el basurero
        self.modo_mantenimiento = False

    def ordenar_apertura_desde_app(self, cmd):
        # Usamos strip() por si la app manda saltos de línea invisibles (\n)
        comando_limpio = cmd.strip() 
        
        if comando_limpio == "1":
            print(">>> PRIORIDAD ALTA: Apertura manual / Vaciado (Sensores pausados)")
            self.modo_mantenimiento = True
            
            # 1. Silenciar inmediatamente cualquier alarma sonora activa
            self.buzzer.duty(0)
            
            # 2. Apagar ambos LEDs (no se prenden en modo mantenimiento)
            self.led_verde.value(0)
            self.led_rojo.value(0)
            
            # 3. Abrir la compuerta a 90 grados para permitir vaciar el basurero
            self.mover_servo(90)
            
            # 4. Señalización en pantalla LCD
            self.lcd.clear()
            if config.LCD_ROWS >= 4:
                self.lcd.move_to(1, 0)
                self.lcd.putstr("MODO MANTENIMIENTO")
                self.lcd.move_to(1, 1)
                self.lcd.putstr("VACIANDO BASURERO ")
                self.lcd.move_to(1, 2)
                self.lcd.putstr("COMPUERTA ABIERTA ")
                self.lcd.move_to(0, 3)
                self.lcd.putstr("Sensores en pausa...")
            else:
                self.lcd.move_to(1, 0)
                self.lcd.putstr("MANTENIMIENTO")
                self.lcd.move_to(0, 1)
                self.lcd.putstr("Tapa abierta")
            
        elif comando_limpio == "0":
            print(">>> PRIORIDAD: Cerrando compuerta y reactivando ciclo normal")
            # 1. Apagar ambos LEDs (no se prenden al cerrar)
            self.led_verde.value(0)
            self.led_rojo.value(0)
            
            # 2. Mover servo a 0 grados (cerrar compuerta)
            self.mover_servo(0)
            
            # 3. Mostrar estado de cierre en LCD
            self.lcd.clear()
            if config.LCD_ROWS >= 4:
                self.lcd.move_to(2, 1)
                self.lcd.putstr("CERRANDO TAPA...")
                self.lcd.move_to(1, 2)
                self.lcd.putstr("REACTIVANDO SISTEMA")
            else:
                self.lcd.move_to(0, 0)
                self.lcd.putstr("CERRANDO TAPA...")
                self.lcd.move_to(0, 1)
                self.lcd.putstr("Reactivando...  ")
            
            # 4. Esperar a que la compuerta cierre físicamente antes de reactivar lecturas
            time.sleep(1.5)
            
            # 5. Desactivar modo mantenimiento y forzar reevaluación inmediata
            self.modo_mantenimiento = False
            self.estado_actual = -1 # Fuerza refresco de estado y sensores

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
        if config.LCD_ROWS >= 4:
            self.lcd.move_to(4, 0)
            self.lcd.putstr("RECICLABLES")
            self.lcd.move_to(0, 1)
            self.lcd.putstr("> Papel y Carton")
            self.lcd.move_to(0, 2)
            self.lcd.putstr("> Plastico y Vidrios")
            self.lcd.move_to(0, 3)
            self.lcd.putstr("> Latas y Metal")
        else:
            self.lcd.move_to(2, 0)
            self.lcd.putstr("RECICLABLES")
            self.lcd.move_to(0, 1)
            self.lcd.putstr("Sistema Listo")

    def mostrar_lleno(self):
        self.lcd.clear()
        if config.LCD_ROWS >= 4:
            self.lcd.move_to(1, 1)
            self.lcd.putstr(" CONTENEDOR LLENO ")
            self.lcd.move_to(0, 2)
            self.lcd.putstr("Dirijase a otro...")
        else:
            self.lcd.move_to(0, 0)
            self.lcd.putstr("CONTENEDOR LLENO")
            self.lcd.move_to(0, 1)
            self.lcd.putstr("Por favor espere")

    def estado_lleno_visual(self):
        self.led_rojo.value(1)
        self.led_verde.value(0)
        self.buzzer.duty(0)

    def estado_normal(self):
        self.led_rojo.value(0)
        self.led_verde.value(1)
        self.buzzer.duty(0)

    def inicializar_sistema(self):
        print("Iniciando componentes...")
        self.mover_servo(0) # Asegurar compuerta cerrada al inicio
        self.led_verde.value(0)
        self.led_rojo.value(0)
        self.mostrar_disponible()
        print("¡Sistema listo para operar!")

    def run(self):
        self.inicializar_sistema()
        print("Calibrando sensor PIR... Espera 30 segundos.")
        time.sleep(30) # Le da tiempo al sensor a estabilizarse

        while True:
            # PRIORIDAD MODO MANTENIMIENTO:
            # Si se ordenó abrir la compuerta, se pausan absolutamente todos los sensores.
            # Los LEDs se mantienen apagados.
            if self.modo_mantenimiento:
                self.led_verde.value(0)
                self.led_rojo.value(0)
                time.sleep(0.2)
                continue

            # Ciclo general normal:
            distancia = self.medir_distancia()
            presencia = self.pir.value()

            # Comprobar si durante la lectura se activó el mantenimiento
            if self.modo_mantenimiento:
                continue

            # --- ESTADO 1: CONTENEDOR LLENO (< 10 cm) ---
            if distancia < config.UMBRAL_LLENO_CM:
                if self.estado_actual != 1:
                    self.estado_lleno_visual()
                    self.mostrar_lleno()
                    self.bt.enviar("1")
                    print("ESTADO: LLENO (Bluetooth: 1)")
                    self.estado_actual = 1

                # Mantener tapa cerrada para usuarios comunes
                if not self.modo_mantenimiento:
                    self.mover_servo(0)

                # Alarma si una persona intenta acercarse cuando está lleno
                # (Solo si no está en modo mantenimiento)
                if presencia == 1 and not self.modo_mantenimiento:
                    print("Aviso sonoro: Persona intentando usar basurero lleno")
                    self.buzzer.freq(1000)
                    self.buzzer.duty(512)
                    time.sleep(0.3)
                    self.buzzer.duty(0)
                    # Pausa no bloqueante con verificación de comando
                    for _ in range(10):
                        if self.modo_mantenimiento:
                            break
                        time.sleep(0.1)

            # --- ESTADO 0: CONTENEDOR DISPONIBLE (>= 10 cm) ---
            else:
                if self.estado_actual != 0:
                    self.estado_normal()
                    self.mostrar_disponible()
                    self.bt.enviar("0")
                    print("ESTADO: DISPONIBLE (Bluetooth: 0)")
                    self.estado_actual = 0

                # Apertura automática por aproximación del usuario
                if presencia == 1 and not self.modo_mantenimiento:
                    print("Usuario detectado - Abriendo tapa automáticamente")
                    self.mover_servo(90)
                    tiempo_abierto = 0
                    while tiempo_abierto < config.TIEMPO_TAPA_ABIERTA_S:
                        if self.modo_mantenimiento:
                            break # Prioridad inmediata
                        time.sleep(0.2)
                        tiempo_abierto += 0.2

                    # Cerrar solo si seguimos en modo automático
                    if not self.modo_mantenimiento:
                        self.mover_servo(0)

            time.sleep(0.2)


if __name__ == "__main__":
    app = BasureroApp()
    app.run()