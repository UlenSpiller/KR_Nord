# Импорт необходимых модулей из библиотеки ezdxf
import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext, pymupdf, layout, config
import os

# Определение путей к папкам относительно текущей директории скрипта
base_path = os.path.dirname(os.path.abspath(__file__))
print(base_path)


# Определение функции для экспорта чертежа в PNG
def export_dark_bg(draw, file_name, png_path):
    msp = draw.modelspace()  # Получение пространства модели (модельного пространства)

    # Изменение цвета линий на черный
    for entity in msp:
        if entity.dxf.color != 7:  # 7 - это цвет черного
            entity.dxf.color = 7

    # 1. Создание контекста рендеринга
    context = RenderContext(doc)
    # 2. Создание бэкэнда для рендеринга в PDF
    backend = pymupdf.PyMuPdfBackend()
    # 4. Создание конфигурации для рендеринга с белым фоном
    cfg = config.Configuration(background_policy=config.BackgroundPolicy.WHITE)
    # 5. Установка конфигурации для фронтенда
    frontend = Frontend(context, backend, config=cfg)
    # 6. Отрисовка модельного пространства
    frontend.draw_layout(msp)
    # 7. Создание листа с размерами чертежа и рамкой в 1 мм по периметру
    page = layout.Page(20, 15, layout.Units.mm, margins=layout.Margins.all(1))

    # 8. Получение изображения в формате PNG в виде байтового потока
    png_bytes = backend.get_pixmap_bytes(page, fmt="png", dpi=96)
    # 9. Запись байтового потока в файл PNG
    with open(f"{png_path}\\{file_name[0:-4]}.png", "wb") as fp:
        print(f"{png_path}\\{file_name[0:-4]}.png")
        fp.write(png_bytes)


# Получить список всех файлов в папке
files = os.listdir(base_path)
print(files)
# Отфильтровать список файлов, оставив только файлы с расширением ".dxf"
dxf_files = [file for file in files if file.endswith('.dxf')]
print(len(dxf_files))
print(dxf_files)
# Пройти по списку файлов и выполнить необходимые операции
k = len(dxf_files)
for i, dxf_file in enumerate(dxf_files):
    print(f'Осталось {k-i} файлов')
    print(dxf_file)
    file_path = os.path.join(base_path, dxf_file)
    print(file_path)
    doc = ezdxf.readfile(file_path)
    # Вызов функции для экспорта чертежа в PNG
    export_dark_bg(doc, dxf_file, base_path)
