import ctypes
from datetime import datetime

import structs

def imprimir_tmp(mbr):
    try:
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
            print("Nombre:", particion.part_name.decode())

    except FileNotFoundError:
        pass

def imprimir_particiones(path):
    try:
        mbr = structs.MBR()
        file = open(path, 'rb')
        contenido_binario = file.read(ctypes.sizeof(mbr))
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
            print("Nombre:", particion.part_name.decode())
            if particion.part_type == b'E':
                tmp = structs.EBR()
                file.seek(particion.part_start)
                contenido_binario = file.read(ctypes.sizeof(tmp))
                ctypes.memmove(ctypes.byref(tmp), contenido_binario, ctypes.sizeof(tmp))

                while True:
                    if tmp.part_next == -1:
                        print("Rompeeeeeee")
                        break
                    
                    print("**** EBR ****")
                    print("Name:", tmp.part_name.decode())
                    print("Status:", tmp.part_status)
                    print("Next:", tmp.part_next)
                    print("Start:", tmp.part_start)
                    print("Size:", tmp.part_s)
                    
                    file.seek(tmp.part_next)
                    contenido_binario = file.read(ctypes.sizeof(tmp))
                    ctypes.memmove(ctypes.byref(tmp), contenido_binario, ctypes.sizeof(tmp))
        file.close()

    except FileNotFoundError:
        pass

def exist_partition(path, name, mbr):
    try:
        for i, particion in enumerate(mbr.mbr_partitions):
            print(particion.part_name.decode())
            if(name == particion.part_name.decode()):
                return 'PE', particion, i
            if particion.part_type == b'E':
                tmp = structs.EBR()
                file = open(path, 'rb')
                file.seek(particion.part_start)
                file.readinto(tmp)
                # contenido_binario = file.read(ctypes.sizeof(tmp))
                # ctypes.memmove(ctypes.byref(tmp), contenido_binario, ctypes.sizeof(tmp))

                while True:
                    if tmp.part_next == -1:
                        break
                    print(tmp.part_name)
                    if name == tmp.part_name.decode():
                        file.close()
                        return 'L', tmp, i
                    file.seek(tmp.part_next)
                    file.readinto(tmp)
                    # contenido_binario = file.read(ctypes.sizeof(tmp))
                    # ctypes.memmove(ctypes.byref(tmp), contenido_binario, ctypes.sizeof(tmp))
                file.close()
        return False, False, False

    except FileNotFoundError:
        pass

def crear_clone_particion(new_partition):
    clone = structs.Partition()
    clone.part_status = new_partition.part_status
    clone.part_type = new_partition.part_type
    clone.part_fit = new_partition.part_fit
    clone.part_start = new_partition.part_start
    clone.part_s = new_partition.part_s
    clone.part_name = new_partition.part_name
    return clone

def crear_clone_ebr(new_ebr):
    clone = structs.EBR()
    clone.part_status = new_ebr.part_status
    clone.part_fit = new_ebr.part_fit
    clone.part_start = new_ebr.part_start
    clone.part_s = new_ebr.part_s
    clone.part_next = new_ebr.part_next
    clone.part_name = new_ebr.part_name
    return clone

def ordenar_particiones(mbr):

    # sorted_partitions = sorted(mbr.mbr_partitions, key=lambda x: (x.part_start >= 0, -x.part_start if x.part_start < 0 else x.part_start), reverse=True)

    # for i, particion in enumerate(sorted_partitions):
    #     mbr.mbr_partitions[i] = particion
    for i in range(3, -1, -1):
        for j in range(i):
            if mbr.mbr_partitions[j].part_start > mbr.mbr_partitions[j + 1].part_start:
                aux = crear_clone_particion(mbr.mbr_partitions[j + 1])
                mbr.mbr_partitions[j + 1] = mbr.mbr_partitions[j]
                mbr.mbr_partitions[j] = aux

    for i in range(3, 0, -1):
        for j in range(i):
            if mbr.mbr_partitions[j].part_status == b'N':
                aux = crear_clone_particion(mbr.mbr_partitions[j])
                mbr.mbr_partitions[j] = mbr.mbr_partitions[j + 1]
                mbr.mbr_partitions[j + 1] = aux

    
    return mbr

