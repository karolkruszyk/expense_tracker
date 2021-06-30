import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import Menu
from tkinter import messagebox
from tkinter import scrolledtext
from ttkthemes import ThemedStyle
from datetime import date as data
import calendar
from datetime import datetime, timedelta
import mysql.connector
from pathlib import Path


class Window():
    def __init__(self):

        self.win = tk.Tk()
        self.win.title("Money Tracker")
        self.win.overrideredirect()

        tab_control = ttk.Notebook(self.win)

        self.main_tab = ttk.Frame(tab_control)
        tab_control.add(self.main_tab, text="Główne")

        self.all_bills_tab = ttk.Frame(tab_control)
        tab_control.add(self.all_bills_tab, text="Wszystkie rachunki")

        tab_control.pack(expand=True, fill="both", padx=5, pady=5)

        ws = self.win.winfo_screenwidth()
        hs = self.win.winfo_screenheight()

        x = (ws/3.5)
        y = (hs/5)

        self.win.geometry('+%d+%d' % (x, y))

        self.add_last_bill_widget()
        self.add_new_bill_widget()
        self.add_sum_bills_widget()
        self.add_menu_bar()
        self.add_all_bills_widget()
        self.add_scroll_text_box()

    ### Menu Bar section ###
    def add_menu_bar(self):
        self.menu_bar = Menu(self.win)
        self.win.config(menu=self.menu_bar)

        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(
            label="Eksportuj dane do pliku", command=self._export_data)
        self.file_menu.add_command(label="Wyczyść bazę danych",
                                   command=self._truncate_database)
        self.file_menu.add_command(label="Wyjście", command=self._exit_program)

        self.menu_bar.add_cascade(label="Plik", menu=self.file_menu)


