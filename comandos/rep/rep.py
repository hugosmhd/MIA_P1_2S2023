import os
import struct
from datetime import datetime
import ctypes
import pyperclip

import structs
from comandos.mount.mount import find_mounted

class rep:
    def __init__(self):
        self.name = ''
        self.path = ''  # string
        self.id = ''
        self.ruta = ''

    def crear_rep(self):
        if(self.name == 'mbr'):
            self.reporte_mbr()
        elif(self.name == 'disk'):
            self.reporte_disk()
        elif(self.name == 'inode'):
            self.reporte_inode()
        elif(self.name == 'block'):
            self.reporte_block()
        elif(self.name == 'bm_inode'):
            self.reporte_bm_inode()
        elif(self.name == 'bm_bloc'):
            self.reporte_bm_bloc()
        # try:
        #     with open(rep.path, "rb") as file:
        #         datos_mbr = file.read(struct.calcsize(structs.size_mbr()))
        #         tam, fecha, sig = structs.deserializar_mbr(datos_mbr)
        #         fecha_hora = datetime.fromtimestamp(fecha)

        #         fecha_formateada = fecha_hora.strftime("%d-%m-%Y %H:%M:%S")
        #         print(" ----- DATOS DEL MBR ----- ")
        #         print(f"Tamaño del disco: {tam} bytes")
        #         print(f"Fecha de creacion del disco: {fecha_formateada}")
        #         print(f"Signature: {sig}")
        # except FileNotFoundError:
        #     print(f"No existe el disco con ruta {rep.path}")
    
    def reporte_mbr(self):
        print("HACER REPORTE MBR")
        print(self.name)
        print(self.path)
        print(self.id)
        print(self.ruta)

        mounted = find_mounted(self.id)
        if(mounted == None):
            print("ID {self.id} no encontrado, verifique su entrada")
            return

        if not os.path.exists(self.path):
            os.makedirs(self.path)

        dot = 'digraph G {\n'
        dot += 'label="Reporte del MBR";\n'
        dot += 'labelloc=top;\n'
        dot += 'edge [ fontname="Courier New", fontsize=20];\n'
        dot += 'node [ shape="box", fontsize=26];\n'
        dot += 'n_1 [label=<\n'
        dot += '<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">\n'
        try:
            mbr = structs.MBR()
            file = open(mounted.path, 'rb')
            file.seek(0)
            file.readinto(mbr)
            fecha_hora = datetime.fromtimestamp(mbr.mbr_fecha_creacion)
            fecha_formateada = fecha_hora.strftime("%d-%m-%Y %H:%M:%S")
            dot += '<TR><TD colspan="2" BGCOLOR="#a569bd">                  MBR                  </TD></TR>\n'
            dot += '<TR><TD><FONT POINT-SIZE="15">mbr_tamano</FONT></TD>\n'
            dot += f'<TD><FONT POINT-SIZE="15">{mbr.mbr_tamano}</FONT></TD></TR>\n'
            dot += '<TR><TD><FONT POINT-SIZE="15">mbr_fecha_creacion</FONT></TD>\n'
            dot += f'<TD><FONT POINT-SIZE="15">{fecha_formateada}</FONT></TD></TR>\n'
            dot += '<TR><TD><FONT POINT-SIZE="15">mbr_dsk_signature</FONT></TD>\n'
            dot += f'<TD><FONT POINT-SIZE="15">{mbr.mbr_dsk_signature}</FONT></TD></TR>\n'
            dot += '<TR><TD><FONT POINT-SIZE="15">dsk_fit</FONT></TD>\n'
            dot += f'<TD><FONT POINT-SIZE="15">{mbr.dsk_fit.decode()}</FONT></TD></TR>\n'

            for i, particion in enumerate(mbr.mbr_partitions):
                if particion.part_type == b'E' or particion.part_type == b'P':
                    dot += '<TR><TD colspan="2" BGCOLOR="#58d68d ">Particion</TD></TR>\n'
                    dot += '<TR><TD><FONT POINT-SIZE="15">part_status</FONT></TD>\n'
                    dot += f'<TD><FONT POINT-SIZE="15">{particion.part_status.decode()}</FONT></TD></TR>\n'
                    dot += '<TR><TD><FONT POINT-SIZE="15">part_type</FONT></TD>\n'
                    dot += f'<TD><FONT POINT-SIZE="15">{particion.part_type.decode()}</FONT></TD></TR>\n'
                    dot += '<TR><TD><FONT POINT-SIZE="15">part_fit</FONT></TD>\n'
                    dot += f'<TD><FONT POINT-SIZE="15">{particion.part_fit.decode()}</FONT></TD></TR>\n'
                    dot += '<TR><TD><FONT POINT-SIZE="15">part_start</FONT></TD>\n'
                    dot += f'<TD><FONT POINT-SIZE="15">{particion.part_start}</FONT></TD></TR>\n'
                    dot += '<TR><TD><FONT POINT-SIZE="15">part_s</FONT></TD>\n'
                    dot += f'<TD><FONT POINT-SIZE="15">{particion.part_s}</FONT></TD></TR>\n'
                    dot += '<TR><TD><FONT POINT-SIZE="15">part_name</FONT></TD>\n'
                    dot += f'<TD><FONT POINT-SIZE="15">{particion.part_name.decode()}</FONT></TD></TR>\n'
                if particion.part_type == b'E':
                    tmp = structs.EBR()
                    file.seek(particion.part_start)
                    contenido_binario = file.read(ctypes.sizeof(tmp))
                    ctypes.memmove(ctypes.byref(tmp), contenido_binario, ctypes.sizeof(tmp))
                    next_part = tmp.part_next

                    while True:
                        if tmp.part_next == -1:
                            break
                        dot += '<TR><TD colspan="2" BGCOLOR="#7fb3d5  ">Particion Logica</TD></TR>\n'
                        dot += '<TR><TD><FONT POINT-SIZE="15">part_status</FONT></TD>\n'
                        dot += f'<TD><FONT POINT-SIZE="15">{tmp.part_status.decode()}</FONT></TD></TR>\n'
                        dot += '<TR><TD><FONT POINT-SIZE="15">part_fit</FONT></TD>\n'
                        dot += f'<TD><FONT POINT-SIZE="15">{tmp.part_fit.decode()}</FONT></TD></TR>\n'
                        dot += '<TR><TD><FONT POINT-SIZE="15">part_start</FONT></TD>\n'
                        dot += f'<TD><FONT POINT-SIZE="15">{tmp.part_start}</FONT></TD></TR>\n'
                        dot += '<TR><TD><FONT POINT-SIZE="15">part_s</FONT></TD>\n'
                        dot += f'<TD><FONT POINT-SIZE="15">{tmp.part_s}</FONT></TD></TR>\n'
                        dot += '<TR><TD><FONT POINT-SIZE="15">part_name</FONT></TD>\n'
                        dot += f'<TD><FONT POINT-SIZE="15">{tmp.part_name.decode()}</FONT></TD></TR>\n'
                        
                        file.seek(tmp.part_next)
                        contenido_binario = file.read(ctypes.sizeof(tmp))
                        ctypes.memmove(ctypes.byref(tmp), contenido_binario, ctypes.sizeof(tmp))
                        if tmp.part_next == -1:
                            dot += '<TR><TD><FONT POINT-SIZE="15">part_next</FONT></TD>\n'
                            dot += f'<TD><FONT POINT-SIZE="15">{tmp.part_next}</FONT></TD></TR>\n'
                        else:
                            dot += '<TR><TD><FONT POINT-SIZE="15">part_next</FONT></TD>\n'
                            dot += f'<TD><FONT POINT-SIZE="15">{next_part}</FONT></TD></TR>\n'
                        next_part = tmp.part_next
            file.close()

        except FileNotFoundError:
            pass

        dot += '</TABLE>>];\n'
        dot += '}'
        print(dot)


    def reporte_disk(self):
        print("HACER REPORTE DISK")
        print(self.name)
        print(self.path)
        print(self.id)
        print(self.ruta)

        mounted = find_mounted(self.id)
        if(mounted == None):
            print("ID {self.id} no encontrado, verifique su entrada")
            return

        if not os.path.exists(self.path):
            os.makedirs(self.path)

        directorio, archivo = os.path.split(mounted.path)

        dot = 'digraph G {\n'
        dot += f'label="Reporte del disco {archivo}";\n'
        dot += 'labelloc=top;\n'
        dot += 'edge [ fontname="Courier New", fontsize=20];\n'
        dot += 'node [ shape="box", fontsize=26];\n'
        dot += 'n_1 [label=<\n'
        dot += "<table border='0' cellborder='1' color='blue' cellspacing='0'>\n"
        try:
            mbr = structs.MBR()
            file = open(mounted.path, 'rb')
            file.seek(0)
            file.readinto(mbr)
            tamanio_total = mbr.mbr_tamano - ctypes.sizeof(structs.MBR)
            dot += "<tr>\n"
            dot += "<td>\n"
            dot += "<table color='orange' cellspacing='0'>\n"
            dot += "    <tr>\n"
            dot += "    <td>   MBR </td>\n"
            dot += "    </tr>\n"
            dot += "</table>\n"
            dot += "</td>\n"
            espacio_anterior = ctypes.sizeof(structs.MBR)
            for i, particion in enumerate(mbr.mbr_partitions):
                if particion.part_type == b'P':
                    if particion.part_start != espacio_anterior:
                        dot += "<td>\n"
                        dot += "    <table color='black' cellspacing='0' cellborder='0'>\n"
                        dot += "        <tr>\n"
                        dot += "        <td></td>\n"
                        dot += "        </tr>\n"
                        dot += "        <tr>\n"
                        dot += f"        <td>Libre<br /><FONT POINT-SIZE='15'>   {round(((particion.part_start - espacio_anterior) / tamanio_total) * 100, 3)}% del disco   </FONT></td>\n"
                        dot += "        </tr>\n"
                        dot += "        <tr>\n"
                        dot += "        <td></td>\n"
                        dot += "        </tr>\n"
                        dot += "    </table>\n"
                        dot += "</td>\n"
                    dot += "<td>\n"
                    dot += "    <table color='black' cellspacing='0' cellborder='0'>\n"
                    dot += "        <tr>\n"
                    dot += "        <td></td>\n"
                    dot += "        </tr>\n"
                    dot += "        <tr>\n"
                    dot += f"        <td>Primaria<br /><FONT POINT-SIZE='15'>   {round(((particion.part_s) / tamanio_total) * 100, 3)}% del disco   </FONT></td>\n"
                    dot += "        </tr>\n"
                    dot += "        <tr>\n"
                    dot += "        <td></td>\n"
                    dot += "        </tr>\n"
                    dot += "    </table>\n"
                    dot += "</td>\n"
                    espacio_anterior = particion.part_start + particion.part_s
                    
                elif particion.part_type == b'E':
                    if particion.part_start != espacio_anterior:
                        dot += "<td>\n"
                        dot += "    <table color='black' cellspacing='0' cellborder='0'>\n"
                        dot += "        <tr>\n"
                        dot += "        <td></td>\n"
                        dot += "        </tr>\n"
                        dot += "        <tr>\n"
                        dot += f"        <td>Libre<br /><FONT POINT-SIZE='15'>   {round(((particion.part_start - espacio_anterior) / tamanio_total) * 100, 3)}% del disco   </FONT></td>\n"
                        dot += "        </tr>\n"
                        dot += "        <tr>\n"
                        dot += "        <td></td>\n"
                        dot += "        </tr>\n"
                        dot += "    </table>\n"
                        dot += "</td>\n"

                    tmp = structs.EBR()
                    file.seek(particion.part_start)
                    contenido_binario = file.read(ctypes.sizeof(tmp))
                    ctypes.memmove(ctypes.byref(tmp), contenido_binario, ctypes.sizeof(tmp))
                    espacio_anterior = particion.part_start + particion.part_s
                    espacio_anterior_logic = particion.part_start
                    dot += "<td>\n"
                    dot += "    <table color='orange' cellspacing='0' cellpadding='0'>\n"
                    dot += "        <tr cellspacing='0'>\n"
                    dot += "        <td>    Extendida    </td>\n"
                    dot += "        </tr>\n"

                    dot += "<tr cellspacing='0'>\n"
                    dot += "    <td cellspacing='0'>\n"
                    dot += "        <table color='orange' border='1' cellspacing='0'>\n"
                    dot += "            <tr>\n"

                    while True:
                        if tmp.part_next == -1:
                            break
                        if tmp.part_start != espacio_anterior_logic:
                            dot += f"<td>Libre<br /><FONT POINT-SIZE='15'>   {round(((tmp.part_start - espacio_anterior_logic) / tamanio_total) * 100, 3)}% del disco   </FONT></td>\n"

                        dot += "<td>EBR</td>"
                        dot += f"<td>Logica<br /><FONT POINT-SIZE='15'>   {round(((tmp.part_s) / tamanio_total) * 100, 3)}% del disco   </FONT></td>"

                        espacio_anterior_logic = tmp.part_start + tmp.part_s
                        file.seek(tmp.part_next)
                        contenido_binario = file.read(ctypes.sizeof(tmp))
                        ctypes.memmove(ctypes.byref(tmp), contenido_binario, ctypes.sizeof(tmp))
                    
                    if ((particion.part_start + particion.part_s) > espacio_anterior_logic):
                        dot += f"<td>Libre<br /><FONT POINT-SIZE='15'>   {round((((particion.part_start + particion.part_s) - espacio_anterior_logic) / tamanio_total) * 100, 3)}% del disco   </FONT></td>\n"
                    
                    dot += "            </tr>\n"
                    dot += "        </table>\n"
                    dot += "    </td>\n"
                    dot += "</tr>\n"
                    
                    dot += "    </table>\n"
                    dot += "</td>\n"
            file.close()

            if mbr.mbr_tamano > espacio_anterior:
                dot += "<td>\n"
                dot += "    <table color='black' cellspacing='0' cellborder='0'>\n"
                dot += "        <tr>\n"
                dot += "        <td></td>\n"
                dot += "        </tr>\n"
                dot += "        <tr>\n"
                dot += f"        <td>Libre<br /><FONT POINT-SIZE='15'>   {round(((tamanio_total - espacio_anterior) / tamanio_total) * 100, 3)}% del disco   </FONT></td>\n"
                dot += "        </tr>\n"
                dot += "        <tr>\n"
                dot += "        <td></td>\n"
                dot += "        </tr>\n"
                dot += "    </table>\n"
                dot += "</td>\n"

            dot += "</tr>\n"

        except FileNotFoundError:
            print("error")
            pass

        dot += '</table>>];\n'
        dot += '}'
        print(dot)
        
    def reporte_inode(self):
        print("HACER REPORTE INODE")
        print(self.name)
        print(self.path)
        print(self.id)
        print(self.ruta)

        mounted = find_mounted(self.id)
        if(mounted == None):
            print("ID {self.id} no encontrado, verifique su entrada")
            return

        if not os.path.exists(self.path):
            os.makedirs(self.path)


        file = open(mounted.path, "rb+")
        sblock = structs.SuperBloque()
        file.seek(mounted.part_start)
        file.readinto(sblock)

        cantidad_inodos = 0
        read_on = sblock.s_bm_inode_start
        file.seek(read_on)
        bit = file.read(1)

        dot = 'digraph G {\n'
        dot += f'label="Reporte de Inodos";\n'
        dot += 'labelloc=top;\n'
        dot += 'edge [ fontname="Courier New", fontsize=20];\n'
        dot += 'node [ shape="box", fontsize=26];\n'
        dot += 'n_1 [label=<\n'
        dot += "<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='8' cellpadding='0'>\n"
        total_activos = 0
        while cantidad_inodos < sblock.s_inodes_count:
            if bit == b'0':
                cantidad_inodos += 1
                read_on += 1
                file.seek(read_on)
                bit = file.read(1)
                continue
            if total_activos == 0 or total_activos == 5:
                dot += "<TR>\n"
            read_on_i = sblock.s_inode_start + (sblock.s_inode_size * cantidad_inodos)
            inodo = structs.Inodo()
            file.seek(read_on_i)
            file.readinto(inodo)
            # print("*****************************************")
            # print(f"Inodo {cantidad_inodos}")
            # print("i_uid", inodo.i_uid)
            # print("i_gid", inodo.i_gid)
            # print("i_type", inodo.i_type)
            # print("i_s", inodo.i_s)
            # print("i_perm", inodo.i_perm)
            dot += "<TD>\n"
            dot += "    <TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0' cellpadding='0'>\n"
            dot += f"        <TR><TD colspan='3' BGCOLOR='{'#f1948a' if inodo.i_type == b'0' else '#f4d03f'}'> Inodo {cantidad_inodos} </TD></TR>\n"
            dot += f"        <TR><TD colspan='1'><FONT POINT-SIZE='15'>  i_uid  </FONT></TD><TD colspan='2'><FONT POINT-SIZE='15'>{inodo.i_uid}</FONT></TD></TR>\n"
            dot += f"        <TR><TD colspan='1'><FONT POINT-SIZE='15'>  i_gid  </FONT></TD><TD colspan='2'><FONT POINT-SIZE='15'>{inodo.i_gid}</FONT></TD></TR>\n"
            dot += f"        <TR><TD colspan='1'><FONT POINT-SIZE='15'>  i_s  </FONT></TD><TD colspan='2'><FONT POINT-SIZE='15'>{inodo.i_s}</FONT></TD></TR>\n"
            fecha_hora = datetime.fromtimestamp(inodo.i_atime)
            fecha_formateada = fecha_hora.strftime("%d-%m-%Y %H:%M:%S")
            dot += f"        <TR><TD colspan='1'><FONT POINT-SIZE='15'>  i_atime  </FONT></TD><TD colspan='2'><FONT POINT-SIZE='15'>{fecha_formateada}</FONT></TD></TR>\n"
            fecha_hora = datetime.fromtimestamp(inodo.i_ctime)
            fecha_formateada = fecha_hora.strftime("%d-%m-%Y %H:%M:%S")
            dot += f"        <TR><TD colspan='1'><FONT POINT-SIZE='15'>  i_ctime  </FONT></TD><TD colspan='2'><FONT POINT-SIZE='15'>{fecha_formateada}</FONT></TD></TR>\n"
            fecha_hora = datetime.fromtimestamp(inodo.i_mtime)
            fecha_formateada = fecha_hora.strftime("%d-%m-%Y %H:%M:%S")
            dot += f"        <TR><TD colspan='1'><FONT POINT-SIZE='15'>  i_mtime  </FONT></TD><TD colspan='2'><FONT POINT-SIZE='15'>{fecha_formateada}</FONT></TD></TR>\n"
            dot += "<TR><TD colspan='3'>\n"
            dot += "<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0' cellpadding='0'>\n"
            for i in range(5):
                dot += "<TR>\n"
                dot += f"<TD><FONT COLOR='#21618c' POINT-SIZE='15'>  <b>i_b{(i+1)+(i*2)}  </b></FONT></TD>\n"
                dot += f"<TD><FONT POINT-SIZE='15'>  {inodo.i_block[i+(i*2)]}</FONT></TD>\n"
                dot += f"<TD><FONT COLOR='#21618c' POINT-SIZE='15'>  <b>i_b{(i+2)+(i*2)}  </b></FONT></TD>\n"
                dot += f"<TD><FONT POINT-SIZE='15'>  {inodo.i_block[(i+1)+(i*2)]}</FONT></TD>\n"
                dot += f"<TD><FONT COLOR='#21618c' POINT-SIZE='15'>  <b>i_b{(i+3)+(i*2)}  </b></FONT></TD>\n"
                dot += f"<TD><FONT POINT-SIZE='15'>  {inodo.i_block[(i+2)+(i*2)]}</FONT></TD>\n"
                dot += "</TR>\n"
                
                # print(i)
            dot += "    </TABLE>\n"
            dot += "</TD></TR>\n"
            dot += f"        <TR><TD colspan='1'><FONT POINT-SIZE='15'>  i_type  </FONT></TD><TD colspan='2'><FONT POINT-SIZE='15'>{inodo.i_type.decode()}</FONT></TD></TR>\n"
            dot += f"        <TR><TD colspan='1'><FONT POINT-SIZE='15'>  i_perm  </FONT></TD><TD colspan='2'><FONT POINT-SIZE='15'>{inodo.i_perm}</FONT></TD></TR>\n"
            dot += "    </TABLE>\n"
            dot += "</TD>\n"
            
            read_on += 1
            file.seek(read_on)
            bit = file.read(1)
            cantidad_inodos += 1
            total_activos += 1
            if total_activos != 0 and total_activos == 5:
                dot += "</TR>\n"
                total_activos = 0

        if total_activos != 0 and (total_activos) != 5:
            dot += "</TR>\n"

        file.close()
        dot += '</TABLE>>];\n'
        dot += '}'
        print(dot)
        pyperclip.copy(dot)

    def reporte_block(self):
        print("HACER REPORTE BLOCK")
        print(self.name)
        print(self.path)
        print(self.id)
        print(self.ruta)

        mounted = find_mounted(self.id)
        if(mounted == None):
            print("ID {self.id} no encontrado, verifique su entrada")
            return

        if not os.path.exists(self.path):
            os.makedirs(self.path)


        file = open(mounted.path, "rb+")
        sblock = structs.SuperBloque()
        file.seek(mounted.part_start)
        file.readinto(sblock)

        cantidad_bloques = 0
        read_on = sblock.s_bm_block_start
        file.seek(read_on)
        bit = file.read(1)

        dot = 'digraph G {\n'
        dot += f'label="Reporte de Bloques";\n'
        dot += 'labelloc=top;\n'
        dot += 'edge [ fontname="Courier New", fontsize=20];\n'
        dot += 'node [ shape="box", fontsize=26];\n'
        dot += 'n_1 [label=<\n'
        dot += "<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='8' cellpadding='0'>\n"
        total_activos = 0
        while cantidad_bloques < sblock.s_blocks_count:
            if bit == b'0':
                cantidad_bloques += 1
                read_on += 1
                file.seek(read_on)
                bit = file.read(1)
                continue
            if total_activos == 0 or total_activos == 5:
                dot += "<TR>\n"
            read_on_b = sblock.s_block_start + (sblock.s_block_size * cantidad_bloques)
            # print("tipo de bloque", cantidad_bloques)
            # print(bit)
            if bit == b'd':
                bloque_carpeta = structs.BloqueCarpeta()
                file.seek(read_on_b)
                file.readinto(bloque_carpeta)
                dot += "<TD>\n"
                dot += "<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0' cellpadding='0'>\n"
                dot += f"    <TR><TD colspan='2' BGCOLOR='#84b6f4'> Bloque Carpeta {cantidad_bloques} </TD></TR>\n"
                dot += f"<TR><TD><FONT POINT-SIZE='15' COLOR='#6c3483'>  <b>b_name</b>  </FONT></TD><TD><FONT POINT-SIZE='15' COLOR='#6c3483'><b>b_inode</b></FONT></TD></TR>"
                for i in range(4):
                    dot += f"    <TR><TD><FONT POINT-SIZE='15'>  {bloque_carpeta.b_content[i].b_name.decode()}  </FONT></TD><TD><FONT POINT-SIZE='15'>{bloque_carpeta.b_content[i].b_inodo}</FONT></TD></TR>\n"
                dot += "</TABLE>\n"
                dot += "</TD>\n"
            elif bit == b'f':
                bloque_archivo = structs.BloqueArchivo()
                file.seek(read_on_b)
                file.readinto(bloque_archivo)
                dot += "<TD>\n"
                dot += "<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0' cellpadding='0'>\n"
                dot += f"    <TR><TD BGCOLOR='#fdfd96'> Bloque Archivo {cantidad_bloques} </TD></TR>\n"
                nuevo_texto = ""
                for i in range(0, len(bloque_archivo.b_content), 16):
                    nuevo_texto += bloque_archivo.b_content[i:i+16].decode() + "<br/>"
                if len(bloque_archivo.b_content) > 0:
                    dot += f"<TR><TD><FONT POINT-SIZE='15'>{nuevo_texto}</FONT></TD></TR>\n"
                dot += "</TABLE>\n"
                dot += "</TD>\n"
            
            read_on += 1
            file.seek(read_on)
            bit = file.read(1)
            cantidad_bloques += 1
            total_activos += 1
            if total_activos != 0 and total_activos == 5:
                dot += "</TR>\n"
                total_activos = 0

        if total_activos != 0 and (total_activos) != 5:
            dot += "</TR>\n"

        file.close()
        dot += '</TABLE>>];\n'
        dot += '}'
        # print(dot)
        pyperclip.copy(dot)

    def reporte_bm_inode(self):
        print("HACER REPORTE BM INODE")
        print(self.name)
        print(self.path)
        print(self.id)
        print(self.ruta)

        mounted = find_mounted(self.id)
        if(mounted == None):
            print("ID {self.id} no encontrado, verifique su entrada")
            return

        if not os.path.exists(self.path):
            os.makedirs(self.path)


        file = open(mounted.path, "rb+")
        sblock = structs.SuperBloque()
        file.seek(mounted.part_start)
        file.readinto(sblock)

        cantidad_inodos = 0
        read_on = sblock.s_bm_inode_start
        file.seek(read_on)
        bit = file.read(1)
        bits = ""
        total_activos = 0
        while cantidad_inodos < sblock.s_inodes_count:
            if total_activos == 20:
                bits += "\n"
            if bit == b'0':
                bits += "0\t"
                total_activos += 1
                read_on += 1
                file.seek(read_on)
                bit = file.read(1)
            else:
                bits += "1\t"
                
                read_on += 1
                file.seek(read_on)
                bit = file.read(1)
                total_activos += 1

            cantidad_inodos += 1
            if total_activos != 0 and total_activos == 20:
                bits += "\n"
                total_activos = 0

        file.close()
        archivo = open("mi_archivo.txt", "w")
        archivo.write(bits)
        archivo.close()
    
    def reporte_bm_bloc(self):
        print("HACER REPORTE BM BLOCK")
        print(self.name)
        print(self.path)
        print(self.id)
        print(self.ruta)

        mounted = find_mounted(self.id)
        if(mounted == None):
            print("ID {self.id} no encontrado, verifique su entrada")
            return

        if not os.path.exists(self.path):
            os.makedirs(self.path)


        file = open(mounted.path, "rb+")
        sblock = structs.SuperBloque()
        file.seek(mounted.part_start)
        file.readinto(sblock)

        cantidad_bloques = 0
        read_on = sblock.s_bm_block_start
        file.seek(read_on)
        bit = file.read(1)
        bits = ""
        total_activos = 0
        while cantidad_bloques < sblock.s_inodes_count:
            if total_activos == 20:
                bits += "\n"
            if bit == b'0':
                bits += "0\t"
                total_activos += 1
                read_on += 1
                file.seek(read_on)
                bit = file.read(1)
            else:
                bits += "1\t"
                
                read_on += 1
                file.seek(read_on)
                bit = file.read(1)
                total_activos += 1

            cantidad_bloques += 1
            if total_activos != 0 and total_activos == 20:
                bits += "\n"
                total_activos = 0

        file.close()
        archivo = open("mi_archivo2.txt", "w")
        archivo.write(bits)
        archivo.close()