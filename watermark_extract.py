import numpy as np
from PIL import Image
import math
import os

def extract_watermark(image_path, orig_wm_shape=(64, 64), Q=20):
    if not os.path.exists(image_path):
        print(f"File {image_path} tidak ditemukan.")
        return None

    # 1. membaca gambar
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img, dtype=np.float32)

    # 2. rgb ke YCbCr manual (ambil channel Y saja)
    R = arr[:,:,0]
    G = arr[:,:,1]
    B = arr[:,:,2]
    Y = 0.299 * R + 0.587 * G + 0.114 * B

    h, w = Y.shape
    h_adj = h - (h % 8)
    w_adj = w - (w % 8)
    Y = Y[:h_adj, :w_adj]

    # 3. matriks DCT 8x8 manual
    N = 8
    C = np.zeros((N, N), dtype=np.float32)
    for i in range(N):
        for j in range(N):
            if i == 0:
                C[i, j] = math.sqrt(1/N)
            else:
                C[i, j] = math.sqrt(2/N) * math.cos((2*j + 1) * i * math.pi / (2*N))
    C_T = C.T

    # 4. proses ekstraksi
    wm_len = orig_wm_shape[0] * orig_wm_shape[1]
    extracted_bits = []

    for r in range(0, h_adj, N):
        for c in range(0, w_adj, N):
            if len(extracted_bits) >= wm_len:
                break
            
            # Ambil blok 8x8
            block = Y[r:r+N, c:c+N]
            
            # Lakukan DCT
            D = np.dot(np.dot(C, block), C_T)
            
            # Ekstraksi bit menggunakan teknik QIM (Odd/Even) yang sama
            val = round(D[4, 4] / Q)
            if val % 2 == 0:
                extracted_bits.append(0) # Jika genap, berarti bit 0
            else:
                extracted_bits.append(1) # Jika ganjil, berarti bit 1

        if len(extracted_bits) >= wm_len:
            break
            
    # Jika gambar terlalu kecil (seharusnya tidak terjadi jika ukuran sesuai)
    while len(extracted_bits) < wm_len:
        extracted_bits.append(0)

    # 5. rekonstruksi menjadi gambar biner
    extracted_arr = np.array(extracted_bits).reshape(orig_wm_shape)
    
    return extracted_arr

def compare_watermarks():
    # Load original watermark
    wm_img = Image.open('watermark.png').convert('L')
    wm_arr = np.array(wm_img)
    wm_bin = (wm_arr >= 128).astype(np.uint8)
    
    qf_list = [90, 70, 50, 30, 10]
    
    print("--- HASIL EKSTRAKSI & EVALUASI KETAHANAN WATERMARK ---")
    for qf in qf_list:
        file_path = f'compressed_QF{qf}.png'
        ext_wm = extract_watermark(file_path, orig_wm_shape=(64, 64), Q=20)
        
        if ext_wm is not None:
            # Hitung akurasi (persentase bit yang sama)
            correct = np.sum(ext_wm == wm_bin)
            total = 64 * 64
            accuracy = (correct / total) * 100
            
            # Simpan hasil ekstraksi untuk verifikasi visual
            ext_img = Image.fromarray((ext_wm * 255).astype(np.uint8), mode='L')
            ext_img.save(f'extracted_QF{qf}.png')
            
            print(f"QF = {qf:2d} -> Akurasi: {accuracy:6.2f}% (Tersimpan sbg extracted_QF{qf}.png)")

if __name__ == '__main__':
    compare_watermarks()
