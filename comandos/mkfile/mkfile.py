import os
import math
import time
import ctypes
# import pyperclip

import structs
from _global._global import particiones_montadas, session_inciada, comando_actual
from comandos.mount.mount import find_mounted
from comandos.mkfs.mkfs import join_file, find_file, file_link, write_file, find_carpeta_archivo
from comandos.fdisk.fdisk import exist_partition
from comandos.mkdir.mkdir import crear_mkdir_r

class mkfile():
    def __init__(self):
        self.path = ""
        self.recursivo = False
        self.size = 0
        self.size_activo = False
        self.cout = ""

    def crear_mkfile(self):

        if self.path == "":
            print("Error: Verifique su entrada faltan parametros obligatorios")
            return

        if not session_inciada.is_logged:
            print("Error: No se ha iniciado ninguna sesion")
            return

        if self.size < 0:
            print("Error: El tamaño del archivo no puede ser negativo")
            return

        directorio, archivo_ = os.path.split(self.path)
        if self.recursivo:
            file = open(session_inciada.mounted.path, "rb+")
            sblock = structs.SuperBloque()
            file.seek(session_inciada.mounted.part_start)
            file.readinto(sblock)
            file.close()
            indo_carpeta_archivo, i_c, encontrada, carpetas = find_carpeta_archivo(sblock, directorio, session_inciada, True)
            inodo_actual = structs.Inodo()
            
            file = open(session_inciada.mounted.path, "rb+")
            read_on_i = sblock.s_inode_start + (ctypes.sizeof(structs.Inodo) * i_c)
            file.seek(read_on_i)
            file.readinto(inodo_actual)
            file.close()

            permisos_u = (inodo_actual.i_perm // 100) % 10  # El primer dígito
            permisos_g = (inodo_actual.i_perm // 10) % 10   # El segundo dígito
            permisos_o = inodo_actual.i_perm % 10            # El tercer dígito
            permisos = False
            if session_inciada.credenciales.id == inodo_actual.i_uid:
                # Permisos de escritura
                if permisos_u == 2 or permisos_u == 3 or permisos_u == 6 or permisos_u == 7:
                    permisos = True
            elif session_inciada.credenciales.group_id == inodo_actual.i_gid:
                # Permisos de escritura
                if permisos_g == 2 or permisos_g == 3 or permisos_g == 6 or permisos_g == 7:
                    permisos = True
            else:
                # Permisos de escritura
                if permisos_o == 2 or permisos_o == 3 or permisos_o == 6 or permisos_o == 7:
                    permisos = True
            
            if not permisos and not session_inciada.is_recovery:
                print(f"Error: Problemas de permisos para crear el directorio {self.path}")
                return

            if not encontrada:
                for i, carpeta in enumerate(carpetas):
                    indo_carpeta_archivo, i_c = crear_mkdir_r(carpeta, indo_carpeta_archivo, i_c)


        # -------------------------------------------
        num = '0'
        numbers = "0123456789"
        content = ""
        if self.cout != "":
            try:

                with open(self.cout, 'r') as archivo:
                    content = archivo.read()
            except FileNotFoundError:
                print(f"Error: La ruta de cout {self.cout} no existe")
                return
        else:
            iterations_fill = self.size // 10
            for _ in range(iterations_fill):
                content += numbers

            iterations_fill = self.size % 10
            for _ in range(iterations_fill):
                content += num
                if num == '9':
                    num = '0'
                    continue
                num = chr(ord(num) + 1)

        sblock = structs.SuperBloque()
        file = open(session_inciada.mounted.path, "rb+")
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()

        directorio, archivo_ = os.path.split(self.path)
        # Se verifica que no exista un archivo con el mismo nombre
        indo_carpeta_archivo, i, _, __ = find_carpeta_archivo(sblock, directorio, session_inciada)
        if(i == -1):
            print(f"Error: Ruta especificada '{directorio}' no existe")
            return
        inodo_archivo, i_f = find_file(sblock, archivo_, session_inciada.mounted.path, indo_carpeta_archivo, False)
        if(i_f != -1):
            print(f"Error: Archivo '{self.path}' ya existe")
            return

        permisos_u = (indo_carpeta_archivo.i_perm // 100) % 10  # El primer dígito
        permisos_g = (indo_carpeta_archivo.i_perm // 10) % 10   # El segundo dígito
        permisos_o = indo_carpeta_archivo.i_perm % 10            # El tercer dígito
        permisos = False
        if session_inciada.credenciales.id == indo_carpeta_archivo.i_uid:
            # Permisos de escritura
            if permisos_u == 2 or permisos_u == 3 or permisos_u == 6 or permisos_u == 7:
                permisos = True
        elif session_inciada.credenciales.group_id == indo_carpeta_archivo.i_gid:
            # Permisos de escritura
            if permisos_g == 2 or permisos_g == 3 or permisos_g == 6 or permisos_g == 7:
                permisos = True
        else:
            # Permisos de escritura
            if permisos_o == 2 or permisos_o == 3 or permisos_o == 6 or permisos_o == 7:
                permisos = True
        
        if not permisos and not session_inciada.is_recovery and session_inciada.credenciales.user != 'root':
            print(f"No tienes permisos de escritura sobre la carpeta {directorio}")
            return

        if sblock.s_first_ino == -1:
            # No hay más inodos disponibles, error
            return
        elif sblock.s_first_blo == -1 and size > 0:
            # No hay más bloques disponibles, error
            return

        inodo_file = structs.Inodo()
        inodo_file.i_uid = session_inciada.credenciales.id
        inodo_file.i_gid = session_inciada.credenciales.group_id
        inodo_file.i_s = len(content)
        inodo_file.i_atime = int(time.time())
        inodo_file.i_ctime = int(time.time())
        inodo_file.i_mtime = int(time.time())
        inodo_file.i_type = b'1'
        inodo_file.i_perm = 664 # 0o664

        file_link(sblock, self.path, session_inciada, indo_carpeta_archivo, i)
        file = open(session_inciada.mounted.path, "rb+")
        
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()
        write_file(sblock, inodo_file, content, session_inciada)
        inodo_archivo, i_f = find_file(sblock, self.path, session_inciada.mounted.path, indo_carpeta_archivo)
        if(i_f == -1):
            print(f"Error: Ruta especificada '{self.path}' no existe")
            return
        # print(inodo_archivo.i_s)
        txt = join_file(sblock, inodo_archivo, session_inciada.mounted.path)
        # pyperclip.copy(txt)

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

    def file_contenido(self):
        num = '0'
        numbers = "0123456789"
        content = ""
        if self.cout != "":
            try:
                with open(self.cout, 'r') as archivo:
                    content = archivo.read(self.size) if self.size_activo else archivo.read()
            except FileNotFoundError:
                print(f"Error: La ruta de cout {self.cout} no existe")
        else:
            iterations_fill = self.size // 10
            for _ in range(iterations_fill):
                content += numbers

            iterations_fill = self.size % 10
            for _ in range(iterations_fill):
                content += num
                if num == '9':
                    num = '0'
                    continue
                num = chr(ord(num) + 1)
        return content
