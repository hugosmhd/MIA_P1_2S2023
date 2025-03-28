import os
import math
import time
import ctypes

import structs
from _global._global import particiones_montadas, session_inciada, users, groups, comando_actual
from comandos.mount.mount import find_mounted
from comandos.mkfs.mkfs import join_file, find_file, remove_grupo_usuario, crear_grupo_usuario
from comandos.fdisk.fdisk import exist_partition

class mkgrp():
    def __init__(self):
        self.name = ""
        self.tipo = 0

    def crear_mkgrp(self):

        if self.name == "":
            print("Error: Verifique su entrada faltan parametros obligatorios")
            return

        if not session_inciada.is_logged:
            print("Error: No se ha iniciado ninguna sesion")
            return
        elif not session_inciada.is_recovery and session_inciada.credenciales.user != 'root':
            print("Error: El comando 'mkgrp' unicamente lo puede hacer un usuario root")
            return

        for group in groups:
            if group == self.name:
                print("El grupo con ese nombre ya existe")
                return

        file = open(session_inciada.mounted.path, "rb+")
        sblock = structs.SuperBloque()
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()

        data_group = str(len(groups) + 1) + ",G," + self.name + "\n"
        crear_grupo_usuario(sblock, data_group, self.name, 'G')

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

    def crear_rmgrp(self):
        if self.name == "":
            print("Error: Verifique su entrada faltan parametros obligatorios")
            return

        if not session_inciada.is_logged:
            print("Error: No se ha iniciado ninguna sesion")
            return
        elif not session_inciada.is_recovery and session_inciada.credenciales.user != 'root':
            print("Error: El comando 'rmgrp' unicamente lo puede hacer un usuario root")
            return

        exist = False
        for group in groups:
            if group == self.name:
                exist = True

        if not exist:
            print("El grupo que desea eliminar no existe, verifique su entrada")
            return

        file = open(session_inciada.mounted.path, "rb+")
        sblock = structs.SuperBloque()
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()

        data_group = f"0,G,{self.name}"
        remove_grupo_usuario(sblock, data_group, self.name, 'G', 2)

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
