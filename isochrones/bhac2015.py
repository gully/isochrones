# %load dartmouth.py
from __future__ import division,print_function
import os,os.path, glob, re
import numpy as np
from pkg_resources import resource_filename
import logging

from scipy.interpolate import LinearNDInterpolator as interpnd
try:
    import pandas as pd
except ImportError:
    pd = None

import pickle

#from .isochrone import Isochrone
from isochrones import Isochrone

#DATADIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
DATADIR = os.getenv('ISOCHRONES',
                    os.path.expanduser(os.path.join('~','.isochrones')))
if not os.path.exists(DATADIR):
    os.mkdir(DATADIR)


TRI_FILE = '{}/BHAC2015.tri'.format(DATADIR)

## For now, just read my local file,
## will want to generalize for wider consumption later
## To get this file run this and point the pandas read_csv to where you put it.
## wget https://raw.githubusercontent.com/BrownDwarf/ApJdataFrames/master/data/BCAH2002/BCAH2002_isochrones.csv > ../isochrones/data/BCAH2002_isochrones.csv
df1 = pd.read_csv('../../../GitHub/ApJdataFrames/data/BHAC2015/BHAC2015_isochrones_simple.csv', delim_whitespace=True)
# hack to make sure stuff will compile for now.
df1['feh'] = 0.0
df1['J'] = df1['Mj']

# Total hack to deal with metallicity, see Isochrones Issue #23.
df2, df3 = df1.copy(), df1.copy()
df2['feh'] = 0.1
df3['feh'] = -0.1
df_out = pd.concat([df1, df2, df3], ignore_index=True)
df1 = df_out


class BHAC2015_Isochrone(Isochrone):
    """BCAH (2002) pre-main sequence stellar models.

    :param bands: (optional)
        ``['J']``, which is the default.


    """
    def __init__(self,bands=['J'], minage=6.0, **kwargs):

        df = df1

        mags = {}
        for band in bands:
            mags[band] = df[band]

        try:
            f = open(TRI_FILE,'rb')
            tri = pickle.load(f)
        except:
            f = open(TRI_FILE,'rb')
            tri = pickle.load(f,encoding='latin-1')
        finally:
            f.close()

        Isochrone.__init__(self,df['mass'],df['Age'],
                           df['feh'],df['mass'],df['logL'],
                           df['Teff'],df['logg'],mags,tri=tri,
                           minage=minage, **kwargs)

    def agerange(self, m, feh=0.0):
        minage = 5.69897 * np.ones_like(m)
        maxage = 10.0 * np.ones_like(m)
        return minage,maxage


############ utility functions used to set up data sets from originals ############


def write_tri(df=df1, outfile=TRI_FILE):
    """
    Writes the Delanuay triangulation of the models to file.
    """
    N = len(df)
    pts = np.zeros((N,3))
    pts[:,0] = np.array(df['mass'])
    pts[:,1] = np.array(df['Age'])
    pts[:,2] = np.array(df['feh'])
    Jmags = np.array(df['J'])

    Jfn = interpnd(pts,Jmags)

    f = open(outfile,'wb')
    pickle.dump(Jfn.tri,f)
    f.close()
    return Jfn


write_tri()
