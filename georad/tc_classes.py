### Tool to plot tropical cyclone path using Tropycal
### Written by Christopher Phillips
### Direct questions to chris.phillips@uah.edu

### Import required modules
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime as dt
import ipywidgets as ipw
import matplotlib.pyplot as pp
import numpy
import tropycal.tracks as tracks
from pydap.client import open_url
from pydap.cas.urs import setup_session
from ipywidgets import HBox, VBox, Button,Layout, HTML,Output,GridspecLayout,Dropdown,GridBox,Textarea,Text,Password
from georad import panel_class.PanelObject as PanelObject

### TCPATH class to plot tropical cyclone path
class TCPath(PanelObject):

    ### Constructor method
    def __init__(self,*args,**kwargs):

        #Set title of panel
        self.title = 'TC Path Tool'

        #Derive class from parent object
        PanelObject.__init__(self,*args, **kwargs)

        #Create Cartopy projection
        self.pcp = ccrs.PlateCarree()

        #Create cartopy feature objects
        self.countries = cfeature.NaturalEarthFeature(category='cultural',
            name='admin_0_countries', scale='50m', facecolor='none')
        self.states = cfeature.NaturalEarthFeature(category="cultural",
            name="admin_1_states_provinces_lines", scale="50m", facecolor="none")

        #Create data set parameters
        self.tpc_source = "ibtracs"
        self.available_basins = ["north_atlantic", "south_america", "east_pacific", "west_pacific", "south_pacific", "north_indian", "south_indian", "australian"]

        #Create GUI elements for storm selection
        #Layout for storm selection elements
        menu_layout = {"width":"auto", "height":"auto"}

        #Dropdown list to select hurricane basin
        self.basin_list = ipw.Dropdown(options=self.available_basins, value=None, description="Basin", disabled=False, layout=menu_layout)
        
        #Text box to enter a year
        self.year_box = ipw.BoundedIntText(value=None, min=1851, max=2019, description="Season", disabled=False, layout=menu_layout)

        #Dropdown menu with storm names
        self.storm_list = ipw.Dropdown(options=[None], value=None, description="Storm", disabled=False, layout=menu_layout)

        #Add button to load storm
        self.storm_button = ipw.Button(description="Load Storm", tooltip="Load Storm and Plot Track", disabled=False, layout={"width":"auto", "border":"3px outset", "height":"auto"})

        #Add GUI elements to display list
        dummy = HBox([self.storm_list, self.storm_button], layout={"width":"auto", "height":"auto", "overflow":"visible"})
        self.inpUSR.children+= (VBox([self.basin_list, self.year_box, dummy],layout={"width":"auto", "height":"auto", "overflow":"visible"}),)

        #Add callback function to buttons and menus
        self.storm_button.on_click(self.plot_storm) #Plot the storm track on button click
        self.basin_list.observe(self.load_tropycal) #Load Tropycal when you select a basin
        self.year_box.observe(self.load_season)     #Load storm list when a season is selected

    ### Method to return GUI contorl panel object
    def getCP(self):
        return self.cp

    ### Method to load IBTrACS
    def load_season(self, change):

        #Check if basin menu changed (and not None)
        if ((change["type"] == "change") and (change["name"] == "value") and (self.year_box.value != None)):

            #Load the season
            self.season = self.tpc_dataset.get_season(self.year_box.value)

            #Loop over all storms in season
            names = []
            ids = []
            for k in self.season.dict.keys():
                names.append("{} - {}".format(self.season.dict[k]["name"], self.season.dict[k]["date"][0].strftime("%Y/%m/%d")))
                ids.append(self.season.dict[k]["id"])

            #Update the storm list
            self.storm_list.options = list(zip(names, ids))

        #Returning
        return

    ### Method to load tropycal dataset on basin selection
    def load_tropycal(self, change):
        #Check if basin menu changed (and not None)
        if ((change["type"] == "change") and (change["name"] == "value") and (self.basin_list.value != None)):

            #Load dataset
            self.tpc_dataset = tracks.TrackDataset(self.basin_list.value, self.tpc_source)

        #Returning
        return

    ### Method to plot storm track (button call back)
    def plot_storm(self, button):

        #Load storm
        self.storm = self.tpc_dataset.get_storm(self.storm_list.value)

        #Direct plot output to display
        with self.out_cp:

            #Turn of blocking behavior of pyplot.show
            plt.ioff()

            #Clear any previous output
            self.out_cp.clear_output()
            try:
                pp.close(fig)
            except:
                pass

            #Create figure and axis objects
            fig, ax = pp.subplots(subplot_kw={"projection":self.pcp})
                                
            #Plot storm track
            ax.plot(self.storm.dict["lon"], self.storm.dict["lat"], color="red", transform=self.pcp)

            #Make the plotlook like a map        
            #Set extent (Box around storm track with 10 degree padding
            ax.set_extent([numpy.min(self.storm.dict["lon"])-10, numpy.max(self.storm.dict["lon"])+10, numpy.min(self.storm.dict["lat"])-10, numpy.max(self.storm.dict["lat"])+10])

            #Coasts and countries
            ax.coastlines()
            ax.add_feature(self.states, edgecolor="black", linewidth=1)
            ax.add_feature(self.countries, edgecolor="black", linewidth=1)

            #Gridlines
            gridlines = ax.gridlines(crs=self.pcp, draw_labels=True, linestyle=":", color="black")
            gridlines.xlabels_top = False
            gridlines.ylabels_right = False

            #Map image
            ax.stock_img()

            #Label the plot
            ax.set_title("Storm {}".format(self.storm.dict["name"]), fontsize=14)

            #Display plot
            pp.show()

        #Returning
        return

