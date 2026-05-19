import numpy as np
from PIL import Image
import math
import os

# Matriks Kuantisasi Luminance Standar JPEG
Q_luminance = np.array([
    [16,  11,  10,  16,  24,  40,  51,  61],
    [12,  12,  14,  19,  26,  58,  60,  55],
    [14,  13,  16,  24,  40,  57,  69,  56],
    [14,  17,  22,  29,  51,  87,  80,  62],
    [18,  22,  37,  56,  68, 109, 103,  77],
    [24,  35,  55,  64,  81, 104, 113,  92],
    [49,  64,  78,  87, 103, 121, 120, 101],
    [72,  92,  95,  98, 112, 100, 103,  99]
], dtype=np.float32)

def scale_quantization_matrix(qf):
    """Fungsi untuk menskalakan Quantization Matrix berdasarkan Quality Factor (1-100)"""
    if qf < 1:
        qf = 1
    if qf > 100:
        qf = 100
        
    # Rumus scaling standar JPEG
    if qf < 50:
        S = 5000 / qf
    else:
        S = 200 - 2 * qf
        
    scaled_q = np.floor((S * Q_luminance + 50) / 100)
    scaled_q[scaled_q == 0] = 1 # Mencegah pembagian dengan nol
    return scaled_q

def simulate_jpeg_compression():
    input_path = 'foto_watermarked.png'
    
    if not os.path.exists(input_path):
        print(f"Error: Gambar '{input_path}' tidak ditemukan.")
        return

    # 1. membaca gambar
    print(f"Membaca gambar input: {input_path}")
    img = Image.open(input_path).convert('RGB')
    arr = np.array(img, dtype=np.float32)

    # 2. transformasi manual rgb keYCbCr
    print("Transformasi RGB ke YCbCr...")
    R = arr[:,:,0]
    G = arr[:,:,1]
    B = arr[:,:,2]

    Y = 0.299 * R + 0.587 * G + 0.114 * B
    Cb = -0.168736 * R - 0.331264 * G + 0.5 * B + 128
    Cr = 0.5 * R - 0.418688 * G - 0.081312 * B + 128

    h, w = Y.shape
    h_adj = h - (h % 8)
    w_adj = w - (w % 8)

    Y = Y[:h_adj, :w_adj]
    Cb = Cb[:h_adj, :w_adj]
    Cr = Cr[:h_adj, :w_adj]

    # 3. persiapan matriks DCT 8x8 manual
    N = 8
    C = np.zeros((N, N), dtype=np.float32)
    for i in range(N):
        for j in range(N):
            if i == 0:
                C[i, j] = math.sqrt(1/N)
            else:
                C[i, j] = math.sqrt(2/N) * math.cos((2*j + 1) * i * math.pi / (2*N))
    C_T = C.T

    # 4. looping evaluasi untuk berbagai nilai QF
    qf_list = [90, 70, 50, 30, 10]
    
    for qf in qf_list:
        print(f"\nMemulai simulasi kompresi dengan QF = {qf}")
        scaled_q = scale_quantization_matrix(qf)
        Y_compressed = np.copy(Y)
        
        # Proses per blok 8x8
        for r in range(0, h_adj, N):
            for c in range(0, w_adj, N):
                block = Y_compressed[r:r+N, c:c+N]
                
                # a. DCT 2D Manual
                D = np.dot(np.dot(C, block), C_T)
                
                # b. Kuantisasi Manual: Bagi koefisien DCT dengan Scaled Quantization Matrix, lalu bulatkan
                D_quantized = np.round(D / scaled_q)
                
                # c. Dekuantisasi: Kalikan kembali dengan Scaled Quantization Matrix
                D_dequantized = D_quantized * scaled_q
                
                # d. Inverse DCT 2D Manual
                block_idct = np.dot(np.dot(C_T, D_dequantized), C)
                
                # Masukkan kembali ke matriks gambar
                Y_compressed[r:r+N, c:c+N] = block_idct

        # 5. transformasi YCbCr kembali ke RGB
        R_new = Y_compressed + 1.402 * (Cr - 128)
        G_new = Y_compressed - 0.344136 * (Cb - 128) - 0.714136 * (Cr - 128)
        B_new = Y_compressed + 1.772 * (Cb - 128)

        # Clipping dan convert ke int [0, 255] sesuai instruksi
        R_new = np.clip(np.round(R_new), 0, 255).astype(np.uint8)
        G_new = np.clip(np.round(G_new), 0, 255).astype(np.uint8)
        B_new = np.clip(np.round(B_new), 0, 255).astype(np.uint8)

        img_out_arr = np.stack([R_new, G_new, B_new], axis=2)

        # 6. simpan hasil kompresi
        output_filename = f'compressed_QF{qf}.png'
        img_out = Image.fromarray(img_out_arr, mode='RGB')
        img_out.save(output_filename)
        print(f"-> Disimpan sebagai: {output_filename}")

    print("\nSimulasi kompresi selesai!")

if __name__ == '__main__':
    simulate_jpeg_compression()
