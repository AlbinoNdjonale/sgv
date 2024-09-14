import sys
sys.path.append("..")

from sgv import cript

try:
    mode = sys.argv[1]
    
    assert mode == "e" or mode == "d"
    
    if mode == "e": print(f'"{cript.encriptar(sys.argv[2])}"')
    else: print(f'"{cript.desencriptar(sys.argv[2])}"')
    
    sys.exit(0)
except IndexError:
    print("Informe todos os parametros")
except AssertionError:
    print("modo invalido por favor inseri um entre (e, d)")
sys.exit(1)