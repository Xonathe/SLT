from PySide2.QtCore import QUrl, QSize, QTimer, Qt, QThread, Signal
from PySide2.QtGui import QIcon, QMovie, QIntValidator, QPixmap, QFont
from PySide2.QtWidgets import QLineEdit, QMainWindow, QPushButton, QToolBar, QWidget, QHBoxLayout, QLabel, \
    QSpacerItem, QSizePolicy, QVBoxLayout, QStackedWidget
from PySide2.QtWebEngineWidgets import QWebEngineView
from configparser import ConfigParser
import keyboard
from fast_bitrix24 import Bitrix
from datetime import datetime
import time
from webhook import webhook
from os import path, mkdir

bitrix = Bitrix(webhook)
work_place = {"1": "832", "2": "833", "3": "834", "4": "835", "5": "836", "6": "837", "7": "838", "10": "839"}


def timer():
    t = datetime.now()
    t = t.strftime('%d.%m.%Y %H:%M:%S')
    return t


def write_log(text, type_log):
    """Пишет лог"""
    log = "C:\\SLT Logs"
    if not path.exists(log):
        mkdir(log)
    cur_time = str(datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
    with open(f'{log}\\{type_log}.log', 'a') as f:
        f.write(f'{cur_time} : {text}\n')


class FindStudent(QThread):
    signal = Signal(list)

    def __init__(self, comp, flag, parent=None):
        QThread.__init__(self, parent)
        self.comp = comp
        self.flag = flag

    def get_key(self, d, value):
        for k, v in d.items():
            if v == value:
                return k

    def run(self):
        if self.flag == "1":
            arr = [work_place[self.comp], None]
        else:
            arr = [work_place[self.comp]]
        while True:
            deals = bitrix.get_all(
                'crm.deal.list',
                params={  # имя, ид, номер места, логин, пароль, ссылка
                    'select': ['TITLE', 'ID', 'UF_CRM_1627850701', 'UF_CRM_1628228915', 'UF_CRM_1628228964',
                               'UF_CRM_1628229056', 'DATE_MODIFY'],
                    'filter': {'STAGE_ID': 'C16:3'}
                }
            )
            if deals:
                deals = sorted(deals, key=lambda x: (x['DATE_MODIFY']))
                for val in arr:
                    print("Ищу по имени компьютера:", self.get_key(work_place, val))
                    for deal in deals:
                        print(("Ищу в сделке:", deal["TITLE"].split(" - ")[0], deal["UF_CRM_1627850701"], deal["ID"]),
                              "journal")
                        if deal['UF_CRM_1627850701'] == val:
                            print("Запись подошла", "journal")
                            if deal['UF_CRM_1628228915'] is None or deal['UF_CRM_1628228964'] is None:
                                print("Запись подошла, но логин или пароль отсутствуют", "journal")
                                continue
                            if val is None:
                                print(("Устанавливаю сделке номер компьютера", deal["ID"]), "journal")
                                # установить рабочее место
                                bitrix.call('crm.deal.update',
                                            [{'ID': deal["ID"],
                                              'fields': {'UF_CRM_1627850701': work_place[self.comp]}}])
                            print(("Перевожу сделку на уровень тестирования", deal["ID"]), "journal")
                            # переместить в Тестрирование
                            bitrix.call('crm.deal.update', [{'ID': deal["ID"], 'fields': {'STAGE_ID': 'C16:4'}}])
                            arr = (deal['TITLE'].split(" - ")[0], deal['ID'], deal['UF_CRM_1627850701'],
                                   deal['UF_CRM_1628228915'],
                                   deal['UF_CRM_1628228964'], deal['UF_CRM_1628229056'])
                            print(arr)
                            self.signal.emit(arr)
                            return
                        else:
                            print("Запись не подходит", "journal")
            print("Начинаю поиск новых сделок...", "journal")
            time.sleep(20)


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        keyboard.add_hotkey("alt + ctrl + l", lambda: self.exit(), suppress=True)
        keyboard.add_hotkey("alt + f4", lambda: None, suppress=True)
        keyboard.add_hotkey("alt + tab", lambda: None, suppress=True)
        keyboard.add_hotkey("alt + esc", lambda: None, suppress=True)
        keyboard.add_hotkey("ctrl + p", lambda: None, suppress=True)
        keyboard.add_hotkey("left windows", lambda: None, suppress=True)
        keyboard.add_hotkey("right windows", lambda: None, suppress=True)
        self.counting = 30
        self.countdown = QTimer()
        self.countdown.timeout.connect(self.show_time)

    def thread_start(self):
        self.student = FindStudent(comp=self.number_pc, flag=self.swn)
        self.student.signal.connect(self.set_variables)
        self.student.finished.connect(self.get_userdata_finished)
        self.student.start()

    def setup_add_ui(self):
        self.setWindowTitle("Первый запуск")
        self.resize(298, 163)
        self.setMinimumSize(QSize(298, 163))
        self.setMaximumSize(QSize(298, 163))
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.add_widget = QWidget(self)
        self.verticalLayout = QVBoxLayout(self.add_widget)
        self.description = QLabel(self.add_widget)
        self.description.setStyleSheet(u"QLabel {color: #A34239; font: 87 12pt \\\"Arial\\\";}")
        self.description.setAlignment(Qt.AlignCenter)
        self.description.setWordWrap(True)
        self.description.setText("Введите номер компьютера:\n(от 1 до 7 места для студентов)")
        self.verticalLayout.addWidget(self.description)
        self.num = QLineEdit(self.add_widget)
        self.num.setMinimumSize(QSize(60, 40))
        self.num.setMaximumSize(QSize(60, 40))
        self.num.setStyleSheet(u"QLineEdit {font: 24px \\\"Arial\\\"; color: #A34239;}")
        self.num.setMaxLength(2)
        self.num.setValidator(QIntValidator())
        self.num.setAlignment(Qt.AlignCenter)
        self.verticalLayout.addWidget(self.num, 0, Qt.AlignHCenter)
        self.ok_button = QPushButton(self.add_widget)
        self.ok_button.setStyleSheet(
            u"QPushButton {border: 1px solid #333333; border-radius: 16px; background-color: "
            u"#A34239; font: 12pt \"Arial\"; color: #ffffff;}\n"
            "QPushButton:hover {border: 1px solid #333333; background-color: #BA4A3F;}\n"
            "QPushButton:pressed {border: 1px solid #333333; background-color: #F1B257;}")
        self.ok_button.setText("ОК")
        self.ok_button.released.connect(self.check_line)
        self.verticalLayout.addWidget(self.ok_button)
        self.setCentralWidget(self.add_widget)

    def check_line(self):
        try:
            text = self.num.text()
            if text != "":
                if 8 > int(text) > 0 or int(text) == 10:
                    self.create_config_file(text)
                else:
                    self.description.setText(
                        "Некорректное число:\n(от 1 до 7 места для студентов)")
            else:
                self.description.setText("Поле не заполнено:\n(от 1 до 7 места для студентов)")
        except ValueError:
            self.description.setText(
                "Некорректное число:\n(от 1 до 7 места для студентов)")

    def create_config_file(self, text):
        config = ConfigParser()
        config.add_section("Video")
        config.set("Video", "fullscreen", "1")
        config.set("Video", "horizontal", "1024")
        config.set("Video", "vertical", "768")
        config.set("Video", "scale", "1.25")
        config.add_section("Computer")
        config.set("Computer", "Number", text)
        config.set("Computer", "searchwithoutnumber", "1")

        with open("slt.ini", "w") as config_file:
            config.write(config_file)
        self.close()
        self.setup_main_ui()
        self.show()
        self.thread_start()

    def setup_main_ui(self):
        self.get_config_data()
        if self.full_screen == "0":
            self.resize(self.x, self.y)
        else:
            self.showMaximized()
            # self.setWindowFlag(Qt.WindowStaysOnTopHint)
            self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowTitle("Система Локального Тестирования")
        self.setWindowIcon(QIcon('img/icon.ico'))
        self.stackedWidget = QStackedWidget(self)
        self.start_window()
        self.waiting_window()
        self.stackedWidget.setCurrentIndex(0)

    def start_window(self):
        start_widget = QWidget(self)
        self.sw_layout = QVBoxLayout(start_widget)
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.sw_layout.addItem(self.verticalSpacer_2)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        self.number_comp = QLabel(start_widget)
        self.number_comp.setText(self.number_pc)
        self.number_comp.setMinimumSize(QSize(250, 250))
        self.number_comp.setMaximumSize(QSize(250, 250))
        self.number_comp.setAlignment(Qt.AlignCenter)
        self.sw_layout.addWidget(self.number_comp, 0, Qt.AlignHCenter)
        self.label_fio = QLabel(start_widget)
        # self.label_fio.setText("")
        self.set_search_img()
        self.label_fio.setSizePolicy(sizePolicy)
        self.label_fio.setMinimumSize(QSize(1000, 200))
        self.label_fio.setMaximumSize(QSize(1000, 200))
        self.label_fio.setAlignment(Qt.AlignCenter)
        self.sw_layout.addWidget(self.label_fio, 0, Qt.AlignHCenter)
        sizePolicy.setHeightForWidth(self.label_fio.sizePolicy().hasHeightForWidth())
        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.sw_layout.addItem(self.verticalSpacer_3)

        self.start_button = QPushButton(start_widget)
        self.start_button.setText("Начать")
        self.start_button.setMinimumSize(QSize(350, 100))
        self.start_button.setMaximumSize(QSize(350, 100))
        self.start_button.released.connect(self.start_testing)
        self.start_button.setEnabled(False)
        self.sw_layout.addWidget(self.start_button, 0, Qt.AlignHCenter | Qt.AlignVCenter)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.sw_layout.addItem(self.verticalSpacer_4)
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.sw_layout.addItem(self.verticalSpacer)
        self.stackedWidget.addWidget(start_widget)
        self.setCentralWidget(self.stackedWidget)
        self.set_style()

    def set_search_img(self):
        gif_search = QMovie("img/loading.gif")
        gif_search.setSpeed(100)
        self.label_fio.setMovie(gif_search)
        gif_search.start()

    def waiting_window(self):
        waiting_widget = QWidget(self)
        wt_layout = QHBoxLayout(waiting_widget)
        loading = QLabel(waiting_widget)
        loading.setAlignment(Qt.AlignCenter)
        gif = QMovie("img/loading.gif")
        gif.setSpeed(500)
        loading.setMovie(gif)
        gif.start()
        wt_layout.addWidget(loading)
        self.stackedWidget.addWidget(waiting_widget)

    def test_complete_form(self):
        self.test_complete = QWidget(self)
        self.verticalLayout = QVBoxLayout(self.test_complete)
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(self.verticalSpacer_2)
        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(self.verticalSpacer_3)
        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(self.verticalSpacer_5)
        self.label_complete = QLabel(self.test_complete)
        font = QFont()
        font.setFamily(u"Bahnschrift")
        font.setPointSize(84)
        self.label_complete.setFont(font)
        self.label_complete.setText("Тест завершен")
        self.verticalLayout.addWidget(self.label_complete, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(self.verticalSpacer_7)
        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(self.verticalSpacer_6)
        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(self.verticalSpacer_4)
        self.label_timer = QLabel(self.test_complete)
        font1 = QFont()
        font1.setFamily(u"Bahnschrift")
        font1.setPointSize(20)
        self.label_timer.setFont(font1)
        self.label_timer.setText(str(self.counting))
        self.verticalLayout.addWidget(self.label_timer, 0, Qt.AlignHCenter)
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(self.verticalSpacer)
        self.stackedWidget.addWidget(self.test_complete)

    def browser_window(self):
        self.browser_widget = QWidget(self)
        bt_layout = QHBoxLayout(self.browser_widget)
        bt_layout.setContentsMargins(0, 0, 0, 0)
        self.browser_page = QWebEngineView(self.browser_widget)
        self.browser_page.page().profile().cookieStore().deleteAllCookies()
        self.browser_page.loadFinished.connect(self.get_test_completion)
        self.browser_page.loadFinished.connect(self.get_current_url)
        bt_layout.addWidget(self.browser_page)
        self.toolbar = QToolBar(self.browser_widget)
        self.toolbar.setMovable(False)
        self.toolbar.setMinimumSize(QSize(0, 40))
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        self.toolbar.setStyleSheet("QToolBar{spacing:15px}")
        self.label_logo = QLabel(self.browser_widget)
        self.label_logo.setPixmap(QPixmap("img/icon.ico"))
        self.label_logo.setScaledContents(True)
        self.label_logo.setMinimumSize(QSize(40, 40))
        self.label_logo.setMaximumSize(QSize(40, 40))
        self.label_logo.setMargin(5)
        self.label_fio_tool = QLabel(self.browser_widget)
        self.label_fio_tool.setText("")
        self.label_fio_tool.setStyleSheet(u"font: 14pt \"Bahnschrift\";")
        between = QWidget()
        between.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_side = QWidget()
        left_side = QWidget()
        left_side.setMinimumSize(0, 20)
        right_side.setMinimumSize(5, 20)

        # Для отладки
        # one = QAction("One", self.browser_widget)
        # two = QAction("Two", self.browser_widget)
        # three = QAction("Three", self.browser_widget)
        # one.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        # two.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        # three.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        # self.toolbar.addAction(one)
        # self.toolbar.addAction(two)
        # self.toolbar.addAction(three)
        # Для отладки

        self.toolbar.addWidget(left_side)
        self.toolbar.addWidget(self.label_logo)
        self.toolbar.addWidget(between)
        self.toolbar.addWidget(self.label_fio_tool)
        self.toolbar.addWidget(right_side)
        self.stackedWidget.addWidget(self.browser_widget)
        self.toolbar.hide()

    def fill_data(self):
        self.browser_page.page().runJavaScript(f"""
                        document.body.style.zoom = {self.scale}
                        document.getElementById("hd_loginform_container").remove();
                        document.getElementsByName('USER_LOGIN')[0].value ='{self.user}';
                        document.getElementsByName('USER_PASSWORD')[0].value ='{self.password}';
                        document.getElementsByClassName('btn btn-primary')[0].click();
        """
                                               )

    def start_testing(self):
        self.stackedWidget.setCurrentIndex(1)
        QTimer.singleShot(1 * 1000, self.display)

    def display(self):
        self.toolbar.show()
        self.stackedWidget.setCurrentIndex(2)

    # def get_current_url1(self):
    #     cur_url = self.browser_page.url().url()
    #     login = cur_url.find("login=yes")
    #     if login != -1:
    #         if not self.start_button.isEnabled():
    #             print("Кнопка активирована", "journal")
    #             self.start_button.setEnabled(True)

    def get_current_url(self):
        def callback(val):
            if val == 1.0:
                if not self.start_button.isEnabled():
                    print("Кнопка активирована", "journal")
                    self.start_button.setEnabled(True)

        js = """
                let num = 0
                var but = document.getElementsByName('next')[0];
                //but.click();
                if(but){num = 1;}
                num;
        """
        self.browser_page.page().runJavaScript(js, 0, callback)

    def get_test_completion(self):
        def callback(val):
            if val == "Выполнение теста завершено." or val == "Тест сдан":
                self.test_complete_form()
                self.stackedWidget.setCurrentIndex(3)
                self.countdown.start(1000)

                print(("Перевожу сделку на уровень получения результата", self.user_id), "journal")
                # переместить в Получение результата
                bitrix.call('crm.deal.update', [{'ID': self.user_id, 'fields': {'STAGE_ID': 'C16:5'}}])
                print("Тест завершен, 30 сек до нового пользователя", "journal")
                self.user = ""
                QTimer.singleShot(30 * 1000, self.return_initial_data)
                print("Новый пользователь", "journal")

        js = "var complete = document.getElementsByClassName('notetext')[0].textContent; complete;"
        self.browser_page.page().runJavaScript(js, 0, callback)

    def show_time(self):
        self.counting -= 1
        self.label_timer.setText(str(self.counting))
        if self.counting == 0:
            self.countdown.stop()
            self.counting = 30

    def get_config_data(self):
        config = ConfigParser()
        config.read("slt.ini")
        self.full_screen = config.get("Video", "FullScreen")
        self.x = config.getint("Video", "Horizontal")
        self.y = config.getint("Video", "Vertical")
        self.scale = config.get("Video", "Scale")
        self.number_pc = config.get("Computer", "Number")
        self.swn = config.get("Computer", "searchwithoutnumber")

    def set_variables(self, s):
        self.browser_window()
        self.label_fio.setText(s[0])
        self.label_fio_tool.setText(s[0] + " (" + s[3] + ")")
        self.user_id = s[1]
        self.user = s[3]
        self.password = s[4]
        self.start_url = s[5]

    def get_userdata_finished(self):  # Вызывается при завершении потока
        self.browser_page.load(QUrl(self.start_url))
        self.browser_page.loadFinished.connect(self.fill_data)

    def return_initial_data(self):
        self.set_search_img()
        self.label_fio_tool.setText("")
        self.user_id = ""
        self.user = ""
        self.password = ""
        self.start_url = ""
        self.toolbar.hide()
        self.start_button.setEnabled(False)
        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget.removeWidget(self.browser_widget)
        self.stackedWidget.removeWidget(self.test_complete)
        self.thread_start()

    def set_style(self):
        self.number_comp.setStyleSheet(u"QLabel {\n"
                                       "font: 75 172pt \"Bahnschrift\";\n"
                                       "color: #BA4A3F\n"
                                       "}")
        self.label_fio.setStyleSheet(u"QLabel { color: #A34239;\n"
                                     "font: 87 58pt \"Bahnschrift\";\n"
                                     "}\n"
                                     "font: 75 46pt \"Bahnschrift\";")
        self.start_button.setStyleSheet(u"QPushButton {\n"
                                        "border-radius: 16px;\n"
                                        "font: 32pt \"Bahnschrift\";\n"
                                        "color: #ffffff;\n"
                                        "}\n"
                                        "QPushButton:enabled {\n"
                                        "background-color: #A34239;\n"
                                        "border: 1px solid #333333;\n"
                                        "}\n"
                                        "QPushButton:hover {\n"
                                        "background-color: #BA4A3F;\n"
                                        "border: 1px solid #333333;\n"
                                        "}\n"
                                        "QPushButton:pressed {\n"
                                        "background-color: #F1B257;\n"
                                        "border: 1px solid #333333;\n"
                                        "}\n"
                                        "QPushButton:disabled {\n"
                                        "background-color: rgba(163, 66, 57, 70);\n"
                                        "}")

    def exit(self):
        if self.user != "":
            bitrix.call('crm.deal.update', [{'ID': self.user_id, 'fields': {'STAGE_ID': 'C16:5'}}])
            print("Выход с передвижением в Получение результата", "journal")
        else:
            print("Пользователь не найден, выход", "journal")
        self.close()
