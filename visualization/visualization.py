import folium
import random
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import tempfile
from utilities import utilities as ut
import matplotlib.pyplot as plt
import io
from base64 import b64encode
from reporting import textfilecreator as tfc


def generate_random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))


def add_polygon(map_obj, polygon, color='black'):
    folium.Polygon(locations=polygon, color=color,
                   weight=2, fill=False).add_to(map_obj)


def plot_paths(data, periods, title, file):
    temps = []
    foliums = []
    # print(data)
    for d, p in zip(data, periods):
        colors = [generate_random_color() for _ in range(len(d))]
        total_rows = len(d)

        m = folium.Map(location=[-38.051268, 145.286780], zoom_start=16)

        # map limits of casey
        add_polygon(m, ut.MAP_LIMITS_FLOAT)

        for idx, (path, number) in enumerate(d):
            color = colors[idx]
            folium.PolyLine([(lat, lon) for lon, lat in path], color=color,
                            weight=5, opacity=0.7, tooltip=f'Cluster {idx}').add_to(m)

        # another way instead of creating html output is to use Qt5
        legend_html = f'''
        <div style="position: fixed;
            bottom: 50px; left: 50px; width: 300px; height: auto;
            border:2px solid grey; z-index:9999; font-size:14px;
            background-color:white; opacity: 0.8;">
            <h4>{title} - {p} Map</h4>
            <p>Rows Read: {total_rows}</p>
        '''

        for idx, (path, number) in enumerate(d):
            legend_html += f'''
            <p style="margin: 5px;"><svg width="20" height="20">
                    <line x1="0" y1="10" x2="20" y2="10" style="stroke:{colors[idx]};stroke-width:5" />
                </svg> Path {idx+1}: {number} repetitions </p>
        '''

        legend_html += '''
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        foliums.append((m, f"{title} - {p}"))
        temp_html = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        m.save(temp_html.name)
        tfc.save_map_to_pdf(temp_html.name, file)
        temps.append(temp_html.name)
    return temps, foliums


class AnotherWindow(QWidget):
    def __init__(self, html):
        super().__init__()
        # print(html)
        self.setGeometry(100, 100, 1200, 800)
        layout = QVBoxLayout()

        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl.fromLocalFile(html))
        layout.addWidget(self.web_view)
        self.setLayout(layout)


class MapWindow(QMainWindow):
    def __init__(self, html, period, title):
        super().__init__()
        # print(html, period)
        self.window1 = AnotherWindow(html[0])
        self.window2 = AnotherWindow(html[1])
        self.window3 = AnotherWindow(html[2])
        self.window4 = AnotherWindow(html[3])
        self.window5 = AnotherWindow(html[4])
        self.window6 = AnotherWindow(html[5])

        l = QVBoxLayout()
        button1 = QPushButton(period[0])
        button1.clicked.connect(self.toggle_window1)
        l.addWidget(button1)

        button2 = QPushButton(period[1])
        button2.clicked.connect(self.toggle_window2)
        l.addWidget(button2)

        button3 = QPushButton(period[2])
        button3.clicked.connect(self.toggle_window3)
        l.addWidget(button3)

        button4 = QPushButton(period[3])
        button4.clicked.connect(self.toggle_window4)
        l.addWidget(button4)

        button5 = QPushButton(period[4])
        button5.clicked.connect(self.toggle_window5)
        l.addWidget(button5)

        button5 = QPushButton(period[5])
        button5.clicked.connect(self.toggle_window6)
        l.addWidget(button5)

        self.setWindowTitle(title)

        w = QWidget()
        w.setLayout(l)
        self.setCentralWidget(w)

    def toggle_window1(self, checked):
        if self.window1.isVisible():
            self.window1.hide()

        else:
            self.window1.show()

    def toggle_window2(self, checked):
        if self.window2.isVisible():
            self.window2.hide()

        else:
            self.window2.show()

    def toggle_window3(self, checked):
        if self.window3.isVisible():
            self.window3.hide()

        else:
            self.window3.show()

    def toggle_window4(self, checked):
        if self.window4.isVisible():
            self.window4.hide()

        else:
            self.window4.show()

    def toggle_window5(self, checked):
        if self.window5.isVisible():
            self.window5.hide()

        else:
            self.window5.show()

    def toggle_window6(self, checked):
        if self.window6.isVisible():
            self.window6.hide()

        else:
            self.window6.show()


# Function to create bar graphs and return them as an HTML string
def create_bar_graphs(values, title, file):

    # Labels for each bar
    labels = ['Dropoff', 'Pickup', 'Weekday',
              'Weekend', 'School holiday', 'Public holiday']

    # Bar graph colors
    # Dark blue, orange, grey, medium green
    colors = ['#003f5c', '#ffa600', '#a3a3a3', '#2f4b7c']

    # Find the maximum percentage in each graph
    max_value_1 = max(values)
    min_value_1 = min(values)

    # Determine the upper limit for the y-axis (20 more than the max value)
    maxylim_1 = 1.5 * max_value_1
    if (min_value_1 <= 0):
        minylim_1 = 1.5 * min_value_1
    else:
        minylim_1 = min_value_1/2

    # Create the first bar graph
    plt.figure(figsize=(10, 6))
    plt.subplot(1, 1, 1)  # 2 rows, 1 column, first subplot
    plt.bar(labels, values, color=colors)
    plt.ylim(minylim_1, maxylim_1)  # Set y-axis limit
    plt.title(title + ' between different periods')
    plt.xlabel('period')
    plt.ylabel(title + ' per hour')
    for i, value in enumerate(values):
        # Position the label above the bar
        plt.text(i, value + 0.05, f'{value:.1f}', ha='center')

    # Save the plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    tfc.save_figure_to_pdf(plt, file)
    plt.close()

    # Encode the image in base64
    encoded_image = b64encode(buf.getvalue()).decode('utf-8')

    # Create an HTML page to display the image
    html = f"""
    <html>
    <body>
        <h1>Bar Graphs</h1>
        <img src="data:image/png;base64,{encoded_image}" alt="Bar Graphs">
    </body>
    </html>
    """

    return html, encoded_image

# PyQt5 Application


class BarWindow(QMainWindow):
    def __init__(self, html, title):
        super().__init__()

        # Set up the main window
        self.setWindowTitle(title)

        # Create a central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QVBoxLayout(central_widget)

        # Create a QWebEngineView to display the HTML
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        # Generate the HTML and load it into the QWebEngineView
        html_content = html
        self.web_view.setHtml(html_content, QUrl(''))
        self.setGeometry(100, 100, 1050, 700)