def posicionar_particion(mbr, size, used, new_partition):
    baseDespues = ctypes.sizeof(mbr)
    baseAntes = baseDespues
    espacioAntes = 0
    espacioDespues = 0
    espacioActual = 0

    for partition in mbr.mbr_partitions:
        if partition.part_status == b'A':
            espacioAntes = partition.part_start - baseDespues
            baseAntes = baseDespues
            baseDespues = partition.part_start + partition.part_s
            espacioDespues = 0
        else:
            espacioDespues = mbr.mbr_tamano - baseDespues
            espacioAntes = 0
        if mbr.dsk_fit == b'F':
            if espacioAntes >= size:
                new_partition.part_start = baseAntes
                mbr.mbr_partitions[used] = new_partition
                # ordenar_particiones(mbr)
                mbr = ordenar_particiones(mbr)
                return mbr
            elif espacioDespues >= size:
                new_partition.part_start = baseDespues
                mbr.mbr_partitions[used] = new_partition
                # ordenar_particiones(mbr)
                mbr = ordenar_particiones(mbr)
                return mbr
        elif mbr.dsk_fit == b'B':
            if espacioAntes >= size and (espacioActual == 0 or espacioActual > espacioAntes):
                new_partition.part_start = baseAntes
                espacioActual = espacioAntes
            elif espacioDespues >= size and (espacioActual == 0 or espacioActual > espacioDespues):
                new_partition.part_start = baseDespues
                espacioActual = espacioDespues
        elif mbr.dsk_fit == b'W':
            if espacioAntes >= size and (espacioActual == 0 or espacioActual < espacioAntes):
                new_partition.part_start = baseAntes
                espacioActual = espacioAntes
            elif espacioDespues >= size and (espacioActual == 0 or espacioActual < espacioDespues):
                new_partition.part_start = baseDespues
                espacioActual = espacioDespues

    # No hay suficiente espacio por lo tanto se retorna false
    if new_partition.part_start == -1:
        return None
    mbr.mbr_partitions[used] = new_partition
    mbr = ordenar_particiones(mbr)
    return mbr

def retornar_extendida(mbr):
    for i in range(4):
        if mbr.mbr_partitions[i].part_type == b'E':
            return mbr.mbr_partitions[i]
    return False

def eliminar_particion(name, path):
    mbr = structs.MBR()
    with open(path, "rb+") as file:
        file.seek(0)
        contenido_binario = file.read(ctypes.sizeof(mbr))
    ctypes.memmove(ctypes.byref(mbr), contenido_binario, ctypes.sizeof(mbr))
    # partition_eliminated = structs.Partition()
    extended = False
    isNotLogic = False

    i = 0
    for partition in mbr.mbr_partitions:
        if name == partition.part_name.decode():
            partition_new = structs.Partition()
            mbr.mbr_partitions[i] = partition_new 
            isNotLogic = True
            break
        elif partition.part_type == b'E':
            extended = partition
        i += 1
    
    if isNotLogic:
        for i in range(3, -1, -1):
            for j in range(i):
                if mbr.mbr_partitions[j].part_status == b'N':
                    aux = crear_clone_particion(mbr.mbr_partitions[j])
                    mbr.mbr_partitions[j] = mbr.mbr_partitions[j + 1]
                    mbr.mbr_partitions[j + 1] = aux
        file = open(path, 'rb+')
        file.seek(0)
        file.write(ctypes.string_at(ctypes.byref(mbr), ctypes.sizeof(mbr)))
        file.close()
    else:
        if not extended:
            print("No existe ninguna particion con ese nombre")
            return

        print("Puede que sea lógica")
        tmp = structs.EBR()
        file = open(path, 'rb+')
        file.seek(extended.part_start)
        contenido_binario = file.read(ctypes.sizeof(tmp))
        ctypes.memmove(ctypes.byref(tmp), contenido_binario, ctypes.sizeof(tmp))
        partitionBefore = structs.EBR()
        partitionNext = structs.EBR()
        existBefore = False

        while True:
            if extended.part_start + extended.part_s < file.tell():
                break
            if tmp.part_status == b'0':
                break
            
            if tmp.part_name.decode() == name:
                print("Se encontró la partición a eliminar")
                if tmp.part_start == extended.part_start:
                    tmp.part_status = b'0'
                    tmp.part_name = b'\0'*16
                    if tmp.part_next != -1:
                        file.seek(tmp.part_next, 0)
                        contenido_binario = file.read(ctypes.sizeof(partitionNext))
                        ctypes.memmove(ctypes.byref(partitionNext), contenido_binario, ctypes.sizeof(partitionNext))
                        if partitionNext.part_status == b'0':
                            tmp.part_next = -1
                    file.seek(tmp.part_start)
                    file.write(ctypes.string_at(ctypes.byref(tmp), ctypes.sizeof(tmp)))
                else:
                    file.seek(tmp.part_next)
                    contenido_binario = file.read(ctypes.sizeof(partitionNext))
                    ctypes.memmove(ctypes.byref(partitionNext), contenido_binario, ctypes.sizeof(partitionNext))
                    if partitionNext.part_next != -1:
                        partitionBefore.part_next = tmp.part_next
                        file.seek(partitionBefore.part_start)
                        file.write(ctypes.string_at(ctypes.byref(partitionBefore), ctypes.sizeof(partitionBefore)))
                        
                        file.seek(tmp.part_start, 0)
                        num = int(tmp.part_s / 2)
                        file.write(b'\0' * num)
                    else:
                        partitionBefore.part_next = tmp.part_start
                        file.seek(partitionBefore.part_start)
                        file.write(ctypes.string_at(ctypes.byref(partitionBefore), ctypes.sizeof(partitionBefore)))
                        
                        file.seek(tmp.part_start)
                        num = int((tmp.part_s + ctypes.sizeof(partitionBefore)) / 2)
                        file.write(b'\0' * num)
                        
                        new_ebr = structs.EBR()
                        new_ebr.part_start = partitionBefore.part_next
                        file.seek(new_ebr.part_start)
                        file.write(ctypes.string_at(ctypes.byref(new_ebr), ctypes.sizeof(new_ebr)))
                break
            
            if tmp.part_status == b'0' and tmp.part_next == -1:
                break
            
            partitionBefore = crear_clone_ebr(tmp)
            existBefore = True
            file.seek(tmp.part_next, 0)
            contenido_binario = file.read(ctypes.sizeof(tmp))
            ctypes.memmove(ctypes.byref(tmp), contenido_binario, ctypes.sizeof(tmp))

        file.close()

