import re
import math
import sys
import json
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

def extract_object_nums(js_code, variable):
    search = variable + '={'
    results = []
    offset = 0

    while True:
        start = js_code.find(search, offset)
        if start == -1:
            break

        start += len(variable + '=')
        i = start
        braces = 0
        obj_text = ''

        while i < len(js_code):
            char = js_code[i]
            obj_text += char
            if char == '{':
                braces += 1
            elif char == '}':
                braces -= 1
                if braces == 0:
                    break
            i += 1

        offset = i

        obj_clean = obj_text.replace('\n', '').strip()
        for ch in "{}:,":
            obj_clean = obj_clean.replace(ch, f" {ch} ")

        parts = obj_clean.split()
        json_parts = []
        for i, part in enumerate(parts):
            if parts[i] == ':' and not parts[i-1].startswith('"'):
                json_parts[-1] = f'"{json_parts[-1]}"'
            json_parts.append(part)

        json_string = ''.join(json_parts)
        try:
            parsed_object = json.loads(json_string)
            results.append(parsed_object)
        except json.decoder.JSONDecodeError:
            results.append(json_string)

    if not results:
        return False #raise ValueError(f'cloudflare object not found: {variable}')
    return results[0] if len(results) == 1 else results

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
            index = int(c) - int(string_number_subtraction)
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

