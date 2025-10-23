import math
import json
import csv
from PIL import Image
import os
from collections import Counter
import statistics
from typing import Dict, Any, Tuple


def save_metrics_to_json(
    metrics_data: Dict[str, Any], filename: str, subfolder: str = "metrics"
) -> str:
    filepath = f"results/{subfolder}/{filename}"

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2, ensure_ascii=False)

    print(f"Метрики сохранены в: {filepath}")
    return filepath


# энтропия шеннона из байтов
"""
H = -∑(p_i × log₂(p_i))
H - энтропия Шеннона (в битах)
p_i - вероятность появления i-го байта (значение от 0x00 до 0xFF)
∑ - суммирование по всем возможным байтам (i = 0...255)
log₂ - логарифм по основанию 2
"""


def calculate_entropy_from_bytes(data_bytes: bytes) -> float:
    if not data_bytes:
        return 0.0

    byte_counts = Counter(data_bytes)
    total_bytes = len(data_bytes)

    entropy = 0.0
    for count in byte_counts.values():
        probability = count / total_bytes
        if probability > 0:
            entropy -= probability * math.log2(probability)

    return entropy


# энтропия шеннона для изображения
def calculate_entropy(image_path: str) -> float:
    try:
        img = Image.open(image_path)
        img_bytes = img.tobytes()
        return calculate_entropy_from_bytes(img_bytes)
    except Exception as e:
        print(f"Ошибка вычисления энтропии для {image_path}: {e}")
        return 0.0


# энтропия для каждого канала исходного изображения
def calculate_channel_entropy_for_image(image_path: str) -> Dict[str, float]:
    try:
        img = Image.open(image_path)
        channels = img.split()

        channel_entropies = {}
        for i, channel in enumerate(channels):
            channel_bytes = channel.tobytes()
            entropy = calculate_entropy_from_bytes(channel_bytes)

            channel_name = ["R", "G", "B", "A"][i] if len(channels) > 1 else "L"
            channel_entropies[channel_name] = entropy

        return channel_entropies
    except Exception as e:
        print(f"Ошибка вычисления энтропии каналов для {image_path}: {e}")
        return {}


# энтропия для каждого канала зашифрованных данных
def calculate_channel_entropy_for_encrypted(
    encrypted_bytes: bytes, original_size: tuple, original_mode: str
) -> Dict[str, float]:
    try:
        channel_entropies = {}

        if original_mode == "RGB":
            expected_size = original_size[0] * original_size[1] * 3
            if len(encrypted_bytes) >= expected_size:
                # Создаем временное изображение из зашифрованных данных
                temp_img = Image.frombytes(
                    "RGB", original_size, encrypted_bytes[:expected_size]
                )
                channels = temp_img.split()

                for i, channel in enumerate(channels):
                    channel_bytes = channel.tobytes()
                    entropy = calculate_entropy_from_bytes(channel_bytes)
                    channel_name = ["R", "G", "B"][i]
                    channel_entropies[channel_name] = entropy
            else:
                print(f"Недостаточно данных для анализа каналов RGB")

        elif original_mode == "L":
            expected_size = original_size[0] * original_size[1]
            if len(encrypted_bytes) >= expected_size:
                temp_img = Image.frombytes(
                    "L", original_size, encrypted_bytes[:expected_size]
                )
                channel_bytes = temp_img.tobytes()
                entropy = calculate_entropy_from_bytes(channel_bytes)
                channel_entropies["L"] = entropy

        elif original_mode == "RGBA":
            expected_size = original_size[0] * original_size[1] * 4
            if len(encrypted_bytes) >= expected_size:
                temp_img = Image.frombytes(
                    "RGBA", original_size, encrypted_bytes[:expected_size]
                )
                channels = temp_img.split()

                for i, channel in enumerate(channels):
                    channel_bytes = channel.tobytes()
                    entropy = calculate_entropy_from_bytes(channel_bytes)
                    channel_name = ["R", "G", "B", "A"][i]
                    channel_entropies[channel_name] = entropy

        # Если не удалось создать изображение, анализируем байты как отдельные "каналы"
        if not channel_entropies:
            print("Используем адаптивный анализ каналов для зашифрованных данных")
            channel_entropies = calculate_adaptive_channel_entropy(encrypted_bytes)

        return channel_entropies

    except Exception as e:
        print(f"Ошибка вычисления энтропии каналов для зашифрованных данных: {e}")
        return calculate_adaptive_channel_entropy(encrypted_bytes)


