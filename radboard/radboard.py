import functools
from IPython.display import display
from ipywidgets import HBox, VBox, Button,Layout, HTML,Output,GridspecLayout,Dropdown,GridBox,Textarea,Text,Password

sys.path.append("../oaqtools")
from oaqtools import QueryOpenAq, PlotOpenAq
sys.path.append("../nmtools")
from nmtools import MERRA_WindRose,MerraAQSpatial,MerraAQTseries

class RADashBoard:

  def __init__(self):
    self.out_cp = Output()
    display(self.out_cp)
    self.objDict = {}
    self.objinfoDict = {}
    self.title = 'Research & Applications Dashboard'
    self.nx   = 1
    self.ny   = 1
    self.panelWidth  = [250,500]
    self.panelHeight = [250,500]
    #self.ob  =   OpenAQGui().createCP()
    self.ob  =  QueryOpenAq().getCP()
    self.state = 0
    self.gridGap = 15
    self.gridPad = 15
    self.panelBorder = 3
    self.dbBorder =5
    self.cpView  = 0
    self.pwdDict= {}
    self.createMainCP = True
    self.accList =['NASA Earth Data']
  
  def addAccount(accname):
    self.accList.append(accname)

  def addObject(self,obj,short_name, desc):
    self.objDict[short_name] = obj
    self.objinfoDict[short_name] = desc

  def displayCP(self):
    
    self.rowSW = Dropdown(options=[1,2,3,4],value=1,description='Rows:',
                          disabled=False,layout={'width':'150px'}
                         )
    self.colSW = Dropdown(options=[1,2,3,4],value=1,description='Columns:',
                            disabled=False,layout={'width':'150px'}
                          )
    self.row  = Dropdown(options=[1,2,3,4],value=1,
                         description='# of row:',disabled=True)
    self.col  = Dropdown(options=[1,2,3,4],value=1,
                         description='# of col:',disabled=True)
    self.obj  = Dropdown(options=[],value=None,
                         description='Object:',disabled=True)
    self.conDB = Button(description='Configure Dashboard',disabled=False,
                          layout={'width':'150px','border':'3px outset'}
                         )
    self.topLabel = HTML(disabled=False,layout={'width': 'auto'})
      
    self.topLabel.value = ( '<div style="background-color: #C0C0C0 ;'+ 
                            'padding: 1em 0em 0em 0em;border-bottom-style:groove;border-width:4px">'+
                           '<b><font size="4"><center><h2>'+self.title+'</h2></center></font></b></div>')
    self.rule = HTML(disabled=True,layout=Layout(width='auto',padding='0px'))
      
    self.rule.value = ( '<div >'+'<hr></div>')
    self.cpMain   = VBox([ 
                          HBox([self.topLabel],layout={'justify_content':'center','flex_flow':'column'}),
                          HBox([
                                HBox([self.rowSW],layout={'justify_content':'flex-start'}),
                                HBox([self.colSW],layout={'justify_content':'flex-end'})
                               ],layout={'padding':'15px'}
                              ),
                          HBox([self.conDB],layout={'justify_content':'center','padding':'15px'})
                               ],layout={'border':'3px groove','width': '400px'}
                        )
    self.rowSW.observe(self.rowSWCB,names='value')
    self.colSW.observe(self.colSWCB,names='value')
    self.conDB.on_click(self.configDBCB)
    with self.out_cp:
      display(self.cpMain)

  def rowSWCB(self,change):
    if change['type'] == 'change':

      # set the city to the new user selected value given 
      # by the "value" attribute in the city selection widget.

      self.ny    = int(self.rowSW.value)
      

  def colSWCB(self,change):
    if change['type'] == 'change':

      # set the city to the new user selected value given 
      # by the "value" attribute in the city selection widget.

      self.nx    = int(self.colSW.value)
      

  def rowSWCB(self,change):
    if change['type'] == 'change':

      # set the city to the new user selected value given 
      # by the "value" attribute in the city selection widget.

      self.ny    = int(self.rowSW.value)
      

  def colSWCB(self,change):
    if change['type'] == 'change':

      # set the city to the new user selected value given 
      # by the "value" attribute in the city selection widget.

      self.nx    = int(self.colSW.value)
      


  def configDBCB(self,b):

    self.out_cp.clear_output()

    self.objList = [*(self.objDict)]

    pw = self.panelWidth[0]

    lw = (pw*self.nx)+((self.nx-1)*self.gridGap)+(self.gridPad*2)

    gw = lw + (2*self.dbBorder)

    lw1 = lw-2

    self.topLabel.layout = {'width': str(lw-2)+'px'}

    gap = str(self.gridGap)+'px'

    pd = str(self.gridPad)

    pad = pd+'px '+pd+'px '+pd+'px '+pd+'px'

    self.gridDB1 = GridspecLayout(self.ny,self.nx,
                                  layout={
                                          'scroll':'False',
                                          'grid_gap':gap,
                                          'padding':pad
                                          }
                                  )
    self.objSW = [ ([0] * self.nx) for y in range(self.ny) ]
    self.objinfoTW = [ ([0] * self.nx) for y in range(self.ny) ]
    self.pwTW = [ ([0] * self.nx) for y in range(self.ny) ]
    self.phTW = [ ([0] * self.nx) for y in range(self.ny) ]

    txw = str(int(0.96*float(self.panelWidth[0])))+'px'
    pw = str(self.panelWidth[0])+'px'
    ph = str(self.panelHeight[0])+'px'
    pb = str(self.panelBorder)+'px groove'

    for i in range(0,self.ny):
      for j in range(0,self.nx):
        desc = 'Panel('+str(i+1)+','+str(j+1)+'):'
        self.objSW[i][j]  = Dropdown(options=self.objList,value=self.objList[0],
                                    description=desc,disabled=False,
                                    layout={'width':txw})
        objinfo = self.objinfoDict[self.objList[0]]
        self.objinfoTW[i][j] = Textarea(value=objinfo,placeholder='',description='',
                                    disabled=False,layout={'width':txw,'border':'2px inset'})
        self.pwTW[i][j] = Text(value=str(self.panelWidth[1]),placeholder='',description='Panel Width:',
                                    disabled=False,layout={'width':txw,'border':'2px inset'})
        self.phTW[i][j] = Text(value=str(self.panelHeight[1]),placeholder='',description='Panel Height',
                                    disabled=False,layout={'width':txw,'border':'2px inset'})
        
        self.gridDB1[i,j] = VBox([self.objSW[i][j],self.pwTW[i][j],self.phTW[i][j],self.objinfoTW[i][j]],layout={'border':'2px solid black'})

        self.objSW[i][j].observe(functools.partial(self.objSWCB, irow_=i, jcol_=j),names='value')
        self.phTW[i][j].observe(functools.partial(self.phTWCB, irow_=i, jcol_=j),names='value')

    gp  = str(self.gridPad)+'px'
    dbb = str(self.dbBorder)+'px groove'
    dbw = str(gw)+'px'

    self.pmLabel = HTML(disabled=False,layout={'width': 'auto','flex_flow':'column'})
    
    self.pmLabel.value = ( '<div style="background-color: #C0C0C0 ;'+ 
                           'border-top-style:groove;border-width:3px'
                           'padding: 1em 0em 0em 0em;border-bottom-style:groove;border-width:3px">'+
                           '<b><font size="4"><center><h3>Password Manager</h3></center></font></b></div>')
    self.accSW = Dropdown(options=self.accList,value=self.accList[0],
                                    description='Account:',disabled=False,
                                    layout={'width':txw})
    self.usrTW = Text(value='',placeholder='',description='Username:',disabled=False,
                                    layout={'width':txw})
    
    self.pwdPW = Password(value='',placeholder='',description='Password:',disabled=False,
                                    layout={'width':txw})
    self.addPWD = Button(description='Add Account',disabled=False,
                        layout={'width':'150px','border':'3px outset'}
                        )
    self.createDB = Button(description='Create Dashboard',disabled=False,
                        layout={'width':'150px','border':'3px outset'}
                        )
    self.addPWD.on_click(self.addPWDCB)
    self.createDB.on_click(self.createDBCB)
    self.reconfigDB = Button(description='Reconfigure Dashboard',disabled=False,
                        layout={'width':'180px','border':'3px outset'}
                        )
    self.reconfigDB.on_click(self.reconfigDBCB)
    
    self.cp   = VBox([ 
                       HBox([self.topLabel],layout={'flex_flow':'column'}),
                       HBox([self.gridDB1]),
                       HBox([self.pmLabel],layout={'flex_flow':'column'}),
                       VBox([self.accSW,self.usrTW,self.pwdPW]),
                       HBox([self.addPWD],layout={'justify_content':'center'}),
                       self.rule,
                       HBox([self.reconfigDB,self.createDB],layout={'justify_content':'center','padding':gp})
                     ],layout={'border':dbb,'width':dbw}
                    )
    with self.out_cp:
      self.out_cp.clear_output()
      display(self.cp)
  def objSWCB(self,change,irow_,jcol_):
    self.objinfoTW[irow_][jcol_].value =self.objinfoDict[self.objSW[irow_][jcol_].value]

  def phTWCB(self,change,irow_,jcol_):
    self.objinfoTW[irow_][jcol_].value =('Hint: Set the same height of all the panels in'+ 
                                         ' a row for optimal panel layout')
    

  def addPWDCB(self,b):
    self.pwdDict[self.accSW.value]={'user':self.usrTW.value,'password':self.pwdPW.value}
    

  def createDBCB(self,b):
    self.out_cp.clear_output()
    wd = [0]*self.ny
    for i in range(self.ny):
      for j in range(self.nx):
        wd[i] += int(self.pwTW[i][j].value)

    tpw = max(wd)
    lw = tpw+((self.nx-1)*self.gridGap)+(self.gridPad*2)
    self.topLabel.layout = {'width': 'auto'}
    gw = lw + (2*self.dbBorder)
    gap = str(self.gridGap)+'px'
    pd = str(self.gridPad)
    pad = pd+'px '+pd+'px '+pd+'px '+pd+'px'
    self.gridDB2  = GridspecLayout(self.ny,self.nx,
                                  layout={
                                          'scroll':'True',
                                          'grid_gap':gap,
                                          'padding':pad
                                          }
                                  )
    ph = str(self.panelHeight[1])+'px'
    pb = str(self.panelBorder)+'px groove'

    for i in range(0,self.ny):
      for j in range(0,self.nx):
        pw = self.pwTW[i][j].value+'px'
        ph = self.phTW[i][j].value+'px'
        obj = self.objDict[self.objSW[i][j].value]()
        obj.pwdDict = self.pwdDict
        obj.spacer.layout={'width':pw}
        obj = obj.getCP()
        obj.layout={'overflow_x':'visible','overflow_y':'visible'}
        self.gridDB2[i,j] = HBox([obj],layout={'height': ph,'width': pw,'border':pb})
    gp  = str(self.gridPad)+'px'
    dbb = str(self.dbBorder)+'px groove'
    dbw = str(gw)+'px'

    self.cp   = VBox([ VBox([self.topLabel,self.gridDB2],layout={'flex_flow':'column'}),
                       HBox([self.reconfigDB],layout={'justify_content':'center','padding':gp})
                     ],layout={'border':dbb,'width':dbw}
                    )
    with self.out_cp:
      self.out_cp.clear_output()
      display(self.cp)
  def reconfigDBCB(self,b):
    with self.out_cp:
      self.out_cp.clear_output()
      self.topLabel.layout={'flex_flow':'column'}
      display(self.cpMain)
	  
class AQDashBoard:
  def __init__(self):
    self.DashBoard = RADashBoard()
    self.DashBoard.title ='Air Pollution Research & Applications Dashboard'
    self.DashBoard.addObject(QueryOpenAq,'OpenAQ Query','Query OpenAQ database')
    self.DashBoard.addObject(PlotOpenAq,'OpenAQ Query','Plot OpenAQ observations')
    self.DashBoard.addObject(MERRA_WindRose,'MERRA_WindRose','Plot wind reose for a location using MERRA observations')
	self.DashBoard.addObject(MerraAQSpatial,'Merra Spatial','Tool for plotting Merra Aerosol Spatial Maps')
    self.DashBoard.addObject(MerraAQTseries,'Merra Series','Tool for plotting Merra Aerosol Time Series')