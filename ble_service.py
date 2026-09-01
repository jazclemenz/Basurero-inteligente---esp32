import ubluetooth
import config

class BasureroBLE:
    def __init__(self, name=config.DEVICE_NAME):
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.ble.config(gap_name=name)
        
        # Servicio UART BLE SPP
        uart_service = (
            config.UART_SERVICE_UUID, 
            ((config.UART_TX_UUID, ubluetooth.FLAG_NOTIFY),)
        )
        ((self.tx,),) = self.ble.gatts_register_services((uart_service,))
        self.anunciar()

    def anunciar(self):
        name = self.ble.config('gap_name')
        payload = bytearray(b'\x02\x01\x06') + bytearray((len(name) + 1, 0x09)) + name
        self.ble.gap_advertise(100, payload)

    def enviar(self, dato):
        try:
            # Notifica el dato codificado en UTF-8 con salto de línea
            self.ble.gatts_notify(0, self.tx, (str(dato) + "\n").encode('utf-8'))
        except Exception:
            pass