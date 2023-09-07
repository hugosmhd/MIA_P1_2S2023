import os
import math
import time
import ctypes

import structs
from _global._global import particiones_montadas, session_inciada, users, groups
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

# //////////////////////////////////////
def find_file(super_bloque, path, path_disk, inodo, msg = True):
    read_on_file = -1
    read_on_archive = -1
    directorio, archivo = os.path.split(path)
    carpetas = directorio.split('/')
    print(carpetas)
    print(directorio, archivo)
    if carpetas[0] != '':
        print("Error: Archivo no encontrado, verifique su ruta")
        return
    inodo_archivo = structs.Inodo()

    bcarpeta = structs.BloqueCarpeta()
    file = open(path_disk, 'rb')

    for b in range(12):
        if inodo.i_block[b] == -1:
            continue
        read_on_file = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * inodo.i_block[b])
        file.seek(read_on_file)
        file.readinto(bcarpeta)
        for j in range(4):
            nombre_carpeta = bcarpeta.b_content[j].b_name.decode()
            if nombre_carpeta == archivo:
                read_on_archive = super_bloque.s_inode_start + (ctypes.sizeof(structs.Inodo) * bcarpeta.b_content[j].b_inodo)
                file.seek(read_on_archive)
                file.readinto(inodo_archivo)
                file.close()
                return inodo_archivo, bcarpeta.b_content[j].b_inodo

    if inodo.i_block[12] != -1:
        bloque_s_indirecto = structs.BloqueApuntadores()
        read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo.i_block[12])
        file.seek(read_on_block)
        file.readinto(bloque_s_indirecto)

        for s in range(16):
            if bloque_s_indirecto.b_pointers[s] == -1:
                break

            read_on_file = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * bloque_s_indirecto.b_pointers[s])
            file.seek(read_on_file)
            file.readinto(bcarpeta)

            for j in range(4):
                nombre_carpeta = bcarpeta.b_content[j].b_name.decode()
                if nombre_carpeta == archivo:
                    read_on_archive = super_bloque.s_inode_start + (ctypes.sizeof(structs.Inodo) * bcarpeta.b_content[j].b_inodo)
                    file.seek(read_on_archive)
                    file.readinto(inodo_archivo)
                    file.close()
                    return inodo_archivo, bcarpeta.b_content[j].b_inodo

    if inodo.i_block[13] != -1:
        bloque_d_indirecto = structs.BloqueApuntadores()
        read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo.i_block[13])
        file.seek(read_on_block)
        file.readinto(bloque_d_indirecto)
        for d in range(16):
            if bloque_d_indirecto.b_pointers[d] == -1:
                continue

            bloque_s_indirecto = structs.BloqueApuntadores()
            read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * bloque_d_indirecto.b_pointers[d])
            file.seek(read_on_block)
            file.readinto(bloque_s_indirecto)
            for s in range(16):
                if bloque_s_indirecto.b_pointers[s] == -1:
                    continue

                read_on_file = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * bloque_s_indirecto.b_pointers[s])
                file.seek(read_on_file)
                file.readinto(bcarpeta)

                for j in range(4):
                    nombre_carpeta = bcarpeta.b_content[j].b_name.decode()
                    if nombre_carpeta == archivo:
                        read_on_archive = super_bloque.s_inode_start + (ctypes.sizeof(structs.Inodo) * bcarpeta.b_content[j].b_inodo)
                        file.seek(read_on_archive)
                        file.readinto(inodo_archivo)
                        file.close()
                        return inodo_archivo, bcarpeta.b_content[j].b_inodo

    if inodo.i_block[14] != -1:
        bloque_t_indirecto = structs.BloqueApuntadores()
        read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo.i_block[14])
        file.seek(read_on_block)
        file.readinto(bloque_t_indirecto)

        for t in range(16):
            if bloque_t_indirecto.b_pointers[t] == -1:
                continue

            bloque_d_indirecto = structs.BloqueApuntadores()
            read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * bloque_t_indirecto.b_pointers[t])
            file.seek(read_on_block)
            file.readinto(bloque_d_indirecto)
            for d in range(16):
                if bloque_d_indirecto.b_pointers[d] == -1:
                    continue

                bloque_s_indirecto = structs.BloqueApuntadores()
                read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * bloque_d_indirecto.b_pointers[d])
                file.seek(read_on_block)
                file.readinto(bloque_s_indirecto)
                for s in range(16):
                    if bloque_s_indirecto.b_pointers[s] == -1:
                        continue

                    read_on_file = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * bloque_s_indirecto.b_pointers[s])
                    file.seek(read_on_file)
                    file.readinto(bcarpeta)

                    for j in range(4):
                        nombre_carpeta = bcarpeta.b_content[j].b_name.decode()
                        if nombre_carpeta == archivo:
                            read_on_archive = super_bloque.s_inode_start + (ctypes.sizeof(structs.Inodo) * bcarpeta.b_content[j].b_inodo)
                            file.seek(read_on_archive)
                            file.readinto(inodo_archivo)
                            file.close()
                            return inodo_archivo, bcarpeta.b_content[j].b_inodo

    file.close()
    if msg:
        print("Error: Archivo no encontrado")
    return inodo_archivo, -1

def find_url(super_bloque, path, user_session):
    print("find_url")
    directorio, carpeta_archivo = os.path.split(path)
    # print(carpeta_archivo)
    carpetas = directorio.split('/')

    # Verificar que arranque desde la raiz
    if carpetas[0] != '':
        print("Error archivo no encontrado, verifique su ruta")
        return


    bcarpeta = structs.BloqueCarpeta()
    bcarpeta_actual = structs.BloqueCarpeta()
    inodo = structs.Inodo()
    i_c = 0
    encontrada = False
    file = open(user_session.mounted.path, 'rb+')
    file.seek(super_bloque.s_inode_start)
    file.readinto(inodo)

    if(len(carpetas) >= 2 and carpetas[1] != ''):
        carpetas = carpetas[1:]
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
                        # read_on_file = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * inodo.i_block[b])
                        # file.seek(read_on_file)
                        # file.readinto(bcarpeta_actual)
                        read_on_archive = super_bloque.s_inode_start + (ctypes.sizeof(structs.Inodo) * bcarpeta.b_content[j].b_inodo)
                        file.seek(read_on_archive)
                        file.readinto(inodo)
                        # i_c = j
                        encontrada = True
                        break
                if encontrada:
                    encontrada = False
                    break

    for b in range(12):
        if inodo.i_block[b] == -1:
            continue
        read_on_file = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * inodo.i_block[b])
        file.seek(read_on_file)
        file.readinto(bcarpeta)
        for j in range(4):
            nombre_carpeta = bcarpeta.b_content[j].b_name.decode()
            if nombre_carpeta == carpeta_archivo:
                print("Archivo Carpeta encontrado")
                read_on_file = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * inodo.i_block[b])
                file.seek(read_on_file)
                file.readinto(bcarpeta_actual)
                i_c = j
                file.close()
                return bcarpeta_actual, i_c, read_on_file

    file.close()
    return bcarpeta_actual, i_c, -1

