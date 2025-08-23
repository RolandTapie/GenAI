from src.tools.weather.weather import *

func_name = "get_weather"
Latitude=48.866667
Longitude=2.333333
argss=(Latitude,Longitude)


def use_tool(func_name, args):
    func = globals()[func_name]
    return(func(*args))

print(use_tool(func_name,argss))