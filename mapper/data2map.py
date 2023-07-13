import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
plt.rcParams.update({'figure.max_open_warning': 0})
from mapper.add_ticks import add_ticks

def save_map(args):
    
    '''
    Creates .png image from a table with filename 'path'
    
    args: iterable; path, min_z = None, max_z = None
    
    Path should contain 'tables'
    '''
    
    path = args[0]
    min_z = args[1]
    max_z = args[2] 
    
    image_filename = os.path.normpath(path).split(os.path.sep)
    image_filename[image_filename.index('tables')] = 'images'
    image_filename[-1] = image_filename[-1] \
                    [:len(image_filename[-1]) - image_filename[-1][::-1].index('.')-1] \
                        + '.png'
    filename = image_filename[-1]

    def fix_unicode(filename: str):
        if ':' in filename and ':\\' not in filename:
            filename = filename.replace(':', ':\\')
        return filename

    to_make = os.path.join(*image_filename[:-1])
    to_make = fix_unicode(to_make)
    if not os.path.exists(to_make):
        os.makedirs(to_make)

    image_filename = os.path.join(to_make, filename)

    parameter = os.path.normpath(path).split(os.path.sep)[-1]
    parameter = parameter.split('_')[1]

    data = pd.read_csv(path, sep = ',')

    fig, ax = plt.subplots()

    plt.ioff()

    names = data.columns.tolist()[0].split(' / ')

    y = data[data.columns.tolist()[0]]
    _x = data.columns.tolist()[1:]
    x = []
    for i in _x:
        if str(i).endswith('.1'):
            i = float(str(i)[:-2] + '0')
        x.append(i)

    z = [data[i].values for i in x]
    z = np.array(z, dtype = float).T
    z = np.ma.masked_invalid(z)
    
    if min_z == None and max_z == None:
        min_z, max_z = np.nanmin(z), np.nanmax(z)

    y = np.array(y, dtype = float)
    x = np.array(x, dtype = float)

    colormap = ax.pcolormesh(z, cmap = 'viridis', vmin = min_z, vmax = max_z, shading = 'flat')
    colorbar = ax.get_figure().colorbar(colormap, ax = ax)
    colorbar.ax.tick_params(labelsize=5, which = 'both')
    colorbar.set_label(parameter)

    title = f'Map {parameter}'
    xlabel = names[0]
    ylabel = names[1]

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    add_ticks(ax, x, y)
        
    fig.savefig(image_filename, dpi = 300, )

    plt.close(fig)