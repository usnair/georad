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