# Weather App Modern with Flask API and Tkinter GUI

## 🚀 Gambaran Umum Aplikasi
`api6_.py` adalah aplikasi cuaca modern yang menggabungkan dua komponen utama:

1. **Backend API menggunakan Flask**  
   - Menyediakan endpoint REST API yang mengambil data cuaca real-time dari OpenWeatherMap API.  
   - Memproses data cuaca agar lebih ringkas dan mudah digunakan oleh client.  

2. **Frontend GUI menggunakan Tkinter**  
   - User interface grafis dengan desain modern, mengusung tema warna biru dan kuning cerah.   
   - Responsif terhadap ukuran jendela sehingga nyaman digunakan di berbagai resolusi layar.  
   - Menampilkan data cuaca yang dinamis dari API lokal secara real-time.  
   - Fitur lengkap termasuk progress bar untuk tingkat awan, ikon cuaca sesuai kondisi, serta tombol fullscreen dan minimize.

---

## 🧩 Struktur dan Komponen Kode

### 1. Konfigurasi dan API Key
- API key OpenWeatherMap diambil dari environment variable `OPENWEATHERMAP_API_KEY` untuk keamanan.  
- Tersedia opsi fallback menggunakan API key langsung (dengan catatan disembunyikan).  
- Jika API key tidak ditemukan, aplikasi akan menampilkan pesan error dan menghentikan proses.

### 2. Server Flask
- Membuat instance Flask untuk menjalankan server API.  
- Endpoint `/weather` menerima parameter `city` untuk mengambil data dari OpenWeatherMap.  
- Fungsi `fetch_weather_from_owm(city)` mengambil dan memformat data suhu, kelembapan, tekanan, kecepatan angin, kondisi cuaca, waktu matahari terbit/terbenam, dan ikon cuaca.  
- Menangani error jika kota tidak ditemukan dengan mengirim respons error yang informatif.

### 3. GUI Tkinter
- Layout responsif menggunakan grid dan pack dengan opsi `sticky="nsew"` dan `expand=True`.  
- Tema warna modern dengan dominan biru tua dan aksen kuning cerah.  
- Font menggunakan Poppins dengan variasi ukuran dan penebalan untuk judul.  
- Input field untuk nama kota dan tombol cari untuk memanggil API lokal.  
- Menampilkan data cuaca lengkap termasuk ikon yang diunduh dan dipasang di canvas.  
- Progress bar interaktif menampilkan tingkat awan secara visual.  
- Tombol fullscreen dan minimize di pojok kanan atas.  
- Frame bertingkat untuk tata letak yang rapi dan otomatis menyesuaikan ukuran.

### 4. Multi-Threading
- Server Flask dijalankan di thread terpisah agar GUI tidak terganggu saat menunggu data dari API.

### 5. Handling Gambar Ikon
- Ikon diunduh sesuai kode kondisi cuaca dari OpenWeather.  
- Diproses menggunakan PIL untuk resize dan ditampilkan dengan Tkinter `PhotoImage`.

---

## 📝 Fungsi Utama

| Fungsi                    | Keterangan                                                      |
|---------------------------|----------------------------------------------------------------|
| `fetch_weather_from_owm(city)` | Mengambil data dari OpenWeather, mengubah format waktu, dan menyiapkan data API. |
| `get_weather_data(city)`        | Endpoint Flask yang mengambil dan mengembalikan data cuaca dalam bentuk JSON. |
| `update_weather_display(city)`  | Update tampilan informasi cuaca di GUI setelah pencarian kota. |
| `toggle_fullscreen()`           | Mengubah mode window menjadi fullscreen atau kembali normal.   |
| `minimize_window()`             | Memperkecil aplikasi ke taskbar.                               |

---

## 🎨 Desain UI & UX

- **Warna latar belakang:** dominan ungu tua dan biru dengan highlight cerah.  
- **Typography:** font Poppins modern, bersih dan mudah dibaca, dengan judul besar dan teks penjelas sedang.  
- **Komponen GUI:** tombol kuning cerah kontras tinggi, input teks solid warna.  
- **Progress Bar:** visualisasi tingkat awan yang menarik dan informatif.  
- **Layout Responsif:** mudah diubah ukuran jendelanya sesuai kebutuhan pengguna.

---

## 📊 Kelebihan dan Pembelajaran

- Menggabungkan backend API Flask dan frontend GUI Tkinter dalam satu aplikasi.  
- Contoh penggunaan multi-threading agar UI Tkinter tetap responsif saat memanggil API.  
- Desain modern dan responsif pada Tkinter yang biasanya kurang fleksibel untuk UI modern.  
- Praktik pengambilan data cuaca real-time dan pemrosesan data eksternal.  
- Struktur kode modular dan mudah dikembangkan.  
- Pengolahan gambar ikon menggunakan PIL untuk UI interaktif.

---

## 📦 Cara Menjalankan

1. Pastikan Python sudah terinstall di sistem Anda.  
2. Install dependencies dengan:  
   ```
   pip install flask requests pillow
   ```  
3. Set environment variable untuk OpenWeatherMap API key:  
   - Di Linux/macOS:  
     ```
     export OPENWEATHERMAP_API_KEY="your_api_key_here"
     ```  
   - Di Windows (PowerShell):  
     ```
     setx OPENWEATHERMAP_API_KEY "your_api_key_here"
     ```  
4. Jalankan file `api6_.py`:  
   ```
   python api6_.py
   ```  
5. Aplikasi GUI akan terbuka dan server API Flask berjalan di background.

---
