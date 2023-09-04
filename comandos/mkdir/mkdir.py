import os
import math
import time
import ctypes

import structs
from _global._global import particiones_montadas, session_inciada
from comandos.mount.mount import find_mounted
from comandos.mkfs.mkfs import join_file, find_file, file_link, write_carpeta, find_carpeta
from comandos.fdisk.fdisk import exist_partition


class mkdir():
    def __init__(self):
        self.path = ""
        self.recursivo = False

    def crear_mkdir(self):
        print("mkdir")

        file = open(session_inciada.mounted.path, "rb+")
        sblock = structs.SuperBloque()
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()

        if sblock.s_first_ino == -1:
            # No hay más inodos disponibles, error
            return
        elif sblock.s_first_blo == -1:
            # No hay más bloques disponibles, error
            return

        inodo_carpeta = structs.Inodo()
        inodo_carpeta.i_uid = 1
        inodo_carpeta.i_gid = 1
        inodo_carpeta.i_s = 0
        inodo_carpeta.i_atime = int(time.time())
        inodo_carpeta.i_ctime = int(time.time())
        inodo_carpeta.i_mtime = int(time.time())
        inodo_carpeta.i_type = b'0'
        inodo_carpeta.i_perm = 664 # 0o664

        # Ahora creamos nuestro bloque de carpeta para crear la carpeta root
        carpeta_root = structs.BloqueCarpeta()
        carpeta_root.b_content[0].b_name = ".".encode('utf-8')[:12].ljust(12, b'\0')
        carpeta_root.b_content[0].b_inodo = 0
        carpeta_root.b_content[1].b_name = "..".encode('utf-8')[:12].ljust(12, b'\0')
        carpeta_root.b_content[1].b_inodo = 0

        directorio, carpeta_crear = os.path.split(self.path)
        indo_carpeta, i = find_carpeta(sblock, directorio, session_inciada)
        file_link(sblock, self.path, session_inciada, indo_carpeta, i)
        file = open(session_inciada.mounted.path, "rb+")
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()
        inodo_carpeta.i_block[0] = sblock.s_first_blo
        write_carpeta(sblock, inodo_carpeta, carpeta_root, session_inciada)

        print("Carpeta creada con exito")