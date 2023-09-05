import os
import math
import time
import ctypes

import structs
from _global._global import particiones_montadas, session_inciada
from comandos.mount.mount import find_mounted
from comandos.mkfs.mkfs import join_file, find_file, file_link, write_file, find_carpeta_archivo
from comandos.fdisk.fdisk import exist_partition
from comandos.mkdir.mkdir import crear_mkdir_r

class mkfile():
    def __init__(self):
        self.path = ""
        self.recursivo = False
        self.size = 0
        self.size_activo = False
        self.cout = ""

    def crear_mkfile(self):
        print("mkfile")
        print(self.size)

        if not session_inciada.is_logged:
            print("Error: No se ha iniciado ninguna sesion")
            return

        directorio, archivo_ = os.path.split(self.path)
        if self.recursivo:
            file = open(session_inciada.mounted.path, "rb+")
            sblock = structs.SuperBloque()
            file.seek(session_inciada.mounted.part_start)
            file.readinto(sblock)
            file.close()
            indo_carpeta_archivo, i_c, encontrada, carpetas = find_carpeta_archivo(sblock, directorio, session_inciada, True)
            if not encontrada:
                print("carpetas_restantes", carpetas)
                for i, carpeta in enumerate(carpetas):
                    indo_carpeta_archivo, i_c = crear_mkdir_r(carpeta, indo_carpeta_archivo, i_c)


        # -------------------------------------------
        num = '0'
        numbers = "0123456789"
        content = ""
        if self.cout != "":
            try:

                with open(self.cout, 'r') as archivo:
                    content = archivo.read(self.size) if self.size_activo else archivo.read()
            except FileNotFoundError:
                print(f"Error: La ruta de cout {self.cout} no existe")
        else:
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
        sblock = structs.SuperBloque()
        file = open(session_inciada.mounted.path, "rb+")
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()

        directorio, archivo_ = os.path.split(self.path)
        # Se verifica que no exista un archivo con el mismo nombre
        indo_carpeta_archivo, i, _, __ = find_carpeta_archivo(sblock, directorio, session_inciada)
        if(i == -1):
            print(f"Error: Ruta especificada '{directorio}' no existe")
            return
        inodo_archivo, i_f = find_file(sblock, archivo_, session_inciada.mounted.path, indo_carpeta_archivo, False)
        if(i_f != -1):
            print(f"Error: Archivo '{self.path}' ya existe")
            return

        if sblock.s_first_ino == -1:
            # No hay más inodos disponibles, error
            return
        elif sblock.s_first_blo == -1 and size > 0:
            # No hay más bloques disponibles, error
            return

        inodo_file = structs.Inodo()
        inodo_file.i_uid = 1
        inodo_file.i_gid = 1
        inodo_file.i_s = len(content)
        inodo_file.i_atime = int(time.time())
        inodo_file.i_ctime = int(time.time())
        inodo_file.i_mtime = int(time.time())
        inodo_file.i_type = b'1'
        inodo_file.i_perm = 664 # 0o664

        file_link(sblock, self.path, session_inciada, indo_carpeta_archivo, i)
        file = open(session_inciada.mounted.path, "rb+")
        
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()
        write_file(sblock, inodo_file, content, session_inciada)
        # print(self.path)
        inodo_archivo, i_f = find_file(sblock, self.path, session_inciada.mounted.path, indo_carpeta_archivo)
        if(i_f == -1):
            print(f"Error: Ruta especificada '{self.path}' no existe")
            return
        # print(inodo_archivo.i_s)
        txt = join_file(sblock, inodo_archivo, session_inciada.mounted.path)
        print("JOIN FILE MKFILE")
        print(txt)

