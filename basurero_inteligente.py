from machine import Pin, PWM, I2C
import time

pin_pir = 23
pir = Pin(pin_pir, Pin.IN)

pin_servo = 18
servo = PWM(Pin(pin_servo), freq=50)  

led_verde = Pin(4, Pin.OUT)   
led_rojo = Pin(5, Pin.OUT)    

pin_buzzer = 19
buzzer = Pin(pin_buzzer, Pin.OUT)

trig = Pin(32, Pin.OUT)
echo = Pin(33, Pin.IN)

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)


from lcd_api import LcdApi
from i2c_lcd import I2cLcd

I2C_ADDR = 0x27  # Dirección I2C común (puede ser 0x3F)
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)


def mover_servo(angulo):
    """Convierte el ángulo en un ciclo de trabajo PWM para el servo."""
    ancho_pulso = int(40 + (angulo / 180) * 75)
    servo.duty(ancho_pulso)


def sonar_buzzer(veces, duracion):
    """Función auxiliar para hacer sonar el buzzer."""
    for _ in range(veces):
        buzzer.value(1)
        time.sleep(duracion)
        buzzer.value(0)
        time.sleep(duracion)


def medir_distancia():
    """Mide la distancia en centímetros usando el sensor HC-SR04."""
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    
    inicio = time.ticks_us()
    fin = time.ticks_us()
    
    while echo.value() == 0:
        inicio = time.ticks_us()
    while echo.value() == 1:
        fin = time.ticks_us()
        
    duracion = time.ticks_diff(fin, inicio)
    distancia = (duracion * 0.0343) / 2
    return distancia


def inicializar_sistema():
    print("Iniciando sistema de Basurero Inteligente")
    lcd.clear()
    lcd.putstr("Iniciando...")
    
    mover_servo(0)          
    led_verde.value(1)    
    led_rojo.value(0)    
    buzzer.value(0)
    
    time.sleep(1)
    lcd.clear()
    lcd.putstr("Sistema Listo\nEsperando...")


inicializar_sistema()
print("Sistema en ejecución. Esperando presencia")

try:
    while True:
        # Medimos distancia con el HC-SR04 (ej: abre si hay algo a menos de 20 cm)
        # O puedes mantener el PIR: if pir.value() == 1:
        distancia = medir_distancia()
        
        if distancia < 20 or pir.value() == 1:
            print("¡Movimiento/Objeto detectado! Abriendo compuerta")
            
            lcd.clear()
            lcd.putstr("Abriendo...\nDeposite residuo")
            
            led_verde.value(0)
            led_rojo.value(1)
            
            # Alerta sonora corta al abrir
            sonar_buzzer(1, 0.1)
            
            mover_servo(90)
            
            time.sleep(4)
            
            print("Cerrando compuerta")
            lcd.clear()
            lcd.putstr("Cerrando...")
            
            mover_servo(0)
            
            led_rojo.value(0)
            led_verde.value(1)
            
            sonar_buzzer(2, 0.1) # Doble pitido al cerrar
            
            print("Sistema listo nuevamente.\n")
            lcd.clear()
            lcd.putstr("Sistema Listo\nEsperando...")
            
            time.sleep(1)
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Programa detenido por el usuario.")
    lcd.clear()
    lcd.putstr("Sistema detenido")
    servo.deinit()
    led_verde.value(0)
    led_rojo.value(0)
    buzzer.value(0)