### Widgets section ###

    ### Last bill ###

    def add_last_bill_widget(self):
        try:
            last_bill_frame = ttk.LabelFrame(
                self.main_tab, text='Ostatni rachunek')
            last_bill_frame.grid(
                column=0, row=0, sticky='NEWS', pady=5, padx=5)
            connection = self.get_connection()
            cursor = connection.cursor()
            select_query = "SELECT shop, type, price, date FROM bills_table ORDER BY date"
            cursor.execute(select_query)
            for bill in cursor:
                last_bill = bill
            old_date = last_bill[3]
            datetimeobject = datetime.strptime(old_date, '%Y-%m-%d')
            new_date = datetimeobject.strftime('%d/%m/%Y')
            last_bill_label = ttk.Label(last_bill_frame, text="Sklep: " + last_bill[0] + "\n" + "Typ: " +
                                        last_bill[1] + "\n" + "Cena: " + last_bill[2] + "\n" + "Data: " + new_date)
            last_bill_label.grid(column=0, row=0)
        except NameError:
            last_bill_label = ttk.Label(
                last_bill_frame, text="Brak ostatiego rachunku")
            last_bill_label.grid(column=0, row=0)

    ### Sum bills ###
    def add_sum_bills_widget(self):
        self.sum_bills_frame = ttk.LabelFrame(
            self.main_tab, text='Sumuj rachunki', width=20)
        self.sum_bills_frame.grid(
            column=1, row=0, sticky='NWES', columnspan=2, pady=5, padx=5)

        ttk.Label(self.sum_bills_frame, text='Sumuj z',
                  width=10).grid(column=0, row=0)
        ttk.Label(self.sum_bills_frame, text='dni').grid(column=2, row=0)

        existing_obj = 0
        sum_button = ttk.Button(self.sum_bills_frame, text="Ok",
                                width=8, command=self._sum_n_days)
        sum_button.grid(column=4, row=0)

        days = tk.StringVar()
        self.days_box = ttk.Combobox(self.sum_bills_frame, width=5,
                                     textvariable=days)
        self.days_box['values'] = (1, 2, 3, 4, 5, 6, 7, 14)
        self.days_box.grid(column=1, row=0)

    def add_scroll_text_box(self):
        self.scr_widget = scrolledtext.ScrolledText(
            self.sum_bills_frame, width=20, height=7, wrap=tk.WORD)
        self.scr_widget.grid(
            column=0, row=2, columnspan=5, sticky='WE', pady=5)
        self.scr_widget.configure(state='disabled')

    ### New bill ###
    def add_new_bill_widget(self):
        new_bill_frame = ttk.LabelFrame(
            self.main_tab, text='Nowy rachunek')
        new_bill_frame.grid(column=3, row=0, sticky='NEWS',
                            pady=5, padx=5)

        ttk.Label(new_bill_frame, text='Sklep: ').grid(
            column=0, row=0, sticky='W', pady=5)
        ttk.Label(new_bill_frame, text='Typ: ').grid(
            column=0, row=1, sticky='W', pady=5)
        ttk.Label(new_bill_frame, text='Cena: ').grid(
            column=0, row=2, sticky='W', pady=5)

        ttk.Label(new_bill_frame, text='Dzień: ').grid(
            column=0, row=3, sticky='W', pady=5)
        ttk.Label(new_bill_frame, text='Miesiąc: ').grid(
            column=2, row=3, sticky='W', pady=5)
        ttk.Label(new_bill_frame, text='Rok: ').grid(
            column=4, row=3, sticky='W', pady=5)

        self.shop = tk.StringVar()
        get_shop = ttk.Combobox(
            new_bill_frame, width=12, textvariable=self.shop)
        get_shop['values'] = self.get_shop_list()
        get_shop.grid(column=1, row=0, sticky='WE', columnspan=6)

        self.type = tk.StringVar()
        get_type = ttk.Combobox(
            new_bill_frame, width=12, textvariable=self.type)
        get_type['values'] = self.get_type_list()
        get_type.grid(column=1, row=1, sticky='WE', columnspan=6)

        self.price = tk.StringVar()
        get_price = ttk.Entry(
            new_bill_frame, width=15, textvariable=self.price)
        get_price.grid(column=1, row=2, sticky='WE', columnspan=6)

        today_combobox = self.get_today()
        self.day = tk.StringVar()
        get_day = ttk.Combobox(new_bill_frame, width=2,
                               textvariable=self.day, state='readonly')
        get_day['values'] = self.days_range()
        get_day.current(int(today_combobox[0])-1)
        get_day.grid(column=1, row=3)

        self.month = tk.StringVar()
        get_month = ttk.Combobox(new_bill_frame, width=2,
                                 textvariable=self.month, state='readonly')
        get_month['values'] = self.months_range()
        get_month.current(int(today_combobox[1])-1)
        get_month.grid(column=3, row=3)

        self.year = tk.StringVar()
        get_year = ttk.Entry(
            new_bill_frame, width=4, textvariable=self.year)
        get_year.insert(0, today_combobox[2])
        get_year.grid(column=5, row=3)

        new_bill_button = ttk.Button(
            new_bill_frame, text="Dodaj nowy rachunek", command=self._create_bill)
        new_bill_button.grid(
            column=0, row=4, columnspan=7, sticky='SWE', pady=5)

    ### Show all bills ###
    def add_all_bills_widget(self):
        self.tree = ttk.Treeview(self.all_bills_tab, columns=(
            'shop', 'type', 'price', 'date'), height=7)
        self.tree.column('#0', width=0, stretch=NO)
        self.tree.column('#1', width=100, minwidth=100, anchor=W)
        self.tree.column('#2', width=100, minwidth=100)
        self.tree.column('#3', width=100, minwidth=100, anchor=CENTER)
        self.tree.column('#4', width=100, minwidth=100, anchor=CENTER)

        self.tree.heading('shop', text='Sklep',
                          command=lambda: self._sort_by_shop(False))
        self.tree.heading('type', text='Typ',
                          command=lambda: self._sort_by_type(False))
        self.tree.heading('price', text='Cena',
                          command=lambda: self._sort_by_price(False, int))
        self.tree.heading('date', text='Data',
                          command=lambda: self._sort_by_date(False, self._str_to_datetime))

        self.tree.pack(pady=5, padx=5, side=LEFT)

        select_query = 'SELECT shop, type, price, date FROM bills_table'
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(select_query)
        i = 0
        for shop, type, price, date in cursor:
            oldformat = date
            datetimeobject = datetime.strptime(oldformat, '%Y-%m-%d')
            date = datetimeobject.strftime('%d/%m/%Y')
            self.tree.insert(parent='', index='end', iid=i,
                             values=(shop, type, price, date))
            i += 1

        connection.close()

        remove_button = ttk.Button(
            self.all_bills_tab, text="Usuń zaznaczony rachunek", command=self._remove_selected_bill)
        remove_button.pack(expand=True)

        edit_button = ttk.Button(
            self.all_bills_tab, text="Edytuj zaznaczony rachunek", command=self.edit_selected_bill_window)
        edit_button.pack(expand=True)