# энтропия для произвольных байтовых данных
def calculate_adaptive_channel_entropy(data_bytes: bytes) -> Dict[str, float]:
    try:
        if len(data_bytes) == 0:
            return {"Channel_1": 0.0}
        # Разделяем данные на 3 "канала" для анализа
        channel_entropies = {}

        if len(data_bytes) >= 3:
            # Для RGB-подобного анализа
            channel1 = bytes([data_bytes[i] for i in range(0, len(data_bytes), 3)])
            channel2 = (
                bytes([data_bytes[i] for i in range(1, len(data_bytes), 3)])
                if len(data_bytes) > 1
                else b""
            )
            channel3 = (
                bytes([data_bytes[i] for i in range(2, len(data_bytes), 3)])
                if len(data_bytes) > 2
                else b""
            )

            channel_entropies["Encrypted_R"] = calculate_entropy_from_bytes(channel1)
            if channel2:
                channel_entropies["Encrypted_G"] = calculate_entropy_from_bytes(
                    channel2
                )
            if channel3:
                channel_entropies["Encrypted_B"] = calculate_entropy_from_bytes(
                    channel3
                )
        else:
            # Для маленьких данных - один канал
            channel_entropies["Encrypted_Data"] = calculate_entropy_from_bytes(
                data_bytes
            )

        return channel_entropies

    except Exception as e:
        print(f"Ошибка в адаптивном анализе каналов: {e}")
        return {"Encrypted_Data": calculate_entropy_from_bytes(data_bytes)}


# коэффициент корреляции Пирсона
"""
corr = ∑[(x_i - μ_x) × (y_i - μ_y)] / √[∑(x_i - μ_x)² × ∑(y_i - μ_y)²]
x_i - значение текущего пикселя
y_i - значение соседнего пикселя
μ_x - среднее значение всех текущих пикселей
μ_y - среднее значение всех соседних пикселей
∑ - суммирование по всем парам соседних пикселей
"""


# коррелляция соседних пикселей для изображения
def calculate_correlation_from_image(
    image_path: str, direction: str = "horizontal"
) -> float:
    try:
        img = Image.open(image_path).convert("L")
        pixels = list(img.getdata())
        width, height = img.size

        return calculate_correlation_from_pixels(pixels, width, height, direction)
    except Exception as e:
        print(f"Ошибка вычисления корреляции для {image_path}: {e}")
        return 0.0


# коррелляция соседних пикселей из массива пикселей
def calculate_correlation_from_pixels(
    pixels: list, width: int, height: int, direction: str = "horizontal"
) -> float:
    try:
        correlations = []

        if direction == "horizontal":
            for y in range(height):
                for x in range(width - 1):
                    p1 = pixels[y * width + x]
                    p2 = pixels[y * width + x + 1]
                    correlations.append((p1, p2))
        elif direction == "vertical":
            for y in range(height - 1):
                for x in range(width):
                    p1 = pixels[y * width + x]
                    p2 = pixels[(y + 1) * width + x]
                    correlations.append((p1, p2))
        elif direction == "diagonal":
            for y in range(height - 1):
                for x in range(width - 1):
                    p1 = pixels[y * width + x]
                    p2 = pixels[(y + 1) * width + x + 1]
                    correlations.append((p1, p2))

        if len(correlations) < 2:
            return 0.0

        x_vals = [p[0] for p in correlations]
        y_vals = [p[1] for p in correlations]

        mean_x = statistics.mean(x_vals)
        mean_y = statistics.mean(y_vals)

        covariance = sum((x - mean_x) * (y - mean_y) for x, y in correlations)
        variance_x = sum((x - mean_x) ** 2 for x in x_vals)
        variance_y = sum((y - mean_y) ** 2 for y in y_vals)

        if variance_x == 0 or variance_y == 0:
            return 0.0

        correlation = covariance / math.sqrt(variance_x * variance_y)
        return correlation
    except Exception as e:
        print(f"Ошибка в calculate_correlation_from_pixels: {e}")
        return 0.0


# NPCR и UACI
"""
Измерение разницы в значениях пикселей между зашифрованным изображением и оригиналом

NPCR = (Количество_измененных_байтов / Общее_количество_байтов) × 100%
NPCR = [∑ D(i,j)] / (M × N) × 100%
где D(i,j) = 1 если байты разные, 0 если одинаковые

Среднее изменение интенсивности между зашифрованным изображением и исходным изображением

UACI = [∑ |B1(i) - B2(i)| / (Общее_количество_байтов × 255)] × 100%
UACI = [∑ |I₁(i,j) - I₂(i,j)| / (M × N × 255)] × 100%
"""


