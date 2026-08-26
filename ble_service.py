import ubluetooth
import config 

_UART_UUID = ubluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    ubluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    ubluetooth.FLAG_READ | ubluetooth.FLAG_NOTIFY,
)
_UART_RX = (
    ubluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    ubluetooth.FLAG_WRITE,
)
_UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX),)


class BasureroBLE:
    def __init__(self, name="Basurero_UNRaf"):
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self._irq)

        self.conn_handle = None
        self.comando_recibido = None

        self._setup_services()
        self._start_advertising(name)

    def _setup_services(self):
        handles = self.ble.gatts_register_services((_UART_SERVICE,))
        ((self.handle_tx, self.handle_rx),) = handles

    def _start_advertising(self, name="Sistema_de_gestion_de_residuos"):
        payload = bytearray(b"\x02\x01\x06")
        payload += bytearray((len(name) + 1, 0x09)) + bytearray(name, "utf-8")
        self.ble.gap_advertise(100000, payload)

    def enviar_nivel(self, distancia):
        """Envía el valor medido por el sensor ultrasónico al celular."""
        if self.conn_handle is not None:
            try:
                mensaje = f"{int(distancia)} cm"
                self.ble.gatts_notify(self.conn_handle, self.handle_tx, mensaje.encode("utf-8"))
                return True
            except:
                pass
        return False

    def _irq(self, event, data):
        if event == 1:  
            self.conn_handle, _, _ = data
            print("App conectada por Bluetooth")

        elif event == 2:  
            self.conn_handle = None
            print("App desconectada")
            self._start_advertising()

        elif event == 3:  
            conn_handle, value_handle = data
            if value_handle == self.handle_rx:
                dato = self.ble.gatts_read(self.handle_rx)
                self.comando_recibido = dato.decode("utf-8").strip()