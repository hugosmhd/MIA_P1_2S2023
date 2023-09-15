import re

import structs
from comandos.mkdisk.mkdisk import mkdisk
from comandos.fdisk.fdisk import fdisk
from comandos.mount.mount import mount
from comandos.mkfs.mkfs import mkfs
from comandos.login.login import login
from comandos.mkgrp.mkgrp import mkgrp
from comandos.mkusr.mkusr import mkusr
from comandos.mkfile.mkfile import mkfile
from comandos.cat.cat import cat
from comandos.rename.rename import rename
from comandos.move.move import move
from comandos.mkdir.mkdir import mkdir
from comandos.recovery.recovery import recovery
from comandos.rep.rep import rep
from comandos.chmod.chmod import chmod
from comandos.chown.chown import chown
from _global._global import comando_actual

def analizar(entrada, rep_journaling = False):
    # cadena = "rep -id=931Disco1 -Path=./home/archivos/reports/reporte2.jpg -name=mbr -delete=full"
    
    # comando = entrada.lower()
    comando = entrada
    comando = comando.strip()
    if not comando.startswith("#"):
        global comando_actual
        comando_actual.clear()
        comando_actual.append(comando)
        cmdentrada = comando.split(' ')
        parametros = []
        for i, param in enumerate(cmdentrada):
            if(i == 0):
                comando = param
            else:
                parametros.append(param)
        instancia = identificar_parametros(comando, parametros, rep_journaling)
        if rep_journaling:
            return instancia
    else:
        print("Linea de comentario")
        print(comando)
        
def identificar_parametros(comando, parametros, rep_journaling):
    comando = comando.lower()
    if(comando == 'mkdisk'):
        analizar_mkdisk(parametros)
    elif(comando == 'rmdisk'):
        analizar_rmdisk(parametros)
    elif(comando == 'fdisk'):
        analizar_fdisk(parametros)
    elif(comando == 'mount'):
        analizar_mount(parametros)
    elif(comando == 'unmount'):
        analizar_unmount(parametros)
    elif(comando == 'mkfs'):
        analizar_mkfs(parametros)
    elif(comando == 'login'):
        analizar_login(parametros)
    elif(comando == 'logout'):
        analizar_logout(parametros)
    elif(comando == 'mkgrp'):
        grupo = analizar_mkgrp(parametros, rep_journaling)
        if rep_journaling:
            return grupo
    elif(comando == 'rmgrp'):
        grupo = analizar_rmgrp(parametros, rep_journaling)
        if rep_journaling:
            return grupo
    elif(comando == 'mkusr'):
        usuario = analizar_mkusr(parametros, rep_journaling)
        if rep_journaling:
            return usuario
    elif(comando == 'rmusr'):
        usuario = analizar_rmusr(parametros, rep_journaling)
        if rep_journaling:
            return usuario
    elif(comando == 'chgrp'):
        usuario = analizar_chgrp(parametros, rep_journaling)
        if rep_journaling:
            return usuario
    elif(comando == 'mkfile'):
        archivo = analizar_mkfile(parametros, rep_journaling)
        if rep_journaling:
            return archivo
    elif(comando == 'chmod'):
        permisos = analizar_chmod(parametros, rep_journaling)
        if rep_journaling:
            return permisos
    elif(comando == 'chown'):
        nuevo_propietario = analizar_chown(parametros, rep_journaling)
        if rep_journaling:
            return nuevo_propietario
    elif(comando == 'cat'):
        analizar_cat(parametros)
    elif(comando == 'rename'):
        archivo_carpeta = analizar_rename(parametros, rep_journaling)
        if rep_journaling:
            return archivo_carpeta
    elif(comando == 'recovery'):
        analizar_recovery(parametros)
    elif(comando == 'loss'):
        analizar_loss(parametros)
    elif(comando == 'move'):
        archivo_carpeta = analizar_move(parametros, rep_journaling)
        if rep_journaling:
            return archivo_carpeta
    elif(comando == 'mkdir'):
        carpeta = analizar_mkdir(parametros, rep_journaling)
        if rep_journaling:
            return carpeta
    elif(comando == 'rep'):
        analizar_rep(parametros)
    elif(comando == 'execute'):
        analizar_execute(parametros)
    elif(comando == 'pause'):
        analizar_pause()
    elif(comando == '\n' or comando == '\t' or comando == '\r' or comando.strip() == ""):
        pass
    else:
        print(f"Comando {comando} no válido")

