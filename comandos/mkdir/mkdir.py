import os
import math
import time
import ctypes

import structs
from _global._global import particiones_montadas, session_inciada, comando_actual
from comandos.mount.mount import find_mounted
from comandos.mkfs.mkfs import join_file, find_file, file_link, write_carpeta, find_carpeta, directory_link_r, find_carpeta_archivo
from comandos.fdisk.fdisk import exist_partition


def crear_mkdir_r(path, indo_carpeta, i):

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

        # directorio, carpeta_crear = os.path.split(path)
        # indo_carpeta, i = find_carpeta(sblock, directorio, session_inciada)
        directory_link_r(sblock, path, session_inciada, indo_carpeta, i)
        file = open(session_inciada.mounted.path, "rb+")
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()
        inodo_carpeta.i_block[0] = sblock.s_first_blo
        i_c = sblock.s_first_ino
        write_carpeta(sblock, inodo_carpeta, carpeta_root, session_inciada)

        return inodo_carpeta, i_c

class mkdir():
    def __init__(self):
        self.path = ""
        self.recursivo = False

    def crear_mkdir(self):

        if self.recursivo:
            directorio, archivo_ = os.path.split(self.path)
            file = open(session_inciada.mounted.path, "rb+")
            sblock = structs.SuperBloque()
            file.seek(session_inciada.mounted.part_start)
            file.readinto(sblock)
            file.close()
            indo_carpeta_archivo, i_c, encontrada, carpetas = find_carpeta_archivo(sblock, directorio, session_inciada, True)
            if not encontrada:
                for i, carpeta in enumerate(carpetas):
                    indo_carpeta_archivo, i_c = crear_mkdir_r(carpeta, indo_carpeta_archivo, i_c)

        file = open(session_inciada.mounted.path, "rb+")
        sblock = structs.SuperBloque()
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()

        directorio, carpeta_crear = os.path.split(self.path)
        indo_carpeta, i = find_carpeta(sblock, directorio, session_inciada)
        if(i == -1):
            print(f"Error: Ruta especificada '{directorio}' no existe")
            return
        inodo_archivo, i_f = find_file(sblock, carpeta_crear, session_inciada.mounted.path, indo_carpeta, False)
        if(i_f != -1):
            print(f"Error: Carpeta '{self.path}' ya existe")
            return

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

        
        file_link(sblock, self.path, session_inciada, indo_carpeta, i)
        file = open(session_inciada.mounted.path, "rb+")
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()
        inodo_carpeta.i_block[0] = sblock.s_first_blo
        write_carpeta(sblock, inodo_carpeta, carpeta_root, session_inciada)

        print("Carpeta creada con exito")
        if sblock.s_filesystem_type == 3:
            print("entra a la escritura del journaling")
            global comando_actual
            print(comando_actual)
            file = open(session_inciada.mounted.path, "rb+")
            journaling_actual = structs.Journaling()
            read_journaling = session_inciada.mounted.part_start + ctypes.sizeof(structs.SuperBloque)
            for _ in range(sblock.s_inodes_count):
                file.seek(read_journaling)
                file.readinto(journaling_actual)

                if(journaling_actual.fecha == 0):
                    journaling_actual.comando = comando_actual[0].encode('utf-8')[:100].ljust(100, b'\0')
                    journaling_actual.fecha = int(time.time())
                    print("Se escribe el journaling en mkfile")
                    print(journaling_actual.comando)
                    print(journaling_actual.fecha)
                    file.seek(read_journaling)
                    file.write(ctypes.string_at(ctypes.byref(journaling_actual), ctypes.sizeof(journaling_actual)))
                    break

                read_journaling += ctypes.sizeof(structs.Journaling)
            file.close()