import os
import math
import time
import ctypes

import structs
from _global._global import particiones_montadas, session_inciada, comando_actual
from comandos.mount.mount import find_mounted
from comandos.mkfs.mkfs import find_url, find_file, file_link, write_file, find_carpeta_archivo
from comandos.fdisk.fdisk import exist_partition


class rename():
    def __init__(self):
        self.path = ""
        self.name = ""

    def crear_rename(self):

        if self.path == "" or self.name == "":
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

        bloque_carpeta, i, write_block = find_url(sblock, self.path, session_inciada)
        if write_block == -1:
            print(f"Error: Ruta {self.path} no encontrada")
            return

        directorio, archivo_ = os.path.split(self.path)
        # Se verifica que no exista un archivo con el mismo nombre
        indo_carpeta_archivo, i, _, __ = find_carpeta_archivo(sblock, directorio, session_inciada)
        if(i == -1):
            print(f"Error: Ruta especificada '{directorio}' no existe")
            return
        inodo_archivo, i_f = find_file(sblock, self.name, session_inciada.mounted.path, indo_carpeta_archivo, False)
        if(i_f != -1):
            print(f"Error: Archivo/Carpeta ya existe con el nombre {self.nombre}")
            return

        
        inodo_actual = structs.Inodo()
        file = open(session_inciada.mounted.path, "rb+")
        read_on_i = sblock.s_inode_start + (ctypes.sizeof(structs.Inodo) * bloque_carpeta.b_content[i].b_inodo)
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
            print(f"No tienes permisos de escritura sobre la carpeta {self.path}")
            return

        bloque_carpeta.b_content[i].b_name = self.name.encode('utf-8')[:12].ljust(12, b'\0')
        file = open(session_inciada.mounted.path, "rb+")
        file.seek(write_block)
        file.write(ctypes.string_at(ctypes.byref(bloque_carpeta), ctypes.sizeof(bloque_carpeta)))
        file.close()

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