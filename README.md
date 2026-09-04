# 🗑️ Basurero Inteligente con ESP32 (Smart Trash Can)

Este proyecto consiste en un contenedor de residuos automatizado desarrollado con un microcontrolador ESP32, sensores de proximidad y nivel, y control inalámbrico vía Bluetooth.

## ⚙️ Especificación y Arquitectura del Software

El firmware de este proyecto fue desarrollado en **MicroPython** aplicando el paradigma de **Programación Orientada a Objetos (POO)**. Esta decisión de diseño permitió construir un sistema altamente modular, limpio y escalable, dividiendo las responsabilidades en distintos archivos y clases:

* **Clase `BasureroApp` (`main.py`):** Es el orquestador principal del sistema. Encapsula los periféricos de hardware (sensores PIR y HC-SR04, servomotor, LEDs, buzzer) como atributos del objeto y coordina la lógica de control a través de un bucle cooperativo y no bloqueante.
* **Clase `BasureroBLE` (`ble_service.py`):** Abstrae toda la complejidad de la conexión inalámbrica Bluetooth Low Energy (BLE) y el perfil GATT. Se encarga de notificar la telemetría (nivel de llenado) y recibir los comandos asíncronos desde la aplicación móvil.
* **Módulos de Configuración e Interfaz (`config.py`, `i2c_lcd.py`):** Aíslan el mapeo de pines, las constantes de temporización y el control de bajo nivel del display I2C.

Gracias a la POO, el sistema evita los retardos que bloquean el procesador y logra que el basurero interactúe en tiempo real tanto con el entorno físico como con la aplicación móvil.

## 🛠️ Materiales Utilizados
* Microcontrolador ESP32
* Sensor Infrarrojo PIR (Detección de presencia)
* Sensor Ultrasónico HC-SR04 (Medición de nivel)
* Servomotor SG90
* Pantalla LCD 16x2 I2C
* LEDs y Buzzer

## 📱 Aplicación Móvil
El proyecto incluye una aplicación desarrollada en MIT App Inventor que se conecta vía Bluetooth Low Energy (BLE) para recibir alertas de llenado y abrir la compuerta de forma remota.
