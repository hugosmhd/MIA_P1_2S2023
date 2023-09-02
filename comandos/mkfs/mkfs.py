import os
import math
import time
import ctypes

import structs
from _global._global import particiones_montadas
from comandos.mount.mount import find_mounted
from comandos.fdisk.fdisk import exist_partition

def next_first_inodo(sblock, path_disk):
    file = open(path_disk, "rb+")
    sblock.s_first_ino += 1
    read_on = sblock.s_bm_inode_start + sblock.s_first_ino
    file.seek(read_on)
    bit = file.read(1)
    while sblock.s_first_ino <= sblock.s_inodes_count:
        if bit == b'0':
            file.close()
            return sblock.s_first_ino
        sblock.s_first_ino += 1
        read_on += 1
        file.seek(read_on)
        bit = file.read(1)

    file.close()
    return -1

def next_first_block(sblock, path_disk):
    file = open(path_disk, "rb")
    sblock.s_first_blo += 1
    read_on = sblock.s_bm_block_start + sblock.s_first_blo
    file.seek(read_on)
    bit = file.read(1)
    # print("next_first_block")
    while sblock.s_first_blo <= sblock.s_blocks_count:
        # print(bit)
        if bit == b'0':
            file.close()
            return sblock.s_first_blo
        sblock.s_first_blo += 1
        read_on += 1
        file.seek(read_on)
        bit = file.read(1)

    file.close()
    return -1

def find_file(super_bloque, path, path_disk, inodo):
    read_on_file = -1
    read_on_archive = -1
    
    directorio, archivo = os.path.split(path)
    carpetas = directorio.split('/')
    print(carpetas)
    print(directorio, archivo)
    if carpetas[0] != '':
        print("Error archivo no encontrado, verifique su ruta")
        return
    # inodo = structs.Inodo()
    inodo_archivo = structs.Inodo()

    bcarpeta = structs.BloqueCarpeta()
    file = open(path_disk, 'rb')
    # file.seek(super_bloque.s_inode_start)
    # file.readinto(inodo)
    # for i, carpeta in enumerate(carpetas):
    #     print(carpeta, i)

    for b in range(12):
        if inodo.i_block[b] == -1:
            continue
        read_on_file = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * inodo.i_block[b])
        file.seek(read_on_file)
        file.readinto(bcarpeta)
        for j in range(4):
            nombre_carpeta = bcarpeta.b_content[j].b_name.decode()
            if nombre_carpeta == archivo:
                # print("Archivo encontrado")
                # print(nombre_carpeta)
                # print(archivo)
                read_on_archive = super_bloque.s_inode_start + (ctypes.sizeof(structs.Inodo) * bcarpeta.b_content[j].b_inodo)
                file.seek(read_on_archive)
                file.readinto(inodo_archivo)
                # i = bcarpeta.b_content[j].b_inodo
                # inodo_actual = inode_archive
                file.close()
                return inodo_archivo

    file.close()
    print("Archivo no encontrado")
    return None

def find_carpeta(super_bloque, path, user_session):
    print("find_carpeta")
    directorio, carpeta_crear = os.path.split(path)
    carpetas = directorio.split('/')

    # Verificar que arranque desde la raiz
    if carpetas[0] != '':
        print("Error archivo no encontrado, verifique su ruta")
        return


    bcarpeta = structs.BloqueCarpeta()
    inodo = structs.Inodo()
    i_c = 0
    encontrada = False
    file = open(user_session.mounted.path, 'rb+')
    file.seek(super_bloque.s_inode_start)
    file.readinto(inodo)

    if(len(carpetas) >= 2 and carpetas[1] != ''):
        for i, carpeta in enumerate(carpetas, start=1):
            # print(carpeta, i)
            for b in range(12):
                if inodo.i_block[b] == -1:
                    continue
                read_on_file = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * inodo.i_block[b])
                file.seek(read_on_file)
                file.readinto(bcarpeta)
                for j in range(4):
                    nombre_carpeta = bcarpeta.b_content[j].b_name.decode()
                    if nombre_carpeta == carpeta:
                        print("Carpeta encontrada jojo encontrado")
                        read_on_archive = super_bloque.s_inode_start + (ctypes.sizeof(structs.Inodo) * bcarpeta.b_content[j].b_inodo)
                        file.seek(read_on_archive)
                        file.readinto(inodo)
                        i_c = bcarpeta.b_content[j].b_inodo
                        encontrada = True
                        break
                if encontrada:
                    encontrada = False
                    break

    file.close()
    print("Holaaaaaaaaaaaaaaaa Adiossssss", i_c)
    return inodo, i_c

