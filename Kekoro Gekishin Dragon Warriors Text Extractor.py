import os
import glob
import codecs

def extraer_bin_archivos(nds_file, archivos_info):
    with open(nds_file, 'rb') as archivo:
        for nombre, offset, longitud in archivos_info:
            archivo.seek(offset)
            datos = archivo.read(longitud)
            
            with open(f'{nombre}.bin', 'wb') as bin_file:
                bin_file.write(datos)
            print(f'{nombre}.bin successfully extracted.')

def read_table(filename):
    table = {}
    with codecs.open(filename, 'r', 'utf-8-sig') as f:
        for line in f:
            if '=' in line:
                hex_code, glyph = line.strip().split('=')
                table[bytes.fromhex(hex_code)] = glyph
    return table

def extract_text(input_file, output_file, start_offset, end_offset, main_table, kana_table, kanji_table):
    with open(input_file, 'rb') as f:
        data = f.read()[start_offset:end_offset]
    current_table = main_table
    result = []
    i = 0
    while i < len(data):
        if data[i:i+2] == b'\xF8\x00':
            result.append('')
            current_table = kanji_table
            i += 2
        elif data[i] == 0xF9:
            result.append(' (')
            current_table = kana_table
            i += 1
        elif data[i] == 0xFA:
            result.append(') ')
            current_table = main_table
            i += 1
        elif data[i] == 0xF4:
            audio_code = f'<Audio {data[i+1]:02X}{data[i+2]:02X}>'
            result.append(audio_code)
            i += 3
        elif data[i] == 0xF2 or data[i] == 0xF3:
            result.append(f'[{data[i]:02X}{data[i+1]:02X}]')
            i += 2
        elif data[i:i+2] == b'\xED\x19':
            result.append('[ED 19]')
            i += 2
        elif data[i:i+2] == b'\xFC\xFD':
            result.append('\n<end>\n\n')
            i += 2
        elif data[i] == 0xFC:
            result.append('<line>\n')
            i += 1
        elif data[i] == 0xFE:
            result.append('Next screen\n')
            i += 1
        elif data[i:i+2] == b'\xE0\x14':
            result.append('(')
            i += 2
        elif data[i:i+2] == b'\xE0\x15':
            result.append(')')
            i += 2
        elif data[i] == 0xFF:
            result.append('<Fin>')
            i += 1
        else:
            if current_table == kanji_table:
                if data[i] == 0x00:
                    result.append(' ')
                    i += 1
                elif data[i] in [0xE0, 0xE1, 0xE2, 0xE3]:
                    char_bytes = data[i:i+2]
                    i += 2
                else:
                    char_bytes = data[i:i+1]
                    i += 1
            else:
                char_bytes = data[i:i+1]
                i += 1
            if char_bytes in current_table:
                result.append(current_table[char_bytes])
            elif len(char_bytes) == 2 and char_bytes[0] in [0xE0, 0xE1, 0xE2, 0xE3]:
                result.append(f'[{char_bytes.hex()}]')
            elif char_bytes != b'\x00':
                result.append(f'[{char_bytes.hex()}]')

    with codecs.open(output_file, 'w', 'utf-8') as f:
        f.write(''.join(result))

# Search for .nds file in the same folder of the script
nds_files = glob.glob('*.nds')

if len(nds_files) == 1:
    nds_file = nds_files[0]
    print(f'Nintendo Ds file found: {nds_file}')
    
# List of files with name, offset and length for .bin extraction
archivos_info_bin = [
    ('dm00', 0x383000, 4135), ('dm01', 0x384C00, 3821), ('dm02', 0x386C00, 3412),
    ('dm03', 0x388200, 1618), ('dm04', 0x389A00, 1392), ('dm05', 0x38AA00, 2141),
    ('dm06', 0x38BC00, 1369), ('dm07', 0x38CA00, 1955), ('dm08', 0x38DC00, 1452),
    ('dm09', 0x38F200, 4957), ('dm10', 0x391000, 2958), ('dm11', 0x391E00, 437),
    ('dm12', 0x392800, 1897), ('dm13', 0x393600, 904), ('dm14', 0x393E00, 986),
    ('dm15', 0x394800, 806), ('dm16', 0x395200, 1956), ('dm17', 0x395E00, 1239),
    ('dm18', 0x397400, 2825), ('dm19', 0x399200, 3717), ('dm20', 0x39AE00, 2400),
    ('dm21', 0x39C600, 3058), ('dm22', 0x39DA00, 928), ('dm23', 0x39E200, 520),
    ('dm24', 0x39EC00, 556), ('dm25', 0x39F400, 1027), ('dm26', 0x3A0C00, 1368),
    ('dm27', 0x3A2200, 985), ('dm28', 0x3A3200, 2332), ('dm29', 0x3A4C00, 2438),
    ('dm30', 0x3A6600, 4171), ('dm31', 0x3A8C00, 4563)
]

