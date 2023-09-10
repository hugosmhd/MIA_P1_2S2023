import os
import math
import time
import ctypes

import structs
from _global._global import particiones_montadas, session_inciada, comando_actual
from comandos.mount.mount import find_mounted
from comandos.mkfs.mkfs import find_url, find_file, file_link, write_file, find_carpeta_archivo
from comandos.fdisk.fdisk import exist_partition


class rename():
    def __init__(self):
        self.path = ""
        self.name = ""

    def crear_rename(self):
        print("rename")
        print(self.path)
        print(self.name)

        file = open(session_inciada.mounted.path, "rb+")
        sblock = structs.SuperBloque()
        file.seek(session_inciada.mounted.part_start)
        file.readinto(sblock)
        file.close()

        bloque_carpeta, i, write_block = find_url(sblock, self.path, session_inciada)
        bloque_carpeta.b_content[i].b_name = self.name.encode('utf-8')[:12].ljust(12, b'\0')
        file = open(session_inciada.mounted.path, "rb+")
        file.seek(write_block)
        file.write(ctypes.string_at(ctypes.byref(bloque_carpeta), ctypes.sizeof(bloque_carpeta)))
        file.close()

        if sblock.s_filesystem_type == 3:
            print("entra a la escritura del journaling")
            global comando_actual
            print(comando_actual)
            file = open(session_inciada.mounted.path, "rb+")
            journaling_actual = structs.Journaling()
            read_journaling = session_inciada.mounted.part_start + ctypes.sizeof(structs.SuperBloque)
            for _ in range(sblock.s_inodes_count):
                file.seek(read_journaling)
                file.readinto(journaling_actual)

                if(journaling_actual.fecha == 0):
                    journaling_actual.comando = comando_actual[0].encode('utf-8')[:100].ljust(100, b'\0')
                    journaling_actual.fecha = int(time.time())
                    print("Se escribe el journaling en mkfile")
                    print(journaling_actual.comando)
                    print(journaling_actual.fecha)
                    file.seek(read_journaling)
                    file.write(ctypes.string_at(ctypes.byref(journaling_actual), ctypes.sizeof(journaling_actual)))
                    break

                read_journaling += ctypes.sizeof(structs.Journaling)
            file.close()
        # print(bloque_carpeta.b_content[2].b_name.decode())
        # print(bloque_carpeta.b_content[2].b_inodo)