import numpy as np
from PIL import Image
import math
import os

def embed_watermark():
    host_path = 'foto wajah sendiri.jpeg'
    watermark_path = 'watermark.png'
    output_path = 'foto_watermarked.png'

    if not os.path.exists(host_path):
        print(f"Error: Gambar '{host_path}' tidak ditemukan di direktori saat ini.")
        return
    if not os.path.exists(watermark_path):
        print(f"Error: Gambar '{watermark_path}' tidak ditemukan di direktori saat ini.")
        return

    # 1. membaca gambar host dan watermark
    # Buka gambar wajah dan konversi ke RGB
    print("1. Membaca gambar host dan watermark...")
    host_img = Image.open(host_path).convert('RGB')
    host_arr = np.array(host_img, dtype=np.float32)

    # Buka gambar watermark dan konversi ke grayscale ('L')
    wm_img = Image.open(watermark_path).convert('L')
    wm_arr = np.array(wm_img)
    
    # Binerisasi watermark (nilai < 128 jadi 0, >= 128 jadi 1)
    wm_bin = (wm_arr >= 128).astype(np.uint8)
    wm_flat = wm_bin.flatten()
    wm_len = len(wm_flat)

    # 2. transformasi manual rgb keYCbCr
    print("2. Transformasi Manual RGB ke YCbCr...")
    R = host_arr[:,:,0]
    G = host_arr[:,:,1]
    B = host_arr[:,:,2]

    # Rumus konversi standar RGB ke YCbCr (menggunakan koefisien ITU-R BT.601)
    Y = 0.299 * R + 0.587 * G + 0.114 * B
    Cb = -0.168736 * R - 0.331264 * G + 0.5 * B + 128
    Cr = 0.5 * R - 0.418688 * G - 0.081312 * B + 128

    # Menyesuaikan dimensi agar kelipatan 8 (karena pemrosesan blok 8x8)
    h, w = Y.shape
    h_adj = h - (h % 8)
    w_adj = w - (w % 8)

    # Potong gambar jika ukurannya bukan kelipatan 8
    Y = Y[:h_adj, :w_adj]
    Cb = Cb[:h_adj, :w_adj]
    Cr = Cr[:h_adj, :w_adj]

    # Cek kapasitas gambar (1 bit per blok 8x8)
    max_capacity = (h_adj // 8) * (w_adj // 8)
    if wm_len > max_capacity:
        print(f"Peringatan: Ukuran watermark terlalu besar ({wm_len} bit) untuk gambar ini (kapasitas {max_capacity} bit).")
        print("Watermark akan dipotong agar muat.")
        wm_flat = wm_flat[:max_capacity]

    # 3. MANUAL DCT (DISCRETE COSINE TRANSFORM)
    print("3. Mempersiapkan Matriks DCT 8x8 Manual...")
    N = 8
    C = np.zeros((N, N), dtype=np.float32)
    # Membuat matriks transformasi C sesuai rumus DCT
    for i in range(N):
        for j in range(N):
            if i == 0:
                C[i, j] = math.sqrt(1/N)
            else:
                C[i, j] = math.sqrt(2/N) * math.cos((2*j + 1) * i * math.pi / (2*N))
    
    C_T = C.T # Transpose dari C untuk proses Inverse DCT (IDCT) nanti

    # 4. BLOCK PROCESSING & EMBEDDING
    print("4. Proses Blok & Menyisipkan Watermark...")
    Y_embed = np.copy(Y)
    wm_idx = 0
    Q = 20 # Parameter kuantisasi (Q), menentukan kekuatan/visibilitas watermark

    for r in range(0, h_adj, N):
        for c in range(0, w_adj, N):
            if wm_idx >= len(wm_flat):
                break
                
            # Ambil blok 8x8 dari channel Y
            block = Y_embed[r:r+N, c:c+N]
            
            # Lakukan DCT 2D Manual menggunakan perkalian matriks: D = C * A * C_T
            D = np.dot(np.dot(C, block), C_T)
            
            # 5. EMBEDDING DI KOORDINAT MID-BAND (4, 4)
            bit = wm_flat[wm_idx]
            
            # Menggunakan teknik Odd/Even Quantization Index Modulation
            val_orig = D[4, 4] / Q
            val = round(val_orig)
            
            if bit == 0:
                # Jika bit 0, nilai yang dikuantisasi harus genap
                if val % 2 != 0:
                    val += 1 if val_orig > val else -1
            else:
                # Jika bit 1, nilai yang dikuantisasi harus ganjil
                if val % 2 == 0:
                    val += 1 if val_orig > val else -1
                    
            # Terapkan kembali nilai setelah dimodifikasi ke koefisien (4,4)
            D[4, 4] = val * Q
            
            # Lakukan IDCT (Inverse DCT) Manual: A' = C_T * D * C
            block_idct = np.dot(np.dot(C_T, D), C)
            
            # Kembalikan blok 8x8 yang sudah disisipi ke matriks Y
            Y_embed[r:r+N, c:c+N] = block_idct
            
            wm_idx += 1

    # 6. TRANSFORMASI MANUAL YCbCr KEMBALI KE RGB
    print("5. Transformasi Manual YCbCr kembali ke RGB...")
    # Gunakan channel Y yang telah disisipi watermark (Y_embed)
    R_new = Y_embed + 1.402 * (Cr - 128)
    G_new = Y_embed - 0.344136 * (Cb - 128) - 0.714136 * (Cr - 128)
    B_new = Y_embed + 1.772 * (Cb - 128)

    # Batasi nilai (clipping) agar tetap dalam rentang warna piksel valid (0-255)
    R_new = np.clip(R_new, 0, 255)
    G_new = np.clip(G_new, 0, 255)
    B_new = np.clip(B_new, 0, 255)

    # Gabungkan kembali 3 channel menjadi array gambar RGB
    img_out_arr = np.stack([R_new, G_new, B_new], axis=2).astype(np.uint8)

    # 7. SIMPAN SEBAGAI GAMBAR BARU
    print("6. Menyimpan hasil gambar...")
    img_out = Image.fromarray(img_out_arr, 'RGB')
    # Simpan dalam format lossless seperti PNG agar koefisien DCT 
    # yang sudah disisipi watermark tidak rusak akibat kompresi ulang JPEG.
    img_out.save(output_path)

    print(f"Proses selesai! Gambar hasil watermarking disimpan sebagai '{output_path}'")

if __name__ == '__main__':
    embed_watermark()
