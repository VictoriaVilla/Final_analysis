import folium
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import tempfile
from utilities import utilities as ut
import matplotlib.pyplot as plt
import io
from base64 import b64encode
from reporting import textfilecreator as tfc
from visualization import visualization as v
from folium.plugins import HeatMap
import pandas as pd


def plot_long_stay_points(data, title, file):
    color = 'red'
    m = folium.Map(location=[-38.051268, 145.286780], zoom_start=16)
    i = 1
    for lat, lon in zip(data['Latitude'], data['Longitude']):
        folium.CircleMarker(location=(lat, lon), radius=3,
                            color=color).add_child(folium.Popup("Car id "+str(i))).add_to(m)
        folium.Marker(location=(lat+0.0003, lon), icon=folium.DivIcon(
            html=f"""<div style="color: red; font-size: 18px">{i}</div>""")).add_to(m)
        # map limits of casey

        i = i+1
    v.add_polygon(m, ut.MAP_LIMITS_FLOAT)
    # another way instead of creating html output is to use Qt5
    legend_html = f'''
        <div style="position: fixed;
            bottom: 50px; left: 50px; width: 300px; height: auto;
            border:2px solid grey; z-index:9999; font-size:14px;
            background-color:white; opacity: 0.8;">
            <h1>{title} - Map</h1>
        '''
    i = 1
    for hours in data['duration_hours']:
        legend_html += f'''
            <p style="margin: 5px;">Car id {i}: parked for {round(hours,2)} hours </p>
        '''
        i = i+1

    legend_html += '''
        </div>
        '''
    m.get_root().html.add_child(folium.Element(legend_html))

    temp_html = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
    m.save(temp_html.name)
    tfc.save_map_to_pdf(temp_html.name, file)
    return temp_html.name, (m, title)


def plot_Heatmap(data, title, file):
    print(data['Latitude'], data['Longitude'])
    m = folium.Map(location=[-38.051268, 145.286780], zoom_start=16)
    m1 = m
    HeatMap(list(zip(data['Latitude'], data['Longitude']))).add_to(m)
    fg = folium.FeatureGroup(name="HeatMap")
    HeatMap(list(zip(data['Latitude'], data['Longitude']))).add_to(fg)
    v.add_polygon(m, ut.MAP_LIMITS_FLOAT)
    v.add_polygon(m1, ut.MAP_LIMITS_FLOAT)

    # another way instead of creating html output is to use Qt5
    legend_html = f'''
        <div style="position: fixed;
            bottom: 50px; left: 50px; width: 300px; height: auto;
            border:2px solid grey; z-index:9999; font-size:14px;
            background-color:white; opacity: 0.8;">
            <h1>{title} - Heatmap</h1>
        </div>
        '''
    m.get_root().html.add_child(folium.Element(legend_html))

    temp_html = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
    m.save(temp_html.name)
    tfc.save_map_to_pdf(temp_html.name, file)
    return temp_html.name, (m, title, fg)


def plot_Heatmaps(data, periods, title, file):
    temps = []
    for d, p in zip(data, periods):
        print(d)
        lat, lon = d
        lat_s = pd.Series(lat)
        lon_s = pd.Series(lon)
        print(lat_s, lon_s)
        m = folium.Map(location=[-38.051268, 145.286780], zoom_start=16)
        HeatMap(list(zip(lat_s, lon_s))).add_to(m)
        v.add_polygon(m, ut.MAP_LIMITS_FLOAT)

        # another way instead of creating html output is to use Qt5
        legend_html = f'''
            <div style="position: fixed;
                bottom: 50px; left: 50px; width: 300px; height: auto;
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color:white; opacity: 0.8;">
                <h1>{title} - {p} - Heatmap</h1>
            </div>
            '''
        m.get_root().html.add_child(folium.Element(legend_html))

        temp_html = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        m.save(temp_html.name)
        tfc.save_map_to_pdf(temp_html.name, file)
        temps.append(temp_html.name)
    print(len(temps))
    print(temps)
    return temps


class MainWindow(QWidget):
    def __init__(self, html):
        super().__init__()
        self.setGeometry(100, 100, 1200, 800)
        layout = QVBoxLayout()
        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl.fromLocalFile(html))
        layout.addWidget(self.web_view)
        self.setLayout(layout)
