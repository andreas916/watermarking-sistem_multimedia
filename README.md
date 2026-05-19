# Tugas Watermarking Sistem Multimedia

Andreas Saputra Tambun - 18224110

Repository ini berisi implementasi manual Discrete Cosine Transform (DCT) untuk penyisipan citra biner (watermark) pada gambar, serta simulasi kompresi JPEG untuk mengevaluasi ketahanan watermark.

## Kesimpulan Evaluasi

Berdasarkan simulasi mengubah Quality Factor (QF), watermark tidak dapat diekstrak mulai dari QF 70 ke bawah.

**Analisis Matematis Kegagalan di QF 70:**
Penurunan drastis dari 100% ke 9.62% pada QF 70 disebabkan oleh matriks pembagi kuantisasi JPEG yang nilainya melampaui langkah energi penyisipan watermark (Q = 20).
Hal ini menyebabkan nilai koefisien yang disisipkan dibulatkan menjadi 0 (bit hitam) oleh algoritma kompresi.
Angka 9.62% merepresentasikan rasio piksel hitam asli (teks) pada citra biner asal.

## Mekanisme Proses

- **Embedding:** RGB -> YCbCr -> Ekstraksi Channel Y -> Split Blok 8x8 -> **Manual DCT** -> Penyisipan bit di Mid-Band Koordinat (4,4) -> Manual IDCT.
- **Simulasi JPEG:** Scaling formula QF standar -> Kuantisasi (pembagian & pembulatan) dengan Matrix Luminance JPEG -> Rekonstruksi.

## Struktur File

- `watermark_embed.py`: Script untuk menyisipkan watermark ke gambar.
- `jpeg_simulation.py`: Script simulasi kompresi JPEG manual.
- `watermark_extract.py`: Script untuk mengekstrak dan menghitung akurasi watermark.
