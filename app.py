import cv2
import pyautogui
import numpy as np
import os
import threading
import time
from screeninfo import get_monitors
from tkinter import Tk, Button, Label, messagebox
from tkinter.ttk import Combobox

# Variables globales
recording = False
paused = False
out = None
start_time = None  # Para llevar el control del tiempo de grabación

# Función para generar el nombre del archivo con formato gs_XX
def get_output_filename():
    base_name = "gs_"
    extension = ".mp4"
    i = 0
    while True:
        file_name = f"{base_name}{i:02d}{extension}"
        if not os.path.exists(file_name):
            return file_name
        i += 1

# Función para mostrar el tiempo transcurrido
def update_timer():
    global start_time
    if recording:
        elapsed_time = time.time() - start_time
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        timer_label.config(text=f"Tiempo: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
        timer_label.after(1000, update_timer)  # Actualiza cada segundo

# Función para empezar a grabar
def start_recording(monitor):
    global out, recording, paused, start_time

    screen_size = (monitor.width, monitor.height)
    fps = 10.0
    output = get_output_filename()

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Cambiar a 'mp4v' para mayor compatibilidad
    out = cv2.VideoWriter(output, fourcc, fps, screen_size)

    recording = True
    paused = False
    start_time = time.time()  # Establecer el tiempo de inicio
    update_timer()  # Iniciar el contador
    print(f"Grabando pantalla del monitor {monitor.x}, {monitor.y}... Guardando como {output}. Presiona Ctrl+C para detener.")

    last_time = time.time()
    while recording:
        if not paused:
            img = pyautogui.screenshot(region=(monitor.x, monitor.y, monitor.width, monitor.height))
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out.write(frame)

            # Controlar la frecuencia de captura de imágenes
            current_time = time.time()
            elapsed = current_time - last_time
            if elapsed < (1 / fps):
                time.sleep((1 / fps) - elapsed)  # Duerme el tiempo restante
            last_time = time.time()  # Actualiza el último tiempo de captura

# Función para detener la grabación
def stop_recording():
    global recording
    if recording:
        recording = False
        out.release()
        cv2.destroyAllWindows()
        messagebox.showinfo("Grabación", "Grabación finalizada.")

# Función que inicia la grabación en un hilo separado
def start_recording_thread():
    monitor_index = monitor_combo.current()
    if monitor_index == -1:
        messagebox.showwarning("Error", "Por favor, selecciona un monitor.")
        return
    monitor = get_monitors()[monitor_index]
    threading.Thread(target=start_recording, args=(monitor,), daemon=True).start()

# Crear la ventana de la aplicación
app = Tk()
app.title("Grabador de Pantalla")
app.geometry("300x200")

# Etiqueta y ComboBox para seleccionar el monitor
Label(app, text="Selecciona el monitor:").pack(pady=10)

monitors = get_monitors()
monitor_options = [f"Monitor {i+1} - {m.width}x{m.height}" for i, m in enumerate(monitors)]
monitor_combo = Combobox(app, values=monitor_options, state="readonly")
monitor_combo.pack(pady=10)

# Etiqueta para mostrar el tiempo
timer_label = Label(app, text="Tiempo: 00:00:00")
timer_label.pack(pady=10)

# Botones de control
start_button = Button(app, text="Grabar", command=start_recording_thread)
start_button.pack(pady=5)

stop_button = Button(app, text="Detener", command=stop_recording)
stop_button.pack(pady=5)

# Iniciar la aplicación
app.mainloop()
