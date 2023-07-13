import numpy as np

def add_ticks(ax, labels_x, labels_y):
    
    y_tick_labels = [round(i, 2) for i in labels_y]

    x_tick_labels = [round(i, 2) for i in labels_x]

    y_ticks = []

    for ind, _ in enumerate(y_tick_labels):
        if len(y_tick_labels) != 1 and ind != len(y_tick_labels) - 1:
            y_ticks.append(round((abs((y_tick_labels[ind + 1] - y_tick_labels[ind])) / 2), 2))
        elif len(y_tick_labels) == 1:
            y_ticks.append(round((y_tick_labels[0] + 0.5), 2))

    if len(y_tick_labels) != 1:
        y_ticks.append(round((abs((y_tick_labels[-1] - y_tick_labels[-2])) / 2), 2))

    x_ticks = []

    for ind, _ in enumerate(x_tick_labels):
        if len(x_tick_labels) != 1 and ind != len(x_tick_labels) - 1:
            x_ticks.append(round((((x_tick_labels[ind + 1] - x_tick_labels[ind])) / 2), 2))
        elif len(x_tick_labels) == 1:
            x_ticks.append(round((x_tick_labels[0] + 0.5), 2))

    if len(x_tick_labels) != 1:
        x_ticks.append(round((abs((x_tick_labels[-1] - x_tick_labels[-2])) / 2), 2))

    y_ticks = np.arange(len(y_ticks)) + 0.5

    if len(y_ticks) > 6:
        ax.set_yticks(y_ticks[::len(y_ticks) // 6])
        ax.set_yticklabels(y_tick_labels[::len(y_tick_labels) // 6])
    else:
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_tick_labels)
        
    x_ticks = np.arange(len(x_ticks)) + 0.5
        
    if len(x_ticks) > 6:
        ax.set_xticks(x_ticks[::len(x_ticks) // 6])
        ax.set_xticklabels(x_tick_labels[::len(x_tick_labels) // 6], rotation=30)
    else:
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_tick_labels, rotation=30)