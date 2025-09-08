import tkinter as tk
from tkinter import messagebox
import math
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
from plyer import notification
import keyboard

class PomodoroTimer:
    """Constantes do método pomodoro"""
    WORK_MIN = 25
    SHORT_BREAK_MIN = 5
    LONG_BRAKE_MIN = 15

    def __init__(self, master):
        self.master = master
        self.master.title('PomoTimer 🍅')

        # Colors
        self.BG_COLOR = "#2b2b2b"
        self.FG_COLOR = "#dcdcdc"
        self.RED = "#e57373"
        self.GREEN = "#81c784"
        self.BLUE = "#64b5f6"
        self.BUTTON_BG = "#3c3f41"

        self.master.config(padx=100, pady=50, bg=self.BG_COLOR)

        self.reps = 0
        self.timer = None

        self.label = tk.Label(text='Timer', fg=self.GREEN, bg=self.BG_COLOR, font=('Segoe UI', 40, 'bold'))
        self.label.grid(column=1, row=0, pady=10)

        self.canvas = tk.Canvas(width=200, height=224, bg=self.BG_COLOR, highlightthickness=0)
        self.timer_text = self.canvas.create_text(100, 112, text='00:00', fill=self.FG_COLOR, font=('Segoe UI', 35, 'bold'))
        self.canvas.grid(column=1, row=1, pady=10)

        # Button Style
        button_font = ('Segoe UI', 12)
        button_config = {
            "font": button_font,
            "bg": self.BUTTON_BG,
            "fg": self.FG_COLOR,
            "relief": "flat",
            "borderwidth": 0,
            "activebackground": "#4e5254",
            "activeforeground": self.FG_COLOR,
            "width": 10,
            "pady": 5
        }

        self.start_buttom = tk.Button(text='Iniciar', command=self.start_timer, **button_config)
        self.start_buttom.grid(column=0, row=2, padx=10)

        self.reset_buttom = tk.Button(text='Resetar', command=self.reset_timer, **button_config)
        self.reset_buttom.grid(column=2, row=2, padx=10)

        self.check_marks = tk.Label(fg=self.GREEN, bg=self.BG_COLOR, font=('Segoe UI', 14))
        self.check_marks.grid(column=1, row=3, pady=20)

        keyboard.add_hotkey('ctrl + alt + s', self.start_with_hotkey)

        self.master.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

    """Funcao para notificacao do desktop"""
    def show_notification(self, title, message):
        notification.notify(
            title=title,
            message=message,
            timeout=5  # Mensagem aparecera por 5 segundos
        )

    """"Função para resetar o timer"""
    def reset_timer(self):
        if self.timer:
            self.master.after_cancel(self.timer)
        self.canvas.itemconfig(self.timer_text, text='00:00')
        self.label.config(text='Temporizador')
        self.check_marks.config(text='')
        self.reps = 0
        self.show_notification('Pomodoro Timer', 'Timer foi resetado.')

    """Iniciar o timer"""
    def start_timer(self):
        self.reps += 1
        work_sec = self.WORK_MIN * 60
        short_break_sec = self.SHORT_BREAK_MIN * 60
        long_break_sec = self.LONG_BRAKE_MIN * 60

        if self.reps % 8 == 0:
            self.count_down(long_break_sec)
            self.label.config(text='Relax', fg=self.BLUE)
            self.show_notification('Pomodoro Timer', 'Tire um tempo maior para descansar!')
        elif self.reps % 2 == 0:
            self.count_down(short_break_sec)
            self.label.config(text='Relax', fg=self.GREEN)
            self.show_notification('Pomodoro Timer', 'Tire um tempo curto de descanso!')
        else:
            self.count_down(work_sec)
            self.label.config(text='Focus', fg=self.RED)
            self.show_notification('Pomodoro Timer', 'Hora de Focar!')

    """Contagem regressiva"""
    def count_down(self, count):
        count_min = math.floor(count / 60)
        count_sec = count % 60
        if count_sec < 10:
            count_sec = f'0{count_sec}'
        else:
            count_sec = str(count_sec)

        self.canvas.itemconfig(self.timer_text, text=f'{count_min}:{count_sec}')

        if count > 0:
            self.timer = self.master.after(1000, self.count_down, count - 1)
        else:
            self.start_timer()
            marks = ''
            work_sessions = math.floor(self.reps / 2)
            for _ in range(work_sessions):
                marks += '✓'
            self.check_marks.config(text=marks)

    """Funcoes de Sistema"""
    def create_image(self):
        image = Image.new('RGB', (64, 64), (255, 255, 255))
        dc = ImageDraw.Draw(image)
        dc.rectangle((16, 16, 48, 48), fill=(0, 128, 0))
        return image

    def show_app(self, icon, item):
        icon.stop()
        self.master.after(0, self.master.deiconify)  # Amostra a janela principal

    def quit_app(self, icon, item):
        icon.stop()
        self.master.quit()

    def minimize_to_tray(self):
        self.master.withdraw()  # esconde a janela
        icon = Icon('Pomodoro', self.create_image(), menu=Menu(
            MenuItem('Show', self.show_app),
            MenuItem('Quit', self.quit_app)
        ))
        icon.run()

    """Funcoes de atalho de teclado"""
    def start_with_hotkey(self):
        self.show_notification('Pomodoro Timer', 'Started via Hotkey!!')
        self.start_timer()

def main():
    window = tk.Tk()
    app = PomodoroTimer(window)
    window.mainloop()

if __name__ == "__main__":
    main()
