import sys
import sqlite3
import warnings
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLineEdit, QListWidget, 
                           QLabel, QComboBox, QCalendarWidget, QMessageBox,
                           QFrame, QScrollArea, QSizePolicy, QListWidgetItem,
                           QMenu, QDialog, QSystemTrayIcon)
from PyQt5.QtCore import Qt, QDate, QMimeData, QSize, QPoint, QUrl
from PyQt5.QtGui import QIcon, QFont, QDrag, QColor, QPalette, QLinearGradient, QGradient, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# PyQt5 uyarılarını bastır
warnings.filterwarnings("ignore", category=DeprecationWarning)

def resource_path(relative_path):
    """PyInstaller ile paketlenmiş uygulamalar için kaynak dosya yolunu çözer."""
    try:
        # PyInstaller oluşturduğu geçici klasör
        base_path = sys._MEIPASS
    except Exception:
        # Geçici klasör yoksa mevcut dizini kullan
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Ses oynatıcıları
ADD_PLAYER = None
DELETE_PLAYER = None
MOVE_PLAYER = None

def init_sounds():
    global ADD_PLAYER, DELETE_PLAYER, MOVE_PLAYER
    try:
        ADD_PLAYER = QMediaPlayer()
        ADD_PLAYER.setMedia(QMediaContent(QUrl.fromLocalFile(resource_path("add.wav"))))
        
        DELETE_PLAYER = QMediaPlayer()
        DELETE_PLAYER.setMedia(QMediaContent(QUrl.fromLocalFile(resource_path("delete.wav"))))
        
        MOVE_PLAYER = QMediaPlayer()
        MOVE_PLAYER.setMedia(QMediaContent(QUrl.fromLocalFile(resource_path("move.wav"))))
    except Exception as e:
        print(f"Ses yükleme hatası: {e}")

def play_add_sound():
    if ADD_PLAYER:
        ADD_PLAYER.setPosition(0)
        ADD_PLAYER.play()

def play_delete_sound():
    if DELETE_PLAYER:
        DELETE_PLAYER.setPosition(0)
        DELETE_PLAYER.play()

def play_move_sound():
    if MOVE_PLAYER:
        MOVE_PLAYER.setPosition(0)
        MOVE_PLAYER.play()