def find_carpeta_archivo(super_bloque, path, user_session):
    print("find_carpeta_archivo")
    directorio, archivo = os.path.split(path)
    carpetas = directorio.split('/')
    print(carpetas)

    # Verificar que arranque desde la raiz
    if carpetas[0] != '':
        print("Error archivo no encontrado, verifique su ruta")
        return


    bcarpeta = structs.BloqueCarpeta()
    inodo = structs.Inodo()
    i_c = 0
    encontrada = False
    file = open(user_session.mounted.path, 'rb+')
    file.seek(super_bloque.s_inode_start)
    file.readinto(inodo)

    if(len(carpetas) >= 2 and carpetas[1] != ''):
        for i, carpeta in enumerate(carpetas, start=1):
            print(carpeta, i)
            for b in range(12):
                if inodo.i_block[b] == -1:
                    continue
                read_on_file = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * inodo.i_block[b])
                file.seek(read_on_file)
                file.readinto(bcarpeta)
                for j in range(4):
                    nombre_carpeta = bcarpeta.b_content[j].b_name.decode()
                    if nombre_carpeta == carpeta:
                        print("Carpeta encontrada jaja encontrado")
                        # print(nombre_carpeta)
                        # print(archivo)
                        read_on_archive = super_bloque.s_inode_start + (ctypes.sizeof(structs.Inodo) * bcarpeta.b_content[j].b_inodo)
                        file.seek(read_on_archive)
                        file.readinto(inodo)
                        i_c = bcarpeta.b_content[j].b_inodo
                        encontrada = True
                        break
                        # i = bcarpeta.b_content[j].b_inodo
                        # inodo_actual = inode_archive
                        # file.close()
                        # return inodo
                if encontrada:
                    encontrada = False
                    break
                

    file.close()
    print("Holaaaaaaaaaaaaaaaa", i_c)
    return inodo, i_c

def join_file(super_bloque, inodo_file, path_disk):
    txt = ""
    read_on_archive = -1
    read_on_block = -1
    file = open(path_disk, "rb")
    block_archive = structs.BloqueArchivo()
    segmentSize = 63
    totalSegments = inodo_file.i_s // segmentSize
    if inodo_file.i_s % segmentSize != 0:
        totalSegments += 1
    iterations_blocks = min(totalSegments, 12)
    # print("Join file")
    # print("iterations_blocks:", iterations_blocks)
    # print("sizeinodo:", inodo_file.i_s)
    for b in range(iterations_blocks):
        if inodo_file.i_block[b] == -1:
            break
        read_on_archive = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * inodo_file.i_block[b])
        file.seek(read_on_archive)
        file.readinto(block_archive)
        txt += block_archive.b_content.decode()

    file.close()
    return txt

