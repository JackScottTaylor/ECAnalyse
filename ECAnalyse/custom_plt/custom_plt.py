# This module contains the function custom_plt which sets a series of custom parameters for matplotlib plots.
# and then returns the customised plt object so it can be used as people are used to.

from .color_palettes import *

# These are explicitly defined here so that they can be accessed
# so the user can design custom figure sizes based on these
# standard values.
fig_w, fig_h = 8.3, 6.225
import matplotlib.pyplot as plt
import numpy as np

def gca():
    ax = plt.old_gca()
    ax.old_plot = ax.plot
    ax.plot = gen_ax_plot(ax)
    return ax

def custom_plt(color_palette=IBM):
    if type(color_palette) == str:
        color_palette = color_palette.lower()
        if color_palette == 'ibm': color_palette = IBM
        elif color_palette == 'tol': color_palette = Tol
        elif color_palette == 'wong': color_palette = Wong
        elif color_palette == 'cb4': color_palette = cb4
        else: color_palette = IBM
    plt.rcParams['axes.prop_cycle'] 				= plt.cycler(color=color_palette)  # Color cycle

    # Set some general parameters.
    plt.rcParams['lines.linewidth'] 				= 3                      # Linewidth
    plt.rcParams['figure.figsize'] 					= [fig_w, fig_h]         # Figure size
    plt.rcParams['axes.linewidth'] 					= 1.2                    # Axes linewidth
    plt.rcParams['font.family'] 					= 'Arial'                # Font family
    plt.rcParams['mathtext.fontset'] 				= 'dejavusans'           # Math font
    plt.rcParams['font.size'] 						= 24                     # Font size
    plt.rcParams['savefig.dpi'] 					= 300                    # Savefig dpi
    plt.rcParams['savefig.format'] 					= 'pdf'                  # Savefig format
    plt.rcParams['figure.constrained_layout.h_pad'] = 0.1                    # Padding in constrained layout
    plt.rcParams['figure.constrained_layout.w_pad'] = 0.1                    # Padding in constrained layout
    plt.rcParams['figure.constrained_layout.use'] 	= True                   # Use constrained layout
    plt.rcParams['legend.labelspacing'] 			= 0.15                   # Legend label spacing
    plt.rcParams['legend.handletextpad']            = 0.3                    # Legend handle text padding
    plt.rcParams['axes.xmargin']					= 0.01                   # X margin
    plt.rcParams['axes.ymargin'] 					= 0.01                   # Y margin
    plt.rcParams['legend.frameon']                  = True                   # Legend frame on
    plt.rcParams['legend.fontsize']                 = 20                     # Legend font size

    # Rewriting some plotting functions so storing the old functions as attributes
    new_plt              = plt
    new_plt.old_gca      = plt.gca
    new_plt.old_subplots = plt.subplots

    def gca():
        '''
        Instead of rewriting the general matplotlib.axes.Axes class and trying to get matplotlib.pyplot
        to use that, instead for each Axes object redefine the plot function. This is perhaps not the most 
        efficient method but as never generating too many Axes objects then should be okay. Function checks
        whether Axes object has old_plot attribute and if it doesn't then adds the new plot function.
        '''
        ax = new_plt.old_gca()
        if hasattr(ax, 'old_plot'): return ax
        ax.old_plot = ax.plot
        ax.plot = gen_ax_plot(ax)
        return ax
    

    def gen_ax_plot(ax):
        # This function generates the new plot function for a provided Axes object.

        def ax_plot(*args, scalex=True, scaley=True, data=None, 
                roll_av=1, raw_transp=False, **kwargs):
            '''
            Creates a new plot function which has the ability to plot the rolling average and to
            also plot the raw data in the same color and half transparent.
            '''
            if raw_transp:
                kwargs['alpha'] = 0.25
                label = ''
                if 'label' in kwargs.keys(): label = kwargs['label']
                kwargs['label'] = ''
                t_plot = ax.old_plot(*args, scalex=scalex, scaley=scaley, data=data, **kwargs)
                kwargs['alpha'] = 1
                kwargs['color'] = t_plot[0].get_color()
                kwargs['label'] = label

            args = [np.convolve(arg, np.ones(roll_av), 'valid') / roll_av for arg in args]
            return ax.old_plot(*args, scalex=scalex, scaley=scaley, data=data, **kwargs)
        return ax_plot
    

    def subplots(nrows=1, ncols=1, *empty, sharex=False, sharey=False, squeeze=True,
                width_ratios=None, height_ratios=None, subplot_kw=None, gridspec_kw=None,
                **fig_kw):
        '''
        This function redefines the subplots function of pyplot.
        It renames the original Axes.plot function and then defines a new Axes.plot function
        which included the extra functionality.
        '''
        
        fig, axs = new_plt.old_subplots(nrows=nrows, ncols=ncols, *empty, sharex=sharex, sharey=sharey,
                                squeeze=squeeze, width_ratios=width_ratios, height_ratios=height_ratios,
                                subplot_kw=subplot_kw, gridspec_kw=gridspec_kw,
                                **fig_kw)
        if not type(axs) == np.ndarray: axs = [axs]
        for ax in axs:
            ax.old_plot = ax.plot
            ax.plot = gen_ax_plot(ax)

        if len(axs) == 1: return fig, axs[0]
        return fig, axs

    new_plt.gca         = gca
    new_plt.subplots    = subplots

    return new_plt