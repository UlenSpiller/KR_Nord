import os  # Импортируем модуль для работы с операционной системой
import tkinter as tk  # Импортируем библиотеку для создания графического интерфейса
import tkinter.ttk as ttk  # Импортируем ttk для создания прогресс бара

from tkinter import Checkbutton, Label, filedialog  # Импортируем несколько конкретных элементов из tkinter
from procedures5 import BDP  # Импортируем функции из модуля procedures5
from procedure_print_pdf import print_new_xml, create_pdf  # Импортируем функции из модуля procedure_print_pdf

file_path = ' '  # Переменная для хранения полного пути к выбранному файлу
name_db = ' '  # Переменная для хранения имени базы данных


# Функция для отображения прогресса
def show_progress():
    progress_window = tk.Toplevel(root)  # Создаем новое окно
    progress_window.title("Progress")  # Устанавливаем заголовок
    progress_window.geometry('300x50')  # Устанавливаем размеры окна
    # Создаем прогресс бар
    progress = ttk.Progressbar(progress_window, orient="horizontal", length=280, mode="indeterminate")
    progress.grid(row=0, column=0, padx=10, pady=10)
    progress.start()  # Запускаем анимацию прогресс бара
    root.update()  # Обновляем главное окно

    return progress_window, progress


# Функция для скрытия прогресса
def hide_progress(progress_window):
    progress_window.destroy()  # Закрываем окно прогресса


# Функция для открытия диалогового окна выбора файла
def open_file_dialog():
    global file_path  # Объявляем, что будем использовать глобальную переменную
    file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])  # Открываем диалоговое окно выбора файла
    print(file_path)  # Выводим выбранный путь файла в консоль
    if file_path:  # Если файл выбран
        selected_file_label.config(
            text=f"Selected File: {file_path}")  # Обновляем текст метки с именем выбранного файла


# Функция для выхода из программы
def exit_program():
    root.quit()


# Функция для начала выполнения задачи
def start_execution():
    global file_path, name_db  # Объявляем, что будем использовать глобальные переменные
    progress_window, progress = show_progress()  # Отображаем прогресс

    if file_path:  # Если файл выбран
        folder_path = os.path.dirname(file_path)  # Получаем путь к папке, содержащей файл
        file_name, _ = os.path.splitext(os.path.basename(file_path))  # Получаем имя файла без расширения
        # и расширение файла
        name_db = os.path.join(folder_path, file_name + '.db')  # Создаем путь к базе данных
        name_xml = os.path.join(folder_path, file_name + '.xml')  # Создаем путь к исходному XML файлу
        name_new_xml = os.path.join(folder_path, file_name + '_new.xml')  # Создаем путь к новому XML файлу
        BDP.delete_temp_db(name_db)  # Удаляем временную базу данных, если она существует
        BDP.create_table(name_db)  # Создаем таблицу в базе данных
        BDP.pars_file(name_db, name_xml)  # Парсим XML файл и записываем данные в базу данных

        if checkbox_rotate_ang_state.get() == 1:  # Если флажок для функции rotate_ang установлен
            BDP.rotate_ang(name_db)  # Выполняем функцию rotate_ang для базы данных

        BDP.make_new_xml(name_db, name_new_xml)  # Создаем новый XML файл на основе данных из базы данных

        if checkbox_create_pdf_state.get() == 1:  # Если флажок для создания PDF файла установлен
            data = print_new_xml(name_new_xml)  # Печатаем новый XML файл
            print('--- Создаем PDF файл ---')
            """Нет желания разбираться в том что я тут нахуевертил, поэтому ввожу переменную crutch (костыль) """
            crutch = os.path.basename(name_new_xml)
            print(f'костыль = {crutch}')

            create_pdf(data, os.path.join(folder_path, crutch[:-4] + '.pdf'), title=f'ORDER NUMBER {crutch[:-4]}')
            print("PDF created.")  # Выводим сообщение о создании PDF файла

        BDP.delete_temp_db(name_db)  # Удаляем временную базу данных
        # status_label.config(text="Status: Completed")  # Обновляем статус на "Completed"
        print("Execution completed.")  # Выводим сообщение о завершении выполнения
    else:
        print("No file selected.")  # Выводим сообщение о том, что файл не выбран
    hide_progress(progress_window)  # Скрываем прогресс


# Создаем основное окно приложения
root = tk.Tk()  # Инициализируем главное окно
root.geometry('600x250')  # Устанавливаем размеры окна
root.title("KR_NORD Optimization of optimization list")  # Устанавливаем заголовок окна

# Создаем метку для отображения выбранного файла
selected_file_label = Label(root, text="Selected File: no file selected", font=("Helvetica", 9))
selected_file_label.grid(row=0, column=1, padx=10, pady=10)

# Создаем кнопку для выбора XML файла
button_select = tk.Button(root, text="Select XML file", command=open_file_dialog)
button_select.grid(row=0, column=0, padx=10, pady=10)

# Создаем кнопку для начала выполнения задачи
button_start = tk.Button(root, text="Start Execution", command=start_execution)
button_start.grid(row=1, column=0, padx=10, pady=10)

# Создаем кнопку для выхода из программы
button_exit = tk.Button(root, text="Exit program", command=exit_program)
button_exit.grid(row=7, column=0, padx=20, pady=10, sticky=tk.W)

# Создаем флажок для функции rotate_ang
checkbox_rotate_ang_state = tk.IntVar(value=1)
checkbox_rotate_ang = Checkbutton(root, text="Execute rotate_ang 86102, 86517", variable=checkbox_rotate_ang_state)
checkbox_rotate_ang.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

# Создаем флажок для создания PDF файла
checkbox_create_pdf_state = tk.IntVar(value=1)
checkbox_create_pdf = Checkbutton(root, text="Create PDF file", variable=checkbox_create_pdf_state)
checkbox_create_pdf.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)


# Запускаем главный цикл обработки событий
root.mainloop()
