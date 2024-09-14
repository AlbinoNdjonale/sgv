from app import app
import components

from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QPushButton as QButton
from PyQt6.QtCore import *

from qbuilder import QBuilder
from save_log import save_log

class MultProcessing(QObject):
    set_text_log = pyqtSignal(str)
    to_list      = pyqtSignal(list)
    
    def __init__(self, database: QBuilder):
        super().__init__()
        self.database = database
        self.vendedores = self.database["vendedor"].all()
        
    def set_data(self):
        products = self.database["vendedor"].all(order_by = "nome")
        
        self.set_log()
        
        self.to_list.emit([
            [
                product["id"],
                product["nome"],
                product["contacto"],
                product["data"],
                "Sim" if product["admin"] else "Não"
             ]
            for product in products
        ])
            
    def set_log(self):
        logs = self.database["log"].all(order_by = "-date", where = {"type": {"eq": "'vendedor'"}})
            
        self.set_text_log.emit("\n\n".join([log["content"] for log in logs]))
        
    def to_filter(
        self,
        id         : QLineEdit,
        nome       : QLineEdit,
        contacto   : QLineEdit,
        data       : QLineEdit,
        admin      : QLineEdit,
        timer      : QTimer
    ):
        
        def check(vendedor): 
            if (id.text().strip() == str(vendedor["id"]) or not id.text().strip())\
            and nome.text().strip().lower() in vendedor["nome"].lower()\
            and contacto.text().strip() in vendedor["contacto"]\
            and data.text().strip() in vendedor["data"]\
            and ((admin.text().strip().lower() == ("sim" if vendedor["admin"] else "não")) or not admin.text().strip()):
                return True
            
            return False
            
        vendedores = [
            [
                vendedor["id"],
                vendedor["nome"],
                vendedor["contacto"],
                vendedor["data"],
                "Sim" if vendedor["admin"] else "Não"
            ]
            for vendedor in self.database["vendedor"].all("nome")
            if check(vendedor)
        ]
        
        self.to_list.emit(vendedores)
        timer.stop()
    
    def save_change(self, master, changes, deletes, vendedor):
        save = QMessageBox.warning(master, "Aviso", "Tens a certeza de que dezejas guardar as alterações feitas?")
        
        if save:
            if deletes:     
                self.database["vendedor"].delete({
                    "$or": [
                        {"id": {"eq": delete["Id"]}}
                        for delete in deletes
                    ]
                })
                
                for delete in deletes:
                    save_log(
                        "vendedor",
                        self.database,
                        "Vendedor deletado com secesso"
                        f"(id do vendedor = {delete['Id']}, id do utilizador = {vendedor})"
                    )
            
            for change in changes:
                self.database["vendedor"].update(
                    {
                        "nome"      : change["Nome"],
                        "contacto"  : change["Contacto"],
                        "data"      : change["Data de Nascimento"],
                        "admin"     : 1 if change["Admin"].strip().lower() == "sim" else 0
                    },
                    {"id": {"eq": change["Id"]}}
                )
                
                save_log(
                    "vendedor",
                    self.database,
                    "Vendedor alterado com secesso"
                    f"(id do vendedor = {change['Id']}, id do utilizador = {vendedor})"
                )
                
            QMessageBox.information(master, "Info", "Alterações salvadas com sucesso.")
        
    def register(self, master, data, vendedor):
        register = QMessageBox.warning(master, "Aviso", "Tens a certeza de que dezejas adicionar este registro?")
        
        if register:
            last_vendedor = self.database["vendedor"].insert(data)
            
            save_log(
                "vendedor",
                self.database,
                "Vendedor adicionado com secesso"
                f"(id do vendedor = {last_vendedor['id']}, id do utilizador = {vendedor})"
            )
                       
            QMessageBox.information(master, "Info", "Vendedor adicionado com sucesso.")
    
    def whatching(self, timer: QTimer):
        def whatch():
            vendedores = self.database["vendedor"].all()
            if not vendedores == self.vendedores:
                self.set_data()
                self.vendedores = vendedores
        timer.timeout.connect(whatch)
        timer.start()
                    
