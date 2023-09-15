import ctypes

import structs
from analizador import analizador

if __name__ == "__main__":
    print("*----------------------------------------------------------*")
    print("*                [MIA] Proyecto 1                          *")
    print("*         Hugo Sebastian Martínez Hernández                *")
    print("*                 Carnet: 202002793                        *")
    print("*----------------------------------------------------------*")
    print()

    repetir = True
    comando = ""
    while repetir:
        comando = input("> ")
        analizador.analizar(comando)
        print()