def add_partition(name, path, add):
    mbr = structs.MBR()
    with open(path, "rb+") as file:
        file.seek(0)
        contenido_binario = file.read(ctypes.sizeof(mbr))
    ctypes.memmove(ctypes.byref(mbr), contenido_binario, ctypes.sizeof(mbr))

    tipo, particion, i = exist_partition(path, name, mbr)
    if not tipo:
        print("No existe ninguna particion con ese nombre")
        return
    
    if tipo == 'PE':
        if add > 0:
            espacio_despues = 0
            if(i == 3):
                espacio_despues = mbr.mbr_tamano - (particion.part_start + particion.part_s)
            else:
                next_partition = mbr.mbr_partitions[i+1]
                if next_partition.part_status == b'A':
                    espacio_despues = next_partition.part_start - (particion.part_start + particion.part_s)
                else:
                    espacio_despues = mbr.mbr_tamano - (particion.part_start + particion.part_s)
            
            if espacio_despues >= add:
                particion.part_s += add
                mbr.mbr_partitions[i] = particion
                file = open(path, 'rb+')
                file.seek(0)
                file.write(ctypes.string_at(ctypes.byref(mbr), ctypes.sizeof(mbr)))
                file.close()
                print(f"Se agrego espacio correctamente a la particion {name}")
                # imprimir_particiones(path)
                return
            else:
                print(f"No hay suficiente espacio para agregar a la particion {name}")
        else:
            if(particion.part_s - ctypes.sizeof(mbr) > add):
                particion.part_s += add
                mbr.mbr_partitions[i] = particion
                file = open(path, 'rb+')
                file.seek(0)
                file.write(ctypes.string_at(ctypes.byref(mbr), ctypes.sizeof(mbr)))
                file.close()
                print(f"Se quito espacio correctamente a la particion {name}")
                # imprimir_particiones(path)
                return
            else:
                print(f"No se puede eliminar esa cantidad de espacio a la particion {name}")
    elif tipo == 'L':
        extended = mbr.mbr_partitions[i]
        if add > 0:
            espacio_despues = 0
            file = open(path, "rb+")
            next_partition = structs.EBR()
            file.seek(particion.part_next)
            contenido_binario = file.read(ctypes.sizeof(next_partition))
            ctypes.memmove(ctypes.byref(next_partition), contenido_binario, ctypes.sizeof(next_partition))

            if next_partition.part_next == -1:
                espacio_despues = (extended.part_start + extended.part_s) - (particion.part_start + particion.part_s)
                if espacio_despues >= add:
                    file.seek(next_partition.part_start)
                    num = int(espacio_despues / 2)
                    file.write(b'\0' * num)
                    particion.part_next += add
                    new_ebr = structs.EBR()
                    new_ebr.part_start = particion.part_next
                    file.seek(new_ebr.part_start)
                    file.write(ctypes.string_at(ctypes.byref(new_ebr), ctypes.sizeof(new_ebr)))
            else:
                espacio_despues = next_partition.part_start - (particion.part_start + particion.part_s)
            
            file.close()

            if espacio_despues >= add:
                particion.part_s += add
                file = open(path, "rb+")
                file.seek(particion.part_start)
                file.write(ctypes.string_at(ctypes.byref(particion), ctypes.sizeof(particion)))
                file.close()
                print("Se agregó espacio correctamente a la partición", name)
                # imprimir_particiones(path)  # You'll need to define this function
                return
            else:
                print("No hay suficiente espacio para agregar a la partición", name)
        else:
            if(particion.part_s - ctypes.sizeof(particion) > add):
                particion.part_s += add
                # mbr.mbr_partitions[i] = particion
                file = open(path, 'rb+')
                file.seek(particion.part_start)
                file.write(ctypes.string_at(ctypes.byref(particion), ctypes.sizeof(particion)))
                file.close()
                print(f"Se quito espacio correctamente a la particion {name}")
                # imprimir_particiones(path)
                return
            else:
                print(f"No se puede eliminar esa cantidad de espacio a la particion {name}")

