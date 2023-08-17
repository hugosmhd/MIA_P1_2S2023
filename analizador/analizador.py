from comandos.mkdisk.mkdisk import mkdisk
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