import os
import math
import time
import ctypes

import structs
from _global._global import particiones_montadas, session_inciada, comando_actual
from comandos.mount.mount import find_mounted
from comandos.mkfs.mkfs import find_url, find_file, file_link_move, find_carpeta, find_carpeta_archivo
from comandos.fdisk.fdisk import exist_partition


class move():
    def __init__(self):
        self.path = ""
        self.destino = ""

    def crear_move(self):

        if self.path == "" or self.destino == "":
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

        # Encontramos la carpeta destino
        indo_destino, i_d = find_carpeta(sblock, self.destino, session_inciada.mounted.path)
        if(i_d == -1):
            print(f"Error: Ruta destino '{self.destino}' no existe")
            return
        permisos_u = (indo_destino.i_perm // 100) % 10  # El primer dígito
        permisos_g = (indo_destino.i_perm // 10) % 10   # El segundo dígito
        permisos_o = indo_destino.i_perm % 10            # El tercer dígito
        permisos = False
        if session_inciada.credenciales.id == indo_destino.i_uid:
            # Permisos de escritura
            if permisos_u == 2 or permisos_u == 3 or permisos_u == 6 or permisos_u == 7:
                permisos = True
        elif session_inciada.credenciales.group_id == indo_destino.i_gid:
            # Permisos de escritura
            if permisos_g == 2 or permisos_g == 3 or permisos_g == 6 or permisos_g == 7:
                permisos = True
        else:
            # Permisos de escritura
            if permisos_o == 2 or permisos_o == 3 or permisos_o == 6 or permisos_o == 7:
                permisos = True
        
        if not permisos and not session_inciada.is_recovery and session_inciada.credenciales.user != 'root':
            print(f"No tienes permisos de escritura sobre la carpeta {self.destino}")
            return
        # Carpeta o Archivo que se desea mover
        indo_origen, i_o = find_carpeta(sblock, self.path, session_inciada.mounted.path)
        if(i_o == -1):
            print(f"Error: Ruta origen '{self.path}' no existe")
            return
        permisos_u = (indo_origen.i_perm // 100) % 10  # El primer dígito
        permisos_g = (indo_origen.i_perm // 10) % 10   # El segundo dígito
        permisos_o = indo_origen.i_perm % 10            # El tercer dígito
        permisos = False
        if session_inciada.credenciales.id == indo_origen.i_uid:
            # Permisos de escritura
            if permisos_u == 2 or permisos_u == 3 or permisos_u == 6 or permisos_u == 7:
                permisos = True
        elif session_inciada.credenciales.group_id == indo_origen.i_gid:
            # Permisos de escritura
            if permisos_g == 2 or permisos_g == 3 or permisos_g == 6 or permisos_g == 7:
                permisos = True
        else:
            # Permisos de escritura
            if permisos_o == 2 or permisos_o == 3 or permisos_o == 6 or permisos_o == 7:
                permisos = True
        
        if not permisos and not session_inciada.is_recovery and session_inciada.credenciales.user != 'root':
            print(f"No tienes permisos de escritura sobre la carpeta {self.destino}")
            return

        bloque_carpeta, i, write_block = find_url(sblock, self.path, session_inciada)
        if(write_block == -1):
            print(f"Error: Ruta origen '{self.path}' no existe")
            return
        name = bloque_carpeta.b_content[i].b_name
        file_link_move(sblock, name, session_inciada, indo_destino, i_o, i_d)

        bloque_carpeta.b_content[i].b_inodo = -1
        bloque_carpeta.b_content[i].b_name = "".encode('utf-8')[:12].ljust(12, b'\0')
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