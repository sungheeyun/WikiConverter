import time
import sys
import os
import psutil

RUSAGE_DENOM = 1024.

if sys.platform == 'darwin':
    # ... it seems that in OSX the output is different units ...
    RUSAGE_DENOM = RUSAGE_DENOM * RUSAGE_DENOM


def memory_usage_psutil():
    # return the memory usage in MB
    process = psutil.Process(os.getpid())
    mem = process.memory_info()[0] / float(2 ** 20)
    return mem


def memory_usage_resource():
    import resource
    mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / RUSAGE_DENOM
    return mem


class Timer(object):
    name_timer_dict = dict()
    __locked = True

    def __init__(self, name):

        if Timer.__locked:
            raise Exception('Timer instance should be instantiated only via Timer.get_timer')

        self.name = name
        self.t0 = None

        self.record_dict = dict()

        self.tic()

    def tic(self):
        self.t0 = time.time()

        self.record_dict[self.t0] = list()

    def print_toc(self, s=None):
        if s:
            prefix = '{} took'.format(s)
        else:
            prefix = 'Elapsed time:'

        print('[{}] {} {:g}'.format(self.name, prefix, self.toc()))

    def toc(self):
        elapsed_time = time.time() - self.t0
        self.record_dict[self.t0].append(elapsed_time)

        return elapsed_time

    @staticmethod
    def get_timer(name=None):
        Timer.__locked = False
        if name not in Timer.name_timer_dict:
            Timer.name_timer_dict[name] = Timer(name)
        Timer.__locked = True

        return Timer.name_timer_dict[name]


class ResourceState(object):

    def __init__(self, name=None):
        assert name is None or isinstance(name, str), name.__class__

        self.name = name

        self.cpu0 = time.clock()
        self.t0 = time.time()

        self.cpuL = list()
        self.timL = list()
        self.psutilMemL = list()
        self.resourceMemL = list()

    def print_stats(self):
        print(self.get_stats_str())

    def get_stats_str(self):

        if len(self.cpuL) == 0:
            print('The record does not exist.')
            return

        if self.name is None:
            postf = ''
        else:
            postf = ' for %s' % self.name

        res = list()

        res.append('Stats%s' % postf)
        res.append('\tTotal elapsed time = %g sec.' % self.timL[-1])
        res.append('\tTotal CPU time = %g sec.' % self.cpuL[-1])
        res.append('\tMax Memory Usage (by psutil) = %g MB' % max(self.psutilMemL))
        res.append('\tMax Memory Usage (by resource) = %g MB' % max(self.resourceMemL))

        return '\n'.join(res)

    def record(self):

        self.cpuL.append(time.clock() - self.cpu0)
        self.timL.append(time.time() - self.t0)
        self.psutilMemL.append(memory_usage_psutil())
        self.resourceMemL.append(memory_usage_resource())


def ord_suffix(i):
    return {1: "st", 2: "nd", 3: "rd"}.get(i % 10 * (i % 100 not in [11, 12, 13]), "th")


def ord_suffix_str(i):
    return '%d%s' % (i, ord_suffix(i))


# def draw_hist_v_dict_list(ax, hist_v_dict_list, start_state=None, goal_state_list=None):
#    import matplotlib
#    assert isinstance(ax, matplotlib.axes.Axes), ax.__class__
#    assert goal_state_list is None or isinstance(goal_state_list, list), goal_state_list.__class__
#
#    vD = dict()
#
#    for idx, valueDict in enumerate(hist_v_dict_list):
#        assert isinstance(valueDict, dict), valueDict.__class__
#
#        for state, fcnval in valueDict.items():
#            if state not in vD:
#                vD[state] = dict()
#                vD[state]['epochL'] = list()
#                vD[state]['valL'] = list()
#
#            vD[state]['epochL'].append(idx)
#            vD[state]['valL'].append(fcnval)
#
#    for state, d in vD.items():
#        ax.plot(d['epochL'], d['valL'], '-')
#        ax.plot(d['epochL'][:1], d['valL'][:1], 'o')
#
#    if start_state is not None:
#        ax.plot(vD[start_state]['epochL'], vD[start_state]['valL'], 'r-', lw=5)
#
#    if goal_state_list is not None:
#        for goalState in goal_state_list:
#            ax.plot(vD[goal_state_list]['epochL'], vD[goal_state_list]['valL'], 'b-', lw=3)
#
#    ax.set_xlabel('Total of %d states' % len(vD))


