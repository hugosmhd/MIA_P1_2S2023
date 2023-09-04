import os
import math
import time
import ctypes

import structs
from _global._global import particiones_montadas, session_inciada, users, groups
from comandos.mount.mount import find_mounted
from comandos.mkfs.mkfs import join_file, find_file, remove_grupo_usuario, crear_grupo_usuario
from comandos.fdisk.fdisk import exist_partition

class mkusr():
    def __init__(self):
        self.user = ""
        self.password = ""
        self.grp = ""

    def crear_mkusr(self):
        print("MAKE MKUSR")

        for user in users:
            if user.user_name == self.user:
                print("El usuario con ese nombre ya existe")
                return

        exist_group = False
        for group in groups:
            if group == self.grp:
                exist_group = True

        if not exist_group:
            print("Error: El grupo para el usuario no existe")
            return

        file = open(session_inciada.mounted.path, "rb+")
        sblock = structs.SuperBloque()
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()
        user_actual = structs.User()
        user_actual.user_name = self.user
        user_actual.user_password = self.password
        user_actual.group_name = self.grp

        data_user = f"{len(users) + 1},U,{self.grp},{self.user},{self.password}\n"
        crear_grupo_usuario(sblock, data_user, self.user, 'U', user_actual)

    def crear_rmusr(self):
        print("MAKE RMUSR, ESTE")


        exist = False
        user = None
        for user in users:
            if user.user_name == self.user:
                exist = True
                break

        if not exist:
            print("El usuario que desea eliminar no existe, verifique su entrada")
            return

        file = open(session_inciada.mounted.path, "rb+")
        sblock = structs.SuperBloque()
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()

        data_user = f"0,U,{user.group_name},{user.user_name},{user.user_password}"
        remove_grupo_usuario(sblock, data_user, user.user_name, 'U', 3)
