from app import app
import components

from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QPushButton as QButton
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from qbuilder import QBuilder
from save_log import save_log
from formatnumber import format_number

class MultProcessing(QObject):
    to_list     = pyqtSignal(list)
    information = pyqtSignal(str)
    wait_start  = pyqtSignal()
    wait_stop   = pyqtSignal()
    restart     = pyqtSignal()
    
    def __init__(self, database: QBuilder):
        super().__init__()
        self.database = database
        self.products = self.database["produto"].all()
    
    def set_data(self):
        products = self.database["produto"].all()
        
        self.to_list.emit(products)
    
    def to_filter(self, name: str, type: str):
        products = [
            product
            for product in self.database["produto"].all()
            if name.strip().lower() in product["nome"].lower()
            and type.strip().lower() in product["tipo"].lower()
        ]
        
        self.to_list.emit(products)
        
    def to_sale(
        self,
        products: list,
        client_name: str,
        totalpago: int,
        vendedor: int
    ):
        
        self.wait_start.emit()
        
        date = datetime.now()
        
        last_sale = self.database["venda"].insert({
            "cliente"  : client_name,
            "vendedor" : vendedor,
            "totalpago": totalpago,
            "data"     : f"{date.year}-{date.month}-{date.day}"
        })
                
        for product in products:
            self.database["produtovendido"].insert({
                "produto"   : product["id"],
                "quantidade": product["quantidade"],
                "venda"     : last_sale["id"]
            })
            
            self.database["produto"].update(
                {"estoque": product["estoque"] - product["quantidade"]},
                {"id": {"eq": product["id"]}}
            )
        
        save_log(
            "venda",
            self.database,
            f"Venda bem sucedida "
            f"(id da venda = {last_sale['id']}, id do utilizador = {vendedor})"
        )
        self.wait_stop.emit()
        
        self.information.emit("Venda feita com sucesso!")
        self.restart.emit()
        self.set_data()
    
    def whatching(self, timer: QTimer):
        def whatch():
            products = self.database["produto"].all()     
            if not products == self.products:
                self.products = products
                self.set_data()
        timer.timeout.connect(whatch)
        timer.start()
        
