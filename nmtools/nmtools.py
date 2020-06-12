from pydap.client import open_url
from pydap.cas.urs import setup_session
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from ipywidgets import Button,Output
from datetime import datetime, timedelta, date
from dateutil import rrule
import ipywidgets as widgets
from IPython.display import display
from ipywidgets import HBox, VBox, Button,Layout, HTML,Output,GridspecLayout,Dropdown,GridBox,Textarea,Text,Password
from ipywidgets import  DatePicker,  FloatSlider
import seaborn as sns
from windrose import WindroseAxes
from calendar import monthrange
from datetime import datetime
import sys
sys.path.append("../panelobj")
from panelobj import PanelObject


#from ..openaqgui.openaqgui import OpenAQGui


from pydap.client import open_url
from pydap.cas.urs import setup_session
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from ipywidgets import Button,Output
from datetime import datetime, timedelta, date
from dateutil import rrule
import ipywidgets as widgets
from IPython.display import display
from ipywidgets import HBox, VBox, Button,Layout, HTML,Output,GridspecLayout,Dropdown,GridBox,Textarea,Text,Password
import seaborn as sns
from windrose import WindroseAxes

class MERRA_WindRose(PanelObject):
    
    def __init__(self,*args,**kwargs):
        self.title = "MERRA2 Wind Rose"
        self.accList =['NASA Earth Data']
        PanelObject.__init__(self,*args, **kwargs)
        self.windms = []
        self.windkt = []
        self.winddir = []
        self.times = []
    def getCP(self):
        self.setLabel() 
        self.usrTW = Text(value='',placeholder='',description='Username:',disabled=False)
        self.usrTW.observe(self.username,names='values')
        self.pwdPW = Password(value='',placeholder='',description='Password:',disabled=False)
        self.pwdPW.observe(self.password,names='value')
        self.st=widgets.DatePicker(description='Start Date',value = datetime.now(),disabled=False)
        self.et=widgets.DatePicker(description='End Date',value = datetime.now(),disabled=False) 
        self.st.observe(self.startDate)
        self.et.observe(self.endDate)
        self.latitude = widgets.BoundedFloatText(value=0.0,min=-90,max=90,step=0.01,description='Latitude:',disabled=False)
        self.longitude= widgets.BoundedFloatText(value=0.0,min=-180,max=180,step=0.01,description='Longitude:',disabled=False)
        self.latitude.observe(self.set_lat_val,names='value')
        self.longitude.observe(self.set_lon_val,names='value')
        self.plotms = Button(description='Plot in m/s',disabled=False,
                           layout={'width':'auto','border':'3px outset'})
        self.plotms.on_click(self.plotWindRose_ms)
        self.plotkt = Button(description='Plot in kt',disabled=False,
                           layout={'width':'auto','border':'3px outset'})
        self.plotkt.on_click(self.plotWindRose_kt)
        self.inpUSR.children+= (VBox([self.usrTW,self.pwdPW,self.st,self.et,self.latitude,self.longitude,self.plotms,self.plotkt],layout={'overflow':'visible'}),)
        with self.out_cp:
          self.out_cp.clear_output()
          display(self.getCP)
        return self.cp
        
    def username(self,t):
        username = t.value
    def password(self,t):
        password=self.pwdPW.value
        
    def startDate(self,date):
        self.start_date = datetime(self.st.value.year, self.st.value.month, self.st.value.day)

        return self.start_date
    def endDate(self,date):
        self.end_date = datetime(self.et.value.year, self.et.value.month, self.et.value.day)
        return self.end_date
    def get_data(self):
        url1 = 'https://goldsmr4.gesdisc.eosdis.nasa.gov:443/opendap/MERRA2/M2I1NXASM.5.12.4/'
        url2 = '/MERRA2_'
        url3 = '.inst1_2d_asm_Nx.'
        zero = '0'
        slash = '/'
        nc = '.nc4'
        for dt in rrule.rrule(rrule.DAILY, dtstart=self.start_date, until=self.end_date):
            #print('Getting data for',dt)
            self.times.append(dt)
            if dt.year >= 2011:
                val = 400
            if dt.year < 2011 and dt.year >= 2001:
                val = 300
            if dt.year < 2001 and dt.year >= 1992:
                val = 200
            if dt.year < 1992:
                val = 100
            if dt.month > 9 and dt.day < 10:
                opendap_url = url1+str(dt.year)+slash+str(dt.month)+url2+str(val)+url3+str(dt.year)+str(dt.month)+zero+str(dt.day)+nc
            if dt.month > 9 and dt.day >=10:
                opendap_url = url1+str(dt.year)+slash+str(dt.month)+url2+str(val)+url3+str(dt.year)+str(dt.month)+str(dt.day)+nc
            if dt.month < 10 and dt.day < 10:
                opendap_url = url1+str(dt.year)+slash+zero+str(dt.month)+url2+str(val)+url3+str(dt.year)+zero+str(dt.month)+zero+str(dt.day)+nc
            if dt.month < 10 and dt.day >= 10:
                opendap_url = url1+str(dt.year)+slash+zero+str(dt.month)+url2+str(val)+url3+str(dt.year)+zero+str(dt.month)+str(dt.day)+nc
            username = self.usrTW.value
            password = self.pwdPW.value
            session = setup_session(username, password, check_url=opendap_url)
            dataset = open_url(opendap_url, session=session)
            self.lon = dataset['lon'][:]
            self.lat = dataset['lat'][:]
            self.time = dataset['time'][:]
            self.uwind     = np.squeeze(dataset['U10M'][:,:,:])
            self.vwind  = np.squeeze(dataset['V10M'][:,:,:])
            self.lons,self.lats = np.meshgrid(self.lon,self.lat)
            self.lat_ind = (np.abs(self.lats[:,1]-self.latv)).argmin()
            self.lon_ind = (np.abs(self.lons[1,:]-self.lonv)).argmin()
            uwind = self.uwind[:,self.lat_ind,self.lon_ind].mean()
            vwind = self.vwind[:,self.lat_ind,self.lon_ind].mean()
            wind_speed = np.sqrt(uwind**2+ vwind**2)
            self.windms.append(wind_speed)
            ws_to_kt = wind_speed*0.514444
            self.windkt.append(ws_to_kt)
            wind_dir_trig_to = (np.arctan2((uwind/wind_speed), (vwind/wind_speed)))
            wind_dir_trig_to_degrees = (wind_dir_trig_to * (180/np.pi))
            wind_dir = wind_dir_trig_to_degrees + 180 
            self.winddir.append(wind_dir)

            
        
    def set_lat_val(self,value):
        self.latv = self.latitude.value
    def set_lon_val(self,value):
        self.lonv = self.longitude.value
    def plotWindRose_kt(self,b):
        plt.ioff()
        with self.out_cp:
          self.out_cp.clear_output()
          print("Getting data ...")
          self.get_data()
          print("Finished")
          fig = plt.figure(figsize=(10, 5))
          ax = WindroseAxes.from_ax()

          ax.bar(self.winddir, self.windkt, normed=True, opening=0.8, edgecolor='white')
          ax.set_legend()
          title = 'MERRA2 Wind Rose (kt) from ' + str(self.start_date) + ' to ' + str(self.end_date) + ' at Latitude ' + str(self.latitude.value) + ' and Longitude ' + str(self.longitude.value)
          ax.set_title(title)
        
          plt.show()
    def plotWindRose_ms(self,b):
        plt.ioff()
        with self.out_cp:
          self.out_cp.clear_output()
          print("Getting data ...")
          self.get_data()
          print("Finished")
          fig = plt.figure(figsize=(10, 5))
          ax = WindroseAxes.from_ax()
          ax.bar(self.winddir, self.windms, normed=True, opening=0.8, edgecolor='white')
          title = 'MERRA2 Wind Rose (m/s) from ' + str(self.start_date) + ' to ' + str(self.end_date) + ' at Latitude ' + str(self.latitude.value) + ' and Longitude ' + str(self.longitude.value)
          ax.set_title(title)
          ax.set_legend()
          plt.show()
