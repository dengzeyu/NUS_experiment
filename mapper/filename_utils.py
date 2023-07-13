def cut(val: float) -> str:
    
    """
    float: 0.000427 -> str: "4.2"
    float: 3.953569 -> str: "4.0"
    """
    
    _int = divmod(val, 1)[0]
    _float = divmod(val, 1)[1] * 10
    if _int == 0.0:
        return cut(_float)
    _float = round(_float)
    if _float == 10:
        _int += 1.0
        _float = 0
    return f'{str(_int)[0]}.{str(_float)}'

def basename(filename, ext = '.csv'):
    """
    Example: removes '-123' from 'my-name-123.csv'
    returns 'my-name.csv'
    """
    
    if '-' in filename:
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
        
        return f'{filename}{ext}'
    
import numpy as np
    
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