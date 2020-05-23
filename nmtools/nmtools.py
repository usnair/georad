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
import seaborn as sns
from windrose import WindroseAxes
import sys
sys.path.append("../panelobj")
from panelobj import PanelObject


#from ..openaqgui.openaqgui import OpenAQGui


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
        url1 = 'https://goldsmr4.gesdisc.eosdis.nasa.gov:443/opendap/MERRA2/M2T1NXAER.5.12.4/'
        url2 = '/MERRA2_'
        url3 = '.tavg1_2d_aer_Nx.'
        zero = '0'
        slash = '/'
        nc = '.nc4'
        self.pm25_val = []
        self.times = []
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
            self.aod      = np.squeeze(dataset['TOTEXTTAU'][:,:,:])
            self.dust_pm  = np.squeeze(dataset['DUSMASS25'][:,:,:])
            self.salt_pm  = np.squeeze(dataset['SSSMASS25'][:,:,:])
            self.org_carb = np.squeeze(dataset['OCSMASS'][:,:,:])
            self.blk_carb = np.squeeze(dataset['BCSMASS'][:,:,:])
            self.so4   = np.squeeze(dataset['SO4SMASS'][:,:,:])
            self.pm25 = (1.375*self.so4 + 1.6*self.org_carb + self.blk_carb + self.dust_pm + self.salt_pm)*1000000000.0
            self.lons,self.lats = np.meshgrid(self.lon,self.lat)
            self.lat_ind = (np.abs(self.lats[:,1]-self.latv)).argmin()
            self.lon_ind = (np.abs(self.lons[1,:]-self.lonv)).argmin()
            self.ave = self.pm25[:,self.lat_ind,self.lon_ind].mean()
            self.pm25_val.append(self.ave)
    def set_lat_val(self,value):
        self.latv = self.latitude.value
    def set_lon_val(self,value):
        self.lonv = self.longitude.value 
    def plotPM25(self,b):
        fig,ax = plt.subplots(1, figsize=(12, 6))
        plt.ioff()
        with self.out_cp:
          self.out_cp.clear_output()
          print("Getting data ...")
          self.get_data()
          print("Finished")
          ax.plot(self.times,self.pm25_val)
          ax.tick_params(axis ='x', rotation = 45)
          title = 'Daily Mean MERRA2 PM2.5' + ' at Latitude ' + str(self.latitude.value) + ' and Longitude ' + str(self.longitude.value)
          ax.set_title(title)
          #ax.set_title('Daily Mean MERRA2 PM2.5')
          ax.set_ylabel('$PM2.5 \; [\mu m^-3]$')
          plt.show()

