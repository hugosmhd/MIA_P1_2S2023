import os
import math
import time
import ctypes
import pyperclip

import structs
from _global._global import particiones_montadas, session_inciada, comando_actual
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
        inodo_archivo, i_f = find_file(sblock, self.path, session_inciada.mounted.path, indo_carpeta_archivo)
        if(i_f == -1):
            print(f"Error: Ruta especificada '{self.path}' no existe")
            return
        # print(inodo_archivo.i_s)
        txt = join_file(sblock, inodo_archivo, session_inciada.mounted.path)
        # pyperclip.copy(txt)

        if sblock.s_filesystem_type == 3:
            global comando_actual
            file = open(session_inciada.mounted.path, "rb+")
            journaling_actual = structs.Journaling()
            read_journaling = session_inciada.mounted.part_start + ctypes.sizeof(structs.SuperBloque)
            for _ in range(sblock.s_inodes_count):
                file.seek(read_journaling)
                file.readinto(journaling_actual)

                if(journaling_actual.fecha == 0):
                    journaling_actual.comando = comando_actual[0].encode('utf-8')[:100].ljust(100, b'\0')
                    journaling_actual.fecha = int(time.time())
                    file.seek(read_journaling)
                    file.write(ctypes.string_at(ctypes.byref(journaling_actual), ctypes.sizeof(journaling_actual)))
                    break

                read_journaling += ctypes.sizeof(structs.Journaling)
            file.close()

    def file_contenido(self):
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
        return content
