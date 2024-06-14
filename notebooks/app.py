import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore', SyntaxWarning)

from satpy.scene import Scene
from satpy.utils import debug_on
from satpy.composites import get_enhanced_image

from datetime import datetime

from glob import glob

import hvplot.xarray

import panel as pn

import numpy as np
## Starting to create satpy scenes
sat_files = glob("input/G16_ABI-L1b-RadF/*")
scn = Scene(filenames = sat_files, reader='abi_l1b')

dataset_names = scn.all_dataset_names()

#print(dataset_names)
scn.load([f'C{x:02d}' for x in range(1, 17)])
# Single bands
band_select = pn.widgets.Select(name='Band name', options=dataset_names)
def get_singleband_plot(bandname=None):
    
    scn.load([bandname])
    result = scn[bandname]
    interactive_plot = result.hvplot.image().opts(title=bandname)

    return interactive_plot
band_iplot = pn.bind(get_singleband_plot,bandname=band_select)
# Composite bands
# For composite bands, we have resolution mismatches to get fields
# so we resample all fields to 2km, by using area from the "C13" band

resampling_area = scn["C13"].area
resampled_scn = scn.resample(resampling_area)
field_select = pn.widgets.Select(name='Composite field name', options=scn.available_composite_names())
def get_compositebands_plot(fieldname=None):
    
    resampled_scn.load([fieldname])
    result = get_enhanced_image(resampled_scn[fieldname])

    result_da = result.data

    #scale result data array to 0 to 255, as 0 to 1 does not seem to work with hvplot
    result_da = result_da*255
    
    interactive_plot = result_da.hvplot.rgb(x='x',y='y',bands='bands',colorbar=True,
                         rasterize=True,dynamic=True,width=800,height=400).opts(title=fieldname)

    return interactive_plot
    
field_iplot = pn.bind(get_compositebands_plot,fieldname=field_select)
# App layout

template = pn.template.MaterialTemplate(
    site="Pythia cookbook",
    title="Visualize GOES-R data",
    sidebar= [],
    collapsed_sidebar=True
)

template.main.append(
    pn.Tabs(
        ("Single fields",
         pn.Row(
            band_select,
             band_iplot
            #sizing_mode='stretch_both'
            ),
        ),
        ("Composite fields",   
         pn.Row(
             field_select,
             field_iplot
            #sizing_mode='stretch_both'
            )
        )
    )
)
template.servable()