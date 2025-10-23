import argparse
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_stream import stream_encrypt, stream_decrypt
from crypto_block import block_encrypt, block_decrypt

def main():
    parser = argparse.ArgumentParser(description='CryptoPic - Image Encryption Tool')
    
    # Основные параметры
    parser.add_argument('--mode', choices=['encrypt', 'decrypt'], required=True, 
                       help='Режим работы: encrypt или decrypt')
    
    # Параметры для encrypt/decrypt режимов
    parser.add_argument('--in', dest='input_file', required=True,
                       help='Входной файл (изображение или шифр)')
    parser.add_argument('--out', dest='output_file', required=True,
                       help='Выходной файл')
    parser.add_argument('--algo', choices=['stream', 'aes-ecb', 'aes-cbc', 'aes-ctr', 'aes-cfb'], required=True,
                       help='Алгоритм шифрования')
    parser.add_argument('--key', required=True,
                       help='Ключ шифрования')
    
    # Опциональные параметры
    parser.add_argument('--iv', help='IV в hex формате (для CBC)')
    parser.add_argument('--nonce', help='Nonce в hex формате (для CTR)')
    parser.add_argument('--meta', help='Файл с метаданными для дешифрования')
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'encrypt':
            handle_encrypt(args)
        elif args.mode == 'decrypt':
            handle_decrypt(args)
            
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

def handle_encrypt(args):
    """Обработка шифрования"""
    print(f"Шифруем {args.input_file} алгоритмом {args.algo}...")
    
    # Определяем режим для блочного шифрования
    mode = None
    if args.algo.startswith('aes-'):
        mode = args.algo.replace('aes-', '')  # 'ecb', 'cbc', 'ctr'
    
    # алгоритм шифрования
    if args.algo == 'stream':
        encrypted_data, meta = stream_encrypt(args.input_file, args.key, args.iv)
    
    elif args.algo.startswith('aes-'):
        # Используем block_encrypt для всех AES режимов
        encrypted_data, meta = block_encrypt(
            args.input_file, 
            args.key, 
            mode=mode,
            iv=args.iv,
            nonce=args.nonce
        )
    
    # сохранение зашифрованных данных
    with open(args.output_file, 'wb') as f:
        f.write(encrypted_data)
    
    # сохранение метаданных
    meta_filename = args.output_file + ".meta.json"
    if args.meta:
        meta_filename = args.meta
    
    with open(meta_filename, 'w') as f:
        json.dump(meta, f, indent=2)
    
    print(f"Успешно зашифровано в {args.output_file}")
    print(f"Метаданные сохранены в {meta_filename}")
    if meta.get('iv'):
        print(f"IV: {meta['iv']}")
    if meta.get('nonce'):
        print(f"Nonce: {meta['nonce']}")

def handle_decrypt(args):
    """Обработка дешифрования"""
    print(f"Дешифруем {args.input_file} алгоритмом {args.algo}...")
    
    # метаданные
    meta = {}
    if args.meta:
        with open(args.meta, 'r') as f:
            meta = json.load(f)
    else:
        # поиск .meta.json файл
        meta_path = args.input_file + ".meta.json"
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                meta = json.load(f)
        else:
            print("Предупреждение: файл метаданных не найден")
    
    # алгоритм дешифрования
    if args.algo == 'stream':
        decrypted_data = stream_decrypt(args.input_file, args.key, meta)
    
    elif args.algo.startswith('aes-'):
        # Используем block_decrypt для всех AES режимов
        decrypted_data = block_decrypt(args.input_file, args.key, meta)
    
    # восстановление изображения
    from PIL import Image
    img = Image.frombytes(meta['mode'], meta['original_size'], decrypted_data)
    img.save(args.output_file)
    
    print(f"Успешно дешифровано в {args.output_file}")

if __name__ == "__main__":
    main()