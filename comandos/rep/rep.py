import os
import struct
from datetime import datetime
import ctypes

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
            # fecha_hora = datetime.fromtimestamp(mbr.mbr_fecha_creacion)
            # fecha_formateada = fecha_hora.strftime("%d-%m-%Y %H:%M:%S")
            # dot += '<TR><TD colspan="2" BGCOLOR="#a569bd">                  MBR                  </TD></TR>\n'
            # dot += '<TR><TD><FONT POINT-SIZE="15">mbr_tamano</FONT></TD>\n'
            # dot += f'<TD><FONT POINT-SIZE="15">{mbr.mbr_tamano}</FONT></TD></TR>\n'
            # dot += '<TR><TD><FONT POINT-SIZE="15">mbr_fecha_creacion</FONT></TD>\n'
            # dot += f'<TD><FONT POINT-SIZE="15">{fecha_formateada}</FONT></TD></TR>\n'
            # dot += '<TR><TD><FONT POINT-SIZE="15">mbr_dsk_signature</FONT></TD>\n'
            # dot += f'<TD><FONT POINT-SIZE="15">{mbr.mbr_dsk_signature}</FONT></TD></TR>\n'
            # dot += '<TR><TD><FONT POINT-SIZE="15">dsk_fit</FONT></TD>\n'
            # dot += f'<TD><FONT POINT-SIZE="15">{mbr.dsk_fit.decode()}</FONT></TD></TR>\n'
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
                    

                    # dot += '<TR><TD colspan="2" BGCOLOR="#58d68d ">Particion</TD></TR>\n'
                    # dot += '<TR><TD><FONT POINT-SIZE="15">part_status</FONT></TD>\n'
                    # dot += f'<TD><FONT POINT-SIZE="15">{particion.part_status.decode()}</FONT></TD></TR>\n'
                    # dot += '<TR><TD><FONT POINT-SIZE="15">part_type</FONT></TD>\n'
                    # dot += f'<TD><FONT POINT-SIZE="15">{particion.part_type.decode()}</FONT></TD></TR>\n'
                    # dot += '<TR><TD><FONT POINT-SIZE="15">part_fit</FONT></TD>\n'
                    # dot += f'<TD><FONT POINT-SIZE="15">{particion.part_fit.decode()}</FONT></TD></TR>\n'
                    # dot += '<TR><TD><FONT POINT-SIZE="15">part_start</FONT></TD>\n'
                    # dot += f'<TD><FONT POINT-SIZE="15">{particion.part_start}</FONT></TD></TR>\n'
                    # dot += '<TR><TD><FONT POINT-SIZE="15">part_s</FONT></TD>\n'
                    # dot += f'<TD><FONT POINT-SIZE="15">{particion.part_s}</FONT></TD></TR>\n'
                    # dot += '<TR><TD><FONT POINT-SIZE="15">part_name</FONT></TD>\n'
                    # dot += f'<TD><FONT POINT-SIZE="15">{particion.part_name.decode()}</FONT></TD></TR>\n'
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
                    # next_part = tmp.part_next
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

                        # dot += '<TR><TD colspan="2" BGCOLOR="#7fb3d5  ">Particion Logica</TD></TR>\n'
                        # dot += '<TR><TD><FONT POINT-SIZE="15">part_status</FONT></TD>\n'
                        # dot += f'<TD><FONT POINT-SIZE="15">{tmp.part_status.decode()}</FONT></TD></TR>\n'
                        # dot += '<TR><TD><FONT POINT-SIZE="15">part_fit</FONT></TD>\n'
                        # dot += f'<TD><FONT POINT-SIZE="15">{tmp.part_fit.decode()}</FONT></TD></TR>\n'
                        # dot += '<TR><TD><FONT POINT-SIZE="15">part_start</FONT></TD>\n'
                        # dot += f'<TD><FONT POINT-SIZE="15">{tmp.part_start}</FONT></TD></TR>\n'
                        # dot += '<TR><TD><FONT POINT-SIZE="15">part_s</FONT></TD>\n'
                        # dot += f'<TD><FONT POINT-SIZE="15">{tmp.part_s}</FONT></TD></TR>\n'
                        # dot += '<TR><TD><FONT POINT-SIZE="15">part_name</FONT></TD>\n'
                        # dot += f'<TD><FONT POINT-SIZE="15">{tmp.part_name.decode()}</FONT></TD></TR>\n'
                        espacio_anterior_logic = tmp.part_start + tmp.part_s
                        file.seek(tmp.part_next)
                        contenido_binario = file.read(ctypes.sizeof(tmp))
                        ctypes.memmove(ctypes.byref(tmp), contenido_binario, ctypes.sizeof(tmp))
                        # if tmp.part_next == -1:
                            # dot += '<TR><TD><FONT POINT-SIZE="15">part_next</FONT></TD>\n'
                            # dot += f'<TD><FONT POINT-SIZE="15">{tmp.part_next}</FONT></TD></TR>\n'
                        # else:
                            # dot += '<TR><TD><FONT POINT-SIZE="15">part_next</FONT></TD>\n'
                            # dot += f'<TD><FONT POINT-SIZE="15">{next_part}</FONT></TD></TR>\n'
                        # next_part = tmp.part_next
                    
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

        

