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
