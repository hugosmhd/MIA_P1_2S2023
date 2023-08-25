from comandos.mkdisk.mkdisk import mkdisk
from comandos.fdisk.fdisk import fdisk
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

# mkdisk -size=30 -unit=M -path="/home/hugosmh/Documentos/Discos/disco2.dsk"
# fdisk -size=5 -unit=M -path="/home/hugosmh/Documentos/Discos/disco2.dsk" -name=Extended1 -type=E -fit=FF
# fdisk -size=2 -unit=M -path="/home/hugosmh/Documentos/Discos/disco2.dsk" -name=Logic1 -type=L
# fdisk -size=3 -unit=M -path="/home/hugosmh/Documentos/Discos/disco2.dsk" -name=Partition1
# fdisk -size=5 -unit=M -path="/home/hugosmh/Documentos/Discos/disco2.dsk" -name=Partition2
# fdisk -size=9 -unit=M -path="/home/hugosmh/Documentos/Discos/disco2.dsk" -name=Partition3
# fdisk -size=7 -unit=M -path="/home/hugosmh/Documentos/Discos/disco2.dsk" -name=Partition4

# mkdisk -size=30 -unit=M -path="/home/hugosmh/Documentos/Discos/disco5.dsk"
# fdisk -size=3 -unit=M -path="/home/hugosmh/Documentos/Discos/disco5.dsk" -name=Partition1
# fdisk -size=10 -unit=M -path="/home/hugosmh/Documentos/Discos/disco5.dsk" -name=Extended1 -type=E -fit=FF
# fdisk -size=4 -unit=K -path="/home/hugosmh/Documentos/Discos/disco5.dsk" -name=Logic1 -type=L
# fdisk -size=5 -unit=K -path="/home/hugosmh/Documentos/Discos/disco5.dsk" -name=Logic2 -type=L
# fdisk -size=5 -unit=M -path="/home/hugosmh/Documentos/Discos/disco5.dsk" -name=Logic3 -type=L
# fdisk -size=5 -unit=M -path="/home/hugosmh/Documentos/Discos/disco5.dsk" -name=Partition2
# fdisk -delete=full -name=Partition1 -path=/home/hugosmh/Documentos/Discos/disco5.dsk
# fdisk -delete=full -name=Logic1 -path=/home/hugosmh/Documentos/Discos/disco5.dsk
# fdisk -delete=full -name=Logic2 -path=/home/hugosmh/Documentos/Discos/disco5.dsk
# fdisk -delete=full -name=Logic3 -path=/home/hugosmh/Documentos/Discos/disco5.dsk
# fdisk -path="/home/hugosmh/Documentos/Discos/disco5.dsk" -name=Partition2 -add=1 -unit=M
# fdisk -path="/home/hugosmh/Documentos/Discos/disco5.dsk" -name=Partition1 -add=1 -unit=M
# fdisk -path="/home/hugosmh/Documentos/Discos/disco5.dsk" -name=Logic3 -add=-1 -unit=M
# fdisk -path="/home/hugosmh/Documentos/Discos/disco5.dsk" -name=Logic1 -add=1 -unit=M
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