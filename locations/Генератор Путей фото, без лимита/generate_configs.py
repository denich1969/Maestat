#=====================================================================
# Скрипт: generate_configs_universal.py (ФИНАЛЬНАЯ ВЕРСИЯ: АБСОЛЮТНО ИЕРАРХИЧНАЯ МАСКА)
#=====================================================================
import os
from pathlib import Path
import re
ROOT_PHOTO_DIR = r"D:\Maestat\Test\pic"
OUTPUT_FILE = "all_found_paths_tuple.txt"
ALLOWED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.mp4', '.gif')
def get_hierarchical_key(path_str):
    """
    ГЕНЕРАЦИЯ КЛЮЧА: Собирает ключ из всех папок (относительно ROOT_PHOTO_DIR).
    Пример: D:\Maestat\Test\pic\face\11\0_0.jpg -> face_11_0
    """
    path = Path(path_str)
    # 1. Вычисляем относительный путь:
    relative_path = path.relative_to(Path(ROOT_PHOTO_DIR))
    # 2. Собираем все части пути в строковый ключ, заменяя разделители на подчеркивания.
    # path.parent.relative_to(Path(ROOT_PHOTO_DIR)) даст 'face/11/0'
    try:
        # Папка, содержащая файл (например, face/11)
        parent_dir = path.parent
        if parent_dir.relative_to(Path(ROOT_PHOTO_DIR)) == Path('.'):
            # Если файл находится прямо в ROOT_PHOTO_DIR, то ключ будет просто имени_файла.
            return f"root_level_photos"
        # Папка иерархия: например, (face/11/0)
        relative_parts = list(parent_dir.relative_to(Path(ROOT_PHOTO_DIR)).parts)
        # Преобразуем чистый путь: face/11/0 -> face_11_0
        key = "_".join(parent_dir.relative_to(Path(ROOT_PHOTO_DIR)).parts)
        # !!! ГРАНТГАРАНТИРОВАННЫЙ КЛЮЧ !!!
        return f"{key}_photos"
    except Exception:
        # Fallback, если Path не может расчитать относительный путь
        return f"fallback_fallback_{hash(path_str)}_photos"
def scan_and_aggregate_paths(root_dir):
    """Сканирует и фильтрует пути, возвращает список или пустой список."""
    print("-" * 60)
    print(f"[INFO] Начинаю универсальное сканирование в: {root_dir}")
    found_paths = []
    try:
        base_path = Path(root_dir).resolve()
        if not base_path.exists():
            print(f"[🔴 ERROR] Каталог не найден или недоступен: {base_path}")
            return []
        for path in base_path.rglob('*'):
            if path.is_file():
                ext = path.suffix.lower()
                if ext in ALLOWED_EXTENSIONS:
                     found_paths.append(str(path))
        total = len(found_paths)
        print(f"[🟢 SUCCESS] Сканирование завершено. Найдено только {total} подходящих медиафайлов.")
        first_5 = found_paths[:5]
        print("[🔎 ДИАГНОСТИКА] Проверка: Вывод первых 5 найденных путей:")
        for path in first_5:
            print(f"    - {path}")
        return found_paths
    except Exception as e:
        print(f"[🔴 FATAL ERROR] Критическая ошибка при сканировании: {e}")
        return []
def format_output_to_tuple(paths):
    """Форматирует и возвращает СТРОКУ с кортежами, используя иерархическую логику: [ПАТТЕРН_ИЕРАРХИИ]"""
    if not paths:
        return "ERROR: Не обнаружено файлов для обработки по заданным расширениям."
    grouped = {}
    unique_sorted_paths = sorted(list(set(paths)))
    output = []
    for path in unique_sorted_paths:
        # *** ИСПОЛЬЗУЕМ ГЕНЕРАТОР ИЕРАРХИЧЕСКОГО КЛЮЧА ***
        key = get_hierarchical_key(path)
        if key not in grouped:
             grouped[key] = []
        grouped[key].append(path)
    # --- ГЕНЕРАЦИЯ КОНТЕНТА ---
    for group_name in sorted(list(grouped.keys())):
        paths_to_add = grouped[group_name]
        # 1. Массив путей для группы
        paths_str = ',\n    '.join([f'"{p}"' for p in paths_to_add])
        output.append(f'{group_name}_paths = [\r\n    ' + '\r\n    '.join([f'"{p}"' for p in paths_to_add]) + ']\r\n')
        # 2. Финальный кортеж
        indices_list = list(range(len(paths_to_add)))
        output.append(f'%{group_name} = ({group_name}_paths, [{", ".join(map(str, indices_list))}] )')
    return "\n".join(output)
if __name__ == "__main__":
    print("=" * 60)
    print("| [*] ЗАПУСК: ПРОВЕРКА ПУТИ И ИЕРАРХИЧНАЯ СБОРКА КОНФИГ-ПАРСЕРА |")
    print("================================================")
    found_paths = scan_and_aggregate_paths(ROOT_PHOTO_DIR)
    final_content = format_output_to_tuple(found_paths)
    try:
        Path("photo_configs").mkdir(exist_ok=True)
        with open("photo_configs/all_found_paths_FINAL.txt", "w") as f:
            f.write(final_content + "\n")
        print("\n[✅ УСПЕШНО] Результаты сохранены в файл 'photo_configs/all_found_paths_FINAL.txt'")
    except Exception as e:
        final_content = f"[!!! КРИТИЧЕСКАЯ ОШИБКА ЗАПИСИ ФАЙЛА !!!] Тип ошибки: {type(e).__name__}: {e}\n[РЕКОМЕНДАЦИЯ]: Проверьте права доступа. Содержимое будет выведено ниже."
        print("\n" + "=" * 60)
        print("--- КОНТЕНТ ДЛЯ КОПИРОВАНИЯ (ВАШ ИТОГ) ---")
        print(final_content)
        print("=" * 60)