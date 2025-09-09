import tkinter as tk
import math
import threading
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
from plyer import notification
import keyboard

class PomodoroTimer:
    """Constantes do método pomodoro"""
    WORK_MIN = 25
    SHORT_BREAK_MIN = 5
    LONG_BREAK_MIN = 15

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

        # Timer State
        self.reps = 0
        self.timer = None
        self.paused = False
        self.remaining_time = 0

        # Window State
        self.mini_window = None
        self.drag_start_x = 0
        self.drag_start_y = 0

        self.label = tk.Label(text='Timer', fg=self.GREEN, bg=self.BG_COLOR, font=('Segoe UI', 40, 'bold'))
        self.label.grid(column=1, row=0, columnspan=3, pady=10)

        self.canvas = tk.Canvas(width=200, height=224, bg=self.BG_COLOR, highlightthickness=0)
        self.timer_text = self.canvas.create_text(100, 112, text='00:00', fill=self.FG_COLOR, font=('Segoe UI', 35, 'bold'))
        self.canvas.grid(column=1, row=1, columnspan=3, pady=10)

        # Button Style
        button_font = ('Segoe UI', 12)
        self.button_config = {
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

        self.start_button = tk.Button(text='Iniciar', command=self.start_timer, **self.button_config)
        self.start_button.grid(column=0, row=2, padx=5)

        self.pause_button = tk.Button(text='Pausar', command=self.toggle_pause, state='disabled', **self.button_config)
        self.pause_button.grid(column=1, row=2, padx=5)

        self.reset_button = tk.Button(text='Resetar', command=self.reset_timer, **self.button_config)
        self.reset_button.grid(column=2, row=2, padx=5)

        self.check_marks = tk.Label(fg=self.GREEN, bg=self.BG_COLOR, font=('Segoe UI', 14))
        self.check_marks.grid(column=0, row=3, columnspan=3, pady=10)

        self.mini_mode_button = tk.Button(text="Modo Flutuante", command=self.toggle_mini_mode, **self.button_config)
        self.mini_mode_button.grid(column=0, row=4, columnspan=3, pady=20)

        # System Tray Icon Setup
        image = self.create_image()
        menu = Menu(MenuItem('Show', self.show_window), MenuItem('Quit', self.quit_app))
        self.icon = Icon('Pomodoro', image, "PomoTimer", menu)

        self.master.protocol("WM_DELETE_WINDOW", self.hide_window)
        keyboard.add_hotkey('ctrl + alt + s', self.start_with_hotkey)

    def show_notification(self, title, message):
        notification.notify(title=title, message=message, timeout=5)

    def reset_timer(self):
        if self.timer:
            self.master.after_cancel(self.timer)
        self.start_button.config(state='normal')
        self.pause_button.config(text="Pausar", state='disabled')
        self.update_timer_display("00:00")
        self.label.config(text='Timer', fg=self.GREEN)
        self.check_marks.config(text='')
        self.reps = 0
        self.paused = False
        self.remaining_time = 0
        self.show_notification('Pomodoro Timer', 'Timer foi resetado.')
        if self.mini_window and self.mini_window.winfo_exists():
            self.mini_pause_button.config(text="Pausar", state='disabled')

    def start_timer(self):
        self.start_button.config(state='disabled')
        self.pause_button.config(state='normal')
        if self.mini_window and self.mini_window.winfo_exists():
            self.mini_pause_button.config(state='normal')
        self.paused = False
        self.reps += 1

        if self.reps % 8 == 0:
            self.count_down(self.LONG_BREAK_MIN * 60)
            self.label.config(text='Relax', fg=self.BLUE)
            self.show_notification('Pomodoro Timer', 'Tire um tempo maior para descansar!')
        elif self.reps % 2 == 0:
            self.count_down(self.SHORT_BREAK_MIN * 60)
            self.label.config(text='Relax', fg=self.GREEN)
            self.show_notification('Pomodoro Timer', 'Tire um tempo curto de descanso!')
        else:
            self.count_down(self.WORK_MIN * 60)
            self.label.config(text='Focus', fg=self.RED)
            self.show_notification('Pomodoro Timer', 'Hora de Focar!')

    def toggle_pause(self):
        if self.paused:
            self.paused = False
            text = "Pausar"
            self.count_down(self.remaining_time)
        else:
            self.paused = True
            text = "Continuar"
            self.master.after_cancel(self.timer)

        self.pause_button.config(text=text)
        if self.mini_window and self.mini_window.winfo_exists():
            self.mini_pause_button.config(text=text)

    def count_down(self, count):
        self.remaining_time = count
        count_min = math.floor(count / 60)
        count_sec = count % 60
        if count_sec < 10:
            count_sec = f'0{count_sec}'

        self.update_timer_display(f'{count_min}:{count_sec}')

        if count > 0:
            self.timer = self.master.after(1000, self.count_down, count - 1)
        else:
            self.start_timer()
            marks = '✓' * math.floor(self.reps / 2)
            self.check_marks.config(text=marks)

    def update_timer_display(self, text):
        self.canvas.itemconfig(self.timer_text, text=text)
        if self.mini_window and self.mini_window.winfo_exists():
            self.mini_timer_label.config(text=text)

    def create_image(self):
        image = Image.new('RGB', (64, 64), (255, 255, 255))
        dc = ImageDraw.Draw(image)
        dc.rectangle((16, 16, 48, 48), fill=(0, 128, 0))
        return image

    def hide_window(self):
        self.master.withdraw()
        threading.Thread(target=self.icon.run, daemon=True).start()

    def show_window(self, icon, item):
        self.icon.stop()
        self.master.deiconify()
        if self.mini_window and self.mini_window.winfo_exists():
            self.destroy_mini_mode_window()

    def quit_app(self, icon, item):
        self.icon.stop()
        if self.timer:
            self.master.after_cancel(self.timer)
        keyboard.remove_hotkey('ctrl + alt + s')
        self.master.destroy()

    def toggle_mini_mode(self):
        if self.mini_window and self.mini_window.winfo_exists():
            self.destroy_mini_mode_window()
        else:
            self.create_mini_mode_window()

    def create_mini_mode_window(self):
        self.master.withdraw()
        self.mini_window = tk.Toplevel(self.master)
        self.mini_window.overrideredirect(True)
        self.mini_window.attributes('-topmost', True)

        content_frame = tk.Frame(self.mini_window, bg=self.BG_COLOR, padx=10, pady=5)
        content_frame.pack()

        self.mini_timer_label = tk.Label(content_frame, text="00:00", bg=self.BG_COLOR, fg=self.FG_COLOR, font=('Segoe UI', 20, 'bold'))
        self.mini_timer_label.pack(side='left', padx=5)

        mini_button_config = self.button_config.copy()
        mini_button_config['width'] = 8
        mini_button_config['pady'] = 2

        self.mini_pause_button = tk.Button(content_frame, text="Pausar", command=self.toggle_pause, **mini_button_config)
        self.mini_pause_button.pack(side='left', padx=5)
        if self.start_button['state'] == 'disabled':
            self.mini_pause_button.config(state='normal', text="Continuar" if self.paused else "Pausar")
        else:
            self.mini_pause_button.config(state='disabled')

        tk.Button(content_frame, text="Restaurar", command=self.destroy_mini_mode_window, **mini_button_config).pack(side='left', padx=5)

        # Update display and position
        self.update_timer_display(self.canvas.itemcget(self.timer_text, 'text'))
        self.mini_window.geometry(f"+{self.master.winfo_x()}+{self.master.winfo_y()}")

        # Drag functionality
        content_frame.bind("<ButtonPress-1>", self.start_move)
        content_frame.bind("<B1-Motion>", self.on_motion)

    def destroy_mini_mode_window(self):
        if self.mini_window and self.mini_window.winfo_exists():
            self.mini_window.destroy()
        self.mini_window = None
        self.master.deiconify()

    def start_move(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_motion(self, event):
        deltax = event.x - self.drag_start_x
        deltay = event.y - self.drag_start_y
        x = self.mini_window.winfo_x() + deltax
        y = self.mini_window.winfo_y() + deltay
        self.mini_window.geometry(f"+{x}+{y}")

    def start_with_hotkey(self):
        if self.start_button['state'] == 'normal':
            self.show_notification('Pomodoro Timer', 'Started via Hotkey!!')
            self.start_timer()

def main():
    window = tk.Tk()
    app = PomodoroTimer(window)
    window.mainloop()

if __name__ == "__main__":
    main()
