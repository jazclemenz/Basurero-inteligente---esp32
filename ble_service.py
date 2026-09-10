import ubluetooth
import config

class BasureroBLE:
    # Se añade callback_comando para recibir la función desde main.py
    def __init__(self, callback_comando= None, name=config.DEVICE_NAME):
        self.conn_handle = None
        self.callback = callback_comando
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.ble.config(gap_name=name)

        # 1. Configurar la interrupción (IRQ) para escuchar eventos BLE
        self.ble.irq(self.ble_irq)

        # 2. Definir el Servicio y DOS características (TX para notificar, RX para escribir)
        uart_service = (
            ubluetooth.UUID(config.UART_SERVICE_UUID), 
            (
                (ubluetooth.UUID(config.UART_TX_UUID), ubluetooth.FLAG_NOTIFY),
                (ubluetooth.UUID(config.UART_RX_UUID), ubluetooth.FLAG_WRITE | ubluetooth.FLAG_WRITE_NO_RESPONSE),
            )
        )
        
        # Registrar servicios y guardar los "handles" (identificadores) de tx y rx
        ((self.tx, self.rx,),) = self.ble.gatts_register_services((uart_service,))
        self.anunciar()

    def ble_irq(self, event, data):
        # 1 = _IRQ_CENTRAL_CONNECT
        if event == 1:
            conn_handle, _, _ = data
            self.conn_handle = conn_handle
            print("BLE: Dispositivo conectado")
        # 2 = _IRQ_CENTRAL_DISCONNECT
        elif event == 2:
            self.conn_handle = None
            print("BLE: Dispositivo desconectado. Reanunciando...")
            self.anunciar()
        # 3 = _IRQ_GATTS_WRITE (alguien escribió en nuestra característica RX)
        elif event == 3:
            conn_handle, value_handle = data
            if value_handle == self.rx:
                raw_data = self.ble.gatts_read(self.rx)
                msg = raw_data.replace(b'\x00', b'').decode('utf-8').strip()
                if self.callback:
                    self.callback(msg)

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