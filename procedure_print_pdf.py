import xml.etree.ElementTree as ET
from fpdf import FPDF
from collections import defaultdict


def list_to_tuple(lst):
    # Если элемент является списком, рекурсивно вызываем эту же функцию
    if isinstance(lst, list):
        return tuple(list_to_tuple(item) for item in lst)
    else:
        return lst


def count_and_create_list(input_list):
    count_dict = defaultdict(int)
    # Подсчет количества каждого элемента в списке
    for item in input_list:
        # Преобразование списка в кортеж для возможности хеширования
        item_tuple = tuple(item)
        count_dict[item_tuple] += 1
    # Создание нового списка списков
    result_list = [[count, list(element)] for element, count in count_dict.items()]
    return result_list


def print_new_xml(name_out_xml):
    # Загрузка XML-данных из файла
    root_node = ET.parse(name_out_xml).getroot()
    pdat_data = []
    for pdat_element in root_node.findall(".//PDAT"):
        pdat_item = (
            pdat_element.find("CODE").text.strip(),
            pdat_element.find("DESC").text.strip(),
            pdat_element.find("DICL").text.strip(),
            pdat_element.find("DOCL").text.strip(),
            pdat_element.find("BQTY").text.strip(),
        )
        pdat_data.append(pdat_item)
    print("""*******************************************************************""")
    print('pdat_data = ', pdat_data, type(pdat_data))
    print("""*******************************************************************""")

    # Создаем словарь
    pdat_dict = {}
    # Перебираем элементы и добавляем их в словарь
    for i, pdat_item in enumerate(pdat_data):
        # Используем data_item в качестве ключа, присваиваем значение None
        pdat_dict[pdat_item] = None
    print("""*******************************************************************""")
    print('pdat_dict = ', pdat_dict, type(pdat_dict))
    print("""*******************************************************************""")
    print("""Конец парсинга списка материалов""")
    print("""Начало парсинга палок и кусков на этих палках""")
    print("""*******************************************************************""")
    bar_data = []
    print('bar_data = ', bar_data, type(bar_data))
    print('++++++++++++++++++++++++++++++++++++++++')
    k = 0
    for bar_element in root_node.findall(".//BAR"):
        print(f'_____________{k}{k}{k}{k}{k}_____ Итерация k номер {k} по тегу BAR')
        bar_item = [
            bar_element.find("CODE").text.strip(), bar_element.find("DESC").text.strip(),
            bar_element.find("DICL").text.strip(), bar_element.find("DOCL").text.strip(),
            bar_element.find("LEN").text.strip(), bar_element.find("POS").text.strip(),
            bar_element.find("LENR").text.strip(), bar_element.find("MLT").text.strip(),
        ]
        print('       Находим описание палки и сохраняем в список bar_item')
        print('type(bar_item) = ', type(bar_item), '   len(bar_item) = ', len(bar_item))
        print('bar_item = ', bar_item)

        print('/*-/*-/*-___ Извлекаем элементы CUT расположенные внутри BAR. ___-*/-*/-*/')
        print('-----Создаем список cut_data-----------')
        cut_data = []
        print('type(cut_data) = ', type(cut_data), '   len(cut_data) = ', len(cut_data))
        print('cut_data = ', cut_data)
        print('     -------------------------------------------------')
        kk = 0
        for cut_element in bar_element.findall(".//CUT"):
            print(f'         Н А Ч А Л О внутреннего цикла. Итерация kk номер {kk} По тегу CUT внутри тега BAR')
            cut_lbl_elements = cut_element.findall("LBL")
            # Инициализируем значения по умолчанию
            cut_lbl_values = [""] * 5
            # Сохраняем тексты из <LBL> в соответствующие столбцы
            for i, lbl in enumerate(cut_lbl_elements):
                if i < 5:
                    cut_lbl_values[i] = lbl.text.strip()

            cut_item = [1] + [
                cut_element.find("ANGL").text.strip(),
                cut_element.find("ANGR").text.strip(),
                cut_element.find("OL").text.strip(),
            ] + cut_lbl_values[2:4]

            kk += 1
            print('          -----Находим описание каждого куска и сохраняем в список cut_item-------------')
            print('          ', type(cut_item), len(cut_item))
            print('          cut_item = ', cut_item)
            print('          -------------------------------------------------')
            print(f'          Добавляем {kk} -й кусок к списку кусков.'
                  f' Получаем список порезки для палки cчитываемой во время внешней итерации k= {k}')
            cut_data.append(cut_item)
            print('          type(cut_data) = ', type(cut_data), '     len(cut_data) = ', len(cut_data))
            print('          cut_data = ', cut_data)
            print('          ***************************************************')

        # k += 1
        print('В Н И М А Н И Е______ Внутренний цикл считывающий куски завершился. Переходим во внешний цикл. '
              'Проверяем список cut_data на повторяющиеся элементы  и группируем их.')

        print('Создаем словарь count_dict для подсчета вхождений')
        count_dict = {}
        print('type(count_dict) = ', type(count_dict), len(count_dict))
        print('count_dict = ', count_dict)

        # Итерируем по списку
        print('Преобразуем список cut_data в кортеж, чтобы сделать его хэшируемым и использовать в качестве '
              'ключа словаря')
        for item in cut_data:
            item_tuple = tuple(item)
            # Проверяем, есть ли такой ключ в словаре
            if item_tuple in count_dict:
                # Если есть, увеличиваем счетчик
                count_dict[item_tuple] += 1
            else:
                # Если нет, добавляем новый ключ
                count_dict[item_tuple] = 1
        print('Печатаем полученный словарь count_dict.')
        print(' type(count_dict) = ', type(count_dict), '   len(count_dict) = ', len(count_dict))
        print('С Л О В А Р Ь count_dict = ', count_dict)
        print('-------------------------------------------------')
        print('Создаем новый список из уникальных кусков и их количества. Сохраняем в переменную cut_data.')
        cut_data = [[str(value)] + list(key)[1:] for key, value in count_dict.items()]

        print('Н О В Ы Й type(cut_data) = ', type(cut_data), '   len(cut_data) = ', len(cut_data))
        print('Н О В Ы Й cut_data = ', cut_data)
        print('*****************************************************************************')
        print()
        print('/*-/*-/*-___ В список bar_item добавляем список cut_data ___-*/-*/-*/')
        bar_item.append(cut_data)
        print(f'    -----Печатаем полный список bar_item на итерацию номер {k}--(конец цикла)--------')
        print('     ', type(bar_item), len(bar_item))
        print('     bar_item = ', bar_item)
        print('     -------------------------------------------------')
        print('Сохраняем описание палки bar_item в список bar_data')
        bar_data.append(bar_item)
        print(type(bar_data), len(bar_data))
        print(f'_____________{k}{k}{k}{k}{k}_____Печатаем список bar_data на итерацию номер {k}-(начало цикла)')
        print('bar_data =', bar_data)
        print('+++++++++++++++++++++++++++++++++++++++++++++++++')
        k += 1
    """"**************************************************************************"""

    print()
    print('///////////////////////////////////////////////////////////////////////////////////////////////////'
          '///////////////////////////////////////////////////////////////////////////////////////////////////')
    print('Конец работы циклов чтения содержимого тегов <BAR> и вложенных  в них <CUT>')
    print('bar_data =', bar_data)
    # Применяем функцию к вашему списку bar_data
    print('Преобразуем список bar_data в кортеж, чтобы сделать его хэшируемым и использовать в качестве '
          'ключа словаря')
    bar_data_tuple = list_to_tuple(bar_data)

    # Печатаем результат
    print(bar_data_tuple)

    bar_count_dict = {}

    for item in bar_data_tuple:
        # Проверяем, есть ли такой ключ в словаре
        if item in bar_count_dict:
            # Если есть, увеличиваем счетчик
            bar_count_dict[item] += 1
        else:
            # Если нет, добавляем новый ключ
            bar_count_dict[item] = 1
    print('Печатаем полученный словарь bar_count_dict.')
    print(' type(bar_count_dict) = ', type(bar_count_dict), '   len(bar_count_dict) = ', len(bar_count_dict))
    print('С Л О В А Р Ь bar_count_dict = ', bar_count_dict)
    print('-------------------------------------------------')
    bar = [[str(value)] + list(key) for key, value in bar_count_dict.items()]
    # print()
    # print(' type(bar) = ', type(bar), '   len(bar) = ', len(bar))
    # print('N E W  L I S T  bar = ', bar)
    # print('-------------------------------------------------')
    bar_tuple = list_to_tuple(bar)
    # print()
    # print(' type(bar_tuple) = ', type(bar_tuple), '   len(bar_tuple) = ', len(bar_tuple))
    # print('T U P L E bar_tuple = ', bar_tuple)
    # print('-------------------------------------------------')
    final_dict = {}
    for i in range(len(pdat_data)):
        final_list = []
        for j in range(len(bar_tuple)):
            # print(print(f' pdat_data[{i}]=', pdat_data[i]))
            # print(print(f' bar_tuple[{j}] =', bar_tuple[j]))
            """Проверяем на совпадение по артикулу, наименованию, цвету изнутри, цвету снаружи """
            if (pdat_data[i][0] == bar_tuple[j][1] and pdat_data[i][1] == bar_tuple[j][2] and pdat_data[i][2] ==
               bar_tuple[j][3]) and pdat_data[i][3] == bar_tuple[j][4]:
                final_list.append(bar_tuple[j])
        final_dict[pdat_data[i]] = final_list
    # print('final_dict = ', final_dict)
    return final_dict


