import base64
from io import BytesIO
from PIL import Image
from pathlib import Path
import config


def base64_to_image(base64_string: str, uin: str, pic_number: int):
    # Декодируем base64 строку в байты
    image_data = base64.b64decode(base64_string)

    # Создаем BytesIO объект из декодированных байтов
    image_bytes = BytesIO(image_data)

    # Открываем изображение с помощью Pillow
    image = Image.open(image_bytes)

    # Определяем формат изображения
    image_format = image.format

    # Сохраняем изображение в файл
    output_filename = f'{str(pic_number)}.{image_format.lower()}'
    p = Path(config.img_base_path / uin)
    p.mkdir(parents=True, exist_ok=True)
    image.save(Path(p / output_filename))
    try:
        del image
    except:
        pass

    config.logger.info(f'-- {uin} Изображение {str(pic_number)} сохранено как {output_filename}')

    return (uin, output_filename)