class TaskCard(QWidget):
    def __init__(self, task_id, title, category, priority, due_date, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.title = title
        self.category = category
        self.priority = priority
        self.due_date = due_date
        self.setMinimumHeight(80)
        self.setFixedWidth(320)
        self.dark_mode = False
        
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setAlignment(Qt.AlignCenter)
        
        # Başlık
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Alt bilgiler için container
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(8)
        bottom_layout.setAlignment(Qt.AlignCenter)
        
        # Öncelik ve tarih
        self.priority_label = QLabel(f"⚡ {priority}")
        self.priority_label.setFont(QFont("Segoe UI", 9))
        
        # Tarihi kısalt
        date_obj = QDate.fromString(due_date, "yyyy-MM-dd")
        formatted_date = date_obj.toString("dd.MM.yy")
        self.date_label = QLabel(f"📅 {formatted_date}")
        self.date_label.setFont(QFont("Segoe UI", 9))
        
        bottom_layout.addWidget(self.priority_label)
        bottom_layout.addWidget(self.date_label)
        
        layout.addWidget(bottom_widget)
        
        # Renk ve stil ayarları
        self.updateStyle()

    def updateStyle(self, dark_mode=False):
        self.dark_mode = dark_mode
        text_color = "#ffffff" if dark_mode else "#1a202c"
        
        if self.priority == "Yüksek":
            if dark_mode:
                color = "#9B2C2C"
                gradient = "#C53030"
                border = "#FC8181"
            else:
                color = "#FFF5F5"
                gradient = "#FED7D7"
                border = "#FEB2B2"
        elif self.priority == "Orta":
            if dark_mode:
                color = "#975A16"
                gradient = "#B7791F"
                border = "#F6AD55"
            else:
                color = "#FFFAF0"
                gradient = "#FEEBC8"
                border = "#FBD38D"
        else:
            if dark_mode:
                color = "#276749"
                gradient = "#2F855A"
                border = "#68D391"
            else:
                color = "#F0FFF4"
                gradient = "#C6F6D5"
                border = "#9AE6B4"
            
        # Ana widget stili
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 {color}, stop:1 {gradient});
                border: 2px solid {border};
                border-radius: 8px;
            }}
            QLabel {{
                color: {text_color}; 
                background: transparent; 
                padding: 3px;
                font-weight: bold;
            }}
        """)

class TaskList(QListWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setViewMode(QListWidget.ListMode)
        self.setFlow(QListWidget.TopToBottom)
        self.setSpacing(10)
        self.setWrapping(False)
        self.setMinimumWidth(350)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.title = title
        self.updateStyle()
        
        # Sağ tık menüsünü etkinleştir
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # İçeriği ortala
        self.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.setHorizontalScrollMode(QListWidget.ScrollPerPixel)
        
        # Liste öğelerinin hizalamasını ayarla
        self.setStyleSheet("""
            QListWidget::item {
                margin-left: 15px;
                margin-right: 15px;
            }
        """)
        
    def delete_task(self, task_id):
        msg = QMessageBox()
        msg.setWindowTitle("Görevi Sil")
        msg.setText("Bu görevi silmek istediğinizden emin misiniz?")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        
        # Tema renklerini uygula
        dark_theme = self.window().dark_theme
        msg.setStyleSheet("""
            QMessageBox {
                background-color: """ + ("#2d3748" if dark_theme else "white") + """;
            }
            QMessageBox QLabel {
                color: """ + ("white" if dark_theme else "#1a202c") + """;
                font-size: 12px;
            }
            QPushButton {
                background-color: """ + ("#4299e1" if dark_theme else "#3182ce") + """;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: """ + ("#3182ce" if dark_theme else "#2c5282") + """;
            }
        """)
        
        # Evet ve Hayır butonlarının metinlerini Türkçe yap
        yes_button = msg.button(QMessageBox.Yes)
        no_button = msg.button(QMessageBox.No)
        yes_button.setText('Evet')
        no_button.setText('Hayır')
        
        if msg.exec_() == QMessageBox.Yes:
            window = self.window()
            window.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            window.conn.commit()
            play_delete_sound()
            return True
        return False

    def show_context_menu(self, position):
        item = self.itemAt(position)
        if not item:
            return
            
        menu = QMenu(self)
        edit_action = menu.addAction("✏️ Düzenle")
        delete_action = menu.addAction("🗑️ Sil")
        menu.addSeparator()
        
        # Taşıma menüsü
        move_menu = QMenu("📦 Taşı", menu)
        categories = ["Yapılacak", "Yapılıyor", "Bitti", "Dilek Listesi"]
        move_actions = {}
        
        for category in categories:
            if category != self.title:  # Mevcut kategoriyi hariç tut
                action = move_menu.addAction(category)
                move_actions[action] = category
                
        menu.addMenu(move_menu)
        
        # Menüyü göster ve seçilen aksiyonu al
        action = menu.exec_(self.mapToGlobal(position))
        
        if not action:
            return
            
        current_widget = self.itemWidget(item)
        
        if action == edit_action:
            # Görevi düzenle
            window = self.window()
            window.edit_task(current_widget)
            play_add_sound()
        elif action == delete_action:
            # Görevi sil (onay ile)
            if self.delete_task(current_widget.task_id):
                self.takeItem(self.row(item))
        elif action in move_actions:
            # Görevi taşı
            new_category = move_actions[action]
            window = self.window()
            window.update_task_category(current_widget.task_id, new_category)
            play_move_sound()
            window.load_tasks()  # Listeleri yenile
        
    def updateStyle(self, dark=False):
        if dark:
            bg_start = "#2d3748"
            bg_end = "#1a202c"
            border = "#4a5568"
            text = "#ffffff"
        else:
            bg_start = "#f8fafc"
            bg_end = "#edf2f7"
            border = "#e2e8f0"
            text = "#2d3748"
            
        self.setStyleSheet(f"""
            QListWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 {bg_start}, stop:1 {bg_end});
                border: 2px solid {border};
                border-radius: 12px;
                padding: 15px;
                color: {text};
            }}
            QListWidget::item {{
                background-color: transparent;
                border: none;
                margin-left: 15px;
                margin-right: 15px;
            }}
            QListWidget::item:selected {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item:hover {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QMenu {{
                background-color: {bg_start};
                color: {text};
                border: 1px solid {border};
                border-radius: 8px;
                padding: 5px;
            }}
            QMenu::item {{
                padding: 8px 25px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: rgba(49, 130, 206, 0.1);
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {border};
                margin: 5px 0px;
            }}
        """)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            current_item = self.currentItem()
            if current_item:
                current_widget = self.itemWidget(current_item)
                if current_widget:
                    # Görevi sil (onay ile)
                    if self.delete_task(current_widget.task_id):
                        self.takeItem(self.row(current_item))
        elif event.key() == Qt.Key_E:  # E tuşuna basıldığında
            current_item = self.currentItem()
            if current_item:
                current_widget = self.itemWidget(current_item)
                if current_widget:
                    # Görevi düzenle
                    window = self.window()
                    window.edit_task(current_widget)
                    play_add_sound()
        # Shift + Sağ/Sol ok tuşları için kontrol
        elif event.modifiers() == Qt.ShiftModifier:
            current_item = self.currentItem()
            if current_item:
                current_widget = self.itemWidget(current_item)
                if current_widget:
                    categories = ["Yapılacak", "Yapılıyor", "Bitti", "Dilek Listesi"]
                    current_index = categories.index(current_widget.category)
                    
                    if event.key() == Qt.Key_Right and current_index < len(categories) - 1:
                        # Sağa taşı
                        new_category = categories[current_index + 1]
                        window = self.window()
                        window.update_task_category(current_widget.task_id, new_category)
                        play_move_sound()
                        window.load_tasks()
                    elif event.key() == Qt.Key_Left and current_index > 0:
                        # Sola taşı
                        new_category = categories[current_index - 1]
                        window = self.window()
                        window.update_task_category(current_widget.task_id, new_category)
                        play_move_sound()
                        window.load_tasks()
        else:
            super().keyPressEvent(event)

class TodoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ta-Du")
        
        # İlk minimize kontrolü için flag
        self.first_minimize = True
        
        # Tüm pencere kontrollerini kaldır ve sadece tam ekran olarak ayarla
        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint  # Tüm pencere dekorasyonlarını kaldır
        )
        
        # Her zaman tam ekran olarak ayarla
        self.showFullScreen()
        
        # Veritabanı klasörünü oluştur ve bağlantıyı kur
        db_folder = os.path.join(os.path.expanduser("~"), "Documents", "Ta-Du")
        os.makedirs(db_folder, exist_ok=True)
        db_path = os.path.join(db_folder, "tasks.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()
        
        # Kaydedilmiş tema tercihini yükle
        self.dark_theme = self.load_theme_preference()
        
        # Logo ayarla
        self.setWindowIcon(QIcon(resource_path('tadu.ico')))
        
        # Sistem tepsisi ikonu oluştur
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(resource_path('tadu.ico')))
        self.tray_icon.setToolTip('Ta-Du')
        
        # Tepsi menüsü
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Göster")
        quit_action = tray_menu.addAction("Çıkış")
        
        show_action.triggered.connect(self.showNormal)
        quit_action.triggered.connect(app.quit)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
        
        # Ana widget ve layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Üst panel container (Başlık ve kapatma butonu için)
        top_container = QWidget()
        top_container_layout = QHBoxLayout(top_container)
        top_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Ta-Du başlığı
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)
        
        title_label = QLabel("Ta-Du")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet(f"color: {'white' if self.dark_theme else '#1a202c'};")
        
        version_label = QLabel("v1.1.0")
        version_label.setFont(QFont("Segoe UI", 8))
        version_label.setStyleSheet(f"color: {'white' if self.dark_theme else '#1a202c'}; padding-top: 5px;")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(version_label)
        title_layout.addStretch()
        
        top_container_layout.addWidget(title_container)
        
        # Boş widget ile sağa doğru it
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        top_container_layout.addWidget(spacer)
        
        # Kapatma butonu
        close_button = QPushButton("✖", self)
        close_button.setFont(QFont("Segoe UI", 14))
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self.minimize_to_tray)
        close_button.setFixedSize(40, 40)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: """ + ("white" if self.dark_theme else "#1a202c") + """;
                padding: 0px;
            }
            QPushButton:hover {
                color: #e53e3e;
            }
        """)
        top_container_layout.addWidget(close_button)
        
        # Top container'ı ana layout'a ekle
        self.main_layout.addWidget(top_container)
        
        # Üst panel (Görev ekleme)
        self.setup_top_panel()
        
        # Kartlar alanı
        self.setup_cards_area()
        
        # Tema değiştirme butonu ve yardım butonu için container
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(10)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.theme_button = QPushButton("🎨 Tema Değiştir")
        self.theme_button.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setCursor(Qt.PointingHandCursor)
        
        self.help_button = QPushButton("❔ Nasıl Kullanılır")
        self.help_button.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.help_button.clicked.connect(self.show_help)
        self.help_button.setCursor(Qt.PointingHandCursor)
        
        self.dev_button = QPushButton("👨‍💻 Geliştirici")
        self.dev_button.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.dev_button.clicked.connect(self.show_developer)
        self.dev_button.setCursor(Qt.PointingHandCursor)
        
        buttons_layout.addWidget(self.theme_button)
        buttons_layout.addWidget(self.help_button)
        buttons_layout.addWidget(self.dev_button)
        
        self.main_layout.addWidget(buttons_container)
        
        # Önce tema ayarını uygula
        self.apply_theme()
        
        # Sonra görevleri yükle
        self.load_tasks()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Kapatma butonunu yeniden konumlandır ve en üstte tut
        close_button = self.findChild(QPushButton, "")
        if close_button and close_button.text() == "✖":
            close_button.move(self.width() - 50, 10)
            close_button.raise_()  # Her boyut değişiminde en üstte tut

    def changeEvent(self, event):
        if event.type() == Qt.WindowState:
            # Her zaman tam ekran modunda tut
            if not self.isFullScreen():
                self.showFullScreen()
            event.accept()

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()
            self.activateWindow()

    def showEvent(self, event):
        # Pencere gösterildiğinde tam ekran yap
        self.showFullScreen()
        super().showEvent(event)

    def closeEvent(self, event):
        # Çarpıya basıldığında sistem tepsisine küçült
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            self.conn.close()
            event.accept()

    def keyPressEvent(self, event):
        # Alt+Tab tuş kombinasyonu için
        if event.key() == Qt.Key_Tab and event.modifiers() == Qt.AltModifier:
            self.hide()
        super().keyPressEvent(event)

    def setup_top_panel(self):
        self.top_panel = QWidget()
        self.top_layout = QHBoxLayout(self.top_panel)
        self.top_layout.setSpacing(15)
        self.top_layout.setContentsMargins(10, 10, 10, 10)
        
        # Görev ekleme alanı
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setSpacing(2)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        input_label = QLabel("📝 Görev")
        input_label.setFont(QFont("Segoe UI", 10))
        input_layout.addWidget(input_label)
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("✍️ Yeni görev ekle...")
        self.task_input.setMinimumWidth(400)
        self.task_input.setFont(QFont("Segoe UI", 11))
        self.task_input.returnPressed.connect(self.add_task)
        input_layout.addWidget(self.task_input)
        
        # Öncelik seçici
        priority_container = QWidget()
        priority_layout = QVBoxLayout(priority_container)
        priority_layout.setSpacing(2)
        priority_layout.setContentsMargins(0, 0, 0, 0)
        
        priority_label = QLabel("🎯 Öncelik")
        priority_label.setFont(QFont("Segoe UI", 10))
        priority_layout.addWidget(priority_label)
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Düşük", "Orta", "Yüksek"])
        self.priority_combo.setFont(QFont("Segoe UI", 11))
        self.priority_combo.setFixedWidth(120)
        priority_layout.addWidget(self.priority_combo)
        
        # Kategori seçici
        category_container = QWidget()
        category_layout = QVBoxLayout(category_container)
        category_layout.setSpacing(2)
        category_layout.setContentsMargins(0, 0, 0, 0)
        
        category_label = QLabel("📋 Kategori")
        category_label.setFont(QFont("Segoe UI", 10))
        category_layout.addWidget(category_label)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Yapılacak", "Yapılıyor", "Bitti", "Dilek Listesi"])
        self.category_combo.setFont(QFont("Segoe UI", 11))
        self.category_combo.setFixedWidth(150)
        category_layout.addWidget(self.category_combo)
        
        # Tarih seçici container
        date_container = QWidget()
        date_layout = QVBoxLayout(date_container)
        date_layout.setSpacing(2)
        date_layout.setContentsMargins(0, 0, 0, 0)
        
        date_label = QLabel("📅 Tarih")
        date_label.setFont(QFont("Segoe UI", 10))
        date_layout.addWidget(date_label)
        
        self.date_button = QPushButton("📅 Tarih Seç")
        self.date_button.setObjectName("dateButton")  # Stil için özel ID
        self.date_button.setFont(QFont("Segoe UI", 11))
        self.date_button.setFixedWidth(120)
        self.date_button.clicked.connect(self.show_calendar)
        self.date_button.setCursor(Qt.PointingHandCursor)
        date_layout.addWidget(self.date_button)
        
        self.selected_date = QDate.currentDate()
        
        # Ekle butonu container
        add_container = QWidget()
        add_layout = QVBoxLayout(add_container)
        add_layout.setSpacing(2)
        add_layout.setContentsMargins(0, 0, 0, 0)
        
        # Boş label ekleyerek hizalama
        empty_label = QLabel("")
        empty_label.setFont(QFont("Segoe UI", 10))
        add_layout.addWidget(empty_label)
        
        self.add_button = QPushButton("➕ Ekle")
        self.add_button.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.add_button.clicked.connect(self.add_task)
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.setFixedWidth(100)
        add_layout.addWidget(self.add_button)
        
        # Üst panel bileşenleri
        self.top_layout.addWidget(input_container, 4)
        self.top_layout.addWidget(priority_container, 1)
        self.top_layout.addWidget(category_container, 1)
        self.top_layout.addWidget(date_container, 1)
        self.top_layout.addWidget(add_container, 1)
        
        self.main_layout.addWidget(self.top_panel)
        
    def setup_cards_area(self):
        self.cards_widget = QWidget()
        self.cards_layout = QHBoxLayout(self.cards_widget)
        self.cards_layout.setSpacing(20)
        
        # Liste alanları
        self.todo_list = TaskList("Yapılacak")
        self.doing_list = TaskList("Yapılıyor")
        self.done_list = TaskList("Bitti")
        self.wishlist = TaskList("Dilek Listesi")
        
        # Liste başlıkları ve containerlar
        todo_container = QWidget()
        todo_layout = QVBoxLayout(todo_container)
        self.todo_title = QLabel("📋 Yapılacak")
        self.todo_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        todo_layout.addWidget(self.todo_title)
        todo_layout.addWidget(self.todo_list)
        
        doing_container = QWidget()
        doing_layout = QVBoxLayout(doing_container)
        self.doing_title = QLabel("🔄 Yapılıyor")
        self.doing_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        doing_layout.addWidget(self.doing_title)
        doing_layout.addWidget(self.doing_list)
        
        done_container = QWidget()
        done_layout = QVBoxLayout(done_container)
        self.done_title = QLabel("✅ Bitti")
        self.done_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        done_layout.addWidget(self.done_title)
        done_layout.addWidget(self.done_list)
        
        wishlist_container = QWidget()
        wishlist_layout = QVBoxLayout(wishlist_container)
        self.wishlist_title = QLabel("⭐ Dilek Listesi")
        self.wishlist_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        wishlist_layout.addWidget(self.wishlist_title)
        wishlist_layout.addWidget(self.wishlist)
        
        self.cards_layout.addWidget(todo_container)
        self.cards_layout.addWidget(doing_container)
        self.cards_layout.addWidget(done_container)
        self.cards_layout.addWidget(wishlist_container)
        
        self.main_layout.addWidget(self.cards_widget)
        
    def create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            due_date TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
        ''')
        
        # Tema tercihi için tablo oluştur
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        ''')
        self.conn.commit()
        
    def load_theme_preference(self):
        self.cursor.execute("SELECT value FROM settings WHERE key = 'theme'")
        result = self.cursor.fetchone()
        return result[0] == 'dark' if result else False
        
    def save_theme_preference(self):
        theme_value = 'dark' if self.dark_theme else 'light'
        self.cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value)
            VALUES ('theme', ?)
        """, (theme_value,))
        self.conn.commit()
        
    def toggle_theme(self):
        self.dark_theme = not self.dark_theme
        self.save_theme_preference()
        self.apply_theme()
        
    def apply_theme(self):
        # Liste stillerini güncelle
        self.todo_list.updateStyle(self.dark_theme)
        self.doing_list.updateStyle(self.dark_theme)
        self.done_list.updateStyle(self.dark_theme)
        self.wishlist.updateStyle(self.dark_theme)
        
        # Başlık renklerini güncelle
        title_color = "white" if self.dark_theme else "#2d3748"
        for title in [self.todo_title, self.doing_title, self.done_title, self.wishlist_title]:
            title.setStyleSheet(f"color: {title_color}; background: transparent;")
            
        # Ta-Du başlığı ve versiyon etiketinin rengini güncelle
        for label in self.findChildren(QLabel):
            if label.text() == "Ta-Du":
                label.setStyleSheet(f"color: {'white' if self.dark_theme else '#1a202c'}; background: transparent;")
            elif label.text() == "v1.1.0":
                label.setStyleSheet(f"color: {'white' if self.dark_theme else '#1a202c'}; background: transparent; padding-top: 5px;")
            
        # Kapatma butonunun rengini güncelle
        for button in self.findChildren(QPushButton):
            if button.text() == "✖":
                button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        color: """ + ("white" if self.dark_theme else "#1a202c") + """;
                        padding: 0px;
                    }
                    QPushButton:hover {
                        color: #e53e3e;
                    }
                """)
        
        if self.dark_theme:
            self.setStyleSheet("""
                QMainWindow, QWidget { 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                              stop:0 #1a202c, stop:1 #2d3748); 
                }
                QPushButton { 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                              stop:0 #4299e1, stop:1 #3182ce);
                    color: white; 
                    border: none; 
                    padding: 12px; 
                    border-radius: 8px;
                }
                QPushButton:hover { 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                              stop:0 #3182ce, stop:1 #2c5282);
                }
                QPushButton#dateButton {
                    background: #2d3748;
                    border: 2px solid #4a5568;
                    color: white;
                    padding: 8px 16px;
                    text-align: left;
                    font-weight: normal;
                }
                QPushButton#dateButton:hover {
                    background: #4a5568;
                    border: 2px solid #718096;
                }
                QLineEdit { 
                    background-color: #2d3748; 
                    color: white; 
                    border: 2px solid #4a5568;
                    padding: 8px 12px;
                    border-radius: 8px;
                    min-height: 20px;
                }
                QComboBox {
                    background-color: #2d3748;
                    color: white;
                    border: 2px solid #4a5568;
                    border-radius: 8px;
                    padding: 4px 8px;
                    min-height: 20px;
                    margin: 0px;
                }
                QComboBox::drop-down {
                    border: none;
                    padding-right: 8px;
                }
                QComboBox::down-arrow {
                    image: none;
                    width: 0px;
                    height: 0px;
                }
                QComboBox QAbstractItemView {
                    background-color: #2d3748;
                    color: white;
                    selection-background-color: #4299e1;
                    border: 2px solid #4a5568;
                    border-radius: 8px;
                    padding: 4px;
                    outline: none;
                }
                QComboBox QAbstractItemView::item {
                    padding: 4px 8px;
                    min-height: 20px;
                    border: none;
                }
                QComboBox QAbstractItemView::item:hover {
                    background-color: #4a5568;
                }
                QComboBox QAbstractItemView::item:selected {
                    background-color: #4299e1;
                }
                QCalendarWidget { 
                    background-color: #2d3748; 
                    color: white;
                    selection-background-color: #4299e1;
                }
                QLabel {
                    color: white;
                    font-size: 14px;
                    background: transparent;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget { 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                              stop:0 #f7fafc, stop:1 #edf2f7);
                }
                QPushButton { 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                              stop:0 #4299e1, stop:1 #3182ce);
                    color: white; 
                    border: none; 
                    padding: 12px; 
                    border-radius: 8px;
                }
                QPushButton:hover { 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                              stop:0 #3182ce, stop:1 #2c5282);
                }
                QPushButton#dateButton {
                    background: white;
                    border: 2px solid #e2e8f0;
                    color: #2d3748;
                    padding: 8px 16px;
                    text-align: left;
                    font-weight: normal;
                }
                QPushButton#dateButton:hover {
                    background: #f7fafc;
                    border: 2px solid #cbd5e0;
                }
                QLineEdit { 
                    background-color: white; 
                    color: #2d3748; 
                    border: 2px solid #e2e8f0;
                    padding: 8px 12px;
                    border-radius: 8px;
                    min-height: 20px;
                }
                QComboBox {
                    background-color: white;
                    color: #2d3748;
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 4px 8px;
                    min-height: 20px;
                    margin: 0px;
                }
                QComboBox::drop-down {
                    border: none;
                    padding-right: 8px;
                }
                QComboBox::down-arrow {
                    image: none;
                    width: 0px;
                    height: 0px;
                }
                QComboBox QAbstractItemView {
                    background-color: white;
                    color: #2d3748;
                    selection-background-color: #4299e1;
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 4px;
                    outline: none;
                }
                QComboBox QAbstractItemView::item {
                    padding: 4px 8px;
                    min-height: 20px;
                    border: none;
                }
                QComboBox QAbstractItemView::item:hover {
                    background-color: #edf2f7;
                }
                QComboBox QAbstractItemView::item:selected {
                    background-color: #4299e1;
                    color: white;
                }
                QCalendarWidget { 
                    background-color: white; 
                    color: #2d3748;
                    selection-background-color: #4299e1;
                }
                QLabel {
                    color: #2d3748;
                    font-size: 14px;
                    background: transparent;
                }
            """)
            
        # Tüm kartların stillerini güncelle
        self.update_all_cards_style()
        
    def update_all_cards_style(self):
        # Tüm listelerdeki kartları güncelle
        lists = [self.todo_list, self.doing_list, self.done_list, self.wishlist]
        for task_list in lists:
            for i in range(task_list.count()):
                item = task_list.item(i)
                card = task_list.itemWidget(item)
                if card:
                    card.updateStyle(self.dark_theme)
            
    def show_calendar(self):
        calendar = QCalendarWidget(self)
        calendar.setMinimumDate(QDate.currentDate())
        calendar.setSelectedDate(self.selected_date)
        calendar.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        calendar.setFixedWidth(400)  # Takvim genişliğini sabitle
        
        # Takvim stilini ayarla
        if self.dark_theme:
            calendar.setStyleSheet("""
                QCalendarWidget {
                    background-color: #2d3748;
                    border: 2px solid #4a5568;
                    border-radius: 12px;
                }
                QCalendarWidget QToolButton {
                    color: white;
                    background-color: transparent;
                    padding: 8px;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QCalendarWidget QToolButton:hover {
                    background-color: #4a5568;
                }
                QCalendarWidget QMenu {
                    background-color: #2d3748;
                    color: white;
                    border: 1px solid #4a5568;
                    border-radius: 4px;
                }
                QCalendarWidget QSpinBox {
                    color: white;
                    background-color: #2d3748;
                    selection-background-color: #4299e1;
                    selection-color: white;
                    border: 1px solid #4a5568;
                    border-radius: 4px;
                    padding: 2px;
                }
                QCalendarWidget QTableView {
                    background-color: #2d3748;
                    selection-background-color: #4299e1;
                    selection-color: white;
                    outline: none;
                }
                QCalendarWidget QAbstractItemView:enabled {
                    color: white;
                    background-color: #2d3748;
                    selection-background-color: #4299e1;
                    selection-color: white;
                }
                QCalendarWidget QWidget#qt_calendar_navigationbar {
                    background-color: #1a202c;
                    border-top-left-radius: 12px;
                    border-top-right-radius: 12px;
                    padding: 4px;
                }
                QCalendarWidget QWidget#qt_calendar_prevmonth,
                QCalendarWidget QWidget#qt_calendar_nextmonth {
                    color: white;
                    qproperty-icon: none;
                    min-width: 32px;
                    max-width: 32px;
                    min-height: 32px;
                    max-height: 32px;
                }
                QCalendarWidget QWidget#qt_calendar_prevmonth {
                    qproperty-text: "◀";
                }
                QCalendarWidget QWidget#qt_calendar_nextmonth {
                    qproperty-text: "▶";
                }
                QCalendarWidget QWidget { 
                    alternate-background-color: #2d3748;
                }
                QCalendarWidget QAbstractItemView:disabled {
                    color: #4a5568;
                }
            """)
        else:
            calendar.setStyleSheet("""
                QCalendarWidget {
                    background-color: white;
                    border: 2px solid #e2e8f0;
                    border-radius: 12px;
                }
                QCalendarWidget QToolButton {
                    color: #2d3748;
                    background-color: transparent;
                    padding: 8px;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QCalendarWidget QToolButton:hover {
                    background-color: #edf2f7;
                }
                QCalendarWidget QMenu {
                    background-color: white;
                    color: #2d3748;
                    border: 1px solid #e2e8f0;
                    border-radius: 4px;
                }
                QCalendarWidget QSpinBox {
                    color: #2d3748;
                    background-color: white;
                    selection-background-color: #4299e1;
                    selection-color: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 4px;
                    padding: 2px;
                }
                QCalendarWidget QTableView {
                    background-color: white;
                    selection-background-color: #4299e1;
                    selection-color: white;
                    outline: none;
                }
                QCalendarWidget QAbstractItemView:enabled {
                    color: #2d3748;
                    background-color: white;
                    selection-background-color: #4299e1;
                    selection-color: white;
                }
                QCalendarWidget QWidget#qt_calendar_navigationbar {
                    background-color: #f7fafc;
                    border-top-left-radius: 12px;
                    border-top-right-radius: 12px;
                    padding: 4px;
                }
                QCalendarWidget QWidget#qt_calendar_prevmonth,
                QCalendarWidget QWidget#qt_calendar_nextmonth {
                    color: #2d3748;
                    qproperty-icon: none;
                    min-width: 32px;
                    max-width: 32px;
                    min-height: 32px;
                    max-height: 32px;
                }
                QCalendarWidget QWidget#qt_calendar_prevmonth {
                    qproperty-text: "◀";
                }
                QCalendarWidget QWidget#qt_calendar_nextmonth {
                    qproperty-text: "▶";
                }
                QCalendarWidget QWidget { 
                    alternate-background-color: white;
                }
                QCalendarWidget QAbstractItemView:disabled {
                    color: #cbd5e0;
                }
            """)
        
        # Takvimi düğmenin altında göster
        button_pos = self.date_button.mapToGlobal(self.date_button.rect().bottomLeft())
        screen = QApplication.primaryScreen().geometry()
        
        # Takvimin ekrandan taşmasını önle
        calendar_x = min(button_pos.x(), screen.right() - calendar.width())
        calendar_y = min(button_pos.y(), screen.bottom() - calendar.height())
        
        # Eğer takvim sol kenara taşıyorsa, x koordinatını 0'a ayarla
        calendar_x = max(calendar_x, screen.left())
        
        calendar.move(calendar_x, calendar_y)
        
        def on_date_selected():
            self.selected_date = calendar.selectedDate()
            self.date_button.setText(f"📅 {self.selected_date.toString('dd.MM.yy')}")
            calendar.close()
            
        calendar.clicked.connect(on_date_selected)
        calendar.show()
        
    def add_task(self):
        title = self.task_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir görev girin!")
            return
            
        category = self.category_combo.currentText()
        priority = self.priority_combo.currentText()
        due_date = self.selected_date.toString("yyyy-MM-dd")
        
        self.cursor.execute('''
        INSERT INTO tasks (title, category, priority, due_date)
        VALUES (?, ?, ?, ?)
        ''', (title, category, priority, due_date))
        self.conn.commit()
        task_id = self.cursor.lastrowid
        
        play_add_sound()
        
        self.task_input.clear()
        self.selected_date = QDate.currentDate()
        self.date_button.setText("📅 Tarih Seç")
        self.load_tasks()
        
    def load_tasks(self):
        self.todo_list.clear()
        self.doing_list.clear()
        self.done_list.clear()
        self.wishlist.clear()
        
        self.cursor.execute("SELECT * FROM tasks WHERE completed = 0")
        tasks = self.cursor.fetchall()
        
        for task in tasks:
            card_widget = TaskCard(task[0], task[1], task[2], task[3], task[4])
            # Kart oluşturulur oluşturulmaz tema ayarını uygula
            card_widget.updateStyle(self.dark_theme)
            
            item = QListWidgetItem()
            item.setSizeHint(card_widget.sizeHint())
            
            if task[2] == "Yapılacak":
                self.todo_list.addItem(item)
                self.todo_list.setItemWidget(item, card_widget)
            elif task[2] == "Yapılıyor":
                self.doing_list.addItem(item)
                self.doing_list.setItemWidget(item, card_widget)
            elif task[2] == "Bitti":
                self.done_list.addItem(item)
                self.done_list.setItemWidget(item, card_widget)
            elif task[2] == "Dilek Listesi":
                self.wishlist.addItem(item)
                self.wishlist.setItemWidget(item, card_widget)
                
    def update_task_category(self, task_id, new_category):
        self.cursor.execute("""
            UPDATE tasks 
            SET category = ? 
            WHERE id = ?
        """, (new_category, task_id))
        self.conn.commit()
        
    def edit_task(self, task_card):
        # Düzenleme penceresi oluştur
        edit_dialog = QDialog(self)
        edit_dialog.setWindowTitle("Görevi Düzenle")
        edit_dialog.setMinimumWidth(400)
        edit_dialog.setStyleSheet("""
            QDialog {
                background-color: """ + ("#2d3748" if self.dark_theme else "white") + """;
                border-radius: 8px;
            }
            QLabel {
                color: """ + ("white" if self.dark_theme else "#2d3748") + """;
                font-size: 12px;
            }
        """)
        
        layout = QVBoxLayout(edit_dialog)
        layout.setSpacing(15)
        
        # Başlık düzenleme
        title_label = QLabel("📝 Görev Başlığı:")
        title_input = QLineEdit(task_card.title)
        title_input.setStyleSheet(self.task_input.styleSheet())
        title_input.setFont(QFont("Segoe UI", 11))
        
        # Öncelik düzenleme
        priority_label = QLabel("🎯 Öncelik:")
        priority_combo = QComboBox()
        priority_combo.addItems(["Düşük", "Orta", "Yüksek"])
        priority_combo.setCurrentText(task_card.priority)
        priority_combo.setStyleSheet(self.priority_combo.styleSheet())
        priority_combo.setFont(QFont("Segoe UI", 11))
        
        # Kategori düzenleme
        category_label = QLabel("📋 Kategori:")
        category_combo = QComboBox()
        category_combo.addItems(["Yapılacak", "Yapılıyor", "Bitti", "Dilek Listesi"])
        category_combo.setCurrentText(task_card.category)
        category_combo.setStyleSheet(self.category_combo.styleSheet())
        category_combo.setFont(QFont("Segoe UI", 11))
        
        # Tarih düzenleme
        date_label = QLabel("📅 Tarih:")
        selected_date = QDate.fromString(task_card.due_date, "yyyy-MM-dd")
        date_edit = QPushButton(f"📅 {selected_date.toString('dd.MM.yy')}")
        date_edit.setStyleSheet(self.date_button.styleSheet())
        date_edit.setFont(QFont("Segoe UI", 11))
        date_edit.setCursor(Qt.PointingHandCursor)
        
        def show_calendar():
            calendar = QCalendarWidget(edit_dialog)
            calendar.setMinimumDate(QDate.currentDate())
            calendar.setSelectedDate(selected_date)
            calendar.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
            calendar.setFixedWidth(400)
            
            # Takvim stilini ayarla
            if self.dark_theme:
                calendar.setStyleSheet("""
                    QCalendarWidget {
                        background-color: #2d3748;
                        border: 2px solid #4a5568;
                        border-radius: 12px;
                    }
                    QCalendarWidget QToolButton {
                        color: white;
                        background-color: transparent;
                        padding: 8px;
                        border: none;
                        border-radius: 4px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QCalendarWidget QToolButton:hover {
                        background-color: #4a5568;
                    }
                    QCalendarWidget QMenu {
                        background-color: #2d3748;
                        color: white;
                        border: 1px solid #4a5568;
                        border-radius: 4px;
                    }
                    QCalendarWidget QSpinBox {
                        color: white;
                        background-color: #2d3748;
                        selection-background-color: #4299e1;
                        selection-color: white;
                        border: 1px solid #4a5568;
                        border-radius: 4px;
                        padding: 2px;
                    }
                    QCalendarWidget QTableView {
                        background-color: #2d3748;
                        selection-background-color: #4299e1;
                        selection-color: white;
                        outline: none;
                    }
                    QCalendarWidget QAbstractItemView:enabled {
                        color: white;
                        background-color: #2d3748;
                        selection-background-color: #4299e1;
                        selection-color: white;
                    }
                    QCalendarWidget QWidget#qt_calendar_navigationbar {
                        background-color: #1a202c;
                        border-top-left-radius: 12px;
                        border-top-right-radius: 12px;
                        padding: 4px;
                    }
                    QCalendarWidget QWidget#qt_calendar_prevmonth,
                    QCalendarWidget QWidget#qt_calendar_nextmonth {
                        color: white;
                        qproperty-icon: none;
                        min-width: 32px;
                        max-width: 32px;
                        min-height: 32px;
                        max-height: 32px;
                    }
                    QCalendarWidget QWidget#qt_calendar_prevmonth {
                        qproperty-text: "◀";
                    }
                    QCalendarWidget QWidget#qt_calendar_nextmonth {
                        qproperty-text: "▶";
                    }
                    QCalendarWidget QWidget { 
                        alternate-background-color: #2d3748;
                    }
                    QCalendarWidget QAbstractItemView:disabled {
                        color: #4a5568;
                    }
                """)
            else:
                calendar.setStyleSheet("""
                    QCalendarWidget {
                        background-color: white;
                        border: 2px solid #e2e8f0;
                        border-radius: 12px;
                    }
                    QCalendarWidget QToolButton {
                        color: #2d3748;
                        background-color: transparent;
                        padding: 8px;
                        border: none;
                        border-radius: 4px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QCalendarWidget QToolButton:hover {
                        background-color: #edf2f7;
                    }
                    QCalendarWidget QMenu {
                        background-color: white;
                        color: #2d3748;
                        border: 1px solid #e2e8f0;
                        border-radius: 4px;
                    }
                    QCalendarWidget QSpinBox {
                        color: #2d3748;
                        background-color: white;
                        selection-background-color: #4299e1;
                        selection-color: white;
                        border: 1px solid #e2e8f0;
                        border-radius: 4px;
                        padding: 2px;
                    }
                    QCalendarWidget QTableView {
                        background-color: white;
                        selection-background-color: #4299e1;
                        selection-color: white;
                        outline: none;
                    }
                    QCalendarWidget QAbstractItemView:enabled {
                        color: #2d3748;
                        background-color: white;
                        selection-background-color: #4299e1;
                        selection-color: white;
                    }
                    QCalendarWidget QWidget#qt_calendar_navigationbar {
                        background-color: #f7fafc;
                        border-top-left-radius: 12px;
                        border-top-right-radius: 12px;
                        padding: 4px;
                    }
                    QCalendarWidget QWidget#qt_calendar_prevmonth,
                    QCalendarWidget QWidget#qt_calendar_nextmonth {
                        color: #2d3748;
                        qproperty-icon: none;
                        min-width: 32px;
                        max-width: 32px;
                        min-height: 32px;
                        max-height: 32px;
                    }
                    QCalendarWidget QWidget#qt_calendar_prevmonth {
                        qproperty-text: "◀";
                    }
                    QCalendarWidget QWidget#qt_calendar_nextmonth {
                        qproperty-text: "▶";
                    }
                    QCalendarWidget QWidget { 
                        alternate-background-color: white;
                    }
                    QCalendarWidget QAbstractItemView:disabled {
                        color: #cbd5e0;
                    }
                """)
            
            # Takvimi düğmenin altında göster
            button_pos = date_edit.mapToGlobal(date_edit.rect().bottomLeft())
            screen = QApplication.primaryScreen().geometry()
            
            # Takvimin ekrandan taşmasını önle
            calendar_x = min(button_pos.x(), screen.right() - calendar.width())
            calendar_y = min(button_pos.y(), screen.bottom() - calendar.height())
            
            # Eğer takvim sol kenara taşıyorsa, x koordinatını 0'a ayarla
            calendar_x = max(calendar_x, screen.left())
            
            calendar.move(calendar_x, calendar_y)
            
            def on_date_selected():
                nonlocal selected_date
                selected_date = calendar.selectedDate()
                date_edit.setText(f"📅 {selected_date.toString('dd.MM.yy')}")
                calendar.close()
            
            calendar.clicked.connect(on_date_selected)
            calendar.show()
            
        date_edit.clicked.connect(show_calendar)
        
        # Butonlar
        button_layout = QHBoxLayout()
        save_button = QPushButton("💾 Kaydet")
        cancel_button = QPushButton("❌ İptal")
        
        for button in [save_button, cancel_button]:
            button.setStyleSheet(self.add_button.styleSheet())
            button.setFont(QFont("Segoe UI", 11))
            button.setCursor(Qt.PointingHandCursor)
            button_layout.addWidget(button)
        
        def save_changes():
            # Veritabanında güncelle
            self.cursor.execute("""
                UPDATE tasks
                SET title = ?, category = ?, priority = ?, due_date = ?
                WHERE id = ?
            """, (
                title_input.text(),
                category_combo.currentText(),
                priority_combo.currentText(),
                selected_date.toString("yyyy-MM-dd"),
                task_card.task_id
            ))
            self.conn.commit()
            self.load_tasks()  # Listeyi yenile
            edit_dialog.close()
        
        save_button.clicked.connect(save_changes)
        cancel_button.clicked.connect(edit_dialog.close)
        
        # Widget'ları düzene ekle
        for widget in [
            title_label, title_input,
            priority_label, priority_combo,
            category_label, category_combo,
            date_label, date_edit
        ]:
            layout.addWidget(widget)
        
        layout.addLayout(button_layout)
        edit_dialog.exec_()

    def minimize_to_tray(self):
        if self.first_minimize:
            msg = QMessageBox(self)
            msg.setWindowTitle("Ta-Du")
            msg.setText("Uygulama Simge Durumuna Küçültüldü")
            msg.setInformativeText("Ta-Du uygulaması görev çubuğunun sağ alt köşesindeki simge durumuna küçültüldü.\n\nUygulamayı tekrar açmak için simgeye çift tıklayabilirsiniz.")
            msg.setIcon(QMessageBox.Information)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: """ + ("#2d3748" if self.dark_theme else "white") + """;
                }
                QMessageBox QLabel {
                    color: """ + ("white" if self.dark_theme else "#1a202c") + """;
                    font-size: 12px;
                }
                QPushButton {
                    background-color: """ + ("#4299e1" if self.dark_theme else "#3182ce") + """;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: """ + ("#3182ce" if self.dark_theme else "#2c5282") + """;
                }
            """)
            msg.exec_()
            self.first_minimize = False
        
        self.hide()  # Uygulamayı gizle

    def show_help(self):
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("Nasıl Kullanılır?")
        help_dialog.setMinimumWidth(700)  # Genişliği artırdım
        help_dialog.setMinimumHeight(600)  # Yükseklik ekledim
        help_dialog.setStyleSheet("""
            QDialog {
                background-color: """ + ("#2d3748" if self.dark_theme else "white") + """;
                border-radius: 8px;
            }
            QLabel {
                color: """ + ("white" if self.dark_theme else "#2d3748") + """;
                font-size: 13px;
                padding: 5px;
                line-height: 1.6;
            }
            QPushButton {
                background-color: """ + ("#4299e1" if self.dark_theme else "#3182ce") + """;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: """ + ("#3182ce" if self.dark_theme else "#2c5282") + """;
            }
        """)
        
        layout = QVBoxLayout(help_dialog)
        layout.setSpacing(15)
        
        # Yardım içeriği
        help_text = """
        <div style='margin: 20px;'>
            <h2 style='color: """ + ("white" if self.dark_theme else "#1a202c") + """; font-size: 24px; margin-bottom: 20px;'>
                🎯 Ta-Du Kullanım Kılavuzu
            </h2>
            
            <h3 style='color: """ + ("white" if self.dark_theme else "#2d3748") + """; font-size: 18px; margin-top: 25px;'>
                📝 Görev Ekleme ve Düzenleme
            </h3>
            <p style='margin-left: 20px; line-height: 1.8;'>
                • Üst kısımdaki görev giriş alanına görev başlığını yazın<br>
                • Öncelik seçin: Düşük 🟢, Orta 🟡, Yüksek 🔴<br>
                • Kategori seçin: Yapılacak, Yapılıyor, Bitti, Dilek Listesi<br>
                • Tarih seçin: Görevin tamamlanması gereken tarihi belirleyin<br>
                • "➕ Ekle" butonuna tıklayın veya Enter tuşuna basın
            </p>
            
            <h3 style='color: """ + ("white" if self.dark_theme else "#2d3748") + """; font-size: 18px; margin-top: 25px;'>
                ⌨️ Klavye Kısayolları
            </h3>
            <p style='margin-left: 20px; line-height: 1.8;'>
                • <b>E tuşu:</b> Seçili görevi düzenleme penceresini açar<br>
                • <b>Delete tuşu:</b> Seçili görevi silmek için onay penceresi açar<br>
                • <b>Shift + Sağ Ok:</b> Görevi bir sonraki kategoriye taşır<br>
                &nbsp;&nbsp;&nbsp;(Yapılacak → Yapılıyor → Bitti → Dilek Listesi)<br>
                • <b>Shift + Sol Ok:</b> Görevi bir önceki kategoriye taşır<br>
                &nbsp;&nbsp;&nbsp;(Dilek Listesi → Bitti → Yapılıyor → Yapılacak)<br>
                • <b>Alt + Tab:</b> Uygulamayı simge durumuna küçültür
            </p>
            
            <h3 style='color: """ + ("white" if self.dark_theme else "#2d3748") + """; font-size: 18px; margin-top: 25px;'>
                🖱️ Fare İşlemleri
            </h3>
            <p style='margin-left: 20px; line-height: 1.8;'>
                • <b>Sağ Tık Menüsü:</b><br>
                &nbsp;&nbsp;&nbsp;✏️ Düzenle: Görevi düzenleme penceresini açar<br>
                &nbsp;&nbsp;&nbsp;🗑️ Sil: Görevi silmek için onay penceresi açar<br>
                &nbsp;&nbsp;&nbsp;📦 Taşı: Görevi başka bir kategoriye taşır<br>
                • <b>Sürükle-Bırak:</b> Görevleri kategoriler arasında taşıyabilirsiniz<br>
                • <b>Sistem Tray İkonu:</b><br>
                &nbsp;&nbsp;&nbsp;➜ Çift tıklama: Uygulamayı tam ekran açar<br>
                &nbsp;&nbsp;&nbsp;➜ Sağ tık: Göster ve Çıkış seçeneklerini gösterir
            </p>
            
            <h3 style='color: """ + ("white" if self.dark_theme else "#2d3748") + """; font-size: 18px; margin-top: 25px;'>
                📋 Kategoriler
            </h3>
            <p style='margin-left: 20px; line-height: 1.8;'>
                • <b>📋 Yapılacak:</b> Henüz başlanmamış görevler<br>
                • <b>🔄 Yapılıyor:</b> Üzerinde çalışılan görevler<br>
                • <b>✅ Bitti:</b> Tamamlanan görevler<br>
                • <b>⭐ Dilek Listesi:</b> İleride yapılması planlanan görevler
            </p>
            
            <h3 style='color: """ + ("white" if self.dark_theme else "#2d3748") + """; font-size: 18px; margin-top: 25px;'>
                🎨 Özelleştirme ve Görünüm
            </h3>
            <p style='margin-left: 20px; line-height: 1.8;'>
                • <b>Tema Değiştirme:</b><br>
                &nbsp;&nbsp;&nbsp;➜ 🎨 Tema Değiştir butonu ile açık/koyu tema arasında geçiş yapın<br>
                • <b>Öncelik Renkleri:</b><br>
                &nbsp;&nbsp;&nbsp;➜ Yüksek: 🔴 Kırmızı tonları<br>
                &nbsp;&nbsp;&nbsp;➜ Orta: 🟡 Turuncu tonları<br>
                &nbsp;&nbsp;&nbsp;➜ Düşük: 🟢 Yeşil tonları
            </p>
            
            <h3 style='color: """ + ("white" if self.dark_theme else "#2d3748") + """; font-size: 18px; margin-top: 25px;'>
                💡 İpuçları
            </h3>
            <p style='margin-left: 20px; line-height: 1.8;'>
                • Kapatma (✖) butonuna tıkladığınızda uygulama sistem tepsisine küçülür<br>
                • Görevlerinizi önceliklerine göre renklendirerek önem derecesini belirleyin<br>
                • Tarihi geçmiş görevler için tarih kısmı kırmızı ile vurgulanır<br>
                • Görevleri sürükleyerek kategoriler arasında hızlıca taşıyabilirsiniz<br>
                • Sistem tepsisindeki simgeye çift tıklayarak uygulamayı tekrar açabilirsiniz
            </p>
        </div>
        """
        
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        help_label.setTextFormat(Qt.RichText)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidget(help_label)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: """ + ("#4a5568" if self.dark_theme else "#e2e8f0") + """;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: """ + ("#718096" if self.dark_theme else "#cbd5e0") + """;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        layout.addWidget(scroll)
        
        # Kapat butonu
        close_button = QPushButton("✔️ Anladım")
        close_button.clicked.connect(help_dialog.close)
        close_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(close_button)
        
        help_dialog.exec_()

    def show_developer(self):
        dev_dialog = QDialog(self)
        dev_dialog.setWindowTitle("Geliştirici Hakkında")
        dev_dialog.setMinimumWidth(500)
        dev_dialog.setStyleSheet("""
            QDialog {
                background-color: """ + ("#2d3748" if self.dark_theme else "white") + """;
                border-radius: 8px;
            }
            QLabel {
                color: """ + ("white" if self.dark_theme else "#2d3748") + """;
                font-size: 13px;
                padding: 5px;
                line-height: 1.6;
            }
            QPushButton {
                background-color: """ + ("#4299e1" if self.dark_theme else "#3182ce") + """;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: """ + ("#3182ce" if self.dark_theme else "#2c5282") + """;
            }
            QWidget#linkWidget {
                background-color: """ + ("#4a5568" if self.dark_theme else "#edf2f7") + """;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
            }
        """)
        
        layout = QVBoxLayout(dev_dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        title_label = QLabel("👨‍💻 Geliştirici Bilgileri")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # İsim
        name_container = QWidget()
        name_container.setObjectName("linkWidget")
        name_layout = QHBoxLayout(name_container)
        name_layout.setContentsMargins(15, 15, 15, 15)
        
        name_icon = QLabel("👤")
        name_icon.setFont(QFont("Segoe UI", 16))
        name_text = QLabel("Taha Mehel")
        name_text.setFont(QFont("Segoe UI", 12, QFont.Bold))
        
        name_layout.addWidget(name_icon)
        name_layout.addWidget(name_text)
        name_layout.addStretch()
        layout.addWidget(name_container)
        
        # E-posta
        email_container = QWidget()
        email_container.setObjectName("linkWidget")
        email_layout = QHBoxLayout(email_container)
        email_layout.setContentsMargins(15, 15, 15, 15)
        
        email_icon = QLabel("📧")
        email_icon.setFont(QFont("Segoe UI", 16))
        email_text = QLabel("tahamehel1@gmail.com")
        email_text.setFont(QFont("Segoe UI", 12))
        
        email_layout.addWidget(email_icon)
        email_layout.addWidget(email_text)
        email_layout.addStretch()
        layout.addWidget(email_container)
        
        # GitHub
        github_container = QWidget()
        github_container.setObjectName("linkWidget")
        github_layout = QHBoxLayout(github_container)
        github_layout.setContentsMargins(15, 15, 15, 15)
        
        github_icon = QLabel("🌐")
        github_icon.setFont(QFont("Segoe UI", 16))
        github_text = QLabel("github.com/tahamhl")
        github_text.setFont(QFont("Segoe UI", 12))
        
        github_layout.addWidget(github_icon)
        github_layout.addWidget(github_text)
        github_layout.addStretch()
        layout.addWidget(github_container)
        
        # Website
        website_container = QWidget()
        website_container.setObjectName("linkWidget")
        website_layout = QHBoxLayout(website_container)
        website_layout.setContentsMargins(15, 15, 15, 15)
        
        website_icon = QLabel("🌍")
        website_icon.setFont(QFont("Segoe UI", 16))
        website_text = QLabel("tahamehel.tr")
        website_text.setFont(QFont("Segoe UI", 12))
        
        website_layout.addWidget(website_icon)
        website_layout.addWidget(website_text)
        website_layout.addStretch()
        layout.addWidget(website_container)
        
        # Boşluk ekle
        layout.addStretch()
        
        # Kapat butonu
        close_button = QPushButton("✔️ Tamam")
        close_button.clicked.connect(dev_dialog.close)
        close_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(close_button)
        
        dev_dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    init_sounds()  # Sesleri başlangıçta yükle
    window = TodoApp()
    window.show()
    sys.exit(app.exec_()) 