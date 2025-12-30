import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout,
    QMessageBox, QComboBox, QHeaderView, QDateEdit, QFrame, 
    QAbstractItemView, QStackedWidget, QFileDialog, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont, QColor, QIcon, QIntValidator
from PyQt5.QtCore import Qt, QDate, QSize

# Arayüz renklerinin bulunduğu kısım
RENK_MENU_BG = "#1e293b"      
RENK_ICERIK_BG = "#f1f5f9"    
RENK_KART_BG = "#ffffff"             
RENK_ACCENT_HOVER = "#be185d" 
RENK_YAZI_KOYU = "#0f172a"    
RENK_YAZI_GRI = "#64748b"     

# Veritabanı
class DatabaseManager:
    def __init__(self, db_name="prostock_v5.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS envanter (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                urun TEXT, birim TEXT, girismiktar INTEGER, giristarih TEXT,
                cikismiktar INTEGER, cikistarih TEXT, kalan INTEGER, aciklama TEXT
            )""")
        self.conn.commit()

    def sorgu(self, sql, params=()):
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            return True, self.cursor.lastrowid
        except Exception as e:
            return False, str(e)
            
    def veri_getir(self, sql, params=()):
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def kpi_getir(self):
        try:
            self.cursor.execute("SELECT COUNT(*), SUM(kalan) FROM envanter")
            res = self.cursor.fetchone()
            return res[0] if res else 0, res[1] if res else 0
        except:
            return 0, 0
#---------------------------------------------
def golge_efekti_ekle(widget):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(20)
    shadow.setColor(QColor(0, 0, 0, 20))
    shadow.setOffset(0, 5)
    widget.setGraphicsEffect(shadow)

# Butonlar
class ModernButton(QPushButton):
    def __init__(self, text, primary=False):
        super().__init__(text)
        self.setFixedHeight(45)
        self.setCursor(Qt.PointingHandCursor)
        
        if primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {RENK_ACCENT};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 600;
                    padding: 0 24px;
                }}
                QPushButton:hover {{
                    background-color: {RENK_ACCENT_HOVER};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: white;
                    color: {RENK_YAZI_KOYU};
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 500;
                    padding: 0 24px;
                }}
                QPushButton:hover {{
                    border-color: {RENK_ACCENT};
                    color: {RENK_ACCENT};
                }}
            """)