class NewWikiTable(object):

    @staticmethod
    def false_function(x):
        return False

    def __init__(self, columnWidthL, title=None):
        assert isinstance(columnWidthL, list), columnWidthL.__class__
        assert title is None or isinstance(title, str), title.__class__

        self.columnWidthL = columnWidthL
        self.title = title
        self.nCols = len(columnWidthL)

        self.rowLL = list()

        self.__initialize()

    def __initialize(self):

        if self.title is None:
            self.title = 'Wiki Table'

    def add_row(self, rowL):
        assert isinstance(rowL, list), rowL.__class__
        assert len(rowL) == self.nCols, (len(rowL), self.nCols)
        self.rowLL.append(rowL)

    def add_row_flex(self, *pargs):

        res = list(pargs)[:self.nCols]

        if len(res) < self.nCols:
            res += [''] * (self.nCols - len(res))

        self.addRow(res)

    def write(self, fid, colorD=dict(), spanD=dict(), boldD=dict(), removeTestFcn=None, hide=False):

        fLL = list()
        for rowL in self.rowLL:
            fLL.append([True for cell in rowL])

        if removeTestFcn is None:
            removeTestFcn = NewWikiTable.false_function

        if hide:
            fid.write(
                '{{showhide showmessage="%s" hidemessage="Hide %s" effect="slide"'
                ' effectduration="0.5" style="background-color: #f6f6f6"}}\n'
                % (self.title, self.title)
            )
        else:
            fid.write('%s\n' % self.title)

        fid.write('(%% border="1" style="width:%dpx" %%)\n' % sum(self.columnWidthL))
        for rowIdx, rowL in enumerate(self.rowLL):

            if removeTestFcn(rowL):
                continue

            for colIdx, cell in enumerate(rowL):

                if not fLL[rowIdx][colIdx]:
                    continue

                colorStr = ''
                color = self.get_value_from_prop_dict(colorD, rowIdx, colIdx)
                if color is not None:
                    colorStr = '(%% style="color:%s" %%)' % color

                spanStr = ''
                span = self.get_value_from_prop_dict(spanD, rowIdx, colIdx)
                if span is not None:
                    spanStr = 'rowspan="%d" colspan="%d"' % span
                    for rr in range(rowIdx, rowIdx + span[0]):
                        for cc in range(colIdx, colIdx + span[1]):
                            fLL[rr][cc] = False

                boldB = False
                bold = self.get_value_from_prop_dict(boldD, rowIdx, colIdx)
                if bold is not None:
                    boldB = bold

                fid.write('|(%% %s style="text-align:center; width:%dpx" %%)%s%s' % (
                    spanStr,
                    self.columnWidthL[colIdx],
                    colorStr,
                    NewWikiTable.__get_cell_str(cell, boldB)
                ))

            fid.write('\n')

        if hide:
            fid.write('{{/showhide}}\n')

    @staticmethod
    def __get_cell_str(cell, boldB):
        assert isinstance(cell, str), cell.__class__

        if boldB:
            return '** %s **' % cell
        else:
            return cell

    def get_value_from_prop_dict(self, propD, rowIdx, colIdx):
        assert isinstance(propD, dict), propD.__class__
        assert isinstance(rowIdx, int), rowIdx.__class__
        assert isinstance(colIdx, int), colIdx.__class__

        if 'exceptions' in propD:
            exceptions = propD['exceptions']
            if rowIdx in exceptions:
                return None
            elif 'last' in exceptions and rowIdx == len(self.rowLL) - 1:
                return None

        res = None

        if rowIdx in propD:
            res = propD[rowIdx]
        elif 'even' in propD and rowIdx % 2 == 0:
            res = propD['even']
        elif 'odd' in propD and rowIdx % 2 == 1:
            res = propD['odd']
        elif 'zermodfour' in propD and rowIdx % 4 == 0:
            res = propD['zermodfour']
        elif 'onemodfour' in propD and rowIdx % 4 == 1:
            res = propD['onemodfour']
        elif 'twomodfour' in propD and rowIdx % 4 == 2:
            res = propD['twomodfour']
        elif 'thrmodfour' in propD and rowIdx % 4 == 3:
            res = propD['thrmodfour']

        elif (rowIdx, colIdx) in propD:
            res = propD[(rowIdx, colIdx)]
        elif rowIdx % 2 == 0 and ('even', colIdx) in propD:
            res = propD[('even', colIdx)]
        elif rowIdx % 2 == 1 and ('odd', colIdx) in propD:
            res = propD[('odd', colIdx)]
        elif colIdx % 2 == 0 and (rowIdx, 'even') in propD:
            res = propD[(rowIdx, 'even')]
        elif colIdx % 2 == 1 and (rowIdx, 'odd') in propD:
            res = propD[(rowIdx, 'odd')]

        return res

    # for backward compatibility

    addRow = add_row
    addRowFlex = add_row_flex


