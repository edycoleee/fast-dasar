# 📱 Panduan Mencoba API untuk Orang Biasa (Non-Programmer)

Halo! Panduan ini untuk Anda yang ingin mencoba API tanpa harus mengerti coding. Sangat mudah! 😊

---

## 🚀 Langkah 1: Jalankan Server

Pertama, kita perlu menjalankan server API. Ikuti langkah ini:

### Di Terminal/Command Prompt:

```bash
# 1. Buka folder project
cd /home/sultan/flask/fast-dasar

# 2. Jalankan server
uvicorn main:app --reload
```

Jika berhasil, Anda akan melihat pesan seperti ini:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**Jangan tutup terminal ini!** Biarkan server tetap berjalan.

---

## 📖 Langkah 2: Buka Dokumentasi Interaktif

Sekarang buka browser Anda (Chrome, Firefox, Safari, dll) dan ketikkan URL ini:

```
http://127.0.0.1:8000/docs
```

Atau klik link di atas jika Anda membaca ini di editor.

### Apa yang akan Anda lihat?

Halaman yang terlihat seperti ini akan muncul - **Swagger UI**, dokumentasi interaktif API kami:

```
📦 Halo API
├─ GET  /
├─ GET  /api/halo/
└─ POST /api/halo/
```

Ini adalah **dokumentasi API otomatis** - tidak perlu membaca manual membosankan! 🎉

---

## 🧪 Langkah 3: Coba Endpoint GET Pertama

### Apa itu "Endpoint"?
Endpoint adalah "pintu masuk" ke API. Ibaratnya seperti tombol di remote TV - setiap tombol melakukan hal berbeda.

### Mari coba endpoint pertama: `GET /`

1. **Cari bagian** bertulisan **`GET /`** (warna biru)
2. **Klik** tombol itu untuk membukanya
3. Anda akan melihat deskripsi: "Root endpoint untuk testing"
4. **Klik tombol biru bertulisan "Try it out"**
5. Lalu **klik "Execute"**

### Hasilnya:
```json
{
  "message": "FastAPI is running!",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

**Selamat!** Anda baru saja memanggil API pertama Anda! 🎊

---

## 🎤 Langkah 4: Coba Endpoint GET Kedua

Endpoint ini memberikan salam:

### `GET /api/halo/`

1. **Cari** bagian dengan **`GET /api/halo/`** (warna biru)
2. **Klik** untuk membuka
3. **Klik "Try it out"**
4. **Klik "Execute"**

### Hasilnya:
```json
{
  "message": "Halo! Welcome to FastAPI"
}
```

Mudah sekali! Tidak perlu input apapun. ✨

---

## 💬 Langkah 5: Coba Endpoint POST (Yang Seru!)

Endpoint ini lebih interaktif - Anda bisa mengirim data!

### `POST /api/halo/`

**Apa itu POST?**
- **GET**: Mengambil data (seperti membaca buku)
- **POST**: Mengirim data (seperti mengisi form)

1. **Cari** bagian dengan **`POST /api/halo/`** (warna hijau)
2. **Klik** untuk membuka
3. **Klik "Try it out"**

### Anda akan melihat form kosong seperti ini:
```json
{
  "nama": "string",
  "handphone": "string"
}
```

4. **Ganti dengan data Anda sendiri:**

```json
{
  "nama": "Budi Santoso",
  "handphone": "08123456789"
}
```

5. **Klik "Execute"**

### Hasilnya:
```json
{
  "message": "Halo Budi Santoso!",
  "nama": "Budi Santoso",
  "handphone": "08123456789"
}
```

**Wow!** API memberikan response yang dipersonalisasi! 🌟

---

## ⚠️ Langkah 6: Coba Endpoint POST dengan Data Salah

Mari coba apa yang terjadi jika data tidak lengkap:

1. **Buka `POST /api/halo/` lagi**
2. **Ubah data menjadi:**

```json
{
  "nama": "Budi Santoso"
}
```

(Perhatikan - `handphone` dihilangkan!)

3. **Klik "Execute"**

### Hasilnya - Error! 🚨

Anda akan melihat pesan error seperti ini:

```json
{
  "detail": [
    {
      "loc": ["body", "handphone"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Artinya:** "Hei! Anda lupa kirim `handphone`! Harus ada!"

Ini adalah **validasi otomatis** API - API otomatis mengecek apakah data yang Anda kirim lengkap dan benar. 🛡️

---

## 📋 Ringkasan Endpoint yang Tersedia

| Endpoint | Tipe | Kegunaan | Input |
|----------|------|----------|-------|
| `/` | GET | Cek status API | Tidak ada |
| `/api/halo/` | GET | Dapatkan ucapan halo | Tidak ada |
| `/api/halo/` | POST | Kirim nama & handphone | nama, handphone |

---

## 🎓 Apa Ini Berguna?

**Ya! Sangat berguna!**

API ini bisa digunakan oleh:
- ✅ Website (untuk mengirim form)
- ✅ Aplikasi mobile (untuk mendapatkan data)
- ✅ Program lain yang ingin berkomunikasi dengan server ini
- ✅ Testing & development

---

## 💡 Tips Berguna

### 1. **Dokumentasi Lain**
Selain `/docs`, ada juga `/redoc`:
```
http://127.0.0.1:8000/redoc
```
Ini dokumentasi versi lain - tampilannya berbeda tapi isinya sama.

### 2. **Menggunakan dari Program Lain**
Jika ingin menggunakan API ini dari JavaScript, Python, dll, bisa pakai:

**JavaScript (contoh):**
```javascript
fetch('http://127.0.0.1:8000/api/halo/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ nama: 'Budi', handphone: '08123456789' })
})
.then(r => r.json())
.then(data => console.log(data))
```

**Python (contoh):**
```python
import requests
data = {'nama': 'Budi', 'handphone': '08123456789'}
response = requests.post('http://127.0.0.1:8000/api/halo/', json=data)
print(response.json())
```

---

## 🚨 Troubleshooting

### Problem: "Cannot connect to http://127.0.0.1:8000"
- **Solusi**: Pastikan server masih berjalan di terminal. Jika sudah ditutup, jalankan ulang `uvicorn main:app --reload`

### Problem: "Cannot read documentation"
- **Solusi**: Coba refresh browser (Ctrl+R atau Cmd+R)

### Problem: API memberikan error 422
- **Solusi**: Periksa apakah semua field sudah diisi dengan benar

---

## 🎯 Selamat!

Anda sekarang tahu cara:
- ✅ Menjalankan server API
- ✅ Mengakses dokumentasi interaktif
- ✅ Mencoba endpoint GET
- ✅ Mencoba endpoint POST
- ✅ Membaca error messages

**Anda resmi menjadi API Tester!** 🎉

---

## 📞 Butuh Bantuan?

Jika ada yang bingung, lihat bagian mana yang tidak mengerti dan coba ulang dari sana. Atau tanya ke programmer yang membuat API ini! 😊

---

Dibuat dengan ❤️ untuk semua orang
