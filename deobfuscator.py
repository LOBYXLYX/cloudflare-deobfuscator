import re
import math
import jsbeautifier

gF = None

def _parse_int(s, radix=10):
    if not isinstance(s, str):
        s = str(s)
    s = s.lstrip()
    if radix == 0 or radix is None:
        if s.startswith(('0x', '0X')):
            radix = 16
        else:
            radix = 10
    if radix <= 10:
        pattern = fr'[0-{radix - 1}]+'
    else:
        pattern = fr'[0-9a-{chr(86 + radix)}A-{chr(54 + radix)}]+'
    match = re.match(pattern, s)
    if not match:
        return math.nan
    return int(match.group(), radix)

def a(obfuscated_string_array, _split_type):
    jE = obfuscated_string_array.split(_split_type)
    return jE

def string_array_iterator(obfuscated_string_array, parseint_array_finder, obf_find_number, string_number_subtraction, _split_type):
    global gF
    arr = a(obfuscated_string_array, _split_type)
    code_to_eval = parseint_array_finder.replace('parseInt', '_parse_int').replace('gE', 'gF').replace('+-', '+ -').replace('+_', '+ _').replace('/', ' / ').replace('*', ' * ')
    
    spglen = len(code_to_eval) 
        
    if code_to_eval[spglen - 1:spglen] == ',':
        code_to_eval = code_to_eval[:spglen - 1]
    
    while True:
        def b(c):
            nonlocal arr, string_number_subtraction
            index = int(c) - string_number_subtraction
            return arr[index]
        
        gF = b

        try:
            f = (eval(code_to_eval))
            if math.isnan(f):
                pass
            if int(f) == obf_find_number:
                break
            else:
                arr.append(arr.pop(0))
        except Exception as e:
            arr.append(arr.pop(0))

def deobfuscator_main(
    string_number_subtraction,
    obf_find_number, 
    parseint_array_finder,
    obfuscated_string_array,
    _split_type='~'
):
    string_array_iterator(obfuscated_string_array, parseint_array_finder, obf_find_number, string_number_subtraction, _split_type)
    
    def _deobfuscator_main(code, beautify=True, parsing_booleans=True):
        # analizar codigo
        code_parts = code.split('(')
        findernum_array = []
        nums_array = []
        found_obf_objects = 0

        chars = ['=', '[', '(', ':', ' ', '{', '+', ',', '', '|']
        obf_ops = {
            'eM[': 'window[',
            'eN[': 'document[',
            'void 0': 'undefined'
        }
        
        if parsing_booleans:
             obf_ops.update({
                '!![]': 'true',
                '![]': 'false',
                '!0': 'true',
                '!1': 'false'
             })
             
        for i,v in enumerate(code_parts):
            if (v[:3].isnumeric() and v[3:4] == ')') or (v[:4].isnumeric() and v[4:5] == ')'):
                prev = code_parts[i - 1]
                finalprev = prev[len(prev) - 2:len(prev)]
                finalprev2 = prev[len(prev) - 3:len(prev) - 2]
                
                if finalprev2 not in chars:
                    continue
                
                if finalprev.isalpha() or (finalprev[:1].isalpha() and finalprev[1:2].isnumeric()):
                    number = v[:3] if (v[:3].isnumeric() and v[3:4] == ')') else v[:4]
                    findernum_array.append(f'{finalprev}({number})')
                    nums_array.append(int(number))
                    
        # Format All
                    
        for findnum, num in zip(findernum_array, nums_array):
            stringfound = gF(num)
        
            code = code.replace(findnum, f"'{stringfound}'")
            found_obf_objects += 1
            
        for obfop, toreplace in obf_ops.items():
            code = code.replace(obfop, toreplace)
            
        for x in range(1, 10):
            for o in range(2, 6):
                code = code.replace(f'{x}e{o}', str(round(eval(f'{x}e{o}'))))
        
        print('Deobfuscated', found_obf_objects, 'Objects')
        deobfuscated = jsbeautifier.beautify(code) if beautify else code
        return deobfuscated
    return _deobfuscator_main, gF

def deobfuscate(code, split_type='~'):
    # Parse String Array Map Obfuscation
    for i,v in enumerate(code.split('function a(')):
        if v[:1].isalpha() and v[2:3] == ')' and len(v.split('~')) > 500:
            variable = v[:2]
            stringarraymap = v.split(f"return {variable}='")[1].split('.split(')[0]

    if stringarraymap[(len(stringarraymap) - 1):len(stringarraymap)] == "'":
        stringarraymap = stringarraymap.replace("'", '')
    
    
    # String Array Base Iterator
    spli1 = code.split('(f=')[1].split('.push(')[0].split('===')[0]

    test = spli1.replace('\n', '').replace(' ', '')
    if '),' in test[(len(test) - 5):len(test)]:
        spli2 = (spli1.split('),')[0] + '),')

    elif ',' in test[(len(test) - 5):len(test)]:
        spli2 = (spli1.split(',')[0] + ',')

    spli2 = spli2.replace('\n', '').strip().replace(' ', '')

    variable = spli2.split('parseInt(')[1][:2]
    _parseInt = spli2.replace(variable, 'gE')
    
    # String Find Number Subtraction
    f_less = int(code.split('f=f-')[1].split(',')[0])
    
    # String Array Iterator Number
    for i,v in enumerate(code.split('parseInt(')):
        if '}}(' in v[:450]:
            variaba = v.split('}(')[1][:2]
            obf_number = round(float(v.split('}(' + variaba)[1].split('),')[0].replace('\n', '').strip()))
            break
            
    # Deobfuscate
    
    _deobf, find_str = deobfuscator_main(
        string_number_subtraction=f_less,
        obf_find_number=obf_number,
        parseint_array_finder=_parseInt,
        obfuscated_string_array=stringarraymap
    )
    open('output.js', 'w').write(_deobf(code))
    print('Saved in output.js')
    

if __name__ == '__main__':
    deobfuscate(open('cf_code.txt', 'r').read())