import tkinter as tk
from tkinter import messagebox
import time
import math
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
from plyer import notification
import keyboard

"""Constantes do método pomodoro"""

WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BRAKE_MIN = 15
reps = 0
timer = None

"""Funcao para notificacao do desktop"""
def show_notification(title, message):
    notification.notify(
        title = title,
        message = message,
        timeout = 5 #Mensagem aparecera por 5 segundos
        )
    

""""Função para resetar o timer"""

def reset_timer():
    window.after_cancel(timer)
    canvas.itemconfig(timer_text, text= '00:00')
    label.config(text= 'Temporizador')
    check_marks.config(text= '')
    global reps
    reps = 0
    show_notification('Pomodoro Timer', 'Timer precisa ser Resetado')


"""Iniciar o timer"""

def start_timer():
    global reps
    reps += 1

    work_sec = WORK_MIN * 60
    short_break_sec = SHORT_BREAK_MIN * 60
    long_break_sec = LONG_BRAKE_MIN * 60

    if reps % 8 == 0:
        count_down(long_break_sec)
        label.config(text= 'Relax', fg= 'blue')
        show_notification('Pomodoro Timer', 'Tire um tempo maior para descansar!')
    elif reps % 2 == 0:
        count_down(short_break_sec)
        label.config(text= 'Relax', fg= 'white-blue')
        show_notification('Pomodoro Timer', 'Tire um tempo curto de descanso!')
    else:
        count_down(work_sec)
        label.config(text= 'Focus', fg= 'red')
        show_notification('Pomodoro Timer', 'Hora de Focar!')

"""Contagem regressiva"""

def count_down(count):
    count_min = math.floor(count / 60)
    count_sec = count % 60
    if count_sec < 10:
        count_sec = f'0{count_sec}'
    else:
        count_sec = str(count_sec)
    
    canvas.itemconfig(timer_text, text= f'{count_min}:{count_sec}')

    if count > 0:
        global timer
        timer = window.after(1000, count_down, count - 1)
    else:
        start_timer()
        marks = ''
        work_sessions = math.floor(reps / 2)
        for _ in range(work_sessions):
            marks += '✓'
        check_marks.config(text=marks)

"""Funcoes de Sistema"""

def create_image():
    image = Image.new('RGB', (64, 64), (255, 255, 255))
    dc = ImageDraw.Draw(image)
    dc.rectangle((16, 16, 48, 48), fill=(0, 128, 0))
    return image

def show_app(icon, item):
    icon.stop()
    window.after(0, window.deiconify) #Amostra a janela principal

def quit_app(icon, item):
    icon.stop()
    window.quit()

def minimize_to_tray():
    window.withdraw() #esconde a janela
    icon = Icon('Pomodoro', create_image(), menu= Menu(
        MenuItem('Show', show_app),
        MenuItem('Quit', quit_app)
    ))
    icon.run()

"""Funcoes de atalho de teclado"""

def start_with_hotkey():
    show_notification('Pomodoro Timer', 'Started via Hotkey!!')
    start_timer()




"""Configuracao de UI"""

window = tk.Tk()
window.title = 'PomoTimer 🍅'
window.config(padx=100, pady=50, bg='#f7f5dd')

window.iconbitmap('Tomato.ico')

label = tk.Label(text='Timer', fg='green', bg='#f7f5dd', font=('Courier', 50))
label.grid(column=1, row=0)

canvas = tk.Canvas(width=200, height=224, bg='#f7f5dd', highlightthickness=0)
timer_text = canvas.create_text(100, 130, text='00:00', fill='black', font=('Courier', 35, 'bold'))
canvas.grid(column=1, row=1)

start_buttom = tk.Button(text= 'Iniciar', command= start_timer, highlightthickness=0)
start_buttom.grid(column=0, row=2)

reset_buttom = tk.Button(text='Resetar', command=reset_timer, highlightthickness=0)
reset_buttom.grid(column=2, row=2)

check_marks = tk.Label(fg='green', bg='#f7f5dd')
check_marks.grid(column=1, row=3)

"""Liga o programa usando ctrl + alt + s"""
keyboard.add_hotkey('ctrl + alt + s', start_with_hotkey)

window.mainloop()
