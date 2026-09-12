# BINUS Disease Detection — Skrining Gejala & Arahan Dokter Spesialis

Web app yang memprediksi **3 kemungkinan kondisi kesehatan teratas** berdasarkan gejala yang dipilih pengguna, lalu mengarahkan ke dokter spesialis yang sesuai — dibangun dengan model machine learning (Random Forest) di atas basis pengetahuan 36 kondisi × 65 gejala.

## ⚠️ Prinsip Etis — Baca Ini Sebelum Menggunakan/Mendemokan

Ini **alat skrining edukatif untuk portofolio**, BUKAN produk medis dan BUKAN pengganti diagnosis dokter. Beberapa keputusan desain sengaja dibuat untuk mencerminkan itu, bukan sekadar disclaimer formalitas:

- **Selalu menampilkan TOP-3, bukan satu jawaban pasti** — karena gejala yang tumpang tindih antar kondisi itu nyata (top-1 accuracy model ini 73%, tapi top-3 accuracy 90%), dan memaksakan satu jawaban tunggal akan menyesatkan.
- **Peringatan darurat (`urgent_warning`) bekerja independen dari model** — kalau gejala yang dipilih termasuk daftar "red flag" (nyeri dada, sesak napas, dll), sistem SELALU menampilkan peringatan untuk segera ke dokter/IGD, terlepas dari apapun hasil prediksi statistiknya. Model machine learning tidak boleh jadi satu-satunya penjaga gerbang untuk gejala yang berpotensi mengancam nyawa.
- **Tidak pernah menampilkan info dosis obat, resep, atau instruksi pengobatan** — hanya nama kondisi, spesialis yang disarankan, dan deskripsi umum satu kalimat.
- **Disclaimer tampil permanen di UI**, bukan cuma di README — baik di halaman input maupun halaman hasil.
- **Datanya sintetis**, dibuat dari basis pengetahuan gejala umum yang dikurasi manual (`src/knowledge_base.py`) — bukan data pasien nyata, bukan basis data medis klinis bersertifikat.

Kalau project ini didiskusikan di wawancara magang, poin-poin di atas justru yang paling penting disebutkan — itu menunjukkan pemahaman tanggung jawab membangun produk di domain sensitif, bukan cuma "bisa bikin model ML".

## Fitur tambahan: BMI, tensi, dan durasi sakit

Selain gejala, pengguna bisa (opsional) mengisi berat/tinggi badan (dihitung jadi kategori BMI), kategori tensi, dan sudah berapa lama merasakan gejala. Tiga hal ini nyata memengaruhi hasil prediksi (bukan cuma pajangan UI) — divalidasi lewat pengujian: gejala yang identik menghasilkan urutan top-3 yang berbeda tergantung kategori BMI/tensi yang dilaporkan.

**Prinsip penting**: setiap field ini punya opsi eksplisit **"Tidak tahu"** dan **"Tidak mau jawab"**, dan keduanya diperlakukan netral oleh model — bukan sinyal negatif. Ini dicapai dengan menyuntikkan kategori `tidak_tahu` secara acak dan **merata ke semua penyakit** saat membuat data latih (lihat `generate_training_data.py`), supaya secara matematis kategori itu tidak memihak kondisi manapun. Pengguna tidak pernah "dirugikan" hasil prediksinya hanya karena memilih untuk tidak menjawab.

## Cara kerja

1. **`knowledge_base.py`** — basis pengetahuan: 36 kondisi kesehatan, masing-masing dipetakan ke gejala karakteristiknya (dengan bobot 0–1), dokter spesialis yang disarankan, kategori, dan status darurat (urgent/tidak).
2. **`generate_training_data.py`** — mensimulasikan ~4.300 "pasien" sintetis: untuk tiap kondisi, gejala intinya muncul sesuai peluang bobotnya, ditambah sedikit noise gejala acak supaya model belajar pola yang robust.
3. **`train_model.py`** — melatih Random Forest classifier, dievaluasi dengan **top-3 accuracy** (bukan cuma top-1) karena itu metrik yang relevan dengan cara aplikasi ini dipakai.
4. **`api.py`** — FastAPI, endpoint `/predict` menerima daftar gejala dan mengembalikan 3 kemungkinan teratas + spesialis + peringatan darurat.
5. **`web/`** — frontend React: checklist gejala per kategori tubuh, state loading, tampilan hasil dengan probability bar dan badge spesialis.

## Cara menjalankan

### Backend
```bash
pip install -r requirements.txt
cd src
python generate_training_data.py
python train_model.py
python api.py
```
API akan jalan di `http://127.0.0.1:8010`. Cek `http://127.0.0.1:8010/health` untuk memastikan sudah aktif.

### Frontend
```bash
cd web
npm install
npm run dev
```
Buka `http://localhost:5173`. Pastikan backend (`uvicorn`) masih berjalan di jendela terminal terpisah.

## Cara deploy (biar bisa diakses lewat link, bukan cuma localhost)

- **Frontend**: `npm run build` di folder `web/`, lalu deploy folder `dist/` ke **Vercel** atau **Netlify** (gratis, tinggal drag & drop).
- **Backend**: deploy `src/` (FastAPI) ke **Render.com** (ada free tier untuk web service Python) atau **Railway**. Setelah dapat URL backend-nya, update `API_BASE` di `web/src/App.jsx` ke URL itu (ganti dari `http://127.0.0.1:8010`), lalu build & deploy ulang frontend-nya.

## Tech stack

Python · scikit-learn (Random Forest) · pandas · Flask · React + Vite

*(Catatan: versi awal project ini pakai FastAPI, lalu dipindah ke Flask supaya bisa di-deploy gratis di PythonAnywhere tanpa perlu kartu kredit sama sekali. Logika prediksinya identik — cuma cara mendefinisikan endpoint & validasi input yang berbeda antar framework.)*

## Ide pengembangan lanjutan

- Ganti basis pengetahuan manual dengan dataset medis publik yang lebih besar dan divalidasi (mis. dataset symptom-disease dari sumber akademis).
- Tambah tingkat keparahan gejala (ringan/sedang/berat), bukan cuma ada/tidak ada.
- Tambah riwayat kesehatan pengguna (usia, riwayat penyakit) sebagai fitur tambahan model.
- Kerja sama dengan tenaga medis untuk validasi basis pengetahuan sebelum dipakai di luar konteks portofolio.

---
*Seluruh data dan model pada project ini bersifat edukatif untuk keperluan portofolio, dikurasi manual berdasarkan pengetahuan kesehatan umum — bukan basis data medis klinis, dan tidak dimaksudkan untuk penggunaan diagnostik nyata.*