class MerraAQSpatial(PanelObject):
  def __init__(self,ptype='space',*args,**kwargs):
    self.title = 'MERRA AQ Spatial Maps'
    PanelObject.__init__(self,*args, **kwargs)
    self.ptype = ptype
  def getCP(self):
    self.setLabel()
    self.plon= 0.0
    self.plat=0.0
    self.dateSelection = datetime.now()
    self.dateLast = datetime(1950,1,1)
    self.selectVar ='AOD'
    self.selectTime=0
    self.dateSW = DatePicker(description='Date',
                             layout=Layout(width='280px'),
                             value = self.dateSelection,
                             disabled=False)
    self.myWidget1=Dropdown(options=['AOD','DUST_PM','SALT_PM','ORG_CARB','BLK_CARB','SO4','PM2.5'],
                            value='AOD',
                            layout=Layout(width='250px'),
                            description='Variable:',
                            disabled=False
                            )
    
    self.myWidget2=Dropdown(options=[],
                            value=None,
                            layout=Layout(width='250px'),
                            description='Varibale:',
                            disabled=False
                            )
  
    self.myWidget3=Dropdown(options=[],
                            value=None,
                            description='Date:',
                            disabled=False
                            )
    self.myWidget4=Dropdown(options=[],
                            value=None,
                            layout=Layout(width='250px'),
                            description='Time:',
                            disabled=False
                            )
    self.latSW = FloatSlider(min=-90.0, max=90.0, step=0.25, 
                                  description='Lat:',disabled=False, continuous_update=False,
                                  orientation='horizontal',readout=True,readout_format='.2f'
                                  )
    self.lonSW = FloatSlider(min=-180.0, max=180.0, step=0.25, 
                                  description='Lon:',disabled=False, continuous_update=False,
                                  orientation='horizontal',readout=True,readout_format='.2f'
                                  )


    self.plotBW = Button(description='Spatial Plot',disabled=False,layout={'width':'200px','border':'3px outset'})
    if self.ptype == 'space':
      self.inpUSR.children+= (HBox([VBox([self.dateSW,self.myWidget4,self.myWidget1]),VBox([self.plotBW])],layout={'overflow':'visible'}),)
    else:
      self.inpUSR.children+= (HBox([VBox([self.dateSW,self.myWidget1]),VBox([self.timeplot,
                              self.latSW,self.lonSW])],layout={'overflow':'visible'}),)
    self.year=np.arange(41)+1980
    self.mm=np.arange(12)+1
    
    
    # formatter = "{:02d}".format
    # self.months=[formatter(item) for item in mm]
    self.dateSW.observe(self.dateSWCB)
    self.myWidget2.options=self.mm
    self.myWidget1.observe(self.myCallback1,names='value')
    self.myWidget2.observe(self.myCallback2,names='value')
    self.date=np.arange(1,30)+1
    self.time=np.arange(24)
    self.myWidget3.options=self.date
    self.myWidget4.options=self.time
    self.myWidget3.observe(self.myCallback3,names='value')
    self.myWidget4.observe(self.myCallback4,names='value')    
    self.latSW.observe(self.latSWCB,names='value')
    self.lonSW.observe(self.lonSWCB,names='value')
    self.plotBW.on_click(self.plotObs)
    return self.cp
  def dateSWCB(self,change):
    if change['type'] == 'change':
      self.dateSelection = self.dateSW.value
  def myCallback1(self,b):
    self.selectVar = self.myWidget1.value
    # print(self.selectYear)
  def myCallback2(self,b):
    formatter = "{:02d}".format
    self.selectMonth=self.myWidget2.value
    self.selectMonth=formatter(self.selectMonth)
    
    # print(self.selectMonth)
  def myCallback3(self,b):
    formatter = "{:02d}".format
    self.selectDate=formatter(self.myWidget3.value)
  def myCallback4(self,b):
    self.selectTime=self.myWidget4.value
  
  def latSWCB(self,change):
      self.plat = self.latSW.value
  def lonSWCB(self,change):
      self.plon = self.lonSW.value

  def plotObs(self,b):
    
    if self.dateSelection.year<1992: self.Vnumber='100'
    elif self.dateSelection.year<2001: self.Vnumber='200'
    elif self.dateSelection.year<2011: self.Vnumber='300'
    else: self.Vnumber='400'

    self.selectYear = self.dateSelection.strftime('%Y')
    self.selectMonth = self.dateSelection.strftime('%m')
    self.selectDate  = self.dateSelection.strftime('%d')
    if self.dateSelection !=  self.dateLast:
      username = self.pwdDict['NASA Earth Data']['user']
      password = self.pwdDict['NASA Earth Data']['password']
      with self.out_cp:
        print('Accessing data...')
      self.opendap_url='https://goldsmr4.gesdisc.eosdis.nasa.gov/opendap/MERRA2/M2T1NXAER.5.12.4/'+self.selectYear+'/'+self.selectMonth+'/MERRA2_'+self.Vnumber+'.tavg1_2d_aer_Nx.'+self.selectYear+self.selectMonth+self.selectDate+'.nc4'
      session = setup_session(username, password, check_url=self.opendap_url)
      dataset = open_url(self.opendap_url, session=session)
      #dataset = open_url(opendap_url)
      lon = dataset['lon'][:]
      lat = dataset['lat'][:]
      self.lons,self.lats = np.meshgrid(lon,lat)
      t=int(self.selectTime)
      aod      = np.squeeze(dataset['TOTEXTTAU'][t,:,:], axis=0)
      dust_pm  = np.squeeze(dataset['DUSMASS25'][t,:,:], axis=0)*1000000000.0
      salt_pm  = np.squeeze(dataset['SSSMASS25'][t,:,:], axis=0)*1000000000.0
      org_carb = np.squeeze(dataset['OCSMASS'][t,:,:], axis=0)*1000000000.0
      blk_carb = np.squeeze(dataset['BCSMASS'][t,:,:], axis=0)*1000000000.0
      so4      = np.squeeze(dataset['SO4SMASS'][t,:,:], axis=0)*1000000000.0
      pm25 = (1.375*so4 + 1.6*org_carb + blk_carb + dust_pm + salt_pm)
      self.vardict = {'AOD': aod,'DUST_PM': dust_pm ,'SALT_PM': salt_pm,'ORG_CARB':org_carb,
                      'BLK_CARB':blk_carb,'SO4':so4,'PM2.5':pm25}
    self.varlab = {'AOD'     : 'Unitless',
                   'DUST_PM' : r'$\mu g m^{-3}$',
                   'SALT_PM' : r'$\mu g m^{-3}$',
                   'ORG_CARB': r'$\mu g m^{-3}$',
                   'BLK_CARB': r'$\mu g m^{-3}$',
                   'SO4'     :r'$\mu g m^{-3}$',
                   'PM2.5'   :r'$\mu g m^{-3}$'
                   }
    var = self.vardict[self.selectVar]
    
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
      plt.contourf(self.lons, self.lats, var,transform=ccrs.PlateCarree(),cmap=plt.cm.jet)
      formatter = "{:02d}".format
      tt=formatter(self.selectTime)
      plt.title('MERRA2 '+
                self.selectVar+
                ','+
                tt+
                ':00 UTC '+ 
                self.selectYear+
                '-'+
                self.selectMonth+
                '-'+
                self.selectDate, 
                size=14
                )
      cb = plt.colorbar(ax=ax, orientation="vertical", pad=0.02, aspect=16, shrink=0.8)
      cb.set_label(self.varlab[self.selectVar],size=12,rotation=90,labelpad=15)
      cb.ax.tick_params(labelsize=10)
      plt.show()
      self.dateLast = self.dateSelection


