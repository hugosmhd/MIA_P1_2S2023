import os
import math
import time
import ctypes

import structs
from _global._global import particiones_montadas, session_inciada
from comandos.mount.mount import find_mounted
from comandos.mkfs.mkfs import find_url, find_file, file_link, write_file, find_carpeta_archivo
from comandos.fdisk.fdisk import exist_partition


class rename():
    def __init__(self):
        self.path = ""
        self.name = ""

    def crear_rename(self):
        print("rename")
        print(self.path)
        print(self.name)

        file = open(session_inciada.mounted.path, "rb+")
        sblock = structs.SuperBloque()
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()

        bloque_carpeta, i, write_block = find_url(sblock, self.path, session_inciada)
        # print("----- Rename ------")
        # print(i)
        # print(bloque_carpeta.b_content[0].b_name.decode())
        # print(bloque_carpeta.b_content[0].b_inodo)
        # print(bloque_carpeta.b_content[1].b_name.decode())
        # print(bloque_carpeta.b_content[1].b_inodo)
        # print(bloque_carpeta.b_content[2].b_name.decode())
        # print(bloque_carpeta.b_content[2].b_inodo)
        # print(bloque_carpeta.b_content[3].b_name.decode())
        # print(bloque_carpeta.b_content[3].b_inodo)
        bloque_carpeta.b_content[i].b_name = self.name.encode('utf-8')[:12].ljust(12, b'\0')
        file = open(session_inciada.mounted.path, "rb+")
        file.seek(write_block)
        file.write(ctypes.string_at(ctypes.byref(bloque_carpeta), ctypes.sizeof(bloque_carpeta)))
        file.close()
        # print(bloque_carpeta.b_content[2].b_name.decode())
        # print(bloque_carpeta.b_content[2].b_inodo)