# Run the extraction of .bin files
extraer_bin_archivos(nds_file, archivos_info_bin)

# Load tables
main_table = read_table('Keroro.tbl')
kana_table = read_table('KeroroKana.tbl')
kanji_table = read_table('KeroroKanji.tbl')

# Information to extract texts from .bin files
archivos_info_txt = [
    ('dm00.bin', 'dm00.txt', 0x5AC, 0x1026),
    ('dm01.bin', 'dm01.txt', 0x5E, 0xEEC),
    ('dm02.bin', 'dm02.txt', 0x90, 0xD53),
    ('dm03.bin', 'dm03.txt', 0x44, 0x651),
    ('dm04.bin', 'dm04.txt', 0x40, 0x56F),
    ('dm05.bin', 'dm05.txt', 0x54, 0x85C),
    ('dm06.bin', 'dm06.txt', 0x4A, 0x558),
    ('dm07.bin', 'dm07.txt', 0x46, 0x7A2),
    ('dm08.bin', 'dm08.txt', 0x46, 0x5AB),
    ('dm09.bin', 'dm09.txt', 0x96, 0x135C),
    ('dm10.bin', 'dm10.txt', 0x6C, 0xB8D),
    ('dm11.bin', 'dm11.txt', 0x22, 0x1B4),
    ('dm12.bin', 'dm12.txt', 0x4C, 0x768),
    ('dm13.bin', 'dm13.txt', 0x34, 0x387),
    ('dm14.bin', 'dm14.txt', 0x38, 0x3D9),
    ('dm15.bin', 'dm15.txt', 0x30, 0x325),
    ('dm16.bin', 'dm16.txt', 0x3E, 0x7A3),
    ('dm17.bin', 'dm17.txt', 0x2E, 0x4D6),
    ('dm18.bin', 'dm18.txt', 0x68, 0xB08),
    ('dm19.bin', 'dm19.txt', 0x88, 0xE84),
    ('dm20.bin', 'dm20.txt', 0x74, 0x95F),
    ('dm21.bin', 'dm21.txt', 0x8C, 0xBF1),
    ('dm22.bin', 'dm22.txt', 0x42, 0x39F),
    ('dm23.bin', 'dm23.txt', 0x2C, 0x207),
    ('dm24.bin', 'dm24.txt', 0x32, 0x22B),
    ('dm25.bin', 'dm25.txt', 0x38, 0x402),
    ('dm26.bin', 'dm26.txt', 0x8C, 0x557),
    ('dm27.bin', 'dm27.txt', 0x3A, 0x3D8),
    ('dm28.bin', 'dm28.txt', 0x64, 0x91B),
    ('dm29.bin', 'dm29.txt', 0x7A, 0x985),
    ('dm30.bin', 'dm30.txt', 0x80, 0x104A),
    ('dm31.bin', 'dm31.txt', 0xB0, 0x11D2)
]

# Process .bin files to extract texts and save them to .txt files
for archivo_bin, archivo_txt, offset, longitud in archivos_info_txt:
    extract_text(archivo_bin, archivo_txt, offset, longitud, main_table, kana_table, kanji_table)
else:

    # Gets the directory of the current script
    directory = os.path.dirname(os.path.abspath(__file__))

# Scrolls through all files in the directory
for filename in os.listdir(directory):
    if filename.endswith(".bin"):
        file_path = os.path.join(directory, filename)
        os.remove(file_path)
        print(f"Deleted: {file_path}")

print("All .bin files have been deleted.")
print('Process completed')
#Made by 343
