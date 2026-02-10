import os
import sys
import subprocess

# Шаблон имени: track1.ogg, track2.ogg, ...
NAME_TEMPLATE = "track{}"

# Форматы, которые конвертируем в .ogg
SOURCE_EXTENSIONS = [".mp3", ".wav", ".flac"]

# Конечное расширение
TARGET_EXTENSION = ".ogg"


def get_script_folder():
    """
    Папка, где лежит сам скрипт или собранный .exe.
    """
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def find_ffmpeg():
    """
    Ищем ffmpeg:
    1) ffmpeg.exe/ffmpeg в папке со скриптом
    2) просто 'ffmpeg' из PATH
    """
    folder = get_script_folder()

    # 1) ffmpeg.exe или ffmpeg рядом со скриптом
    local_candidates = ["ffmpeg.exe", "ffmpeg"]
    for name in local_candidates:
        path = os.path.join(folder, name)
        if os.path.isfile(path):
            return path

    # 2) ffmpeg из PATH
    return "ffmpeg"


def convert_to_ogg(folder, ffmpeg_path):
    print("=== Конвертация в .ogg ===")
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

    for name in files:
        base, ext = os.path.splitext(name)
        ext_lower = ext.lower()

        if ext_lower not in SOURCE_EXTENSIONS:
            continue

        src_path = os.path.join(folder, name)
        ogg_path = os.path.join(folder, base + TARGET_EXTENSION)

        if os.path.exists(ogg_path):
            print(f"Пропуск (уже есть .ogg): {name}")
            continue

        print(f"Конвертируем: {name} -> {base}{TARGET_EXTENSION}")

        try:
            result = subprocess.run(
                [
                    ffmpeg_path,
                    "-y",  # перезаписывать без вопросов (мы и так проверяем)
                    "-i",
                    src_path,
                    "-c:a",
                    "libvorbis",
                    "-qscale:a",
                    "5",
                    ogg_path,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            if result.returncode != 0:
                print(f"Ошибка конвертации файла: {name}")
        except FileNotFoundError:
            print(
                "Ошибка: ffmpeg не найден. Убедитесь, что ffmpeg установлен или лежит рядом со скриптом."
            )
            break


def rename_ogg_files(folder):
    print("\n=== Переименование .ogg ===")
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

    # Исключаем сам скрипт/исполняемый файл
    self_name = os.path.basename(sys.argv[0])
    files = [f for f in files if f != self_name]

    # Берём только .ogg
    ogg_files = [f for f in files if os.path.splitext(f)[1].lower() == TARGET_EXTENSION]

    ogg_files.sort()

    if not ogg_files:
        print("В папке нет .ogg файлов для переименования.")
        return

    print("Найдено .ogg файлов:", len(ogg_files))

    counter = 1
    for old_name in ogg_files:
        old_path = os.path.join(folder, old_name)
        base, ext = os.path.splitext(old_name)

        new_base = NAME_TEMPLATE.format(counter)  # track1, track2, ...
        new_name = new_base + TARGET_EXTENSION  # track1.ogg
        new_path = os.path.join(folder, new_name)

        if os.path.exists(new_path) and old_path.lower() != new_path.lower():
            print(f"Пропуск: {old_name} -> {new_name} (уже существует)")
        else:
            print(f"{old_name} -> {new_name}")
            os.rename(old_path, new_path)

        counter += 1


def main():
    folder = get_script_folder()
    print("Папка:", folder)

    ffmpeg_path = find_ffmpeg()
    print("Используем ffmpeg:", ffmpeg_path)

    convert_to_ogg(folder, ffmpeg_path)
    rename_ogg_files(folder)

    input("\nГотово. Нажмите Enter, чтобы закрыть окно...")


if __name__ == "__main__":
    main()
