import struct
import ctypes


class User():
    def __init__(self):
        self.user_name = ""
        self.user_password = ""
        self.group_name = ""

class SesionUsuario():
    def __init__(self, credenciales, mounted, is_logged):
        self.credenciales = credenciales
        self.mounted = mounted
        self.is_logged = is_logged

class Mounted():
    def __init__(self, path, name, id, part_start):
        self.path = path
        self.name = name
        self.id = id
        self.part_start = part_start

class Inodo(ctypes.Structure):
    _fields_ = [
        ('i_uid', ctypes.c_int),
        ('i_gid', ctypes.c_int),
        ('i_s', ctypes.c_int),
        ('i_atime', ctypes.c_longlong),
        ('i_ctime', ctypes.c_longlong),
        ('i_mtime', ctypes.c_longlong),
        ('i_block', ctypes.c_int * 15),
        ('i_type', ctypes.c_char),
        ('i_perm', ctypes.c_int)
    ]

    def __init__(self):
        self.i_uid = 0
        self.i_gid = 0
        self.i_s = 0
        self.i_atime = 0
        self.i_ctime = 0
        self.i_mtime = 0
        self.i_block = (ctypes.c_int * 15)(-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1)
        self.i_type = 0
        self.i_perm = 0

class Content(ctypes.Structure):
    _fields_ = [
        ('b_name', ctypes.c_char * 12),
        ('b_inodo', ctypes.c_int)
    ]

    def __init__(self):
        self.b_name = b'\0' * 12
        self.b_inodo = -1

class BloqueCarpeta(ctypes.Structure):
    _fields_ = [
        ('b_content', Content * 4),
    ]

    def __init__(self):
        self.b_content = (Content * 4)()
        for i in range(4):
            self.b_content[i].b_inodo = -1

class BloqueArchivo(ctypes.Structure):
    _fields_ = [
        ('b_content', ctypes.c_char * 64),
    ]

    def __init__(self):
        self.b_content = b'\0' * 64

class BloqueApuntadores(ctypes.Structure):
    _fields_ = [
        ('b_pointers', ctypes.c_int * 16),
    ]

    def __init__(self):
        self.b_pointers = -1 * 16

class SuperBloque(ctypes.Structure):
    _fields_ = [
        ('s_filesystem_type', ctypes.c_int),
        ('s_inodes_count', ctypes.c_int),
        ('s_blocks_count', ctypes.c_int),
        ('s_free_blocks_count', ctypes.c_int),
        ('s_free_inodes_count', ctypes.c_int),
        ('s_mtime', ctypes.c_longlong),
        ('s_umtime', ctypes.c_longlong),
        ('s_mnt_count', ctypes.c_int),
        ('s_magic', ctypes.c_int),
        ('s_inode_size', ctypes.c_int),
        ('s_block_size', ctypes.c_int),
        ('s_first_ino', ctypes.c_int),
        ('s_first_blo', ctypes.c_int),
        ('s_bm_inode_start', ctypes.c_int),
        ('s_bm_block_start', ctypes.c_int),
        ('s_inode_start', ctypes.c_int),
        ('s_block_start', ctypes.c_int)
    ]

    def __init__(self):
        self.s_filesystem_type = 0
        self.s_inodes_count = 0
        self.s_blocks_count = 0
        self.s_free_blocks_count = 0
        self.s_free_inodes_count = 0
        self.s_mtime = 0
        self.s_umtime = 0
        self.s_mnt_count = 0
        self.s_magic = 0
        self.s_inode_size = 0
        self.s_block_size = 0
        self.s_first_ino = 0
        self.s_first_blo = 0
        self.s_bm_inode_start = 0
        self.s_bm_block_start = 0
        self.s_inode_start = 0
        self.s_block_start = 0

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