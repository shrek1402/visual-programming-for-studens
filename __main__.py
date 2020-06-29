import mydesign
import pymysql
from PyQt5 import QtWidgets, QtGui, QtCore
import sys
from typing import NoReturn


class ExampleApp(QtWidgets.QMainWindow, mydesign.Ui_MainWindow):
    con = pymysql.connect('localhost', 'root', 'Prigayveronika@1328!', 'MYDATABASE')

    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.use("MYDATABASE")

        # Первая кнопка ОК связывается с сигналом
        self.pushButton_11.clicked.connect(lambda: self.btnClicked(self.tableWidget_4,
                                                                   self.select_frow_where("gr",
                                                                                          "id_f",
                                                                                          self.spinBox_4),
                                                                   "MYDATABASE",
                                                                   "gr"))
        # Вторая кнопка ОК связывается с сигналом
        self.pushButton_8.clicked.connect(lambda: self.btnClicked(self.tableWidget_3,
                                                                  self.select_frow_where("students",
                                                                                         "id_gr",
                                                                                         self.spinBox_3),
                                                                  "MYDATABASE",
                                                                  "students"))

        # Первая кнопка ADD связывается с сигналом
        self.pushButton_12.clicked.connect(lambda: self.btnAdd(self.tableWidget_5,
                                                               self.select_from("faculty"),
                                                               "MYDATABASE",
                                                               "faculty"))

        # Вторая кнопка ADD связывается с сигналом
        self.pushButton_9.clicked.connect(lambda: self.btnAdd(self.tableWidget_4,
                                                              self.select_frow_where("gr",
                                                                                     "id_f",
                                                                                     self.spinBox_4),
                                                              "MYDATABASE",
                                                              "gr"))

        self.pushButton.clicked.connect(lambda: self.btnSearch(self.lineEdit_2, self.lineEdit))

        # Вызовем наш сигнал для первой тблицы, чтобы она показывалась при запуске программы
        self.btnClicked(self.tableWidget_5, self.select_from("faculty"), "MYDATABASE", "faculty")

    # Формирует запрос для получения всех строк таблицы table
    def select_from(self, table: str) -> NoReturn:
        return f"SELECT * FROM {table}"

    # Формирует запрос для получения строк таблицы(A), ссылающихся на другую таблицу(B)
    # с помощью поля id таблицы(B)
    def select_frow_where(self, table, id, spin_box):
        return f"SELECT * FROM {table} WHERE {table}.{id} = {spin_box.value()};"

    def num_column(self, database: str, table: str):
        return f"SELECT COUNT(*) " \
               f"FROM INFORMATION_SCHEMA.COLUMNS " \
               f"WHERE TABLE_SCHEMA = '{database}' " \
               f"AND TABLE_NAME = '{table}';"

    def show_columns(self, database, table):
        return f"SHOW columns FROM {database}.{table};"

    def use(self, database):
        return f"use {database};"

    # Сигнал, выполняемый по нажатию кнопки OK
    def btnClicked(self, table_widget: QtWidgets.QTableWidget, query: str, database: str, table: str) -> NoReturn:
        cur = self.con.cursor()  # Создадим курсос
        cur.execute(self.num_column(database, table))  # Сделаем запрос
        num_column = cur.fetchall()[0][0]  # Извлекем данные по запросу
        table_widget.setColumnCount(num_column)  # Устанавливаем кол-во столбцов num_column

        cur.execute(self.show_columns(database, table))
        names_column = cur.fetchall()  # Получаем названия столбцов

        for column in range(num_column):
            item = QtWidgets.QTableWidgetItem()
            table_widget.setHorizontalHeaderItem(column, item)
            item = table_widget.horizontalHeaderItem(column)
            item.setText(names_column[column][0])  # Устанавливаем названия столбцов

        with self.con:
            cur = self.con.cursor()  # Создадим курсос
            cur.execute(query)  # Сделаем запрос
            rows = cur.fetchall()  # Извлекем данные по запросу
            table_widget.setRowCount(len(rows))

            for row in range(len(rows)):
                table_widget.setRowCount(row + 2)  # Чтобы заполнить строку ее нужно сначала создать
                for column in range(len(rows[row])):  # Shift нужен, чтобы не показы-вать столбец с id
                    item = QtWidgets.QTableWidgetItem()  # Создадим экземпляр ячейки
                    table_widget.setItem(row, column, item)  # Присвоем строке row, столбцу column эту ячейку
                    table_widget.item(row, column).setText(str(rows[row][column]))  # Заполним ячейку данными
                    # table_widget.item(row, column).setBackground(QtGui.QColor(100, 100, 150))
        # print(table_widget.findItems("1", QtCore.Qt.MatchExactly))
    # Сигнал, выполняемый по нажатию кнопки ADD
    def btnAdd(self, table_widget: QtWidgets.QTableWidget, query: str, database, table):
        with self.con:
            cur = self.con.cursor()  # Создадим курсос
            cur.execute(query)  # Сделаем запрос
            n_rows = len(cur.fetchall())  # Извлекем данные по запросу

            cur.execute(self.num_column(database, table))  # Сделаем запрос
            num_column = cur.fetchall()[0][0]  # Извлекем данные по запросу

            cur.execute(self.show_columns(database, table))
            names_column = cur.fetchall()  # Получаем названия столбцов

            columns = ""
            data_add = ""
            for column in range(1, num_column):
                if column == num_column - 1:
                    columns += str(names_column[column][0])
                    data_add += "'" + str(table_widget.item(n_rows, column).text()) + "'"
                else:
                    columns += str(names_column[column][0]) + ", "
                    data_add += "'" + str(table_widget.item(n_rows, column).text()) + "'" + ", "

            cur.execute(f"INSERT INTO {table} ({columns}) VALUES ({data_add});")
            self.btnClicked(table_widget, query, database, table)

    def btnSearch(self, line_edit_no_accurate, line_edit_accurate):
        # Перерисуем таблицы, а то вдруг что
        self.btnClicked(self.tableWidget_5, self.select_from("faculty"), "MYDATABASE", "faculty")
        self.btnClicked(self.tableWidget_4,
                        self.select_frow_where("gr",
                                               "id_f",
                                               self.spinBox_4),
                        "MYDATABASE",
                        "gr")
        # QtCore.Qt.MatchExactly флаг для точного совпадения
        # QtCore.Qt.MatchContains флаг для поиска подстроки в строке
        #
        # Читаем и умнеем --> http://doc.crossplatform.ru/qt/4.7.x/qt.html#MatchFlag-enum

        if len(line_edit_no_accurate.text()) is not 0:
            search = line_edit_no_accurate.text()
            flag = QtCore.Qt.MatchContains
        elif len(line_edit_accurate.text()) is not 0:
            search = line_edit_accurate.text()
            flag = QtCore.Qt.MatchExactly
        else:
            return

        cells = self.tableWidget_5.findItems(search, flag)
        cells += self.tableWidget_4.findItems(search, flag)
        cells += self.tableWidget_3.findItems(search, flag)
        print(cells)
        for cell in cells:
            cell.setBackground(QtGui.QColor(100, 100, 150))

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
