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
        # print("Grupos ", data_group)
        # indo_carpeta_archivo, i = find_carpeta_archivo(sblock, "/", session_inciada)
        # inodo_archivo, i_ino = find_file(sblock, "/user.txt", session_inciada.mounted.path, indo_carpeta_archivo)
        # txt = join_file(sblock, inodo_archivo, session_inciada.mounted.path)

        # segmentSize = 64
        # # segment_actual = len(txt) // segmentSize
        # # print("segment_actual ", segment_actual)
        # # segment = txt[segment_actual * segmentSize : (segment_actual + 1) * segmentSize]
        # txt += data_group
        # totalSegments = (len(txt)) // segmentSize
        # # write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * inodo_archivo.i_block[totalSegments - 1])
        # file = open(session_inciada.mounted.path, "rb+")
        # write_on_b = None
        # write_on_i = None
        # totalSegments = (totalSegments + 1) if len(txt) % 64 != 0 else totalSegments
        # # print("totalSegments", totalSegments)
        # iterations_blocks = min(totalSegments, 12)
        # for s in range(iterations_blocks):
        #     new_segment = txt[s * segmentSize : (s + 1) * segmentSize]
        #     # print("Wola", s)
        #     # print("new_segment ", new_segment)
        #     # # print(inodo_archivo.i_block[s])
        #     file_user = structs.BloqueArchivo()
        #     file_user.b_content = new_segment.encode('utf-8')[:64].ljust(64, b'\0')
        #     if inodo_archivo.i_block[s] == -1:
        #     #     print("Entraaaaaaa", s)
        #         inodo_archivo.i_block[s] = sblock.s_first_blo
        #         write_on_b = sblock.s_bm_block_start + sblock.s_first_blo
        #         file.seek(write_on_b)
        #         file.write(b'f')
        #         sblock.s_first_blo = next_first_block(sblock, session_inciada.mounted.path)
        #         sblock.s_free_blocks_count -= 1

        #     # print("ssss", inodo_archivo.i_block[s])    
        #     print(file_user.b_content)
        #     write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * inodo_archivo.i_block[s])
        #     file.seek(write_on)
        #     file.write(file_user)
        #     # print("termina")
            
        
        # file.seek(session_inciada.mounted.part_start)
        # file.write(sblock)
        # inodo_archivo.i_s = len(txt)
        # write_on_i = sblock.s_inode_start + (ctypes.sizeof(structs.Inodo) * i_ino)
        # file.seek(write_on_i)
        # file.write(inodo_archivo)
        # file.close()
        # groups.append(self.name)

        # inodo_arch, i_f = find_file(sblock, "/user.txt", session_inciada.mounted.path, indo_carpeta_archivo)
        # print(inodo_arch.i_block[0])
        # print(inodo_arch.i_block[1])
        # print(inodo_arch.i_block[2])
        # # print("INODO ", i_ino)
        # txt = join_file(sblock, inodo_arch, session_inciada.mounted.path)
        # print("JOIN FILE MKFILE")
        # print(txt)
        # print(inodo_archivo.i_s)

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
        remove_grupo_usuario(sblock, data_group, self.name, 'G')

        # indo_carpeta_archivo, i = find_carpeta_archivo(sblock, "/", session_inciada)
        # inodo_archivo, i_ino = find_file(sblock, "/user.txt", session_inciada.mounted.path, indo_carpeta_archivo)
        # txt = join_file(sblock, inodo_archivo, session_inciada.mounted.path)
        # lineas = txt.split('\n')
        # new_txt = ""
        # for i, linea in enumerate(lineas):
        #     grupo = linea.split(',')
        #     # print(linea)
        #     if len(linea) > 0 and grupo[1] == 'G':
        #     #     grupo = linea.split(',')
        #     #     print("buenaaaaaaaas", grupo[0], grupo[2])
        #         if grupo[0] != '0' and grupo[2] == self.name:
        #             new_txt += f"0,G,{self.name}\n"
        #             continue
        #         elif grupo[2] == self.name:
        #             print("El grupo ya ha sido eliminado anteriormente")
        #             return

        #     if len(linea) > 0:
        #         new_txt += linea + '\n'
        
        # print("Terminado, ", new_txt)


        # # -------------------------------------------------
        # segmentSize = 64
        # # segment_actual = len(txt) // segmentSize
        # # print("segment_actual ", segment_actual)
        # # segment = txt[segment_actual * segmentSize : (segment_actual + 1) * segmentSize]
        # # txt += data_group
        # totalSegments = (len(new_txt)) // segmentSize
        # # write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * inodo_archivo.i_block[totalSegments - 1])
        # file = open(session_inciada.mounted.path, "rb+")
        # totalSegments = (totalSegments + 1) if len(new_txt) % 64 != 0 else totalSegments
        # print("totalSegments", totalSegments)
        # iterations_blocks = min(totalSegments, 12)
        # for s in range(iterations_blocks):
        #     new_segment = new_txt[s * segmentSize : (s + 1) * segmentSize]
        #     # print("Wola", s)
        #     # print("new_segment ", new_segment)
        #     # # print(inodo_archivo.i_block[s])
        #     file_user = structs.BloqueArchivo()
        #     file_user.b_content = new_segment.encode('utf-8')[:64].ljust(64, b'\0')
        #     if inodo_archivo.i_block[s] == -1:
        #     #     print("Entraaaaaaa", s)
        #         inodo_archivo.i_block[s] = sblock.s_first_blo
        #         write_on_b = sblock.s_bm_block_start + sblock.s_first_blo
        #         file.seek(write_on_b)
        #         file.write(b'f')
        #         sblock.s_first_blo = next_first_block(sblock, session_inciada.mounted.path)
        #         sblock.s_free_blocks_count -= 1

        #     # print("ssss", inodo_archivo.i_block[s])    
        #     print(file_user.b_content)
        #     write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * inodo_archivo.i_block[s])
        #     file.seek(write_on)
        #     file.write(file_user)
        #     # print("termina")
            
        
        # file.seek(session_inciada.mounted.part_start)
        # file.write(sblock)
        # inodo_archivo.i_s = len(new_txt)
        # write_on_i = sblock.s_inode_start + (ctypes.sizeof(structs.Inodo) * i_ino)
        # file.seek(write_on_i)
        # file.write(inodo_archivo)
        # file.close()

        # inodo_arch, i_f = find_file(sblock, "/user.txt", session_inciada.mounted.path, indo_carpeta_archivo)
        # print(inodo_arch.i_block[0])
        # print(inodo_arch.i_block[1])
        # print(inodo_arch.i_block[2])
        # print("INODO ", i_ino)
        # txt = join_file(sblock, inodo_arch, session_inciada.mounted.path)
        # print("JOIN FILE MKFILE")
        # print(txt)
        # print(inodo_archivo.i_s)
