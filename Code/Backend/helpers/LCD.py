from RPi import GPIO
from time import sleep

class LCD():
    def __init__(self, par_GPIO_arr, par_rs, par_e):
        self.GPIO_arr = par_GPIO_arr
        self.rs = par_rs
        self.e = par_e
        self.delay = 0.05

        self._init_LCD()

    def _set_data_bits(self, value):
        mask = 0b10000000
        # for loop die value bit per bit overloopt en waarde naar datalijn stuurt
        for i in range(0, len(self.GPIO_arr)):
            if (value & (mask >> i)) == 0:
                GPIO.output(self.GPIO_arr[i], GPIO.LOW)
            else:
                GPIO.output(self.GPIO_arr[i], GPIO.HIGH)
    
    def _send_instruction(self, value):
        # zet rs lijn op correcte niveau en maak klokpuls met e lijn, roept ook set_data_bits(value) aan
        # rs laag
        GPIO.output(self.rs, GPIO.LOW)
        # e hoog
        GPIO.output(self.e, GPIO.HIGH)
        # data klaarzetten
        self._set_data_bits(value)
        # e laag + delay
        sleep(self.delay)
        GPIO.output(self.e, GPIO.LOW)
        sleep(self.delay)

    def _send_character(self, value):
        # rs hoog
        GPIO.output(self.rs, GPIO.HIGH)
        # e hoog
        GPIO.output(self.e, GPIO.HIGH)
        # data klaarzetten
        self._set_data_bits(value)
        # e laag + delay
        GPIO.output(self.e, GPIO.LOW)
        sleep(self.delay)

    def write_message(self, message):
        for char_index in range(0, len(message)):
            char = ord(message[char_index])
            self._send_character(char)
            if char_index == 15:
                self._send_instruction(0b10101000)

    def _init_LCD(self):
        # function set
        self._send_instruction(0b00111000) #db5 hoog herkent functie, 8bit: 1, 2lijen: 1, 5x7: 0, 2x om het even wat
        # display on
        self._send_instruction(0b00001100) #db4 hoog herkent functie, display aan: 1, cursor aan: 1, cursor blinking: 1
        # clear display & cursor home
        self._send_instruction(0b00000001)

    def change_cursor_position(self, bitwaarde):
        self._send_instruction(bitwaarde)

    def clear_LCD(self):
        # clear display & cursor home
        self._send_instruction(0b00000001)

    @property
    def GPIO_arr(self):
        return self._GPIO_arr
    @GPIO_arr.setter
    def GPIO_arr(self, value):
        self._GPIO_arr = value

    @property
    def rs(self):
        return self._rs
    @rs.setter
    def rs(self, value):
        self._rs = value

    @property
    def e(self):
        return self._e
    @e.setter
    def e(self, value):
        self._e = value