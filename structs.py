import struct
import ctypes


class EBR(ctypes.Structure):
    _fields_ = [
        ('part_status', ctypes.c_char),
        ('part_fit', ctypes.c_char),
        ('part_start', ctypes.c_int),
        ('part_s', ctypes.c_int),
        ('part_next', ctypes.c_int),
        ('part_name', ctypes.c_char * 16)
    ]

    def __init__(self):
        self.part_status = b'0'
        self.part_fit = b'0'
        self.part_start = -1
        self.part_s = -1
        self.part_next = -1
        self.part_name = b'\0'*16

    # def set_part_status(self, part_status):
    #     self.part_status = part_status.encode('utf-8')[:1]

    # def set_part_type(self, part_type):
    #     self.part_type = part_type.encode('utf-8')[:1]

    # def set_part_fit(self, part_fit):
    #     self.part_fit = part_fit.encode('utf-8')[:1]

    # def set_part_start(self, part_start):
    #     self.part_start = part_start

    # def set_part_s(self, part_s):
    #     self.part_s = part_s

    # def set_part_name(self, part_name):
    #     self.part_name = part_name.encode('utf-8')[:16].ljust(16, b'\0')

class Partition(ctypes.Structure):
    _fields_ = [
        ('part_status', ctypes.c_char),
        ('part_type', ctypes.c_char),
        ('part_fit', ctypes.c_char),
        ('part_start', ctypes.c_int),
        ('part_s', ctypes.c_int),
        ('part_name', ctypes.c_char * 16)
    ]

    def __init__(self):
        self.part_status = b'N'
        self.part_type = b'0'
        self.part_fit = b'0'
        self.part_start = -1
        self.part_s = -1
        self.part_name = b'\0'*16

    def set_part_status(self, part_status):
        self.part_status = part_status.encode('utf-8')[:1]

    def set_part_type(self, part_type):
        self.part_type = part_type.encode('utf-8')[:1]

    def set_part_fit(self, part_fit):
        self.part_fit = part_fit.encode('utf-8')[:1]

    def set_part_start(self, part_start):
        self.part_start = part_start

    def set_part_s(self, part_s):
        self.part_s = part_s

    def set_part_name(self, part_name):
        self.part_name = part_name.encode('utf-8')[:16].ljust(16, b'\0')

    # def serializar(self):
    #     data = struct.pack(
    #         '1s 1s 1s i i 16s',
    #         self.part_status,
    #         self.part_type,
    #         self.part_fit,
    #         self.part_start,
    #         self.part_s,
    #         self.part_name
    #     )        
    #     return data

class MBR(ctypes.Structure):
    _fields_ = [
        ('mbr_tamano', ctypes.c_int),
        ('mbr_fecha_creacion', ctypes.c_longlong),
        ('mbr_dsk_signature', ctypes.c_int),
        ('dsk_fit', ctypes.c_char),
        ('mbr_partitions', Partition * 4)
    ]

    def __init__(self):
        self.mbr_tamano = 0
        self.mbr_fecha_creacion = 0
        self.mbr_dsk_signature = 0
        self.dsk_fit = b'0'
        self.mbr_partitions

    def set_mbr_tamano(self, mbr_tamano):
        self.mbr_tamano = mbr_tamano

    def set_mbr_fecha_creacion(self, mbr_fecha_creacion):
        self.mbr_fecha_creacion = mbr_fecha_creacion

    def set_mbr_dsk_signature(self, mbr_dsk_signature):
        self.mbr_dsk_signature = mbr_dsk_signature

    def set_dsk_fit(self, dsk_fit):
        self.dsk_fit = dsk_fit.encode('utf-8')[:1]

    def set_mbr_partitions(self, mbr_partitions):
        self.mbr_partitions = mbr_partitions

    # def serializar(self):
    #     data = struct.pack(
    #         'I q I 1s',
    #         self.mbr_tamano,
    #         self.mbr_fecha_creacion,
    #         self.mbr_dsk_signature,
    #         self.dsk_fit
    #     )        
    #     return data

# def size_mbr():
#     return 'I q I 1s'

# def deserializar_mbr(data):
#     desempaquetados = struct.unpack(size_mbr(), data)
#     return desempaquetados

# def size_partition():
#     return '1s 1s 1s i i 16s'

# def deserializar_partition(data):
#     desempaquetados = struct.unpack(size_partition(), data)
#     return desempaquetados