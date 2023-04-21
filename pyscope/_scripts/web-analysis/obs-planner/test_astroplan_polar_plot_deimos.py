# Test plot_sky and simbsd byte issue with PyWebIO using skeletal script

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import astropy.units as u
#from astroplan.plots import plot_sky
from astropy.time import Time
from astroplan import FixedTarget, Observer
import io
import pywebio
from pywebio import config,start_server
from astroquery.simbad import Simbad

from plot_sky_ftn import plot_sky

matplotlib.use('agg')  # required, use a non-interactive backend


def main():
    object_name = 'M1'
    
    observer = Observer.at_site('APO')
    observe_time = Time.now()
    observe_time = observe_time + np.linspace(-4, 5, 10)*u.hour
    
    object = FixedTarget.from_name(object_name)
    fig, ax = plt.subplots()
    plt.axis('off')
    ax = plot_sky(object, observer, observe_time)
    ax.legend(loc='center left', bbox_to_anchor=(1.25, 0.5))
    plot_sky(object, observer, observe_time)
    plt.legend(loc='center left', bbox_to_anchor=(1.25, 0.5))
    
    buf = io.BytesIO()
    fig.savefig(buf)
    pywebio.output.put_image(buf.getvalue())
    
    # Test lookup byte problem

    target = FixedTarget.from_name(object_name, name=object_name) # Astroplan FixedTarget object 
    coords = target.coord
    coords_str = target.coord.to_string(style ='hmsdms', precision=1, sep=':', decimal =False)  

   # Now try SIMBAD lookup to retrieve more information
    simbad = Simbad()
    simbad.add_votable_fields('dim', 'main_id','flux(V)','dimensions','otype','typed_id','otype','morphtype','sptype')
    t = simbad.query_object(object_name)
    objtype = t['OTYPE'][0]
    pywebio.output.put_text(objtype, type(objtype))

''''
if __name__ == "__main__":
    main()
'''
start_server(main, port=8080, debug=True)