### Function section ###
    def get_connection(self):
        connection = mysql.connector.connect(
            user='karol', password='123456789', host='localhost', database='bills', auth_plugin='mysql_native_password')
        return connection

    def get_today(self):
        today_date = str(data.today())
        this_day = today_date[len(today_date)-2] + \
            today_date[len(today_date)-1]
        this_month = today_date[len(today_date)-5] + \
            today_date[len(today_date)-4]
        this_year = today_date[len(today_date)-10] + today_date[len(today_date)-9] + \
            today_date[len(today_date)-8] + today_date[len(today_date)-7]
        return this_day, this_month, this_year

    def get_shop_list(self):
        shop_list = []
        connection = self.get_connection()
        cursor = connection.cursor()
        shop_list_query = 'SELECT DISTINCT shop FROM bills_table'
        cursor.execute(shop_list_query)
        for shop in cursor:
            shop_list.append(shop)
        connection.close()
        return shop_list

    def get_type_list(self):
        type_list = []
        connection = self.get_connection()
        cursor = connection.cursor()
        type_list_query = 'SELECT DISTINCT type FROM bills_table'
        cursor.execute(type_list_query)
        for type in cursor:
            type_list.append(type)
        connection.close()
        return type_list

    def days_range(self):
        days_list = []
        for i in range(1, 32):
            if i < 10:
                days_list.append('0' + str(i))
            else:
                days_list.append(str(i))
        return days_list

    def months_range(self):
        months_list = []
        for i in range(1, 13):
            if i < 10:
                months_list.append('0' + str(i))
            else:
                months_list.append(str(i))
        return months_list

    def refresh(self):
        self.win.destroy()
        self.__init__()

