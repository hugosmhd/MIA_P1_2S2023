import time
import random
import ctypes
import os
import struct
from datetime import datetime

import structs

class mkdisk:
    def __init__(self):
        self.size = 0   # int
        self.path = ''  # string
        self.name = ''  # string
        self.fit = 'FF'   # char
        self.unit = 'M'  # char

    def crear_mkdisk(self, disco):

        if self.size == 0 or self.path == '':
            print("Error: Verifique su entrada faltan parametros obligatorios")
            return

        directorio, archivo = os.path.split(disco.path)
        
        if not os.path.exists(directorio):
            os.makedirs(directorio)

        elif os.path.isfile(self.path):
            print(f"El disco {self.path} ya existe")
            return

        file = open(self.path, "wb")
        tam_disco = 0
        ceros = b"\0" * 1024

        if disco.unit.upper() == "K":
            for i in range(disco.size):
                file.write(ceros)
            tam_disco = 1024 * disco.size
        elif disco.unit.upper() == "M" or disco.unit == "":
            for i in range(1024 * disco.size):
                file.write(ceros)
            tam_disco = 1024 * 1024 * disco.size
        
        disco_mbr = structs.MBR()
        disco_mbr.set_mbr_tamano(tam_disco)
        disco_mbr.set_mbr_fecha_creacion(int(time.time()))
        disco_mbr.set_mbr_dsk_signature(random.randint(0, 2147483647))
        if disco.fit == "FF":
            disco_mbr.set_dsk_fit('F')
        elif disco.fit == "WF":
            disco_mbr.set_dsk_fit('W')
        elif disco.fit == "BF":
            disco_mbr.set_dsk_fit('B')
        particiones_iniciales = [
            structs.Partition(),
            structs.Partition(),
            structs.Partition(),
            structs.Partition()
        ]
        for i, particion in enumerate(particiones_iniciales):
            disco_mbr.mbr_partitions[i] = particion

        file.seek(0)
        file.write(ctypes.string_at(ctypes.byref(disco_mbr), ctypes.sizeof(disco_mbr)))

        print(f"Disco \"{disco.path}\" creado correctamente")
        file.close()

    def crear_rmdisk(self):

        if self.path == '':
            print("Error: Verifique su entrada faltan parametros obligatorios")
            return

        directorio, archivo = os.path.split(self.path)
        
        answer = input("¿Está seguro de eliminar el disco? S/N: ")
        answer = answer.upper()

        if answer == "S":
            # Reemplaza 'disco->path' con la ruta real del disco
            try:
                os.remove(self.path)
                print("Disco eliminado correctamente")
            except FileNotFoundError:
                print("El disco no existe.")
            except Exception as e:
                print(f"Error al eliminar el disco: {e}")
        else:
            print("Operación cancelada con éxito.")
