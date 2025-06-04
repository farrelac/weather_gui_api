# --- START OF FILE weather_app_modern_v5.py ---

import threading
import requests
from flask import Flask, request, jsonify
import datetime
import tkinter as tk
from tkinter import ttk  # Import themed widgets for Progressbar
import tkinter.font as tkfont  # Import tkinter.font for font operations
from PIL import Image, ImageTk, ImageOps, ImageDraw, ImageFont
import io
import time
import sys
import os

# --- KONSTANTA & KONFIGURASI UMUM (Tidak Bergantung Tkinter Root) ---
# Gunakan Environment Variable untuk API Key (RECOMMENDED)
# Pastikan environment variable OPENWEATHERMAP_API_KEY diset di terminal sebelum menjalankan script.
API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")

# OPSI: Jika kesulitan dengan environment variable, bisa gunakan API Key langsung di sini untuk DEMO CEPAT.
# HAPUS ATAU KOMEN BARIS DI ATAS (API_KEY = os.environ.get(...)), dan UN-KOMEN BARIS DI BAWAH ini:
# API_KEY = "92c86ac6896ca566aa3b2e2dd154e7c6"  # <-- PASTE API KEY KAMU DI SINI (Jika pakai opsi langsung)


# Jika tidak ada API Key dari environment (dan tidak pakai opsi langsung), tampilkan pesan error dan keluar
if not API_KEY:
    print("Error: OPENWEATHERMAP_API_KEY environment variable not set.")
    print("Please set it before running the script.")
    print("Example (Linux/macOS): export OPENWEATHERMAP_API_KEY='your_api_key'")
    print("Example (Windows Command Prompt): set OPENWEATHERMAP_API_KEY=your_api_key")
    print("Example (Windows PowerShell): $env:OPENWEATHERMAP_API_KEY='your_api_key'")
    sys.exit(1)  # Keluar dari program jika API Key tidak ada


# Pengaturan URL API OpenWeatherMap
BASE_OWM_API_URL = "http://api.openweathermap.org/data/2.5/"
BASE_OWM_ICON_URL = "http://openweathermap.org/img/wn/"

# --- Definisi Tema Warna (Modern & Menarik - Mengambil Inspirasi dari Gambar) ---
THEME = {
    "primary_bg": "#1a237e",       # Sangat gelap biru/ungu (latar belakang utama)
    "secondary_bg": "#303f9f",     # Lebih terang biru/ungu (latar belakang container info cuaca)
    "card_bg": "#3949ab",          # Medium biru/ungu (latar belakang kartu detail)
    "text_primary": "#ffffff",     # Putih (teks utama, judul, label)
    "text_secondary": "#bbdefb",   # Biru muda (deskripsi, beberapa label)
    "accent_temp": "#ffeb3b",      # Kuning cerah (suhu utama)
    "accent_detail_value": "#ffeb3b", # Kuning cerah (nilai detail)
    "accent_icon": "#ffeb3b",      # Kuning cerah (ikon aplikasi, beberapa ikon detail)
    "button_bg": "#ffca28",        # Kuning (latar belakang tombol)
    "button_fg": "#1a237e",        # Warna teks tombol (sesuai primary_bg)
    "entry_bg": "#e0e0e0",         # Abu-abu terang (latar belakang input)
    "entry_fg": "#1a237e",         # Warna teks input (sesuai primary_bg)
    "entry_insert": "gray",        # Warna kursor
    "error_fg": "#ff8a65",         # Oranye terang (pesan error)
    "footer_fg": "#e0e0e0",        # Abu-abu terang (teks footer)
}


# --- Flask API Server ---
# Kode Flask server tetap sama
app = Flask(__name__)