def find_carpeta(super_bloque, path, user_session):
    print("find_carpeta")
    # directorio, carpeta_crear = os.path.split(path)
    carpetas = path.split('/')

    # Verificar que arranque desde la raiz
    if carpetas[0] != '':
        print("Error archivo no encontrado, verifique su ruta")
        return


    bcarpeta = structs.BloqueCarpeta()
    inodo = structs.Inodo()
    i_c = 0
    encontrada = False
    carpeta_encontrada = False
    file = open(user_session.mounted.path, 'rb+')
    file.seek(super_bloque.s_inode_start)
    file.readinto(inodo)

    if(len(carpetas) >= 2 and carpetas[1] != ''):
        carpetas = carpetas[1:]
        for i, carpeta in enumerate(carpetas, start=1):
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
                    carpeta_encontrada = True
                    break
            if not carpeta_encontrada:
                return inodo, -1

    file.close()
    print("Holaaaaaaaaaaaaaaaa Adiossssss", i_c)
    return inodo, i_c

# //////////////////////////////////////
def find_carpeta_archivo(super_bloque, path, user_session, last_file = False):
    print("find_carpeta_archivo")
    carpetas = path.split('/')
    print(carpetas)

    # Verificar que arranque desde la raiz
    if carpetas[0] != '':
        print("Error archivo no encontrado, verifique su ruta")
        return


    bcarpeta = structs.BloqueCarpeta()
    inodo = structs.Inodo()
    i_c = 0
    encontrada = False
    carpeta_encontrada = False
    file = open(user_session.mounted.path, 'rb+')
    file.seek(super_bloque.s_inode_start)
    file.readinto(inodo)

    if(len(carpetas) >= 2 and carpetas[1] != ''):
        carpetas = carpetas[1:]
        for i, carpeta in enumerate(carpetas):
            for b in range(12):
                if inodo.i_block[b] == -1:
                    continue

                read_on_file = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * inodo.i_block[b])
                file.seek(read_on_file)
                file.readinto(bcarpeta)

                for j in range(4):
                    nombre_carpeta = bcarpeta.b_content[j].b_name.decode()
                    if nombre_carpeta == carpeta:
                        i_c = bcarpeta.b_content[j].b_inodo
                        read_on_archive = super_bloque.s_inode_start + (ctypes.sizeof(structs.Inodo) * bcarpeta.b_content[j].b_inodo)
                        file.seek(read_on_archive)
                        file.readinto(inodo)
                        encontrada = True
                        break

                if encontrada:
                    encontrada = False
                    carpeta_encontrada = True
                    break

            if carpeta_encontrada:
                carpeta_encontrada = False
                continue

            # Recorrer el bloque indirecto simple
            if inodo.i_block[12] != -1:
                bloque_s_indirecto = structs.BloqueApuntadores()
                read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo.i_block[12])
                file.seek(read_on_block)
                file.readinto(bloque_s_indirecto)

                for s in range(16):
                    if bloque_s_indirecto.b_pointers[s] == -1:
                        continue

                    read_on_file = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * bloque_s_indirecto.b_pointers[s])
                    file.seek(read_on_file)
                    file.readinto(bcarpeta)

                    for j in range(4):
                        nombre_carpeta = bcarpeta.b_content[j].b_name.decode()
                        if nombre_carpeta == carpeta:
                            i_c = bcarpeta.b_content[j].b_inodo
                            read_on_archive = super_bloque.s_inode_start + (ctypes.sizeof(structs.Inodo) * bcarpeta.b_content[j].b_inodo)
                            file.seek(read_on_archive)
                            file.readinto(inodo)
                            encontrada = True
                            break

                    if encontrada:
                        encontrada = False
                        carpeta_encontrada = True
                        break

            if carpeta_encontrada:
                carpeta_encontrada = False
                continue

            # Recorrer el bloque indirecto doble
            if inodo.i_block[13] != -1:
                bloque_d_indirecto = structs.BloqueApuntadores()
                read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo.i_block[13])
                file.seek(read_on_block)
                file.readinto(bloque_d_indirecto)
                for d in range(16):
                    if bloque_d_indirecto.b_pointers[d] == -1:
                        continue

                    bloque_s_indirecto = structs.BloqueApuntadores()
                    read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * bloque_d_indirecto.b_pointers[d])
                    file.seek(read_on_block)
                    file.readinto(bloque_s_indirecto)
                    for s in range(16):
                        if bloque_s_indirecto.b_pointers[s] == -1:
                            continue

                        read_on_file = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * bloque_s_indirecto.b_pointers[s])
                        file.seek(read_on_file)
                        file.readinto(bcarpeta)

                        for j in range(4):
                            nombre_carpeta = bcarpeta.b_content[j].b_name.decode()
                            if nombre_carpeta == carpeta:
                                i_c = bcarpeta.b_content[j].b_inodo
                                read_on_archive = super_bloque.s_inode_start + (ctypes.sizeof(structs.Inodo) * bcarpeta.b_content[j].b_inodo)
                                file.seek(read_on_archive)
                                file.readinto(inodo)
                                encontrada = True
                                break

                        if encontrada:
                            break
                    
                    if encontrada:
                        encontrada = False
                        carpeta_encontrada = True
                        break

            if carpeta_encontrada:
                carpeta_encontrada = False
                continue

            # Recorrer el bloque indirecto triple
            if inodo.i_block[14] != -1:
                bloque_t_indirecto = structs.BloqueApuntadores()
                read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo.i_block[14])
                file.seek(read_on_block)
                file.readinto(bloque_t_indirecto)

                for t in range(16):
                    if bloque_t_indirecto.b_pointers[t] == -1:
                        continue

                    bloque_d_indirecto = structs.BloqueApuntadores()
                    read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * bloque_t_indirecto.b_pointers[t])
                    file.seek(read_on_block)
                    file.readinto(bloque_d_indirecto)
                    for d in range(16):
                        if bloque_d_indirecto.b_pointers[d] == -1:
                            continue

                        bloque_s_indirecto = structs.BloqueApuntadores()
                        read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * bloque_d_indirecto.b_pointers[d])
                        file.seek(read_on_block)
                        file.readinto(bloque_s_indirecto)
                        for s in range(16):
                            if bloque_s_indirecto.b_pointers[s] == -1:
                                continue

                            read_on_file = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * bloque_s_indirecto.b_pointers[s])
                            file.seek(read_on_file)
                            file.readinto(bcarpeta)

                            for j in range(4):
                                nombre_carpeta = bcarpeta.b_content[j].b_name.decode()
                                if nombre_carpeta == carpeta:
                                    i_c = bcarpeta.b_content[j].b_inodo
                                    read_on_archive = super_bloque.s_inode_start + (ctypes.sizeof(structs.Inodo) * bcarpeta.b_content[j].b_inodo)
                                    file.seek(read_on_archive)
                                    file.readinto(inodo)
                                    encontrada = True
                                    break

                            if encontrada:
                                break
                        
                        if encontrada:
                            break

                    if encontrada:
                        encontrada = False
                        carpeta_encontrada = True
                        break

            if carpeta_encontrada:
                carpeta_encontrada = False
                continue

            if not carpeta_encontrada and not last_file:
                return inodo, -1, False, -1
            elif not carpeta_encontrada and last_file:
                return inodo, i_c, False, carpetas[i:]
            
            carpeta_encontrada = False

                

    file.close()
    return inodo, i_c, True, -1

