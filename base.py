import ctypes
from ctypes import wintypes
import struct  # 添加这一行以导入 struct 模块

IMAGE_DIRECTORY_ENTRY_EXPORT = 0

class IMAGE_DATA_DIRECTORY(ctypes.Structure):
    _fields_ = [
        ('VirtualAddress', wintypes.DWORD),
        ('Size', wintypes.DWORD),
    ]

class IMAGE_EXPORT_DIRECTORY(ctypes.Structure):
    _fields_ = [
        ('Characteristics', wintypes.DWORD),
        ('TimeDateStamp', wintypes.DWORD),
        ('MajorVersion', wintypes.WORD),
        ('MinorVersion', wintypes.WORD),
        ('Name', wintypes.DWORD),
        ('Base', wintypes.DWORD),
        ('NumberOfFunctions', wintypes.DWORD),
        ('NumberOfNames', wintypes.DWORD),
        ('AddressOfFunctions', wintypes.DWORD),
        ('AddressOfNames', wintypes.DWORD),
        ('AddressOfNameOrdinals', wintypes.DWORD),
    ]

def get_exports(dll_path):
    with open(dll_path, 'rb') as f:
        data = f.read()

    dos_header = ctypes.create_string_buffer(data[:64])
    pe_offset = struct.unpack_from('<L', dos_header, 0x3C)[0]

    pe_header = ctypes.create_string_buffer(data[pe_offset:pe_offset+24])
    machine = struct.unpack_from('<H', pe_header, 4)[0]
    number_of_sections = struct.unpack_from('<H', pe_header, 6)[0]
    optional_header_size = struct.unpack_from('<H', pe_header, 20)[0]

    optional_header = ctypes.create_string_buffer(data[pe_offset+24:pe_offset+24+optional_header_size])
    export_directory_rva = struct.unpack_from('<L', optional_header, 96)[0]
    export_directory_size = struct.unpack_from('<L', optional_header, 100)[0]

    export_directory = IMAGE_EXPORT_DIRECTORY.from_buffer_copy(data[export_directory_rva:export_directory_rva+export_directory_size])

    functions = []
    names = []
    ordinals = []

    if export_directory.AddressOfFunctions:
        address_of_functions = export_directory.AddressOfFunctions - export_directory_rva + export_directory_rva
        for i in range(export_directory.NumberOfFunctions):
            func_rva = struct.unpack_from('<L', data[address_of_functions+i*4:])[0]
            functions.append(func_rva)

    if export_directory.AddressOfNames:
        address_of_names = export_directory.AddressOfNames - export_directory_rva + export_directory_rva
        for i in range(export_directory.NumberOfNames):
            name_rva = struct.unpack_from('<L', data[address_of_names+i*4:])[0]
            name = b''
            j = 0
            while True:
                byte = data[name_rva+j:name_rva+j+1]
                if byte == b'\x00':
                    break
                name += byte
                j += 1
            names.append(name.decode('utf-8'))

    if export_directory.AddressOfNameOrdinals:
        address_of_name_ordinals = export_directory.AddressOfNameOrdinals - export_directory_rva + export_directory_rva
        for i in range(export_directory.NumberOfNames):
            ordinal = struct.unpack_from('<H', data[address_of_name_ordinals+i*2:])[0]
            ordinals.append(ordinal)

    exports = []
    for i in range(len(names)):
        exports.append((ordinals[i] + export_directory.Base, names[i], functions[i]))

    return exports

dll_path = r'E:\project\python\serveAssets\plugins\RegDll.dll'
exports = get_exports(dll_path)
for ordinal, name, address in exports:
    print(f'Ordinal: {ordinal}, Name: {name}, Address: {address:#x}')