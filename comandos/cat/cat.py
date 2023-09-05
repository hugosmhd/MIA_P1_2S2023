import os
import math
import time
import ctypes

import structs
from _global._global import particiones_montadas, session_inciada
from comandos.mount.mount import find_mounted
from comandos.mkfs.mkfs import join_file, find_file, file_link, write_file, find_carpeta_archivo
from comandos.fdisk.fdisk import exist_partition

class cat():
    def __init__(self):
        self.files = []

    def crear_cat(self):
        # print("Crear cat")
        # print(self.files)

        file = open(session_inciada.mounted.path, "rb+")
        sblock = structs.SuperBloque()
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()

        for archivo in self.files:
            directorio, archivo_ = os.path.split(archivo)
            indo_carpeta_archivo, i, _, __ = find_carpeta_archivo(sblock, directorio, session_inciada)
            inodo_archivo, i_f = find_file(sblock, archivo, session_inciada.mounted.path, indo_carpeta_archivo)
            txt = join_file(sblock, inodo_archivo, session_inciada.mounted.path)
            print("JOIN FILE MKFILE CAT")
            print(txt)
