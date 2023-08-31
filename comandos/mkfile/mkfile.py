import os
import math
import time
import ctypes

import structs
from _global._global import particiones_montadas, session_inciada
from comandos.mount.mount import find_mounted
from comandos.mkfs.mkfs import join_file, find_file, file_link, write_file, find_carpeta_archivo
from comandos.fdisk.fdisk import exist_partition


class mkfile():
    def __init__(self):
        self.path = ""
        self.recursivo = False
        self.size = 0
        self.cout = ""

    def crear_mkfile(self):
        print("mkfile")
        print(self.size)
        num = '0'
        numbers = "0123456789"
        content = ""
        iterations_fill = self.size // 10
        for _ in range(iterations_fill):
            content += numbers

        iterations_fill = self.size % 10
        for _ in range(iterations_fill):
            content += num
            if num == '9':
                num = '0'
                continue
            num = chr(ord(num) + 1)

        # print(content)

        file = open(session_inciada.mounted.path, "rb+")
        sblock = structs.SuperBloque()
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()

        if sblock.s_first_ino == -1:
            # No hay más inodos disponibles, error
            return
        elif sblock.s_first_blo == -1 and size > 0:
            # No hay más bloques disponibles, error
            return

        inodo_file = structs.Inodo()
        inodo_file.i_uid = 1
        inodo_file.i_gid = 1
        inodo_file.i_s = self.size
        inodo_file.i_atime = int(time.time())
        inodo_file.i_ctime = int(time.time())
        inodo_file.i_mtime = int(time.time())
        inodo_file.i_type = b'1'
        inodo_file.i_perm = 0o664

        indo_carpeta_archivo = find_carpeta_archivo(sblock, self.path, session_inciada)
        file_link(sblock, self.path, session_inciada, indo_carpeta_archivo)
        file = open(session_inciada.mounted.path, "rb+")
        sblock = structs.SuperBloque()
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()
        write_file(sblock, inodo_file, content, session_inciada)
        # print(self.path)
        inodo_archivo = find_file(sblock, self.path, session_inciada.mounted.path, indo_carpeta_archivo)
        # print(inodo_archivo.i_s)
        txt = join_file(sblock, inodo_archivo, session_inciada.mounted.path)
        print("JOIN FILE MKFILE")
        print(txt)

