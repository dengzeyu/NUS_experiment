import os
import matplotlib.pyplot as plt
plt.rcParams.update({'figure.max_open_warning': 0})
import imageio
from filename_utils import unify_filename, fix_unicode

def create_gif(filename, idx, parameters_to_read):
    
    path = os.path.normpath(filename).split(os.path.sep)
    name = path[-1]
    try:
        name = name[:len(name) - name[::-1].index('.') - 1]
    except ValueError:
        pass
    name = unify_filename(name)
    name = name[:(len(name) - name[::-1].find('-') - 1)]
    cur_dir = os.path.join(*path[:path.index('data_files')])
    cur_dir = fix_unicode(cur_dir)
    tomake_gif = os.path.join(cur_dir, '2d_maps', 'images', f'{name}_{idx}', 
                           'gifs')

    tomake_gif = fix_unicode(tomake_gif)

    if not os.path.exists(tomake_gif):
        os.makedirs(tomake_gif)

    path_files = os.path.join(cur_dir, '2d_maps', 'images', f'{name}_{idx}')
    path_files = fix_unicode(path_files)

    image_files = []
    for (root, dir_names, file_names) in os.walk(path_files):
        for i in file_names:
            if '.png' in i:
                file = os.path.join(root, i)
                image_files.append(fix_unicode(file))
        
    for parameter in parameters_to_read:
        parameter_files = []
        parameter_idx = []
        for filename in image_files:
            if parameter in filename:
                parameter_files.append(filename)
                name = os.path.normpath(filename).split(os.path.sep)[-1]
                parameter_idx.append(name[:name.index('_')])
        dat = zip(parameter_idx, parameter_files)
        parameter_files = sorted(dat, key = lambda tup: tup[0])
        parameter_files = [i[1] for i in parameter_files]
        parameter_images = [imageio.imread(i, format = 'PNG') for i in parameter_files]
        gif_name = os.path.join(tomake_gif, f'{idx}_{parameter}_gif.gif')
        gif_name = fix_unicode(gif_name)
        imageio.mimsave(gif_name, parameter_images, fps = 3, loop = 0)
        