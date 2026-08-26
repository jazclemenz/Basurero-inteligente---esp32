<<<<<<< HEAD
import time
class LcdApi:
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00

    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5X10DOTS = 0x04
    LCD_5X8DOTS = 0x00

    def __init__(self, num_lines, num_columns):
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.cursor_x = 0
        self.cursor_y = 0
        self.completed_init = False

    def clear(self):
        self.hal_write_command(self.LCD_CLEARDISPLAY)
        time.sleep_ms(2) 
        self.set_cursor(0, 0)

    def home(self):
        self.hal_write_command(self.LCD_RETURNHOME)
        self.hal_sleep_ms(2)

    def show_cursor(self, status):
        if status:
            self.display_control |= self.LCD_CURSORON
        else:
            self.display_control &= ~self.LCD_CURSORON
        self.hal_write_command(self.LCD_DISPLAYCONTROL | self.display_control)

    def blink_cursor_on(self, status):
        if status:
            self.display_control |= self.LCD_BLINKON
        else:
            self.display_control &= ~self.LCD_BLINKON
        self.hal_write_command(self.LCD_DISPLAYCONTROL | self.display_control)

    def display_on(self):
        self.display_control |= self.LCD_DISPLAYON
        self.hal_write_command(self.LCD_DISPLAYCONTROL | self.display_control)

    def display_off(self):
        self.display_control &= ~self.LCD_DISPLAYON
        self.hal_write_command(self.LCD_DISPLAYCONTROL | self.display_control)

    def putstr(self, string):
        for char in string:
            self.putchar(char)

    def putchar(self, char):
        if char == '\n':
            self.cursor_x = 0
            self.cursor_y += 1
            if self.cursor_y >= self.num_lines:
                self.cursor_y = 0
            self.set_cursor(self.cursor_x, self.cursor_y)
        else:
            self.hal_write_data(ord(char))
            self.cursor_x += 1
            if self.cursor_x >= self.num_columns:
                self.cursor_x = 0
                self.cursor_y += 1
                if self.cursor_y >= self.num_lines:
                    self.cursor_y = 0
                self.set_cursor(self.cursor_x, self.cursor_y)

    def set_cursor(self, col, row):
        if col < 0:
            self.cursor_x = 0
        elif col >= self.num_columns:
            self.cursor_x = self.num_columns - 1
        else:
            self.cursor_x = col

        if row < 0:
            self.cursor_y = 0
        elif row >= self.num_lines:
            self.cursor_y = self.num_lines - 1
        else:
            self.cursor_y = row
            
        addr = [0x00, 0x40, 0x14, 0x54][self.cursor_y] + self.cursor_x
        self.hal_write_command(self.LCD_SETDDRAMADDR | addr)
=======
class LcdApi:
    lcd_-supported_commands = [
    ]
    
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    def __init__(self, num_lines, num_columns):
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.cursor_x = 0
        self.cursor_y = 0
        self.impl_clear()
        self.impl_home()

    def clear(self):
        self.impl_clear()
        self.cursor_x = 0
        self.cursor_y = 0

    def home(self):
        self.impl_home()
        self.cursor_x = 0
        self.cursor_y = 0

    def set_cursor(self, col, row):
        if row >= self.num_lines:
            row = self.num_lines - 1
        self.cursor_x = col
        self.cursor_y = row
        self.impl_set_cursor(col, row)

    def putchar(self, char):
        if char == '\n':
            self.cursor_y += 1
            if self.cursor_y >= self.num_lines:
                self.cursor_y = 0
            self.cursor_x = 0
            self.set_cursor(self.cursor_x, self.cursor_y)
        else:
            self.impl_write_char(ord(char))
            self.cursor_x += 1
            if self.cursor_x >= self.num_columns:
                self.cursor_x = 0
                self.cursor_y += 1
                if self.cursor_y >= self.num_lines:
                    self.cursor_y = 0
                self.set_cursor(self.cursor_x, self.cursor_y)

    def putstr(self, string):
        for char in string:
            self.putchar(char)
>>>>>>> 9b8f607a7863d00cfd8dfe210091a972d88cc6bf
