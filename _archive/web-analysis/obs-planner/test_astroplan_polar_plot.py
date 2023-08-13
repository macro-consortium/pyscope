# Test plot_sky with PyWegIO using skeletal script

import numpy as np
import matplotlib,astroplan
import matplotlib.pyplot as plt
import astropy.units as u
from astroplan.plots import plot_sky
from astropy.time import Time
from astroplan import FixedTarget, Observer
import io
import pywebio,astroquery
from pywebio import config,start_server
from astroquery.simbad import Simbad
import astroquery,astropy

#matplotlib.use('agg')  # required, use a non-interactive backend


def main():
    
    web = True

    if web:
        pywebio.output.put_text('Matplotlib version: ', matplotlib.__version__)
        pywebio.output.put_text('Astroplan version: ', astroplan.__version__)
    else:
        print('Matplotlib version: ', matplotlib.__version__)
        print('Astroplan version: ', astroplan.__version__)
        print('Astroquery version',astroquery.__version__)
        print('Astropy version',astropy.__version__)
    
    object_name = 'M81'
    
    observer = Observer.at_site('APO')
    observe_time = Time.now()
    observe_time = observe_time + np.linspace(-4, 5, 10)*u.hour
    
    object = FixedTarget.from_name(object_name)
    
    # Create fig, ax objects using kw args, not subplots(projection=polar) [no longer supported]
    fig,ax = plt.subplots(subplot_kw={'projection':'polar'})
    #plt.axis('off') # remove axis rectangular box
    ax = plot_sky(object, observer, observe_time,ax=ax)
    ax.legend(loc='center left', bbox_to_anchor=(0.85, 1.0))
    
    if web:
        buf = io.BytesIO()
        fig.savefig(buf)
        pywebio.output.put_image(buf.getvalue())
    else:
        plt.show()
    # Test lookup byte problem

    target = FixedTarget.from_name(object_name, name=object_name) # Astroplan FixedTarget object 
    coords = target.coord
    coords_str = target.coord.to_string(style ='hmsdms', precision=1, sep=':', decimal =False) 
    print(coords_str) 

   # Now try SIMBAD lookup to retrieve more information
    simbad = Simbad()
    simbad.add_votable_fields('dim', 'main_id','flux(V)','dimensions','otype','typed_id','otype','morphtype','sptype')
    t = simbad.query_object(object_name)
    objtype = t['OTYPE'][0]
    
    # Otype returns either a string or byte depending on version of astroquery!
    print(type(objtype))
    try:
        objtype = objtype.decode()
    except (UnicodeDecodeError, AttributeError):
        pass
    
    if web:
       pywebio.output.put_text(objtype, type(objtype))
    else:
       print(objtype, type(objtype))

if __name__ == "__main__":
    main()

start_server(main, port=8080, debug=True)


