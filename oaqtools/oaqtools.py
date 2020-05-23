from IPython.display import display
from ipywidgets import HBox, VBox, Button,Layout, HTML,Output,\
                       GridspecLayout,Dropdown,GridBox,Textarea,Text
import openaq
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from .openaqgui import OpenAQGui

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