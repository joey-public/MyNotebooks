import sys

PURPLE = '\033[1;35;48m'
CYAN = '\033[1;36;48m'
BOLD = '\033[1;37;48m'
BLUE = '\033[1;34;48m'
GREEN = '\033[1;32;48m'
YELLOW = '\033[1;33;48m'
RED = '\033[1;31;48m'
BLACK = '\033[1;30;48m'
UNDERLINE = '\033[4;37;48m'
END = '\033[1;37;0m'
colors = {
        'purple':PURPLE,
        'cyan':CYAN,
        'bold':BOLD,
        'blue':BLUE,
        'green':GREEN,
        'yellow':YELLOW,
        'red':RED,
        'black':BLACK,
        'underline':UNDERLINE,
}
def color_str(input_str, color):
    if not(color in colors.keys()): return input_str
    return colors[color]+input_str+END

def pad_str(input_str, new_len, symbol=' ', align='l'):
    str_len = len(input_str)
    for color in colors:
        if colors[color] in input_str:
            str_len -= len(colors[color])
    buf_count = new_len-str_len
    if buf_count<=0: return input_str
    if align == 'l':#add buffer to end of input_str
        for i in range(buf_count):
            input_str += symbol
    elif align == 'r':#add buffer to beginning of input_str
        temp = ''
        for i in range(buf_count):
            temp += symbol
        input_str = temp + input_str
    elif align == 'c':#center input_str with symbol on both sides
        rbuf = buf_count // 2
        lbuf = buf_count-rbuf 
        temp = ''
        for i in range(lbuf): input_str += symbol
        for i in range(rbuf): temp += symbol
        input_str = temp + input_str
    else:
        print('invalid align')
    return input_str
def delete_lines(n=1):
    for i in range(n):
        _delete_last_line()
def delete_printed_str(i_str:str):
    n = len(i_str.split('\n'))
    delete_lines(n)
#https://stackoverflow.com/questions/19596750/is-there-a-way-to-clear-your-printed-text-in-python
def _delete_last_line():
    #cursor up one line
    sys.stdout.write('\x1b[1A')
    #delete last line
    sys.stdout.write('\x1b[2K')
