# Tugas Watermarking Sistem Multimedia

Andreas Saputra Tambun - 18224110

## Kesimpulan

Berdasarkan simulasi mengubah Quality Factor (QF), watermark tidak dapat diekstrak mulai dari QF 70 ke bawah.

**Analisis di QF 70:**
Penurunan drastis dari 100% ke 9.62% pada QF 70 itu karena matriks pembagi kuantisasi JPEG nilainya melampaui langkah energi penyisipan watermark (Q = 20).
Ini menyebabkan nilai koefisien yang disisipkan dibulatkan menjadi 0 (bit hitam) oleh algoritma kompresi.
Angka 9.62% merepresentasikan rasio piksel hitam asli (teks) pada citra biner asal.

## Struktur File

- `watermark_embed.py`: menyisipkan watermark ke gambar.
- `jpeg_simulation.py`: simulasi kompresi JPEG manual.
- `watermark_extract.py`: mengekstrak dan menghitung akurasi watermark.