# //////////////////////////////////////
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
        # print(b)
        if inodo_file.i_block[b] == -1:
            break
        read_on_archive = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * inodo_file.i_block[b])
        file.seek(read_on_archive)
        file.readinto(block_archive)
        txt += block_archive.b_content.decode()
    
    totalSegments -= 12
    # print("totalSegments:", totalSegments)

    if totalSegments > 0:
        if inodo_file.i_block[12] == -1:
            return txt
        print("Entra en el bloque simple indirecto")

        iterations_blocks = min(totalSegments, 16)
        bloque_s_indirecto = structs.BloqueApuntadores()

        read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo_file.i_block[12])
        file.seek(read_on_block)
        file.readinto(bloque_s_indirecto)

        for b in range(iterations_blocks):
            if bloque_s_indirecto.b_pointers[b] == -1:
                break

            read_on_archive = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * bloque_s_indirecto.b_pointers[b])
            file.seek(read_on_archive)
            file.readinto(block_archive)
            txt += block_archive.b_content.decode()

    totalSegments -= 16

    if totalSegments > 0:
        if inodo_file.i_block[13] == -1:
            return txt

        print("Entra en el bloque doble indirecto")

        iterations_blocks = min(totalSegments, 256)
        iterations_db = iterations_blocks // 16

        if iterations_blocks % 16 != 0:
            iterations_db += 1

        bloque_doble = structs.BloqueApuntadores()

        read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo_file.i_block[13])
        file.seek(read_on_block)
        file.readinto(bloque_doble)

        for d in range(iterations_db):
            bloque_simple = structs.BloqueApuntadores()
            read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * bloque_doble.b_pointers[d])
            file.seek(read_on_block)
            file.readinto(bloque_simple)

            for s in range(16):
                if bloque_simple.b_pointers[s] == -1:
                    break

                read_on_archive = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * bloque_simple.b_pointers[s])
                file.seek(read_on_archive)
                block_archive = structs.BloqueArchivo()
                file.readinto(block_archive)

                # print("join file:")
                txt += block_archive.b_content.decode()

    totalSegments -= 256

    if totalSegments > 0:
        if inodo_file.i_block[14] == -1:
            return txt

        print("Entra en el bloque triple indirecto")

        iterations_blocks = min(totalSegments, 4096)
        iterations_tb = iterations_blocks // 256

        if iterations_blocks % 256 != 0:
            iterations_tb += 1

        bloque_triple = structs.BloqueApuntadores()

        read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo_file.i_block[14])
        file.seek(read_on_block)
        file.readinto(bloque_triple)

        for t in range(iterations_tb):
            bloque_doble = structs.BloqueApuntadores()
            read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * bloque_triple.b_pointers[t])
            file.seek(read_on_block)
            file.readinto(bloque_doble)
            for d in range(16):
                if bloque_doble.b_pointers[d] == -1:
                    break

                bloque_simple = structs.BloqueApuntadores()
                read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * bloque_doble.b_pointers[d])
                file.seek(read_on_block)
                file.readinto(bloque_simple)

                for s in range(16):
                    if bloque_simple.b_pointers[s] == -1:
                        break

                    read_on_archive = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * bloque_simple.b_pointers[s])
                    file.seek(read_on_archive)
                    block_archive = structs.BloqueArchivo()
                    file.readinto(block_archive)

                    # print("join file:")
                    txt += block_archive.b_content.decode()


    file.close()
    return txt

def file_link_move(super_bloque, name, user_session, inodo, i_o, i_d):
    print("file_link_move")
    read_on_file = -1
    read_on_archive = -1
    write_on_inodo = -1
    write_on_block = -1
    # directorio, archivo = os.path.split(path)
    # carpetas = directorio.split('/')

    # Verificar que arranque desde la raiz
    # if carpetas[0] != '':
    #     print("Error archivo no encontrado, verifique su ruta")
    #     return

    file = open(user_session.mounted.path, 'rb+')

    bcarpeta = structs.BloqueCarpeta()
    uno = b'1'
    for b in range(12):
        if inodo.i_block[b] == -1:
            if super_bloque.s_first_blo == -1:
                # YA NO HAY MÁS BLOQUES PARA CREAR
                print("No hay mas bloques desde MKFS")
                return

            carpeta = structs.BloqueCarpeta()
            carpeta.b_content[0].b_name = name
            carpeta.b_content[0].b_inodo = i_o # aqui seria colocar el numero de inodo que te manden
            write_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * super_bloque.s_first_blo)
            file.seek(write_on_block)
            file.write(ctypes.string_at(ctypes.byref(carpeta), ctypes.sizeof(carpeta)))

            inodo.i_block[b] = super_bloque.s_first_blo 
            write_on_inodo = super_bloque.s_inode_start + (ctypes.sizeof(structs.Inodo) * i_d)
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
            if bcarpeta.b_content[j].b_inodo == -1:
                bcarpeta.b_content[j].b_name = name
                bcarpeta.b_content[j].b_inodo = i_o
                file.seek(read_on_file)
                file.write(ctypes.string_at(ctypes.byref(bcarpeta), ctypes.sizeof(bcarpeta)))
                file.close()
                return

    file.close()

