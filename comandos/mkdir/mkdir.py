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
        inodo_carpeta.i_uid = session_inciada.credenciales.id
        inodo_carpeta.i_gid = session_inciada.credenciales.group_id
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

        if self.path == "":
            print("Error: Verifique su entrada faltan parametros obligatorios")
            return

        if not session_inciada.is_logged:
            print("Error: No se ha iniciado ninguna sesion")
            return

        if self.recursivo:
            directorio, archivo_ = os.path.split(self.path)
            file = open(session_inciada.mounted.path, "rb+")
            sblock = structs.SuperBloque()
            file.seek(session_inciada.mounted.part_start)
            file.readinto(sblock)
            file.close()
            indo_carpeta_archivo, i_c, encontrada, carpetas = find_carpeta_archivo(sblock, directorio, session_inciada, True)
            
            inodo_actual = structs.Inodo()
            file = open(session_inciada.mounted.path, "rb+")
            read_on_i = sblock.s_inode_start + (ctypes.sizeof(structs.Inodo) * i_c)
            file.seek(read_on_i)
            file.readinto(inodo_actual)
            file.close()

            permisos_u = (inodo_actual.i_perm // 100) % 10  # El primer dígito
            permisos_g = (inodo_actual.i_perm // 10) % 10   # El segundo dígito
            permisos_o = inodo_actual.i_perm % 10            # El tercer dígito
            permisos = False

            if session_inciada.credenciales.id == inodo_actual.i_uid:
                # Permisos de escritura
                if permisos_u == 2 or permisos_u == 3 or permisos_u == 6 or permisos_u == 7:
                    permisos = True
            elif session_inciada.credenciales.group_id == inodo_actual.i_gid:
                # Permisos de escritura
                if permisos_g == 2 or permisos_g == 3 or permisos_g == 6 or permisos_g == 7:
                    permisos = True
            else:
                # Permisos de escritura
                if permisos_o == 2 or permisos_o == 3 or permisos_o == 6 or permisos_o == 7:
                    permisos = True
            
            if not permisos and not session_inciada.is_recovery and session_inciada.credenciales.user != 'root':
                print(f"Error: Problemas de permisos para crear el directorio {self.path}")
                return

            if not encontrada:
                for i, carpeta in enumerate(carpetas):
                    indo_carpeta_archivo, i_c = crear_mkdir_r(carpeta, indo_carpeta_archivo, i_c)

        file = open(session_inciada.mounted.path, "rb+")
        sblock = structs.SuperBloque()
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()

        directorio, carpeta_crear = os.path.split(self.path)
        indo_carpeta, i = find_carpeta(sblock, directorio, session_inciada.mounted.path)
        if(i == -1):
            print(f"Error: Ruta especificada '{directorio}' no existe")
            return
        inodo_archivo, i_f = find_file(sblock, carpeta_crear, session_inciada.mounted.path, indo_carpeta, False)
        if(i_f != -1):
            print(f"Error: Carpeta '{self.path}' ya existe")
            return

        permisos_u = (indo_carpeta.i_perm // 100) % 10  # El primer dígito
        permisos_g = (indo_carpeta.i_perm // 10) % 10   # El segundo dígito
        permisos_o = indo_carpeta.i_perm % 10            # El tercer dígito
        permisos = False
        if session_inciada.credenciales.id == indo_carpeta.i_uid:
            # Permisos de escritura
            if permisos_u == 2 or permisos_u == 3 or permisos_u == 6 or permisos_u == 7:
                permisos = True
        elif session_inciada.credenciales.group_id == indo_carpeta.i_gid:
            # Permisos de escritura
            if permisos_g == 2 or permisos_g == 3 or permisos_g == 6 or permisos_g == 7:
                permisos = True
        else:
            # Permisos de escritura
            if permisos_o == 2 or permisos_o == 3 or permisos_o == 6 or permisos_o == 7:
                permisos = True
        
        if not permisos and not session_inciada.is_recovery and session_inciada.credenciales.user != 'root':
            print(f"No tienes permisos de escritura sobre la carpeta {self.path}")
            return

        if sblock.s_first_ino == -1:
            # No hay más inodos disponibles, error
            return
        elif sblock.s_first_blo == -1:
            # No hay más bloques disponibles, error
            return

        inodo_carpeta = structs.Inodo()
        inodo_carpeta.i_uid = session_inciada.credenciales.id
        inodo_carpeta.i_gid = session_inciada.credenciales.group_id
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