### Tool to plot tropical cyclone location in conjunctyion with MERRA
### Written by Christopher Phillips
### Direct questions to chris.phillips@uah.edu
### TCPATH class to plot tropical cyclone path
class TCMERRA(PanelObject):

    ### Constructor method
    def __init__(self,*args,**kwargs):

        #Set title of panel
        self.title = 'TC-MERRA Analysis'

        #Derive class from parent object
        PanelObject.__init__(self,*args, **kwargs)

        #Create Cartopy projection
        self.pcp = ccrs.PlateCarree()

        #Create cartopy feature objects
        self.countries = cfeature.NaturalEarthFeature(category='cultural',
            name='admin_0_countries', scale='50m', facecolor='none')
        self.states = cfeature.NaturalEarthFeature(category="cultural",
            name="admin_1_states_provinces_lines", scale="50m", facecolor="none")

        #Create data set parameters
        self.tpc_source = "ibtracs"
        self.available_basins = ["north_atlantic", "south_america", "east_pacific", "west_pacific", "south_pacific", "north_indian", "south_indian", "australian"]

        #Create GUI elements for storm selection
        #Layout for storm selection elements
        menu_layout = {"width":"auto", "height":"auto"}

        #Dropdown list to select hurricane basin
        self.basin_list = ipw.Dropdown(options=self.available_basins, value=None, description="Basin", disabled=False, layout=menu_layout)
        
        #Text box to enter a year
        self.year_box = ipw.BoundedIntText(value=None, min=1851, max=2019, description="Season", disabled=False, layout=menu_layout)

        #Dropdown menu with storm names
        self.storm_list = ipw.Dropdown(options=[None], value=None, description="Storm", disabled=False, layout=menu_layout)

        #Add button to load storm
        self.storm_button = ipw.Button(description="Load Storm", tooltip="Load Storm and Plot Track", disabled=False, layout={"width":"auto", "border":"3px outset", "height":"auto"})

        #Add dropdown menu with storm dates
        self.date_list = ipw.Dropdown(options=[None], value=None, description="Date", disabled=False, layout=menu_layout)

        #Add GUI elements to display list
        left = VBox([self.basin_list, self.year_box, self.storm_list],layout={"width":"auto", "height":"auto", "overflow":"visible"})
        right = VBox([self.storm_button, self.date_list], layout={"width":"auto", "height":"auto", "overflow":"visible"})
        self.inpUSR.children+= (HBox([left, right],layout={"width":"auto", "height":"auto", "overflow":"visible"}),)

        #Add callback function to buttons and menus
        self.storm_button.on_click(self.load_storm) #Plot the storm track on button click
        self.date_list.observe(self.change_date)
        self.basin_list.observe(self.load_tropycal) #Load Tropycal when you select a basin
        self.year_box.observe(self.load_season)     #Load storm list when a season is selected

    ### Method to change date information for object
    def change_date(self, change):

        #Check for date selection change
        if ((change["type"] == "change") and (change["name"] == "value")):

            #Set current date
            self.date = self.date_list.value

            #Find index of current date in storm info
            for i in range(len(self.storm.dict["date"])):
                if (self.date == self.storm.dict["date"][i]):
                    self.date_ind = i
                    break

            #Replot storm location
            self.plot_storm()

        #Returning
        return

    ### Method to return GUI contorl panel object
    def getCP(self):
        return self.cp

    ### Method to subset data
    ### Generates indices that match desired region of plot
    ### Inputs:
    ###  extent, list of floats, [west lon, east lon, south lat, north lat]
    ###
    ### Outputs,
    ###   subset, tuple of ints (y1, y2, x1, x2), array indices corresponding to subsetted region.
    def get_subset(self):
                                    
        #Calculate coordinates of each bounding side
        dx = self.lons[1]-self.lons[0]
        dy = self.lats[1]-self.lats[0]
        lon1_ind = int((self.storm_extent[0]-self.lons[0])/dx)
        lon2_ind = int((self.storm_extent[1]-self.lons[0])/dx)
        lat1_ind = int((self.storm_extent[2]-self.lats[0])/dy) #Do south first because MERRA stores south first.
        lat2_ind = int((self.storm_extent[3]-self.lats[0])/dy)
        
        self.yind1 = lat1_ind
        self.yind2 = lat2_ind
        self.xind1 = lon1_ind
        self.xind2 = lon2_ind

        #Returning
        return 

    ### Method to load IBTrACS
    def load_season(self, change):

        #Check if basin menu changed (and not None)
        if ((change["type"] == "change") and (change["name"] == "value") and (self.year_box.value != None)):

            #Load the season
            self.season = self.tpc_dataset.get_season(self.year_box.value)

            #Loop over all storms in season
            names = []
            ids = []
            for k in self.season.dict.keys():
                names.append("{} - {}".format(self.season.dict[k]["name"], self.season.dict[k]["date"][0].strftime("%Y/%m/%d")))
                ids.append(self.season.dict[k]["id"])

            #Update the storm list
            self.storm_list.options = list(zip(names, ids))

        #Returning
        return

    ### Method to load data from Tropycal and MERRA
    def load_storm(self, button):

        #Load storm
        self.storm = self.tpc_dataset.get_storm(self.storm_list.value)

        #Update list of dates
        dates = list(d.strftime("%Y/%m/%d-%H00Z") for d in self.storm.dict["date"])
        self.date_list.options=list(zip(dates, self.storm.dict["date"]))
        self.date_ind = 0
        self.date_list.value=self.storm.dict["date"][self.date_ind]

        #Returning
        return

    ### Method to load tropycal dataset on basin selection
    def load_tropycal(self, change):
        
        #Check if basin menu changed (and not None)
        if ((change["type"] == "change") and (change["name"] == "value") and (self.basin_list.value != None)):

            #Load dataset
            self.tpc_dataset = tracks.TrackDataset(self.basin_list.value, self.tpc_source)

        #Returning
        return

    ### Method to plot storm track (button call back)
    def plot_storm(self):

        #Grab extent of storm region
        self.storm_extent = [self.storm.dict["lon"][self.date_ind]-10, self.storm.dict["lon"][self.date_ind]+10, self.storm.dict["lat"][self.date_ind]-10, self.storm.dict["lat"][self.date_ind]+10]

        #Load relevant MERRA data
        #Retrieve username and password
        username = self.pwdDict['NASA Earth Data']['user']
        password = self.pwdDict['NASA Earth Data']['password']

        #Build url
        self.atmos_opendap_url = "https://goldsmr4.gesdisc.eosdis.nasa.gov/opendap/MERRA2/M2T1NXSLV.5.12.4/{}/{:02d}/MERRA2_400.tavg1_2d_slv_Nx.{}.nc4".format(self.date.year, self.date.month, self.date.strftime("%Y%m%d"))

        #Load MERRA
        try:
            session = setup_session(username, password, check_url=self.atmos_opendap_url)
            dataset = open_url(self.atmos_opendap_url, session=session)
        except: #Older data might use a number other than 400 in the url
            self.atmos_opendap_url = "https://goldsmr4.gesdisc.eosdis.nasa.gov/opendap/MERRA2/M2T1NXSLV.5.12.4/{}/{:02d}/MERRA2_300.tavg1_2d_slv_Nx.{}.nc4".format(self.date.year, self.date.month, self.date.strftime("%Y%m%d"))
            session = setup_session(username, password, check_url=self.atmos_opendap_url)
            dataset = open_url(self.atmos_opendap_url, session=session)

        #Pull the correct hour for the analysis
        hour = self.date.hour

        #First pull lat and lons and get subset
        self.lons = numpy.squeeze(dataset["lon"][:])
        self.lats = numpy.squeeze(dataset["lat"][:])
        self.get_subset()

        #Now pull the rest of the analysis data
        uwind = numpy.squeeze(dataset["U10M"][hour, self.yind1:self.yind2, self.xind1:self.xind2])
        vwind = numpy.squeeze(dataset["V10M"][hour, self.yind1:self.yind2, self.xind1:self.xind2])
        pres = numpy.squeeze(dataset["SLP"][hour, self.yind1:self.yind2, self.xind1:self.xind2])/100.0 #Pa -> hPa

        #Direct plot output to display
        with self.out_cp:

            #Turn of blocking behavior of pyplot.show
            plt.ioff()

            #Clear any previous output
            self.out_cp.clear_output()
            try:
                pp.close(fig)
            except:
                pass

            #Create figure and axis objects
            fig, ax = pp.subplots(subplot_kw={"projection":self.pcp})

            #Determine color according to storm intensity
            if (self.storm.dict["wmo_vmax"][self.date_ind] <= 33): #Storm wind is in knots
                c = "blue"
            elif (self.storm.dict["wmo_vmax"][self.date_ind] <= 63):
                c = "green"
            elif (self.storm.dict["wmo_vmax"][self.date_ind] <= 82):
                c = "yellow"
            elif (self.storm.dict["wmo_vmax"][self.date_ind] <= 95):
                c = "orange"
            elif (self.storm.dict["wmo_vmax"][self.date_ind] <= 112):
                c = "red"
            elif (self.storm.dict["wmo_vmax"][self.date_ind] <= 136):
                c = "purple"
            elif (self.storm.dict["wmo_vmax"][self.date_ind] > 136):
                c = "black"
            else: #In case of no wind reports
                c = "white"

            #Add fake lines for legend
            ax.plot(0, 0, "o", color="black")
            ax.plot(0, 0, "o", color="purple")
            ax.plot(0, 0, "o", color="red")
            ax.plot(0, 0, "o", color="orange")
            ax.plot(0, 0, "o", color="yellow")
            ax.plot(0, 0, "o", color="green")
            ax.plot(0, 0, "o", color="blue")

            #Plot MERRA analysis
            cont = ax.contourf(self.lons[self.xind1:self.xind2], self.lats[self.yind1:self.yind2], pres, transform=self.pcp)
            self.cb = pp.colorbar(cont)
            self.cb.set_label("Pressure (hPa)")
            ax.barbs(self.lons[self.xind1:self.xind2][::4], self.lats[self.yind1:self.yind2][::4], uwind[::4,::4], vwind[::4,::4], transform=self.pcp)            

            #Plot storm location (color-coded by intensity)
            ax.scatter(self.storm.dict["lon"][self.date_ind], self.storm.dict["lat"][self.date_ind], color=c, transform=self.pcp)

            #Make the plotlook like a map        
            #Set extent (Box around storm location with 10 degree padding
            ax.set_extent(self.storm_extent)

            #Coasts and countries
            ax.coastlines()
            ax.add_feature(self.states, edgecolor="black", linewidth=1)
            ax.add_feature(self.countries, edgecolor="black", linewidth=1)

            #Gridlines
            gridlines = ax.gridlines(crs=self.pcp, draw_labels=True, linestyle=":", color="black")
            gridlines.xlabels_top = False
            gridlines.ylabels_right = False

            #Map image
            ax.stock_img()

            ax.legend(["Cat 5", "Cat 4", "Cat 3", "Cat 2", "Cat 1", "TS", "TD"], loc="upper right")

            #Label the plot
            ax.set_title("Storm {} - {}".format(self.storm.dict["name"], self.date.strftime("%Y/%m/%d")), fontsize=14)

            #Display plot
            pp.show()

        #Returning
        return
