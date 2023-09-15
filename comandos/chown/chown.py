import os
import math
import time
import ctypes
import pyperclip

import structs
from _global._global import particiones_montadas, session_inciada, comando_actual, users
from comandos.mount.mount import find_mounted
from comandos.mkfs.mkfs import find_carpeta, find_file, cambiar_permisos_r, cambiar_propietario_r, find_carpeta_archivo
from comandos.fdisk.fdisk import exist_partition
from comandos.mkdir.mkdir import crear_mkdir_r

class chown():
    def __init__(self):
        self.path = ""
        self.user = ""
        self.recursivo = False

    def crear_chown(self):

        if self.user == "" or self.path == "":
            print("Error: Verifique su entrada faltan parametros obligatorios")
            return
        
        # SOLO ROOT LO PUEDE USAR PARA TODOS
        # LOS USUARIOS SOLO SOBRE SUS PROPIOS ARCHIVOS
        if not session_inciada.is_logged:
            print("Error: No se ha iniciado ninguna sesion")
            return
        

        existe_usuario = False
        usuario = None
        for user in users:
            if user.user == self.user:
                existe_usuario = True
                usuario = user
                break
        
        if not existe_usuario:
            print(f"Error: El usuario {self.user} no existe")
            return

        file = open(session_inciada.mounted.path, "rb+")
        sblock = structs.SuperBloque()
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()

        # Carpeta o Archivo que se desea cambiar de propietario
        indo_origen, i_o = find_carpeta(sblock, self.path, session_inciada.mounted.path)
        if session_inciada.credenciales.user != 'root' and indo_origen.i_uid != session_inciada.credenciales.id:
            print(f"Error: No se puedes cambiar de propietario el archivo {self.path}")
            return

        if not self.recursivo:
            indo_origen.i_uid = int(usuario.id)
            file = open(session_inciada.mounted.path, "rb+")
            write_on = sblock.s_inode_start + (ctypes.sizeof(structs.Inodo) * i_o)
            file.seek(write_on)
            file.write(ctypes.string_at(ctypes.byref(indo_origen), ctypes.sizeof(indo_origen)))
            file.close()
        else:
            file = open(session_inciada.mounted.path, "rb+")
            cambiar_propietario_r(sblock, file, indo_origen, i_o, usuario.id, session_inciada.credenciales.id)
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
