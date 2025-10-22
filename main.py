import sys
import cv2
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                             QVBoxLayout, QHBoxLayout, QSlider, QPushButton,
                             QSizePolicy, QSplashScreen)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QTimer, QSize # <-- Tambahkan QSize
from PyQt5.QtGui import QImage, QPixmap, QIcon # <-- Tambahkan QIcon

icon_folder = "icon/"
# -----------------------------------------------------------------
# KELAS CAMERA THREAD (Tidak berubah)
# -----------------------------------------------------------------
class CameraThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self.running = True
        self.brightness = 0
        self.contrast = 1.0
        self.zoom = 1.0

    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Tidak bisa membuka kamera.")
            return

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            try:
                # 1. Terapkan Brightness dan Contrast
                frame_processed = cv2.convertScaleAbs(frame, alpha=self.contrast, beta=self.brightness)

                # 2. Terapkan Zoom
                h, w, _ = frame_processed.shape
                new_h, new_w = int(h / self.zoom), int(w / self.zoom)
                x1 = int((w - new_w) / 2)
                y1 = int((h - new_h) / 2)
                
                frame_zoomed = frame_processed[y1:y1 + new_h, x1:x1 + new_w]
                frame_final = cv2.resize(frame_zoomed, (w, h), interpolation=cv2.INTER_LINEAR)

            except cv2.error:
                frame_final = frame
            
            # Konversi frame OpenCV (BGR) ke QImage (RGB)
            rgb_image = cv2.cvtColor(frame_final, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            qt_image_scaled = qt_image.scaled(640, 480, Qt.KeepAspectRatio)
            self.change_pixmap_signal.emit(qt_image_scaled)

        cap.release()

    def stop(self):
        self.running = False
        self.wait()

    @pyqtSlot(int)
    def set_brightness(self, value):
        self.brightness = value

    @pyqtSlot(int)
    def set_contrast(self, value):
        self.contrast = value / 50.0 

    @pyqtSlot(int)
    def set_zoom(self, value):
        self.zoom = value / 100.0

# -----------------------------------------------------------------
# KELAS MAIN WINDOW (Layout baru dengan Icon & Nilai Slider)
# -----------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplikasi Deteksi Vena")
        self.setGeometry(100, 100, 1024, 600)

        self.camera_is_on = False
        self.thread = None

        main_layout = QHBoxLayout()

        # --- 1. Kolom Kiri (Logo & Kontrol) ---
        left_column = QVBoxLayout()
        
        self.logo_label = QLabel()
        try:
            self.logo_label.setPixmap(QPixmap(f"{icon_folder}melanveer.png").scaled(150, 100, Qt.KeepAspectRatio))
        except:
            self.logo_label.setText("LOGO") 
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("border: 1px ; min-height: 100px;")
        left_column.addWidget(self.logo_label)

        # *** PERUBAHAN DI SINI: Pemanggilan create_slider dimodifikasi ***
        
        # Slider Brightness
        brightness_layout, self.brightness_slider = self.create_slider(
            "Brightness", f"{icon_folder}brightness.png", -100, 100, 0
        )
        left_column.addWidget(brightness_layout)

        # Slider Contrast
        contrast_layout, self.contrast_slider = self.create_slider(
            "Contrast", f"{icon_folder}contras.png", 0, 100, 50
        )
        left_column.addWidget(contrast_layout)
        
        # Slider Zoom
        zoom_layout, self.zoom_slider = self.create_slider(
            "Zoom", f"{icon_folder}zoom.png", 100, 400, 100
        )
        left_column.addWidget(zoom_layout)
        
        left_column.addStretch() 
        main_layout.addLayout(left_column, 1) 

        # --- 2. Kolom Tengah (Video) ---
        self.image_label = QLabel("Kamera Nonaktif")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 2px ;")
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.image_label, 3) 

        # --- 3. Kolom Kanan (Aksi & Hasil) ---
        right_column = QVBoxLayout()
        
        # *** PERUBAHAN DI SINI: Tombol On/Off (Ungu) dengan Icon ***
        self.toggle_camera_btn = QPushButton(" Nyalakan Kamera") # Tambah spasi
        try:
            self.toggle_camera_btn.setIcon(QIcon(f"{icon_folder}on_of.png"))
            self.toggle_camera_btn.setIconSize(QSize(24, 24))
        except:
            print("Warning: camera_icon.png tidak ditemukan")
        self.toggle_camera_btn.setStyleSheet("background-color: #8E44AD; color: white; font-weight: bold; min-height: 50px; text-align: left; padding-left: 10px;")
        self.toggle_camera_btn.clicked.connect(self.toggle_camera)
        right_column.addWidget(self.toggle_camera_btn)
        
        # Hasil Ukur (Coklat Tua)
        self.hasil_ukur_label = QLabel("Hasil Ukur:\n- mm")
        self.hasil_ukur_label.setAlignment(Qt.AlignCenter)
        self.hasil_ukur_label.setStyleSheet("background-color: #875431; color: white; font-size: 16px; border: 1px solid black; min-height: 150px;")
        right_column.addWidget(self.hasil_ukur_label)

        # *** PERUBAHAN DI SINI: Tombol Start Ukur (Orange) dengan Icon ***
        self.start_ukur_btn = QPushButton(" Start Ukur") # Tambah spasi
        try:
            self.start_ukur_btn.setIcon(QIcon(f"{icon_folder}batery.png"))
            self.start_ukur_btn.setIconSize(QSize(24, 24))
        except:
            print("Warning: measure_icon.png tidak ditemukan")
        self.start_ukur_btn.setStyleSheet("background-color: #E67E22; color: white; font-weight: bold; min-height: 50px; text-align: left; padding-left: 10px;")
        self.start_ukur_btn.clicked.connect(self.start_measurement)
        right_column.addWidget(self.start_ukur_btn)

        right_column.addStretch() 
        main_layout.addLayout(right_column, 1) 

        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        
        # central_widget.setStyleSheet("background-color: #4EBFFF;")
        self.setCentralWidget(central_widget)

    # *** FUNGSI INI DIMODIFIKASI SECARA TOTAL ***
    def create_slider(self, name, icon_path, min_val, max_val, default_val):
        """Helper function untuk membuat grup slider (tanpa kotak)"""
        
        # Layout utama untuk grup ini (Icon, Label+Value, Slider)
        layout = QVBoxLayout()
        layout.setSpacing(5) # Beri sedikit jarak antar elemen

        # 1. Icon
        icon_label = QLabel()
        try:
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except:
            icon_label.setText("[ICON]") # Fallback
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # 2. Layout untuk Label Teks dan Label Nilai (Side-by-side)
        label_layout = QHBoxLayout()
        
        text_label = QLabel(name)
        value_label = QLabel(str(default_val)) # Label untuk nilai
        value_label.setAlignment(Qt.AlignRight) # Ratakan kanan
        
        label_layout.addWidget(text_label)
        label_layout.addStretch() # Dorong nilai ke kanan
        label_layout.addWidget(value_label)
        
        # Tambahkan layout label HBox ke layout VBox utama
        layout.addLayout(label_layout)

        # 3. Slider
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default_val)
        
        # *** HUBUNGKAN SLIDER KE LABEL NILAI ***
        slider.valueChanged.connect(lambda value: value_label.setText(str(value)))
        
        layout.addWidget(slider)
        
        # Tambahkan batas tipis di sekitar grup slider
        container_widget = QWidget()
        container_widget.setLayout(layout)
        container_widget.setStyleSheet("border-radius: 5px; padding: 5px;")
        
        # Kembalikan layout DAN slider-nya
        return container_widget, slider

    @pyqtSlot(QImage)
    def update_image(self, qt_image):
        self.image_label.setPixmap(QPixmap.fromImage(qt_image))

    def toggle_camera(self):
        if not self.camera_is_on:
            self.thread = CameraThread()
            self.thread.change_pixmap_signal.connect(self.update_image)
            
            # *** PERUBAHAN CARA MENGAKSES SLIDER ***
            # Langsung hubungkan ke self.brightness_slider, dll.
            self.brightness_slider.valueChanged.connect(self.thread.set_brightness)
            self.contrast_slider.valueChanged.connect(self.thread.set_contrast)
            self.zoom_slider.valueChanged.connect(self.thread.set_zoom)
            
            self.thread.start()
            self.toggle_camera_btn.setText(" Matikan Kamera") # Jaga spasi
            self.camera_is_on = True
        else:
            if self.thread:
                self.thread.stop()
                self.thread = None
            
            self.image_label.setText("Kamera Nonaktif")
            self.image_label.setPixmap(QPixmap()) 
            self.toggle_camera_btn.setText(" Nyalakan Kamera") # Jaga spasi
            self.camera_is_on = False

    def start_measurement(self):
        if self.camera_is_on:
            print("Memulai logika pengukuran...")
            self.hasil_ukur_label.setText("Hasil Ukur:\n3.14 mm") 
        else:
            self.hasil_ukur_label.setText("Hasil Ukur:\nKamera off")

    def closeEvent(self, event):
        if self.thread:
            self.thread.stop()
        event.accept()

# -----------------------------------------------------------------
# BAGIAN UTAMA (Tidak berubah)
# -----------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        pixmap = QPixmap(f"{icon_folder}logosplash.png")
    except:
        pixmap = QPixmap(600, 300) 
        pixmap.fill(Qt.white)
        
    splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
    splash.show()
    
    window = MainWindow()

    QTimer.singleShot(3000, lambda: (splash.finish(window), window.show()))

    sys.exit(app.exec_())