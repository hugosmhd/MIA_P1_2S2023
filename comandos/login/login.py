import os
import math
import time
import ctypes

import structs
from _global._global import particiones_montadas, session_inciada
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
    indo_carpeta_archivo = find_carpeta_archivo(sblock, "/", session_inciada)
    inodo_archivo = find_file(sblock, "/user.txt", mounted.path, indo_carpeta_archivo)
    usuarios = join_file(sblock, inodo_archivo, mounted.path)
    print(usuarios)
    lineas = usuarios.split("\n")

    for i, linea in enumerate(lineas):
        atributos = linea.split(",")

        if len(atributos) == 5:
            if atributos[0] != "0":
                if atributos[3] == user.user and atributos[4] == user.password:
                    print("Usuario encontrado")
                    session_inciada.credenciales = user
                    session_inciada.mounted = mounted
                    session_inciada.is_logged = True
                    print(user.user)
                    print(user.password)
                    print(user.id)



class login():
    def __init__(self):
        self.id = ""
        self.password = ""
        self.user = ""

    def crear_login(self, user):

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
        if tipo == 'PE':
            
            # print("Superbloque")
            # print(sblock.s_inodes_count)
            # print("Inodo Archivo")
            # print(inodo_archive.i_s)
            # usuarios = join_file(sblock, inodo_archive, mounted.path)
            # print(usuarios)

            authenticate(mounted, particion.part_start, user)

