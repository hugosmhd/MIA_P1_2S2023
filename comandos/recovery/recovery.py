import os
import math
import time
import ctypes
# import pyperclip

import structs
from _global._global import particiones_montadas, session_inciada, comando_actual, users, groups
from analizador import analizador
from comandos.mount.mount import find_mounted
from comandos.mkfs.mkfs import join_file, find_file, file_link, write_file, find_carpeta_archivo
from comandos.fdisk.fdisk import exist_partition
from comandos.mkdir.mkdir import crear_mkdir_r

class recovery():
    def __init__(self):
        self.id = ""

    def crear_recovery(self):
        if not session_inciada.is_logged:
            print("Error: No se ha iniciado ninguna sesion")
            return

        mounted = find_mounted(self.id)
        if(mounted == None):
            print("ID {self.id} no encontrado, verifique su entrada")
            return
        
        session_inciada.is_recovery = True
        super_bloque = structs.SuperBloque()
        file = open(mounted.path, "rb+")
        file.seek(mounted.part_start)
        file.readinto(super_bloque)
        
        super_bloque.s_first_ino = 2
        super_bloque.s_first_blo = 2
        super_bloque.s_filesystem_type = 2

        # Escribimos el superbloque en la posicion inicial
        file.seek(mounted.part_start)
        file.write(ctypes.string_at(ctypes.byref(super_bloque), ctypes.sizeof(super_bloque)))

        # Ahora solo tenemos que ingresar el primer inodo raiz
        inodo_root = structs.Inodo()
        inodo_root.i_uid = 1
        inodo_root.i_gid = 1
        inodo_root.i_size = 0
        inodo_root.i_atime = int(time.time())
        inodo_root.i_ctime = int(time.time())
        inodo_root.i_mtime = int(time.time())
        inodo_root.i_type = b'0'
        inodo_root.i_perm = 664
        inodo_root.i_block[0] = 0

        # Ahora creamos nuestro bloque de carpeta para crear la carpeta root
        carpeta_root = structs.BloqueCarpeta()
        carpeta_root.b_content[0].b_name = ".".encode('utf-8')[:12].ljust(12, b'\0')
        carpeta_root.b_content[0].b_inodo = 0
        carpeta_root.b_content[1].b_name = "..".encode('utf-8')[:12].ljust(12, b'\0')
        carpeta_root.b_content[1].b_inodo = 0
        carpeta_root.b_content[2].b_name = "user.txt".encode('utf-8')[:12].ljust(12, b'\0')
        carpeta_root.b_content[2].b_inodo = 1

        data = "1,G,root\n1,U,root,root,123\n"
        inodo_file_user = structs.Inodo()
        inodo_file_user.i_uid = 1
        inodo_file_user.i_gid = 1
        inodo_file_user.i_s = len(data.encode('utf-8'))
        inodo_file_user.i_atime = super_bloque.s_umtime
        inodo_file_user.i_ctime = super_bloque.s_umtime
        inodo_file_user.i_mtime = super_bloque.s_umtime
        inodo_file_user.i_type = b'1'
        inodo_file_user.i_perm = 664 # 0o664
        inodo_file_user.i_block[0] = 1

        file_user = structs.BloqueArchivo()
        file_user.b_content = data.encode('utf-8')[:64].ljust(64, b'\0')

        file.seek(super_bloque.s_bm_inode_start)
        # INODO CARPETA ROOT
        file.write(b'1')
        # INODO ARCHIVO USER
        file.write(b'1')

        file.seek(super_bloque.s_bm_block_start)
        # BLOQUE CARPETA ROOT
        file.write(b'd')
        # BLOQUE ARCHIVO USER.TXT
        file.write(b'f')

        file.seek(super_bloque.s_inode_start)
        # INODO CARPETA ROOT
        file.write(ctypes.string_at(ctypes.byref(inodo_root), ctypes.sizeof(inodo_root)))
        # INODO ARCHIVO USER
        file.write(ctypes.string_at(ctypes.byref(inodo_file_user), ctypes.sizeof(inodo_file_user)))

        file.seek(super_bloque.s_block_start)
        # BLOQUE CARPETA ROOT
        file.write(ctypes.string_at(ctypes.byref(carpeta_root), ctypes.sizeof(carpeta_root)))
        # BLOQUE ARCHIVO USER.TXT
        file.write(ctypes.string_at(ctypes.byref(file_user), ctypes.sizeof(file_user)))
        
        
        file.close()

        file = open(mounted.path, "rb+")
        journaling_actual = structs.Journaling()
        read_journaling = mounted.part_start + ctypes.sizeof(structs.SuperBloque)
        global users
        global groups
        usuarios = users.copy()
        grupos = groups.copy()
        users.clear()
        groups.clear()
        user_actual = structs.User()
        user_actual.id = str(1)
        user_actual.user = 'root'
        user_actual.password = '123'
        user_actual.group_name = 'root'
        user_actual.group_id = 1
        users.append(user_actual)
        groups.append('root')
        # session_inciada.is_recovery = True
        for _ in range(super_bloque.s_inodes_count):
            file.seek(read_journaling)
            file.readinto(journaling_actual)

            if(journaling_actual.fecha == 0):
                break

            analizador.analizar(journaling_actual.comando.decode())
            read_journaling += ctypes.sizeof(structs.Journaling)
        
        # Escribimos el superbloque en la posicion inicial
        super_bloque.s_filesystem_type = 3
        file.seek(mounted.part_start)
        file.write(ctypes.string_at(ctypes.byref(super_bloque), ctypes.sizeof(super_bloque)))
        file.close()
        new_users = usuarios.copy()
        new_groups = grupos.copy()
        session_inciada.is_recovery = False
        # user = new_users
        # groups = new_groups
    
    def crear_loss(self):
        if not session_inciada.is_logged:
            print("Error: No se ha iniciado ninguna sesion")
            return

        mounted = find_mounted(self.id)
        if(mounted == None):
            print("ID {self.id} no encontrado, verifique su entrada")
            return
        
        super_bloque = structs.SuperBloque()
        file = open(mounted.path, "rb+")
        file.seek(mounted.part_start)
        file.readinto(super_bloque)

        super_bloque.s_free_inodes_count = super_bloque.s_inodes_count
        super_bloque.s_free_blocks_count = super_bloque.s_blocks_count
        super_bloque.s_first_ino = 0
        super_bloque.s_first_blo = 0
        file.seek(mounted.part_start)
        file.write(ctypes.string_at(ctypes.byref(super_bloque), ctypes.sizeof(super_bloque)))
        file.close()

        file = open(mounted.path, "rb+")
        cero = b'0'
        # Ahora escribimos el bitmap de inodos
        file.seek(super_bloque.s_bm_inode_start)
        file.write(cero * super_bloque.s_inodes_count)

        # Ahora escribimos el bitmap de bloques
        file.seek(super_bloque.s_bm_block_start)
        file.write(cero * super_bloque.s_blocks_count)

        # Ahora escribimos los inodos
        inodo = structs.Inodo()
        file.seek(super_bloque.s_inode_start)
        for i in range(super_bloque.s_inodes_count):
            file.write(ctypes.string_at(ctypes.byref(inodo), ctypes.sizeof(inodo)))
        
        # Ahora escribimos los bloques
        bloque = structs.BloqueApuntadores()
        file.seek(super_bloque.s_block_start)
        for i in range(super_bloque.s_blocks_count):
            file.write(ctypes.string_at(ctypes.byref(bloque), ctypes.sizeof(bloque)))
            
        file.close()
    