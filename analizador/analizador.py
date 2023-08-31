from comandos.mkdisk.mkdisk import mkdisk
from comandos.fdisk.fdisk import fdisk
from comandos.mount.mount import mount
from comandos.mkfs.mkfs import mkfs
from comandos.login.login import login
from comandos.mkfile.mkfile import mkfile
from comandos.mkdir.mkdir import mkdir
from comandos.rep.rep import rep
import structs

def analizar(entrada):
    # comando = entrada.lower()
    comando = entrada
    cmdentrada = comando.split(' ')
    parametros = []
    for i, param in enumerate(cmdentrada):
        if(param == '#'):
            continue
        if(i == 0):
            comando = param
        else:
            parametros.append(param)
    identificar_parametros(comando, parametros)
    # print(comando)
    # print(parametros)
        
def identificar_parametros(comando, parametros):
    comando.lower()
    if(comando == 'mkdisk'):
        analizar_mkdisk(parametros)
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
    elif(comando == 'mkfile'):
        analizar_mkfile(parametros)
    elif(comando == 'mkdir'):
        analizar_mkdir(parametros)
    elif(comando == 'rep'):
        analizar_rep(parametros)
    elif(comando == 'execute'):
        analizar_execute(parametros)
    else:
        print("Comando no válido")

def get_path(i, parametros):
    valor = ""
    concatenar = False
    comillas = False
    finalPath = False
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
                
            if tmpParam[posicion] == '"' and concatenar:
                comillas = True
                
            if tmpParam[j] == '=':
                concatenar = True
                posicion = j + 1
                
        if not finalPath:
            i += 1
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
                print("------------------------------------------")
                print("LINEA DEL ARCHIVO:", line.strip())
                comando = line.strip()
                analizar(comando)
    except FileNotFoundError:
        print(f"El script con ruta {path} no existe")


# execute -path=/home/hugosmh/Escritorio/TAREAS_MIA/MIA_P1_2S2023/script1.txt
# execute -path=/home/hugosmh/Escritorio/TAREAS_MIA/MIA_P1_2S2023/script2.txt
# fdisk -size=5 -unit=M -path="/home/hugosmh/Documentos/Discos/disco2.dsk" -name=Partition2
# fdisk -size=9 -unit=M -path="/home/hugosmh/Documentos/Discos/disco2.dsk" -name=Partition3
# fdisk -size=7 -unit=M -path="/home/hugosmh/Documentos/Discos/disco2.dsk" -name=Partition4
# fdisk -size=5 -unit=M -path="/home/hugosmh/Documentos/Discos/disco2.dsk" -name=Extended1 -type=E -fit=FF
# fdisk -size=2 -unit=M -path="/home/hugosmh/Documentos/Discos/disco2.dsk" -name=Logic1 -type=L
# fdisk -delete=full -name=Partition1 -path=/home/hugosmh/Documentos/Discos/disco2.dsk
# fdisk -delete=full -name=Partition2 -path=/home/hugosmh/Documentos/Discos/disco2.dsk
# fdisk -delete=full -name=Partition3 -path=/home/hugosmh/Documentos/Discos/disco2.dsk
# fdisk -delete=full -name=Partition4 -path=/home/hugosmh/Documentos/Discos/disco2.dsk
# fdisk -path="/home/hugosmh/Documentos/Discos/disco2.dsk" -name=Partition1 -add=1 -unit=M
# fdisk -path="/home/hugosmh/Documentos/Discos/disco2.dsk" -name=Extended1 -add=1 -unit=M
# fdisk -path="/home/hugosmh/Documentos/Discos/disco2.dsk" -name=Partition3 -add=1 -unit=M
# mount -path="/home/hugosmh/Documentos/Discos/disco2.dsk" -name=Partition2
# mount -path="/home/hugosmh/Documentos/Discos/disco2.dsk" -name=Partition3
# mount -path="/home/hugosmh/Documentos/Discos/disco2.dsk" -name=Extended1
# mount -path="/home/hugosmh/Documentos/Discos/disco2.dsk" -name=Logic1
# unmount -id=931disco2
# unmount -id=933disco2
# unmount -id=934disco2
# unmount -id=932disco2
# mkgrp -name=usuarios
# mkgrp -name=usuarioa
# mkgrp -name=usuarioc
# logout
# login -user=roots -pass=123 -id=931disco2
# mkdir -path=/home/user/docs -r
# mkdisk -size=30 -unit=M -path="/home/hugosmh/Documentos/Discos/disco2.dsk"
# fdisk -size=3 -unit=M -path="/home/hugosmh/Documentos/Discos/disco2.dsk" -name=Partition1
# mount -path="/home/hugosmh/Documentos/Discos/disco2.dsk" -name=Partition1
# mkfs -type=full -id=931disco2
# login -user=root -pass=123 -id=931disco2
# mkfile -size=1827 -path=/b.txt
# mkfile -size=1764 -path=/a.txt
# mkfile -size=193 -path=/c.txt
# mkfile -size=64 -path=/d.txt
# mkfile -size=65 -path=/e.txt
# mkfile -size=7 -path=/f.txt
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

        i += 1
    disco.crear_mkdisk(disco)

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
        else:
            print(f"Parametro no aceptado en 'fdisk': {valor}")
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
        else:
            print(f"Parametro no aceptado en 'mount': {valor}")
        i += 1
    particion_montar.crear_mount()

def analizar_unmount(parametros):
    particion_desmontar = mount()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-id=") == 0:
            particion_desmontar.name = get_valor_parametro(param)
        else:
            print(f"Parametro no aceptado en 'unmount': {valor}")
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
        else:
            print(f"Parametro no aceptado en 'mkfs': {valor}")
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
        else:
            print(f"Parametro no aceptado en 'login': {valor}")
        i += 1
    autenticacion.crear_login(autenticacion)

def analizar_mkfile(parametros):
    archivo = mkfile()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-path=") == 0:
            archivo.path, i = get_path(i, parametros)
        elif param.find("-r=") == 0:
            archivo.recursivo = True
        elif param.find("-size=") == 0:
            archivo.size = int(get_valor_parametro(param))
        elif param.find("-cout=") == 0:
            archivo.cout, i = get_path(i, parametros)
        else:
            print(f"Parametro no aceptado en 'mkfile': {valor}")
        i += 1
    archivo.crear_mkfile()

def analizar_mkdir(parametros):
    archivo = mkdir()
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-path=") == 0:
            archivo.path, i = get_path(i, parametros)
        elif param.find("-r=") == 0:
            archivo.recursivo = True
        else:
            print(f"Parametro no aceptado en 'mkdir': {valor}")
        i += 1
    archivo.crear_mkdir()

def analizar_rep(parametros):
    reporte = rep()
    reporte.path = "disco.dsk"
    reporte.crear_rep(reporte)

# execute -path=execute.txt
def analizar_execute(parametros):
    i = 0
    while i < len(parametros):
        param = parametros[i]
        if param.find("-path=") == 0:
            path, i = get_path(i, parametros)
        i += 1
    leer_script(path)