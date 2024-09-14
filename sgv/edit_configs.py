from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QPushButton as QButton

from base_path import base_path

from read_configs import read_configs
import cript

class EditConfigs(QDialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        
        self.configs = read_configs()
        
        self.resize(400, 300)
        self.setWindowTitle("Editar Configurações")
        self.setLayout(QVBoxLayout())
        self.setProperty("class", "box")
        
        lbl_configs = QLabel("Configurações da Base de dados")
        lbl_configs.setProperty("class", "better-visible2")
        self.layout().addWidget(lbl_configs)
        
        self.db_type = QComboBox()
        self.db_type.addItems([
            "sqlite",
            "mysql"
        ])
        self.db_type.setProperty("class", "edit")
        self.db_type.currentTextChanged.connect(self.display)
        
        self.layout().addWidget(self.db_type)
        
        self.stack = QStackedWidget()
        self.layout().addWidget(self.stack)
        self.stack.addWidget(self.stack_sqlite())
        self.stack.addWidget(self.stack_mysql())
        
        self.db_type.setCurrentText(self.configs["db_type"])
        
        btn_save = QButton("Salvar Alterações")
        btn_save.clicked.connect(self.save_configs)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setProperty("class", "btn")
        
        self.layout().addWidget(btn_save)
        
        self.show()
    
    def save_configs(self):
        save = QMessageBox.warning(self, "Aviso", "Tens a certeza desta operação?")
        
        if save:
            self.configs["db_type"]        = self.db_type.currentText()
            self.configs["db_host"]        = self.db_host.text()
            self.configs["db_user"]        = self.db_user.text()
            self.configs["db_password"]    = self.db_password.text()
            self.configs["db_name_sqlite"] = self.db_sqlite.text()
            self.configs["db_name_mysql"]  = self.db_mysql.text()
            
            configs = cript.desencriptar(self.configs)
            
            configs = "\n".join([f'{key} = "{value}"' for key, value in configs.items()])
            
            with open(base_path+"/files/configs.conf", "w", encoding = "utf-8" ) as file:
                file.write(configs)
            
            QMessageBox.information(self, "Info", "Alterações guardadas com sucesso.")
        
    def display(self, db_type):
        self.stack.setCurrentIndex(0 if db_type == "sqlite" else 1)
        
    def stack_sqlite(self):
        stack = QWidget()
        stack.setLayout(QVBoxLayout())
        stack.layout().setContentsMargins(*([0]*4))
        
        stack.layout().addWidget(QLabel("Selecione a base de dados"))
        
        wrapper_db = QWidget()
        stack.layout().addWidget(wrapper_db)
        wrapper_db.setLayout(QHBoxLayout())
        wrapper_db.layout().setContentsMargins(*([0]*4))
                
        self.db_sqlite = QLineEdit()
        self.db_sqlite.setProperty("class", "edit")
        wrapper_db.layout().addWidget(self.db_sqlite)
        
        def select_db():
            db = QFileDialog.getOpenFileName(self, filter = "Db Files (*.db *.sqlite3)")
            if db: self.db_sqlite.setText(db[0])
            
        btn_find_db = QButton("procurar")
        btn_find_db.clicked.connect(select_db)
        btn_find_db.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_find_db.setProperty("class", "btn")
        wrapper_db.layout().addWidget(btn_find_db)
        
        stack.layout().addStretch()
        
        return stack
    
    def stack_mysql(self):
        stack = QWidget()
        
        form_db = QFormLayout()
        stack.setLayout(form_db)
        form_db.setContentsMargins(*([0]*4))
        
        self.db_mysql = QLineEdit()
        self.db_mysql.setProperty("class", "edit")
        form_db.addRow(QLabel("Nome"), self.db_mysql)
        
        self.db_host = QLineEdit()
        self.db_host.setProperty("class", "edit")
        form_db.addRow(QLabel("Host"), self.db_host)
        
        self.db_user = QLineEdit()
        self.db_user.setProperty("class", "edit")
        form_db.addRow(QLabel("Usuário"), self.db_user)
        
        self.db_password = QLineEdit()
        self.db_password.setProperty("class", "edit")
        form_db.addRow(QLabel("Palavra Passe"), self.db_password)
                
        return stack