def get_path(i, parametros):
    valor = ""
    concatenar = False
    comillas = False
    finalPath = False
    ya_no_entra = True
    posicion = 0
    while i < len(parametros) and not finalPath:
        tmpParam = parametros[i]
        
        if concatenar:
            valor += " "
        
        for j in range(len(tmpParam)):
            if concatenar and comillas:
                if tmpParam[j] != '"' and comillas == 1:
                    caracter = tmpParam[j]
                    valor = valor + caracter
                elif tmpParam[j] == '"' and comillas == 1:
                    finalPath = True
                    break
            elif concatenar and comillas == False and tmpParam[posicion] != '"':
                finalPath = True
                caracter = tmpParam[j]
                valor = valor + caracter

            if ya_no_entra and tmpParam[posicion] == '"' and concatenar:
                comillas = True
                ya_no_entra = False
                
            if tmpParam[j] == '=' and not concatenar:
                concatenar = True
                posicion = j + 1
                
        if not finalPath:
            i += 1
    
    valor = valor.rstrip('/')
    return valor, i

def get_valor_parametro(parametro):
    valor = ""
    i = 0
    concatenar = False
    while i < len(parametro):
        if(concatenar):
            valor += parametro[i]
        if(parametro[i] == '='):
            concatenar = True
        i += 1
    return valor

def leer_script(path):
    try:
        with open(path, "r") as file:
            for line in file:
                print("---------------- **************** ---------------- **************** ---------------- **************** ---------------- ****************")
                print("LINEA DEL ARCHIVO:", line.strip())
                comando = line.strip()
                analizar(comando)
    except FileNotFoundError:
        print(f"El script con ruta {path} no existe")

# execute -path=/home/hugosmh/Escritorio/TAREAS_MIA/MIA_P1_2S2023/scripts/avanzado1.txt
# execute -path=/home/hugosmh/Escritorio/TAREAS_MIA/MIA_P1_2S2023/basico.txt
# execute -path=/home/hugosmh/Escritorio/TAREAS_MIA/MIA_P1_2S2023/chmod.txt
# execute -path=/home/hugosmh/Escritorio/TAREAS_MIA/MIA_P1_2S2023/new_script.txt
# execute -path=/home/hugosmh/Escritorio/TAREAS_MIA/MIA_P1_2S2023/new_script2.txt
# execute -path=/home/hugosmh/Escritorio/TAREAS_MIA/MIA_P1_2S2023/script4.txt
# execute -path=/home/hugosmh/Escritorio/TAREAS_MIA/MIA_P1_2S2023/script5.txt
# execute -path=/home/hugosmh/Escritorio/TAREAS_MIA/MIA_P1_2S2023/script6.txt
# execute -path=/home/hugosmh/Escritorio/TAREAS_MIA/MIA_P1_2S2023/script1.txt
# execute -path=/home/hugosmh/Escritorio/TAREAS_MIA/MIA_P1_2S2023/script2.txt
def analizar_chown(parametros, rep_journaling = False):
    nuevo_propietario = chown()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-path=") == 0:
            nuevo_propietario.path, i = get_path(i, parametros)
        elif param.find("-r") == 0:
            nuevo_propietario.recursivo = True
        elif param.find("-user=") == 0:
            nuevo_propietario.user = get_valor_parametro(param)
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'chown': {param}")
        i += 1
    if rep_journaling:
        return nuevo_propietario
    nuevo_propietario.crear_chown()

def analizar_chmod(parametros, rep_journaling = False):
    permisos = chmod()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-path=") == 0:
            permisos.path, i = get_path(i, parametros)
        elif param.find("-r") == 0:
            permisos.recursivo = True
        elif param.find("-ugo=") == 0:
            permisos.ugo = int(get_valor_parametro(param))
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'chmod': {param}")
        i += 1
    if rep_journaling:
        return permisos
    permisos.crear_chmod()

