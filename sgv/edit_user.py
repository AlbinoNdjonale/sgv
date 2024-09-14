from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QPushButton as QButton

from qbuilder import QBuilder

class EditUser(QDialog):
    def __init__(self, parent, database: QBuilder, id_user):
        super().__init__(parent)
        
        self.id_user = id_user
        self.database = database
        self.setProperty("class", "box")
        self.setObjectName("edit-user")
        
        self.setWindowTitle("Alterar password")
        self.resize(400, 300)
        self.setLayout(QVBoxLayout())
        
        self.layout().addWidget(QLabel("Palavra passe"))
        self.password = QLineEdit()
        self.password.setProperty("class", "edit")
        self.layout().addWidget(self.password)
        
        self.layout().addWidget(QLabel("Nova Palavra passe"))
        self.new_password = QLineEdit()
        self.new_password.setProperty("class", "edit")
        self.layout().addWidget(self.new_password)
        
        self.layout().addWidget(QLabel("Confirmar Nova Palavra passe"))
        self.confirm_new_password = QLineEdit()
        self.confirm_new_password.setProperty("class", "edit")
        self.layout().addWidget(self.confirm_new_password)
        
        btn_save = QButton("Salvar as alteraçóes")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self.save_password)
        btn_save.setProperty("class", "btn")
        self.layout().addWidget(btn_save)
        
        self.show()
        
    def save_password(self):
        password = self.password.text().strip()
        new_password = self.new_password.text().strip()
        confirm_new_password = self.confirm_new_password.text().strip()
                 
        if not all([password, new_password, confirm_new_password]):
            QMessageBox.critical(self, "Error", "Por favor preenha todos os campos")
            return
            
        user = self.database["vendedor"].get({
            "id": {"eq": self.id_user}
        })
        
        if not user["senha"] == password:
            QMessageBox.critical(self, "Error", "Palavra passe errada")
            return
        
        if not new_password == confirm_new_password:
            QMessageBox.critical(self, "Error", "Você errou a confirmação da nova palavra passe")
            return
        
        save = QMessageBox.warning(self, "Aviso", "Tens a serteza de que desejas alterar a palavra passe?")
        
        if save:
            self.database["vendedor"].update(
                { "senha": new_password },
                { "id": {"eq": self.id_user} }
            )
            
            QMessageBox.information(self, "Info", "Palavra passe alterda com sucesso.")
            
            self.hide()