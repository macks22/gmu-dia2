# coding: utf-8
import os
import zipfile
import matplotlib.pyplot as plt

tableau10 = [
    (31, 119, 180),
    (255, 127, 14),
    (44,160,44),
    (214,39,40),
    (148,103,189),
    (140,86,75),
    (227,119,194),
    (127,127,127),
    (188,189,34),
    (23,190,207)
]
to_rgb_float = lambda num: num / 255.0
colors = [tuple(map(to_rgb_float, tup)) for tup in colors]
basic_colors = ['b', 'g', 'r', 'y', 'm', 'c']


def plot_data(data, labels, num_subplots=5, per_subplot=50,
              name="barplot", colors=colors):
    max_size = max([len(l) for l in data])
    size = max_size
    x = np.arange(size)

    n_subplots = np.ceil(float(size) / per_subplot)
    num_plots = int(np.ceil(float(n_subplots) / num_subplots))
    print "writing %d plots with %d subplots each" % (num_plots, num_subplots)

    plotsize = num_subplots * per_subplot
    yticks = ['0.0', '', '0.5', '', '1.0']
    width = 0.85 / len(data)

    try: os.mkdir(name)
    except OSError: pass
    prevdir = os.curdir
    zpath = os.path.join(os.path.abspath(name), '%s.zip' % name)
    zf = zipfile.ZipFile(zpath, 'w')
    os.chdir(name)

    for pnum in range(num_plots):
        rectangles = []
        fig = plt.figure()
        for spnum in range(num_subplots):
            ax = plt.subplot(num_subplots,1,spnum+1)
            start = spnum * per_subplot + pnum * plotsize
            end = (spnum+1) * per_subplot + pnum * plotsize

            for dnum, dat in enumerate(data):
                rect = ax.bar(x[start:end]+(dnum*width), dat[start:end],
                              width=width, color=colors[dnum])
                ax.set_yticklabels(yticks)
                ax.set_xlim(start, end)

                # Shrink current axis's height by 10% on the bottom
                # box = ax.get_position()
                # ax.set_position([box.x0, box.y0, box.width * 0.9, box.height])

                if spnum == 0: rectangles.append(rect)

            if spnum == 0:
                firsts = [r[0] for r in rectangles]
                ax.set_title(name)
                # Put a legend to the right of the current axis
                ax.legend(firsts, labels,
                          loc='center left', bbox_to_anchor=(1, 0.8))

        fig.set_size_inches(18,10)
        fname = "%s-%s.png" % (name, pnum)
        plt.savefig(fname, bbox_inches='tight', dpi=300)
        zf.write(fname)
        fig.clf()

    os.chdir(prevdir)
    zf.close()
