#=====================================================================
# Скрипт: generate_configs_universal.py (ФИНАЛЬНАЯ ВЕРСИЯ: АБСОЛЮТНО ИЕРАРХИЧНАЯ МАСКА)
#=====================================================================
import os
from pathlib import Path
import re
# Скрипт будет искать подкаталог 'pic' по абсолютному пути.
ROOT_PHOTO_DIR = r"D:\Maestat\Test\pic"
# Скрипт будет искать подкаталог 'pic' в той же папке, где он сам запущен.
#ROOT_PHOTO_DIR = Path(os.path.join(Path(__file__).parent, 'pic')).resolve()
OUTPUT_FILE = "all_found_paths_tuple.txt"
ALLOWED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.mp4', '.gif', '.webm')
def get_hierarchical_key(path_str):
    """
    ГЕНЕРАЦИЯ КЛЮЧА: Собирает ключ из всех папок (относительно ROOT_PHOTO_DIR).
    Пример: face/11/0_0.jpg -> face_11_0
    """
    path = Path(path_str)
    try:
        # Используем относительный путь родительской папки
        parent_dir = path.parent
        relative_parts = list(parent_dir.relative_to(Path(ROOT_PHOTO_DIR)).parts)
        if not relative_parts:
             # Если роот-директория равна директории папки
            return "root_level_photos"
        # Преобразуем чистый путь: face/11/0 -> face_11_0
        key = "_".join(relative_parts)
        # Префикс в конце, чтобы отделить от группы
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
        base_path = Path(root_dir)
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
        # *** ДИАГНОСТИКА ***: Выводим первые 5 путей, чтобы доказать работу сканера.
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
    # Структура: { 'имя_ключа': {'photos': [path1, path2], 'videos': [path1, path2]} }
    grouped = {}
    unique_sorted_paths = sorted(list(set(paths)))
    output = []
    for path in unique_sorted_paths:
        # 1. Получаем иерархический ключ
        key = get_hierarchical_key(path)
        if key not in grouped:
             grouped[key] = {'photos': [], 'videos': []}
        # 2. Определяем тип файла для ветвления логики
        ext = Path(path).suffix.lower()
        if ext in ('.jpg', '.jpeg', '.png', '.webp', '.gif'):
            # Добавляем в список фото
            grouped[key]['photos'].append(path)
        elif ext in ('.mp4', '.webm'):
            # Добавляем в список видео
            grouped[key]['videos'].append(path)
        # Другие типы игнорируются
    # --- ГЕНЕРАЦИЯ КОНТЕНТА ---
    for key in sorted(list(grouped.keys())):
        group_data = grouped[key]
        # Обрабатываем фотографии (jpg/png/webp/gif)
        photos_paths = group_data.get('photos', [])
        if photos_paths:
            photo_key = f'{key}_photos'
            output.append(f'{photo_key}_paths = [\n    ' + '\n    '.join([f'"{p}"' for p in photos_paths]) + ']\n')
            photo_indices_list = list(range(len(photos_paths)))
            output.append(f'%{photo_key} = ({photo_key}_paths, [{", ".join(map(str, photo_indices_list))}] )')
        # Обрабатываем видео (mp4/webm)
        videos_paths = group_data.get('videos', [])
        if videos_paths:
            video_key = f'{key}_videos'
            output.append(f'{video_key}_paths = [\n    ' + '\n    '.join([f'"{p}"' for p in videos_paths]) + ']\n')
            video_indices_list = list(range(len(videos_paths)))
            output.append(f'%{video_key} = ({video_key}_paths, [{", ".join(map(str, video_indices_list))}] )')
    return "\n".join(output)
if __name__ == "__main__":
    print("=" * 60)
    print("| [*] ЗАПУСК: АВТОМАТИЧЕСКАЯ ГЕНЕРАЦИЯ КОНФИГ-ПАРСЕРА |")
    print("================================================")
    found_paths = scan_and_aggregate_paths(ROOT_PHOTO_DIR)
    final_content = format_output_to_tuple(found_paths)
    # --- ФИНАЛЬНАЯ ВАЛИДАЦИЯ (Запись файла) ---
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