def file_link(super_bloque, path, user_session, inodo, i):
    # print("file_link")
    read_on_file = -1
    read_on_archive = -1
    write_on_inodo = -1
    write_on_block = -1
    directorio, archivo = os.path.split(path)
    carpetas = directorio.split('/')

    # Verificar que arranque desde la raiz
    if carpetas[0] != '':
        print("Error archivo no encontrado, verifique su ruta")
        return

    # inodo = structs.Inodo()
    file = open(user_session.mounted.path, 'rb+')
    # file.seek(super_bloque.s_inode_start)
    # file.readinto(inodo)
    # i = 0
    # for i, carpeta in enumerate(carpetas):
    #     print(carpeta, i)

    bcarpeta = structs.BloqueCarpeta()
    uno = b'1'
    for b in range(12):
        if inodo.i_block[b] == -1:
            if super_bloque.s_first_blo == -1:
                # YA NO HAY MÁS BLOQUES PARA CREAR
                print("No hay mas bloques desde MKFS")
                return

            carpeta = structs.BloqueCarpeta()
            carpeta.b_content[0].b_name = archivo.encode('utf-8')[:12].ljust(12, b'\0')
            carpeta.b_content[0].b_inodo = super_bloque.s_first_ino
            write_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * super_bloque.s_first_blo)
            file.seek(write_on_block)
            file.write(ctypes.string_at(ctypes.byref(carpeta), ctypes.sizeof(carpeta)))

            inodo.i_block[b] = super_bloque.s_first_blo
            write_on_inodo = super_bloque.s_inode_start + (ctypes.sizeof(structs.Inodo) * i)
            file.seek(write_on_inodo)
            file.write(ctypes.string_at(ctypes.byref(inodo), ctypes.sizeof(inodo)))

            write_on_block = super_bloque.s_bm_block_start + super_bloque.s_first_blo
            file.seek(write_on_block)
            file.write(b'd')

            super_bloque.s_first_blo = next_first_block(super_bloque, user_session.mounted.path)
            super_bloque.s_free_blocks_count -= 1
            file.seek(user_session.mounted.part_start)
            file.write(ctypes.string_at(ctypes.byref(super_bloque), ctypes.sizeof(super_bloque)))

            file.close()
            return

        
        read_on_file = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * inodo.i_block[b])
        file.seek(read_on_file)
        file.readinto(bcarpeta)
        for j in range(4):
            # print("JAJAJAJAJA")
            # print(bcarpeta.b_content[j].b_inodo)
            if bcarpeta.b_content[j].b_inodo == -1:
                # print(archivo)
                # print(super_bloque.s_first_ino)
                bcarpeta.b_content[j].b_name = archivo.encode('utf-8')[:12].ljust(12, b'\0')
                bcarpeta.b_content[j].b_inodo = super_bloque.s_first_ino
                file.seek(read_on_file)
                file.write(ctypes.string_at(ctypes.byref(bcarpeta), ctypes.sizeof(bcarpeta)))
                file.close()
                return

    file.close()