class MerraAQTseries(PanelObject):
  def __init__(self,ptype='time',*args,**kwargs):
    self.title = 'MERRA GUI'
    PanelObject.__init__(self,*args, **kwargs)
    self.ptype = ptype
  def getCP(self):
    self.setLabel()
    self.plon= 0.0
    self.plat=0.0
    self.dateSelection = datetime.now()
    self.dateLast = datetime(1950,1,1)
    self.selectVar ='AOD'
    self.selectTime=0
    self.dateSW = DatePicker(description='Date',
                             layout=Layout(width='280px'),
                             value = self.dateSelection,
                             disabled=False)
    self.myWidget1=Dropdown(options=['AOD','DUST_PM','SALT_PM','ORG_CARB','BLK_CARB','SO4','PM2.5'],
                            value='AOD',
                            layout=Layout(width='280px'),
                            description='Variable:',
                            disabled=False
                            )
    
    self.myWidget2=Dropdown(options=[],
                            value=None,
                            layout=Layout(width='280px'),
                            description='Variable:',
                            disabled=False
                            )
  
    self.myWidget3=Dropdown(options=[],
                            value=None,
                            description='Date:',
                            disabled=False
                            )
    self.myWidget4=Dropdown(options=[],
                            value=None,
                            layout=Layout(width='250px'),
                            description='Time:',
                            disabled=False
                            )
    self.latSW = FloatSlider(min=-90.0, max=90.0, step=0.25, 
                                  description='Lat:',disabled=False, continuous_update=False,
                                  orientation='horizontal',readout=True,readout_format='.2f'
                                  )
    self.lonSW = FloatSlider(min=-180.0, max=180.0, step=0.25, 
                                  description='Lon:',disabled=False, continuous_update=False,
                                  orientation='horizontal',readout=True,readout_format='.2f'
                                  )


    self.plotBW = Button(description='Spatial Plot',disabled=False,layout={'width':'200px','border':'3px outset'})
    self.timeplot=Button(description='Time Series Plot',disabled=False,layout={'width':'auto','border':'3px outset'})
    if self.ptype == 'space':
      self.inpUSR.children+= (HBox([VBox([self.dateSW,self.myWidget4,self.myWidget1]),VBox([self.plotBW])],layout={'overflow':'visible'}),)
    else:
      self.inpUSR.children+= (HBox([VBox([self.dateSW,self.latSW,self.lonSW]),VBox([self.myWidget1,self.timeplot])],layout={'overflow':'visible'}),)
    self.year=np.arange(41)+1980
    self.mm=np.arange(12)+1
    
    
    # formatter = "{:02d}".format
    # self.months=[formatter(item) for item in mm]
    self.dateSW.observe(self.dateSWCB)
    self.myWidget2.options=self.mm
    self.myWidget1.observe(self.myCallback1,names='value')
    self.myWidget2.observe(self.myCallback2,names='value')
    self.date=np.arange(1,30)+1
    self.time=np.arange(24)
    self.myWidget3.options=self.date
    self.myWidget4.options=self.time
    self.myWidget3.observe(self.myCallback3,names='value')
    self.myWidget4.observe(self.myCallback4,names='value')    
    self.latSW.observe(self.latSWCB,names='value')
    self.lonSW.observe(self.lonSWCB,names='value')
    #self.plotBW.on_click(self.plotObs)
    self.timeplot.on_click(self.tplots)
    return self.cp
  def dateSWCB(self,change):
    if change['type'] == 'change':
      self.dateSelection = self.dateSW.value
  def myCallback1(self,b):
    self.selectVar = self.myWidget1.value
    # print(self.selectYear)
  def myCallback2(self,b):
    formatter = "{:02d}".format
    self.selectMonth=self.myWidget2.value
    self.selectMonth=formatter(self.selectMonth)
    
    # print(self.selectMonth)
  def myCallback3(self,b):
    formatter = "{:02d}".format
    self.selectDate=formatter(self.myWidget3.value)
  def myCallback4(self,b):
    self.selectTime=self.myWidget4.value
  
  def latSWCB(self,change):
      self.plat = self.latSW.value
  def lonSWCB(self,change):
      self.plon = self.lonSW.value

  def tplots(self,b):
    if self.dateSelection.year<1992: self.Vnumber='100'
    elif self.dateSelection.year<2001: self.Vnumber='200'
    elif self.dateSelection.year<2011: self.Vnumber='300'
    else: self.Vnumber='400'

    self.selectYear = self.dateSelection.strftime('%Y')
    self.selectMonth = self.dateSelection.strftime('%m')
    self.selectDate  = self.dateSelection.strftime('%d')
    
    if self.dateSelection != self.dateLast:
      with self.out_cp:
        print('Accessing data...')
      self.opendap_url='https://goldsmr4.gesdisc.eosdis.nasa.gov/opendap/MERRA2/M2T1NXAER.5.12.4/'+self.selectYear+'/'+self.selectMonth+'/MERRA2_'+self.Vnumber+'.tavg1_2d_aer_Nx.'+self.selectYear+self.selectMonth+self.selectDate+'.nc4'
      # #Put your NASA Earthdata username and password here
      username = self.pwdDict['NASA Earth Data']['user']
      password = self.pwdDict['NASA Earth Data']['password']
      #username='mxue02'
      #password='Xzx19950222'
      session = setup_session(username, password, check_url=self.opendap_url)
      dataset = open_url(self.opendap_url, session=session)
      self.lon = dataset['lon'][:]
      self.lat = dataset['lat'][:]
      #set the latitude and longtitude here
      plon=-120
      plat=45
      with self.out_cp:
        print('User selected lat/lon',self.plat,self.plon)
      ind_lon=(np.abs(np.asarray(self.lon) - self.plon)).argmin()
      ind_lat=(np.abs(np.asarray(self.lat)-self.plat)).argmin()
      ind_lon=int(ind_lon)
      ind_lat=int(ind_lat)
    
      aod= np.squeeze(dataset['TOTEXTTAU'][:,ind_lon,ind_lat])
      dust_pm  = np.squeeze(dataset['DUSMASS25'][:,ind_lon,ind_lat])*1000000000.0
      salt_pm  = np.squeeze(dataset['SSSMASS25'][:,ind_lon,ind_lat])*1000000000.0
      org_carb = np.squeeze(dataset['OCSMASS'][:,ind_lon,ind_lat])*1000000000.0
      blk_carb = np.squeeze(dataset['BCSMASS'][:,ind_lon,ind_lat])*1000000000.0
      so4      = np.squeeze(dataset['SO4SMASS'][:,ind_lon,ind_lat])*1000000000.0
      pm25 = (1.375*so4 + 1.6*org_carb + blk_carb + dust_pm + salt_pm)
      self.vardict = {'AOD': aod,'DUST_PM': dust_pm ,'SALT_PM': salt_pm,'ORG_CARB':org_carb,
                 'BLK_CARB':blk_carb,'SO4':so4,'PM2.5':pm25}
    self.varlab = {'AOD'     : 'AOD (Unitless)',
                   'DUST_PM' : r'Dust PM$_{2.5}(\mu g m^{-3})$',
                   'SALT_PM' : r'Salt PM$_{2.5}(\mu g m^{-3})$',
                   'ORG_CARB': r'Org Carbon PM$_{2.5} (\mu g m^{-3})$',
                   'BLK_CARB': r'Black Carbon PM$_{2.5}(\mu g m^{-3})$',
                   'SO4'     :r'SO$_4 PM_{2.5} (\mu g m^{-3})$',
                   'PM2.5'   :r'Total PM$_{2.5}(\mu g m^{-3})$'
                   }
    var = self.vardict[self.selectVar] 
    tt=np.arange(24)
    with self.out_cp:
      plt.ioff()
      self.out_cp.clear_output()
      fig = plt.figure(figsize=(8,4))
      plt.plot(tt,var)
      plt.title('Diurnal variation of MERRA2 '+self.selectVar+','+ self.selectYear+'-'+self.selectMonth+'-'+self.selectDate)
      plt.xlabel('Time (UTC)')
      plt.ylabel(self.varlab[self.selectVar])
      plt.show()
      self.dateLast = self.dateSelection