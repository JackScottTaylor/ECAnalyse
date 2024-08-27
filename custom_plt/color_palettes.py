# This module simply contains come color palettes that can be used for plotting.
# Personally I think the IBM color palette is the nicest but the number of colors is
# slightly limited

# I have switched the order of the Wong color palette slightly as I (Jack) wanted
#  the second colour to be blue. 
Wong = [
    '#000000', # black
    '#0072B2', # blue
    '#D55E00', # vermillion
    '#CC79A7', # reddish purple
    '#E69F00', # orange
    '#56B4E9', # sky blue
    '#009E73', # bluish green
    '#F0E442', # yellow
]

# For the Tol color palette I (Jack) have made the first colour black and have
# reversed the usual order.
Tol = [ '#000000'] + [
        '#332288',
        '#117733',
        '#44AA99',
        '#88CCEE',
        '#DDCC77',
        '#CC6677',
        '#AA4499',
        '#882255',
][::-1]

# For the IBM color palette I (Jack) have made the first colour black and have
# mixed up the order to suit my preferences.
IBM = [
    '#000000',
    '#DC267F',
    '#648FFF',
    '#FFB000',
    '#785EF0',
    '#FE6100'
]

# Found at 'https://stackoverflow.com/questions/65013406/how-to-generate-30-distinct-colors-that-are-color-blind-friendly'
# A fourth color-blind friendly palette that contains a lot more distinct colours.
cb4 = [
    "#000000",
    "#004949",
    "#009292",
    "#ff6db6",
    "#ffb6db",
    "#490092",
    "#006ddb",
    "#b66dff",
    "#6db6ff",
    "#b6dbff",
    "#920000",
    "#924900",
    "#db6d00",
    "#24ff24",
    "#ffff6d"
]