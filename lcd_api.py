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