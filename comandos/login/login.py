import os
import math
import time
import ctypes

import structs
from _global._global import particiones_montadas, session_inciada, users, groups
from comandos.mount.mount import find_mounted
from comandos.mkfs.mkfs import join_file, find_file, find_carpeta_archivo
from comandos.fdisk.fdisk import exist_partition


def authenticate(mounted, part_start, user):
    file = open(mounted.path, "rb+")
    sblock = structs.SuperBloque()
    file.seek(part_start)
    file.readinto(sblock)

    # inodo_archive = structs.Inodo()
    # file.seek(sblock.s_inode_start + (ctypes.sizeof(structs.Inodo)))
    # file.readinto(inodo_archive)
    # file.close()
    session_inciada.mounted = mounted
    indo_carpeta_archivo, i, _, __ = find_carpeta_archivo(sblock, "/", session_inciada)
    if(i == -1):
        print(f"Error: Ruta especificada '/' no existe")
        return
    inodo_archivo, i_f = find_file(sblock, "/user.txt", mounted.path, indo_carpeta_archivo)
    if(i_f == -1):
        print(f"Error: Ruta especificada '/user.txt' no existe")
        return
    usuarios = join_file(sblock, inodo_archivo, mounted.path)
    print(usuarios)
    lineas = usuarios.split("\n")

    for i, linea in enumerate(lineas):
        atributos = linea.split(",")

        if len(atributos) == 5:
            user_actual = structs.User()
            user_actual.user_name = atributos[3]
            user_actual.user_password = atributos[4]
            user_actual.group_name = atributos[2]
            users.append(user_actual)
            if atributos[0] != "0":
                if atributos[3] == user.user and atributos[4] == user.password:
                    print("Usuario encontrado")
                    session_inciada.credenciales = user
                    session_inciada.mounted = mounted
                    session_inciada.is_logged = True
                    print(user.user)
                    print(user.password)
                    print(user.id)
            else:
                if atributos[3] == user.user and atributos[4] == user.password:
                    print("Error el usuario que busca ha sido eliminado.")
                    users.clear()
                    groups.clear()
                    return
        elif len(atributos) == 3:
            groups.append(atributos[2])


class login():
    def __init__(self):
        self.id = ""
        self.password = ""
        self.user = ""

    def crear_login(self, user):

        if session_inciada.is_logged:
            print("Error: Actualmente hay una sesion iniciada")
            return

        mounted = find_mounted(self.id)
        if(mounted == None):
            print("ID {self.id} no encontrado, verifique su entrada")
            return

        mbr = structs.MBR()
        file = open(mounted.path, 'rb')
        file.seek(0, 0)
        contenido_binario = file.read(ctypes.sizeof(mbr))
        ctypes.memmove(ctypes.byref(mbr), contenido_binario, ctypes.sizeof(mbr))
        file.close()
        tipo, particion, i = exist_partition(mounted.path, mounted.name, mbr)
        authenticate(mounted, mounted.part_start, user)

    def crear_logout(self):
        if session_inciada.is_logged:
            session_inciada.credenciales = None
            session_inciada.mounted = None
            session_inciada.is_logged = False
            users.clear()
            groups.clear()
            print("Sesion cerrada correctamente...")
            return
        print("Error no hay sesion iniciada actualmente")

