import spidev

class Mcp():
    def __init__(self, par_bus = 0, par_device = 0):
        # variabelen
        self.bus = par_bus
        self.device = par_device

        # openen + instellingen connectie
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 1350000

    def read_channel(self, ch):
        # opstellen commando_byte
        ch = (int(bin(ch),2) << 4) | 0b10000000
        commando_byte = [0b00000001, ch, 0b00000000]
        
        # commando wordt verstuurd, de teruggegeven byte worden opgeslaan in list_bytes
        list_bytes = self.spi.xfer(commando_byte)

        byte1 = list_bytes[1]
        byte2 = list_bytes[2]
        result = ((byte1 & 0b00000011)<< 8) | byte2
        return result

    def closespi(self):
        # sluit connectie
        self.spi.close()

    @property
    def bus(self):
        return self._bus
    @bus.setter
    def bus(self, value):
        self._bus = value
        
    @property
    def device(self):
        return self._device
    @device.setter
    def device(self, value):
        self._device = value