import os    
import numpy as np
from datetime import datetime

def cut(val: float, repeated = False, flag = False) -> str:
    
    """
    float: 0.000427 -> str: "4.2"
    float: 3.953569 -> str: "4.0"
    float: -3.953569 -> str: "-4.0"
    """
    
    if not repeated:
        neg_flag = False
    else:
        neg_flag = flag
    
    if val < 0 :
        val = abs(val)
        neg_flag = True
    elif ((val == 0) or (val == 0.0)) and not repeated:
        return '0.0'
    
    _int = divmod(val, 1)[0]
    _float = divmod(val, 1)[1] * 10
    
    if _int == 0.0:
        return cut(_float, repeated = True, flag = neg_flag)
    _float = round(_float)
    _int = round(_int)
    if _float == 10:
        _int += 1
        _float = 0
        
    if neg_flag == True:
        return f'-{_int}.{_float}'
    else:
        return f'{_int}.{_float}'

def basename(filename, ext = '.csv'):
    """
    Example: removes '-123' from 'my-name-123.csv'
    returns 'my-name.csv'
    """
    
    if '-' in filename:
        if ext in filename:
            filename = filename[:-len(ext)]
        ind = len(filename) - filename[::-1].index('-') - 1
        flag = True
        s = 0
        for letter in filename[ind + 1:]:
            if not letter.isdigit():
                flag = False
                break
            else:
                s += 1
        if flag:
            filename = filename[:-(s + 1)]
        
    if filename.endswith(ext):
        return filename
    else:
        return f'{filename}{ext}'
    
int1, int2 = np.meshgrid(np.arange(0, 10), np.arange(0, 10))

possibilities = []
for i in range(0, int1.flatten().shape[0]):
    possibilities.append(f'{int1.flatten()[i]}.{int2.flatten()[i]}')

def unify_filename(filename: str, possibilities = possibilities):
    '''
    A function that removes "_......int1.int2_........int3.int4" from filename
    '''
    if any((match1 := num) in filename for num in possibilities):
        filename = (filename[:filename.index(match1)], filename[filename.index(match1) + 3:])
        idx_ = len(filename[0]) - filename[0][::-1].index('_') - 1
        name = filename[0][:idx_] + filename[1]
    else:
        name = filename
    if any((match2 := num) in name for num in possibilities):
        name = (name[:name.index(match2)], name[name.index(match2) + 3:])
        idx_ = len(name[0]) - name[0][::-1].index('_') - 1
        name = name[0][:idx_] + name[1]
    return name

def fix_unicode(filename: str):
    '''
    A function add '/' in filename if it starts with 'C:U'
    Example: 'C:Users/New_user/Doc1.csv' -> 'C:/Users/New_user/Doc1.csv'
    '''
    if ':' in filename and ':\\' not in filename:
        filename = filename.replace(':', ':\\')
    return filename

def get_filename_index(filename, core_dir, YMD):
    '''
    Function to return the index (+1) of max indexed filename 
    '''
    
    files = []
    path = os.path.normpath(filename).split(os.path.sep)
    
    if 'data_files' in path:
        to_find = os.path.join(*path[:path.index('data_files') + 1]) #directory to search in
        to_find = fix_unicode(to_find)
    else:
        try:
            to_find = os.path.join(*path[:-1])
        except:
            to_find = os.path.join(core_dir, f'{YMD}')
        to_find = fix_unicode(to_find)
    
    for (_, _, file_names) in os.walk(to_find): #get all the files from subdirectories
        files.extend(file_names)
    ind = [0]
    basic_name = os.path.normpath(filename).split(os.path.sep)[-1]
    #example: my_name123_1.0_2.0-4.csv -> my_name123
    if '.' in basic_name:
        basic_name = basic_name[:(len(basic_name) - basic_name[::-1].find('.') - 1)] #all before last .
    if '-' in basic_name:
        basic_name = basic_name[:(len(basic_name) - basic_name[::-1].find('-') - 1)] #all before last -
    basic_name = unify_filename(basic_name)
    for file in files:
        if basic_name in file and 'manual' not in file and 'setget' not in file:
            index_start = len(file) - file[::-1].find('-') - 1
            index_stop = len(file) - file[::-1].find('.') - 1
            try:
                ind.append(int(file[index_start + 1 : index_stop]))
            except:
                ind.append(np.nan)
    previous_ind = int(np.nanmax(ind))
    if np.isnan(previous_ind):
        previous_ind = 0
    return previous_ind + 1

def main():
    DAY = datetime.today().strftime('%d')
    MONTH = datetime.today().strftime('%m')
    YEAR = datetime.today().strftime('%Y')[-2:]
    
    YMD = f'{YEAR}{MONTH}{DAY}'
    core_dir = r'D:\Program_sweep\App'

    

if __name__ == '__main__':
    main()