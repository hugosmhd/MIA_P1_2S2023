import os
import math
import time
import ctypes

import structs
from _global._global import particiones_montadas, session_inciada, users, groups
from comandos.mount.mount import find_mounted
from comandos.mkfs.mkfs import join_file, find_file, remove_grupo_usuario, crear_grupo_usuario
from comandos.fdisk.fdisk import exist_partition

class mkgrp():
    def __init__(self):
        self.name = ""

    def crear_mkgrp(self):
        print("MAKE MKGRP")

        if not session_inciada.is_logged:
            print("Error: No se ha iniciado ninguna sesion")
            return
        elif session_inciada.is_logged and session_inciada.credenciales.user != 'root':
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

    def crear_rmgrp(self):
        print("MAKE RMGRP, ESTE")

        if not session_inciada.is_logged:
            print("Error: No se ha iniciado ninguna sesion")
            return
        elif session_inciada.is_logged and session_inciada.credenciales.user != 'root':
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
