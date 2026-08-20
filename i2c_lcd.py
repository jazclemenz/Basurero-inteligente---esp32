from lcd_api import LcdApi
import time

LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00
LCD_FIRST_ROW = 0x80
LCD_SECOND_ROW = 0xC0
LCD_ENABLE_BIT = 0x04
LCD_READ_WRITE = 0x02
LCD_REGISTER_SELECT = 0x01

class I2cLcd(LcdApi):
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.i2c.writeto(self.i2c_addr, b'\x00')
        time.sleep_ms(20)
  
        self.hal_write_init_nibble(0x30)
        time.sleep_ms(5)
        self.hal_write_init_nibble(0x30)
        time.sleep_ms(1)
        self.hal_write_init_nibble(0x30)
        time.sleep_ms(1)
        self.hal_write_init_nibble(0x20)
        time.sleep_ms(1)
        
        super().__init__(num_lines, num_columns)
        
        cmd = LcdApi.LCD_FUNCTIONSET | 0x08  
        if num_lines > 1:
            cmd |= 0x08
        self.hal_write_command(cmd)
        
        cmd = LcdApi.LCD_DISPLAYCONTROL | LcdApi.LCD_DISPLAYON | LcdApi.LCD_CURSOROFF | LcdApi.LCD_BLINKOFF
        self.hal_write_command(cmd)
        self.hal_write_command(LcdApi.LCD_CLEARDISPLAY)
        self.hal_write_command(LcdApi.LCD_ENTRYMODESET | LcdApi.LCD_ENTRYLEFT | LcdApi.LCD_ENTRYSHIFTDECREMENT)
        self.backlight = True

    def hal_write_init_nibble(self, nibble):
        byte = (nibble & 0xF0) | LCD_BACKLIGHT | LCD_ENABLE_BIT
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        time.sleep_us(1)
        self.i2c.writeto(self.i2c_addr, bytes([byte & ~LCD_ENABLE_BIT]))
        time.sleep_us(50)

    def hal_write_command(self, cmd):
        byte = ((cmd >> 4) & 0xF0) | LCD_BACKLIGHT | LCD_ENABLE_BIT
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        time.sleep_us(1)
        self.i2c.writeto(self.i2c_addr, bytes([byte & ~LCD_ENABLE_BIT]))
        time.sleep_us(50)
        
        byte = (cmd & 0xF0) | LCD_BACKLIGHT | LCD_ENABLE_BIT
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        time.sleep_us(1)
        self.i2c.writeto(self.i2c_addr, bytes([byte & ~LCD_ENABLE_BIT]))
        time.sleep_us(50)

    def hal_write_data(self, data):
        byte = ((data >> 4) & 0xF0) | LCD_BACKLIGHT | LCD_REGISTER_SELECT | LCD_ENABLE_BIT
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        time.sleep_us(1)
        self.i2c.writeto(self.i2c_addr, bytes([byte & ~LCD_ENABLE_BIT]))
        time.sleep_us(50)
        
        byte = (data & 0xF0) | LCD_BACKLIGHT | LCD_REGISTER_SELECT | LCD_ENABLE_BIT
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        time.sleep_us(1)
        self.i2c.writeto(self.i2c_addr, bytes([byte & ~LCD_ENABLE_BIT]))
        time.sleep_us(50)

    def impl_clear(self):
        self.hal_write_command(LcdApi.LCD_CLEARDISPLAY)
        time.sleep_ms(2)

    def impl_home(self):
        self.hal_write_command(LcdApi.LCD_RETURNHOME)
        time.sleep_ms(2)

    def impl_set_cursor(self, col, row):
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row >= self.num_lines:
            row = self.num_lines - 1
        self.hal_write_command(LcdApi.LCD_SETDDRAMADDR | (col + row_offsets[row]))

    def impl_write_char(self, char_val):
        self.hal_write_data(char_val)

    def hal_sleep_ms(self, ms):
        time.sleep_ms(ms)