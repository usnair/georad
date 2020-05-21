#Module imports
from IPython.display import display
from ipywidgets import HBox, VBox, Button,Layout, HTML,Output,GridspecLayout,Dropdown,GridBox,Textarea,Text,Password
import openaq
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from georad import panel_class.PanelObject as PanelObject

class OpenAQGui(PanelObject):
  def __init__(self,*args,**kwargs):
    self.title = 'OpenAQ GUI'
    PanelObject.__init__(self,*args, **kwargs)

    # initialize openaq api

    self.api        = openaq.OpenAQ()

    self.createGuiElemenents()

  def getCP(self):
    return self.cp

  def createGuiElemenents(self):

    # setup selection widgets

    self.countrySW = Dropdown(options=[],
                              value=None,
                              description='Country:',
                              layout=Layout(width='250px', grid_area='country'),
                              disabled=False
                             )
    
    self.citySW    = Dropdown(options=[],
                              value=None,
                              description='City:',
                              layout=Layout(width='250px', grid_area='city'),
                              disabled=False
                             )
    
    self.locationSW = Dropdown(options=[],
                               value=None,
                               description='Location:',
                               layout=Layout(width='250px', grid_area='location'),
                               disabled=False
                              )
    self.inpUSR.children+= (VBox([self.countrySW,self.citySW,self.locationSW],layout={'overflow':'visible'}),)
    
    # get the list of countries. Set the default country selection 
    # to be the first country on the list and extract the corresponding 
    # country code

    self.countries  = self.api.countries(df=True,limit=1000)
    self.country    = self.countries.iloc[0]['name']
    self.ccode    = self.countries.iloc[0]['code']
    
    self.countrySW.options = list(self.countries['name'])

    self.countrySW.value   = self.country
    
    # get the list of cities for the country selected and set the 
    # default city selection to be the first city on the list

    self.updateCities()

    # get the list of locations for the city selected and set the 
    # default location selection to be the first location on the list

    self.updateLocations()

    # set up  callback functions for the selection widgets

    self.countrySW.observe(self.countrySWCB,names='value')

    self.citySW.observe(self.citySWCB,names='value')

    self.locationSW.observe(self.locationSWCB,names='value')


  def updateCities(self):
    self.cities         = self.api.cities(country=self.ccode,df=True,limit=1000)
    self.city           = self.cities.iloc[0]['city']
    cities              = list(self.cities['name'])
    self.citySW.options = [i.replace("\n","")for i in  cities]
    self.citySW.value   = self.city

  def updateLocations(self):
  
    self.locations  = self.api.locations(city=self.city,df=True,limit=1000)
    self.location   = self.locations.iloc[0]['location']
    locations       = list(self.locations['location'])
    self.locationSW.options = [i.replace("\n","")for i in  locations]
    self.locationSW.value   = self.location

  def countrySWCB(self,change):
    if change['type'] == 'change':

      # set the country to the new user selected value given 
      # by the "value" attribute in the country selection widget.
      
      self.country    = self.countrySW.value
      self.ccode      = self.countries[self.countries['name'] == self.country]['code'].values[0]

      # get list of cities and set the default city as the first city
      # on the list

      self.updateCities()

      # get list of locations and set the default location as the first location
      # on the list

      self.updateLocations()     

  def citySWCB(self,change):
    if change['type'] == 'change':

      # set the city to the new user selected value given 
      # by the "value" attribute in the city selection widget.

      self.city    = self.citySW.value

      # get list of locations and set the default location as the first location
      # on the list

      self.updateLocations()    

  def locationSWCB(self,change):
    if change['type'] == 'change':

      # set the location to the new user selected value given 
      # by the "value" attribute in the location selection widget.

      self.location    = self.locationSW.value
      #self.showQuery()

  def execQuery(self):
      try:
        df = self.locations.loc[self.locations['location']==self.location].T
        with self.out_cp:
          self.out_cp.clear_output()
          display(df)
      except Exception:
        with self.out_cp:
          self.out_cp.clear_output()
          print('Error getting data')

############################################################
############################################################
############################################################
class QueryOpenAq(OpenAQGui):
  def __init__(self,*args,**kwargs):
    OpenAQGui.__init__(self,*args, **kwargs)

  def getCP(self):

    self.title = 'Query OpenAQ'

    self.setLabel()
    
    self.showInfo = Button(description='Query',disabled=False,
                           layout={'width':'auto','border':'3px outset'})
    
    self.showInfo.on_click(self.showQuery)

    self.inpUSR.children+= (VBox([self.showInfo],layout={'overflow':'visible'}),)


    return self.cp

  def showQuery(self,b):
      try:
        df = self.locations.loc[self.locations['location']==self.location].T
        with self.out_cp:
          self.out_cp.clear_output()
          display(df)
      except Exception:
        with self.out_cp:
          self.out_cp.clear_output()
          print('Error getting data')

class PlotOpenAq(OpenAQGui):
  def __init__(self,*args,**kwargs):
    OpenAQGui.__init__(self,*args, **kwargs)

  def getCP(self):

    self.title = 'Query OpenAQ'
    
    self.setLabel()
    
    self.plotStn = Button(description='Plot',disabled=False,
                           layout={'width':'150px','overflow':'visible','border':'3px outset'})
    
    self.plotStn.on_click(self.plotObs)

    self.inpUSR.children+= (VBox([self.plotStn],layout={'overflow':'visible'}),)

    return self.cp
  
  def plotObs(self,b):
    try:
      res = self.api.measurements(location=self.location,parameter='pm25', limit=10000,df=True)
      plot_obs = True
    except Exception:
      print("Error getting data")
      plot_obs = False
      return False
    with self.out_cp:
      plt.ioff()
      fig,ax = plt.subplots(1, figsize=(12, 6))
      sns.set(style="ticks", font_scale=1.35)
      for group, df in res.groupby('location'):
        _df = df.query("value >= 0.0").resample('12h').mean()
        # Convert from ppm to ppb
        _df['value'] *= 1e0
        # Plot the data
        _df.value.plot(ax=ax, label=group)
      ax.legend(loc='best')
      ax.set_ylim(0, None)
      ax.set_ylabel("$PM2.5 \; [\mu m^-3]$", fontsize=18)
      ax.set_xlabel("")
      # move the legend to the side
      plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
      sns.despine(offset=5)
      self.out_cp.clear_output()
      #display(fig)
      plt.show()
      return True
