import os
import ctypes

import structs
from _global._global import particiones_montadas
from comandos.fdisk.fdisk import exist_partition

def get_number_mount(path, name):
    number = 1
    for montada in particiones_montadas:
        if(path == montada.path and name == montada.name):
            return -1
        elif path == montada.path:
            number += 1
    return number

def recorrer_montadas():
    for montada in particiones_montadas:
        print(f"\t> Ruta: {montada.path},  Particion: {montada.name},  Id: {montada.id}")

def find_mounted(id_):
    for montada in particiones_montadas:
        if(id_ == montada.id):
            return montada
    return None

class mount:
    def __init__(self):
        self.path = ""
        self.name = ""

    def crear_mount(self):
        if self.path == "" and self.name == "":
            recorrer_montadas()
            return
        mbr = structs.MBR()
        with open(self.path, "rb") as file:
            file.seek(0, 0)
            contenido_binario = file.read(ctypes.sizeof(mbr))
        ctypes.memmove(ctypes.byref(mbr), contenido_binario, ctypes.sizeof(mbr))

        tipo, particion, i = exist_partition(self.path, self.name, mbr)
        if not tipo:
            print("No existe ninguna particion con ese nombre")
            return
        
        if tipo == 'PE':
            particion = mbr.mbr_partitions[i]
            if particion.part_type == b'P':
                number = get_number_mount(self.path, self.name)
                if(number != -1):
                    archivo = os.path.splitext(os.path.basename(self.path))[0]
                    id_ = "93" + str(number) + archivo
                    new_mount = structs.Mounted(self.path, self.name, id_, particion.part_start)
                    # print("New mount")
                    # print(new_mount.path)
                    # print(new_mount.name)
                    # print(new_mount.id)
                    particiones_montadas.append(new_mount)
                    recorrer_montadas()
                else:
                    print(f"La particion {self.name} ya ha sido montada")
                    return
            elif particion.part_type == b'E':
                print(f"La particion {self.name} no se puede montar porque es una particion extendida")
                return
        else:
            number = get_number_mount(self.path, self.name)
            if(number != -1):
                archivo = os.path.splitext(os.path.basename(self.path))[0]
                id_ = "93" + str(number) + archivo
                new_mount = structs.Mounted(self.path, self.name, id_, particion.part_start)
                # print("New mount")
                # print(new_mount.path)
                # print(new_mount.name)
                # print(new_mount.id)
                particiones_montadas.append(new_mount)
                recorrer_montadas()
            else:
                print(f"La particion {self.name} ya ha sido montada")
                return

    def crear_unmount(self):
        for i, montada in enumerate(particiones_montadas):
            if(self.name == montada.id):
                particiones_montadas.pop(i)
                print(f"La particion {montada.name} ha sido desmontada")
                return
        print(f"No se ha encontrado ninguna particion con el id {self.name}")