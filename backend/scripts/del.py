import json
import os

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))


def delete_records_before_id(filename, target_id):
    """
    Deletes all records from a JSON file that come before the record with the specified target_id.

    Args:
        filename (str): Имя JSON-файла.
        target_id (int): ID, до которого (не включая) записи будут удалены.
    """

    data_filepath = os.path.join(SCRIPT_DIR, "..", "data", filename)

    try:
        with open(data_filepath, "r", encoding="utf-8") as f:
            data = json.load(f).get("messages", [])
    except FileNotFoundError:
        print(f"Ошибка: Файл '{filename}' не найден.")
        return
    except json.JSONDecodeError:
        print(f"Ошибка: Не удалось декодировать JSON из файла '{filename}'.")
        return

    if not isinstance(data, list):
        print(f"Ошибка: Ожидалось, что '{filename}' содержит список JSON-объектов.")
        return

    found_index = -1
    for i, record in enumerate(data):
        if isinstance(record, dict) and record.get("id") == target_id:
            found_index = i
            break

    if found_index != -1:
        # Оставляем записи, начиная с найденного индекса
        updated_data = data[found_index:]

        # Формируем имя нового файла
        base, ext = os.path.splitext(filename)
        new_filename = f"{base}-lite{ext}"
        new_data_filepath = os.path.join(SCRIPT_DIR, "..", "data", new_filename)

        try:
            with open(new_data_filepath, "w", encoding="utf-8") as f:
                json.dump(updated_data, f, ensure_ascii=False, indent=4)
            print(f"Обновленные данные сохранены в файл '{new_filename}'.")
            print(
                f"В новом файле {len(updated_data)} записей (исходный файл содержал {len(data)})."
            )
        except IOError:
            print(f"Ошибка: Не удалось записать обновленные данные в '{new_filename}'.")
    else:
        print(
            f"Запись с id {target_id} не найдена в файле '{filename}'. Файл не изменен."
        )


if __name__ == "__main__":
    # Убедитесь, что файл estudia-liite.json находится в той же директории,
    # что и этот скрипт, или укажите полный путь к файлу.
    delete_records_before_id(filename="children.json", target_id=128022)
