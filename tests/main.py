from HotTest import Teste
import sys

sys.path.append("..")

from sgv import(
    cript,
    formatnumber
)

class TestSgv(Teste):
    def __init__(self):
        super(TestSgv, self).__init__(__file__, "Testando o SGV")
        
        self.add_files_watch([
            __file__,
            "../sgv/cript.py",
            "../sgv/formatnumber.py"
        ])
        
        self.add_teste(
            "Teste Encripta",
            cript.encriptar,
            ["Albino Ndjonale"],
            "wlG{z ](0c zrln"
        )
        
        self.add_teste(
            "Teste Decripta",
            cript.desencriptar,
            ["wlG{z ](0c zrln"],
            "Albino Ndjonale"
        )
        
        self.add_teste(
            "Teste Format Number",
            formatnumber.format_number,
            [1000],
            "1 000.00 KZ"
        )
        
        self.add_teste(
            "Teste Format Number com moeda",
            formatnumber.format_number,
            [1000, "00 US"],
            "1 000.00 US"
        )
        
TestSgv().run()