# //////////////////////////////////////
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

    bcarpeta = structs.BloqueCarpeta()
    uno = b'1'
    print("Se recorre bloques directos")
    # for b in range(12):
    #     if inodo.i_block[b] == -1:
    #         if super_bloque.s_first_blo == -1:
    #             # YA NO HAY MÁS BLOQUES PARA CREAR
    #             print("Error: No hay mas bloques desde MKFS")
    #             file.close()
    #             return
    #         carpeta = structs.BloqueCarpeta()
    #         carpeta.b_content[0].b_name = archivo.encode('utf-8')[:12].ljust(12, b'\0')
    #         carpeta.b_content[0].b_inodo = super_bloque.s_first_ino
    #         write_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * super_bloque.s_first_blo)
    #         file.seek(write_on_block)
    #         file.write(ctypes.string_at(ctypes.byref(carpeta), ctypes.sizeof(carpeta)))

    #         inodo.i_block[b] = super_bloque.s_first_blo
    #         write_on_inodo = super_bloque.s_inode_start + (ctypes.sizeof(structs.Inodo) * i)
    #         file.seek(write_on_inodo)
    #         file.write(ctypes.string_at(ctypes.byref(inodo), ctypes.sizeof(inodo)))

    #         write_on_block = super_bloque.s_bm_block_start + super_bloque.s_first_blo
    #         file.seek(write_on_block)
    #         file.write(b'd')

    #         super_bloque.s_first_blo = next_first_block(super_bloque, user_session.mounted.path)
    #         super_bloque.s_free_blocks_count -= 1
    #         file.seek(user_session.mounted.part_start)
    #         file.write(ctypes.string_at(ctypes.byref(super_bloque), ctypes.sizeof(super_bloque)))

    #         file.close()
    #         return
        
    #     read_on_file = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * inodo.i_block[b])
    #     file.seek(read_on_file)
    #     file.readinto(bcarpeta)
    #     for j in range(4):
    #         if bcarpeta.b_content[j].b_inodo == -1:
    #             bcarpeta.b_content[j].b_name = archivo.encode('utf-8')[:12].ljust(12, b'\0')
    #             bcarpeta.b_content[j].b_inodo = super_bloque.s_first_ino
    #             file.seek(read_on_file)
    #             file.write(ctypes.string_at(ctypes.byref(bcarpeta), ctypes.sizeof(bcarpeta)))
    #             file.close()
    #             return

    # print("Se recorre primer bloque indirecto simple")
    # if inodo.i_block[12] == -1:
    #     inodo.i_block[12] = super_bloque.s_first_blo
    #     write_on_inodo = super_bloque.s_inode_start + (ctypes.sizeof(structs.Inodo) * i)
    #     file.seek(write_on_inodo)
    #     file.write(ctypes.string_at(ctypes.byref(inodo), ctypes.sizeof(inodo)))

    #     bloque_s_indirecto = structs.BloqueApuntadores()
    #     write_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo.i_block[12])
    #     file.seek(write_on_block)
    #     file.write(ctypes.string_at(ctypes.byref(bloque_s_indirecto), ctypes.sizeof(bloque_s_indirecto)))

    #     write_on_block = super_bloque.s_bm_block_start + inodo.i_block[12]
    #     file.seek(write_on_block)
    #     file.write(b's')

    #     super_bloque.s_first_blo = next_first_block(super_bloque, user_session.mounted.path)
    #     super_bloque.s_free_blocks_count -= 1

    # print("Entra en el bloque simple indirecto")
    # bloque_s_indirecto = structs.BloqueApuntadores()

    # read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo.i_block[12])
    # file.seek(read_on_block)
    # file.readinto(bloque_s_indirecto)

    # for b in range(16):
    #     if bloque_s_indirecto.b_pointers[b] == -1:
    #         if super_bloque.s_first_blo == -1:
    #             # YA NO HAY MÁS BLOQUES PARA CREAR
    #             print("Error: No hay mas bloques desde MKFS")
    #             file.close()
    #             return

    #         carpeta = structs.BloqueCarpeta()
    #         carpeta.b_content[0].b_name = archivo.encode('utf-8')[:12].ljust(12, b'\0')
    #         carpeta.b_content[0].b_inodo = super_bloque.s_first_ino
    #         write_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * super_bloque.s_first_blo)
    #         file.seek(write_on_block)
    #         file.write(ctypes.string_at(ctypes.byref(carpeta), ctypes.sizeof(carpeta)))

    #         bloque_s_indirecto.b_pointers[b] = super_bloque.s_first_blo
    #         write_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo.i_block[12])
    #         file.seek(write_on_block)
    #         file.write(ctypes.string_at(ctypes.byref(bloque_s_indirecto), ctypes.sizeof(bloque_s_indirecto)))

    #         write_on_block = super_bloque.s_bm_block_start + super_bloque.s_first_blo
    #         file.seek(write_on_block)
    #         file.write(b'd')

    #         super_bloque.s_first_blo = next_first_block(super_bloque, user_session.mounted.path)
    #         super_bloque.s_free_blocks_count -= 1
    #         file.seek(user_session.mounted.part_start)
    #         file.write(ctypes.string_at(ctypes.byref(super_bloque), ctypes.sizeof(super_bloque)))

    #         file.close()
    #         return

    #     read_on_file = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * bloque_s_indirecto.b_pointers[b])
    #     file.seek(read_on_file)
    #     file.readinto(bcarpeta)
    #     for j in range(4):
    #         if bcarpeta.b_content[j].b_inodo == -1:
    #             bcarpeta.b_content[j].b_name = archivo.encode('utf-8')[:12].ljust(12, b'\0')
    #             bcarpeta.b_content[j].b_inodo = super_bloque.s_first_ino
    #             file.seek(read_on_file)
    #             file.write(ctypes.string_at(ctypes.byref(bcarpeta), ctypes.sizeof(bcarpeta)))
    #             file.close()
    #             return

    # -----------------------------------------------------------------------------------
    # print("Se recorre segundo bloque indirecto doble")
    # if inodo.i_block[13] == -1:
    #     inodo.i_block[13] = super_bloque.s_first_blo
    #     write_on_inodo = super_bloque.s_inode_start + (ctypes.sizeof(structs.Inodo) * i)
    #     file.seek(write_on_inodo)
    #     file.write(ctypes.string_at(ctypes.byref(inodo), ctypes.sizeof(inodo)))

    #     bloque_doble = structs.BloqueApuntadores()
    #     write_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo.i_block[13])
    #     file.seek(write_on_block)
    #     file.write(ctypes.string_at(ctypes.byref(bloque_doble), ctypes.sizeof(bloque_doble)))

    #     write_on_block = super_bloque.s_bm_block_start + inodo.i_block[13]
    #     file.seek(write_on_block)
    #     file.write(b'l')

    #     super_bloque.s_first_blo = next_first_block(super_bloque, user_session.mounted.path)
    #     super_bloque.s_free_blocks_count -= 1

    # print("Entra en el bloque doble indirecto")
    # bloque_doble = structs.BloqueApuntadores()

    # read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo.i_block[13])
    # file.seek(read_on_block)
    # file.readinto(bloque_doble)

    # for d in range(16):
    #     bloque_simple = structs.BloqueApuntadores()
    #     if bloque_doble.b_pointers[d] == -1:
    #         bloque_doble.b_pointers[d] = super_bloque.s_first_blo
    #         super_bloque.s_first_blo = next_first_block(super_bloque, user_session.mounted.path)
    #         super_bloque.s_free_blocks_count -= 1
            
    #         write_on_block = super_bloque.s_bm_block_start + bloque_doble.b_pointers[d]
    #         file.seek(write_on_block)
    #         file.write(b's')

    #         write_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * inodo.i_block[13])
    #         file.seek(write_on_block)
    #         file.write(ctypes.string_at(ctypes.byref(bloque_doble), ctypes.sizeof(bloque_doble)))
    #     else:
    #         read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * bloque_doble.b_pointers[d])
    #         file.seek(read_on_block)
    #         file.readinto(bloque_simple)

    #     for s in range(16):
    #         if bloque_simple.b_pointers[s] == -1:
    #             if super_bloque.s_first_blo == -1:
    #                 # YA NO HAY MÁS BLOQUES PARA CREAR
    #                 print("Error: No hay mas bloques desde MKFS")
    #                 file.close()
    #                 return

    #             carpeta = structs.BloqueCarpeta()
    #             carpeta.b_content[0].b_name = archivo.encode('utf-8')[:12].ljust(12, b'\0')
    #             carpeta.b_content[0].b_inodo = super_bloque.s_first_ino
    #             write_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * super_bloque.s_first_blo)
    #             file.seek(write_on_block)
    #             file.write(ctypes.string_at(ctypes.byref(carpeta), ctypes.sizeof(carpeta)))

    #             bloque_simple.b_pointers[s] = super_bloque.s_first_blo
    #             write_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * bloque_doble.b_pointers[d])
    #             file.seek(write_on_block)
    #             file.write(ctypes.string_at(ctypes.byref(bloque_simple), ctypes.sizeof(bloque_simple)))

    #             write_on_block = super_bloque.s_bm_block_start + super_bloque.s_first_blo
    #             file.seek(write_on_block)
    #             file.write(b'd')

    #             super_bloque.s_first_blo = next_first_block(super_bloque, user_session.mounted.path)
    #             super_bloque.s_free_blocks_count -= 1
    #             file.seek(user_session.mounted.part_start)
    #             file.write(ctypes.string_at(ctypes.byref(super_bloque), ctypes.sizeof(super_bloque)))
    #             file.close()
    #             return

    #         read_on_file = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * bloque_simple.b_pointers[s])
    #         file.seek(read_on_file)
    #         file.readinto(bcarpeta)
    #         for j in range(4):
    #             if bcarpeta.b_content[j].b_inodo == -1:
    #                 bcarpeta.b_content[j].b_name = archivo.encode('utf-8')[:12].ljust(12, b'\0')
    #                 bcarpeta.b_content[j].b_inodo = super_bloque.s_first_ino
    #                 file.seek(read_on_file)
    #                 file.write(ctypes.string_at(ctypes.byref(bcarpeta), ctypes.sizeof(bcarpeta)))
    #                 file.close()
    #                 return

    # -----------------------------------------------------------------------------------
    print("Se recorre tercer bloque indirecto triple")
    if inodo.i_block[14] == -1:
        inodo.i_block[14] = super_bloque.s_first_blo
        write_on_inodo = super_bloque.s_inode_start + (ctypes.sizeof(structs.Inodo) * i)
        file.seek(write_on_inodo)
        file.write(ctypes.string_at(ctypes.byref(inodo), ctypes.sizeof(inodo)))

        bloque_doble = structs.BloqueApuntadores()
        write_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo.i_block[14])
        file.seek(write_on_block)
        file.write(ctypes.string_at(ctypes.byref(bloque_doble), ctypes.sizeof(bloque_doble)))

        write_on_block = super_bloque.s_bm_block_start + inodo.i_block[14]
        file.seek(write_on_block)
        file.write(b't')

        super_bloque.s_first_blo = next_first_block(super_bloque, user_session.mounted.path)
        super_bloque.s_free_blocks_count -= 1

    print("Entra en el bloque triple indirecto")
    bloque_triple = structs.BloqueApuntadores()

    read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo.i_block[14])
    file.seek(read_on_block)
    file.readinto(bloque_triple)

    for t in range(16):
        bloque_doble = structs.BloqueApuntadores()
        if bloque_triple.b_pointers[t] == -1:
            bloque_triple.b_pointers[t] = super_bloque.s_first_blo
            super_bloque.s_first_blo = next_first_block(super_bloque, user_session.mounted.path)
            super_bloque.s_free_blocks_count -= 1
            
            write_on_block = super_bloque.s_bm_block_start + bloque_triple.b_pointers[t]
            file.seek(write_on_block)
            file.write(b'l')

            write_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * inodo.i_block[14])
            file.seek(write_on_block)
            file.write(ctypes.string_at(ctypes.byref(bloque_triple), ctypes.sizeof(bloque_triple)))
        else:
            read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * bloque_triple.b_pointers[t])
            file.seek(read_on_block)
            file.readinto(bloque_doble)
        for d in range(16):
            bloque_simple = structs.BloqueApuntadores()
            if bloque_doble.b_pointers[d] == -1:
                bloque_doble.b_pointers[d] = super_bloque.s_first_blo
                super_bloque.s_first_blo = next_first_block(super_bloque, user_session.mounted.path)
                super_bloque.s_free_blocks_count -= 1
                
                write_on_block = super_bloque.s_bm_block_start + bloque_doble.b_pointers[d]
                file.seek(write_on_block)
                file.write(b's')

                write_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * bloque_triple.b_pointers[t])
                file.seek(write_on_block)
                file.write(ctypes.string_at(ctypes.byref(bloque_doble), ctypes.sizeof(bloque_doble)))
            else:
                read_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * bloque_doble.b_pointers[d])
                file.seek(read_on_block)
                file.readinto(bloque_simple)

            for s in range(16):
                if bloque_simple.b_pointers[s] == -1:
                    if super_bloque.s_first_blo == -1:
                        # YA NO HAY MÁS BLOQUES PARA CREAR
                        print("Error: No hay mas bloques desde MKFS")
                        file.close()
                        return

                    carpeta = structs.BloqueCarpeta()
                    carpeta.b_content[0].b_name = archivo.encode('utf-8')[:12].ljust(12, b'\0')
                    carpeta.b_content[0].b_inodo = super_bloque.s_first_ino
                    write_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * super_bloque.s_first_blo)
                    file.seek(write_on_block)
                    file.write(ctypes.string_at(ctypes.byref(carpeta), ctypes.sizeof(carpeta)))

                    bloque_simple.b_pointers[s] = super_bloque.s_first_blo
                    write_on_block = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * bloque_doble.b_pointers[d])
                    file.seek(write_on_block)
                    file.write(ctypes.string_at(ctypes.byref(bloque_simple), ctypes.sizeof(bloque_simple)))

                    write_on_block = super_bloque.s_bm_block_start + super_bloque.s_first_blo
                    file.seek(write_on_block)
                    file.write(b'd')

                    super_bloque.s_first_blo = next_first_block(super_bloque, user_session.mounted.path)
                    super_bloque.s_free_blocks_count -= 1
                    file.seek(user_session.mounted.part_start)
                    file.write(ctypes.string_at(ctypes.byref(super_bloque), ctypes.sizeof(super_bloque)))
                    file.close()
                    return

                read_on_file = super_bloque.s_block_start + (ctypes.sizeof(structs.BloqueCarpeta) * bloque_simple.b_pointers[s])
                file.seek(read_on_file)
                file.readinto(bcarpeta)
                for j in range(4):
                    if bcarpeta.b_content[j].b_inodo == -1:
                        bcarpeta.b_content[j].b_name = archivo.encode('utf-8')[:12].ljust(12, b'\0')
                        bcarpeta.b_content[j].b_inodo = super_bloque.s_first_ino
                        file.seek(read_on_file)
                        file.write(ctypes.string_at(ctypes.byref(bcarpeta), ctypes.sizeof(bcarpeta)))
                        file.close()
                        return


    file.close()