def calculate_npcr_uaci(bytes1: bytes, bytes2: bytes) -> Tuple[float, float]:
    try:
        if len(bytes1) != len(bytes2):
            # Используем минимальную длину для вычислений
            min_len = min(len(bytes1), len(bytes2))
            bytes1 = bytes1[:min_len]
            bytes2 = bytes2[:min_len]

        total_bytes = len(bytes1)
        if total_bytes == 0:
            return 0.0, 0.0

        changed_bytes = 0
        total_difference = 0

        for i in range(total_bytes):
            if bytes1[i] != bytes2[i]:
                changed_bytes += 1
                total_difference += abs(bytes1[i] - bytes2[i])

        npcr = (changed_bytes / total_bytes) * 100
        uaci = (total_difference / (total_bytes * 255)) * 100

        return npcr, uaci
    except Exception as e:
        print(f"Ошибка вычисления NPCR/UACI: {e}")
        return 0.0, 0.0


# avalanche effect
"""
Avalanche Effect = (Количество_измененных_битов / Общее_количество_битов) × 100%
AE = [∑ popcount(B1_i ⊕ B2_i)] / (N × 8) × 100%
"""


def calculate_avalanche_effect(bytes1: bytes, bytes2: bytes) -> float:
    try:
        if len(bytes1) != len(bytes2):
            # Используем минимальную длину для вычислений
            min_len = min(len(bytes1), len(bytes2))
            bytes1 = bytes1[:min_len]
            bytes2 = bytes2[:min_len]

        total_bits = len(bytes1) * 8
        if total_bits == 0:
            return 0.0

        changed_bits = 0

        for i in range(len(bytes1)):
            xor_result = bytes1[i] ^ bytes2[i]
            changed_bits += bin(xor_result).count("1")

        avalanche_percent = (changed_bits / total_bits) * 100
        return avalanche_percent
    except Exception as e:
        print(f"Ошибка вычисления avalanche effect: {e}")
        return 0.0


# анализ распределения байтов
"""
идеальное распределение: 
expected_per_byte = total_bytes / 256

отклонение для каждого байта:
deviation_i = |actual_count_i - expected_per_byte|

среднее отклонение:
avg_deviation = (∑ deviation_i) / 256

оценка равномерности:
uniformity_score = (1 - (avg_deviation / expected_per_byte)) × 100%

"""


def analyze_byte_distribution(data_bytes: bytes, label: str) -> Dict[str, Any]:
    try:
        byte_counts = Counter(data_bytes)
        total_bytes = len(data_bytes)

        if total_bytes == 0:
            return {
                "unique_bytes": 0,
                "total_bytes": 0,
                "avg_deviation": 0,
                "max_deviation": 0,
                "uniformity_score": 0,
            }

        # Идеальное равномерное распределение
        expected_per_byte = total_bytes / 256

        # Вычисление отклонения от равномерности
        deviations = []
        for byte_val in range(256):
            actual_count = byte_counts.get(byte_val, 0)
            deviation = abs(actual_count - expected_per_byte)
            deviations.append(deviation)

        avg_deviation = sum(deviations) / len(deviations)
        max_deviation = max(deviations)

        uniformity_score = (
            (1 - (avg_deviation / expected_per_byte)) * 100
            if expected_per_byte > 0
            else 0
        )

        return {
            "unique_bytes": len(byte_counts),
            "total_bytes": total_bytes,
            "avg_deviation": avg_deviation,
            "max_deviation": max_deviation,
            "uniformity_score": uniformity_score,
        }
    except Exception as e:
        print(f"Ошибка анализа распределения байтов ({label}): {e}")
        return {
            "unique_bytes": 0,
            "total_bytes": 0,
            "avg_deviation": 0,
            "max_deviation": 0,
            "uniformity_score": 0,
        }