class Vendedor(QHBoxLayout):
    def __init__(self, master, vendedor: dict, database: QBuilder, thread: QThread):
        super().__init__()
        self.master   = master
        self.vendedor = vendedor
        self.database = database
        
        self.products_to_remove: list[dict] = []
        
        self.setContentsMargins(*([5]*4))
        
        self.timer_to_list = QTimer(self.master)
        self.timer_to_list.setInterval(10)
        self.timer_to_list.timeout.connect(self.add_to_table_product)
        
        self.timer_to_filter = QTimer(self.master)
        self.timer_to_filter.setInterval(600)
        
        self.mult_processing = MultProcessing(self.database)
        self.mult_processing.moveToThread(thread)
        self.mult_processing.to_list.connect(self.to_list)
        
        self.timer_whatching = QTimer(self.master)
        self.timer_whatching.setInterval(20)
        
        # Parte Esquerda
        left_area = QWidget()
        left_area.setLayout(QVBoxLayout())
        left_area.layout().setContentsMargins(*([0]*4))
        self.addWidget(left_area)
        left_area.setMaximumWidth(550)
        
        # Canto Superior esquerdo
        left_top_area = QWidget()
        left_top_area.setProperty("class", "box")
        left_top_area.setLayout(QVBoxLayout())
        left_area.layout().addWidget(left_top_area)
        
        lbl_add_product = QLabel("Adicionar Produto")
        lbl_add_product.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_add_product.setProperty("class", "better-visible2")
        left_top_area.layout().addWidget(lbl_add_product)
        
        widget_add_product = QWidget()
        widget_add_product.setProperty("class", "box-light")
        left_top_area.layout().addWidget(widget_add_product)
        form_add_product = QFormLayout()
        widget_add_product.setLayout(form_add_product)
        
        self.fields_register: dict[str, QLineEdit] = {}
        
        labels: list[tuple[str, str]] = [
            ("Nome", "nome"),
            ("Contacto", "contacto"),
            ("Data de Nascimento", "data"),
            ("Senha", "senha"),
            ("Admin", "admin")
        ]
        
        for label, key in labels:
            field = QLineEdit()
            self.fields_register[key] = field
            field.setProperty("class", "edit")
            form_add_product.addRow(QLabel(label), field)
        
        btn_add_product = QButton("registrar")
        btn_add_product.clicked.connect(self.register)
        btn_add_product.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_product.setProperty("class", "btn")
        left_top_area.layout().addWidget(btn_add_product)
        
        btn_add_product_cancel = QButton("Cancelar")
        btn_add_product_cancel.clicked.connect(lambda: [field.clear() for field in self.fields_register.values()])
        btn_add_product_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_product_cancel.setProperty("class", "btn-cancel")
        wraper_btn_cancel = QWidget()
        wraper_btn_cancel.setLayout(QHBoxLayout())
        wraper_btn_cancel.layout().setContentsMargins(*([0]*4))
        wraper_btn_cancel.layout().addStretch()
        wraper_btn_cancel.layout().addWidget(btn_add_product_cancel)
        left_top_area.layout().addWidget(wraper_btn_cancel)
        
        # Canto Inferior esquerdo
        left_bottom_area = QWidget()
        left_bottom_area.setProperty("class", "box")
        left_bottom_area.setLayout(QVBoxLayout())
        left_area.layout().addWidget(left_bottom_area)
        
        lbl_last_action = QLabel("Ultimas Ações")
        lbl_last_action.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_last_action.setProperty("class", "better-visible2")
        left_bottom_area.layout().addWidget(lbl_last_action)
        
        self.tex_log = QTextEdit()
        self.tex_log.setReadOnly(True)
        self.tex_log.setProperty("class", "box-light")
        left_bottom_area.layout().addWidget(self.tex_log)
        self.mult_processing.set_text_log.connect(self.set_log)
        
        # Parte direita
        right_area = QWidget()
        right_area.setProperty("class", "box")
        right_area.setLayout(QVBoxLayout())
        right_area.layout().setContentsMargins(*([5]*4))
        self.addWidget(right_area)
        
        # Canto Superior direito
        lbl_visulize_sale = QLabel("Visualizar Vendedores")
        lbl_visulize_sale.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_visulize_sale.setProperty("class", "better-visible2")
        right_area.layout().addWidget(lbl_visulize_sale)
        
        form_filter = QWidget()
        form_filter.setProperty("class", "box-light")
        layout_form_filter = QFormLayout()
        layout_form_filter.setContentsMargins(*([5]*4))
        form_filter.setLayout(layout_form_filter)
        right_area.layout().addWidget(form_filter)
                
        self.fields_filter: dict[str, QLineEdit] = {}
        
        self.timer_to_filter.timeout.connect(
            lambda: self.mult_processing.to_filter(
                **self.fields_filter,
                timer = self.timer_to_filter
            ))
        
        labels: list[tuple[str, str]] = [
            ("Id", "id"),
            ("Nome", "nome"),
            ("Contacto", "contacto"),
            ("Data de Nascimento", "data"),
            ("Admin", "admin")
        ]
        
        for label, key in labels:
            field = QLineEdit()
            field.textChanged.connect(self.to_filter)
            field.setProperty("class", "edit")
            layout_form_filter.addRow(QLabel(label), field)
            
            self.fields_filter[key] = field
        
        # Canto Inferior direito
        self.lbl_n_products = QLabel(f"Total de Vendedores: 0")
        self.lbl_n_products.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_area.layout().addWidget(self.lbl_n_products)
        
        widget_table = QWidget()
        widget_table.setLayout(QVBoxLayout())
        widget_table.layout().setContentsMargins(*([0]*4))
        right_area.layout().addWidget(widget_table)
        
        scroll_table = QScrollArea()
        scroll_table.setWidgetResizable(True)
        widget_table.layout().addWidget(scroll_table)
        
        self.table = components.Table([
            ("Id", False),
            ("Nome", True),
            ("Contacto", True),
            ("Data de Nascimento", True),
            ("Admin", True)
        ])
        
        self.table.after_remove_row.append(self.remove_to_table_product)
        self.table.after_clear.append(self.products_to_remove.clear)
        
        scroll_table.setWidget(self.table)
        
        widget_save_and_cancel = QWidget()
        right_area.layout().addWidget(widget_save_and_cancel)
        widget_save_and_cancel.setLayout(QHBoxLayout())
        widget_save_and_cancel.layout().setContentsMargins(0, 5, 0, 0)
        widget_save_and_cancel.layout().addStretch()
        
        btn_save = QButton("Guardar alterações")
        btn_save.clicked.connect(self.save_change)
        
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setProperty("class", "btn")
        widget_save_and_cancel.layout().addWidget(btn_save)
        
        btn_cancel = QButton("Restaurar")
        btn_cancel.clicked.connect(lambda: self.mult_processing.set_data())
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setProperty("class", "btn-cancel")
        widget_save_and_cancel.layout().addWidget(btn_cancel)
        
        ######################################################
        
        self.mult_processing.set_data()
        self.mult_processing.whatching(self.timer_whatching)
    
    def register(self):
        self.mult_processing.register(
            self.master,
            {key: value.text() for key, value in self.fields_register.items()},
            self.vendedor["id"]
        )
        
        for field in self.fields_register.values(): field.clear()
        self.mult_processing.set_data()
        
    def save_change(self):
        self.mult_processing.save_change(
            self.master,
            self.table.get_rows_changed(),
            self.products_to_remove,
            self.vendedor["id"]
        )
        
        self.products_to_remove.clear()
        self.table.changed_rows.clear()
    
    def set_log(self, text: str):
        self.tex_log.clear()
        self.tex_log.setText(text)
        
    def to_filter(self):
        if self.timer_to_filter.isActive():
            self.timer_to_filter.stop()
        
        self.timer_to_filter.start()
        
    def remove_to_table_product(self, row, _):
        self.lbl_n_products.setText(f"Total de Vendedores: {len(self.table.rows)}")
        
        if row is not None:
            self.products_to_remove.append(row)
            
    def add_to_table_product(self):
        if self.count_to_list == len(self.sales):
            self.lbl_n_products.setText(f"Total de Vendedores: {len(self.table.rows)}")
            self.timer_to_list.stop()
            return
           
        self.table.add_row(self.sales[self.count_to_list])
        self.lbl_n_products.setText(f"Total de Vendedores: {len(self.table.rows)}")
        self.count_to_list += 1
        
    def to_list(self, sales: list[dict]):
        self.table.clear()
        self.sales = sales
        self.count_to_list = 0
        
        if not self.timer_to_list.isActive():
            self.timer_to_list.start()