def deobfuscator(
    javascript,
    string_number_subtraction,
    obf_find_number, 
    parseint_array_finder,
    obfuscated_string_array,
    _split_type='~'
):
    string_array_iterator(obfuscated_string_array, parseint_array_finder, obf_find_number, string_number_subtraction, _split_type)
    
    w_var = javascript.split('=this||self')[0]
    window_var = w_var[len(w_var) -2:len(w_var)]
    document_var = javascript.split('=this||self,')[1].split('=')[0]
    
    def _deobfuscator_main(code, beautify=True, parsing_booleans=True):
        # analizar codigo
        code_parts = code.split('(')
        findernum_array = []
        nums_array = []

        chars = ['=', '[', '(', ':', ' ', '{', '+', ',', '', '|']
        obf_ops = {
            f'{window_var}[': 'window[',
            f'{document_var}[': 'document[',
            'void 0': 'undefined'
        }
        
        if parsing_booleans:
             obf_ops.update({
                '!![]': 'true',
                '![]': 'false',
                '!0': 'true',
                '!1': 'false'
             })
        
        obj_seed_map = {}
        parsed_arr_map_calls = []
             
        for i,v in enumerate(code_parts):
            if (v[:2].isalpha() and v[2:3] == '.' or (v[:1].isalpha() and v[1:2].isnumeric() and v[2:3] == '.')) and (v[3:4].isalpha() and v[4:5] == ')' or (v[3:4].isalpha() and v[5:6] == ')')):
                prev = code_parts[i - 1]
                finalprev = prev[len(prev) - 2:len(prev)]
                finalprev2 = prev[len(prev) - 3:len(prev) - 2]
                
                if finalprev2 not in chars:
                    continue
                
                obj_name = v[:2]
                prop = v.split('.')[1].split(')')[0]
                if obj_name in obj_seed_map:
                    obj = obj_seed_map[obj_name]
                else:
                    obj = extract_object_nums(code, obj_name)
                    
                    if obj == False:
                        obj = extract_object_nums(javascript, obj_name)
                        
                        if obj == False:
                            raise ValueError(f'cloudflare object not found: {obj_name}')
                    obj_seed_map[obj_name] = obj

                parsed_arr_map_calls.append({
                    'obj_name': v[:2],
                    'obj': obj,
                    'prop': prop,
                    'call_arr_map': finalprev
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
        
        # formatear
                    
        for parsed in parsed_arr_map_calls:
            real_seed = gF(parsed['obj'][parsed['prop']])
            obj_seeds = str(parsed['obj']).replace(' ', '').replace("'", '')
            obj_seeds = f'{parsed["obj_name"]}={obj_seeds},' # goofy object

            caller = parsed['call_arr_map']
            code = code.replace(f'{caller}({parsed["obj_name"]}.{parsed["prop"]})', f"'{real_seed}'").replace(obj_seeds, '')
            
            
        for findnum, num in zip(findernum_array, nums_array):
            stringfound = gF(num)
            code = code.replace(findnum, f"'{stringfound}'")
            
        for obfop, toreplace in obf_ops.items():
            code = code.replace(obfop, toreplace)
            
        for x in range(1, 10):
            for o in range(2, 6):
                code = code.replace(f'{x}e{o}', str(round(eval(f'{x}e{o}'))))
        
        deobfuscated = jsbeautifier.beautify(code) if beautify else code
        return deobfuscated
    return _deobfuscator_main, gF

def _deobfuscate(js_code, split_type='~'):
    spli2 = None
    obf_letters = 'aertyuiopsdfghjklbzxcvnmQWERTYUIOPASDFGHJKLZXCVBNM'
    lett_list = list(obf_letters)
    
    for let in lett_list:
        try:
            spli1 = js_code.split(f'({let}=')[1].split('.push(')[0].split('===')[0]
            test = spli1.replace('\n', '').replace(' ', '')
            if '),' in test[(len(test) - 5):len(test)]:
                spli2 = (spli1.split('),')[0] + '),')

            elif ',' in test[(len(test) - 5):len(test)]:
                spli2 = (spli1.split(',')[0] + ',')
            
            if spli2 is not None and len(spli2) < 300 and spli2.count('parseInt') > 4:
                break
        except (IndexError, ValueError):
            continue

    instruction = spli2.replace('\n', '').strip().replace(' ', '')
    identifier_properties = []
    
    for i, part in enumerate(instruction.split('.')):
        identifier_prop = part.split('))')[0].replace(' ', '')
        
        if len(identifier_prop) > 5:
            continue
        
        identifier_properties.append(identifier_prop)

    call_arr_map_name = instruction.split('parseInt(')[1].split('(')[0]
    obj_name = instruction.split('parseInt(')[1].split('(')[1].split('.')[0]
    obj = extract_object_nums(js_code[:9500], obj_name)
    
    for prop in identifier_properties:
        num = obj[prop]
        
        instruction = instruction.replace(f'{obj_name}.{prop}', str(num))
    
    parse_int = instruction.replace(call_arr_map_name, 'gE')
    
    full_array = None
    array_func_names = list(obf_letters)
    
    for func_name in array_func_names:
        for i, code in enumerate(js_code.split(f'function {func_name}(')):
            if code[:1].isalpha() and code[2:3] == ')' and len(code.split('~')) > 500:
                variable = code[:2]
                full_array = code.split(f"return {variable}='")[1].split('.split(')[0]
                break
            
    if full_array is None:
        raise ValueError('Not VM String Array Found')
    
    if full_array[(len(full_array) - 1):len(full_array)] == "'":
        full_array = full_array.replace("'", '')
        
    lett_list = list(obf_letters)
    for i, code in enumerate(js_code.split('return ')):
        for lett in lett_list:
            if f'{lett}={lett}-' in code:
                unknown_type = code.split('-')[1].split(',')[0]
                
                if not unknown_type.isnumeric():
                    continue
                sub_less = unknown_type
                break
    
    # String Array Iterator Number
    for i,v in enumerate(js_code.split('parseInt(')):
        if '}}(' in v[:450]:
            variaba = v.split('}(')[1][:2]
            obf_number = round(float(v.split('}(' + variaba)[1].split('),')[0].replace('\n', '').strip()))
            break
            
    # Deobfuscate
    
    _deobf, find_str = deobfuscator(
        javascript=js_code,
        string_number_subtraction=sub_less,
        obf_find_number=obf_number,
        parseint_array_finder=parse_int,
        obfuscated_string_array=full_array,
        _split_type=split_type
    )
    open('output.js', 'w').write(_deobf(js_code))
    print('Saved in output.js')

if __name__ == '__main__':
    code = _deobfuscate(open('cf_code.txt', 'r').read())