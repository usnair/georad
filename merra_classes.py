from pydap.client import open_url
from pydap.cas.urs import setup_session
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from ipywidgets import Button,Output
from georad import panel_class.PanelObject as PanelObject

# Explore this link to select the appropriate dataset and variable - https://goldsmr4.gesdisc.eosdis.nasa.gov/opendap/hyrax/MERRA2/. 
# In the example below, I am pulling aerosol fields from MERRA2 diurnal dataset.  When you navigate down to datasets, it has info on
# different variables 

class MerraAero(PanelObject):
  def __init__(self,*args,**kwargs):
    self.title = 'MERRA GUI'
    PanelObject.__init__(self,*args, **kwargs)
    self.opendap_url="https://goldsmr4.gesdisc.eosdis.nasa.gov/opendap/MERRA2_DIURNAL/M2TUNXAER.5.12.4/2019/MERRA2_400.tavgU_2d_aer_Nx.201911.nc4"

    self.plotBW = Button(description='Plot',disabled=False,layout={'width':'auto','border':'3px outset'})
    
    self.plotBW.on_click(self.plotObs)

    self.inpUSR.children+= (VBox([self.plotBW],layout={'overflow':'visible'}),)
  def getCP(self):
    return self.cp
  def plotObs(self,b):
    #Put your NASA Earthdata username and password here
    username = self.pwdDict['NASA Earth Data']['user']
    #username = 'nair@nsstc.uah.edu'
    password = self.pwdDict['NASA Earth Data']['password']
    session = setup_session(username, password, check_url=self.opendap_url)
    dataset = open_url(self.opendap_url, session=session)
    #dataset = open_url(opendap_url)
    lon = dataset['lon'][:]
    lat = dataset['lat'][:]
    aod      = np.squeeze(dataset['TOTEXTTAU'][0,:,:])
    dust_pm  = np.squeeze(dataset['DUSMASS25'][0,:,:])
    salt_pm  = np.squeeze(dataset['SSSMASS25'][0,:,:])
    org_carb = np.squeeze(dataset['OCSMASS'][0,:,:])
    blk_carb = np.squeeze(dataset['BCSMASS'][0,:,:])
    so4      = np.squeeze(dataset['SO4SMASS'][0,:,:])
    pm25 = (1.375*so4 + 1.6*org_carb + blk_carb + dust_pm + salt_pm)*1000000000.0
    eta  = pm25/aod
    lons,lats = np.meshgrid(lon,lat)
    # Set the figure size, projection, and extent
    with self.out_cp:
      plt.ioff()
      self.out_cp.clear_output()
      fig = plt.figure(figsize=(8,4))
      ax = plt.axes(projection=ccrs.Robinson())
      ax.set_global()
      #ax.set_extent([65, 100, 5.0,35.0])
      ax.coastlines(resolution="110m",linewidth=1)
      ax.gridlines(linestyle='--',color='black')
      # Set contour levels, then draw the plot and a colorbar
      clevs = np.arange(230,311,5)
      plt.contourf(lons, lats, pm25,transform=ccrs.PlateCarree(),cmap=plt.cm.jet)
      plt.title('MERRA2 Aerosol Eta Factor, 0 UTC,1 Nov 2019', size=14)
      cb = plt.colorbar(ax=ax, orientation="vertical", pad=0.02, aspect=16, shrink=0.8)
      cb.set_label('K',size=12,rotation=0,labelpad=15)
      cb.ax.tick_params(labelsize=10)
      plt.show()
