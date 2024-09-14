"""
Teste
======

Use este modulo para criar testes em seus projectos e 
com isso aumentar a sua produtividade

Exemplo:

>>> from Teste import Teste
>>> import appAserTestatado
>>>
>>> class GroupTesteName(Teste):
>>>     def __init__(self):
>>>         super(GroupTesteName, self).__init__(__file__, "Descrição dos Testes")
>>>
>>>         self.addDirWtch(".", recursive = True, ignore = [
>>>             "./Teste",
>>>             "*/__pycache__"
>>>         ])
>>>
>>>         self.addTeste("TesteName", appAserTestatado.FuncaoTestada, {"v": 5}, 15)
>>>
>>> TesteOla().run()
"""

import sys
import os
import typing
from . import __typing as tp
import platform

class Teste:
    __fileswatch : list[dict]         = []
    __tests      : list[tp.testeType] = []
    __maxnametest: int                = 0
    __asserts    : dict               = {
        "equal": {
            "assert": lambda es, rt: es == rt,
            "msg"   : lambda es, rt: f"""\n    Resultado do Teste: {rt}\n    Resultado Esperado: {es}"""
        },

        "notequal": {
            "assert": lambda es, rt: not (es == rt),
            "msg"   : lambda es, rt: f"""\n    Resultado do Teste:     {rt}\n    Resultado Não Esperado: {es}"""
        },

        "in": {
            "assert": lambda es, rt: es in rt,
            "msg"   : lambda es, rt: f"""\n    Resultado do Teste:   {rt}\n    Resultados Esperados: {es}"""
        },

        "notin": {
            "assert": lambda es, rt: not (es in rt),
            "msg"   : lambda es, rt: f"""\n    Resultado do Teste:       {rt}\n    Resultados Não Esperados: {es}"""
        }
    }
 
    def __init__(self, file: str, name: str):
        """
        Inicializa a istância de teste você deve passar
        dois parametros obrigatório
        
        1 - file: Este parametro será sempre o caminho absoluto
        que a ponta para o arquivo que é interpretado,
        este valor é armazenado automaticamente na variavel
        `__file__`
        
        2 - name: Este parametro é uma descrição dos testes
        
        Exemplo:
        
        >>> self.__init__(__file__, "Testando a função de calculo de fatórial")
        """

        self.File = file
        self.name = name
    
    def run(self):
        """
        Run the Tests
        """

        reload = False
        if len(sys.argv) == 2 and sys.argv[1] == "--reload":
            reload = True
            del sys.argv[1]

        if reload or len(sys.argv) == 2:
            os.system("cls" if platform.system() == "Windows" else "clear")

        self.all(reload)
        
        if reload:
            c = 2
            
            try:
                while True:
                    index = 0
                    for filewatch in self.__fileswatch:
                        file = open(filewatch["path"], "rb")

                        context = file.read()
                        file.close()
                        if not filewatch["context"] == context:
                            os.system(f"python {self.File} {c}")
                            c += 1
                            file = open(filewatch["path"], "rb")
                            self.__fileswatch[index]["context"] = file.read()
                            file.close()
                            break
                        index += 1
            except:
                print("Terminado")
            
    def add_teste(
        self,
        name: str,
        test: typing.Callable,
        params: dict[str] | list = None,
        res: typing.Any = None,
        _assert: tp.Asserts = "equal") -> None:
        """Add a Test
        
        Keyword arguments:
        name -- The name or description of Test
        test -- A function

        Return: return_description
        """
        
        
        self.__tests.append({
            "nome"      : name,
            "teste"     : test,
            "parametros": params,
            "res"       : res,
            "_assert"   :_assert
        })
        
        if len(name) > self.__maxnametest: self.__maxnametest = len(name)
        
    def to_test(self, test):        
        try:
            if test["parametros"] is None: res = test["teste"]()
            elif type(test["parametros"]) == dict: res = test["teste"](**test["parametros"])
            else: res = test["teste"](*test["parametros"])

            return self.__asserts[test["_assert"]]["assert"](res, test["res"]), res
        except Exception as error:
            return None, error
        
    def __dir_or_file(self, contexts: list[str], path: str, ignore: list[str] = []):
        dirs, files = [], []
        for context in contexts:
            if self._in(path+"/"+context, ignore): continue
            try:
                _ = open(path+"/"+context)
                files.append(path+"/"+context)
            except:
                dirs.append(path+"/"+context)
        return dirs, files
        
    def add_dir_watch(self, path: str, recursive: bool = False, ignore: list[str] = []) -> None:
        """Add a directori for watch
        
        Keyword arguments:
        path -- The Path of directori
        recursive -- if is `True` all directori in the main directori
        """
        
        dirs, files = self.__dir_or_file(os.listdir(path), path, ignore)
         
        self.add_files_watch(files)
        if recursive:
            for dir in dirs:
                self.add_dir_watch(dir, True, ignore)
                
    def add_file_watch(self, path: str) -> None:
        """Add a file for watch
        
        Keyword arguments:
        path -- The path of file
        """
        
        file = open(path, "rb")

        self.__fileswatch.append(
            {"context": file.read(), "path": path}
        )
        file.close()
    
    def add_files_watch(self, paths: list[str]) -> None:
        """Add Files for Watch
        
        Keyword arguments:
        paths -- A list of path of files
        """
        
        for file in paths:
            self.add_file_watch(file)
        
    def _in(self, path: str, ignore: list[str]):
        for dirOrFile in ignore:
            indexs = []
            
            for part in dirOrFile.split("*"):
                if part == "": continue
                tmp = self.indexs(path, part)
                if len(tmp) > 0:
                    indexs.extend(tmp)
            
            if len(indexs) > 0:
                indexs = sorted(indexs, key = lambda item: item[0])
                newpath = "*".join([path[pos[0]:pos[1]] for pos in indexs])
                if not indexs[0][0] == 0: newpath = "*"+newpath
                if not indexs[-1][1] == len(path): newpath += "*"
                path = newpath
        
        return path in ignore
    
    def indexs(self, word: str, point: str) -> list[int]:
        start = 0
        end = len(word)
        res = []
        while True:
            tmp = word.find(point, start, end)
            if not tmp == -1:
                res.append((tmp, tmp+len(point)))
                start = tmp + len(point)
            else: break
            if start >= end: break
        return res
        
    def all(self, reload: bool):
        errors = diferents = oks = 0
        print(f"{self.name} {'-'*40} {1 if len(sys.argv) == 1 else sys.argv[1]}\n")
        for test in self.__tests:
            TEST = self.to_test(test)
            if TEST[0] is None:
                errors += 1
                print(f"{test['nome']} {'-'*(self.__maxnametest-len(test['nome']))}{'-'*25} \033[31mERRO:")
                print(f"\n    {TEST}")
            elif TEST[0]:
                oks += 1
                print(f"{test['nome']} {'-'*(self.__maxnametest-len(test['nome']))}{'-'*25} \033[32mOK:")
                print(f"\n Resultado: {TEST[1]}")
            elif not TEST[0]:
                diferents += 1
                print(f"{test['nome']} {'-'*(self.__maxnametest-len(test['nome']))}{'-'*25} \033[33mNÃO ESPERADO:")
                print(self.__asserts[test["_assert"]]["msg"](test["res"], TEST[1]))
            print(f"\n    PARAMETROS:")
            if test["parametros"] is not None:
                if type(test["parametros"]) == dict:
                    for key, value in test["parametros"].items(): print(f"{' '*8}{key} = {value}")
                else:
                    for value in test["parametros"]: print(f"{' '*8}{value}")
            else: print(f"{' '*8}None")
            print("\033[m")
        print(f"Números de testes realizados: {len(self.__tests)}")
        print(f"(susseful: {oks}, different: {diferents}, error: {errors})")

        if (not reload) and (not oks == len(self.__tests)): sys.exit(1)