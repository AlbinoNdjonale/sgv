import random

ALPHA = []

S = "abcdefghijklmnopqrstuvwyz"
ALPHA.extend(S)
ALPHA.extend(S.upper())
ALPHA.extend("".join([str(i) for i in range(10)]))
ALPHA.extend(",.\"':;^~|\\/!@£§€{}[]")
ALPHA.extend("#$%&()*-+=«?-_ ")

random.seed(1)
RALPHA = sorted(ALPHA, key = lambda x: random.randint(0, len(ALPHA)))

def criptografia(value: dict[str] | list | tuple | str, enc: bool):
    if type(value) == str:
        To   = ALPHA if enc else RALPHA
        From = RALPHA if enc else ALPHA
        
        res = ""
        for i in value:
            indice = None if not i in To else To.index(i)
            res += i if indice is None else From[indice]
        return res
    
    if type(value) == list or type(value) == tuple:
        return [criptografia(i, enc) for i in value]
    
    if type(value) == dict:
        res: dict[str] = {}
        for key, Value in value.items():
            res[key] = criptografia(Value, enc)
            
        return res
    
def encriptar(value: dict | list | tuple | str): return criptografia(value, True)
def desencriptar(value: dict | list | tuple | str): return criptografia(value, False)
