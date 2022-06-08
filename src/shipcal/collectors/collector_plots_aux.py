from shipcal.elements import Element
from shipcal.weather import Weather
from .collector import Collector

from pathlib import Path

from bokeh.io import output_notebook
from bokeh.models import ColumnDataSource,Range1d,LinearAxis, Range1d, DaysTicker,FactorRange
from bokeh.palettes import Spectral6
from bokeh.layouts import column,row
from bokeh.plotting import figure, show
from bokeh.palettes import Category20


 
sevilla_file = Path("C:/Users/migue/Desktop/PYTHON/SHIPcal/src/shipcal/weather/data/Sevilla.csv")
sevilla = Weather(sevilla_file, "1h")
collec = Collector(67, None, 0, 0, 0)
#collec.get_incidence_angle_v1(sevilla,50)

for i in range(1,68):
    collec.get_incidence_angle_v1(sevilla,i)
    
    
p1 = figure(x_axis_type="datetime", title="Comparacion consumo & demanda mensual",height=400,width=750,)
p1.grid.grid_line_alpha=1
p1.xaxis.axis_label = 'Date'
p1.yaxis.axis_label = 'vapor'
p1.line(boiler_eff_mes.index,boiler_eff_mes.consumo_gas, color='red', legend_label='Consumo gas')
p1.line(boiler_eff_mes.index,boiler_eff_mes.demanda_vapor, color='blue', legend_label='Demanda vapor')
p1.xgrid.grid_line_color = None

p2 = figure(x_axis_type="datetime", title="Eficiencia boiler %",height=400,width=750,y_range=[0,200])
p2.grid.grid_line_alpha=1
p2.xaxis.axis_label = 'Date'
p2.yaxis.axis_label = 'Boiler eff'
p2.line(boiler_eff_mes.index,boiler_eff_mes.boiler_eff, color='green', legend_label='Eff boiler')
p2.xgrid.grid_line_color = None

show(column(p1,p2))