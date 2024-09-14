from app import app
import components
from formatnumber import format_number

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from qbuilder import QBuilder

class MultProcessing(QObject):
    set_receita     = pyqtSignal(str)
    set_text_log    = pyqtSignal(str)
    to_list         = pyqtSignal(list)
    to_list_product = pyqtSignal(list)
    
    def __init__(self, database: QBuilder):
        super().__init__()
        self.database = database
        self.sales = self.database["venda"].all()
        
    def set_data(self):
        sales = self.database["venda"].all(order_by = "-id")
        
        self.calculate_receita(sales = sales)
        self.set_log()
        
        self.to_list.emit([
            [
                sale["id"],
                sale["data"],
                self.get_vendedor(sale["vendedor"]),
                sale["cliente"],
                format_number(sale["totalpago"])
            ]
            for sale in sales
        ])
    
    def set_data_product(self, sale_id):
        products = self.database["produtovendido", "produto"].all(
            where = {"produtovendido.venda": {"eq": sale_id}},
            on = {"produtovendido.produto": {"eq": "produto.id"}}
        )
        
        self.to_list_product.emit([
            [
                product["produto_nome"],
                format_number(product["produto_preco"]),
                product["produtovendido_quantidade"]
            ]
            for product in products
        ])
        
    def get_vendedor(self, id: int):
        if vendedor := self.database["vendedor"].get({"id": {"eq": id}}):
            return vendedor["nome"]
        
        return ""
        
    def calculate_receita(self, n_months = 3, sales = None):
        if not sales:
            sales = self.database["venda"].all(order_by = "-data")
        
        receita = sum([venda["totalpago"] for venda in sales[:n_months]])
        
        self.set_receita.emit(format_number(receita))
        
    def set_log(self):
        logs = self.database["log"].all(order_by = "-date", where = {"type": {"eq": "'venda'"}})
            
        self.set_text_log.emit("\n\n".join([log["content"] for log in logs]))
        
    def to_filter(
        self,
        id       : QLineEdit,
        date     : QLineEdit,
        vendedor : QLineEdit,
        client   : QLineEdit,
        totalpago: QLineEdit,
        products : QLineEdit,
        timer    : QTimer
    ):
        
        def check(sale):
            vendedor_name = self.get_vendedor(sale["vendedor"])
            
            products_name = self.database[
                "venda",
                "produto",
                "produtovendido"
            ].all(
                where = {"venda.id": {"eq": sale["id"]}},
                on    = {
                    "$and": [
                        {"produto.id": {"eq": "produtovendido.produto"}},
                        {"venda.id": {"eq": "produtovendido.venda"}}
                    ]
                }
            )
            
            products_name = [product["produto_nome"].lower() for product in products_name]
            
            if (id.text().strip() == str(sale["id"]) or not id.text().strip())\
            and date.text().strip() in sale["data"]\
            and vendedor.text().strip().lower() in vendedor_name.lower()\
            and client.text().strip().lower() in sale["cliente"].lower()\
            and (totalpago.text().strip() == str(sale["totalpago"])\
            or not totalpago.text().strip())\
            and (all([
                product_name.strip().lower() in products_name
                for product_name in products.text().split(";")
            ]) or not products.text().strip()):
                return True
            
            return False
            
        sales = [
            [
                sale["id"],
                sale["data"],
                self.get_vendedor(sale["vendedor"]),
                sale["cliente"],
                format_number(sale["totalpago"])
            ]
            for sale in self.database["venda"].all("-id")
            if check(sale)
        ]
        
        self.to_list.emit(sales)
        timer.stop()
    
    def whatching(self, timer: QTimer):
        
        def whatch():
            sales = self.database["venda"].all()
            if not sales == self.sales:
                self.set_data()
                self.sales = sales
                
        timer.timeout.connect(whatch)
        timer.start()
       