# İnput kısımları
class ModernInput(QLineEdit):
    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(45)
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 14px;
                color: {RENK_YAZI_KOYU};
            }}
            QLineEdit:focus {{
                border-color: {RENK_ACCENT};
            }}
        """)

# KPI Kartı
class KPICard(QFrame):
    def __init__(self, baslik, deger, ikon="📊"):
        super().__init__()
        self.setFixedHeight(120)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {RENK_KART_BG};
                border-radius: 12px;
            }}
        """)
        golge_efekti_ekle(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # İkon ve Başlık
        ust = QHBoxLayout()
        ikon_lbl = QLabel(ikon)
        ikon_lbl.setStyleSheet("font-size: 32px;")
        baslik_lbl = QLabel(baslik)
        baslik_lbl.setStyleSheet(f"color: {RENK_YAZI_GRI}; font-size: 13px; font-weight: 500;")
        ust.addWidget(ikon_lbl)
        ust.addStretch()
        layout.addLayout(ust)
        layout.addWidget(baslik_lbl)
        
        # Değer
        self.deger_lbl = QLabel(str(deger))
        self.deger_lbl.setStyleSheet(f"color: {RENK_YAZI_KOYU}; font-size: 28px; font-weight: 700;")
        layout.addWidget(self.deger_lbl)
    
    def guncelle(self, deger):
        self.deger_lbl.setText(str(deger))

# Main
class ModernProStock(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.setWindowTitle("ProStock - Modern Depo Yönetimi")
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet(f"background-color: {RENK_ICERIK_BG};")
        
        # Ana Widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar Menü
        self.sidebar = self.sidebar_olustur()
        main_layout.addWidget(self.sidebar)
        
        # İçerik Alanı
        self.stacked = QStackedWidget()
        self.stacked.setStyleSheet(f"background-color: {RENK_ICERIK_BG};")
        
        # Sayfalar
        self.stok_sayfa = self.stok_giris_sayfa()
        self.liste_sayfa = self.envanter_liste_sayfa()
        
        self.stacked.addWidget(self.stok_sayfa)
        self.stacked.addWidget(self.liste_sayfa)
        
        main_layout.addWidget(self.stacked, 1)
        
        self.kpi_guncelle()
    
    def sidebar_olustur(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet(f"background-color: {RENK_MENU_BG};")
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 30, 20, 30)
        layout.setSpacing(15)
        
        # Logo/Başlık
        baslik = QLabel("📦 ProStock")
        baslik.setStyleSheet("color: white; font-size: 26px; font-weight: 700; margin-bottom: 20px;")
        layout.addWidget(baslik)
        
        # Menü Butonları
        self.menu_btn_stok = self.menu_button("➕ Stok Giriş/Çıkış", 0)
        self.menu_btn_liste = self.menu_button("📋 Envanter Listesi", 1)
        
        layout.addWidget(self.menu_btn_stok)
        layout.addWidget(self.menu_btn_liste)
        layout.addStretch()
        
        # Alt Bilgi
        footer = QLabel("v5.0 | Modern Edition")
        footer.setStyleSheet(f"color: {RENK_YAZI_GRI}; font-size: 11px; margin-top: 10px;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)
        
        return sidebar
    
    def menu_button(self, text, index):
        btn = QPushButton(text)
        btn.setFixedHeight(50)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                border: none;
                text-align: left;
                padding-left: 20px;
                font-size: 15px;
                font-weight: 500;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {RENK_ACCENT};
            }}
        """)
        btn.clicked.connect(lambda: self.stacked.setCurrentIndex(index))
        return btn
    
    def stok_giris_sayfa(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Başlık
        baslik = QLabel("Stok Giriş ve Çıkış İşlemleri")
        baslik.setStyleSheet(f"color: {RENK_YAZI_KOYU}; font-size: 28px; font-weight: 700;")
        layout.addWidget(baslik)
        
        # KPI Kartları
        kpi_layout = QHBoxLayout()
        self.kpi_toplam = KPICard("Toplam Ürün", "0", "📦")
        self.kpi_stok = KPICard("Toplam Stok", "0", "📊")
        kpi_layout.addWidget(self.kpi_toplam)
        kpi_layout.addWidget(self.kpi_stok)
        layout.addLayout(kpi_layout)
        
        # Form Alanı
        form_card = QFrame()
        form_card.setStyleSheet(f"background-color: {RENK_KART_BG}; border-radius: 12px;")
        golge_efekti_ekle(form_card)
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(20)
        
        # Ürün Bilgileri
        self.urun_input = ModernInput("Ürün Adı")
        self.birim_combo = QComboBox()
        self.birim_combo.addItems(["Adet", "Kg", "Lt", "Paket", "Kutu"])
        self.birim_combo.setFixedHeight(45)
        self.birim_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 14px;
            }}
        """)
        
        form_layout.addWidget(QLabel("Ürün Adı:"))
        form_layout.addWidget(self.urun_input)
        form_layout.addWidget(QLabel("Birim:"))
        form_layout.addWidget(self.birim_combo)
        
        # Giriş
        form_layout.addWidget(QLabel("GİRİŞ İŞLEMLERİ", font=QFont("Arial", 12, QFont.Bold)))
        self.giris_miktar = ModernInput("Giriş Miktarı")
        self.giris_miktar.setValidator(QIntValidator(0, 999999))
        self.giris_tarih = QDateEdit()
        self.giris_tarih.setDate(QDate.currentDate())
        self.giris_tarih.setCalendarPopup(True)
        self.giris_tarih.setFixedHeight(45)
        
        form_layout.addWidget(self.giris_miktar)
        form_layout.addWidget(self.giris_tarih)
        
        # Çıkış
        form_layout.addWidget(QLabel("ÇIKIŞ İŞLEMLERİ", font=QFont("Arial", 12, QFont.Bold)))
        self.cikis_miktar = ModernInput("Çıkış Miktarı")
        self.cikis_miktar.setValidator(QIntValidator(0, 999999))
        self.cikis_tarih = QDateEdit()
        self.cikis_tarih.setDate(QDate.currentDate())
        self.cikis_tarih.setCalendarPopup(True)
        self.cikis_tarih.setFixedHeight(45)
        
        form_layout.addWidget(self.cikis_miktar)
        form_layout.addWidget(self.cikis_tarih)
        
        # Açıklama
        self.aciklama = ModernInput("Açıklama (Opsiyonel)")
        form_layout.addWidget(self.aciklama)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        kaydet_btn = ModernButton("💾 Kaydet", primary=True)
        kaydet_btn.clicked.connect(self.kayit_ekle)
        temizle_btn = ModernButton("🔄 Temizle")
        temizle_btn.clicked.connect(self.formu_temizle)
        
        btn_layout.addWidget(kaydet_btn)
        btn_layout.addWidget(temizle_btn)
        form_layout.addLayout(btn_layout)
        
        layout.addWidget(form_card)
        layout.addStretch()
        
        return page
    
    def envanter_liste_sayfa(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Başlık ve Arama
        ust = QHBoxLayout()
        baslik = QLabel("Envanter Listesi")
        baslik.setStyleSheet(f"color: {RENK_YAZI_KOYU}; font-size: 28px; font-weight: 700;")
        ust.addWidget(baslik)
        ust.addStretch()
        
        self.arama_input = ModernInput("🔍 Ürün ara...")
        self.arama_input.setFixedWidth(300)
        self.arama_input.textChanged.connect(self.tabloyu_guncelle)
        ust.addWidget(self.arama_input)
        layout.addLayout(ust)
        
        # Tablo
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(9)
        self.tablo.setHorizontalHeaderLabels([
            "ID", "Ürün", "Birim", "Giriş", "Giriş Tarih",
            "Çıkış", "Çıkış Tarih", "Kalan", "Açıklama"
        ])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                border-radius: 12px;
                gridline-color: #e2e8f0;
            }}
            QHeaderView::section {{
                background-color: {RENK_MENU_BG};
                color: white;
                padding: 12px;
                font-weight: 600;
                border: none;
            }}
        """)
        
        layout.addWidget(self.tablo)
        
        # Alt Butonlar
        btn_layout = QHBoxLayout()
        export_btn = ModernButton("📥 CSV'ye Aktar")
        export_btn.clicked.connect(self.csv_aktar)
        sil_btn = ModernButton("🗑️ Seçili Kaydı Sil")
        sil_btn.clicked.connect(self.kayit_sil)
        
        btn_layout.addWidget(export_btn)
        btn_layout.addWidget(sil_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        return page
    
    def kayit_ekle(self):
        urun = self.urun_input.text().strip()
        if not urun:
            QMessageBox.warning(self, "Uyarı", "Ürün adı boş olamaz!")
            return
        
        birim = self.birim_combo.currentText()
        g_miktar = int(self.giris_miktar.text() or 0)
        g_tarih = self.giris_tarih.date().toString("yyyy-MM-dd")
        c_miktar = int(self.cikis_miktar.text() or 0)
        c_tarih = self.cikis_tarih.date().toString("yyyy-MM-dd")
        kalan = g_miktar - c_miktar
        aciklama = self.aciklama.text()
        
        sql = """INSERT INTO envanter (urun, birim, girismiktar, giristarih, 
                 cikismiktar, cikistarih, kalan, aciklama) 
                 VALUES (?,?,?,?,?,?,?,?)"""
        
        basarili, _ = self.db.sorgu(sql, (urun, birim, g_miktar, g_tarih, 
                                           c_miktar, c_tarih, kalan, aciklama))
        
        if basarili:
            QMessageBox.information(self, "Başarılı", "Kayıt eklendi!")
            self.formu_temizle()
            self.tabloyu_guncelle()
            self.kpi_guncelle()
    
    def formu_temizle(self):
        self.urun_input.clear()
        self.giris_miktar.clear()
        self.cikis_miktar.clear()
        self.aciklama.clear()
        self.giris_tarih.setDate(QDate.currentDate())
        self.cikis_tarih.setDate(QDate.currentDate())
    
    def tabloyu_guncelle(self):
        arama = self.arama_input.text()
        sql = "SELECT * FROM envanter WHERE urun LIKE ?"
        veriler = self.db.veri_getir(sql, (f"%{arama}%",))
        
        self.tablo.setRowCount(len(veriler))
        for i, row in enumerate(veriler):
            for j, val in enumerate(row):
                self.tablo.setItem(i, j, QTableWidgetItem(str(val)))
    
    def kayit_sil(self):
        secili = self.tablo.currentRow()
        if secili >= 0:
            kayit_id = self.tablo.item(secili, 0).text()
            onay = QMessageBox.question(self, "Onay", "Kaydı silmek istediğinize emin misiniz?")
            if onay == QMessageBox.Yes:
                self.db.sorgu("DELETE FROM envanter WHERE id=?", (kayit_id,))
                self.tabloyu_guncelle()
                self.kpi_guncelle()
    
    def csv_aktar(self):
        dosya, _ = QFileDialog.getSaveFileName(self, "CSV Kaydet", "", "CSV Files (*.csv)")
        if dosya:
            veriler = self.db.veri_getir("SELECT * FROM envanter")
            with open(dosya, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Ürün", "Birim", "Giriş", "Giriş Tarih",
                                 "Çıkış", "Çıkış Tarih", "Kalan", "Açıklama"])
                writer.writerows(veriler)
            QMessageBox.information(self, "Başarılı", "CSV dosyası kaydedildi!")
    
    def kpi_guncelle(self):
        toplam, stok = self.db.kpi_getir()
        self.kpi_toplam.guncelle(toplam)
        self.kpi_stok.guncelle(stok or 0)

# Uygulamayı başlatan kısım
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Font ayarları
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = ModernProStock()
    window.show()
    sys.exit(app.exec_())
