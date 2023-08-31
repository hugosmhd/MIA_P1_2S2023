import time
import random
import ctypes
import os
import struct
from datetime import datetime

import structs

class mkdisk:
    def __init__(self):
        self.size = 0   # int
        self.path = ''  # string
        self.name = ''  # string
        self.fit = 'FF'   # char
        self.unit = 'M'  # char

    def crear_mkdisk(self, disco):
        # print("MKDISK")
        # print("SIZE", self.size)
        # print("PATH", self.path)
        # print("NAME", self.name)
        # print("FIT", self.fit)
        # print("UNIT", self.unit)

        directorio, archivo = os.path.split(disco.path)
        # print(archivo)
        
        if not os.path.exists(directorio):
            os.makedirs(directorio)

        elif os.path.isfile(self.path):
            print(f"El disco {self.path} ya existe")
            return

        file = open(self.path, "wb")
        # with open(self.path, "wb") as file:
        tam_disco = 0
        ceros = b"\0" * 1024

        if disco.unit == "K":
            for i in range(disco.size):
                file.write(ceros)
            tam_disco = 1024 * disco.size
        elif disco.unit == "M" or disco.unit == "":
            for i in range(1024 * disco.size):
                file.write(ceros)
            tam_disco = 1024 * 1024 * disco.size
        
        disco_mbr = structs.MBR()
        disco_mbr.set_mbr_tamano(tam_disco)
        disco_mbr.set_mbr_fecha_creacion(int(time.time()))
        disco_mbr.set_mbr_dsk_signature(random.randint(0, 2147483647))
        if disco.fit == "FF":
            disco_mbr.set_dsk_fit('F')
        elif disco.fit == "WF":
            disco_mbr.set_dsk_fit('W')
        elif disco.fit == "BF":
            disco_mbr.set_dsk_fit('B')
        particiones_iniciales = [
            structs.Partition(),
            structs.Partition(),
            structs.Partition(),
            structs.Partition()
        ]
        for i, particion in enumerate(particiones_iniciales):
            disco_mbr.mbr_partitions[i] = particion

        print(ctypes.sizeof(disco_mbr))
        file.seek(0)
        file.write(ctypes.string_at(ctypes.byref(disco_mbr), ctypes.sizeof(disco_mbr)))

        # print("Tamaño del MBR ", ctypes.sizeof(disco))
        print(f"Disco \"{disco.path}\" creado correctamente")
        file.close()
        
        try:
            with open(disco.path, "rb") as file:
                contenido_binario = file.read()
            mbr = structs.MBR()
            ctypes.memmove(ctypes.byref(mbr), contenido_binario, ctypes.sizeof(mbr))
            print(" ----- DATOS DEL MBR ----- ")
            print(f"Tamaño del disco: {mbr.mbr_tamano} bytes")
            fecha_hora = datetime.fromtimestamp(mbr.mbr_fecha_creacion)
            fecha_formateada = fecha_hora.strftime("%d-%m-%Y %H:%M:%S")
            print(f"Fecha de creacion del disco: {fecha_formateada}")
            print(f"Signature: {mbr.mbr_dsk_signature}")
            print(f"Fit: {mbr.dsk_fit.decode()}")

            for i, particion in enumerate(mbr.mbr_partitions):
                print("------------------------------------------")
                print(f"Partición {i + 1}:")
                print("Estado:", particion.part_status.decode())
                print("Tipo:", particion.part_type.decode())
                print("Fit:", particion.part_fit.decode())
                print("Inicio:", particion.part_start)
                print("Tamaño:", particion.part_s)
                print("Nombre:", particion.part_name)

                # file.seek(0)
                # datos_mbr = file.read(struct.calcsize(structs.size_mbr()))
                # tam, fecha, sig, fit, partition = structs.deserializar_mbr(datos_mbr)
                # fecha_hora = datetime.fromtimestamp(fecha)

                # fecha_formateada = fecha_hora.strftime("%d-%m-%Y %H:%M:%S")
                # print(" ----- DATOS DEL MBR ----- ")
                # print(f"Tamaño del disco: {tam} bytes")
                # print(f"Fecha de creacion del disco: {fecha_formateada}")
                # print(f"Signature: {sig}")
                # print(f"Fit: {fit}")
        except FileNotFoundError:
            pass
