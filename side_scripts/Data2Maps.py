import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import os
import matplotlib.pyplot as plt
plt.rcParams.update({'figure.max_open_warning': 0})
import imageio

cur_dir = os.getcwd()


files = os.listdir(os.path.join(cur_dir, 'data_files_230421'))

max_res = -1e18
max_vol = -1e18
min_vol = 1e18
min_res = 1e18

frames_res_230421 = []
frames_vol_230421 = []

for i in range(1, 26):
    j = 0
    for file in files:
        if not file.startswith('230421_3_') and i == int(file.split('_')[1].split('.')[0]) and j < 31:
            try:
                data = pd.read_csv(os.path.join(cur_dir, 'data_files_230421', file))
                res = data['GPIB0::1::INSTR.y'].values / 2 * 5e6
                res = res[:res.shape[0] // 2]
                vol = data['GPIB0::2::INSTR.x'].values * 1000
                vol = vol[:vol.shape[0] // 2]
                res_max = np.max(res)
                res_min = np.min(res)
                vol_max = np.max(vol)
                vol_min = np.min(vol)
                if res_max > max_res:
                    max_res = res_max
                if res_min < min_res:
                    min_res = res_min
                if vol_max > max_vol:
                    max_vol = vol_max
                if vol_min < min_vol:
                    min_vol = vol_min
            except:
                pass

for i in range(1, 26):
    j = 0
    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()
    for file in files:
        if not file.startswith('230421_3_') and i == int(file.split('_')[1].split('.')[0]) and j < 31:
            data = pd.read_csv(os.path.join(cur_dir, 'data_files_230421', file))
            res = data['GPIB0::1::INSTR.y'].values / 2 * 5e6
            res = res[:res.shape[0] // 2]
            vol = data['GPIB0::2::INSTR.x'].values * 1000
            vol = vol[:vol.shape[0] // 2]
            x = data['COM6.position'].values
            x = x[:x.shape[0] // 2]
            y = data['COM4.position'].values[0]
            z = data['COM5.position'].values[0]
            f_res = interp1d(x, res, kind = 'nearest', fill_value="extrapolate")
            f_vol = interp1d(x, vol, kind = 'nearest', fill_value="extrapolate")
            t = np.linspace(-15, 15, 103)
            res = np.array(f_res(t))
            vol = np.array(f_vol(t))
            if j == 0:
                map2D_res = np.array([res])
                map2D_vol = np.array([vol])
            else:
                map2D_res = np.vstack([map2D_res, res])
                map2D_vol = np.vstack([map2D_vol, vol])
            j += 1
            
    x, y = np.meshgrid(np.linspace(-15, 15, 103), np.linspace(-15, 15, 31))
    ax1.grid(False)
    ax2.grid(False)
    colormap_res = ax1.pcolor(x, y, map2D_res, cmap = 'gist_earth', vmax = max_res, vmin = min_res, rasterized=True)
    colormap_vol = ax2.pcolor(x, y, map2D_vol, cmap = 'gist_earth', vmax = max_vol, vmin = min_vol, rasterized=True)
    ax1.set_xlabel('X, mm')
    ax1.set_ylabel('Y, mm')
    ax1.set_title(r'$\Delta R$ map')
    ax2.set_xlabel('X, mm')
    ax2.set_ylabel('Y, mm')
    ax2.set_title(r'$\Delta V$ map')
    ax1.text(-15, 13, f'Z = {i + 30}, mm', color = 'White', fontsize = 'x-large')
    ax2.text(-15, 13, f'Z = {i + 30}, mm', color = 'White', fontsize = 'x-large')
    colorbar_res = fig1.colorbar(colormap_res)
    colorbar_res.set_label(r'$\Delta R$, Ohm')
    colorbar_vol = fig2.colorbar(colormap_vol)
    colorbar_vol.set_label(r'$\Delta V$, mV')
    if i != 14:
        fig1.savefig(os.path.join(cur_dir, 'data_files_230421', 'Maps_230421', f'Res_{i}.png'), dpi = 300)
        image_res = imageio.imread(os.path.join(cur_dir, 'data_files_230421', 'Maps_230421', f'Res_{i}.png'))
        frames_res_230421.append(image_res)
        fig2.savefig(os.path.join(cur_dir, 'data_files_230421', 'Maps_230421', f'Vol_{i}.png'), dpi = 300)
        image_vol = imageio.imread(os.path.join(cur_dir, 'data_files_230421', 'Maps_230421', f'Vol_{i}.png'))
        frames_vol_230421.append(image_vol)

imageio.mimsave(os.path.join(cur_dir, 'data_files_230421', 'Maps_230421', 'Res_230421.gif'), # output gif
                frames_res_230421, fps = 3, loop = 1)

imageio.mimsave(os.path.join(cur_dir, 'data_files_230421', 'Maps_230421', 'Vol_230421.gif'), # output gif
                frames_vol_230421, fps = 3, loop = 1)

files = os.listdir(os.path.join(cur_dir, 'data_files_230421'))

max_res = -1e18
max_vol = -1e18
min_vol = 1e18
min_res = 1e18

frames_res_230421_3 = []
frames_vol_230421_3 = []

for i in range(1, 26):
    j = 0
    for file in files:
        if file.startswith('230421_3_') and i == int(file.split('_')[2].split('.')[0]) and j < 31:
            try:
                data = pd.read_csv(os.path.join(cur_dir, 'data_files_230421', file))
                res = data['GPIB0::1::INSTR.y'].values / 2 * 5e6
                res = res[:res.shape[0] // 2]
                vol = data['GPIB0::2::INSTR.x'].values * 1000
                vol = vol[:vol.shape[0] // 2]
                res_max = np.max(res)
                res_min = np.min(res)
                vol_max = np.max(vol)
                vol_min = np.min(vol)
                if res_max > max_res:
                    max_res = res_max
                if res_min < min_res:
                    min_res = res_min
                if vol_max > max_vol:
                    max_vol = vol_max
                if vol_min < min_vol:
                    min_vol = vol_min
            except:
                pass

for i in range(1, 26):
    j = 0
    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()
    for file in files:
        if file.startswith('230421_3_') and i == int(file.split('_')[2].split('.')[0]) and j < 31:
            data = pd.read_csv(os.path.join(cur_dir, 'data_files_230421', file))
            res = data['GPIB0::1::INSTR.y'].values / 2 * 5e6
            res = res[:res.shape[0] // 2]
            vol = data['GPIB0::2::INSTR.x'].values * 1000
            vol = vol[:vol.shape[0] // 2]
            x = data['COM6.position'].values
            x = x[:x.shape[0] // 2]
            y = data['COM4.position'].values[0]
            z = data['COM5.position'].values[0]
            f_res = interp1d(x, res, kind = 'nearest', fill_value="extrapolate")
            f_vol = interp1d(x, vol, kind = 'nearest', fill_value="extrapolate")
            t = np.linspace(-15, 15, 103)
            res = np.array(f_res(t))
            vol = np.array(f_vol(t))
            if j == 0:
                map2D_res = np.array([res])
                map2D_vol = np.array([vol])
            else:
                map2D_res = np.vstack([map2D_res, res])
                map2D_vol = np.vstack([map2D_vol, vol])
            j += 1
            
    x, y = np.meshgrid(np.linspace(-15, 15, 103), np.linspace(-15, 15, 31))
    ax1.grid(False)
    ax2.grid(False)
    colormap_res = ax1.pcolor(x, y, map2D_res, cmap = 'gist_earth', vmax = max_res, vmin = min_res, rasterized=True)
    colormap_vol = ax2.pcolor(x, y, map2D_vol, cmap = 'gist_earth', vmax = max_vol, vmin = min_vol, rasterized=True)
    ax1.set_xlabel('X, mm')
    ax1.set_ylabel('Y, mm')
    ax1.set_title(r'$\Delta R$ map')
    ax2.set_xlabel('X, mm')
    ax2.set_ylabel('Y, mm')
    ax2.set_title(r'$\Delta V$ map')
    ax1.text(-15, 13, f'Z = {i}, mm', color = 'White', fontsize = 'x-large')
    ax2.text(-15, 13, f'Z = {i}, mm', color = 'White', fontsize = 'x-large')
    colorbar_res = fig1.colorbar(colormap_res)
    colorbar_res.set_label(r'$\Delta R$, Ohm')
    colorbar_vol = fig2.colorbar(colormap_vol)
    colorbar_vol.set_label(r'$\Delta V$, mV')
    if i != 11:
        fig1.savefig(os.path.join(cur_dir, 'data_files_230421', 'Maps_230421_3', f'Res_{i}.png'), dpi = 300)
        image_res = imageio.imread(os.path.join(cur_dir, 'data_files_230421', 'Maps_230421_3', f'Res_{i}.png'))
        frames_res_230421_3.append(image_res)
        fig2.savefig(os.path.join(cur_dir, 'data_files_230421', 'Maps_230421_3', f'Vol_{i}.png'), dpi = 300)
        image_vol = imageio.imread(os.path.join(cur_dir, 'data_files_230421', 'Maps_230421_3', f'Vol_{i}.png'))
        frames_vol_230421_3.append(image_vol)

imageio.mimsave(os.path.join(cur_dir, 'data_files_230421', 'Maps_230421_3', 'Res_230421.gif'), # output gif
                frames_res_230421_3, fps = 3, loop = 1)

imageio.mimsave(os.path.join(cur_dir, 'data_files_230421', 'Maps_230421_3', 'Vol_230421.gif'), # output gif
                frames_vol_230421_3, fps = 3, loop = 1)

files = os.listdir(os.path.join(cur_dir, 'data_files_230422'))

max_res = -1e18
max_vol = -1e18
min_vol = 1e18
min_res = 1e18

frames_res_230422 = []
frames_vol_230422 = []

for i in range(1, 26):
    j = 0
    for file in files:
        if i == int(file.split('_')[1].split('.')[0]) and j < 31:
            try:
                data = pd.read_csv(os.path.join(cur_dir, 'data_files_230422', file))
                res = data['GPIB0::1::INSTR.y'].values / 2 * 5e6
                res = res[:res.shape[0] // 2]
                vol = data['GPIB0::2::INSTR.x'].values * 1000
                vol = vol[:vol.shape[0] // 2]
                res_max = np.max(res)
                res_min = np.min(res)
                vol_max = np.max(vol)
                vol_min = np.min(vol)
                if res_max > max_res:
                    max_res = res_max
                if res_min < min_res:
                    min_res = res_min
                if vol_max > max_vol:
                    max_vol = vol_max
                if vol_min < min_vol:
                    min_vol = vol_min
            except:
                pass

for i in range(1, 26):
    j = 0
    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()
    for file in files:
        if i == int(file.split('_')[1].split('.')[0]) and j < 31:
            data = pd.read_csv(os.path.join(cur_dir, 'data_files_230422', file))
            res = data['GPIB0::1::INSTR.y'].values / 2 * 5e6
            res = res[:res.shape[0] // 2]
            vol = data['GPIB0::2::INSTR.x'].values * 1000
            vol = vol[:vol.shape[0] // 2]
            x = data['COM6.position'].values
            x = x[:x.shape[0] // 2]
            y = data['COM4.position'].values[0]
            z = data['COM5.position'].values[0]
            f_res = interp1d(x, res, kind = 'nearest', fill_value="extrapolate")
            f_vol = interp1d(x, vol, kind = 'nearest', fill_value="extrapolate")
            t = np.linspace(-15, 15, 103)
            res = np.array(f_res(t))
            vol = np.array(f_vol(t))
            if j == 0:
                map2D_res = np.array([res])
                map2D_vol = np.array([vol])
            else:
                map2D_res = np.vstack([map2D_res, res])
                map2D_vol = np.vstack([map2D_vol, vol])
            j += 1
    x, y = np.meshgrid(np.linspace(-15, 15, 103), np.linspace(-15, 15, 31))
    ax1.grid(False)
    ax2.grid(False)
    colormap_res = ax1.pcolor(x, y, map2D_res, cmap = 'gist_earth', vmax = max_res, vmin = min_res, rasterized=True)
    colormap_vol = ax2.pcolor(x, y, map2D_vol, cmap = 'gist_earth', vmax = max_vol, vmin = min_vol, rasterized=True)
    ax1.set_xlabel('X, mm')
    ax1.set_ylabel('Y, mm')
    ax1.set_title(r'$\Delta R$ map')
    ax2.set_xlabel('X, mm')
    ax2.set_ylabel('Y, mm')
    ax2.set_title(r'$\Delta V$ map')
    ax1.text(-15, 13, f'Z = {i + 55}, mm', color = 'White', fontsize = 'x-large')
    ax2.text(-15, 13, f'Z = {i + 55}, mm', color = 'White', fontsize = 'x-large')
    colorbar_res = fig1.colorbar(colormap_res)
    colorbar_res.set_label(r'$\Delta R$, Ohm')
    colorbar_vol = fig2.colorbar(colormap_vol)
    colorbar_vol.set_label(r'$\Delta V$, mV')
    if i != 1:
        fig1.savefig(os.path.join(cur_dir, 'data_files_230422', 'Maps_230422', f'Res_{i}.png'), dpi = 300)
        image_res = imageio.imread(os.path.join(cur_dir, 'data_files_230422', 'Maps_230422', f'Res_{i}.png'))
        frames_res_230422.append(image_res)
        fig2.savefig(os.path.join(cur_dir, 'data_files_230422', 'Maps_230422', f'Vol_{i}.png'), dpi = 300)
        image_vol = imageio.imread(os.path.join(cur_dir, 'data_files_230422', 'Maps_230422', f'Vol_{i}.png'))
        frames_vol_230422.append(image_vol)

imageio.mimsave(os.path.join(cur_dir, 'data_files_230422', 'Maps_230422', 'Res_230422.gif'), # output gif
                frames_res_230422, fps = 3, loop = 1)

imageio.mimsave(os.path.join(cur_dir, 'data_files_230422', 'Maps_230422', 'Vol_230422.gif'), # output gif
                frames_vol_230422, fps = 3, loop = 1)

files = os.listdir(os.path.join(cur_dir, 'data_files_230423'))

max_res = -1e18
max_vol = -1e18
min_vol = 1e18
min_res = 1e18

frames_res_230423 = []
frames_vol_230423 = []

for i in range(1, 13):
    j = 0
    for file in files:
        if i == int(file.split('_')[1].split('.')[0]) and j < 41:
            try:
                data = pd.read_csv(os.path.join(cur_dir, 'data_files_230423', file))
                res = data['GPIB0::1::INSTR.x'].values / 2 * 5e6
                res = res[:res.shape[0] // 2]
                vol = data['GPIB0::2::INSTR.x'].values * 1000
                vol = vol[:vol.shape[0] // 2]
                res_max = np.max(res)
                res_min = np.min(res)
                vol_max = np.max(vol)
                vol_min = np.min(vol)
                if res_max > max_res:
                    max_res = res_max
                if res_min < min_res:
                    min_res = res_min
                if vol_max > max_vol:
                    max_vol = vol_max
                if vol_min < min_vol:
                    min_vol = vol_min
            except:
                pass

for i in range(1, 13):
    j = 0
    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()
    for file in files:
        if i == int(file.split('_')[1].split('.')[0]) and j < 41:
            data = pd.read_csv(os.path.join(cur_dir, 'data_files_230423', file))
            res = data['GPIB0::1::INSTR.x'].values / 2 * 5e6
            res = res[:res.shape[0] // 2]
            vol = data['GPIB0::2::INSTR.x'].values * 1000
            vol = vol[:vol.shape[0] // 2]
            x = data['COM6.position'].values
            x = x[:x.shape[0] // 2]
            y = data['COM4.position'].values[0]
            z = data['COM5.position'].values[0]
            f_res = interp1d(x, res, kind = 'nearest', fill_value="extrapolate")
            f_vol = interp1d(x, vol, kind = 'nearest', fill_value="extrapolate")
            t = np.linspace(-20, 20, 136)
            res = np.array(f_res(t))
            vol = np.array(f_vol(t))
            if j == 0:
                map2D_res = np.array([res])
                map2D_vol = np.array([vol])
            else:
                map2D_res = np.vstack([map2D_res, res])
                map2D_vol = np.vstack([map2D_vol, vol])
            j += 1
            
    x, y = np.meshgrid(np.linspace(-20, 20, 136), np.linspace(-20, 20, 41))
    ax1.grid(False)
    ax2.grid(False)
    colormap_res = ax1.pcolor(x, y, map2D_res, cmap = 'gist_earth', vmax = max_res, vmin = min_res, rasterized=True)
    colormap_vol = ax2.pcolor(x, y, map2D_vol, cmap = 'gist_earth', vmax = max_vol, vmin = min_vol, rasterized=True)
    ax1.set_xlabel('X, mm')
    ax1.set_ylabel('Y, mm')
    ax1.set_title(r'$\Delta R$ map')
    ax2.set_xlabel('X, mm')
    ax2.set_ylabel('Y, mm')
    ax2.set_title(r'$\Delta V$ map')
    ax1.text(-20, 18, f'Z = {i}, mm', color = 'White', fontsize = 'x-large')
    ax2.text(-20, 18, f'Z = {i}, mm', color = 'White', fontsize = 'x-large')
    colorbar_res = fig1.colorbar(colormap_res)
    colorbar_res.set_label(r'$\Delta R$, Ohm')
    colorbar_vol = fig2.colorbar(colormap_vol)
    colorbar_vol.set_label(r'$\Delta V$, mV')
    if i != 2 and i != 17:
        fig1.savefig(os.path.join(cur_dir, 'data_files_230423', 'Maps_230423', f'Res_{i}.png'), dpi = 300)
        image_res = imageio.imread(os.path.join(cur_dir, 'data_files_230423', 'Maps_230423', f'Res_{i}.png'))
        frames_res_230423.append(image_res)
        fig2.savefig(os.path.join(cur_dir, 'data_files_230423', 'Maps_230423', f'Vol_{i}.png'), dpi = 300)
        image_vol = imageio.imread(os.path.join(cur_dir, 'data_files_230423', 'Maps_230423', f'Vol_{i}.png'))
        frames_vol_230423.append(image_vol)

imageio.mimsave(os.path.join(cur_dir, 'data_files_230423', 'Maps_230423', 'Res_230423.gif'), # output gif
                frames_res_230423, fps = 3, loop = 1)

imageio.mimsave(os.path.join(cur_dir, 'data_files_230423', 'Maps_230423', 'Vol_230423.gif'), # output gif
                frames_vol_230423, fps = 3, loop = 1)


files = os.listdir(os.path.join(cur_dir, 'data_files_230423_1'))

max_res = -1e18
max_vol = -1e18
min_vol = 1e18
min_res = 1e18

frames_res_230423_1 = []
frames_vol_230423_1 = []

for i in range(1, 21):
    j = 0
    for file in files:
        if i == int(file.split('_')[1].split('.')[0]) and j < 31:
            try:
                data = pd.read_csv(os.path.join(cur_dir, 'data_files_230423_1', file))
                res = data['GPIB0::1::INSTR.y'].values / 2 * 5e6
                res = res[:res.shape[0] // 2]
                vol = data['GPIB0::2::INSTR.x'].values * 1000
                vol = vol[:vol.shape[0] // 2]
                res_max = np.max(res)
                res_min = np.min(res)
                vol_max = np.max(vol)
                vol_min = np.min(vol)
                if res_max > max_res:
                    max_res = res_max
                if res_min < min_res:
                    min_res = res_min
                if vol_max > max_vol:
                    max_vol = vol_max
                if vol_min < min_vol:
                    min_vol = vol_min
            except:
                pass

for i in range(1, 21):
    j = 0
    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()
    for file in files:
        if i == int(file.split('_')[1].split('.')[0]) and j < 31:
            data = pd.read_csv(os.path.join(cur_dir, 'data_files_230423_1', file))
            res = data['GPIB0::1::INSTR.y'].values / 2 * 5e6
            res = res[:res.shape[0] // 2]
            vol = data['GPIB0::2::INSTR.x'].values * 1000
            vol = vol[:vol.shape[0] // 2]
            x = data['COM6.position'].values
            x = x[:x.shape[0] // 2]
            y = data['COM4.position'].values[0]
            z = data['COM5.position'].values[0]
            f_res = interp1d(x, res, kind = 'nearest', fill_value="extrapolate")
            f_vol = interp1d(x, vol, kind = 'nearest', fill_value="extrapolate")
            t = np.linspace(-15, 15, 103)
            res = np.array(f_res(t))
            vol = np.array(f_vol(t))
            if j == 0:
                map2D_res = np.array([res])
                map2D_vol = np.array([vol])
            else:
                map2D_res = np.vstack([map2D_res, res])
                map2D_vol = np.vstack([map2D_vol, vol])
            j += 1
            
    x, y = np.meshgrid(np.linspace(-15, 15, 103), np.linspace(-15, 15, 31))
    ax1.grid(False)
    ax2.grid(False)
    colormap_res = ax1.pcolor(x, y, map2D_res, cmap = 'gist_earth', vmax = max_res, vmin = min_res, rasterized=True)
    colormap_vol = ax2.pcolor(x, y, map2D_vol, cmap = 'gist_earth', vmax = max_vol, vmin = min_vol, rasterized=True)
    ax1.set_xlabel('X, mm')
    ax1.set_ylabel('Y, mm')
    ax1.set_title(r'$\Delta R$ map')
    ax2.set_xlabel('X, mm')
    ax2.set_ylabel('Y, mm')
    ax2.set_title(r'$\Delta V$ map')
    ax1.text(-15, 13, f'Z = {i}, mm', color = 'Black', fontsize = 'x-large')
    ax2.text(-15, 13, f'Z = {i}, mm', color = 'White', fontsize = 'x-large')
    colorbar_res = fig1.colorbar(colormap_res)
    colorbar_res.set_label(r'$\Delta R$, Ohm')
    colorbar_vol = fig2.colorbar(colormap_vol)
    colorbar_vol.set_label(r'$\Delta V$, mV')
    if i != 1 and i != 2:
        fig1.savefig(os.path.join(cur_dir, 'data_files_230423_1', 'Maps_230423', f'Res_{i}.png'), dpi = 300)
        image_res = imageio.imread(os.path.join(cur_dir, 'data_files_230423_1', 'Maps_230423', f'Res_{i}.png'))
        frames_res_230423_1.append(image_res)
        fig2.savefig(os.path.join(cur_dir, 'data_files_230423_1', 'Maps_230423', f'Vol_{i}.png'), dpi = 300)
        image_vol = imageio.imread(os.path.join(cur_dir, 'data_files_230423_1', 'Maps_230423', f'Vol_{i}.png'))
        frames_vol_230423_1.append(image_vol)

imageio.mimsave(os.path.join(cur_dir, 'data_files_230423_1', 'Maps_230423', 'Res_230423.gif'), # output gif
                frames_res_230423_1, fps = 3, loop = 1)

imageio.mimsave(os.path.join(cur_dir, 'data_files_230423_1', 'Maps_230423', 'Vol_230423.gif'), # output gif
                frames_vol_230423_1, fps = 3, loop = 1) 

frames_zero_gate_res = np.concatenate((frames_res_230421_3, frames_res_230421, frames_res_230422))
frames_zero_gate_vol = np.concatenate((frames_vol_230421_3, frames_vol_230421, frames_vol_230422))
    
imageio.mimsave(os.path.join(cur_dir,'Res_zero_gate_no_loop.gif'), # output gif
                frames_zero_gate_res, fps = 3, loop = 1)

imageio.mimsave(os.path.join(cur_dir,'Res_zero_gate_loop.gif'), # output gif
                frames_zero_gate_res, fps = 3)

imageio.mimsave(os.path.join(cur_dir,'Vol_zero_gate_no_loop.gif'), # output gif
                frames_zero_gate_vol, fps = 3, loop = 1)

imageio.mimsave(os.path.join(cur_dir,'Vol_zero_gate_loop.gif'), # output gif
                frames_zero_gate_vol, fps = 3)