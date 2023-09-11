import os
import math
import time
import ctypes

import structs
from _global._global import particiones_montadas, session_inciada, comando_actual
from comandos.mount.mount import find_mounted
from comandos.mkfs.mkfs import find_url, find_file, file_link_move, find_carpeta, find_carpeta_archivo
from comandos.fdisk.fdisk import exist_partition


class move():
    def __init__(self):
        self.path = ""
        self.destino = ""

    def crear_move(self):
        file = open(session_inciada.mounted.path, "rb+")
        sblock = structs.SuperBloque()
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()

        # Encontramos la carpeta destino
        indo_destino, i_d = find_carpeta(sblock, self.destino, session_inciada)

        # Carpeta o Archivo que se desea mover
        indo_origen, i_o = find_carpeta(sblock, self.path, session_inciada)
        bloque_carpeta, i, write_block = find_url(sblock, self.path, session_inciada)
        name = bloque_carpeta.b_content[i].b_name
        file_link_move(sblock, name, session_inciada, indo_destino, i_o, i_d)

        bloque_carpeta.b_content[i].b_inodo = -1
        bloque_carpeta.b_content[i].b_name = "".encode('utf-8')[:12].ljust(12, b'\0')
        file = open(session_inciada.mounted.path, "rb+")
        file.seek(write_block)
        file.write(ctypes.string_at(ctypes.byref(bloque_carpeta), ctypes.sizeof(bloque_carpeta)))
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