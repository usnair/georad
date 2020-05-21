%matplotlib inline
%config InlineBackend.close_figures=False #Don't display plot at end of running code

db = RADashBoard()
db.title = 'Air Pollution Research & Applications Dashboard'
db.addObject(QueryOpenAq,'OpenAQ Query','Tool for querying the OpenAQ database. This is a lot of fun  for all.')
db.addObject(PlotOpenAq,'Plot OpenAQ','Tool for plotting time series of OpenAQ stations')
db.addObject(MerraAero,'Plot Merra','Tool for plotting Merra Aerosol Spatial Plots')
db.addObject(TCPath, "Plot TC Track", "Tool for plotting a tropical cyclone track")
db.addObject(TCMERRA, "Plot TC with MERRA", "Tool for plotting TC location on top of MERRA surface analysis")
db.displayCP()
