from app import app
from base_path import base_path
from edit_configs import EditConfigs
from edit_user import EditUser
from components import Wait

from datetime import datetime

import pages

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QPushButton as QButton

import qbuilder
from read_configs import read_configs

import sys

tables = {
    "venda": [
        "id", "data", "cliente", "vendedor", "totalpago"
    ],
    
    "produto": [
        "id", "nome", "preco", "estoque", "prazo", "fornecedor", "tipo"
    ],
    
    "produtovendido": [
        "id", "produto", "venda", "quantidade"
    ],
    
    "vendedor": [
        "id", "nome", "contacto", "data", "senha", "admin"
    ],
    
    "log": [
        "id", "type", "date", "content"
    ],
    
    "info": [
        "id", "`key`", "value"
    ]
}

class Login(QObject):
    start        = pyqtSignal(list, qbuilder.QBuilder, dict, list)
    clear_fields = pyqtSignal()
    critical     = pyqtSignal(str)
    wait_start   = pyqtSignal()
    wait_stop    = pyqtSignal()
    finished     = pyqtSignal()
        
    def run(
        self,
        name: QLineEdit,
        password: QLineEdit
    ):
        
        self.wait_start.emit()
                
        user_name     = name.text()
        user_password = password.text()
        
        self.clear_fields.emit()
        
        CONFIGS = read_configs()
        
        try:
            database = qbuilder.QBuilder(
                CONFIGS["db_type"],
                tables,
                CONFIGS["db_name_"+CONFIGS["db_type"]],
                CONFIGS["db_host"],
                CONFIGS["db_user"],
                CONFIGS["db_password"]
            )
        except qbuilder.ErrorToConnect as e:
            self.wait_stop.emit()
            self.critical.emit(
                e.message+"\nverifique os dados de configuração"
            )
            self.finished.emit()
            return
        
        user = database["vendedor"].get({
            "$and": [
                {"nome": {"eq": f"'{user_name}'"}},
                {"senha": {"eq": f"'{user_password}'"}}
            ]
        })
        
        info = database["info"].all()
        
        if user:
            list_pages = [
                "Home",
                *(["Vendas", "Produto", "Vendedor"] if user["admin"]else[])
            ]
            
            self.start.emit(list_pages, database, user, info)
        else:
            self.wait_stop.emit()
            self.critical.emit("Usuário não encontrado")
            self.finished.emit()
            return
        
        self.wait_stop.emit()
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowIcon(QIcon(base_path+"/img/icon.ico"))
        
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(QVBoxLayout())
        self.centralWidget().layout().setContentsMargins(*([0]*4))
        
        open_edit_configs = self.addAction("")
        open_edit_configs.triggered.connect(lambda: EditConfigs(self))
        open_edit_configs.setShortcut("Ctrl+l")
        
        self.drow_login()
        
    def start(self, list_pages, database: qbuilder.QBuilder, vendedor: dict, info: list):
        self.database = database
        self.vendedor = vendedor
        
        open_user_configs = self.addAction("")
        open_user_configs.triggered.connect(lambda: EditUser(self, self.database, self.vendedor["id"]))
        open_user_configs.setShortcut("Ctrl+p")
        
        top_bar = QWidget()
        top_bar.setLayout(QHBoxLayout())
        top_bar.layout().setContentsMargins(*([5]*4))
        
        lbl_vendedor = QLabel(f"Utilizador: {self.vendedor['nome']}")
        lbl_vendedor.setProperty("class", "better-visible2")
        
        top_bar.layout().addWidget(lbl_vendedor)
        top_bar.layout().addStretch()
         
        months = [
            "Janeiro",
            "Fevereiro",
            "Março",
            "Abril",
            "Maio",
            "Junho",
            "Julho",
            "Agosto",
            "Setembro",
            "Outubro",
            "Novembro",
            "Desembro"
        ]
        
        weekdays = [
            "Segunda",
            "Terça",
            "Quarta",
            "Quinta",
            "Sexta",
            "Sabado",
            "Domingo"
        ]
        
        lbl_date = QLabel()
        lbl_date.setAlignment(Qt.AlignmentFlag.AlignBottom)
        lbl_date.setObjectName("date")
        lbl_time = QLabel()
        lbl_time.setObjectName("time")
        
        top_bar.layout().addWidget(lbl_date)
        top_bar.layout().addWidget(lbl_time)
        
        def update_date():
            date = datetime.now()
             
            lbl_date.setText(
                f"{weekdays[date.weekday()]}, "
                f"{date.day} de {months[date.month-1]} de {date.year}"
            )
            
            lbl_time.setText(
                f"{0 if date.hour < 10 else ''}{date.hour}:"
                f"{0 if date.minute < 10 else ''}{date.minute}:"
                f"{0 if date.second < 10 else ''}{date.second}"
            )
        
        update_date()
        
        timer_date = QTimer(self)
        timer_date.setInterval(1000)
        timer_date.timeout.connect(update_date)
        timer_date.start()
        
        self.centralWidget().layout().addWidget(top_bar)
        
        self.main = QTabWidget()
            
        self.widget_login.setVisible(False)
        del self.widget_login
        
        self.centralWidget().layout().addWidget(self.main)
        
        win.showMaximized()
        for in_ in info:
            try:
                if in_["key"] == "nome": win.setWindowTitle(in_["value"])
            except: pass
        
        for page in list_pages:
            view = QWidget()
            view_layout = getattr(pages, page)(
                self,
                vendedor,
                database,
                self.login_thread
            )
            view.setLayout(view_layout)
            self.main.addTab(view, page)
        
    def drow_login(self):
        self.setWindowTitle("Login")
        self.resize(400, 300)
        
        self.widget_login = QWidget()
        
        self.widget_login.setObjectName("login")
        self.widget_login.setProperty("class", "bg-main")
        self.centralWidget().layout().addWidget(self.widget_login)
        
        self.widget_login.setLayout(QVBoxLayout())
        
        self.widget_login.layout().addStretch()
        self.widget_login.layout().addStretch()
        
        name = QLineEdit()
        name.setProperty("class", "edit")
        self.widget_login.layout().addWidget(QLabel("Nome"))
        self.widget_login.layout().addWidget(name)

        self.widget_login.layout().addStretch()

        password = QLineEdit()
        password.setProperty("class", "edit")
        password.setEchoMode(QLineEdit.EchoMode.Password)
        self.widget_login.layout().addWidget(QLabel("Palavra Passe"))
        self.widget_login.layout().addWidget(password)

        self.widget_login.layout().addStretch()

        btn_login = QButton("entrar")
        
        wait = Wait(self)
        
        self.login_thread = QThread()
        login             = Login()
        
        login.moveToThread(self.login_thread)
        login.start.connect(self.start)
        login.wait_start.connect(wait.show)
        login.wait_stop.connect(wait.hide)
        login.finished.connect(self.login_thread.quit)
        
        def clear_fields():
            name.clear()
            password.clear()
        
        def critical(msg):
            name.setFocus()
            QMessageBox.critical(self, "error", msg)
        
        login.clear_fields.connect(clear_fields)
        login.critical.connect(critical)
        
        btn_login.clicked.connect(self.login_thread.start)
        btn_login.clicked.connect(lambda: login.run(name, password))
        
        btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_login.setProperty("class", "btn")
        self.widget_login.layout().addWidget(btn_login)
        
        name.returnPressed.connect(password.setFocus)
        password.returnPressed.connect(btn_login.click)

        self.widget_login.layout().addStretch()
        self.widget_login.layout().addStretch()

if __name__ == "__main__":        
    win = MainWindow()
    win.show()
    
    sys.exit(app.exec())
