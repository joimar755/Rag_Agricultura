import flet as ft
import serial
import threading

# 🔌 CAMBIA TU PUERTO
SERIAL_PORT = "/dev/ttyUSB2"
BAUDRATE = 115200


def main(page: ft.Page):

    # =======================
    # 🎨 CONFIG UI
    # =======================
    page.title = "Smart Crop Monitor"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.padding = 20
    page.scroll = "auto"

    # =======================
    # 📡 SERIAL
    # =======================
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.1)
    except Exception as e:
        print("Error serial:", e)
        ser = None

    # =======================
    # 🌡 SENSOR UI (DINÁMICO)
    # =======================
    temp_text = ft.Text("0", size=35, color="#00FF00", weight="bold")
    hum_text = ft.Text("0", size=35, color="#00FFFF", weight="bold")
    soil_text = ft.Text("0", size=35, color="#3A8DFF", weight="bold")

    # =======================
    # 📦 CARD SENSOR
    # =======================
    def sensor_card(label, value_widget, color):
        return ft.Container(
            content=ft.Column([
                ft.Text(label, size=14, color="white"),
                value_widget,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#1e1e1e",
            padding=15,
            border_radius=10,
            border=ft.border.all(1, "#3d3d3d"),
            expand=True
        )

    sensors_section = ft.Column([
        ft.Text("🌱 Condiciones (Sensores)", size=18, weight="bold", color="white"),
        sensor_card("Temperatura (°C)", temp_text, "#00FF00"),
        sensor_card("Humedad del Aire (%)", hum_text, "#00FFFF"),
        sensor_card("Humedad del Suelo (%)", soil_text, "#3A8DFF"),
    ], spacing=10)

    # =======================
    # 🤖 CHAT SIMPLE
    # =======================
    chat_box = ft.Container(
        height=200,
        bgcolor="#1a1a1a",
        border_radius=10,
        padding=10,
        content=ft.Text("Bot: listo para ayudarte 🌱", color="white")
    )

    chatbot_section = ft.Column([
        ft.Text("💬 Asistente IA", size=18, weight="bold", color="white"),
        chat_box
    ], margin=ft.margin.only(top=20))

    # =======================
    # 📷 YOLO SECTION
    # =======================
    def upload_yolo(e):
        print("📷 Imagen lista para YOLO")

    yolo_section = ft.Container(
        content=ft.Column([
            ft.Text("📷 Visión Artificial (YOLO)", size=18, color="#0078D7"),

            ft.Container(
                content=ft.Image(
                    src="https://via.placeholder.com/400x300"
                ),
                border_radius=10,
                border=ft.border.all(1, "#3d3d3d"),
            ),

            ft.ElevatedButton(
                "SUBIR E ANALIZAR CON YOLO",
                bgcolor="#0078D7",
                on_click=upload_yolo
            )
        ]),
        margin=ft.margin.only(bottom=20)
    )

    # =======================
    # 📡 LECTURA SERIAL
    # =======================
    def read_serial():

        while True:
            if ser and ser.is_open:
                try:
                    line = ser.readline().decode(errors="ignore").strip()

                    if line:
                        print("RAW:", line)

                        data = line.split(",")

                        if len(data) >= 2:
                            t = data[0]
                            h = data[1]
                            s = data[2] 

                            # 🔥 ACTUALIZAR UI
                            temp_text.value = t
                            hum_text.value = h
                            soil_text.value = s

                            page.update()

                except Exception as e:
                    print("Error serial:", e)

    if ser:
        threading.Thread(target=read_serial, daemon=True).start()

    # =======================
    # 📱 AGREGAR UI
    # =======================
    page.add(
        yolo_section,
        sensors_section,
        chatbot_section
    )


ft.app(target=main)