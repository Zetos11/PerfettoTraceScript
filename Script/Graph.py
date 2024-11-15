import sys
import matplotlib.pyplot as plt
import matplotx
import numpy as np
import seaborn as sns

context = {'font.size': 10.0,
 'axes.labelsize': 'large',
 'axes.titlesize': 'large',
 'xtick.labelsize': 'large',
 'ytick.labelsize': 'large',
 'legend.fontsize': 'large',
 'legend.title_fontsize': 'large',
 'axes.linewidth': 0.8,
 'grid.linewidth': 0.8,
 'lines.linewidth': 1.5,
 'lines.markersize': 6.0,
 'patch.linewidth': 1.0,
 'xtick.major.width': 0.8,
 'ytick.major.width': 0.8,
 'xtick.minor.width': 0.6,
 'ytick.minor.width': 0.6,
 'xtick.major.size': 3.5,
 'ytick.major.size': 3.5,
 'xtick.minor.size': 2.0,
 'ytick.minor.size': 2.0
}

palette = sns.color_palette("deep", 25)


def display_graph(data):
    sns.set_theme(context=context, style="dark", palette=palette)
    fig = plt.figure()
    fig.set_size_inches(15, 15)
    gs = fig.add_gridspec(len(data), hspace=0.5)
    axs = gs.subplots(sharex=True)
    fig.suptitle('Rails Power Consumption')
    idx = 0
    colors = get_color_list(len(data))
    for elt in data:
        x = []
        for i in range(len(elt["delta_list"])):
            x.append(i*0.25)  # 0.25 is the time interval between each energy sample
        y = np.array(elt["delta_list"])
        axs[idx].plot(x, y, color=palette[idx], label=elt["rail"])
        axs[idx].yaxis.get_major_ticks()[0].label1.set_visible(False)
        matplotx.line_labels(axs[idx])
        idx += 1

    for ax in axs:
        ax.label_outer()

    plt.show()
    fig.savefig("out/out.png")

def get_color_list(size):
    color = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    res = []
    for i in range(size//8 + 1):
        res = res + color
    return res

