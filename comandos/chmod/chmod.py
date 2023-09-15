import os
import math
import time
import ctypes
import pyperclip

import structs
from _global._global import particiones_montadas, session_inciada, comando_actual
from comandos.mount.mount import find_mounted
from comandos.mkfs.mkfs import find_carpeta, find_file, cambiar_permisos_r, write_file, find_carpeta_archivo
from comandos.fdisk.fdisk import exist_partition
from comandos.mkdir.mkdir import crear_mkdir_r

class chmod():
    def __init__(self):
        self.path = ""
        self.recursivo = False
        self.ugo = 0

    def crear_chmod(self):

        if self.path == "" or self.ugo == "":
            print("Error: Verifique su entrada faltan parametros obligatorios")
            return
        
        # SOLO ROOT LO PUEDE USAR
        if not session_inciada.is_logged:
            print("Error: No se ha iniciado ninguna sesion")
            return
        elif not session_inciada.is_recovery and session_inciada.credenciales.user != 'root':
            print("Error: El comando 'chgrp' unicamente lo puede hacer un usuario root")
            return

        file = open(session_inciada.mounted.path, "rb+")
        sblock = structs.SuperBloque()
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()

        # Carpeta o Archivo que se desea cambiar permisos
        indo_origen, i_o = find_carpeta(sblock, self.path, session_inciada.mounted.path)
        if(i_o == -1):
            print(f"Error: Ruta destino '{self.path}' no existe")
            return
        p_propietario = self.ugo // 100
        p_grupo = (self.ugo // 10) % 10
        p_otros = self.ugo % 10
        if p_propietario > 7:
            print("Error: Rango no valido para los permisos del propietario")
            return
        elif p_grupo > 7:
            print("Error: Rango no valido para los permisos del grupo")
            return
        elif p_otros > 7:
            print("Error: Rango no valido para los permisos de otros usuarios")
            return

        if not self.recursivo:
            indo_origen.i_perm = self.ugo
            file = open(session_inciada.mounted.path, "rb+")
            write_on = sblock.s_inode_start + (ctypes.sizeof(structs.Inodo) * i_o)
            file.seek(write_on)
            file.write(ctypes.string_at(ctypes.byref(indo_origen), ctypes.sizeof(indo_origen)))
            file.close()
        else:
            print("Antes de enviar, ", i_o)
            file = open(session_inciada.mounted.path, "rb+")
            cambiar_permisos_r(sblock, file, indo_origen, i_o, self.ugo)
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

