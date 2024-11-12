# This module contains the function custom_plt which sets a series of custom parameters for matplotlib plots.
# and then returns the customised plt object so it can be used as people are used to.


from .color_palettes import *

# These are explicitly defined here so that they can be accessed
# so the user can design custom figure sizes based on these
# standard values.
fig_w, fig_h = 8.3, 6.225

from matplotlib.pyplot import plot as ref_plot

import matplotlib.pyplot as plt
import numpy as np

def plot(*args, scalex=True, scaley=True, data=None, 
         roll_av=1, raw_transp=False, **kwargs):
    '''
    Redefinition of matplotlib.pyplot plot method so that can add some convenience
    One option to add is performing rolling average and plotting the raw in transparent.
    '''
    if raw_transp:
        kwargs['alpha'] = 0.25
        label = ''
        if 'label' in kwargs.keys(): label = kwargs['label']
        kwargs['label'] = ''
        t_plot = ref_plot(*args, scalex=scalex, scaley=scaley, data=data, **kwargs)
        kwargs['alpha'] = 1
        kwargs['color'] = t_plot[0].get_color()
        kwargs['label'] = label

    args = [np.convolve(arg, np.ones(roll_av), 'valid') / roll_av for arg in args]
    ref_plot(*args, scalex=scalex, scaley=scaley, data=data, **kwargs)
    

def custom_plt():
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
    plt.rcParams['axes.prop_cycle'] 				= plt.cycler(color=IBM)  # Color cycle
    plt.rcParams['legend.frameon']                  = True                   # Legend frame on
    plt.rcParams['legend.fontsize']                 = 20                     # Legend font size

    plt.plot = plot
    return plt