def make_primaria(name, path, size, fit, type_char):
    mbr = structs.MBR()
    with open(path, "rb") as file:
        contenido_binario = file.read(ctypes.sizeof(mbr))
    ctypes.memmove(ctypes.byref(mbr), contenido_binario, ctypes.sizeof(mbr))

    usadas = 0
    extendida = 0
    for i, particion in enumerate(mbr.mbr_partitions):
        if(particion.part_status == b'A'):
            usadas += 1
        if(particion.part_type == b'E'):
            extendida += 1
    
    if usadas == 4:
        print("No hay más espacio para particiones")
        return
    elif type_char == 'E' and extendida == 1:
        print("No se puede crear más de una partición extendida")
        return

    tipo, particion, i = exist_partition(path, name, mbr)
    if tipo == 'PE' or tipo == 'L':
        print("Ya existe una partición con ese nombre")
        return

    nueva_particion = structs.Partition()
    nueva_particion.part_status = b'A'
    nueva_particion.part_s = size
    nueva_particion.part_type = bytes(type_char, 'utf-8')
    nueva_particion.part_fit = bytes(fit.upper(), 'utf-8')
    nueva_particion.part_name = name.encode('utf-8')[:16].ljust(16, b'\0')

    nuevo_mbr = posicionar_particion(mbr, size, usadas, nueva_particion)
    if nuevo_mbr == None:
        print("Espacio insuficiente para agregar la particion")
        imprimir_particiones(path)
        return
    with open(path, "rb+") as file:
        file.seek(0)
        file.write(ctypes.string_at(ctypes.byref(nuevo_mbr), ctypes.sizeof(nuevo_mbr)))
        if(type_char == 'E'):
            ebr = structs.EBR()
            ebr.part_start = nueva_particion.part_start
            file.seek(nueva_particion.part_start)
            file.write(ctypes.string_at(ctypes.byref(ebr), ctypes.sizeof(ebr)))

    imprimir_particiones(path)
    # imprimir_tmp(nuevo_mbr)