def write_file(sblock, inodo_file, txt, user_session):
    # print("write_file")
    # print("Bloque libre:", sblock.s_first_blo)
    # print("Inodo libre:", sblock.s_first_ino)
    segmentSize = 63
    totalSegments = len(txt) // segmentSize
    if len(txt) % segmentSize != 0:
        totalSegments += 1
    # print("Total Segments", totalSegments)
    block_archive = structs.BloqueArchivo()
    write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * sblock.s_first_blo)
    file = open(user_session.mounted.path, "rb+")
    write_on_b = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * sblock.s_first_blo)
    write_on_i = sblock.s_inode_start + (ctypes.sizeof(structs.Inodo) * sblock.s_first_ino)
    uno = b'1'
    iterations_blocks = 12 if totalSegments > 12 else totalSegments

    for s in range(iterations_blocks):
        if sblock.s_first_blo == -1:
            # Ya no hay suficientes bloques
            print("Ya no hay suficientes bloques")
            file.close()
            return

        new_segment = txt[s * segmentSize: (s + 1) * segmentSize]
        # BLOQUE DE ARCHIVO CON EL CONTENIDO
        file_user = structs.BloqueArchivo()
        file_user.b_content = new_segment.encode('utf-8')[:64].ljust(64, b'\0')
        # SE ESCRIBE EL BLOQUE DE CONTENIDO
        file.seek(write_on)
        file.write(ctypes.string_at(ctypes.byref(file_user), ctypes.sizeof(file_user)))
        file.seek(write_on)
        file.readinto(block_archive)

        # SE ACTUALIZA EL APUNTADOR DE BLOQUE DEL INODO
        inodo_file.i_block[s] = sblock.s_first_blo
        write_on_b = sblock.s_bm_block_start + sblock.s_first_blo
        file.seek(write_on_b)
        file.write(b'f')

        # SE ACTUALIZA EL APUNTADOR DONDE SE ESCRIBIRÁ EL NUEVO BLOQUE
        sblock.s_first_blo = next_first_block(sblock, user_session.mounted.path)
        write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * sblock.s_first_blo)
        # SE RESTA LA CANTIDAD DE BLOQUES LIBRES
        sblock.s_free_blocks_count -= 1

    # SE ESCRIBE EL NUEVO INODO DEL ARCHIVO
    # print("Se escribe el inodo, ", sblock.s_first_ino)
    # print(inodo_file.i_s)
    write_on_i = sblock.s_inode_start + (ctypes.sizeof(structs.Inodo) * sblock.s_first_ino)
    file.seek(write_on_i)
    file.write(ctypes.string_at(ctypes.byref(inodo_file), ctypes.sizeof(inodo_file)))

    # SE ACTUALIZA EL BITMAP DE INODOS
    write_on_i = sblock.s_bm_inode_start + sblock.s_first_ino
    file.seek(write_on_i)
    file.write(uno)

    # SE ESCRIBE EL NUEVO SUPER BLOQUE
    sblock.s_first_ino = next_first_inodo(sblock, user_session.mounted.path)
    sblock.s_free_inodes_count -= 1
    file.seek(user_session.mounted.part_start)
    file.write(ctypes.string_at(ctypes.byref(sblock), ctypes.sizeof(sblock)))
    file.close()

def write_carpeta(sblock, inodo_file, carpeta_root, user_session):
    file = open(user_session.mounted.path, "rb+")
    write_on_b = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * sblock.s_first_blo)
    file.seek(write_on_b)
    file.write(ctypes.string_at(ctypes.byref(carpeta_root), ctypes.sizeof(carpeta_root)))

    write_on_i = sblock.s_inode_start + (ctypes.sizeof(structs.Inodo) * sblock.s_first_ino)
    file.seek(write_on_i)
    file.write(ctypes.string_at(ctypes.byref(inodo_file), ctypes.sizeof(inodo_file)))

    # SE ACTUALIZA EL BITMAP DE INODOS
    uno = b'1'
    write_on_i = sblock.s_bm_inode_start + sblock.s_first_ino
    file.seek(write_on_i)
    file.write(uno)

    # SE ACTUALIZA EL BITMAP DE INODOS
    write_on_b = sblock.s_bm_block_start + sblock.s_first_blo
    file.seek(write_on_b)
    file.write(b'd')

    # SE ESCRIBE EL NUEVO SUPER BLOQUE
    sblock.s_first_ino = next_first_inodo(sblock, user_session.mounted.path)
    sblock.s_free_inodes_count -= 1
    sblock.s_first_blo = next_first_block(sblock, user_session.mounted.path)
    sblock.s_free_blocks_count -= 1
    file.seek(user_session.mounted.part_start)
    file.write(ctypes.string_at(ctypes.byref(sblock), ctypes.sizeof(sblock)))
    file.close()


