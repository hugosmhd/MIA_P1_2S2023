import os
import math
import time
import ctypes

import structs
from _global._global import particiones_montadas, session_inciada, users, groups, comando_actual
from comandos.mount.mount import find_mounted
from comandos.mkfs.mkfs import join_file, find_file, remove_grupo_usuario, crear_grupo_usuario
from comandos.fdisk.fdisk import exist_partition

class mkusr():
    def __init__(self):
        self.user = ""
        self.password = ""
        self.grp = ""
        self.tipo = 0

    def crear_mkusr(self):

        if not session_inciada.is_logged:
            print("Error: No se ha iniciado ninguna sesion")
            return
        elif session_inciada.is_logged and session_inciada.credenciales.user != 'root':
            print("Error: El comando 'mkusr' unicamente lo puede hacer un usuario root")
            return

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

    def crear_rmusr(self):

        if not session_inciada.is_logged:
            print("Error: No se ha iniciado ninguna sesion")
            return
        elif session_inciada.is_logged and session_inciada.credenciales.user != 'root':
            print("Error: El comando 'rmusr' unicamente lo puede hacer un usuario root")
            return

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
