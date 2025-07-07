import tkinter as tk
import minimalmodbus
import serial
from time import sleep
import threading
import csv
from tkinter import filedialog
from datetime import datetime

# ----------------- SETUP MODBUS -----------------
def setup_client(address):
    client = minimalmodbus.Instrument('COM4', address, debug=False)
    client.serial.baudrate = 9600
    client.serial.bytesize = 8
    client.serial.parity = serial.PARITY_NONE
    client.serial.stopbits = 1
    client.serial.timeout = 1
    client.mode = minimalmodbus.MODE_RTU
    client.clear_buffers_before_each_transaction = True
    return client

# client1 = setup_client(31)
# client2 = setup_client(32)
client3 = setup_client(33)
# client4 = setup_client(34)

# ----------------- GUI STYLE CONFIG -----------------
main_bg = "#1E1E2F"
card_bg = "#2F2F3F"
text_color = "#E8E8F0"
highlight = "#00BFFF"
font_main = ("Segoe UI", 14)
font_title = ("Segoe UI", 20, "bold")

# ----------------- MAIN TKINTER WINDOW -----------------
root = tk.Tk()
root.title("🌡️ Modbus Sensor Dashboard")
root.geometry("700x500")
root.configure(bg=main_bg)
root.resizable(False, False)

# ----------------- TITLE -----------------
title = tk.Label(root, text="🌡️ Modbus SHS17-APX2-xxxx-2", font=font_title, bg=main_bg, fg=highlight)
title.pack(pady=20)

# ----------------- CARD FRAME -----------------
frame = tk.Frame(root, bg=main_bg)
frame.pack(padx=20, pady=10, fill="both", expand=True)

# ----------------- CARD CREATOR -----------------
def create_sensor_card(parent, row, column, title):
    card = tk.Frame(parent, bg=card_bg, bd=2, relief="ridge", padx=10, pady=10)
    card.grid(row=row, column=column, padx=15, pady=15, sticky="nsew")

    label_title = tk.Label(card, text=title, font=("Segoe UI", 16, "bold"), fg=highlight, bg=card_bg)
    label_title.pack(pady=(0, 10))

    temp = tk.Label(card, text="Temperature: -- °C", font=font_main, bg=card_bg, fg=text_color, anchor="w")
    temp.pack(fill="x")

    hum = tk.Label(card, text="Humidity: -- %", font=font_main, bg=card_bg, fg=text_color, anchor="w")
    hum.pack(fill="x")

    return temp, hum

# ----------------- CREATE 4 CARDS -----------------
temp_label1, hum_label1 = create_sensor_card(frame, 0, 0, "🌬️ Outdoor Air")
temp_label2, hum_label2 = create_sensor_card(frame, 0, 1, "💨 Exhaust Air")
temp_label3, hum_label3 = create_sensor_card(frame, 1, 0, "🌀 Supply Air")
temp_label4, hum_label4 = create_sensor_card(frame, 1, 1, "🔁 Return Air")

# ----------------- DATA READING THREAD -----------------
def read_data():
    while True:
        def update(client, temp_label, hum_label, label_name):
            try:
                temp = client.read_float(2)
                hum = client.read_float(6)
                temp_label.config(text=f"Temperature: {round(temp, 2)} °C")
                hum_label.config(text=f"Humidity: {round(hum, 2)} %")

                # เก็บข้อมูลลง CSV ทุกครั้งที่มีการอ่านค่า
                save_to_csv(label_name, temp, hum)

            except minimalmodbus.NoResponseError:
                temp_label.config(text="Temperature: No Response")
                hum_label.config(text="Humidity: No Response")
            except Exception as e:
                temp_label.config(text=f"Temp Error: {e}")
                hum_label.config(text="Humidity: Error")

        # update(client1, temp_label1, hum_label1, "Outdoor")
        # update(client2, temp_label2, hum_label2, "Exhaust")
        update(client3, temp_label3, hum_label3, "Supply")
        # update(client4, temp_label4, hum_label4, "Return")
        sleep(2)

# ----------------- SAVE TO CSV FUNCTION -----------------
def save_to_csv(sensor_name, temp, hum):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # บันทึกข้อมูลลงในไฟล์ CSV
    with open('sensor_data.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        # บันทึกข้อมูลในรูปแบบ [Timestamp, Sensor Name, Temperature, Humidity]
        writer.writerow([timestamp, sensor_name, temp, hum])

# ----------------- START THREAD -----------------
threading.Thread(target=read_data, daemon=True).start()

# ----------------- EXPORT CSV BUTTON -----------------
def export_csv():
    # เปิดไฟล์บันทึก
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Sensor", "Temperature", "Humidity"])
            # อ่านข้อมูลจากไฟล์เดิมแล้วเขียนลงในไฟล์ใหม่
            with open('sensor_data.csv', mode='r') as read_file:
                reader = csv.reader(read_file)
                next(reader)  # ข้ามหัวตาราง
                for row in reader:
                    writer.writerow(row)

# ----------------- EXPORT CSV BUTTON -----------------
export_button = tk.Button(root, text="Export to CSV", font=("Segoe UI", 14), bg=highlight, fg=main_bg, command=export_csv)
export_button.pack(pady=20)

# ----------------- MAINLOOP -----------------
root.mainloop()