class Home(QVBoxLayout):
    def __init__(self, master, vendedor: dict, database: QBuilder, thread: QThread):
        super().__init__()
        self.master   = master
        self.vendedor = vendedor
        self.database = database
        
        self.setContentsMargins(*([5]*4))
        
        self.timer_to_list = QTimer(self.master)
        self.timer_to_list.setInterval(10)
        self.timer_to_list.timeout.connect(self.add_to_list_product)
        
        wait = components.Wait(self.master)
        
        self.mult_processing = MultProcessing(self.database)
        self.mult_processing.moveToThread(thread)
        self.mult_processing.wait_start.connect(wait.show)
        self.mult_processing.wait_stop.connect(wait.hide)
        self.mult_processing.to_list.connect(self.to_list)
        self.mult_processing.restart.connect(self.cancel_sale)
        self.mult_processing.information.connect(
            lambda text: QMessageBox.information(
                self.master,
                "Information",
                text
            ))
        
        self.timer_whatching = QTimer(self.master)
        self.timer_whatching.setInterval(20)
        
        # Parte Superior
        top_area = QWidget()
        top_area.setLayout(QHBoxLayout())
        top_area.layout().setContentsMargins(*([0]*4))
        self.addWidget(top_area)
        
        # Canto Superior Esquerdo
        top_left_area = QWidget()
        top_left_area.setProperty("class", "box")
        top_left_area.setLayout(QVBoxLayout())
        top_area.layout().addWidget(top_left_area)
        
        form_filter_products = QWidget()
        layout_filter_products = QFormLayout()
        layout_filter_products.setContentsMargins(*([0]*4))
        form_filter_products.setLayout(layout_filter_products)
        top_left_area.layout().addWidget(form_filter_products)
        
        product_name = QLineEdit()
        product_name.setProperty("class", "edit")
        layout_filter_products.addRow(QLabel("Nomde do Produto"), product_name)
        
        product_type = QLineEdit()
        product_type.setProperty("class", "edit")
        layout_filter_products.addRow(QLabel("Tipo do Produto"), product_type)
                
        for field in product_name, product_type:
            field.textChanged.connect(lambda: self.mult_processing.to_filter(
                product_name.text(),
                product_type.text()
            ))
        
        self.numero_produto = QLabel("Número de Produtos: 0")
        self.numero_produto.setAlignment(Qt.AlignmentFlag.AlignRight)
        top_left_area.layout().addWidget(self.numero_produto)
        
        self.list_product = QListWidget()
        self.list_product.itemClicked.connect(self.item_clicked)
        self.list_product.setContentsMargins(*([5]*4))
        self.list_product.setProperty("class", "box-light")
        top_left_area.layout().addWidget(self.list_product)
        
        # Canto Superior Direito
        top_right_area = QWidget()
        top_right_area.setProperty("class", "box")
        top_right_area.setLayout(QVBoxLayout())
        top_area.layout().addWidget(top_right_area)
        
        form_add_product = QWidget()
        form_add_product.setProperty("class", "box-light")
        form_add_product.setObjectName("form_add_product")
        layout_add_product = QFormLayout()
        layout_add_product.setContentsMargins(*([5]*4))
        form_add_product.setLayout(layout_add_product)
        top_right_area.layout().addWidget(form_add_product)
        top_right_area.layout().addStretch()
        
        fields: list[tuple[str, str]] = [
            ("Nome do Produto", "nome"),
            ("Preço", "preco"),
            ("Estoque", "estoque"),
            ("Prazo", "prazo"),
            ("Fornecedor", "fornecedor"),
            ("Tipo", "tipo"),
            ("Quantidade", "quantidade")
        ]
        
        self.fields: dict[str, QLabel | QLineEdit] = {}
        
        for field, key in fields:
            if field == "Quantidade":
                self.fields[key] = QLineEdit()
                self.fields[key].returnPressed.connect(self.add_product)
                self.fields[key].setProperty("class", "edit")
                self.fields[key].setValidator(QIntValidator())
            else:
                self.fields[key] = QLabel()
                self.fields[key].setProperty("class", "no-edit")
            self.fields[key].setAlignment(Qt.AlignmentFlag.AlignRight)
            lbl = QLabel(field)
            lbl.setProperty("class", "better-visible2")
            layout_add_product.addRow(lbl, self.fields[key])
        
        self.btn_add_prodct = QButton("Adicionar a lista de compra")
        self.btn_add_prodct.clicked.connect(self.add_product)
        self.btn_add_prodct.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_prodct.setEnabled(False)
        self.btn_add_prodct.setProperty("class", "btn")
        top_right_area.layout().addWidget(self.btn_add_prodct)
        
        # Parte Inferior
        bottom_area = QWidget()
        bottom_area.setLayout(QHBoxLayout())
        bottom_area.layout().setContentsMargins(*([0]*4))
        self.addWidget(bottom_area)
        
        # Canto Inferior Esquerdo
        self.bottom_left_area = QWidget()
        self.bottom_left_area.setProperty("class", "box")
        self.bottom_left_area.setLayout(QVBoxLayout())
        bottom_area.layout().addWidget(self.bottom_left_area)
        
        scroll_bottom_left_area = QScrollArea()
        scroll_bottom_left_area.setWidgetResizable(True)
        self.bottom_left_area.layout().addWidget(scroll_bottom_left_area)
        
        self.list_product_table = components.Table([
            ("Nome", False),
            ("Preço", False),
            ("Quantidade", True)
        ])
        
        self.list_product_table.after_add_row.append(self.cost_total_and_troco)
        self.list_product_table.after_remove_row.append(self.cost_total_and_troco)
        self.list_product_table.after_change.append(self.cost_total_and_troco)
        
        scroll_bottom_left_area.setWidget(self.list_product_table)
        scroll_bottom_left_area.setContentsMargins(*([0]*4))
        
        # Canto Inferior Direito
        bottom_right_area = QWidget()
        bottom_right_area.setProperty("class", "box")
        bottom_right_area.setLayout(QVBoxLayout())
        bottom_area.layout().addWidget(bottom_right_area)
        
        form_sale = QWidget()
        form_sale.setObjectName("form_sale")
        layout_sale = QFormLayout()
        layout_sale.setContentsMargins(*([5]*4))
        form_sale.setLayout(layout_sale)
        bottom_right_area.layout().addWidget(form_sale)
        form_sale.setProperty("class", "box-light")
        
        self.cost_total = QLabel("0.00 KZ")
        self.cost_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout_sale.addRow(QLabel("Total a Pagar"), self.cost_total)
        
        self.value_received = QLineEdit()
        self.value_received.textChanged.connect(self.calculate_troco)
        self.value_received.setValidator(QIntValidator())
        self.value_received.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.value_received.setProperty("class", "edit")
        layout_sale.addRow(QLabel("Valor Recebido"), self.value_received)
        
        self.troco = QLabel("0.00 KZ")
        self.troco.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout_sale.addRow(QLabel("Troco"), self.troco)
        
        self.client_name = QLineEdit()
        self.client_name.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.client_name.setProperty("class", "edit")
        layout_sale.addRow(QLabel("Nomde do Cliente"), self.client_name)
        
        bottom_right_area.layout().addStretch()
        
        btn_sale = QButton("Vendido")
        btn_sale.clicked.connect(self.to_sale)
        btn_sale.setCursor(Qt.CursorShape.PointingHandCursor)
        bottom_right_area.layout().addWidget(btn_sale)
        btn_sale.setProperty("class", "btn")
        
        area_to_cancel = QWidget()
        bottom_right_area.layout().addWidget(area_to_cancel)
        area_to_cancel.setLayout(QHBoxLayout())
        area_to_cancel.layout().setContentsMargins(*([0]*4))
        
        btn_cancel = QButton("Cancelar Venda")
        btn_cancel.clicked.connect(self.cancel_sale)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setProperty("class", "btn-cancel")
        area_to_cancel.layout().addStretch()
        area_to_cancel.layout().addWidget(btn_cancel)
        
        ####################################################
        
        self.mult_processing.set_data()
        self.mult_processing.whatching(self.timer_whatching)
        
    def to_sale(self):
        products = self.list_product_table.get_rows()
        
        if len(products) == 0:
            QMessageBox.critical(self.master, "Erro", "Não há produtos selecionados.")
            return
        
        client_name = self.client_name.text().strip()\
            if self.client_name.text().strip()\
            else "Consumidor Final"
            
        cost_total = int(self.cost_total.text()\
            .replace(".00 KZ", "")\
            .replace(" ", "")
        )
        
        value_received = self.value_received.text().strip()
        value_received = int(value_received) if value_received else 0
        
        if cost_total > value_received:
            QMessageBox.critical(self.master, "Erro", "Valor insuficiente.")
            self.value_received.setFocus()
            return
        
        self.mult_processing.to_sale(
            [
                {
                    "id"        : self.items[product["Nome"]]["id"],
                    "quantidade": int(product["Quantidade"]),
                    "estoque"   : self.items[product["Nome"]]["estoque"]
                }
                for product in products
            ],
            client_name,
            cost_total,
            self.vendedor["id"]
        )
    
    def cancel_sale(self):
        self.value_received.clear()
        self.client_name.clear()
        self.clear_selected()
        self.list_product_table.clear()
        
    def clear_selected(self):
        for key in self.fields:
            self.fields[key].clear()
        self.btn_add_prodct.setEnabled(False)
        
    def add_product(self):
        quantidade = self.fields["quantidade"].text()
        nome       = self.fields['nome'].text()
        preco      = self.fields['preco'].text()
        estoque    = self.fields['estoque'].text()
        
        if quantidade.strip() == "" or int(quantidade.strip()) < 1:
            QMessageBox.critical(self.master, "Erro", "Digite a quantidade do produto")
            self.fields["quantidade"].setFocus()
        elif int(quantidade) > int(estoque):
            QMessageBox.critical(self.master, "Erro", "A quantidade de produtos excedeu o nosso estoque")
            self.fields["quantidade"].setFocus()
        else:
            self.list_product_table.add_row([
                nome,
                preco,
                quantidade
            ])
            
            self.clear_selected()
            
    def calculate_troco(self):
        cost_total = int(self.cost_total.text()\
            .replace(".00 KZ", "")\
            .replace(" ", "")
        )
        
        value_received = self.value_received.text().strip()
        value_received = int(value_received) if value_received else 0
        
        if (troco := (value_received - cost_total)) > 0:
            self.troco.setText(format_number(troco))
        else:
            self.troco.setText("0.00 KZ")
            
    def calculate_cost_total(self):
        products = self.list_product_table.get_rows()
        
        cost_total = sum([int(product["Preço"]\
            .replace(".00 KZ", "")\
            .replace(" ", ""))*int(product["Quantidade"])
            for product in products]
        )
    
        self.cost_total.setText(format_number(cost_total))
    
    def cost_total_and_troco(self, *args):
        self.calculate_cost_total()
        self.calculate_troco()
    
    def item_clicked(self, item: QLabel):
        for key, value in self.items[item.text()].items():
            if key == "id": continue
            if key == "prazo":
                value = str(value).split("-")
                value.reverse()
                value = "/".join(value)
            if key == "preco":
                self.fields[key].setText(format_number(value))
            else:
                self.fields[key].setText(str(value).replace("None", "Vazio"))
                
        self.fields["quantidade"].clear()
        self.fields["quantidade"].setFocus()
        self.btn_add_prodct.setEnabled(True)     
    
    def add_to_list_product(self):
        if self.count_to_list == len(self.products):
           self.numero_produto.setText(f"Número de Produtos: {self.list_product.count()}")
           self.timer_to_list.stop()
           return
           
        self.items[self.products[self.count_to_list]["nome"]] = self.products[self.count_to_list]
        self.list_product.addItem(self.products[self.count_to_list]["nome"])
        self.numero_produto.setText(f"Número de Produtos: {self.list_product.count()}")
        self.count_to_list += 1
    
    def to_list(self, products: list[dict]):
        self.items: dict[str, dict] = {}
        
        self.list_product.clear()
        
        self.products = products
        
        self.count_to_list = 0
        
        if not self.timer_to_list.isActive():
            self.timer_to_list.start()