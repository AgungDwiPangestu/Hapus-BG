from PIL import Image

def make_transparent(input_path, output_path, target_color, tolerance=50):
    """
    Mengubah warna tertentu menjadi transparan.
    
    :param input_path: Lokasi file gambar input
    :param output_path: Lokasi file gambar output
    :param target_color: Tuple warna RGB yang ingin dihapus (R, G, B)
    :param tolerance: Tingkat toleransi (0-255). Semakin besar, warna yang mirip juga ikut terhapus.
    """
    try:
        # Buka gambar dan ubah mode ke RGBA (agar mendukung transparansi)
        img = Image.open(input_path)
        img = img.convert("RGBA")
        
        datas = img.getdata()
        
        newData = []
        
        # Pecah target warna
        tr, tg, tb = target_color
        
        print(f"Sedang memproses gambar... Menghapus warna RGB: {target_color}")
        
        for item in datas:
            # item[0]=R, item[1]=G, item[2]=B, item[3]=Alpha
            
            # Cek apakah pixel ini mirip dengan warna target (dalam batas toleransi)
            if (abs(item[0] - tr) < tolerance and 
                abs(item[1] - tg) < tolerance and 
                abs(item[2] - tb) < tolerance):
                
                # Jika mirip warna target, ubah jadi transparan (0 alpha)
                newData.append((255, 255, 255, 0))
            else:
                # Jika tidak, biarkan pixel apa adanya
                newData.append(item)
        
        # Simpan data baru ke gambar
        img.putdata(newData)
        img.save(output_path, "PNG")
        print(f"Berhasil! Gambar disimpan di: {output_path}")

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

# --- KONFIGURASI DI SINI ---

# 1. Nama file gambar Anda (pastikan satu folder dengan script ini)
input_file = "bingkai_saya.png" 

# 2. Nama file hasil
output_file = "bingkai_transparan.png"

# 3. Warna yang mau dihapus (Format RGB)
# Hijau Stabilo (Green Screen) = (0, 255, 0)
# Hitam = (0, 0, 0)
# Putih = (255, 255, 255)
warna_yang_dihapus = (0, 255, 0) 

# Jalankan fungsi
if __name__ == "__main__":
    make_transparent(input_file, output_file, warna_yang_dihapus)