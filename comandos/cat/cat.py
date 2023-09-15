import os
import math
import time
import ctypes
# import pyperclip

import structs
from _global._global import particiones_montadas, session_inciada
from comandos.mount.mount import find_mounted
from comandos.mkfs.mkfs import join_file, find_file, file_link, write_file, find_carpeta_archivo
from comandos.fdisk.fdisk import exist_partition

class cat():
    def __init__(self):
        self.files = []

    def crear_cat(self):

        if len(self.files) == 0:
            print("Error: Verifique su entrada faltan parametros obligatorios")
            return
        
        if not session_inciada.is_logged:
            print("Error: No se ha iniciado ninguna sesion")
            return

        file = open(session_inciada.mounted.path, "rb+")
        sblock = structs.SuperBloque()
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()

        for archivo in self.files:
            directorio, archivo_ = os.path.split(archivo)
            indo_carpeta_archivo, i, _, __ = find_carpeta_archivo(sblock, directorio, session_inciada)
            if(i == -1):
                print(f"Error: Ruta especificada '{directorio}' no existe")
                return
            inodo_archivo, i_f = find_file(sblock, archivo, session_inciada.mounted.path, indo_carpeta_archivo)
            if(i_f == -1):
                print(f"Error: Ruta especificada '{archivo}' no existe")
                return

            permisos_u = (inodo_archivo.i_perm // 100) % 10  # El primer dígito
            permisos_g = (inodo_archivo.i_perm // 10) % 10   # El segundo dígito
            permisos_o = inodo_archivo.i_perm % 10            # El tercer dígito
            permisos = False
            if session_inciada.credenciales.id == inodo_archivo.i_uid:
                # Permisos de lectura
                if permisos_u >= 4:
                    permisos = True
            elif session_inciada.credenciales.group_id == inodo_archivo.i_gid:
                # Permisos de lectura
                if permisos_g >= 4:
                    permisos = True
            else:
                # Permisos de lectura
                if permisos_o >= 4:
                    permisos = True
            
            if not permisos and session_inciada.credenciales.user != 'root':
                print(f"No tienes permisos de lectura sobre el archivo {archivo}")
                continue

            txt = join_file(sblock, inodo_archivo, session_inciada.mounted.path)
            print(txt)
            # pyperclip.copy(txt)
