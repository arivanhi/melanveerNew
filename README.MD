# Aplikasi Deteksi Vena

Aplikasi desktop berbasis Python untuk deteksi vena secara *real-time* menggunakan Raspberry Pi CM4, kamera inframerah, dan antarmuka PyQt5.

## Fitur

* **Live Feed:** Menampilkan video *feed* langsung dari kamera.
* **Splash Screen:** Menampilkan logo aplikasi saat startup.
* **Kontrol Gambar:** Penyesuaian *real-time* untuk:
    * Brightness
    * Contrast
    * Zoom
* **UI Intuitif:** Tata letak tiga kolom yang bersih dengan ikon dan nilai parameter yang interaktif.
* **(Dalam Pengembangan)** Pengukuran lebar vena.
* **(Dalam Pengembangan)** Monitor daya baterai menggunakan MCP3008.

## Kebutuhan Perangkat Keras

* Raspberry Pi CM4 (atau model Raspberry Pi 3/4/5 lainnya)
* Sistem Operasi Raspberry Pi OS (Debian Bookworm atau lebih baru)
* Kamera (inframerah) yang kompatibel dengan Raspberry Pi.
* (Opsional) ADC MCP3008 untuk monitoring baterai.

## Instalasi & Cara Menjalankan

Metode instalasi ini dirancang khusus untuk Raspberry Pi OS agar mendapatkan performa terbaik dengan menghindari kompilasi paket-paket berat.

### 1. Klona (Clone) Repository

```bash
git clone https://github.com/arivanhi/melanveerNew.git
cd NAMA_REPO_ANDA
```

### 2. Instalasi Dependensi Sistem (via `apt`)

Ini adalah langkah paling penting. Kita akan menginstal paket-paket berat (OpenCV, PyQt5, RPi.GPIO) langsung dari *repository* Raspberry Pi OS.

```bash
sudo apt update
sudo apt install python3-pip python3-venv python3-full python3-opencv python3-pyqt5 python3-rpi.gpio
```

### 3. Buat Virtual Environment

Kita akan membuat *virtual environment* (`venv`) yang juga bisa "melihat" paket-paket sistem yang baru saja kita instal.

```bash
# Buat venv dengan akses ke paket sistem
python3 -m venv --system-site-packages venv
```

### 4. Aktifkan Virtual Environment

Anda harus melakukan ini setiap kali Anda ingin menjalankan aplikasi.

```bash
source venv/bin/activate
```

*(Prompt terminal Anda sekarang akan diawali dengan `(venv)`)*

### 5. Instal Sisa Paket (via `pip`)

Sekarang kita instal sisa paket Python yang tidak ada di `apt` (seperti *library* Adafruit) menggunakan file `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 6. (Opsional) Perbaiki Peringatan Qt

Jika Anda melihat peringatan `QStandardPaths: wrong permissions...`, jalankan perintah ini satu kali untuk memperbaikinya:

```bash
chmod 0700 /run/user/1000
```

## Menjalankan Aplikasi

Pastikan Anda berada di dalam *virtual environment* yang aktif (`source venv/bin/activate`).

```bash
# Ganti 'main.py' dengan nama file skrip Python utama Anda
python3 main.py
```

## Struktur File Penting

Pastikan semua file ikon dan logo berada di folder yang sama dengan skrip utama Anda.

```
.
├── main.py                   # Skrip Python utama (vena_viewer_layout_v3.py)
├── requirements.txt          # Paket pip
├── README.md                 # File ini
└── icon/
    ├── logo_splash.png           # Gambar untuk splash screen
    ├── logo_app.png              # Logo kecil di UI
    ├── brightness_icon.png       # Ikon slider brightness
    ├── contrast_icon.png         # Ikon slider contrast
    ├── zoom_icon.png             # Ikon slider zoom
    ├── camera_icon.png           # Ikon tombol on/off kamera
    └── measure_icon.png          # Ikon tombol start ukur
```