# корреляция для зашифрованных данных
def calculate_encrypted_correlation(
    encrypted_bytes: bytes, image_size: tuple, image_mode: str, direction: str
) -> float:
    try:
        width, height = image_size
        # Определяем ожидаемый размер данных для изображения
        if image_mode == "RGB":
            expected_size = width * height * 3
            if len(encrypted_bytes) >= expected_size:
                temp_img = Image.frombytes(
                    "RGB", (width, height), encrypted_bytes[:expected_size]
                )
                temp_img = temp_img.convert("L")
                pixels = list(temp_img.getdata())
                return calculate_correlation_from_pixels(
                    pixels, width, height, direction
                )
        elif image_mode == "L":
            expected_size = width * height
            if len(encrypted_bytes) >= expected_size:
                temp_img = Image.frombytes(
                    "L", (width, height), encrypted_bytes[:expected_size]
                )
                pixels = list(temp_img.getdata())
                return calculate_correlation_from_pixels(
                    pixels, width, height, direction
                )
        elif image_mode == "RGBA":
            expected_size = width * height * 4
            if len(encrypted_bytes) >= expected_size:
                temp_img = Image.frombytes(
                    "RGBA", (width, height), encrypted_bytes[:expected_size]
                )
                temp_img = temp_img.convert("L")
                pixels = list(temp_img.getdata())
                return calculate_correlation_from_pixels(
                    pixels, width, height, direction
                )

        # Если данных недостаточно, используем адаптивный метод
        print(f" Недостаточно данных для корреляции, используем адаптивный метод")
        return calculate_adaptive_correlation(encrypted_bytes, direction)

    except Exception as e:
        print(f" Ошибка вычисления корреляции для зашифрованных данных: {e}")
        return calculate_adaptive_correlation(encrypted_bytes, direction)