### Command section ###
    def _sort_by_shop(self, reverse):
        shop_list = [(self.tree.set(item, 'shop'), item)
                     for item in self.tree.get_children('')]
        shop_list.sort(reverse=reverse)
        for index, (val, item) in enumerate(shop_list):
            self.tree.move(item, '', index)
        self.tree.heading('shop', command=lambda:
                          self._sort_by_shop(not reverse))

    def _sort_by_type(self, reverse):
        type_list = [(self.tree.set(item, 'type'), item)
                     for item in self.tree.get_children('')]
        type_list.sort(reverse=reverse)
        for index, (val, item) in enumerate(type_list):
            self.tree.move(item, '', index)
        self.tree.heading('type', command=lambda:
                          self._sort_by_type(not reverse))

    def _sort_by_price(self, reverse, data_type):
        l = [(self.tree.set(item, 'price'), item)
             for item in self.tree.get_children('')]
        l.sort(key=lambda t: data_type(t[0]), reverse=reverse)
        for index, (_, item) in enumerate(l):
            self.tree.move(item, '', index)
        self.tree.heading('price', command=lambda:
                          self._sort_by_price(not reverse, int))

    def _sort_by_date(self, reverse, data_type):

        l = [(self.tree.set(k, 'date'), k) for k in self.tree.get_children('')]
        l.sort(key=lambda t: data_type(t[0]), reverse=reverse)
        for index, (_, k) in enumerate(l):
            self.tree.move(k, '', index)
        self.tree.heading('date', command=lambda: self._sort_by_date(
            not reverse, self._str_to_datetime))

    def _str_to_datetime(self, string):
        return datetime.strptime(string, "%d/%m/%Y")

    def _truncate_database(self):
        answer = messagebox.askyesno(
            'Usuwanie danych', 'Czy chcesz usunąć wszystkie dane z bazy?')
        if answer == True:
            connection = self.get_connection()
            cursor = connection.cursor()
            truncate_query = 'TRUNCATE bills_table'
            cursor.execute(truncate_query)
            connection.commit()
            connection.close()
            self.refresh()
        elif answer == False:
            pass

    def _exit_program(self):
        answer = messagebox.askyesno(
            'Wyjście', 'Czy chcesz wyjść z programu?')
        if answer == True:
            self.win.quit()
            self.win.destroy()
            exit()
            self.refresh()
        elif answer == False:
            pass

    def _export_data(self):
        messagebox.showinfo(
            'Eksport danych', "Twoje pliki zostaną wyeksportowane do katalogu 'Dokumenty'")
        select_query = 'SELECT shop, type, price, date FROM bills_table'
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(select_query)
        home = str(Path.home())

        file_var = open(f"{home}\Documents\MoneyTrackerData.txt", 'w')

        for shop, type, price, date in cursor:
            file_var.write(f"{shop} {type} {price} {date}\n")

        file_var.close()

    def _create_bill(self):
        if_price_ok = False

        if len(self.price.get()) == 0:
            messagebox.showerror('Błąd', 'Wypełnij wszyskie pola!')
        elif not self.shop.get() or not self.type.get() or not self.price.get() or not self.year.get() or float(self.year.get()) < 1000 or float(self.year.get()) > 9999:
            messagebox.showerror('Błąd', 'Wypełnij wszyskie pola!')
            if_price_ok = False
        elif len(self.price.get()) != 0:
            try:
                test = float(self.price.get())
                if_price_ok = True
                del test
            except:
                messagebox.showerror('Błąd', 'Cena musi być liczbą!')
                if_price_ok = False

        if if_price_ok == True:
            self._msg()
            connection = self.get_connection()
            cursor = connection.cursor()
            self.shop = self.shop.get()
            self.new_shop = ""
            for letter in self.shop:
                if letter == " ":
                    letter = "-"
                else:
                    letter = letter
                self.new_shop += letter

            insert_query = "INSERT INTO bills_table(shop, type, price, date) VALUES(%(shop)s, %(type)s, %(price)s, %(date)s)"
            insert_data = {
                'shop': str(self.new_shop),
                'type': str(self.type.get()),
                'price': str(self.price.get()),
                'date': str(self.year.get() + "-" + self.month.get() + "-" + self.day.get())
            }
            cursor.execute(insert_query, insert_data)
            connection.commit()
            connection.close()
            self.refresh()

    def _msg(self):
        messagebox.showinfo('Powodzenie', 'Dodano nowy rachunek!')

    def _sum_n_days(self):
        how_many_days = int(self.days_box.get())
        show_date = datetime.now() - timedelta(days=how_many_days)

        select_query = f"SELECT date, price FROM bills_table WHERE date >= '{show_date}'"
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(select_query)
        summary = 0
        self.scr_widget.configure(state='normal')
        self.scr_widget.delete('1.0', END)
        for date, price in cursor:
            oldformat = date
            datetimeobject = datetime.strptime(oldformat, '%Y-%m-%d')
            newformat = datetimeobject.strftime('%d/%m/%Y')
            widget_str = f'{newformat} : {price} zł \n'
            self.scr_widget.insert(tk.INSERT, widget_str)
            summary += int(price)
        widget_sum = f'W sumie: {summary} zł \n'
        self.scr_widget.insert(tk.INSERT, widget_sum)
        self.scr_widget.configure(state='disabled')

    def _remove_selected_bill(self):
        chose = self.tree.selection()[0]
        dict = self.tree.set(chose)
        shop = dict['shop']
        type = dict['type']
        price = dict['price']
        date = dict['date']
        oldformat = date
        datetimeobject = datetime.strptime(oldformat, '%d/%m/%Y')
        date = datetimeobject.strftime('%Y-%m-%d')

        connection = self.get_connection()
        cursor = connection.cursor()
        pre_query = 'SET SQL_SAFE_UPDATES = 0;'
        delete_query = f"DELETE from bills_table WHERE shop='{shop}' and type='{type}' and price={price} and date='{date}';"
        cursor.execute(pre_query)
        cursor.execute(delete_query)
        connection.commit()
        connection.close()
        self.refresh()

    def _edit_bill(self):
        chose = self.tree.selection()[0]
        dict = self.tree.set(chose)
        shop = dict['shop']
        type = dict['type']
        price = dict['price']
        date = dict['date']
        oldformat = date
        datetimeobject = datetime.strptime(oldformat, '%d/%m/%Y')
        date = datetimeobject.strftime('%Y-%m-%d')

        connection = self.get_connection()
        cursor = connection.cursor()
        pre_query = 'SET SQL_SAFE_UPDATES = 0;'
        update_shop_query = f"UPDATE bills_table SET shop='{str(self.edit_get_shop.get())}' WHERE shop='{shop}' and type='{type}' and price={price} and date='{date}';"
        update_type_query = f"UPDATE bills_table SET type='{str(self.edit_get_type.get())}' WHERE shop='{self.edit_get_shop.get()}' and type='{type}' and price={price} and date='{date}';"
        update_price_query = f"UPDATE bills_table SET price='{str(self.edit_get_price.get())}' WHERE shop='{self.edit_get_shop.get()}' and type='{self.edit_get_type.get()}' and price={price} and date='{date}';"
        edit_date = str(self.edit_get_year.get() + "-" +
                        self.edit_get_month.get() + "-" + self.edit_get_day.get())
        update_date_query = f"UPDATE bills_table SET date='{edit_date}' WHERE shop='{self.edit_get_shop.get()}' and type='{self.edit_get_type.get()}' and price={self.edit_get_price.get()} and date='{date}';"

        cursor.execute(pre_query)
        cursor.execute(update_shop_query)
        cursor.execute(update_type_query)
        cursor.execute(update_price_query)
        cursor.execute(update_date_query)
        connection.commit()
        connection.close()
        self.refresh()
        self.edit_win.destroy()

    def edit_selected_bill_window(self):
        self.edit_win = tk.Tk()
        self.edit_win.title("Edytuj rachunek")
        self.edit_win.overrideredirect()

        # self.style = ThemedStyle(self.edit_win)
        # self.style.set_theme("radiance")

        edit_bill_frame = ttk.LabelFrame(
            self.edit_win, text='Edytuj rachunek')
        edit_bill_frame.grid(column=3, row=0, sticky='NEWS',
                             pady=5, padx=5)

        ttk.Label(edit_bill_frame, text='Sklep: ').grid(
            column=0, row=0, sticky='W', pady=5)
        ttk.Label(edit_bill_frame, text='Typ: ').grid(
            column=0, row=1, sticky='W', pady=5)
        ttk.Label(edit_bill_frame, text='Cena: ').grid(
            column=0, row=2, sticky='W', pady=5)

        ttk.Label(edit_bill_frame, text='Dzień: ').grid(
            column=0, row=3, sticky='W', pady=5)
        ttk.Label(edit_bill_frame, text='Miesiąc: ').grid(
            column=2, row=3, sticky='W', pady=5)
        ttk.Label(edit_bill_frame, text='Rok: ').grid(
            column=4, row=3, sticky='W', pady=5)

        self.edit_shop = tk.StringVar()
        self.edit_get_shop = ttk.Combobox(
            edit_bill_frame, width=12, textvariable=self.edit_shop)
        self.edit_get_shop['values'] = self.get_shop_list()
        self.edit_get_shop.grid(column=1, row=0, sticky='WE', columnspan=6)

        self.edit_type = tk.StringVar()
        self.edit_get_type = ttk.Combobox(
            edit_bill_frame, width=12, textvariable=self.edit_type)
        self.edit_get_type['values'] = self.get_type_list()
        self.edit_get_type.grid(column=1, row=1, sticky='WE', columnspan=6)

        self.edit_price = tk.StringVar()
        self.edit_get_price = ttk.Entry(
            edit_bill_frame, width=15, textvariable=self.edit_price)
        self.edit_get_price.grid(column=1, row=2, sticky='WE', columnspan=6)

        today_combobox = self.get_today()
        self.edit_day = tk.StringVar()
        self.edit_get_day = ttk.Combobox(edit_bill_frame, width=2,
                                         textvariable=self.edit_day, state='readonly')
        self.edit_get_day['values'] = self.days_range()
        self.edit_get_day.current(int(today_combobox[0])-1)
        self.edit_get_day.grid(column=1, row=3)

        self.edit_month = tk.StringVar()
        self.edit_get_month = ttk.Combobox(edit_bill_frame, width=2,
                                           textvariable=self.edit_month, state='readonly')
        self.edit_get_month['values'] = self.months_range()
        self.edit_get_month.current(int(today_combobox[1])-1)
        self.edit_get_month.grid(column=3, row=3)

        self.edit_year = tk.StringVar()
        self.edit_get_year = ttk.Entry(
            edit_bill_frame, width=4, textvariable=self.edit_year)
        self.edit_get_year.insert(0, today_combobox[2])
        self.edit_get_year.grid(column=5, row=3)

        edit_bill_button = ttk.Button(
            edit_bill_frame, text="OK!", command=self._edit_bill)
        edit_bill_button.grid(
            column=0, row=4, columnspan=7, sticky='SWE', pady=5)


### Main section ###
objwin = Window()
objwin.win.mainloop()
