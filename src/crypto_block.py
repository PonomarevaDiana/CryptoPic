from PIL import Image
import os
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Random import get_random_bytes

#шифрование блоков независимо
def ecb_encrypt(data, key):
    cipher = AES.new(key, AES.MODE_ECB)
    #дополнение данных до размера блока
    padded_data = pad(data, AES.block_size)
    return cipher.encrypt(padded_data)

def ecb_decrypt(encrypted_data, key):
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_data = cipher.decrypt(encrypted_data)
    return unpad(decrypted_data, AES.block_size)

#шифрование с цепочкой блоков
def cbc_encrypt(data, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    padded_data = pad(data, AES.block_size)
    return cipher.encrypt(padded_data)

def cbc_decrypt(encrypted_data, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    decrypted_data = cipher.decrypt(encrypted_data)
    return unpad(decrypted_data, AES.block_size)

#поточный режим, паддинга не требуется
def cfb_encrypt(data, key, iv):
    cipher = AES.new(key, AES.MODE_CFB, iv=iv, segment_size=128)
    return cipher.encrypt(data)

def cfb_decrypt(encrypted_data, key, iv):
    cipher = AES.new(key, AES.MODE_CFB, iv=iv, segment_size=128)
    return cipher.decrypt(encrypted_data)

#шифр с уникальным nonce, паддинг не нужен
def ctr_encrypt(data, key, nonce):
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    return cipher.encrypt(data)

def ctr_decrypt(encrypted_data, key, nonce):
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    return cipher.decrypt(encrypted_data)

def initialize_aes_key(key_string):
    if isinstance(key_string, bytes):
        key_bytes = key_string
    else:
        key_bytes = key_string.encode('utf-8')

    #простое дополнение/обрезание до 16 байт для AES-128
    if len(key_bytes) < 16:
        key_bytes = key_bytes.ljust(16, b'\0')
    elif len(key_bytes) > 16:
        key_bytes = key_bytes[:16]
    
    return key_bytes

def generate_secure_iv():
    return get_random_bytes(AES.block_size) 

def generate_secure_nonce():
    return get_random_bytes(8)  # 8 байт для CTR nonce

def simple_hash(data, output_length=32, return_hex=False):
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    # Простой алгоритм перемешивания
    result = bytearray(output_length)
    
    #заполнение первоначальное 
    for i in range(output_length):
        result[i] = (data[i % len(data)] + i * 37) & 0xFF
    
    # Раунды перемешивания
    for round in range(5):
        for i in range(output_length):
            # XOR с соседним байтом
            result[i] ^= result[(i + 11) % output_length]
            result[i] = (result[i] * 167 + 113) & 0xFF
    
    if return_hex:
        return result.hex()
    else:
        return bytes(result)

def block_encrypt(image_path, key_string, mode='cbc', iv=None, nonce=None):
    img = Image.open(image_path)
    img_bytes = img.tobytes()
    
    #ключ
    key_bytes = initialize_aes_key(key_string)
    
    #IV/nonce - конвертируем строки в bytes
    if mode in ['cbc', 'cfb']:
        iv = generate_secure_iv()
        print(f"Сгенерирован случайный IV для {mode.upper()}: {iv.hex()}")
    
    elif mode == 'ctr':
        if nonce is None:
            nonce = generate_secure_nonce()
            print(f"Сгенерирован случайный nonce для CTR: {nonce.hex()}")
        else:
            if isinstance(nonce, str):
                nonce = bytes.fromhex(nonce)
            print(f"Используется nonce: {nonce.hex()}")
    
    #режим шифрования
    if mode == 'ecb':
        encrypted_bytes = ecb_encrypt(img_bytes, key_bytes)
        print("Режим: ECB")
        
    elif mode == 'cbc':
        encrypted_bytes = cbc_encrypt(img_bytes, key_bytes, iv)
        print("Режим: CBC")
        
    elif mode == 'cfb':
        encrypted_bytes = cfb_encrypt(img_bytes, key_bytes, iv)
        print("Режим: CFB")
        
    elif mode == 'ctr':
        encrypted_bytes = ctr_encrypt(img_bytes, key_bytes, nonce)
        print("Режим: CTR")
        
    else:
        raise ValueError(f"Неизвестный режим шифрования: {mode}")
    
    #метаданные
    meta = {
        "algorithm": f"AES-{mode.upper()}",
        "original_size": img.size,
        "mode": img.mode,
        "key_size": len(key_bytes),
        "original_filename": os.path.basename(image_path),
        "key_hash": simple_hash(key_string, 16, return_hex=True),
        "requires_padding": mode in ['ecb', 'cbc']
    }
    
    #добавляем IV/nonce в метаданные
    if mode in ['cbc', 'cfb']:
        meta['iv'] = iv.hex()
    
    if mode == 'ctr':
        meta['nonce'] = nonce.hex()
    
    return encrypted_bytes, meta


def block_decrypt(input_path, key_string, meta):

    # Загружаем зашифрованные данные
    with open(input_path, 'rb') as f:
        encrypted_bytes = f.read()
    
    # Проверяем метаданные
    algorithm = meta.get('algorithm', '')
    if not algorithm.startswith('AES-'):
        raise ValueError("Неверный алгоритм в метаданных!")
    
    mode = algorithm.split('-')[1].lower()
    
    # Проверяем хэш ключа
    expected_hash = meta.get('key_hash')
    if expected_hash:
        actual_hash = simple_hash(key_string, 16, return_hex=True)
        if actual_hash != expected_hash:
            print("Предупреждение: хэш ключа не совпадает! Возможно неверный ключ.")
    
    # Инициализируем ключ
    key_bytes = initialize_aes_key(key_string)
    
    # Получаем IV/nonce из метаданных
    iv = None
    nonce = None
    
    if mode in ['cbc', 'cfb']:
        iv_hex = meta.get('iv')
        if not iv_hex:
            raise ValueError(f"IV не найден в метаданных для режима {mode.upper()}!")
        iv = bytes.fromhex(iv_hex)
        print(f"Используется IV из метаданных: {iv_hex[:16]}...")
    
    if mode == 'ctr':
        nonce_hex = meta.get('nonce')
        if not nonce_hex:
            raise ValueError("Nonce не найден в метаданных для режима CTR!")
        nonce = bytes.fromhex(nonce_hex)
        print(f"Используется nonce из метаданных: {nonce_hex[:16]}...")
    
    # Выбираем режим дешифрования
    if mode == 'ecb':
        decrypted_bytes = ecb_decrypt(encrypted_bytes, key_bytes)
        
    elif mode == 'cbc':
        decrypted_bytes = cbc_decrypt(encrypted_bytes, key_bytes, iv)
        
    elif mode == 'cfb':
        decrypted_bytes = cfb_decrypt(encrypted_bytes, key_bytes, iv)
        
    elif mode == 'ctr':
        decrypted_bytes = ctr_decrypt(encrypted_bytes, key_bytes, nonce)
        
    else:
        raise ValueError(f"Неизвестный режим шифрования: {mode}")
    
    return decrypted_bytes
