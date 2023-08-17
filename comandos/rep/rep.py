import struct
from datetime import datetime

import structs
class rep:
    def __init__(self):
        self.path = ''  # string

    def crear_rep(self, rep):
        try:
            with open(rep.path, "rb") as file:
                datos_mbr = file.read(struct.calcsize(structs.size_mbr()))
                tam, fecha, sig = structs.deserializar_mbr(datos_mbr)
                fecha_hora = datetime.fromtimestamp(fecha)

                fecha_formateada = fecha_hora.strftime("%d-%m-%Y %H:%M:%S")
                print(" ----- DATOS DEL MBR ----- ")
                print(f"Tamaño del disco: {tam} bytes")
                print(f"Fecha de creacion del disco: {fecha_formateada}")
                print(f"Signature: {sig}")
        except FileNotFoundError:
            print(f"No existe el disco con ruta {rep.path}")