# def do_correlation_analysis(
#        data_frame,
#        scatter_plot_figsize=(20, 20),
#        corr_heatmap_figsize=(20, 20),
#        scatter_plot_kws=dict(),
#        corr_heatmap_kws=dict(),
#        skip_scatter_plot=False
# ):
#    if skip_scatter_plot:
#        fig1 = None
#    else:
#        import seaborn as sns
#        fig1 = sns.pairplot(data_frame, **scatter_plot_kws).fig
#        fig1.set_size_inches(*scatter_plot_figsize)
#
#    from matplotlib import pyplot as plt
#    corr = data_frame.corr()
#    fig2, ax2 = plt.subplots(figsize=corr_heatmap_figsize)
#    plot_corr_heatmap(corr, ax=ax2, **corr_heatmap_kws)
#
#    if fig1 is None:
#        return ((fig2,), corr)
#    else:
#        return ((fig1, fig2), corr)
#
#
# def plot_corr_heatmap(corr_matrix, ax=None, *pargs, **kargs):
#    """
#    Plots the heatmap for the correlation matrix.
#
#    :param corr_matrix: an object representing 2-D array which is a correlation matrix
#    :param pargs: any number of positional arguments
#    :param ax: matplotlib Axes on which it draws the heatmap
#    :param kargs: any number of keyword arguments
#    :return:
#    """
#    import seaborn as sns
#    vmin = kargs.pop('vmin', -1.0)
#    vmax = kargs.pop('vmax', 1.0)
#    # cmap = kargs.pop('cmap', sns.diverging_palette(250, 10, as_cmap=True))
#    cmap = kargs.pop('cmap', sns.diverging_palette(220, 10, as_cmap=True))
#    annot = kargs.pop('annot', True)
#
#    fig = sns.heatmap(
#        corr_matrix, ax=ax, vmin=vmin, vmax=vmax, cmap=cmap, annot=annot,
#        *pargs, **kargs
#    )
#
#    for xticklabel in ax.get_xticklabels():
#        xticklabel.set_rotation(90)
#        xticklabel.set_horizontalalignment('right')
#
#    for yticklabel in ax.get_yticklabels():
#        yticklabel.set_rotation(0)
#        yticklabel.set_horizontalalignment('right')
#
#    return fig
#
#
# def plot_corr(df, size=10):
#    '''Plot a graphical correlation matrix for a dataframe.
#
#    Input:
#        df: pandas DataFrame
#        size: vertical and horizontal size of the plot'''
#
#    from matplotlib import pyplot as plt
#    import matplotlib.pyplot as plt
#
#    # Compute the correlation matrix for the received dataframe
#    corr = df.corr()
#
#    # Plot the correlation matrix
#    fig, ax = plt.subplots(figsize=(size, size))
#    cax = ax.matshow(corr, cmap='RdYlGn')
#    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90);
#    plt.yticks(range(len(corr.columns)), corr.columns);
#
#    # Add the colorbar legend
#    cbar = fig.colorbar(cax, ticks=[-1, 0, 1], aspect=40, shrink=.8)
#
#    return fig, ax