def fetch_weather_from_owm(city):
    url = f"{BASE_OWM_API_URL}weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "id"
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()

        timezone_offset = data.get('timezone', 0)
        sunrise_utc = datetime.datetime.utcfromtimestamp(data['sys']['sunrise'])
        sunset_utc = datetime.datetime.utcfromtimestamp(data['sys']['sunset'])
        sunrise_local = sunrise_utc + datetime.timedelta(seconds=timezone_offset)
        sunset_local = sunset_utc + datetime.timedelta(seconds=timezone_offset)

        weather = {
            "city": f"{data['name']}, {data['sys']['country']}",
            "temp": data['main']['temp'],
            "description": data['weather'][0]['description'].capitalize(),
            "humidity": data['main']['humidity'],
            "wind_speed": data['wind']['speed'],
            "pressure": data['main']['pressure'],
            "visibility": round(data.get('visibility', 0) / 1000, 1),
            "sunrise": sunrise_local.strftime('%H:%M'),
            "sunset": sunset_local.strftime('%H:%M'),
            "clouds": data['clouds']['all'],
            "icon": data['weather'][0]['icon'],
            "feels_like": data['main']['feels_like']
        }
        return weather
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather from OWM: {e}")
        if isinstance(e, requests.exceptions.HTTPError):
             return {"error": f"HTTP Error: {e.response.status_code} - {e.response.reason}"}
        elif isinstance(e, requests.exceptions.ConnectionError):
             return {"error": "Connection Error. Please check your internet."}
        elif isinstance(e, requests.exceptions.Timeout):
             return {"error": "Request Timeout."}
        else:
             return {"error": f"Network Error: {e}"}

    except KeyError as e:
        print(f"Error parsing OWM weather data (missing key): {e}")
        return {"error": "Invalid data format from API."}
    except Exception as e:
        print(f"An unexpected error occurred during fetch: {e}")
        return {"error": f"An unexpected error occurred: {e}"}


@app.route("/weather")
def weather_api():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "Parameter 'city' wajib diisi"}), 400

    result = fetch_weather_from_owm(city)

    if "error" in result:
        if "city not found" in result["error"].lower() or "not found" in result["error"].lower():
             return jsonify({"error": "Kota tidak ditemukan."}), 404
        else:
             return jsonify(result), 500

    return jsonify(result), 200


def run_api():
    app.run(port=5000, debug=False, use_reloader=False)