# метод вычисления корреляции для произвольных байтов
def calculate_adaptive_correlation(data_bytes: bytes, direction: str) -> float:
    try:
        if len(data_bytes) < 2:
            return 0.0

        # Создаем виртуальную "изображение" из байтов
        virtual_width = min(100, len(data_bytes) // 2)
        virtual_height = max(1, len(data_bytes) // virtual_width)

        # Используем первые virtual_width * virtual_height байтов как пиксели
        pixels = list(data_bytes[: virtual_width * virtual_height])

        return calculate_correlation_from_pixels(
            pixels, virtual_width, virtual_height, direction
        )
    except Exception as e:
        print(f"Ошибка в адаптивной корреляции: {e}")
        return 0.0


# чувствительность к изменению ключа
def analyze_key_sensitivity(
    original_path: str, key1: str, key2: str, algorithm: str = "stream-rc4-custom"
) -> Dict[str, Any]:
    try:
        print(f"АНАЛИЗ ЧУВСТВИТЕЛЬНОСТИ К КЛЮЧУ")
        print(f"   Ключ 1: {key1}")
        print(f"   Ключ 2: {key2}")

        original_img = Image.open(original_path)
        original_bytes = original_img.tobytes()

        # Шифруем с первым ключом
        print("   Шифрование с ключом 1...")
        encrypted1 = encrypt_with_key(original_path, key1, algorithm)

        # Шифруем со вторым ключом
        print("   Шифрование с ключом 2...")
        encrypted2 = encrypt_with_key(original_path, key2, algorithm)

        # Вычисляем метрики различий между двумя шифрами
        print("   Вычисление метрик различий...")
        npcr, uaci = calculate_npcr_uaci(encrypted1, encrypted2)
        avalanche = calculate_avalanche_effect(encrypted1, encrypted2)

        # Энтропия каждого шифра
        entropy1 = calculate_entropy_from_bytes(encrypted1)
        entropy2 = calculate_entropy_from_bytes(encrypted2)

        # Распределение байтов
        distribution1 = analyze_byte_distribution(encrypted1, "key1_encrypted")
        distribution2 = analyze_byte_distribution(encrypted2, "key2_encrypted")

        results = {
            "test_type": "key_sensitivity",
            "original_image": original_path,
            "algorithm": algorithm,
            "keys": {"key1": key1, "key2": key2, "key_difference": f"Изменен 1 символ"},
            "sensitivity_metrics": {
                "npcr": npcr,
                "uaci": uaci,
                "avalanche_effect": avalanche,
                "entropy_key1": entropy1,
                "entropy_key2": entropy2,
                "entropy_difference": abs(entropy1 - entropy2),
            },
            "distributions": {"key1": distribution1, "key2": distribution2},
            "file_sizes": {
                "encrypted_key1": len(encrypted1),
                "encrypted_key2": len(encrypted2),
            },
        }

        print(f"Анализ чувствительности завершен:")
        print(f"   NPCR: {npcr:.6f}%")
        print(f"   UACI: {uaci:.6f}%")
        print(f"   Avalanche: {avalanche:.6f}%")

        return results

    except Exception as e:
        print(f"Ошибка анализа чувствительности к ключу: {e}")


def encrypt_with_key(image_path: str, key: str, algorithm: str) -> bytes:
    try:
        if algorithm.startswith("aes-"):
            # импортируем тут во избежать циклических импортов
            from crypto_block import block_encrypt

            mode = algorithm.replace("aes-", "")
            encrypted_data, meta = block_encrypt(image_path, key, mode=mode)
            return encrypted_data

        elif algorithm == "stream-rc4-custom":
            from crypto_stream import stream_encrypt

            encrypted_data, meta = stream_encrypt(image_path, key)
            return encrypted_data

        else:
            raise ValueError(f"Неизвестный алгоритм: {algorithm}")

    except ImportError as e:
        print(f" Модуль для {algorithm} не найден: {e}")


# анализ чувствительности к изменению IV/nonce
def analyze_iv_nonce_sensitivity(
    original_path: str, key: str, algorithm: str
) -> Dict[str, Any]:
    try:
        print(f"АНАЛИЗ ЧУВСТВИТЕЛЬНОСТИ К IV/NONCE")

        # шифруем с разными IV/nonce
        if algorithm in ["aes-cbc", "aes-cfb", "aes-ctr"]:
            print("   Тестирование с разными параметрами...")
            # с первыми параметрами
            encrypted1 = encrypt_with_key(original_path, key, algorithm)
            # со вторыми параметрами
            encrypted2 = encrypt_with_key(original_path, key, algorithm)

        else:
            print(f"   Алгоритм {algorithm} не использует IV/nonce")
            return {}

        # метрики различий
        npcr, uaci = calculate_npcr_uaci(encrypted1, encrypted2)
        avalanche = calculate_avalanche_effect(encrypted1, encrypted2)

        results = {
            "test_type": "iv_nonce_sensitivity",
            "algorithm": algorithm,
            "sensitivity_metrics": {
                "npcr": npcr,
                "uaci": uaci,
                "avalanche_effect": avalanche,
            },
        }

        print(f" Анализ чувствительности к параметрам завершен:")
        print(f"   NPCR: {npcr:.6f}%")

        return results

    except Exception as e:
        print(f" Ошибка анализа чувствительности к IV/nonce: {e}")
        return {}


def compute_all_metrics(
    original_path: str, encrypted_bin_path: str, image_name: str, algorithm: str
) -> Dict[str, Any]:

    # проверка существования файлов
    if not os.path.exists(original_path):
        raise FileNotFoundError(f"Исходный файл не найден: {original_path}")
    if not os.path.exists(encrypted_bin_path):
        raise FileNotFoundError(f"Зашифрованный файл не найден: {encrypted_bin_path}")

    try:
        with open(encrypted_bin_path, "rb") as f:
            encrypted_bytes = f.read()

        original_img = Image.open(original_path)
        original_bytes = original_img.tobytes()

        # дешифруем данные для корректного сравнения
        meta_path = encrypted_bin_path + ".meta.json"
        with open(meta_path, "r") as f:
            meta = json.load(f)

        # дешифр для проверки обратимости
        if algorithm.startswith("aes-"):
            from crypto_block import block_decrypt

            decrypted_bytes = block_decrypt(encrypted_bin_path, "test123", meta)
        else:
            from crypto_stream import stream_decrypt

            decrypted_bytes = stream_decrypt(encrypted_bin_path, "test123", meta)

        print("ВЫЧИСЛЕНИЕ ЭНТРОПИИ...")
        original_entropy = calculate_entropy_from_bytes(original_bytes)
        encrypted_entropy = calculate_entropy_from_bytes(encrypted_bytes)

        print(f"   Исходная энтропия: {original_entropy:.6f}")
        print(f"   Энтропия шифра: {encrypted_entropy:.6f}")

        print("ЭНТРОПИЯ КАНАЛОВ...")
        original_channel_entropy = calculate_channel_entropy_for_image(original_path)
        encrypted_channel_entropy = calculate_channel_entropy_for_encrypted(
            encrypted_bytes, original_img.size, original_img.mode
        )

        print(f"   Исходные каналы: {original_channel_entropy}")
        print(f"   Зашифрованные каналы: {encrypted_channel_entropy}")

        print("NPCR/UACI...")
        # сравнение оригинала с зашифрованнными данными
        npcr, uaci = calculate_npcr_uaci(original_bytes, encrypted_bytes)
        print(f"   NPCR: {npcr:.6f}%")
        print(f"   UACI: {uaci:.6f}%")

        print("AVALANCHE EFFECT...")
        avalanche = calculate_avalanche_effect(original_bytes, encrypted_bytes)
        print(f"   Avalanche effect: {avalanche:.6f}%")

        print("КОРРЕЛЯЦИЯ...")
        correlations = {}
        for direction in ["horizontal", "vertical", "diagonal"]:
            original_corr = calculate_correlation_from_image(original_path, direction)
            encrypted_corr = calculate_encrypted_correlation(
                encrypted_bytes, original_img.size, original_img.mode, direction
            )

            correlations[direction] = {
                "original": original_corr,
                "encrypted": encrypted_corr,
                "reduction": (
                    abs(original_corr - encrypted_corr)
                    if original_corr != 0
                    else encrypted_corr
                ),
            }
            print(f"   {direction}: {original_corr:.6f} → {encrypted_corr:.6f}")

        print("РАСПРЕДЕЛЕНИЕ БАЙТОВ...")
        original_distribution = analyze_byte_distribution(original_bytes, "original")
        encrypted_distribution = analyze_byte_distribution(encrypted_bytes, "encrypted")

        print("ПРОВЕРКА ОБРАТИМОСТИ...")
        reversibility_ok = original_bytes == decrypted_bytes
        if reversibility_ok:
            print("--------------- ОБРАТИМОСТЬ: УСПЕХ - данные полностью восстановлены")
        else:
            print("--------------- ОБРАТИМОСТЬ: ОШИБКА - данные не совпадают")
            print(f"   Оригинал: {len(original_bytes)} байт")
            print(f"   Дешифр:   {len(decrypted_bytes)} байт")

            # Диагностика различий
            min_len = min(len(original_bytes), len(decrypted_bytes))
            differences = sum(
                1 for i in range(min_len) if original_bytes[i] != decrypted_bytes[i]
            )
            print(f"   Различий: {differences} из {min_len} байт")

        print("АНАЛИЗ ЧУВСТВИТЕЛЬНОСТИ К КЛЮЧУ...")
        key_sensitivity_results = analyze_key_sensitivity(
            original_path, "test_key_123", "test_key_124", algorithm
        )

        print("АНАЛИЗ ЧУВСТВИТЕЛЬНОСТИ К IV/NONCE...")
        iv_sensitivity_results = analyze_iv_nonce_sensitivity(
            original_path, "test_key_123", algorithm
        )

        results = {
            "image_name": image_name,
            "original_path": original_path,
            "encrypted_path": encrypted_bin_path,
            "image_size": original_img.size,
            "image_mode": original_img.mode,
            "algorithm": algorithm,
            "entropy": {
                "original": original_entropy,
                "encrypted": encrypted_entropy,
                "improvement": encrypted_entropy - original_entropy,
            },
            "channel_entropy": {
                "original": original_channel_entropy,
                "encrypted": encrypted_channel_entropy,
            },
            "npcr_uaci": {"npcr": npcr, "uaci": uaci},
            "avalanche_effect": avalanche,
            "correlations": correlations,
            "byte_distribution": {
                "original": original_distribution,
                "encrypted": encrypted_distribution,
            },
            "file_sizes": {
                "original_bytes": len(original_bytes),
                "encrypted_bytes": len(encrypted_bytes),
                "decrypted_bytes": len(decrypted_bytes),
            },
            "key_sensitivity": key_sensitivity_results,
            "iv_nonce_sensitivity": iv_sensitivity_results,
        }

        print("ВЫЧИСЛЕНИЯ ЗАВЕРШЕНЫ")
        return results

    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА при вычислении метрик для {image_name}: {e}")
        return create_fallback_metrics(
            image_name, original_path, encrypted_bin_path, algorithm
        )


def create_fallback_metrics(
    image_name: str, original_path: str, encrypted_path: str, algorithm: str
) -> Dict[str, Any]:
    print(f"СОЗДАНИЕ РЕЗЕРВНЫХ МЕТРИК ДЛЯ {image_name}")

    try:
        with open(encrypted_path, "rb") as f:
            encrypted_bytes = f.read()
        original_img = Image.open(original_path)
        original_bytes = original_img.tobytes()
    except:
        encrypted_bytes = b""
        original_bytes = b""

    return {
        "image_name": image_name,
        "original_path": original_path,
        "encrypted_path": encrypted_path,
        "image_size": (100, 100),
        "image_mode": "RGB",
        "algorithm": algorithm,
        "entropy": {
            "original": calculate_entropy_from_bytes(original_bytes),
            "encrypted": calculate_entropy_from_bytes(encrypted_bytes),
            "improvement": 0.0,
        },
        "channel_entropy": {
            "original": {"R": 0.0, "G": 0.0, "B": 0.0},
            "encrypted": {
                "Encrypted_Data": calculate_entropy_from_bytes(encrypted_bytes)
            },
        },
        "npcr_uaci": {"npcr": 0.0, "uaci": 0.0},
        "avalanche_effect": 0.0,
        "correlations": {
            "horizontal": {"original": 0.0, "encrypted": 0.0, "reduction": 0.0},
            "vertical": {"original": 0.0, "encrypted": 0.0, "reduction": 0.0},
            "diagonal": {"original": 0.0, "encrypted": 0.0, "reduction": 0.0},
        },
        "byte_distribution": {
            "original": analyze_byte_distribution(original_bytes, "original"),
            "encrypted": analyze_byte_distribution(encrypted_bytes, "encrypted"),
        },
        "file_sizes": {
            "original_bytes": len(original_bytes),
            "encrypted_bytes": len(encrypted_bytes),
        },
    }


def update_summary_table(new_results: Dict[str, Any]):
    summary_file = "results/report_data/summary_table.csv"
    entropy_data = new_results.get(
        "entropy", {"original": 0, "encrypted": 0, "improvement": 0}
    )
    npcr_data = new_results.get("npcr_uaci", {"npcr": 0, "uaci": 0})
    correlations = new_results.get("correlations", {})
    horizontal_corr = correlations.get("horizontal", {"original": 0, "encrypted": 0})
    file_sizes = new_results.get(
        "file_sizes", {"original_bytes": 0, "encrypted_bytes": 0}
    )
    key_sensitivity = new_results.get("key_sensitivity", {}).get(
        "sensitivity_metrics", {}
    )
    iv_sensitivity = new_results.get("iv_nonce_sensitivity", {}).get(
        "sensitivity_metrics", {}
    )

    row_data = {
        "image": new_results.get("image_name", "unknown"),
        "algorithm": new_results.get("algorithm", "unknown"),
        "original_entropy": f"{entropy_data.get('original', 0):.6f}",
        "encrypted_entropy": f"{entropy_data.get('encrypted', 0):.6f}",
        "entropy_improvement": f"{entropy_data.get('improvement', 0):+.6f}",
        "npcr": f"{npcr_data.get('npcr', 0):.6f}%",
        "uaci": f"{npcr_data.get('uaci', 0):.6f}%",
        "avalanche": f"{new_results.get('avalanche_effect', 0):.6f}%",
        "horizontal_corr_original": f"{horizontal_corr.get('original', 0):.6f}",
        "horizontal_corr_encrypted": f"{horizontal_corr.get('encrypted', 0):.6f}",
        "file_size_original": file_sizes.get("original_bytes", 0),
        "file_size_encrypted": file_sizes.get("encrypted_bytes", 0),
        "key_sensitivity_npcr": f"{key_sensitivity.get('npcr', 0):.6f}%",
        "key_sensitivity_uaci": f"{key_sensitivity.get('uaci', 0):.6f}%",
        "key_sensitivity_avalanche": f"{key_sensitivity.get('avalanche_effect', 0):.6f}%",
        "iv_sensitivity_npcr": f"{iv_sensitivity.get('npcr', 0):.6f}%",
    }

    # Проверяем существует ли файл
    if os.path.exists(summary_file):
        with open(summary_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            existing_data = list(reader)

        # Обновляем или добавляем строку
        updated = False
        for i, row in enumerate(existing_data):
            if (
                row["image"] == new_results["image_name"]
                and row["algorithm"] == new_results["algorithm"]
            ):
                existing_data[i] = row_data
                updated = True
                break

        if not updated:
            existing_data.append(row_data)
    else:
        existing_data = [row_data]

    # Сохраняем обновленные данные
    with open(summary_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = row_data.keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_data)

    print(f"Сводная таблица обновлена: {summary_file}")


# Основная функция для использования
def analyze_and_save_metrics(
    original_path: str, encrypted_bin_path: str, image_name: str, algorithm: str
) -> Dict[str, Any]:
    try:
        results = compute_all_metrics(
            original_path, encrypted_bin_path, image_name, algorithm
        )
        metrics_filename = f"{image_name}_metrics.json"
        save_metrics_to_json(results, metrics_filename)
        update_summary_table(results)

        print(f" МЕТРИКИ ВЫЧИСЛЕНЫ И СОХРАНЕНЫ: {image_name}")
        return results

    except Exception as e:
        print(f" ОШИБКА В ОСНОВНОЙ ФУНКЦИИ: {e}")
        fallback_results = create_fallback_metrics(
            image_name, original_path, encrypted_bin_path, algorithm
        )
        metrics_filename = f"{image_name}_metrics.json"
        save_metrics_to_json(fallback_results, metrics_filename)
        update_summary_table(fallback_results)
        return fallback_results


if __name__ == "__main__":

    test_images = {
        "ECB": {
            "checkerboard": (
                "imgs/input/checkerboard.png",
                "imgs/encrypted/checkerboard_aes_ecb.bin",
            ),
            "gradient": (
                "imgs/input/gradient.png",
                "imgs/encrypted/gradient_aes_ecb.bin",
            ),
            "noise_texture": (
                "imgs/input/noise_texture.png",
                "imgs/encrypted/noise_texture_aes_ecb.bin",
            ),
            "my": ("imgs/input/my.jpg", "imgs/encrypted/my_aes_ecb.bin"),
        },
        "CBC": {
            "checkerboard": (
                "imgs/input/checkerboard.png",
                "imgs/encrypted/checkerboard_aes_cbc.bin",
            ),
            "gradient": (
                "imgs/input/gradient.png",
                "imgs/encrypted/gradient_aes_cbc.bin",
            ),
            "noise_texture": (
                "imgs/input/noise_texture.png",
                "imgs/encrypted/noise_texture_aes_cbc.bin",
            ),
            "my": ("imgs/input/my.jpg", "imgs/encrypted/my_aes_cbc.bin"),
        },
        "CFB": {
            "checkerboard": (
                "imgs/input/checkerboard.png",
                "imgs/encrypted/checkerboard_aes_cfb.bin",
            ),
            "gradient": (
                "imgs/input/gradient.png",
                "imgs/encrypted/gradient_aes_cfb.bin",
            ),
            "noise_texture": (
                "imgs/input/noise_texture.png",
                "imgs/encrypted/noise_texture_aes_cfb.bin",
            ),
            "my": ("imgs/input/my.jpg", "imgs/encrypted/my_aes_cfb.bin"),
        },
        "CTR": {
            "checkerboard": (
                "imgs/input/checkerboard.png",
                "imgs/encrypted/checkerboard_aes_ctr.bin",
            ),
            "gradient": (
                "imgs/input/gradient.png",
                "imgs/encrypted/gradient_aes_ctr.bin",
            ),
            "noise_texture": (
                "imgs/input/noise_texture.png",
                "imgs/encrypted/noise_texture_aes_ctr.bin",
            ),
            "my": ("imgs/input/my.jpg", "imgs/encrypted/my_aes_ctr.bin"),
        },
        "STREAM": {
            "checkerboard": (
                "imgs/input/checkerboard.png",
                "imgs/encrypted/checkerboard_stream.bin",
            ),
            "gradient": (
                "imgs/input/gradient.png",
                "imgs/encrypted/gradient_stream.bin",
            ),
            "noise_texture": (
                "imgs/input/noise_texture.png",
                "imgs/encrypted/noise_texture_stream.bin",
            ),
            "my": ("imgs/input/my.jpg", "imgs/encrypted/my_stream.bin"),
        },
    }

    for mode, images in test_images.items():
        print(f"\n Режим {mode}:")
        for name, (original, encrypted) in images.items():
            if os.path.exists(original) and os.path.exists(encrypted):
                try:
                    # Определяем алгоритм на основе режима
                    if mode == "STREAM":
                        algorithm = "stream-rc4-custom"
                    else:
                        algorithm = f"aes-{mode.lower()}"  # 'aes-cbc', 'aes-cfb', 'aes-ctr', 'aes-ecb'

                    results = analyze_and_save_metrics(
                        original, encrypted, f"{name}_{mode.lower()}", algorithm
                    )

                    print(
                        f" {name}: энтропия {results['entropy']['original']:.3f} → {results['entropy']['encrypted']:.3f}"
                    )
                except Exception as e:
                    print(f" Ошибка для {name} ({mode}): {e}")
