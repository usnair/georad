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