def directory_link_r(super_bloque, path, user_session, inodo, i):
    read_on_file = -1
    read_on_archive = -1
    write_on_inodo = -1
    write_on_block = -1
    # directorio, archivo = os.path.split(path)
    # carpetas = directorio.split('/')

    # Verificar que arranque desde la raiz
    # if carpetas[0] != '':
    #     print("Error archivo no encontrado, verifique su ruta")
    #     return

    file = open(user_session.mounted.path, 'rb+')

    bcarpeta = structs.BloqueCarpeta()
    uno = b'1'
    for b in range(12):
        if inodo.i_block[b] == -1:
            if super_bloque.s_first_blo == -1:
                # YA NO HAY MÁS BLOQUES PARA CREAR
                print("No hay mas bloques desde MKFS")
                return

            carpeta = structs.BloqueCarpeta()
            carpeta.b_content[0].b_name = path.encode('utf-8')[:12].ljust(12, b'\0')
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
            if bcarpeta.b_content[j].b_inodo == -1:
                bcarpeta.b_content[j].b_name = path.encode('utf-8')[:12].ljust(12, b'\0')
                bcarpeta.b_content[j].b_inodo = super_bloque.s_first_ino
                file.seek(read_on_file)
                file.write(ctypes.string_at(ctypes.byref(bcarpeta), ctypes.sizeof(bcarpeta)))
                file.close()
                return

    file.close()