def analizar_mkdisk(parametros):
    disco = mkdisk()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-path=") == 0:
            disco.path, i = get_path(i, parametros)
        elif param.find("-size=") == 0:
            disco.size = int(get_valor_parametro(param))
        elif param.find("-fit=") == 0:
            disco.fit = get_valor_parametro(param)
        elif param.find("-unit=") == 0:
            disco.unit = get_valor_parametro(param)
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'mkdisk': {param}")

        i += 1
    disco.crear_mkdisk(disco)

def analizar_rmdisk(parametros):
    disco = mkdisk()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-path=") == 0:
            disco.path, i = get_path(i, parametros)
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'rmdisk': {param}")

        i += 1
    disco.crear_rmdisk()

def analizar_fdisk(parametros):
    particion = fdisk()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-path=") == 0:
            particion.path, i = get_path(i, parametros)
        elif param.find("-size=") == 0:
            particion.size = int(get_valor_parametro(param))
        elif param.find("-name=") == 0:
            particion.name = get_valor_parametro(param)
        elif param.find("-unit=") == 0:
            particion.unit = get_valor_parametro(param)
        elif param.find("-type=") == 0:
            particion.type = get_valor_parametro(param)
        elif param.find("-fit=") == 0:
            particion.fit = get_valor_parametro(param)
        elif param.find("-delete=") == 0:
            particion.suprim = get_valor_parametro(param)
        elif param.find("-add=") == 0:
            particion.add = int(get_valor_parametro(param))
            particion.isAdd = True
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'fdisk': {param}")
        i += 1
    particion.crear_fdisk()

def analizar_mount(parametros):
    particion_montar = mount()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-path=") == 0:
            particion_montar.path, i = get_path(i, parametros)
        elif param.find("-name=") == 0:
            particion_montar.name = get_valor_parametro(param)
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'mount': {param}")
        i += 1
    particion_montar.crear_mount()

def analizar_unmount(parametros):
    particion_desmontar = mount()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-id=") == 0:
            particion_desmontar.name = get_valor_parametro(param)
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'unmount': {param}")
        i += 1
    particion_desmontar.crear_unmount()

def analizar_mkfs(parametros):
    formatear_particion = mkfs()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-id=") == 0:
            formatear_particion.id = get_valor_parametro(param)
        elif param.find("-type=") == 0:
            formatear_particion.type = get_valor_parametro(param)
        elif param.find("-fs=") == 0:
            formatear_particion.fs = get_valor_parametro(param)
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'mkfs': {param}")
        i += 1
    formatear_particion.crear_mkfs()

def analizar_login(parametros):
    autenticacion = login()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-id=") == 0:
            autenticacion.id = get_valor_parametro(param)
        elif param.find("-user=") == 0:
            autenticacion.user = get_valor_parametro(param)
        elif param.find("-pass=") == 0:
            autenticacion.password = get_valor_parametro(param)
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'login': {param}")
        i += 1
    autenticacion.crear_login(autenticacion)

def analizar_logout(parametros):
    autenticacion = login()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        print(f"Parametro no aceptado en 'logout': {param}")
        i += 1
    autenticacion.crear_logout()

def analizar_mkgrp(parametros, rep_journaling = False):
    new_grp = mkgrp()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-name=") == 0:
            new_grp.name = get_valor_parametro(param)
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'mkgrp': {param}")
        i += 1
        
    if rep_journaling:
        new_grp.tipo = 1
        return new_grp
    new_grp.crear_mkgrp()

def analizar_rmgrp(parametros, rep_journaling = False):
    new_grp = mkgrp()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-name=") == 0:
            new_grp.name = get_valor_parametro(param)
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'mkgrp': {param}")
        i += 1

    if rep_journaling:
        new_grp.tipo = 2
        return new_grp

    new_grp.crear_rmgrp()

def analizar_mkusr(parametros, rep_journaling = False):
    new_user = mkusr()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-user=") == 0:
            new_user.user = get_valor_parametro(param)
        elif param.find("-pass=") == 0:
            new_user.password = get_valor_parametro(param)
        elif param.find("-grp=") == 0:
            new_user.grp = get_valor_parametro(param)
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'mkusr': {param}")
        i += 1

    if rep_journaling:
        new_user.tipo = 1
        return new_user
    new_user.crear_mkusr()