# --- Tkinter GUI ---

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Penjelajah Cuaca Modern")
        self.root.config(bg=THEME["primary_bg"])
        self.root.geometry("900x650")
        self.root.minsize(700, 500)

        # Grid Responsif Utama pada root
        self.root.columnconfigure(0, weight=1)

        # --- Tentukan FONT_FAMILY dan Konstanta Font DI SINI sebagai Atribut Instance ---
        # Lakukan ini setelah root window dibuat
        self.FONT_FAMILY = "Poppins" if "Poppins" in tkfont.families() else "Arial"

        # Definisikan konstanta font sebagai atribut instance menggunakan self.FONT_FAMILY
        self.FONT_TITLE = (self.FONT_FAMILY, 42, "bold")
        self.FONT_SUBTITLE = (self.FONT_FAMILY, 16)
        self.FONT_INPUT = (self.FONT_FAMILY, 18)
        self.FONT_BUTTON = (self.FONT_FAMILY, 18, "bold")
        self.FONT_LOCATION = (self.FONT_FAMILY, 28, "bold")
        self.FONT_TEMP = (self.FONT_FAMILY, 80, "bold")
        self.FONT_DESC = (self.FONT_FAMILY, 22)
        self.FONT_FEELS = (self.FONT_FAMILY, 16)
        self.FONT_DETAIL_LABEL = (self.FONT_FAMILY, 14)
        self.FONT_DETAIL_VALUE = (self.FONT_FAMILY, 20, "bold")
        self.FONT_SUN_TIME = (self.FONT_FAMILY, 16, "bold")
        self.FONT_CLOUD_PERCENT = (self.FONT_FAMILY, 16, "bold")
        self.FONT_EXTRA_INFO = (self.FONT_FAMILY, 14)
        self.FONT_FOOTER = (self.FONT_FAMILY, 10)
        self.FONT_ERROR = (self.FONT_FAMILY, 14)


        # --- Initialize Style for ttk widgets ---
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')


        # --- Main Content Frame ---
        self.main_frame = tk.Frame(self.root, bg=THEME["primary_bg"])
        self.main_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.main_frame.columnconfigure(0, weight=1)


        # --- Row 0: Icon Aplikasi & Judul Utama & Subtitle ---
        self.header_frame = tk.Frame(self.main_frame, bg=THEME["primary_bg"])
        self.header_frame.grid(row=0, column=0, pady=(0, 30), sticky="n")

        self.app_icon_label = tk.Label(self.header_frame, text="☀️", font=(self.FONT_FAMILY, 60),
                                       bg=THEME["primary_bg"], fg=THEME["accent_icon"])
        self.app_icon_label.pack(side=tk.LEFT, padx=(0, 15))

        self.title_subtitle_frame = tk.Frame(self.header_frame, bg=THEME["primary_bg"])
        self.title_subtitle_frame.pack(side=tk.LEFT, anchor="s")

        self.title_label = tk.Label(self.title_subtitle_frame, text="Penjelajah Cuaca", font=self.FONT_TITLE,
                                    fg=THEME["text_primary"], bg=THEME["primary_bg"])
        self.title_label.pack(pady=(0, 0), anchor="w")

        self.subtitle_label = tk.Label(self.title_subtitle_frame, text="Temukan kondisi cuaca di seluruh dunia", font=self.FONT_SUBTITLE,
                                       fg=THEME["text_primary"], bg=THEME["primary_bg"])
        self.subtitle_label.pack(pady=(0, 0), anchor="w")


        # --- Row 1: Frame Input Kota dan Tombol Cari ---
        self.input_frame = tk.Frame(self.main_frame, bg=THEME["primary_bg"])
        self.input_frame.grid(row=1, column=0, pady=(0, 40), padx=50, sticky="ew")

        self.input_frame.columnconfigure(0, weight=1)
        self.input_frame.columnconfigure(1, weight=0)

        self.city_var = tk.StringVar()
        self.search_entry = tk.Entry(self.input_frame, textvariable=self.city_var,
                                     font=self.FONT_INPUT, justify='center', relief=tk.FLAT, bd=0,
                                     bg=THEME["entry_bg"], fg=THEME["entry_fg"], insertbackground=THEME["entry_insert"])
        self.search_entry.grid(row=0, column=0, padx=(0, 15), ipady=10, sticky="ew")
        self.search_entry.focus()
        self.search_entry.bind('<Return>', lambda event: self.search_weather())


        self.search_button = tk.Button(self.input_frame, text="Cari",
                                       font=self.FONT_BUTTON,
                                       fg=THEME["button_fg"], bg=THEME["button_bg"],
                                       activebackground=THEME["button_bg"], activeforeground=THEME["button_fg"],
                                       bd=0, relief="flat", command=self.search_weather, cursor="hand2",
                                       padx=25, pady=10)
        self.search_button.grid(row=0, column=1, sticky="e")


        # --- Row 2: Frame Hasil Cuaca Utama (Lokasi, Suhu, Ikon, Deskripsi) ---
        self.weather_info_frame = tk.Frame(self.main_frame, bg=THEME["secondary_bg"], padx=20, pady=20)
        self.weather_info_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 20))

        self.weather_info_frame.columnconfigure(0, weight=0)
        self.weather_info_frame.columnconfigure(1, weight=1)

        self.icon_lbl = tk.Label(self.weather_info_frame, bg=THEME["secondary_bg"])
        self.icon_lbl.grid(row=0, column=0, rowspan=2, sticky="nswe", padx=(0, 20))

        self.location_lbl = tk.Label(self.weather_info_frame, text="", font=self.FONT_LOCATION,
                                     fg=THEME["text_primary"], bg=THEME["secondary_bg"])
        self.location_lbl.grid(row=0, column=1, sticky="w")

        self.temp_lbl = tk.Label(self.weather_info_frame, text="--°C", font=self.FONT_TEMP,
                                 fg=THEME["accent_temp"], bg=THEME["secondary_bg"])
        self.temp_lbl.grid(row=1, column=1, sticky="w")


        # Deskripsi Cuaca (Row 3 di main_frame)
        self.desc_label = tk.Label(self.main_frame, text="", font=self.FONT_DESC,
                                   fg=THEME["text_secondary"], bg=THEME["primary_bg"])
        self.desc_label.grid(row=3, column=0, pady=(0, 10))


        # Row 4: Frame Detail Cuaca (Kartu)
        self.detail_cards_frame = tk.Frame(self.main_frame, bg=THEME["primary_bg"])
        self.detail_cards_frame.grid(row=4, column=0, pady=(0, 30), padx=40, sticky="ew")

        for i in range(6):
            self.detail_cards_frame.columnconfigure(i, weight=1)

        detail_configs = [
            ("💧", "Kelembaban", "humidity", "%"),
            ("💨", "Angin", "wind_speed", " m/s"),
            ("🌡️", "Tekanan", "pressure", " hPa"),
            ("👁️", "Jarak", "visibility", " km"),
            ("☀️", "Terbit", "sunrise", ""),
            ("🌙", "Terbenam", "sunset", ""),
        ]
        self.detail_widgets = {}

        for i, (icon_char, title_text, data_key, unit) in enumerate(detail_configs):
            detail_frame = tk.Frame(self.detail_cards_frame, bg=THEME["card_bg"], padx=5, pady=5)
            detail_frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            detail_frame.columnconfigure(0, weight=1)

            icon_label = tk.Label(detail_frame, text=icon_char, font=(self.FONT_FAMILY, 24),
                                 bg=THEME["card_bg"], fg=THEME["accent_icon"])
            icon_label.grid(row=0, column=0, pady=(0, 5))

            value_label = tk.Label(detail_frame, text="--", font=self.FONT_DETAIL_VALUE,
                                   bg=THEME["card_bg"], fg=THEME["accent_detail_value"])
            value_label.grid(row=1, column=0, pady=(0, 0))

            title_label = tk.Label(detail_frame, text=title_text, font=self.FONT_DETAIL_LABEL,
                                   bg=THEME["card_bg"], fg=THEME["text_primary"])
            title_label.grid(row=2, column=0, pady=(0, 0))

            self.detail_widgets[data_key] = {
                "frame": detail_frame, "icon": icon_label, "value": value_label, "label": title_label, "unit": unit
            }


        # Row 5: Label tambahan untuk Clouds dan 'Feels Like'
        self.extra_info_frame = tk.Frame(self.main_frame, bg=THEME["primary_bg"])
        self.extra_info_frame.grid(row=5, column=0, pady=(0, 20), padx=40, sticky="ew")

        self.extra_info_frame.columnconfigure(0, weight=1)
        self.extra_info_frame.columnconfigure(1, weight=1)

        self.cloud_label = tk.Label(self.extra_info_frame, text="☁️ Keadaan Berawan: --%", font=self.FONT_EXTRA_INFO,
                                    fg=THEME["text_secondary"], bg=THEME["primary_bg"])
        self.cloud_label.grid(row=0, column=0, sticky="w")

        self.feels_like_label = tk.Label(self.extra_info_frame, text="Terasa Seperti: --°C", font=self.FONT_EXTRA_INFO,
                                         fg=THEME["text_secondary"], bg=THEME["primary_bg"])
        self.feels_like_label.grid(row=0, column=1, sticky="e", padx=(15,0))


        # Row 6: Progress Bar
        self.clouds_progress = ttk.Progressbar(self.main_frame, orient='horizontal', mode='determinate')
        self.clouds_progress.grid(row=6, column=0, pady=(0, 30), padx=40, sticky="ew")


        # Row 7: Label Pesan Error
        self.error_message_label = tk.Label(self.main_frame, text="", font=self.FONT_ERROR,
                                            bg=THEME["primary_bg"], fg=THEME["error_fg"])
        self.error_message_label.grid(row=7, column=0, pady=(0, 10))

        # Row 8: Footer
        self.footer_lbl = tk.Label(self.main_frame, text="⚡ Didukung oleh OpenWeather API", font=self.FONT_FOOTER,
                                   bg=THEME["primary_bg"], fg=THEME["footer_fg"])
        self.footer_lbl.grid(row=8, column=0, pady=(10, 0))


    def apply_theme(self):
        """Applies the static theme colors to all widgets."""
        theme = THEME

        self.root.config(bg=theme["primary_bg"])
        self.main_frame.config(bg=theme["primary_bg"])
        self.header_frame.config(bg=theme["primary_bg"])
        self.title_subtitle_frame.config(bg=theme["primary_bg"])

        self.app_icon_label.config(bg=theme["primary_bg"], fg=theme["accent_icon"])
        self.title_label.config(bg=theme["primary_bg"], fg=theme["text_primary"])
        self.subtitle_label.config(bg=theme["primary_bg"], fg=theme["text_primary"])

        self.input_frame.config(bg=theme["primary_bg"])
        self.search_entry.config(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["entry_insert"])
        self.search_button.config(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["button_bg"], activeforeground=theme["button_fg"])

        self.weather_info_frame.config(bg=theme["secondary_bg"])
        self.location_lbl.config(bg=theme["secondary_bg"], fg=theme["text_primary"])
        self.temp_icon_frame.config(bg=theme["secondary_bg"])
        self.temp_lbl.config(bg=theme["secondary_bg"], fg=theme["accent_temp"])
        self.icon_lbl.config(bg=theme["secondary_bg"])
        self.desc_label.config(bg=THEME["primary_bg"], fg=THEME["text_secondary"])
        self.feels_like_label.config(bg=THEME["primary_bg"], fg=THEME["text_secondary"])
        self.desc_feels_frame.config(bg=THEME["primary_bg"])


        self.detail_cards_frame.config(bg=THEME["primary_bg"])
        for key in self.detail_widgets:
             widget_set = self.detail_widgets[key]
             widget_set["frame"].config(bg=theme["card_bg"])
             widget_set["icon"].config(bg=theme["card_bg"], fg=THEME["accent_icon"])
             widget_set["value"].config(bg=theme["card_bg"], fg=THEME["accent_detail_value"])
             widget_set["label"].config(bg=theme["card_bg"], fg=THEME["text_primary"])


        self.extra_info_frame.config(bg=THEME["primary_bg"])
        self.cloud_label.config(bg=THEME["primary_bg"], fg=THEME["text_secondary"])
        self.feels_like_label.config(bg=THEME["primary_bg"], fg=THEME["text_secondary"])


        # Konfigurasi Style untuk ttk.Progressbar (Statis)
        style = self.style
        static_style_name = "Static.Horizontal.TProgressbar"

        style.configure(static_style_name,
                        background=theme["progress_fg"],
                        troughcolor=theme["progress_bg"],
                        borderwidth=0,
                        relief="flat")

        self.clouds_progress.config(style=static_style_name)


        self.error_message_label.config(bg=theme["primary_bg"], fg=theme["error_fg"])
        self.footer_lbl.config(bg=theme["primary_bg"], fg=theme["footer_fg"])


    def search_weather(self):
        city = self.search_entry.get().strip()
        if not city:
            self.error_message_label.config(text="Error: Masukkan nama kota.", fg=THEME["error_fg"], font=self.FONT_ERROR)
            self.clear_weather_display()
            return

        self.error_message_label.config(text="")
        self.set_loading_state(True)
        self.clear_weather_display()

        threading.Thread(target=self.get_and_display_weather, args=(city,), daemon=True).start()


    def set_loading_state(self, loading):
        """Mengatur tampilan tombol Cari saat loading."""
        if loading:
            self.search_button.config(text="Loading...", state=tk.DISABLED)
        else:
            self.search_button.config(text="Cari", state=tk.NORMAL)


    def get_and_display_weather(self, city):
        """Memanggil API Flask dan mengupdate GUI (dalam thread terpisah)."""
        try:
            url = f"http://127.0.0.1:5000/weather?city={city}"
            res = requests.get(url, timeout=15)

            if res.status_code != 200:
                 error_data = res.json()
                 error_message = error_data.get("error", f"API Error (Status: {res.status_code})")
                 raise Exception(error_message)

            data = res.json()
            self.root.after(0, self.update_weather_display, data)

        except Exception as e:
            print(f"Error in get_and_display_weather: {e}")
            error_text = str(e)
            self.root.after(0, lambda: self.error_message_label.config(text=f"Error: {error_text}", fg=THEME["error_fg"], font=self.FONT_ERROR))
            self.root.after(0, lambda: self.clear_weather_display())
        finally:
            self.root.after(0, lambda: self.set_loading_state(False))


    def update_weather_display(self, data: dict):
        """Updates GUI widgets with received weather data (runs in main Tkinter thread)."""
        self.location_lbl.config(text=f"📍 {data.get('city', 'N/A')}")

        temp_val = data.get('temp')
        self.temp_lbl.config(text=f"{int(round(temp_val))}°C" if isinstance(temp_val, (int, float)) else "--°C")

        self.desc_label.config(text=data.get('description', '').capitalize())

        detail_data_map = {
            "humidity": (data.get('humidity'), "%"),
            "wind_speed": (data.get('wind_speed'), " m/s"),
            "pressure": (data.get('pressure'), " hPa"),
            "visibility": (data.get('visibility'), " km"),
            "sunrise": (data.get('sunrise'), ""),
            "sunset": (data.get('sunset'), ""),
        }

        for key, (value, unit) in detail_data_map.items():
            if key in self.detail_widgets:
                display_text = "--"
                if isinstance(value, (int, float)):
                    if key == "visibility":
                        formatted_value = f"{value:.0f}"
                    elif key == "wind_speed":
                        formatted_value = f"{value:.1f}"
                    else:
                        formatted_value = f"{value}"
                    display_text = formatted_value
                elif isinstance(value, str) and value != "":
                    display_text = value

                self.detail_widgets[key]["value"].config(text=f"{display_text}{unit}".strip())

        clouds_val = data.get('clouds')
        if isinstance(clouds_val, (int, float)):
            self.cloud_label.config(text=f"☁️ Keadaan Berawan: {int(round(clouds_val))}%")
            self.clouds_progress['value'] = max(0, min(100, clouds_val))
        else:
            self.cloud_label.config(text="☁️ Keadaan Berawan: --%")
            self.clouds_progress['value'] = 0

        feels_val = data.get('feels_like')
        self.feels_like_label.config(text=f"Terasa Seperti: {int(round(feels_val))}°C" if isinstance(feels_val, (int, float)) else "Terasa Seperti: --°C")

        icon_id = data.get('icon')
        self.load_weather_icon(icon_id)


    def load_weather_icon(self, icon_id: str):
        """Fetches and displays the weather icon (should ideally run in separate thread)."""
        if icon_id:
            icon_url = f"{BASE_OWM_ICON_URL}{icon_id}@2x.png"
            try:
                res = requests.get(icon_url, timeout=5)
                res.raise_for_status()
                img_data = res.content
                image = Image.open(io.BytesIO(img_data))
                image = image.resize((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.icon_lbl.config(image=photo, text="")
                self.icon_lbl.image = photo
            except Exception as e:
                 print(f"Error loading icon {icon_id}: {e}")
                 self.icon_lbl.config(image="", text="Icon\nN/A", font=(self.FONT_FAMILY, 12),
                                      bg=THEME["secondary_bg"], fg=THEME["text_primary"])
                 self.icon_lbl.image = None


        else:
            self.icon_lbl.config(image="", text="Icon\nN/A", font=(self.FONT_FAMILY, 12),
                                 bg=THEME["secondary_bg"], fg=THEME["text_primary"])
            self.icon_lbl.image = None


    def clear_weather_display(self):
        """Clears the weather display widgets."""
        self.city_var.set("")

        self.location_lbl.config(text="")
        self.temp_lbl.config(text="--°C")
        self.desc_label.config(text="")
        self.feels_like_label.config(text="")

        detail_keys = ["humidity", "wind_speed", "pressure", "visibility", "sunrise", "sunset"]
        placeholder_values = ["--", "--", "--", "--", "--:--", "--:--"]

        for i, key in enumerate(detail_keys):
             if key in self.detail_widgets:
                 unit = self.detail_widgets[key]["unit"]
                 display_text = placeholder_values[i]
                 if unit and placeholder_values[i] not in ["--:--"]:
                      display_text = f"{display_text}{unit}".strip()

                 self.detail_widgets[key]["value"].config(text=display_text)


        self.cloud_label.config(text="☁️ Keadaan Berawan: --%")
        self.clouds_progress['value'] = 0

        self.icon_lbl.config(image="", text="Icon\nN/A", font=(self.FONT_FAMILY, 12),
                             bg=THEME["secondary_bg"], fg=THEME["text_primary"])
        self.icon_lbl.image = None


# --- Jalankan Flask dan GUI bersamaan ---
if __name__ == "__main__":
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    time.sleep(1)

    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()