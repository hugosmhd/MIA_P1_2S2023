import os
import struct
from datetime import datetime
import ctypes
import pyperclip

import structs
from analizador import analizador
from _global._global import particiones_montadas, session_inciada
from comandos.mount.mount import find_mounted, find_mounted_rep
from comandos.mkfs.mkfs import join_file, find_file, find_carpeta_archivo
from comandos.mkfile.mkfile import mkfile
from comandos.mkdir.mkdir import mkdir
from comandos.mkgrp.mkgrp import mkgrp
from comandos.mkusr.mkusr import mkusr
from comandos.move.move import move
from comandos.rename.rename import rename

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
        elif(self.name == 'bm_block'):
            self.reporte_bm_block()
        elif(self.name == 'tree'):
            self.reporte_tree()
        elif(self.name == 'sb'):
            self.reporte_sb()
        elif(self.name == 'file'):
            self.reporte_file()
        elif(self.name == 'journaling'):
            self.reporte_journaling()
    
    def reporte_mbr(self):
        print("HACER REPORTE MBR")
        # print(self.name)
        # print(self.path)
        # print(self.id)
        # print(self.ruta)

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
                    status = find_mounted_rep(particion.part_name.decode(), mounted.path)
                    dot += f'<TD><FONT POINT-SIZE="15">{"1" if status else "0"}</FONT></TD></TR>\n'
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
                        status = find_mounted_rep(tmp.part_name.decode(), mounted.path)
                        dot += f'<TD><FONT POINT-SIZE="15">{"1" if status else "0"}</FONT></TD></TR>\n'
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
        pyperclip.copy(dot)

    def reporte_disk(self):
        print("HACER REPORTE DISK")

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
        dot += "<table border='0' cellborder='0' color='blue' cellspacing='0'>\n"
        try:
            mbr = structs.MBR()
            file = open(mounted.path, 'rb')
            file.seek(0)
            file.readinto(mbr)
            tamanio_total = mbr.mbr_tamano - ctypes.sizeof(structs.MBR)
            dot += "<tr>\n"
            dot += "<td>\n"
            dot += "<table color='#229954' border='2' cellspacing='0'>\n"
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
                    dot += "    <table color='#7d3c98' border='3' cellspacing='0' cellborder='0'>\n"
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
                        dot += "    <table color='#2874a6' border='3' cellspacing='0' cellborder='0'>\n"
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
                dot += "    <table color='#2874a6' border='3' cellspacing='0' cellborder='0'>\n"
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
        pyperclip.copy(dot)
        
    def reporte_inode(self):
        print("HACER REPORTE INODE")

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
        pyperclip.copy(dot)

    def reporte_block(self):
        print("HACER REPORTE BLOCK")

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
        pyperclip.copy(dot)

    def reporte_bm_inode(self):
        print("HACER REPORTE BM INODE")

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
    
    def reporte_bm_block(self):
        print("HACER REPORTE BM BLOCK")

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

    def reporte_tree(self):
        print("HACER REPORTE TREE")

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
        dot += 'overlap=false;'
        dot += 'ranksep=1;'
        dot += "graph [\n"
        dot += '    fontname="Helvetica,Arial,sans-serif"\n'
        dot += '    rankdir = "LR"\n'
        dot += "]\n"
        dot += "node [\n"
        dot += '    fontname="Helvetica,Arial,sans-serif"\n'
        dot += "    shape=record\n"
        dot += "    style=filled\n"
        dot += "    fillcolor=gray95\n"
        dot += "]\n"
        enlaces = ""

        total_activos = 0
        while cantidad_inodos < sblock.s_inodes_count:
            if bit == b'0':
                cantidad_inodos += 1
                read_on += 1
                file.seek(read_on)
                bit = file.read(1)
                continue
            read_on_i = sblock.s_inode_start + (sblock.s_inode_size * cantidad_inodos)
            inodo = structs.Inodo()
            file.seek(read_on_i)
            file.readinto(inodo)
            dot += f"inodo_{cantidad_inodos} [\n"
            dot += "    shape=plain\n"
            dot += "    label=<<table border='0' cellborder='1' cellspacing='0' cellpadding='0'>\n"
            dot += f"        <tr> <td port='i_e' colspan='2' BGCOLOR='{'#f1948a' if inodo.i_type == b'0' else '#f4d03f'}'> <b>Inodo {cantidad_inodos}</b> </td> </tr>\n"
            dot += f"        <tr> <td>i_uid</td><td>{inodo.i_uid}</td> </tr>\n"
            dot += f"        <tr> <td>i_gid</td><td port='ss1'>{inodo.i_gid}</td></tr>\n"
            dot += f"        <tr> <td>i_s</td><td port='ss2'>{inodo.i_s}</td> </tr>\n"
            dot += f"        <tr> <td>i_type</td><td port='ss2'>{inodo.i_type.decode()}</td> </tr>\n"
            dot += f"        <tr> <td>i_perm</td><td port='ss2'>{inodo.i_perm}</td> </tr>\n"
            fecha_hora = datetime.fromtimestamp(inodo.i_atime)
            fecha_formateada = fecha_hora.strftime("%d-%m-%Y %H:%M:%S")
            dot += f"        <tr> <td>i_atime</td><td port='ss3'>{fecha_formateada}</td> </tr>\n"
            fecha_hora = datetime.fromtimestamp(inodo.i_ctime)
            fecha_formateada = fecha_hora.strftime("%d-%m-%Y %H:%M:%S")
            dot += f"        <tr> <td>i_ctime</td><td port='ss3'>{fecha_formateada}</td> </tr>\n"
            fecha_hora = datetime.fromtimestamp(inodo.i_mtime)
            fecha_formateada = fecha_hora.strftime("%d-%m-%Y %H:%M:%S")
            dot += f"        <tr> <td>i_ctime</td><td port='ss3'>{fecha_formateada}</td> </tr>\n"
            for i in range(15):
                if inodo.i_block[i] != -1:
                    dot += f"        <tr> <td port='a_u{inodo.i_block[i]}'>ap{i+1}</td><td port='a_s{inodo.i_block[i]}'>{inodo.i_block[i]}</td> </tr>\n"
                    enlaces += f"inodo_{cantidad_inodos}:a_s{inodo.i_block[i]} -> bloque_{inodo.i_block[i]}:b_e;\n"
                else:
                    dot += f"        <tr> <td>ap{i+1}</td><td>{inodo.i_block[i]}</td> </tr>\n"
            dot += "    </table>>\n"
            dot += "]\n"
            
            read_on += 1
            file.seek(read_on)
            bit = file.read(1)
            cantidad_inodos += 1

        cantidad_bloques = 0
        read_on = sblock.s_bm_block_start
        file.seek(read_on)
        bit = file.read(1)

        while cantidad_bloques < sblock.s_blocks_count:
            if bit == b'0':
                cantidad_bloques += 1
                read_on += 1
                file.seek(read_on)
                bit = file.read(1)
                continue
            read_on_b = sblock.s_block_start + (sblock.s_block_size * cantidad_bloques)
            if bit == b'd':
                bloque_carpeta = structs.BloqueCarpeta()
                file.seek(read_on_b)
                file.readinto(bloque_carpeta)
                dot += f"bloque_{cantidad_bloques} [\n"
                dot += "    shape=plain\n"
                dot += "    label=<<table border='0' cellborder='1' cellspacing='0' cellpadding='0'>\n"
                dot += f"        <tr> <td port='b_e' colspan='2' bgcolor='#84b6f4'> <b>  Bloque Carpeta {cantidad_bloques}</b> </td> </tr>\n"
                dot += f"       <tr><td><font point-size='15' color='#6c3483'>  <b>b_name  </b>  </font></td><td><font point-size='15' color='#6c3483'>  <b>b_inode</b>  </font></td></tr>\n"
                for i in range(4):
                    if bloque_carpeta.b_content[i].b_inodo != -1 and bloque_carpeta.b_content[i].b_name.decode() != "." and bloque_carpeta.b_content[i].b_name.decode() != "..":
                        dot += f"    <tr><td port='a_u{bloque_carpeta.b_content[i].b_inodo}'><font point-size='15'>  {bloque_carpeta.b_content[i].b_name.decode()}  </font></td><td port='a_s{bloque_carpeta.b_content[i].b_inodo}'><font point-size='15'>{bloque_carpeta.b_content[i].b_inodo}</font></td></tr>\n"
                        enlaces += f"bloque_{cantidad_bloques}:a_s{bloque_carpeta.b_content[i].b_inodo} -> inodo_{bloque_carpeta.b_content[i].b_inodo}:i_e;\n"
                    else:
                        dot += f"    <tr><td><font point-size='15'>  {bloque_carpeta.b_content[i].b_name.decode()}  </font></td><td><font point-size='15'>{bloque_carpeta.b_content[i].b_inodo}</font></td></tr>\n"
                dot += "    </table>>\n"
                dot += "]\n"
            elif bit == b'f':
                bloque_archivo = structs.BloqueArchivo()
                file.seek(read_on_b)
                file.readinto(bloque_archivo)
                dot += f"bloque_{cantidad_bloques} [\n"
                dot += "    shape=plain\n"
                dot += "    label=<<table border='0' cellborder='1' cellspacing='0' cellpadding='0'>\n"
                dot += f"        <tr> <td port='b_e' bgcolor='#fdfd96'> <b>  Bloque Archivo {cantidad_bloques}</b>   </td> </tr>\n"

                nuevo_texto = ""
                for i in range(0, len(bloque_archivo.b_content), 16):
                    nuevo_texto += bloque_archivo.b_content[i:i+16].decode() + "<br/>"
                if len(bloque_archivo.b_content) > 0:
                    dot += f"    <tr><td><font point-size='15'>  {nuevo_texto}  </font></td></tr>\n"
                dot += "    </table>>\n"
                dot += "]\n"
            elif bit == b's':
                bloque_apuntador = structs.BloqueApuntadores()
                file.seek(read_on_b)
                file.readinto(bloque_apuntador)
                dot += f"bloque_{cantidad_bloques} [\n"
                dot += "    shape=plain\n"
                dot += "    label=<<table border='0' cellborder='1' cellspacing='0' cellpadding='0'>\n"
                dot += f"        <tr> <td port='b_e' colspan='2' bgcolor='#77dd77'> <b>  Bloque Indirecto S {cantidad_bloques}</b>   </td> </tr>\n"
                for i in range(16):
                    if bloque_apuntador.b_pointers[i] != -1:
                        dot += f"    <tr><td port='a_u{bloque_apuntador.b_pointers[i]}'><font point-size='15'>  b_pointer[{i}]</font></td><td port='a_s{bloque_apuntador.b_pointers[i]}'><font point-size='15'>{bloque_apuntador.b_pointers[i]}</font></td></tr>\n"
                        enlaces += f"bloque_{cantidad_bloques}:a_s{bloque_apuntador.b_pointers[i]} -> bloque_{bloque_apuntador.b_pointers[i]}:b_e;\n"
                    else:
                        dot += f"    <tr><td><font point-size='15'>  b_pointer[{i}]  </font></td><td><font point-size='15'>{bloque_apuntador.b_pointers[i]}</font></td></tr>\n"
                dot += "    </table>>\n"
                dot += "]\n"
            elif bit == b'l':
                bloque_apuntador = structs.BloqueApuntadores()
                file.seek(read_on_b)
                file.readinto(bloque_apuntador)
                dot += f"bloque_{cantidad_bloques} [\n"
                dot += "    shape=plain\n"
                dot += "    label=<<table border='0' cellborder='1' cellspacing='0' cellpadding='0'>\n"
                dot += f"        <tr> <td port='b_e' colspan='2' bgcolor='#fdcae1'> <b>  Bloque Indirecto D {cantidad_bloques}</b>   </td> </tr>\n"
                for i in range(16):
                    if bloque_apuntador.b_pointers[i] != -1:
                        dot += f"    <tr><td port='a_u{bloque_apuntador.b_pointers[i]}'><font point-size='15'>  b_pointer[{i}]</font></td><td port='a_s{bloque_apuntador.b_pointers[i]}'><font point-size='15'>{bloque_apuntador.b_pointers[i]}</font></td></tr>\n"
                        enlaces += f"bloque_{cantidad_bloques}:a_s{bloque_apuntador.b_pointers[i]} -> bloque_{bloque_apuntador.b_pointers[i]}:b_e;\n"
                    else:
                        dot += f"    <tr><td><font point-size='15'>  b_pointer[{i}]  </font></td><td><font point-size='15'>{bloque_apuntador.b_pointers[i]}</font></td></tr>\n"
                dot += "    </table>>\n"
                dot += "]\n"
            elif bit == b't':
                bloque_apuntador = structs.BloqueApuntadores()
                file.seek(read_on_b)
                file.readinto(bloque_apuntador)
                dot += f"bloque_{cantidad_bloques} [\n"
                dot += "    shape=plain\n"
                dot += "    label=<<table border='0' cellborder='1' cellspacing='0' cellpadding='0'>\n"
                dot += f"        <tr> <td port='b_e' colspan='2' bgcolor='#fdcae1'> <b>  Bloque Indirecto T {cantidad_bloques}</b>   </td> </tr>\n"
                for i in range(16):
                    if bloque_apuntador.b_pointers[i] != -1:
                        dot += f"    <tr><td port='a_u{bloque_apuntador.b_pointers[i]}'><font point-size='15'>  b_pointer[{i}]</font></td><td port='a_s{bloque_apuntador.b_pointers[i]}'><font point-size='15'>{bloque_apuntador.b_pointers[i]}</font></td></tr>\n"
                        enlaces += f"bloque_{cantidad_bloques}:a_s{bloque_apuntador.b_pointers[i]} -> bloque_{bloque_apuntador.b_pointers[i]}:b_e;\n"
                    else:
                        dot += f"    <tr><td><font point-size='15'>  b_pointer[{i}]  </font></td><td><font point-size='15'>{bloque_apuntador.b_pointers[i]}</font></td></tr>\n"
                dot += "    </table>>\n"
                dot += "]\n"
            
            read_on += 1
            file.seek(read_on)
            bit = file.read(1)
            cantidad_bloques += 1

        file.close()
        dot += enlaces
        dot += '}'

        with open("./rep.dot", "w") as fich:
            fich.write(dot)
            fich.close()

        rep_dot = "./rep.dot"
        rep_pdf = "./rep.pdf"
        crear_pdf = f"dot -Tpdf {rep_dot} -o {rep_pdf}"
        os.system(crear_pdf)
        pyperclip.copy(dot)

    def reporte_sb(self):
        print("HACER REPORTE SB")

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

        dot = 'digraph G {\n'
        dot += f'label="Reporte del Superbloque";\n'
        dot += 'labelloc=top;\n'
        dot += 'edge [ fontname="Courier New", fontsize=20];\n'
        dot += 'node [ shape="box", fontsize=26];\n'
        dot += 'n_1 [label=<\n'
        dot += "<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0' cellpadding='1'>\n"
        dot += f"   <TR><TD colspan='2' BGCOLOR='#196f3d'> Reporte de SUPERBLOQUE </TD></TR>\n"
        dot += f"   <TR><TD BGCOLOR='#58d68d'><FONT POINT-SIZE='15'>  <b>s_filesystem_type</b>  </FONT></TD><TD BGCOLOR='#58d68d'><FONT POINT-SIZE='15'>{sblock.s_filesystem_type}</FONT></TD></TR>\n"
        dot += f"   <TR><TD><FONT POINT-SIZE='15'>  <b>s_inodes_count</b>  </FONT></TD><TD><FONT POINT-SIZE='15'>{sblock.s_inodes_count}</FONT></TD></TR>\n"
        dot += f"   <TR><TD BGCOLOR='#58d68d'><FONT POINT-SIZE='15'>  <b>s_blocks_count</b>  </FONT></TD><TD BGCOLOR='#58d68d'><FONT POINT-SIZE='15'>{sblock.s_blocks_count}</FONT></TD></TR>\n"
        dot += f"   <TR><TD><FONT POINT-SIZE='15'>  <b>s_free_blocks_count</b>  </FONT></TD><TD><FONT POINT-SIZE='15'>{sblock.s_free_blocks_count}</FONT></TD></TR>\n"
        dot += f"   <TR><TD BGCOLOR='#58d68d'><FONT POINT-SIZE='15'>  <b>s_free_inodes_count</b>  </FONT></TD><TD BGCOLOR='#58d68d'><FONT POINT-SIZE='15'>{sblock.s_free_inodes_count}</FONT></TD></TR>\n"
        fecha_hora = datetime.fromtimestamp(sblock.s_mtime)
        fecha_formateada = fecha_hora.strftime("%d-%m-%Y %H:%M:%S")
        dot += f"   <TR><TD><FONT POINT-SIZE='15'>  <b>s_mtime</b>  </FONT></TD><TD><FONT POINT-SIZE='15'>{fecha_formateada}</FONT></TD></TR>\n"
        fecha_hora = datetime.fromtimestamp(sblock.s_umtime)
        fecha_formateada = fecha_hora.strftime("%d-%m-%Y %H:%M:%S")
        dot += f"   <TR><TD BGCOLOR='#58d68d'><FONT POINT-SIZE='15'>  <b>s_umtime</b>  </FONT></TD><TD BGCOLOR='#58d68d'><FONT POINT-SIZE='15'>{fecha_formateada}</FONT></TD></TR>\n"
        dot += f"   <TR><TD><FONT POINT-SIZE='15'>  <b>s_mnt_count</b>  </FONT></TD><TD><FONT POINT-SIZE='15'>{sblock.s_mnt_count}</FONT></TD></TR>\n"
        dot += f"   <TR><TD BGCOLOR='#58d68d'><FONT POINT-SIZE='15'>  <b>s_magic</b>  </FONT></TD><TD BGCOLOR='#58d68d'><FONT POINT-SIZE='15'>{sblock.s_magic}</FONT></TD></TR>\n"
        dot += f"   <TR><TD><FONT POINT-SIZE='15'>  <b>s_inode_size</b>  </FONT></TD><TD><FONT POINT-SIZE='15'>{sblock.s_inode_size}</FONT></TD></TR>\n"
        dot += f"   <TR><TD BGCOLOR='#58d68d'><FONT POINT-SIZE='15'>  <b>s_block_size</b>  </FONT></TD><TD BGCOLOR='#58d68d'><FONT POINT-SIZE='15'>{sblock.s_block_size}</FONT></TD></TR>\n"
        dot += f"   <TR><TD><FONT POINT-SIZE='15'>  <b>s_first_ino</b>  </FONT></TD><TD><FONT POINT-SIZE='15'>{sblock.s_first_ino}</FONT></TD></TR>\n"
        dot += f"   <TR><TD BGCOLOR='#58d68d'><FONT POINT-SIZE='15'>  <b>s_first_blo</b>  </FONT></TD><TD BGCOLOR='#58d68d'><FONT POINT-SIZE='15'>{sblock.s_first_blo}</FONT></TD></TR>\n"
        dot += f"   <TR><TD><FONT POINT-SIZE='15'>  <b>s_bm_inode_start</b>  </FONT></TD><TD><FONT POINT-SIZE='15'>{sblock.s_bm_inode_start}</FONT></TD></TR>\n"
        dot += f"   <TR><TD BGCOLOR='#58d68d'><FONT POINT-SIZE='15'>  <b>s_bm_block_start</b>  </FONT></TD><TD BGCOLOR='#58d68d'><FONT POINT-SIZE='15'>{sblock.s_bm_block_start}</FONT></TD></TR>\n"
        dot += f"   <TR><TD><FONT POINT-SIZE='15'>  <b>s_inode_start</b>  </FONT></TD><TD><FONT POINT-SIZE='15'>{sblock.s_inode_start}</FONT></TD></TR>\n"
        dot += f"   <TR><TD BGCOLOR='#58d68d'><FONT POINT-SIZE='15'>  <b>s_block_start</b>  </FONT></TD><TD BGCOLOR='#58d68d'><FONT POINT-SIZE='15'>{sblock.s_block_start}</FONT></TD></TR>\n"
            
        file.close()
        dot += '</TABLE>>];\n'
        dot += '}'
        pyperclip.copy(dot)
    
    def reporte_file(self):
        print("HACER REPORTE FILE")

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

        # Hay que probar
        nuevo_mounted = session_inciada.mounted
        session_inciada.mounted = mounted
        directorio, archivo_ = os.path.split(self.ruta)
        indo_carpeta_archivo, i, _, __ = find_carpeta_archivo(sblock, directorio, session_inciada)
        if(i == -1):
            print(f"Error: Ruta especificada '{self.directorio}' no existe")
            return
        inodo_archivo, i_f = find_file(sblock, self.ruta, session_inciada.mounted.path, indo_carpeta_archivo)
        if(i_f == -1):
            print(f"Error: Ruta especificada '{self.ruta}' no existe")
            return

        session_inciada.mounted = nuevo_mounted

        txt = join_file(sblock, inodo_archivo, mounted.path)

        file.close()
        archivo = open("mi_archivo3.txt", "w")
        archivo.write(txt)
        archivo.close()

    def reporte_journaling(self):
        print("HACER REPORTE JOURNALING")

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

        if sblock.s_filesystem_type == 3:
            file = open(mounted.path, "rb+")
            journaling_actual = structs.Journaling()
            read_journaling = mounted.part_start + ctypes.sizeof(structs.SuperBloque)
            dot = 'digraph G {\n'
            dot += f'label="Reporte del Journaling";\n'
            dot += 'labelloc=top;\n'
            dot += 'edge [ fontname="Courier New", fontsize=20];\n'
            dot += 'node [ shape="box", fontsize=26];\n'
            dot += 'tabla_journaling [label=<\n'
            dot += "<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0' cellpadding='1'>\n"
            dot += "<TR>\n"
            dot += "    <TD BGCOLOR='#1c2833'><FONT COLOR='white'>  Operacion  </FONT></TD>\n"
            dot += "    <TD BGCOLOR='#1c2833'><FONT COLOR='white'>   Path   </FONT></TD>\n"
            dot += "    <TD BGCOLOR='#1c2833'><FONT COLOR='white'>   Contenido   </FONT></TD>\n"
            dot += "    <TD BGCOLOR='#1c2833'><FONT COLOR='white'>Fecha</FONT></TD>\n"
            dot += "</TR>\n"
            for _ in range(sblock.s_inodes_count):
                file.seek(read_journaling)
                file.readinto(journaling_actual)

                if(journaling_actual.fecha == 0):
                    break
                instancia = analizador.analizar(journaling_actual.comando.decode(), True)
                fecha_hora = datetime.fromtimestamp(journaling_actual.fecha)
                fecha_formateada = fecha_hora.strftime("%d-%m-%Y %H:%M:%S")
                if isinstance(instancia, mkfile):
                    dot += f"<TR>\n"
                    dot += f"    <TD><FONT POINT-SIZE='18'><b>mkfile</b></FONT></TD>\n"
                    nuevo_texto = ""
                    for i in range(0, len(instancia.path), 10):
                        nuevo_texto += instancia.path[i:i+10] + "<br/>"
                    dot += f"    <TD><FONT POINT-SIZE='15'>{nuevo_texto}</FONT></TD>\n"

                    content = instancia.file_contenido()
                    nuevo_texto = ""
                    for i in range(0, len(content), 30):
                        nuevo_texto += content[i:i+30] + "<br/>"
                    if len(content) > 0:
                        dot += f"    <TD><FONT POINT-SIZE='15'>{nuevo_texto}</FONT></TD>\n"
                    dot += f"    <TD><FONT POINT-SIZE='15'>{fecha_formateada}</FONT></TD>\n"
                    dot += f"</TR>\n"
                elif isinstance(instancia, mkdir):
                    dot += f"<TR>\n"
                    dot += f"    <TD><FONT POINT-SIZE='18'><b>mkdir</b></FONT></TD>\n"
                    nuevo_texto = ""
                    for i in range(0, len(instancia.path), 10):
                        nuevo_texto += instancia.path[i:i+10] + "<br/>"
                    dot += f"    <TD><FONT POINT-SIZE='15'>{nuevo_texto}</FONT></TD>\n"
                    dot += f"    <TD><FONT POINT-SIZE='15'>-</FONT></TD>\n"
                    dot += f"    <TD><FONT POINT-SIZE='15'>{fecha_formateada}</FONT></TD>\n"
                    dot += f"</TR>\n"
                elif isinstance(instancia, mkgrp):
                    if(instancia.tipo == 1):
                        dot += f"<TR>\n"
                        dot += f"    <TD><FONT POINT-SIZE='18'><b>mkgrp</b></FONT></TD>\n"
                        dot += f"    <TD><FONT POINT-SIZE='15'>/users.txt</FONT></TD>\n"
                        dot += f"    <TD><FONT POINT-SIZE='15'>{instancia.name}</FONT></TD>\n"
                        dot += f"    <TD><FONT POINT-SIZE='15'>{fecha_formateada}</FONT></TD>\n"
                        dot += f"</TR>\n"
                    elif(instancia.tipo == 2):
                        dot += f"<TR>\n"
                        dot += f"    <TD><FONT POINT-SIZE='18'><b>rmgrp</b></FONT></TD>\n"
                        dot += f"    <TD><FONT POINT-SIZE='15'>/users.txt</FONT></TD>\n"
                        dot += f"    <TD><FONT POINT-SIZE='15'>-</FONT></TD>\n"
                        dot += f"    <TD><FONT POINT-SIZE='15'>{fecha_formateada}</FONT></TD>\n"
                        dot += f"</TR>\n"
                elif isinstance(instancia, mkusr):
                    if(instancia.tipo == 1):
                        dot += f"<TR>\n"
                        dot += f"    <TD><FONT POINT-SIZE='18'><b>mkusr</b></FONT></TD>\n"
                        dot += f"    <TD><FONT POINT-SIZE='15'>/users.txt</FONT></TD>\n"
                        dot += f"    <TD><FONT POINT-SIZE='15'>{instancia.user}<br/>{instancia.password}</FONT></TD>\n"
                        dot += f"    <TD><FONT POINT-SIZE='15'>{fecha_formateada}</FONT></TD>\n"
                        dot += f"</TR>\n"
                    elif(instancia.tipo == 2):
                        dot += f"<TR>\n"
                        dot += f"    <TD><FONT POINT-SIZE='18'><b>rmusr</b></FONT></TD>\n"
                        dot += f"    <TD><FONT POINT-SIZE='15'>/users.txt</FONT></TD>\n"
                        dot += f"    <TD><FONT POINT-SIZE='15'>-</FONT></TD>\n"
                        dot += f"    <TD><FONT POINT-SIZE='15'>{fecha_formateada}</FONT></TD>\n"
                        dot += f"</TR>\n"
                elif isinstance(instancia, move):
                    dot += f"<TR>\n"
                    dot += f"    <TD><FONT POINT-SIZE='18'><b>move</b></FONT></TD>\n"
                    nuevo_texto = ""
                    for i in range(0, len(instancia.path), 10):
                        nuevo_texto += instancia.path[i:i+10] + "<br/>"
                    dot += f"    <TD><FONT POINT-SIZE='15'>{nuevo_texto}</FONT></TD>\n"
                    dot += f"    <TD><FONT POINT-SIZE='15'>-</FONT></TD>\n"
                    dot += f"    <TD><FONT POINT-SIZE='15'>{fecha_formateada}</FONT></TD>\n"
                    dot += f"</TR>\n"
                elif isinstance(instancia, rename):
                    dot += f"<TR>\n"
                    dot += f"    <TD><FONT POINT-SIZE='18'><b>rename</b></FONT></TD>\n"
                    nuevo_texto = ""
                    for i in range(0, len(instancia.path), 10):
                        nuevo_texto += instancia.path[i:i+10] + "<br/>"
                    dot += f"    <TD><FONT POINT-SIZE='15'>{nuevo_texto}</FONT></TD>\n"
                    dot += f"    <TD><FONT POINT-SIZE='15'>{instancia.name}</FONT></TD>\n"
                    dot += f"    <TD><FONT POINT-SIZE='15'>{fecha_formateada}</FONT></TD>\n"
                    dot += f"</TR>\n"
                read_journaling += ctypes.sizeof(structs.Journaling)

            
            file.close()
            dot += '</TABLE>>];\n'
            dot += '}'
            pyperclip.copy(dot)