# //////////////////////////////////////
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
            print("Error: Ya no hay suficientes bloques")
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

    totalSegments -= 12
    if totalSegments > 0:
        if sblock.s_first_blo == -1:
            # Ya no hay suficientes bloques
            print("Error: Ya no hay suficientes bloques")
            file.close()
            return
        print("Se escribe el primer bloque indirecto simple")
        iterations_blocks = 16 if totalSegments > 16 else totalSegments
        bloque_simple = structs.BloqueApuntadores()
        inodo_file.i_block[12] = sblock.s_first_blo
        sblock.s_first_blo = next_first_block(sblock, user_session.mounted.path)
        write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * sblock.s_first_blo)
        # SE RESTA LA CANTIDAD DE BLOQUES LIBRES
        sblock.s_free_blocks_count -= 1

        for s in range(iterations_blocks):
            if sblock.s_first_blo == -1:
                # Ya no hay suficientes bloques
                print("Error: Ya no hay suficientes bloques")
                file.close()
                return

            new_segment = txt[(s + 12) * segmentSize : (s + 13) * segmentSize]
            # BLOQUE DE ARCHIVO CON EL CONTENIDO
            file_user = structs.BloqueArchivo()
            file_user.b_content = new_segment.encode('utf-8')[:64].ljust(64, b'\0')
            # SE ESCRIBE EL BLOQUE DE CONTENIDO
            file.seek(write_on)
            file.write(ctypes.string_at(ctypes.byref(file_user), ctypes.sizeof(file_user)))

            # SE ACTUALIZA EL APUNTADOR DE BLOQUE DEL BLOQUE SIMPLE
            bloque_simple.b_pointers[s] = sblock.s_first_blo
            write_on_b = sblock.s_bm_block_start + (sblock.s_first_blo)
            file.seek(write_on_b)
            file.write(b'f')

            # SE ACTUALIZA EL APUNTADOR DONDE SE ESCRIBIRÁ EL NUEVO BLOQUE
            sblock.s_first_blo = next_first_block(sblock, user_session.mounted.path)
            write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * sblock.s_first_blo)
            # SE RESTA LA CANTIDAD DE BLOQUES LIBRES
            sblock.s_free_blocks_count -= 1
        
        write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo_file.i_block[12])
        file.seek(write_on)
        file.write(ctypes.string_at(ctypes.byref(bloque_simple), ctypes.sizeof(bloque_simple)))

        write_on_b = sblock.s_bm_block_start + inodo_file.i_block[12]
        file.seek(write_on_b)
        file.write(b's')
    
    totalSegments -= 16
    if totalSegments > 0:
        if sblock.s_first_blo == -1:
            # Ya no hay suficientes bloques
            print("Error: Ya no hay suficientes bloques")
            file.close()
            return
        print("Se escribe el segundo bloque indirecto doble")
        iterations_blocks = 256 if totalSegments > 256 else totalSegments
        iterations_db = iterations_blocks // 16  # División entera para calcular el número de dobles bloques

        if iterations_blocks % 16 != 0:
            iterations_db += 1
        print("iterations_blocks:", iterations_blocks)
        print("iterations_db:", iterations_db)

        bloque_doble = structs.BloqueApuntadores()
        inodo_file.i_block[13] = sblock.s_first_blo
        write_on_db = -1
        sblock.s_first_blo = next_first_block(sblock, user_session.mounted.path)
        sblock.s_free_blocks_count -= 1

        for d in range(iterations_db):
            bloque_doble.b_pointers[d] = sblock.s_first_blo
            sblock.s_first_blo = next_first_block(sblock, user_session.mounted.path)
            sblock.s_free_blocks_count -= 1
            write_on_db = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * sblock.s_first_blo)
            bloque_simple = structs.BloqueApuntadores()
            for s in range(16):
                new_segment = txt[(s + 28 + (d * 16)) * segmentSize : (s + 29 + (d * 16)) * segmentSize]
                file_user = structs.BloqueArchivo()
                file_user.b_content = new_segment.encode('utf-8')[:64].ljust(64, b'\0')
                # SE ESCRIBE EL BLOQUE DE CONTENIDO
                file.seek(write_on_db)
                file.write(ctypes.string_at(ctypes.byref(file_user), ctypes.sizeof(file_user)))

                # SE ACTUALIZA EL APUNTADOR DE BLOQUE DEL INODO
                bloque_simple.b_pointers[s] = sblock.s_first_blo
                write_on_b = sblock.s_bm_block_start + sblock.s_first_blo
                file.seek(write_on_b)
                file.write(b'f')

                # SE ACTUALIZA EL APUNTADOR DONDE SE ESCRIBIRÁ EL NUEVO BLOQUE
                sblock.s_first_blo = next_first_block(sblock, user_session.mounted.path)
                write_on_db = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * sblock.s_first_blo)

                # SE RESTA LA CANTIDAD DE BLOQUES LIBRES
                sblock.s_free_blocks_count -= 1
                totalSegments -= 1

                if totalSegments == 0:
                    break

            write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * bloque_doble.b_pointers[d])
            file.seek(write_on)
            file.write(bloque_simple)

            write_on_b = sblock.s_bm_block_start + bloque_doble.b_pointers[d]
            file.seek(write_on_b)
            file.write(b's')
        
        write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo_file.i_block[13])
        file.seek(write_on)
        file.write(ctypes.string_at(ctypes.byref(bloque_doble), ctypes.sizeof(bloque_doble)))

        write_on_b = sblock.s_bm_block_start + inodo_file.i_block[13]
        file.seek(write_on_b)
        file.write(b'l')
        # /////////////////////////////////////////////////////////

        # bloque_simple = structs.BloqueApuntadores()
        # inodo_file.i_block[12] = sblock.s_first_blo
        # sblock.s_first_blo = next_first_block(sblock, user_session.mounted.path)
        # write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * sblock.s_first_blo)
        # # SE RESTA LA CANTIDAD DE BLOQUES LIBRES
        # sblock.s_free_blocks_count -= 1

        # for s in range(iterations_blocks):
        #     if sblock.s_first_blo == -1:
        #         # Ya no hay suficientes bloques
        #         print("Error: Ya no hay suficientes bloques")
        #         file.close()
        #         return

        #     new_segment = txt[(s + 12) * segmentSize : (s + 13) * segmentSize]
        #     # BLOQUE DE ARCHIVO CON EL CONTENIDO
        #     file_user = structs.BloqueArchivo()
        #     file_user.b_content = new_segment.encode('utf-8')[:64].ljust(64, b'\0')
        #     # SE ESCRIBE EL BLOQUE DE CONTENIDO
        #     file.seek(write_on)
        #     file.write(ctypes.string_at(ctypes.byref(file_user), ctypes.sizeof(file_user)))

        #     # SE ACTUALIZA EL APUNTADOR DE BLOQUE DEL BLOQUE SIMPLE
        #     bloque_simple.b_pointers[s] = sblock.s_first_blo
        #     write_on_b = sblock.s_bm_block_start + (sblock.s_first_blo)
        #     file.seek(write_on_b)
        #     file.write(b'f')

        #     # SE ACTUALIZA EL APUNTADOR DONDE SE ESCRIBIRÁ EL NUEVO BLOQUE
        #     sblock.s_first_blo = next_first_block(sblock, user_session.mounted.path)
        #     write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * sblock.s_first_blo)
        #     # SE RESTA LA CANTIDAD DE BLOQUES LIBRES
        #     sblock.s_free_blocks_count -= 1
        
        # write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo_file.i_block[12])
        # file.seek(write_on)
        # file.write(ctypes.string_at(ctypes.byref(bloque_simple), ctypes.sizeof(bloque_simple)))

        # write_on_b = sblock.s_bm_block_start + inodo_file.i_block[12]
        # file.seek(write_on_b)
        # file.write(b's')

        # /////////////////////////////////////////////////////////
    
    # totalSegments -= 256
    if totalSegments > 0:
        if sblock.s_first_blo == -1:
            # Ya no hay suficientes bloques
            print("Error: Ya no hay suficientes bloques")
            file.close()
            return
        # 512 bloques
        # 32256 caracteres
        print("Se escribe el tercer bloque indirecto tripe")
        iterations_blocks = 4096 if totalSegments > 4096 else totalSegments
        iterations_tb = iterations_blocks // 256  # División entera para calcular el número de dobles bloques

        if iterations_blocks % 256 != 0:
            iterations_tb += 1

        print("iterations_blocks:", iterations_blocks)
        print("iterations_tb:", iterations_tb)

        bloque_triple = structs.BloqueApuntadores()
        inodo_file.i_block[14] = sblock.s_first_blo
        write_on_db = -1
        sblock.s_first_blo = next_first_block(sblock, user_session.mounted.path)
        sblock.s_free_blocks_count -= 1

        for t in range(iterations_tb):
            bloque_triple.b_pointers[t] = sblock.s_first_blo
            sblock.s_first_blo = next_first_block(sblock, user_session.mounted.path)
            sblock.s_free_blocks_count -= 1
            write_on_db = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * sblock.s_first_blo)
            bloque_doble = structs.BloqueApuntadores()
            for d in range(16):
                bloque_doble.b_pointers[d] = sblock.s_first_blo
                sblock.s_first_blo = next_first_block(sblock, user_session.mounted.path)
                sblock.s_free_blocks_count -= 1
                write_on_db = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * sblock.s_first_blo)
                bloque_simple = structs.BloqueApuntadores()
                for s in range(16):
                    new_segment = txt[(s + 284 + (d * 16) + (t * 256)) * segmentSize : (s + 285 + (d * 16) + (t * 256)) * segmentSize]
                    file_user = structs.BloqueArchivo()
                    file_user.b_content = new_segment.encode('utf-8')[:64].ljust(64, b'\0')
                    # SE ESCRIBE EL BLOQUE DE CONTENIDO
                    file.seek(write_on_db)
                    file.write(ctypes.string_at(ctypes.byref(file_user), ctypes.sizeof(file_user)))

                    # SE ACTUALIZA EL APUNTADOR DE BLOQUE DEL INODO
                    bloque_simple.b_pointers[s] = sblock.s_first_blo
                    write_on_b = sblock.s_bm_block_start + sblock.s_first_blo
                    file.seek(write_on_b)
                    file.write(b'f')

                    # SE ACTUALIZA EL APUNTADOR DONDE SE ESCRIBIRÁ EL NUEVO BLOQUE
                    sblock.s_first_blo = next_first_block(sblock, user_session.mounted.path)
                    write_on_db = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * sblock.s_first_blo)

                    # SE RESTA LA CANTIDAD DE BLOQUES LIBRES
                    sblock.s_free_blocks_count -= 1
                    totalSegments -= 1

                    if totalSegments == 0:
                        break

                write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * bloque_doble.b_pointers[d])
                file.seek(write_on)
                file.write(bloque_simple)

                write_on_b = sblock.s_bm_block_start + bloque_doble.b_pointers[d]
                file.seek(write_on_b)
                file.write(b's')

                if totalSegments == 0:
                    break
        
            write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * bloque_triple.b_pointers[t])
            file.seek(write_on)
            file.write(ctypes.string_at(ctypes.byref(bloque_doble), ctypes.sizeof(bloque_doble)))

            write_on_b = sblock.s_bm_block_start + bloque_triple.b_pointers[t]
            file.seek(write_on_b)
            file.write(b'l')

        write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo_file.i_block[14])
        file.seek(write_on)
        file.write(ctypes.string_at(ctypes.byref(bloque_triple), ctypes.sizeof(bloque_triple)))

        write_on_b = sblock.s_bm_block_start + inodo_file.i_block[14]
        file.seek(write_on_b)
        file.write(b't')


        # /////////////////////////////////////////////////////////
        # print("Se escribe el tercer bloque indirecto tripe")
        # iterations_blocks = 4096 if totalSegments > 4096 else totalSegments
        # iterations_db = iterations_blocks // 16  # División entera para calcular el número de dobles bloques

        # if iterations_blocks % 16 != 0:
        #     iterations_db += 1
        # print("iterations_blocks:", iterations_blocks)
        # print("iterations_db:", iterations_db)

        # bloque_doble = structs.BloqueApuntadores()
        # inodo_file.i_block[13] = sblock.s_first_blo
        # write_on_db = -1
        # sblock.s_first_blo = next_first_block(sblock, user_session.mounted.path)
        # sblock.s_free_blocks_count -= 1

        # for d in range(iterations_db):
        #     bloque_doble.b_pointers[d] = sblock.s_first_blo
        #     sblock.s_first_blo = next_first_block(sblock, user_session.mounted.path)
        #     sblock.s_free_blocks_count -= 1
        #     write_on_db = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * sblock.s_first_blo)
        #     bloque_simple = structs.BloqueApuntadores()
        #     for s in range(16):
        #         new_segment = txt[(s + 28 + (d * 16)) * segmentSize : (s + 29 + (d * 16)) * segmentSize]
        #         file_user = structs.BloqueArchivo()
        #         file_user.b_content = new_segment.encode('utf-8')[:64].ljust(64, b'\0')
        #         # SE ESCRIBE EL BLOQUE DE CONTENIDO
        #         file.seek(write_on_db)
        #         file.write(ctypes.string_at(ctypes.byref(file_user), ctypes.sizeof(file_user)))

        #         # SE ACTUALIZA EL APUNTADOR DE BLOQUE DEL INODO
        #         bloque_simple.b_pointers[s] = sblock.s_first_blo
        #         write_on_b = sblock.s_bm_block_start + sblock.s_first_blo
        #         file.seek(write_on_b)
        #         file.write(b'f')

        #         # SE ACTUALIZA EL APUNTADOR DONDE SE ESCRIBIRÁ EL NUEVO BLOQUE
        #         sblock.s_first_blo = next_first_block(sblock, user_session.mounted.path)
        #         write_on_db = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * sblock.s_first_blo)

        #         # SE RESTA LA CANTIDAD DE BLOQUES LIBRES
        #         sblock.s_free_blocks_count -= 1
        #         totalSegments -= 1

        #         if totalSegments == 0:
        #             break

        #     write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * bloque_doble.b_pointers[d])
        #     file.seek(write_on)
        #     file.write(bloque_simple)

        #     write_on_b = sblock.s_bm_block_start + bloque_doble.b_pointers[d]
        #     file.seek(write_on_b)
        #     file.write(b's')
        
        # write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueApuntadores) * inodo_file.i_block[13])
        # file.seek(write_on)
        # file.write(ctypes.string_at(ctypes.byref(bloque_doble), ctypes.sizeof(bloque_doble)))

        # write_on_b = sblock.s_bm_block_start + inodo_file.i_block[13]
        # file.seek(write_on_b)
        # file.write(b'l')

        # /////////////////////////////////////////////////////////
    
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

