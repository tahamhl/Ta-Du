# 📋 Ta-Du: Modern Görev Yönetim Uygulaması

<div align="center">
  <img src="tadu.png" alt="Ta-Du Logo" width="150">
  <br>
  <strong>Minimalist ve Kullanıcı Dostu Görev Yönetimi</strong>
  <br>
  <sub>v1.1.0</sub>
</div>

## 📖 İçindekiler
- [Proje Hakkında](#-proje-hakkında)
- [Özellikler](#-özellikler)
- [Kurulum](#-kurulum)
- [Geliştirme Ortamı Kurulumu](#-geliştirme-ortamı-kurulumu)
- [PyInstaller ile Dağıtım](#-pyinstaller-ile-dağıtım)
- [Kullanım](#-kullanım)
- [Katkıda Bulunma](#-katkıda-bulunma)
- [Lisans](#-lisans)
- [İletişim](#-iletişim)

## 🎯 Proje Hakkında
Ta-Du, modern ve kullanıcı dostu bir görev yönetim uygulamasıdır. PyQt5 ile geliştirilmiş olan bu uygulama, görevlerinizi kategorilere ayırmanıza, önceliklendirmenize ve takip etmenize olanak sağlar. Tam ekran modunda çalışan uygulama, sistem tepsisine küçültülebilir ve her zaman elinizin altında kalır.

## ✨ Özellikler
- **Modern Arayüz**: Şık ve kullanıcı dostu tasarım
- **Kategori Sistemi**: 
  - 📋 Yapılacak
  - 🔄 Yapılıyor
  - ✅ Bitti
  - ⭐ Dilek Listesi
- **Öncelik Seviyeleri**:
  - 🔴 Yüksek
  - 🟡 Orta
  - 🟢 Düşük
- **Ses Efektleri**: Görev ekleme, silme ve taşıma işlemlerinde
- **Tema Desteği**: Açık/Koyu tema seçeneği
- **Sistem Tepsisi**: Arka planda çalışabilme özelliği
- **Veri Saklama**: SQLite veritabanı ile kalıcı depolama
- **Sürükle-Bırak**: Görevleri kategoriler arası taşıma
- **Klavye Kısayolları**: Hızlı işlem yapabilme

## 💻 Kurulum
1. [Releases](https://github.com/tahamhl/ta-du/releases) sayfasından son sürümü indirin
2. Veya direkt olarak [tahamehel.tr/Ta-Du/Ta-Du.rar](https://tahamehel.tr/Ta-Du/Ta-Du.rar) adresinden indirin
3. İndirilen `Ta-Du.exe` dosyasını çalıştırın
4. Uygulama otomatik olarak başlayacaktır

## 🛠 Geliştirme Ortamı Kurulumu
```bash
# Repoyu klonlayın
git clone https://github.com/tahamhl/ta-du.git
cd ta-du

# Sanal ortam oluşturun (opsiyonel ama önerilen)
python -m venv venv
source venv/bin/activate  # Linux/Mac için
venv\Scripts\activate     # Windows için

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Uygulamayı çalıştırın
python todo.py
```

## 📦 PyInstaller ile Dağıtım
Ta-Du'yu executable dosyaya dönüştürmek için PyInstaller kullanılmıştır. İşte adım adım dağıtım süreci:

### 1. Gerekli Dosyalar
```plaintext
ta-du/
├── todo.py           # Ana uygulama dosyası
├── ta_du.spec       # PyInstaller spec dosyası
├── tadu.ico         # Uygulama ikonu
├── add.wav          # Ses dosyası
├── delete.wav       # Ses dosyası
├── move.wav         # Ses dosyası
└── requirements.txt  # Bağımlılıklar
```

### 2. Bağımlılıkların Yüklenmesi
```bash
pip install pyinstaller
pip install -r requirements.txt
```

### 3. PyInstaller Spec Dosyası
```python
# ta_du.spec
block_cipher = None

a = Analysis(
    ['todo.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('add.wav', '.'),
        ('delete.wav', '.'),
        ('move.wav', '.'),
        ('tadu.ico', '.')
    ],
    hiddenimports=['PyQt5.QtMultimedia'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Ta-Du',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='tadu.ico'
)
```

### 4. Dağıtım Oluşturma
```bash
# PyInstaller ile exe oluşturma
python -m PyInstaller ta_du.spec --clean
```

### 5. Çıktı Dosyaları
Dağıtım sonrası `dist` klasöründe oluşan dosyalar:
```plaintext
dist/
└── Ta-Du.exe       # Çalıştırılabilir uygulama
```

### 6. Önemli Notlar
- Veritabanı `%USERPROFILE%\Documents\Ta-Du\` klasöründe oluşturulur
- Ses ve ikon dosyaları exe içine gömülüdür
- Uygulama ilk çalıştırmada gerekli klasörleri otomatik oluşturur

## 🎮 Kullanım
### Klavye Kısayolları
- **E**: Seçili görevi düzenle
- **Delete**: Seçili görevi sil
- **Shift + Sağ Ok**: Görevi sağdaki kategoriye taşı
- **Shift + Sol Ok**: Görevi soldaki kategoriye taşı
- **Alt + Tab**: Uygulamayı simge durumuna küçült

### Fare İşlemleri
- **Sağ Tık**: Görev üzerinde işlem menüsü
- **Sürükle-Bırak**: Görevleri kategoriler arası taşıma
- **Çift Tık**: Sistem tepsisi simgesinden uygulamayı aç

## 👥 Katkıda Bulunma
1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik: XYZ'`)
4. Branch'inizi push edin (`git push origin feature/yeniOzellik`)
5. Pull Request oluşturun

## 📄 Lisans
Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 📞 İletişim
- **Geliştirici**: Taha Mehel
- **Website**: [tahamehel.tr](https://tahamehel.tr)
- **GitHub**: [@tahamhl](https://github.com/tahamhl)
- **E-posta**: tahamehel1@gmail.com

---
<div align="center">
  <sub>Ta-Du ile görevlerinizi organize edin, zamanınızı yönetin! ⭐</sub>
</div> 