def make_ext2(part_size, start, path):

    super_bloque = structs.SuperBloque()
    inodo = structs.Inodo()
    bloque = structs.BloqueCarpeta()
    # print("Peso SuperBloque", ctypes.sizeof(super_bloque))
    # print("Peso Inodo", ctypes.sizeof(inodo))
    # print("Peso BloqueCarpeta", ctypes.sizeof(bloque))

    n = (part_size - ctypes.sizeof(super_bloque)) / (1 + 3 + ctypes.sizeof(inodo) + (3 * ctypes.sizeof(bloque)))
    numero_estructuras = int(math.floor(n))
    print(f"numero_estructuras: {numero_estructuras}")

    super_bloque.s_filesystem_type = 2
    super_bloque.s_inodes_count = super_bloque.s_free_inodes_count = numero_estructuras
    super_bloque.s_blocks_count = super_bloque.s_free_blocks_count = numero_estructuras * 3
    super_bloque.s_mtime = int(time.time())
    super_bloque.s_umtime = int(time.time())
    super_bloque.s_mnt_count = 0
    super_bloque.s_magic = 0xEF53
    super_bloque.s_inode_size = ctypes.sizeof(inodo)
    super_bloque.s_block_size = ctypes.sizeof(bloque)
    super_bloque.s_bm_inode_start = start + ctypes.sizeof(super_bloque)
    super_bloque.s_bm_block_start = super_bloque.s_bm_inode_start + numero_estructuras
    super_bloque.s_inode_start = super_bloque.s_bm_block_start + (3 * numero_estructuras)
    super_bloque.s_block_start = super_bloque.s_inode_start + (numero_estructuras * ctypes.sizeof(inodo))
    super_bloque.s_first_ino = 2
    super_bloque.s_first_blo = 2

    # Escribimos el superbloque en la posicion inicial
    file = open(path, 'rb+')
    file.seek(start)
    file.write(ctypes.string_at(ctypes.byref(super_bloque), ctypes.sizeof(super_bloque)))

    cero = b'0'
    uno = b'1'
    # Ahora escribimos el bitmap de inodos
    file.seek(super_bloque.s_bm_inode_start)
    file.write(cero * super_bloque.s_inodes_count)
    # for i in range(super_bloque.s_inodes_count):
    #     file.write(cero)

    # Ahora escribimos el bitmap de bloques
    file.seek(super_bloque.s_bm_block_start)
    file.write(cero * super_bloque.s_blocks_count)
    # for i in range(super_bloque.s_blocks_count):
    #     file.write(cero)

    # Ahora escribimos los inodos
    file.seek(super_bloque.s_inode_start)
    for i in range(super_bloque.s_inodes_count):
        file.write(ctypes.string_at(ctypes.byref(inodo), ctypes.sizeof(inodo)))
    
    # Ahora escribimos los bloques
    file.seek(super_bloque.s_block_start)
    for i in range(super_bloque.s_blocks_count):
        file.write(ctypes.string_at(ctypes.byref(bloque), ctypes.sizeof(bloque)))

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
    # carpeta_root.b_content[3].b_name = "saber".encode('utf-8')[:12].ljust(12, b'\0')
    # carpeta_root.b_content[3].b_inodo = 4

    data = "1,G,root\n1,U,root,root,123\n"
    inodo_file_user = structs.Inodo()
    inodo_file_user.i_uid = 1
    inodo_file_user.i_gid = 1
    inodo_file_user.i_s = len(data.encode('utf-8'))
    inodo_file_user.i_atime = super_bloque.s_umtime
    inodo_file_user.i_ctime = super_bloque.s_umtime
    inodo_file_user.i_mtime = super_bloque.s_umtime
    inodo_file_user.i_type = b'1'
    inodo_file_user.i_perm = 0o664 # 0o664
    inodo_file_user.i_block[0] = 1

    file_user = structs.BloqueArchivo()
    # print("Peso BloqueArchivo", ctypes.sizeof(file_user))
    file_user.b_content = data.encode('utf-8')[:64].ljust(64, b'\0')

    file.seek(super_bloque.s_bm_inode_start)
    # INODO CARPETA ROOT
    file.write(uno)
    # INODO ARCHIVO USER
    file.write(uno)

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
    print("Se creo el sistema de archivos EXT2 con exito")

class mkfs():
    def __init__(self):
        self.id = ""
        self.type = ""
        self.fs = "2fs"

    def crear_mkfs(self):

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
            make_ext2(particion.part_s, particion.part_start, mounted.path)

        