def analizar_chgrp(parametros, rep_journaling = False):
    new_group = mkusr()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-user=") == 0:
            new_group.user = get_valor_parametro(param)
        elif param.find("-grp=") == 0:
            new_group.grp = get_valor_parametro(param)
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'chgrp': {param}")
        i += 1

    if rep_journaling:
        new_group.tipo = 3
        return new_group
    new_group.crear_chgrp()

def analizar_rmusr(parametros, rep_journaling = False):
    new_user = mkusr()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-user=") == 0:
            new_user.user = get_valor_parametro(param)
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'mkusr': {param}")
        i += 1

    if rep_journaling:
        new_user.tipo = 2
        return new_user

    new_user.crear_rmusr()

def analizar_mkfile(parametros, rep_journaling = False):
    archivo = mkfile()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-path=") == 0:
            archivo.path, i = get_path(i, parametros)
        elif param.find("-r") == 0:
            archivo.recursivo = True
        elif param.find("-size=") == 0:
            archivo.size = int(get_valor_parametro(param))
            archivo.size_activo = True
        elif param.find("-cont=") == 0:
            archivo.cout, i = get_path(i, parametros)
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'mkfile': {param}")
        i += 1
    if rep_journaling:
        return archivo
    archivo.crear_mkfile()

def analizar_rename(parametros, rep_journaling):
    archivo_carpeta = rename()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-path=") == 0:
            archivo_carpeta.path, i = get_path(i, parametros)
        elif param.find("-name=") == 0:
            archivo_carpeta.name, i = get_path(i, parametros)
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'rename': {param}")
        i += 1

    if rep_journaling:
        return archivo_carpeta

    archivo_carpeta.crear_rename()

def analizar_move(parametros, rep_journaling):
    archivo_carpeta = move()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-path=") == 0:
            archivo_carpeta.path, i = get_path(i, parametros)
        elif param.find("-destino=") == 0:
            archivo_carpeta.destino, i = get_path(i, parametros)
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'move': {param}")
        i += 1

    if rep_journaling:
        return archivo_carpeta

    archivo_carpeta.crear_move()

def analizar_cat(parametros):
    archivo = cat()
    i = 0
    num_file = 1
    while i < len(parametros):
        param = parametros[i]
        if param.find(f"-file{num_file}=") == 0:
            file, i = get_path(i, parametros)
            archivo.files.append(file)
            num_file += 1
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'cat': {param}, verifique que siga la secuencia")
        i += 1
    archivo.crear_cat()

def analizar_mkdir(parametros, rep_journaling):
    carpeta = mkdir()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-path=") == 0:
            carpeta.path, i = get_path(i, parametros)
        elif param.find("-r") == 0:
            carpeta.recursivo = True
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'mkdir': {param}")
        i += 1
    
    if rep_journaling:
        return carpeta
        
    carpeta.crear_mkdir()

def analizar_recovery(parametros):
    recuperacion = recovery()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-id=") == 0:
            recuperacion.id = get_valor_parametro(param)
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'recovery': {param}")
        i += 1
    recuperacion.crear_recovery()

def analizar_loss(parametros):
    perder_datos = recovery()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-id=") == 0:
            perder_datos.id = get_valor_parametro(param)
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'loss': {param}")
        i += 1
    perder_datos.crear_loss()

def analizar_pause():
    input("Presione ENTER para continuar...")

def analizar_rep(parametros):
    reporte = rep()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-path=") == 0:
            reporte.path, i = get_path(i, parametros)
        elif param.find("-name=") == 0:
            reporte.name = get_valor_parametro(param)
        elif param.find("-id=") == 0:
            reporte.id = get_valor_parametro(param)
        elif param.find("-ruta=") == 0:
            reporte.ruta, i = get_path(i, parametros)
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        else:
            print(f"Parametro no aceptado en 'rep': {param}")
        i += 1
    reporte.crear_rep()

def analizar_execute(parametros):
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-path=") == 0:
            path, i = get_path(i, parametros)
        elif param.startswith("#"):
            break
        elif param == '':
            i += 1
            continue
        i += 1
    leer_script(path)