# //////////////////////////////////////
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

def crear_grupo_usuario(sblock, data, name_g_u, tipo, user_actual = None):
    indo_carpeta_archivo, i, _, __ = find_carpeta_archivo(sblock, "/", session_inciada)
    if(i == -1):
        print(f"Error: Ruta especificada '{self.path}' no existe")
        return
    inodo_archivo, i_ino = find_file(sblock, "/user.txt", session_inciada.mounted.path, indo_carpeta_archivo)
    if(i_ino == -1):
        print(f"Error: Ruta especificada '/user.txt' no existe")
        return
    txt = join_file(sblock, inodo_archivo, session_inciada.mounted.path)

    segmentSize = 64
    txt += data
    totalSegments = (len(txt)) // segmentSize
    file = open(session_inciada.mounted.path, "rb+")
    write_on_b = None
    write_on_i = None
    totalSegments = (totalSegments + 1) if len(txt) % 64 != 0 else totalSegments
    iterations_blocks = min(totalSegments, 12)
    
    for s in range(iterations_blocks):
        new_segment = txt[s * segmentSize : (s + 1) * segmentSize]
        file_user = structs.BloqueArchivo()
        file_user.b_content = new_segment.encode('utf-8')[:64].ljust(64, b'\0')
        if inodo_archivo.i_block[s] == -1:
            inodo_archivo.i_block[s] = sblock.s_first_blo
            write_on_b = sblock.s_bm_block_start + sblock.s_first_blo
            file.seek(write_on_b)
            file.write(b'f')
            sblock.s_first_blo = next_first_block(sblock, session_inciada.mounted.path)
            sblock.s_free_blocks_count -= 1

        print(file_user.b_content)
        write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * inodo_archivo.i_block[s])
        file.seek(write_on)
        file.write(file_user)
        
    
    file.seek(session_inciada.mounted.part_start)
    file.write(sblock)
    inodo_archivo.i_s = len(txt)
    write_on_i = sblock.s_inode_start + (ctypes.sizeof(structs.Inodo) * i_ino)
    file.seek(write_on_i)
    file.write(inodo_archivo)
    file.close()
    if tipo == 'G':
        groups.append(name_g_u)
    elif tipo == 'U':
        users.append(user_actual)

    inodo_arch, i_f = find_file(sblock, "/user.txt", session_inciada.mounted.path, indo_carpeta_archivo)
    if(i_f == -1):
        print(f"Error: Ruta especificada '/user.txt' no existe")
        return
    txt = join_file(sblock, inodo_arch, session_inciada.mounted.path)
    print("JOIN FILE MKFILE")
    print(txt)
    print(inodo_archivo.i_s)

