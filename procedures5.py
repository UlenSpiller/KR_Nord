import sqlite3


class BDP:  # MA - mobile accounting

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """Создаем базу ****.db  и таблицы  ver, head_pdat, body_bar, bar_cut"""

    @staticmethod
    def create_table(name_db):
        with sqlite3.connect(name_db) as db:
            cur = db.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS vers(
                ver_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ver_mj TEXT, 
                ver_mn TEXT
                );""")
            print("Таблица ver актуализирована")
            # noinspection
            cur.execute("""CREATE TABLE IF NOT EXISTS head_pdats( 
                pdat_code TEXT,
                pdat_desc TEXT,
                pdat_dicl TEXT,
                pdat_docl TEXT,
                pdat_bqty TEXT);""")
            print("Таблица head_pdats актуализирована")

            cur.execute("""CREATE TABLE IF NOT EXISTS body_bars(
                 bar_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 bar_bran TEXT,
                 bar_syst TEXT,
                 bar_code TEXT,
                 bar_desc TEXT,
                 bar_dicl TEXT,
                 bar_docl TEXT,
                 bar_len TEXT,
                 bar_pos  TEXT,
                 bar_lenr TEXT,
                 bar_h TEXT,
                 bar_mlt TEXT
                 );""")
            print("Таблица body_bars актуализирована")

            cur.execute("""CREATE TABLE IF NOT EXISTS bar_cuts(
                 cut_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 bar_id INTEGER,
                 cut_priority INTEGER,
                 cut_angl INTEGER,
                 cut_angr INTEGER,
                 cut_ab1 TEXT,
                 cut_ab2 TEXT,
                 cut_il TEXT,
                 cut_ol TEXT,
                 cut_bcod TEXT,
                 cut_csna TEXT,
                 cut_csnu TEXT,
                 cut_tina TEXT,
                 cut_stat TEXT,
                 cut_lbl_row1 TEXT,
                 cut_lbl_row2 TEXT,
                 cut_lbl_row3 TEXT,
                 cut_lbl_row4 TEXT,
                 cut_lbl_row5 TEXT
                 );""")
            print("Таблица bar_cuts актуализирована")

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    """Парсим файл и заполняем таблицы vers, head_pdats, body_bars, bar_cuts данными"""

    @staticmethod
    def pars_file(name_db, name_xml):
        import xml.etree.ElementTree as ET

        # Загрузка XML-данных из файла
        root_node = ET.parse(name_xml).getroot()

        """ Итерация по всем элементам VER. """
        ver_data = []
        for ver_element in root_node.findall(".//VER"):
            ver_item = (
                ver_element.find("MJ").text.strip(),
                ver_element.find("MN").text.strip(),
            )
            ver_data.append(ver_item)
            with sqlite3.connect(name_db) as db:
                cur = db.cursor()
                cur.execute("""SELECT COUNT (*) FROM vers;""")
                cur.executemany(
                    """INSERT INTO vers(ver_mj, ver_mn) VALUES(?,?);""", ver_data)

            db.commit()  # Завершение транзакции
            print('Стартовые данные vers внесены')

        """ Итерация по всем элементам PDAT. Список материала для порезки."""
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

        with sqlite3.connect(name_db) as db:
            cur = db.cursor()
            cur.execute("""SELECT COUNT (*) FROM head_pdats;""")

            cur.executemany(
                """INSERT INTO head_pdats(pdat_code, pdat_desc, pdat_dicl, pdat_docl, pdat_bqty)
                 VALUES(?,?,?,?,?);""", pdat_data)

        db.commit()  # Завершение транзакции
        print('Стартовые данные head_pdats внесены')

        """ Итерация по всем элементам BAR. Описание палок материала и выкраиваемых кусков."""

        with sqlite3.connect(name_db) as db:
            cur = db.cursor()

            # Итерация по всем элементам BAR
            for bar_element in root_node.findall(".//BAR"):
                bar_item = (
                    bar_element.find("BRAN").text.strip(),
                    bar_element.find("SYST").text.strip(),
                    bar_element.find("CODE").text.strip(),
                    bar_element.find("DESC").text.strip(),
                    bar_element.find("DICL").text.strip(),
                    bar_element.find("DOCL").text.strip(),
                    bar_element.find("LEN").text.strip(),
                    bar_element.find("POS").text.strip(),
                    bar_element.find("LENR").text.strip(),
                    bar_element.find("H").text.strip(),
                    bar_element.find("MLT").text.strip(),
                )

                # Добавляем данные в таблицу body_bars
                cur.execute(
                    """INSERT INTO body_bars(bar_bran, bar_syst, bar_code, bar_desc, bar_dicl,
                             bar_docl, bar_len, bar_pos, bar_lenr, bar_h, bar_mlt)
                             VALUES(?,?,?,?,?,?,?,?,?,?,?);""", bar_item)

                # Получаем bar_id, который только что был добавлен
                cur.execute("SELECT last_insert_rowid();")
                row = cur.fetchone()
                assert row is not None, 'Результат должен быть не пустым'
                value_bar_id = row[0]  # Получить значение

                cut_priority = 1  # Начальное значение номера <CUT> внутри каждого <BAR>

                """ Извлекаем элементы CUT расположенные внутри BAR."""
                for cut_element in bar_element.findall(".//CUT"):
                    cut_lbl_elements = cut_element.findall("LBL")
                    # Инициализируем значения по умолчанию
                    cut_lbl_values = [""] * 5
                    # Сохраняем тексты из <LBL> в соответствующие столбцы
                    for i, lbl in enumerate(cut_lbl_elements):
                        if i < 5:
                            cut_lbl_values[i] = lbl.text.strip()
                    cut_data = (
                                   value_bar_id,
                                   cut_priority,
                                   cut_element.find("ANGL").text.strip(),
                                   cut_element.find("ANGR").text.strip(),
                                   cut_element.find("AB1").text.strip(),
                                   cut_element.find("AB2").text.strip(),
                                   cut_element.find("IL").text.strip(),
                                   cut_element.find("OL").text.strip(),
                                   cut_element.find("BCOD").text.strip(),
                                   cut_element.find("CSNA").text.strip()
                                   if cut_element.find("CSNU") is not None else None,
                                   cut_element.find("TINA").text.strip(),
                                   cut_element.find("STAT").text.strip(),
                               ) + tuple(cut_lbl_values)

                    # Добавляем данные в таблицу bar_cuts
                    cur.execute(
                        """INSERT INTO bar_cuts(bar_id, cut_priority, cut_angl, cut_angr, cut_ab1,
                                 cut_ab2, cut_il, cut_ol, cut_bcod, cut_csna, cut_tina, cut_stat,
                                 cut_lbl_row1, cut_lbl_row2, cut_lbl_row3, cut_lbl_row4, cut_lbl_row5)
                                 VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);""", cut_data)
                    cut_priority += 1

        db.commit()  # Завершение транзакции
        db.close()

        print('Данные body_bars  и bar_cuts внесены')

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    """Удаляем базу данных перед или после созданием файла *.db """

    @staticmethod
    def delete_temp_db(name_db):  # Принимаем путь к папке, а не к файлу
        import os
        if os.path.exists(name_db):
            os.remove(name_db)
            print(f"Файл {name_db} был успешно удален.")
        else:
            print(f"Файл {name_db} не существует.")

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    """Переворачиваем углы на раме 86102 """

    @staticmethod
    def rotate_ang(name_db):
        import sqlite3

        # Подключение к базе данных SQLite
        conn = sqlite3.connect(name_db)
        cursor = conn.cursor()

        # SQL-запрос для правого объединения и выборки строк, удовлетворяющих условию с регулярным выражением
        select_query = """
            SELECT bc.cut_id, bb.bar_code, bc.cut_angl, bc.cut_angr, cut_ol
            FROM body_bars AS bb
            LEFT JOIN bar_cuts AS bc ON bb.bar_id = bc.bar_id
            WHERE (bb.bar_code LIKE '86102%' OR bb.bar_code LIKE '86517%') AND bc.cut_angl != bc.cut_angr """
        # (bb.bar_code LIKE '86102%')
        # (bb.bar_code LIKE '86102%' OR bb.bar_code LIKE '86517%')
        # Выполнение SQL-запроса
        cursor.execute(select_query)

        # Получение результатов выборки
        rows = cursor.fetchall()
        conn.close()

        print(rows)
        print(len(rows))
        rotate_rows = list(rows)  # Преобразовываем кортеж в список

        for i in range(len(rotate_rows)):
            rotate_angl = rotate_rows[i][3]
            rotate_rows[i] = (rotate_rows[i][0], rotate_rows[i][1], rotate_angl, rotate_rows[i][2], rotate_rows[i][4])

        print('***************ТАБЛИЦА СОХРАНЕНА*****************')
        print(len(rotate_rows))
        print(rotate_rows)

        # Подключение к базе данных SQLite
        conn = sqlite3.connect(name_db)
        cursor = conn.cursor()

        k = 0
        for i in range(len(rotate_rows)):
            cut_id = rotate_rows[i][0]
            cut_angl = rotate_rows[i][2]
            cut_angr = rotate_rows[i][3]

            # SQL-запрос обновления для каждой строки
            update_query = """
                UPDATE bar_cuts
                SET cut_angl = ?,
                    cut_angr = ?
                WHERE cut_id = ?"""
            cursor.execute(update_query, (cut_angl, cut_angr, cut_id))
            assert cursor.rowcount == 1, f"Ожидали обновить {len(rotate_rows)} строк, фактически обновлено {k}"
            k = k + cursor.rowcount

        print(f"Ожидали обновить {len(rotate_rows)} строк, фактически обновлено {k}")
        # Проверка, что количество обновлённых строк соответствует ожиданиям
        # assert cursor.rowcount == len(
        #     rotate_rows), f"Ожидали обновить {len(rotate_rows)} строк, фактически обновлено {cursor.rowcount}"

        # Сохранение изменений
        conn.commit()

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    """Записываем преобразованные данные в файл *_new.xml"""

    @staticmethod
    def make_new_xml(name_db, name_out_xml):
        import sqlite3
        import xml.etree.ElementTree as ET

        # name_db = '060_test.db'  # Имя БД из которой формируется xml файл
        # name_out_xml = 'example.xml'
        """Создаем корневой элемент"""
        job_teg = ET.Element("JOB")

        """****************************** Начало сборки в теге HEAD***********************************"""
        """Создаем элементы VER и добавляем их к корневому элементу"""
        ver_teg = ET.Element("VER")
        # ver_teg.text = 'This is child for JOB'
        job_teg.append(ver_teg)

        # Подключение к базе данных SQLite
        conn = sqlite3.connect(name_db)
        cursor = conn.cursor()
        # SQL-запрос для правого объединения и выборки строк, удовлетворяющих условию с регулярным выражением
        select_query = """SELECT ver_mj, ver_mn FROM vers """
        # Выполнение SQL-запроса
        cursor.execute(select_query)

        # Получение результатов выборки
        ver_rows = cursor.fetchall()
        conn.close()
        print(ver_rows, len(ver_rows))
        for i in range(len(ver_rows)):
            mj_teg = ET.Element("MJ")
            mj_teg.text = ver_rows[i][0]
            ver_teg.append(mj_teg)

            mn_teg = ET.Element("MN")
            mn_teg.text = ver_rows[i][1]
            ver_teg.append(mn_teg)
        """****************************** Конец сборки в теге VER***********************************"""
        # //////////////////////////////////////////////////////////////////////////////////////////
        """****************************** Начало сборки в теге HEAD***********************************"""

        head_teg = ET.Element("HEAD")
        # head_teg.text = "This is HEAD"
        job_teg.append(head_teg)

        conn = sqlite3.connect(name_db)
        cursor = conn.cursor()
        # SQL-запрос для правого объединения и выборки строк, удовлетворяющих условию с регулярным выражением
        select_query = """SELECT pdat_code, pdat_desc, pdat_dicl, pdat_docl, pdat_bqty FROM head_pdats """
        # Выполнение SQL-запроса
        cursor.execute(select_query)

        # Получение результатов выборки
        head_pdats_rows = cursor.fetchall()
        conn.close()
        print(head_pdats_rows, len(head_pdats_rows))
        print(head_pdats_rows[0][0])
        for i in head_pdats_rows:
            print(f'i ={i}')

            pdat_teg = ET.Element("PDAT")
            # head_teg.text = "This is HEAD"
            head_teg.append(pdat_teg)
            # -----------CODE------------
            code_teg = ET.Element("CODE")
            code_teg.text = i[0]
            print(i[0])
            pdat_teg.append(code_teg)
            # ------------DESC---------
            desc_teg = ET.Element("DESC")
            desc_teg.text = i[1]
            print(i[1])
            pdat_teg.append(desc_teg)
            # ------------DICL---------
            dicl_teg = ET.Element("DICL")
            dicl_teg.text = i[2]
            print(i[2])
            pdat_teg.append(dicl_teg)
            # ------------DOCL---------
            docl_teg = ET.Element("DOCL")
            docl_teg.text = i[3]
            print(i[3])
            pdat_teg.append(docl_teg)
            # ------------BTQY---------
            bqty_teg = ET.Element("BQTY")
            bqty_teg.text = i[4]
            print(i[4])
            pdat_teg.append(bqty_teg)

        """****************************** Конец сборки в теге HEAD***********************************"""
        # //////////////////////////////////////////////////////////////////////////////////////////
        """****************************** Начало сборки в теге BODY***********************************"""
        # bb.bar_id, bar_bran, bar_syst, bar_code, bar_desc, bar_dicl, bar_docl, bar_len,
        #                  bar_pos, bar_lenr, bar_h, bar_mlt
        body_teg = ET.Element("BODY")
        # body_teg.text = "This is BODY"
        job_teg.append(body_teg)

        conn = sqlite3.connect(name_db)
        cursor = conn.cursor()
        # SQL-запрос для правого объединения и выборки строк, удовлетворяющих условию с регулярным выражением
        select_query = """SELECT * FROM body_bars ORDER BY bar_code, bar_id;"""
        # Выполнение SQL-запроса
        cursor.execute(select_query)

        # Получение результатов выборки
        body_bars_rows = cursor.fetchall()
        conn.close()
        print(body_bars_rows, len(body_bars_rows))
        for i in body_bars_rows:
            print(f'i ={i}')
            # -----------BAR------------
            bar_teg = ET.Element("BAR")
            body_teg.append(bar_teg)
            # -----------BRAN------------
            bran_teg = ET.Element("BRAN")
            bran_teg.text = i[1]
            print(i[1])
            bar_teg.append(bran_teg)
            # -----------SYST------------
            syst_teg = ET.Element("SYST")
            syst_teg.text = i[2]
            print(i[2])
            bar_teg.append(syst_teg)
            # -----------CODE------------
            code_teg = ET.Element("CODE")
            code_teg.text = i[3]
            print(i[3])
            bar_teg.append(code_teg)
            # -----------DESC------------
            desc_teg = ET.Element("DESC")
            desc_teg.text = i[4]
            print(i[4])
            bar_teg.append(desc_teg)
            # ------------DICL---------
            dicl_teg = ET.Element("DICL")
            dicl_teg.text = i[5]
            print(i[5])
            bar_teg.append(dicl_teg)
            # ------------DOCL---------
            docl_teg = ET.Element("DOCL")
            docl_teg.text = i[6]
            print(i[6])
            bar_teg.append(docl_teg)
            # ------------LEN---------
            len_teg = ET.Element("LEN")
            len_teg.text = i[7]
            print(i[7])
            bar_teg.append(len_teg)
            # ------------POS---------
            pos_teg = ET.Element("POS")
            pos_teg.text = i[8]
            print(i[8])
            bar_teg.append(pos_teg)
            # ------------LENR---------
            lenr_teg = ET.Element("LENR")
            lenr_teg.text = i[9]
            print(i[9])
            bar_teg.append(lenr_teg)
            # ------------H---------
            h_teg = ET.Element("H")
            h_teg.text = i[10]
            print(i[10])
            bar_teg.append(h_teg)
            # ------------MLT---------
            mlt_teg = ET.Element("MLT")
            mlt_teg.text = i[11]
            print(i[11])
            bar_teg.append(mlt_teg)

            """******** Начало сборки в теге CUT *********"""
            conn = sqlite3.connect(name_db)
            cursor = conn.cursor()
            # SQL-запрос для правого объединения и выборки строк, удовлетворяющих условию с регулярным выражением
            select_query = f"""SELECT * FROM bar_cuts WHERE bar_id = {i[0]} ORDER BY cut_priority; """
            # Выполнение SQL-запроса
            cursor.execute(select_query)

            # Получение результатов выборки
            bar_cuts_rows = cursor.fetchall()
            conn.close()
            print('+++++++++++++++teg <CUTS> +++++++++++++++ ')
            print(i[0])
            print(bar_cuts_rows, len(bar_cuts_rows))

            for j in bar_cuts_rows:
                print(f'j ={j}')
                # # -----------CUT------------
                cut_teg = ET.Element("CUT")
                bar_teg.append(cut_teg)
                # -----------ANGL------------
                angl_teg = ET.Element("ANGL")
                angl_teg.text = str(j[3])
                print(j[3])
                cut_teg.append(angl_teg)
                # -----------ANGR------------
                angr_teg = ET.Element("ANGR")
                angr_teg.text = str(j[4])
                print(j[4])
                cut_teg.append(angr_teg)
                # -----------AB1------------
                ab1_teg = ET.Element("AB1")
                ab1_teg.text = j[5]
                print(j[5])
                cut_teg.append(ab1_teg)
                # -----------AB2------------
                ab2_teg = ET.Element("AB2")
                ab2_teg.text = j[6]
                print(j[6])
                cut_teg.append(ab2_teg)
                # -----------IL------------
                il_teg = ET.Element("IL")
                il_teg.text = j[7]
                print(j[7])
                cut_teg.append(il_teg)
                # -----------OL------------
                ol_teg = ET.Element("OL")
                ol_teg.text = j[8]
                print(j[8])
                cut_teg.append(ol_teg)
                # -----------BCOD------------
                bcod_teg = ET.Element("BCOD")
                bcod_teg.text = j[9]
                print(j[9])
                cut_teg.append(bcod_teg)
                # -----------CSNA------------
                csna_teg = ET.Element("CSNA")
                csna_teg.text = j[10]
                print(j[10])
                cut_teg.append(csna_teg)
                # -----------CSNU------------
                csnu_value = j[11]
                csnu_teg = ET.Element("CSNU")
                if csnu_value is not None:
                    csnu_teg.text = csnu_value
                    print(csnu_value)
                else:
                    # Устанавливаем csnu_value как пустую строку, если оно None
                    csnu_value = ''
                    print("")
                csnu_teg.text = csnu_value
                cut_teg.append(csnu_teg)
                # -----------TINA------------
                tina_teg = ET.Element("TINA")
                tina_teg.text = j[12]
                print(j[12])
                cut_teg.append(tina_teg)
                # -----------STAT------------
                stat_teg = ET.Element("STAT")
                stat_teg.text = j[13]
                print(j[13])
                cut_teg.append(stat_teg)
                # -----------LBL_ROW1------------
                lbl_row1_teg = ET.Element("LBL")
                lbl_row1_teg.text = j[14]
                print(j[14])
                cut_teg.append(lbl_row1_teg)
                # -----------LBL_ROW2------------
                lbl_row2_teg = ET.Element("LBL")
                lbl_row2_teg.text = j[15]
                print(j[15])
                cut_teg.append(lbl_row2_teg)
                # -----------LBL_ROW3------------
                lbl_row3_teg = ET.Element("LBL")
                lbl_row3_teg.text = j[16]
                print(j[16])
                cut_teg.append(lbl_row3_teg)
                # -----------LBL_ROW4------------
                lbl_row4_teg = ET.Element("LBL")
                lbl_row4_teg.text = j[17]
                print(j[17])
                cut_teg.append(lbl_row4_teg)
                # -----------LBL_ROW5------------
                lbl_row5_teg = ET.Element("LBL")
                lbl_row5_teg.text = j[18]
                print(j[18])
                cut_teg.append(lbl_row5_teg)

        """****************************** Конец сборки в теге BODY***********************************"""
        # Создаем XML-дерево
        tree = ET.ElementTree(job_teg)
        # Сохраняем XML-дерево в файл с кодировкой UTF-8
        with open(name_out_xml, 'wb') as f:
            tree.write(f, encoding="utf-8", xml_declaration=True)
        print("XML-файл сохранен.")
