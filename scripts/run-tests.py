import os
import sys
import subprocess

TEST_COMMANDS = [
        # ==================== STREAM CIPHER ====================
        ("python src/cryptopic.py --mode encrypt --in imgs/input/noise_texture.png --out imgs/encrypted/noise_texture_stream.bin --algo stream --key \"test123\"", 
         "Шифрование noise_texture (stream)"),
        ("python src/cryptopic.py --mode decrypt --in imgs/encrypted/noise_texture_stream.bin --out imgs/decrypted/noise_texture_stream_dec.bmp --algo stream --key \"test123\" --meta imgs/encrypted/noise_texture_stream.bin.meta.json",
         "Дешифрование noise_texture (stream)"),
        
        ("python src/cryptopic.py --mode encrypt --in imgs/input/checkerboard.png --out imgs/encrypted/checkerboard_stream.bin --algo stream --key \"test123\"",
         "Шифрование checkerboard (stream)"),
        ("python src/cryptopic.py --mode decrypt --in imgs/encrypted/checkerboard_stream.bin --out imgs/decrypted/checkerboard_stream_dec.bmp --algo stream --key \"test123\" --meta imgs/encrypted/checkerboard_stream.bin.meta.json",
         "Дешифрование checkerboard (stream)"),
        
        ("python src/cryptopic.py --mode encrypt --in imgs/input/gradient.png --out imgs/encrypted/gradient_stream.bin --algo stream --key \"test123\"",
         "Шифрование gradient (stream)"),
        ("python src/cryptopic.py --mode decrypt --in imgs/encrypted/gradient_stream.bin --out imgs/decrypted/gradient_stream_dec.bmp --algo stream --key \"test123\" --meta imgs/encrypted/gradient_stream.bin.meta.json",
         "Дешифрование gradient (stream)"),
        
        ("python src/cryptopic.py --mode encrypt --in imgs/input/my.jpg --out imgs/encrypted/my_stream.bin --algo stream --key \"test123\"",
         "Шифрование my.jpg (stream)"),
        ("python src/cryptopic.py --mode decrypt --in imgs/encrypted/my_stream.bin --out imgs/decrypted/my_stream_dec.bmp --algo stream --key \"test123\" --meta imgs/encrypted/my_stream.bin.meta.json",
         "Дешифрование my.jpg (stream)"),
        
        # ==================== AES-ECB ====================
        ("python src/cryptopic.py --mode encrypt --in imgs/input/noise_texture.png --out imgs/encrypted/noise_texture_aes_ecb.bin --algo aes-ecb --key \"test123\"",
         "Шифрование noise_texture (AES-ECB)"),
        ("python src/cryptopic.py --mode decrypt --in imgs/encrypted/noise_texture_aes_ecb.bin --out imgs/decrypted/noise_texture_aes_ecb_dec.bmp --algo aes-ecb --key \"test123\" --meta imgs/encrypted/noise_texture_aes_ecb.bin.meta.json",
         "Дешифрование noise_texture (AES-ECB)"),
        
        ("python src/cryptopic.py --mode encrypt --in imgs/input/checkerboard.png --out imgs/encrypted/checkerboard_aes_ecb.bin --algo aes-ecb --key \"test123\"",
         "Шифрование checkerboard (AES-ECB)"),
        ("python src/cryptopic.py --mode decrypt --in imgs/encrypted/checkerboard_aes_ecb.bin --out imgs/decrypted/checkerboard_aes_ecb_dec.bmp --algo aes-ecb --key \"test123\" --meta imgs/encrypted/checkerboard_aes_ecb.bin.meta.json",
         "Дешифрование checkerboard (AES-ECB)"),
        
        ("python src/cryptopic.py --mode encrypt --in imgs/input/gradient.png --out imgs/encrypted/gradient_aes_ecb.bin --algo aes-ecb --key \"test123\"",
         "Шифрование gradient (AES-ECB)"),
        ("python src/cryptopic.py --mode decrypt --in imgs/encrypted/gradient_aes_ecb.bin --out imgs/decrypted/gradient_aes_ecb_dec.bmp --algo aes-ecb --key \"test123\" --meta imgs/encrypted/gradient_aes_ecb.bin.meta.json",
         "Дешифрование gradient (AES-ECB)"),
        
        ("python src/cryptopic.py --mode encrypt --in imgs/input/my.jpg --out imgs/encrypted/my_aes_ecb.bin --algo aes-ecb --key \"test123\"",
         "Шифрование my.jpg (AES-ECB)"),
        ("python src/cryptopic.py --mode decrypt --in imgs/encrypted/my_aes_ecb.bin --out imgs/decrypted/my_aes_ecb_dec.bmp --algo aes-ecb --key \"test123\" --meta imgs/encrypted/my_aes_ecb.bin.meta.json",
         "Дешифрование my.jpg (AES-ECB)"),
        
        # ==================== AES-CBC ====================
        ("python src/cryptopic.py --mode encrypt --in imgs/input/noise_texture.png --out imgs/encrypted/noise_texture_aes_cbc.bin --algo aes-cbc --key \"test123\"",
         "Шифрование noise_texture (AES-CBC)"),
        ("python src/cryptopic.py --mode decrypt --in imgs/encrypted/noise_texture_aes_cbc.bin --out imgs/decrypted/noise_texture_aes_cbc_dec.bmp --algo aes-cbc --key \"test123\" --meta imgs/encrypted/noise_texture_aes_cbc.bin.meta.json",
         "Дешифрование noise_texture (AES-CBC)"),
        
        ("python src/cryptopic.py --mode encrypt --in imgs/input/checkerboard.png --out imgs/encrypted/checkerboard_aes_cbc.bin --algo aes-cbc --key \"test123\"",
         "Шифрование checkerboard (AES-CBC)"),
        ("python src/cryptopic.py --mode decrypt --in imgs/encrypted/checkerboard_aes_cbc.bin --out imgs/decrypted/checkerboard_aes_cbc_dec.bmp --algo aes-cbc --key \"test123\" --meta imgs/encrypted/checkerboard_aes_cbc.bin.meta.json",
         "Дешифрование checkerboard (AES-CBC)"),
        
        ("python src/cryptopic.py --mode encrypt --in imgs/input/gradient.png --out imgs/encrypted/gradient_aes_cbc.bin --algo aes-cbc --key \"test123\"",
         "Шифрование gradient (AES-CBC)"),
        ("python src/cryptopic.py --mode decrypt --in imgs/encrypted/gradient_aes_cbc.bin --out imgs/decrypted/gradient_aes_cbc_dec.bmp --algo aes-cbc --key \"test123\" --meta imgs/encrypted/gradient_aes_cbc.bin.meta.json",
         "Дешифрование gradient (AES-CBC)"),
        
        ("python src/cryptopic.py --mode encrypt --in imgs/input/my.jpg --out imgs/encrypted/my_aes_cbc.bin --algo aes-cbc --key \"test123\"",
         "Шифрование my.jpg (AES-CBC)"),
        ("python src/cryptopic.py --mode decrypt --in imgs/encrypted/my_aes_cbc.bin --out imgs/decrypted/my_aes_cbc_dec.bmp --algo aes-cbc --key \"test123\" --meta imgs/encrypted/my_aes_cbc.bin.meta.json",
         "Дешифрование my.jpg (AES-CBC)"),
        
        # ==================== AES-CTR ====================
        ("python src/cryptopic.py --mode encrypt --in imgs/input/noise_texture.png --out imgs/encrypted/noise_texture_aes_ctr.bin --algo aes-ctr --key \"test123\"",
         "Шифрование noise_texture (AES-CTR)"),
        ("python src/cryptopic.py --mode decrypt --in imgs/encrypted/noise_texture_aes_ctr.bin --out imgs/decrypted/noise_texture_aes_ctr_dec.bmp --algo aes-ctr --key \"test123\" --meta imgs/encrypted/noise_texture_aes_ctr.bin.meta.json",
         "Дешифрование noise_texture (AES-CTR)"),
        
        ("python src/cryptopic.py --mode encrypt --in imgs/input/checkerboard.png --out imgs/encrypted/checkerboard_aes_ctr.bin --algo aes-ctr --key \"test123\"",
         "Шифрование checkerboard (AES-CTR)"),
        ("python src/cryptopic.py --mode decrypt --in imgs/encrypted/checkerboard_aes_ctr.bin --out imgs/decrypted/checkerboard_aes_ctr_dec.bmp --algo aes-ctr --key \"test123\" --meta imgs/encrypted/checkerboard_aes_ctr.bin.meta.json",
         "Дешифрование checkerboard (AES-CTR)"),
        
        ("python src/cryptopic.py --mode encrypt --in imgs/input/gradient.png --out imgs/encrypted/gradient_aes_ctr.bin --algo aes-ctr --key \"test123\"",
         "Шифрование gradient (AES-CTR)"),
        ("python src/cryptopic.py --mode decrypt --in imgs/encrypted/gradient_aes_ctr.bin --out imgs/decrypted/gradient_aes_ctr_dec.bmp --algo aes-ctr --key \"test123\" --meta imgs/encrypted/gradient_aes_ctr.bin.meta.json",
         "Дешифрование gradient (AES-CTR)"),
        
        ("python src/cryptopic.py --mode encrypt --in imgs/input/my.jpg --out imgs/encrypted/my_aes_ctr.bin --algo aes-ctr --key \"test123\"",
         "Шифрование my.jpg (AES-CTR)"),
        ("python src/cryptopic.py --mode decrypt --in imgs/encrypted/my_aes_ctr.bin --out imgs/decrypted/my_aes_ctr_dec.bmp --algo aes-ctr --key \"test123\" --meta imgs/encrypted/my_aes_ctr.bin.meta.json",
         "Дешифрование my.jpg (AES-CTR)"),
        
        # ==================== AES-CFB ====================
        ("python src/cryptopic.py --mode encrypt --in imgs/input/noise_texture.png --out imgs/encrypted/noise_texture_aes_cfb.bin --algo aes-cfb --key \"test123\"",
         "Шифрование noise_texture (AES-CFB)"),
        ("python src/cryptopic.py --mode decrypt --in imgs/encrypted/noise_texture_aes_cfb.bin --out imgs/decrypted/noise_texture_aes_cfb_dec.bmp --algo aes-cfb --key \"test123\" --meta imgs/encrypted/noise_texture_aes_cfb.bin.meta.json",
         "Дешифрование noise_texture (AES-CFB)"),
        
        ("python src/cryptopic.py --mode encrypt --in imgs/input/checkerboard.png --out imgs/encrypted/checkerboard_aes_cfb.bin --algo aes-cfb --key \"test123\"",
         "Шифрование checkerboard (AES-CFB)"),
        ("python src/cryptopic.py --mode decrypt --in imgs/encrypted/checkerboard_aes_cfb.bin --out imgs/decrypted/checkerboard_aes_cfb_dec.bmp --algo aes-cfb --key \"test123\" --meta imgs/encrypted/checkerboard_aes_cfb.bin.meta.json",
         "Дешифрование checkerboard (AES-CFB)"),
        
        ("python src/cryptopic.py --mode encrypt --in imgs/input/gradient.png --out imgs/encrypted/gradient_aes_cfb.bin --algo aes-cfb --key \"test123\"",
         "Шифрование gradient (AES-CFB)"),
        ("python src/cryptopic.py --mode decrypt --in imgs/encrypted/gradient_aes_cfb.bin --out imgs/decrypted/gradient_aes_cfb_dec.bmp --algo aes-ecb --key \"test123\" --meta imgs/encrypted/gradient_aes_cfb.bin.meta.json",
         "Дешифрование gradient (AES-CFB)"),
        
        ("python src/cryptopic.py --mode encrypt --in imgs/input/my.jpg --out imgs/encrypted/my_aes_cfb.bin --algo aes-cfb --key \"test123\"",
         "Шифрование my.jpg (AES-CFB)"),
        ("python src/cryptopic.py --mode decrypt --in imgs/encrypted/my_aes_cfb.bin --out imgs/decrypted/my_aes_cfb_dec.bmp --algo aes-cfb --key \"test123\" --meta imgs/encrypted/my_aes_cfb.bin.meta.json",
         "Дешифрование my.jpg (AES-CFB)"),
        
    ]

def run_command(cmd, description=""):
    if description:
        print(f"\n {description}")
    print(f" Выполняю: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(" Успешно")
        return True
    else:
        print(f" Ошибка: {result.stderr}")
        return False

def run_all_tests():
    print(" ЗАПУСК ВСЕХ ТЕСТОВЫХ КОМАНД")
    print("=" * 60)
    
    # Создаем директории
    os.makedirs("imgs/encrypted", exist_ok=True)
    os.makedirs("imgs/decrypted", exist_ok=True)
    
    success_count = 0
    total_commands = len(TEST_COMMANDS)
    
    for i, (cmd, description) in enumerate(TEST_COMMANDS, 1):
        print(f"\n[{i}/{total_commands}] {description}")
        
        if run_command(cmd, description):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f" ИТОГ: {success_count}/{total_commands} команд выполнено успешно")
    print(f"{'='*60}")

if __name__ == "__main__":
    run_all_tests()