def remove_grupo_usuario(sblock, data, name_g_u, tipo, index):
    indo_carpeta_archivo, i, _, __ = find_carpeta_archivo(sblock, "/", session_inciada)
    if(i == -1):
        print(f"Error: Ruta especificada '{self.path}' no existe")
        return
    inodo_archivo, i_ino = find_file(sblock, "/user.txt", session_inciada.mounted.path, indo_carpeta_archivo)
    if(i_ino == -1):
        print(f"Error: Ruta especificada '/user.txt' no existe")
        return
    txt = join_file(sblock, inodo_archivo, session_inciada.mounted.path)
    lineas = txt.split('\n')
    new_txt = ""
    for i, linea in enumerate(lineas):
        grupo_usuario = linea.split(',')
        # print(linea)
        if len(linea) > 0 and grupo_usuario[1] == tipo:
        #     grupo_usuario = linea.split(',')
        #     print("buenaaaaaaaas", grupo_usuario[0], grupo_usuario[2])
            if grupo_usuario[0] != '0' and grupo_usuario[index] == name_g_u:
                new_txt += f"{data}\n"
                continue
            elif grupo_usuario[index] == name_g_u:
                print(f"El {'grupo' if tipo == 'G' else 'usuario'} ya ha sido eliminado anteriormente")
                return

        if len(linea) > 0:
            new_txt += linea + '\n'
    
    print("Terminado, ", new_txt)


    # -------------------------------------------------
    segmentSize = 64
    # segment_actual = len(txt) // segmentSize
    # print("segment_actual ", segment_actual)
    # segment = txt[segment_actual * segmentSize : (segment_actual + 1) * segmentSize]
    # txt += data_group
    totalSegments = (len(new_txt)) // segmentSize
    # write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * inodo_archivo.i_block[totalSegments - 1])
    file = open(session_inciada.mounted.path, "rb+")
    totalSegments = (totalSegments + 1) if len(new_txt) % 64 != 0 else totalSegments
    print("totalSegments", totalSegments)
    iterations_blocks = min(totalSegments, 12)
    for s in range(iterations_blocks):
        new_segment = new_txt[s * segmentSize : (s + 1) * segmentSize]
        # print("Wola", s)
        # print("new_segment ", new_segment)
        # # print(inodo_archivo.i_block[s])
        file_user = structs.BloqueArchivo()
        file_user.b_content = new_segment.encode('utf-8')[:64].ljust(64, b'\0')
        if inodo_archivo.i_block[s] == -1:
        #     print("Entraaaaaaa", s)
            inodo_archivo.i_block[s] = sblock.s_first_blo
            write_on_b = sblock.s_bm_block_start + sblock.s_first_blo
            file.seek(write_on_b)
            file.write(b'f')
            sblock.s_first_blo = next_first_block(sblock, session_inciada.mounted.path)
            sblock.s_free_blocks_count -= 1

        # print("ssss", inodo_archivo.i_block[s])    
        print(file_user.b_content)
        write_on = sblock.s_block_start + (ctypes.sizeof(structs.BloqueArchivo) * inodo_archivo.i_block[s])
        file.seek(write_on)
        file.write(file_user)
        # print("termina")
        
    
    file.seek(session_inciada.mounted.part_start)
    file.write(sblock)
    inodo_archivo.i_s = len(new_txt)
    write_on_i = sblock.s_inode_start + (ctypes.sizeof(structs.Inodo) * i_ino)
    file.seek(write_on_i)
    file.write(inodo_archivo)
    file.close()

    inodo_arch, i_f = find_file(sblock, "/user.txt", session_inciada.mounted.path, indo_carpeta_archivo)
    if(i_f == -1):
        print(f"Error: Ruta especificada '/user.txt' no existe")
        return
    print(inodo_arch.i_block[0])
    print(inodo_arch.i_block[1])
    print(inodo_arch.i_block[2])
    print("INODO ", i_ino)
    txt = join_file(sblock, inodo_arch, session_inciada.mounted.path)
    print("JOIN FILE MKFILE")
    print(txt)
    print(inodo_archivo.i_s)

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

        