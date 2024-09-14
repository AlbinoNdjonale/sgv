import mysql.connector as mysql
import os
import sqlite3

class ErrorToConnect(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class Table:
    def __init__(self, name: str | tuple, qbuilder):
        self.__table_name = name
        self.qbuilder: QBuilder = qbuilder
        
        if isinstance(name, str):
            self.attrs = self.qbuilder.tables[name]
        else:
            self.attrs = []
            for table_name in name:
                attrs = self.qbuilder.tables[table_name]
                self.attrs.extend([f"{table_name}.{attr}" for attr in attrs])
     
    def __set_key(self, values) -> list[dict[str]]:
        res = []
        
        for value in values:
            item = {}
            for key, attr in enumerate(self.attrs):
                item[attr.replace(".", "_")] = (
                    value[key]
                    if isinstance(value[key], int | str)
                    else str(value[key])
                )
            res.append(item)
        
        return res
    
    def build_cond(self, filter: dict[str, dict]):
        sqls = []
        
        for attr in filter:
            if attr[0] == "$":
                sqls.append(f" {attr[1:]} ".join(
                    [f"({self.build_cond(cond)})" for cond in filter[attr]]
                ))
            else:
                if (value := filter[attr].get("eq")) is not None:
                    sqls.append(f"{attr} = {value}")
                elif (value := filter[attr].get("lt")) is not None:
                    sqls.append(f"{attr} < {value}")
                elif (value := filter[attr].get("gt")) is not None:
                    sqls.append(f"{attr} > {value}")
                elif (value := filter[attr].get("le")) is not None:
                    sqls.append(f"{attr} <= {value}")
                elif (value := filter[attr].get("ge")) is not None:
                    sqls.append(f"{attr} >= {value}")
                elif (value := filter[attr].get("like")) is not None:
                    sqls.append(f"{attr} like {value}")
                else:
                    raise TypeError("Operação invalida.")
            
        return sqls[0]
    
    def __builder_slice(self, slice: str, filter: dict):
        return f" {slice} {self.build_cond(filter)}" 
        
    @property
    def table_name(self) -> str:
        if isinstance(self.__table_name, str):
            return self.__table_name
        
        return " JOIN ".join(self.__table_name)
    
    def delete(
        self,
        where: dict[str] = None,
        on: dict[str] = None
    ):
        conn = self.qbuilder.connect()
        cursor = conn.cursor()
        
        _where = self.__builder_slice("WHERE", where) if where else ""
        _on    = self.__builder_slice("ON", on) if on else ""
        
        sql = (
            f"DELETE FROM {self.table_name}"
            f"{_on}{_where};"
        )
        
        cursor.execute(sql)
        
        conn.commit()
        conn.close()
        
        return self.all(where = where)
    
    def update(
        self,
        value: dict[str],
        where: dict[str] = None,
        on: dict[str] = None
    ):
        if isinstance(value, list):
            return [self.update(v) for v in value]
        
        conn = self.qbuilder.connect()
        cursor = conn.cursor()
        
        _where = self.__builder_slice("WHERE", where) if where else ""
        _on    = self.__builder_slice("ON", on) if  on else ""
        
        attrs_update = ", ".join(
            [f"{key} = '{v}'" for key, v in value.items()]
        )
        
        sql = (
            f"UPDATE {self.table_name} SET {attrs_update}"
            f"{_on}{_where};"
        )
        cursor.execute(sql)
        
        conn.commit()
        conn.close()
        
        return self.all(where = where)
    
    def insert(self, value: dict[str] | list[dict[str]]):
        if isinstance(value, list):
            return [self.insert(v) for v in value]
        
        conn = self.qbuilder.connect()
        cursor = conn.cursor()
        
        keys   = ",".join(value.keys())
        values = ",".join([f"'{v}'" for v in value.values()])
        
        sql = f"INSERT INTO {self.table_name} ({keys}) VALUES ({values});"
        cursor.execute(sql)
        
        sql = f"SELECT MAX(id),{','.join(self.attrs)} FROM {self.table_name};"
        cursor.execute(sql)
        
        res = list(cursor.fetchone())
        del res[0]
        res = self.__set_key([res])[0]
        
        conn.commit()
        conn.close()
        
        return res
        
    def all(
        self,
        order_by: str = None,
        where: dict[str] = None,
        on: dict[str] = None
    ) -> list[dict[str]]:
        
        if order_by:
            if order_by[0] == "-":
                order_by = order_by[1:]+" DESC"
                
        conn = self.qbuilder.connect()
        cursor = conn.cursor()
        
        _where = self.__builder_slice("WHERE", where) if where else ""
        _on    = self.__builder_slice("ON", on) if on else ""
    
        sql = (
            f"SELECT {','.join(self.attrs)} FROM {self.table_name}"
            f"{_on}{_where}"
            f"{(' order by '+order_by) if order_by else ''};"
        )
        
        cursor.execute(sql)
        
        res = self.__set_key(cursor.fetchall())
        
        conn.close()
        
        return res
    
    def get(self, where: dict[str], on: dict[str] = None):
        conn = self.qbuilder.connect()
        cursor = conn.cursor()
        
        _where = self.__builder_slice("WHERE", where) if where else ""
        _on    = self.__builder_slice("ON", on) if on else ""
        
        sql = (
            f"SELECT {','.join(self.attrs)} FROM {self.table_name}"
            f"{_on}{_where};"
        )
        
        cursor.execute(sql)
        
        res = self.__set_key(cursor.fetchmany())
        
        conn.close()
        
        if not res: return None
        
        return res[0]

class QBuilder:
    def __init__(
        self,
        db_type: str,
        tables: dict[str, list[str]],
        db: str,
        host: str = None,
        user: str = None,
        password: str = None
    ):
        if (not os.path.exists(db)) and db_type == "sqlite":
            raise ErrorToConnect("Base de Dados não encotrada.")
        elif db_type == "mysql":
            try:
                mysql.connect(
                    host     = host,
                    database = db,
                    user     = user,
                    password = password
                )
            except mysql.errors.DatabaseError:
                raise ErrorToConnect(
                    "Não foi possivel estabelecer uma "
                    "conexão com a base de dados."
                )
        
        self.db_type  = db_type
        self.database = db
        self.host     = host
        self.user     = user
        self.password = password
        
        self.tables = tables
        
    def connect(self):
        if self.db_type == "sqlite":
            return sqlite3.connect(self.database)
        elif self.db_type == "mysql":
            return mysql.connect(
                host     = self.host,
                database = self.database,
                user     = self.user,
                password = self.password
            )
    
    def __getitem__(self, key: str | tuple) -> Table:
        return Table(key, self)