def make_logica(name, path, size, fit):
    mbr = structs.MBR()
    with open(path, "rb") as file:
        contenido_binario = file.read(ctypes.sizeof(mbr))
    ctypes.memmove(ctypes.byref(mbr), contenido_binario, ctypes.sizeof(mbr))

    tipo, particion, i = exist_partition(path, name, mbr)
    if tipo == 'PE' or tipo == 'L':
        print("Ya existe una partición con ese nombre")
        return

    extended = retornar_extendida(mbr)
    if not extended:
        print("No existe ninguna partición extendida para crear una lógica")
        return

    nlogic = structs.EBR()
    nlogic.part_status = b'1' #
    nlogic.part_s = size #
    nlogic.part_next = -1 #
    nlogic.part_fit = bytes(fit.upper(), 'utf-8') #
    nlogic.part_name = name.encode('utf-8')[:16].ljust(16, b'\0') #

    partitionBefore = structs.EBR()
    partSaveBefore = structs.EBR()
    tmp = structs.EBR()
    with open(path, "rb") as file:
        file.seek(extended.part_start)
        contenido_binario = file.read(ctypes.sizeof(tmp))
    ctypes.memmove(ctypes.byref(tmp), contenido_binario, ctypes.sizeof(tmp))

    baseDespues = tmp.part_start
    baseAntes = baseDespues
    espacioAntes = 0
    espacioDespues = 0
    espacioActual = 0
    existBefore = False
    isWriteBefore = False

    file = open(path, 'rb+')
    while True:
        if tmp.part_start == extended.part_start and tmp.part_status == b'0' and tmp.part_next != -1:
            nlogic.part_next = tmp.part_next
            espacioAntes = tmp.part_s
        elif tmp.part_next != -1:
            espacioAntes = tmp.part_start - baseDespues
            baseAntes = baseDespues
            baseDespues = tmp.part_start + tmp.part_s
        else:
            espacioDespues = (extended.part_start + extended.part_s) - baseDespues
    
        if extended.part_fit == b'F':
            if espacioAntes >= size:
                nlogic.part_start = baseAntes
                if existBefore:
                    nlogic.part_next = partitionBefore.part_next
                    partitionBefore.part_next = nlogic.part_start
                    file.seek(partitionBefore.part_start)
                    file.write(ctypes.string_at(ctypes.byref(partitionBefore), ctypes.sizeof(partitionBefore)))
                    file.seek(nlogic.part_start)
                    file.write(ctypes.string_at(ctypes.byref(nlogic), ctypes.sizeof(nlogic)))
                    break
                file.seek(nlogic.part_start)
                file.write(ctypes.string_at(ctypes.byref(nlogic), ctypes.sizeof(nlogic)))
                break

            elif espacioDespues >= size:
                nlogic.part_start = baseDespues
                nlogic.part_next = nlogic.part_start + nlogic.part_s
                if existBefore:
                    partitionBefore.part_next = nlogic.part_start
                    file.seek(partitionBefore.part_start)
                    file.write(ctypes.string_at(ctypes.byref(partitionBefore), ctypes.sizeof(partitionBefore)))
                    file.seek(nlogic.part_start)
                    file.write(ctypes.string_at(ctypes.byref(nlogic), ctypes.sizeof(nlogic)))
                    new_ebr = structs.EBR()
                    new_ebr.part_start = nlogic.part_next
                    file.seek(new_ebr.part_start)
                    file.write(ctypes.string_at(ctypes.byref(new_ebr), ctypes.sizeof(new_ebr)))
                    break
                file.seek(nlogic.part_start)
                file.write(ctypes.string_at(ctypes.byref(nlogic), ctypes.sizeof(nlogic)))
                new_ebr = structs.EBR()
                new_ebr.part_start = nlogic.part_next
                file.seek(new_ebr.part_start)
                file.write(ctypes.string_at(ctypes.byref(new_ebr), ctypes.sizeof(new_ebr)))
                break
        elif extended.part_fit == b'B':
            if espacioAntes >= size and (espacioActual == 0 or espacioActual > espacioAntes):
                nlogic.part_start = baseAntes
                espacioActual = espacioAntes
                isWriteBefore = True
                partSaveBefore = crear_clone_ebr(partitionBefore)
            elif espacioDespues >= size and (espacioActual == 0 or espacioActual > espacioDespues):
                nlogic.part_start = baseDespues
                espacioActual = espacioDespues
                nlogic.part_next = nlogic.part_start + nlogic.part_s
                isWriteBefore = False
                partSaveBefore = crear_clone_ebr(partitionBefore)
        elif extended.part_fit == b'W':
            if espacioAntes >= size and (espacioActual == 0 or espacioActual < espacioAntes):
                nlogic.part_start = baseAntes
                espacioActual = espacioAntes
                isWriteBefore = True
                partSaveBefore = crear_clone_ebr(partitionBefore)
            elif espacioDespues >= size and (espacioActual == 0 or espacioActual < espacioDespues):
                nlogic.part_start = baseDespues
                espacioActual = espacioDespues
                nlogic.part_next = nlogic.part_start + nlogic.part_s
                isWriteBefore = False
                partSaveBefore = crear_clone_ebr(partitionBefore)

        if tmp.part_status == b'0' and tmp.part_next == -1:
            break
        
        partitionBefore = crear_clone_ebr(tmp)
        existBefore = True
        file.seek(tmp.part_next)
        contenido_binario = file.read(ctypes.sizeof(tmp))
        ctypes.memmove(ctypes.byref(tmp), contenido_binario, ctypes.sizeof(tmp))

    if nlogic.part_start == -1:
        print("Espacio insuficiente para agregar la particion")
        imprimir_particiones(path)
        return

    if extended.part_fit == b'B' or extended.part_fit == b'W':
        if isWriteBefore:
            if existBefore:
                nlogic.part_next = partSaveBefore.part_next
                partSaveBefore.part_next = nlogic.part_start
                file.seek(partSaveBefore.part_start, 0)
                file.write(ctypes.string_at(ctypes.byref(partSaveBefore), ctypes.sizeof(partSaveBefore)))
                file.seek(nlogic.part_start, 0)
                file.write(ctypes.string_at(ctypes.byref(nlogic), ctypes.sizeof(nlogic)))
            else:
                file.seek(nlogic.part_start)
                file.write(ctypes.string_at(ctypes.byref(nlogic), ctypes.sizeof(nlogic)))
        else:
            if existBefore: # revisar que funcione
                partSaveBefore.part_next = nlogic.part_start
                file.seek(partSaveBefore.part_start)
                file.write(ctypes.string_at(ctypes.byref(partSaveBefore), ctypes.sizeof(partSaveBefore)))
                file.seek(nlogic.part_start)
                file.write(ctypes.string_at(ctypes.byref(nlogic), ctypes.sizeof(nlogic)))
                new_ebr = structs.EBR()
                new_ebr.part_start = nlogic.part_next
                file.seek(new_ebr.part_start)
                file.write(ctypes.string_at(ctypes.byref(new_ebr), ctypes.sizeof(new_ebr)))
            else:
                file.seek(nlogic.part_start)
                file.write(ctypes.string_at(ctypes.byref(nlogic), ctypes.sizeof(nlogic)))
                new_ebr = structs.EBR()
                new_ebr.part_start = nlogic.part_next
                file.seek(new_ebr.part_start)
                file.write(ctypes.string_at(ctypes.byref(new_ebr), ctypes.sizeof(new_ebr)))

    file.close()
    imprimir_particiones(path)