class Vendas(QHBoxLayout):
    def __init__(self, master, vendedor: dict, database: QBuilder, thread: QThread):
        super().__init__()
        self.master   = master
        self.vendedor = vendedor
        self.database = database
        
        self.setContentsMargins(*([5]*4))
        
        self.timer_to_list = QTimer(self.master)
        self.timer_to_list.setInterval(10)
        self.timer_to_list.timeout.connect(self.add_to_table_sale)
        
        self.timer_to_list_product = QTimer(self.master)
        self.timer_to_list_product.setInterval(10)
        self.timer_to_list_product.timeout.connect(self.add_to_table_product)
        
        self.timer_to_filter = QTimer(self.master)
        self.timer_to_filter.setInterval(600)
        
        self.mult_processing = MultProcessing(self.database)
        self.mult_processing.moveToThread(thread)
        self.mult_processing.to_list.connect(self.to_list)
        self.mult_processing.to_list_product.connect(self.to_list_product)
        
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
        
        lbl_receita = QLabel("Receitas")
        lbl_receita.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_receita.setProperty("class", "better-visible2")
        left_top_area.layout().addWidget(lbl_receita)
        
        area_n_months = QWidget()
        area_n_months.setProperty("class", "area_receita")
        area_n_months.setLayout(QHBoxLayout())
        left_top_area.layout().addWidget(area_n_months)
        area_n_months.layout().setContentsMargins(*([0]*4))
        
        area_n_months.layout().addWidget(QLabel("Receita dos"))
        spb_n_months = QSpinBox()
        spb_n_months.valueChanged.connect(
            lambda: self.mult_processing.calculate_receita(
                spb_n_months.value()
            ))
        spb_n_months.setValue(3)
        area_n_months.layout().addWidget(spb_n_months)
        area_n_months.layout().addWidget(QLabel("Ultimo(s) mesi(s)"))
        
        area_receitas = QWidget()
        area_receitas.setProperty("class", "area_receita")
        area_receitas.setLayout(QHBoxLayout())
        left_top_area.layout().addWidget(area_receitas)
        area_receitas.layout().setContentsMargins(*([0]*4))
        
        area_receitas.layout().addWidget(QLabel("Receita:"))
        lbl_receita_result = QLabel("0.00 KZ")
        area_receitas.layout().addWidget(lbl_receita_result)
        self.mult_processing.set_receita.connect(lbl_receita_result.setText)
        
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
        self.mult_processing.set_text_log.connect(self.tex_log.setText)
        
        # Parte direita
        right_area = QWidget()
        right_area.setProperty("class", "box")
        right_area.setLayout(QVBoxLayout())
        right_area.layout().setContentsMargins(*([5]*4))
        self.addWidget(right_area)
        
        # Canto Superior direito
        lbl_visulize_sale = QLabel("Visualizar Vendas")
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
            ("Data da Venda", "date"),
            ("Vendedor", "vendedor"),
            ("Cliente", "client"),
            ("Total Pago", "totalpago"),
            ("Produtos", "products")
        ]
        
        for label, key in labels:
            field = QLineEdit()
            field.textChanged.connect(self.to_filter)
            field.setProperty("class", "edit")
            layout_form_filter.addRow(QLabel(label), field)
            
            self.fields_filter[key] = field
        
        # Canto Inferior direito
        self.lbl_n_sales = QLabel(f"Total de Vendas: 0")
        self.lbl_n_sales.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_area.layout().addWidget(self.lbl_n_sales)
        
        widget_table = QWidget()
        widget_table.setLayout(QVBoxLayout())
        widget_table.layout().setContentsMargins(*([0]*4))
        right_area.layout().addWidget(widget_table)
        
        scroll_table = QScrollArea()
        scroll_table.setWidgetResizable(True)
        widget_table.layout().addWidget(scroll_table)
        
        self.table = components.Table([
            ("Id", False),
            ("Data da Venda", False),
            ("Vendedor", False),
            ("Cliente", False),
            ("Total Pago", False)
        ], True)
        
        self.table.on_doubleclick.append(self.show_products)
        
        scroll_table.setWidget(self.table)
        
        ######################################################
        
        self.mult_processing.set_data()
        self.mult_processing.whatching(self.timer_whatching)
        
    def to_filter(self):
        if self.timer_to_filter.isActive():
            self.timer_to_filter.stop()
        
        self.timer_to_filter.start()
        
    def add_to_table_sale(self):
        if self.count_to_list == len(self.sales):
            self.lbl_n_sales.setText(f"Total de Vendas: {len(self.table.rows)}")
            self.timer_to_list.stop()
            return
           
        self.table.add_row(self.sales[self.count_to_list])
        self.lbl_n_sales.setText(f"Total de Vendas: {len(self.table.rows)}")
        self.count_to_list += 1
    
    def add_to_table_product(self):
        if self.count_to_list_product == len(self.products):
            self.timer_to_list_product.stop()
            return
        
        self.table_products.add_row(self.products[self.count_to_list_product])
        self.count_to_list_product += 1
    
    def to_list(self, sales: list[dict]):
        self.table.clear()
        self.sales = sales
        self.count_to_list = 0
        
        if not self.timer_to_list.isActive():
            self.timer_to_list.start()
            
    def to_list_product(self, products: list[dict]):
        self.products = products
        self.count_to_list_product = 0
        self.timer_to_list_product.start()
            
    def show_products(self, sale, _):
        products_dialog = QDialog(self.master)
        products_dialog.setProperty("class", "box")
        products_dialog.setWindowTitle("Produtos")
        products_dialog.resize(400, 300)
        products_dialog.setLayout(QVBoxLayout())
        
        scroll_products = QScrollArea()
        scroll_products.setWidgetResizable(True)
        products_dialog.layout().addWidget(scroll_products)
        
        self.table_products = components.Table([
            ("Nome", False),
            ("Preço", False),
            ("Quantidade", False)
        ], True)
        scroll_products.setWidget(self.table_products)
        
        self.mult_processing.set_data_product(sale["Id"])
        
        products_dialog.show()