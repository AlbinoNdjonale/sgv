from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QPushButton as QButton
import typing

class Column(QLabel):
    def __init__(self, text: str, master, edit: bool):
        super().__init__(text)
        
        self.edit = edit
        
        self.after_text_change = []
        
        self.edit_field = QLineEdit(master)
        self.edit_field.setWindowFlag(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint
        )
        
        self.edit_field.focusOutEvent = self.finished
        self.edit_field.returnPressed.connect(self.finished)
        
    def mouseDoubleClickEvent(self, e: QMouseEvent) -> None:
        super().mouseDoubleClickEvent(e)
        
        pos = e.globalPosition().toPoint()
        
        self.edit_field.setGeometry(pos.x(), pos.y(), self.sizeHint().width()+30, 30)
        
        self.edit_field.setText(self.text())
        self.edit_field.setFocus()
        self.edit_field.show()
     
    def finished(self, e = None):
        if self.edit:
            self.setText(self.edit_field.text())
            for after in self.after_text_change: after()
        
        self.edit_field.hide()

class Table(QWidget):
    def __init__(
        self,
        columns: list[str],
        no_delete: bool = False
    ):
        super().__init__()
        
        self.no_delete    = no_delete
        self.selected_row = None
        self.changed_rows = set([])
        
        self.after_add_row: list[typing.Callable[[], None]]    = []
        self.after_remove_row: list[typing.Callable[[dict[str], int], None]] = []
        self.after_clear: list[typing.Callable[[], None]]      = []
        self.after_change: list[typing.Callable[[], None]]      = []
        
        self.after_select_row = []
        self.on_doubleclick   = []
        
        self.setLayout(QHBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(*([0]*4))
                
        self.rows: list[QWidget] = []
        
        self.table_widget = QWidget()
        self.table_widget.setLayout(QVBoxLayout())
        self.table_widget.layout().setSpacing(0)
        self.table_widget.layout().setContentsMargins(*([0]*4))
        self.layout().addWidget(self.table_widget)
            
        columns, edits = list(zip(*columns))
        
        self.edits   = list(edits)
        self.columns = ["", *columns]
        if not no_delete: self.columns.append("")
        self.columns_label: list[list[QLabel]] =  [[] for _ in self.columns]
        
        self.drow_header()
        
        self.scroll_cells = QScrollArea()
        self.scroll_cells.setWidgetResizable(True)
        self.layout().addWidget(self.scroll_cells.verticalScrollBar())
        self.scroll_cells.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_widget.layout().addWidget(self.scroll_cells)
        
        central_cells = QWidget()
        self.scroll_cells.setWidget(central_cells)
        central_cells.setLayout(QVBoxLayout())
        central_cells.layout().setSpacing(0)
        central_cells.layout().setContentsMargins(*([0]*4))
        
        self.wraper_widget_cells = QWidget()
        central_cells.layout().addWidget(self.wraper_widget_cells)
        self.wraper_widget_cells.setLayout(QVBoxLayout())
        self.wraper_widget_cells.layout().setContentsMargins(*([0]*4))
        
        self.widget_cells = QWidget()
        
        self.wraper_widget_cells.layout().addWidget(self.widget_cells)
        self.widget_cells.setLayout(QVBoxLayout())
        self.widget_cells.layout().setSpacing(0)
        self.widget_cells.layout().setContentsMargins(*([0]*4))
        
        central_cells.layout().addStretch()
        
    def on_edit_column(self, key):
        self.resizeEvent()
        self.changed_rows.add(key)
        
        for after in self.after_change: after()
        
    def drow_header(self):
        header = QWidget()
        header.setProperty("class", "theader")
        header.setLayout(QHBoxLayout())
        header.layout().setSpacing(0)
        header.layout().setContentsMargins(*([0]*4))
        
        for key, column in enumerate(self.columns):
            label_column = QLabel(str(column))
            label_column.setStyleSheet("padding: 6px")
            label_column.setWordWrap(True)
            header.layout().addWidget(label_column)
            
            self.columns_label[key].append(label_column)
       
        header.layout().addStretch()
            
        self.table_widget.layout().addWidget(header)
        
    def clear(self):
        self.wraper_widget_cells.layout().removeWidget(self.widget_cells)
        
        self.widget_cells = QWidget()
        
        self.wraper_widget_cells.layout().addWidget(self.widget_cells)
        self.widget_cells.setLayout(QVBoxLayout())
        self.widget_cells.layout().setSpacing(0)
        self.widget_cells.layout().setContentsMargins(*([0]*4))
        
        self.rows.clear()
        self.selected_row = None
        self.changed_rows = set([])
        
        for key, _ in enumerate(self.columns_label):
            del self.columns_label[key][1:]
        
        for after in self.after_clear: after()
        
        for after in self.after_remove_row: after(None, None)
    
    def remove_row(self, row: QWidget):
        if not row in self.rows: return
        
        self.widget_cells.layout().removeWidget(row)
        index = self.rows.index(row) + 1
        data_row = self.get_rows(index)
        self.rows.remove(row)
        
        if row == self.selected_row:
            self.selected_row = None
            
        if index in self.changed_rows:
            self.changed_rows.remove(index)
        
        for key, _ in enumerate(self.columns_label):
            self.columns_label[key].remove(self.columns_label[key][index])
        
        del row
        self.to_style()
        for after in self.after_remove_row: after(data_row, index)
    
    def add_row(self, columns: list[str]):
        row = QWidget()
        self.rows.append(row)
        row.setLayout(QHBoxLayout())
        row.layout().setSpacing(0)
        row.layout().setContentsMargins(*([0]*4))
        
        row_id = QButton("")
        row_id.setCursor(Qt.CursorShape.PointingHandCursor)
        row_id.clicked.connect(lambda: self.select_row(row))
        row_id.mouseDoubleClickEvent = lambda _: self.double_click(row)
        
        row_id.setStyleSheet("padding: 6px; border: none; max-width: 6px;")
        row.layout().addWidget(row_id)
        self.columns_label[0].append(row_id)
        
        for key, column in enumerate(columns):
            label_column = Column(str(column), self, self.edits[key])
            label_column.after_text_change.append(lambda: self.on_edit_column(self.rows.index(row)+1))
            label_column.setStyleSheet("padding: 6px")
            label_column.setWordWrap(True)
            row.layout().addWidget(label_column)
            self.columns_label[key+1].append(label_column)
        
        if not self.no_delete:
            wraper_btn_remover = QWidget()
            wraper_btn_remover.setLayout(QVBoxLayout())
            wraper_btn_remover.layout().setContentsMargins(*([3]*4))
            btn_remove = QButton("REMOVER")
            btn_remove.clicked.connect(lambda: self.remove_row(row))
            btn_remove.setProperty("class", "btn-remove")
            btn_remove.setCursor(Qt.CursorShape.PointingHandCursor)
            row.layout().addWidget(wraper_btn_remover)
            wraper_btn_remover.layout().addWidget(btn_remove)
            self.columns_label[key+2].append(wraper_btn_remover)
        
        row.layout().addStretch()
        
        self.widget_cells.layout().addWidget(row)
        row.setStyleSheet(f"background: #{'999' if (len(self.rows))%2==0 else 'ccc'}")
        self.resizeEvent()
        
        for after in self.after_add_row: after()
        
    def select_row(self, row: QWidget):
        if self.selected_row:
            index = self.rows.index(self.selected_row)
            self.selected_row.setStyleSheet(f"background: #{'999' if (index+1)%2==0 else 'ccc'}")
        
        row.setStyleSheet("background: #0ce;")
        self.selected_row = row
        
        for after in self.after_select_row:
            index = self.rows.index(row) + 1
            after(
                self.get_rows(index),
                index
            )
        
    def double_click(self, row: QWidget):
        for after in self.on_doubleclick:
            index = self.rows.index(row) + 1
            after(
                self.get_rows(index),
                index
            )
    
    def to_list(self, values: list[list[str | int | float]]):
        for columns in values:
            self.add_row(columns)
    
    def to_style(self):
        for key, row in enumerate(self.rows):
            row.setStyleSheet(f"background: #{'999' if (key+1)%2==0 else 'ccc'}")
    
    def get_rows(self, key: int = None) -> list[dict[str, str]]:
        if key is None:
            return [self.get_rows(key+1) for key, _ in enumerate(self.rows)]
        
        columns_label = (self.columns_label\
        if self.no_delete else self.columns_label[:-1])
        
        row = {}
        for index, columns in enumerate(columns_label[1:]):
            row[self.columns[index+1]] = columns[key].text()
            
        return row
    
    def get_rows_changed(self):
        return [self.get_rows(key) for key in self.changed_rows]
    
    def resizeEvent(self, e: QResizeEvent = None) -> None:
        if e:
            super().resizeEvent(e)
        
        for column in self.columns_label:
            MAX = max([cell.sizeHint().width() for cell in column])
            
            for cell in column: cell.setFixedWidth(MAX)