class fdisk:
    def __init__(self):
        self.unit = 'K'   # int
        self.type = 'P'  # string
        self.fit = 'WF'   # char
        self.isAdd = False  # char
        self.size = 0
        self.path = ""
        self.name = ""
        self.suprim = ""
        self.add = 0

    def crear_fdisk(self):
        # print("FDISK")
        self.unit = self.unit.lower()
        # print("UNIT", self.unit)
        # print("TYPE", self.type)
        # print("FIT", self.fit)
        # print("ISADD", self.isAdd)
        # print("SIZE", self.size)
        # print("PATH", self.path)
        # print("NAME", self.name)
        # print("SUPRIM", self.suprim)
        # print("ADD", self.add)



        size = 0
        add = 0

        if self.unit == 'b':
            size = self.size
            add = self.add
        elif self.unit == 'k':
            size = self.size * 1024
            add = self.add * 1024
        elif self.unit == 'm':
            size = self.size * 1024 * 1024
            add = self.add * 1024 * 1024
        else:
            print("Unidad no permitida")
            return

        if self.suprim != "":
            eliminar_particion(self.name, self.path)
            imprimir_particiones(self.path)
            return
        elif self.isAdd:
            add_partition(self.name, self.path, add)
            imprimir_particiones(self.path)
            return

        self.fit = self.fit.lower()
        if self.fit == "bf":
            self.fit = 'B'
        elif self.fit == "ff":
            self.fit = 'F'
        elif self.fit == "wf" or self.fit == "":
            self.fit = 'W'
        else:
            print("Fit no permitido")
            return

        self.type = self.type.upper()
        if self.type == "P":
            make_primaria(self.name, self.path, size, self.fit, 'P')
        elif self.type == "E":
            make_primaria(self.name, self.path, size, self.fit, 'E')
        elif self.type == "L":
            make_logica(self.name, self.path, size, self.fit)
        else:
            print("Tipo de particion no permitida")
            return