class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, self.title, 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page %s' % self.page_no(), 0, 0, 'C')


def create_pdf(data_, pdf_filename, title="Your Default Title"):
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print('--------П Е Р Е Х О Д И М   К   П Е Ч А Т И   В   P D F-----------------------------------------')
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    pdf = PDF()
    pdf.title = title
    pdf.add_page()

    for key, v in data_.items():
        print()
        print(' key = ', key)
        print(f'Profile: {key[0]}; {key[1]}; color: {key[2]}/{key[3]} in total:{key[4]}')
        print('-------------------------------------------------')
        pdf.set_font('Arial', 'B', 14)

        pdf.cell(0, 10, f"Profile: {key[0]}; {key[1]}; color: {key[2]}/{key[3]} in total:{key[4]}", ln=True)
        print('+++++++++++++++++++++')
        kkk = 0
        for i in range(len(v)):
            print('СМОТРИ ЗДЕСЬ!!!')
            print(f' len(v[{i}]) =', len(v[i]), f'v[{i}] = ', v[i])
            print('v[i][0] =', v[i][0])
            s_n = int(v[i][0]) + kkk  # stick_number
            pdf.set_font('Arial', '', 14)
            pdf.cell(0, 7, f"Length of the stick: {v[i][5]}; remaining part: {v[i][7]}; "
                           f"total sticks: {v[i][0]}", ln=True)
            print(f' len(v[{i}[9]]) =', len(v[i][9]), f'v[{i}[9]] = ', v[i][9])
            for n in range(len(v[i][9])):
                print(f' len(v[{i}[9][{n}]) =', len(v[i][9][n]), f'v[{i}[9][{n}]] = ', v[i][9][n])
                pdf.cell(0, 8, f" {v[i][9][n][0]} | {v[i][9][n][1]} | {v[i][9][n][2]}"
                               f" | {v[i][9][n][3]} | {v[i][9][n][5]} | {v[i][9][n][4]}", ln=True)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 5, f"----------------S t i c k   n u m b e r  {s_n}  i s   o v e r----------------",
                     ln=True)
            kkk = s_n
        pdf.ln(5)  # Добавляем отступ в 10 единиц

    pdf.output(pdf_filename)
    print(f"PDF с именем '{pdf_filename}' создан успешно.")


# name_xml = '23060_uus.xml'
# output_pdf = name_xml[:-4] + '.pdf'
# data = print_new_xml(name_xml)
# create_pdf(data, output_pdf, title=f'ORDER NUMBER {name_xml[:-4]}')
