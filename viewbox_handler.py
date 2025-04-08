import pyqtgraph as pg
import numpy as np
import time
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal, QEvent, QTimer

DEFAULT_Y_PADDING_RATIO = 0.1
GRAPH_UPDATE_TIMEOUT = 0.05  # Seconds between graph updates when X-axis range is changed
GRAPH_TIMER_UPDATE_TIMEOUT = int((GRAPH_UPDATE_TIMEOUT + 0.1) * 1000)  # Timer to render one last time after plot bounds change

class GeneralPlotWidget:
    """
    Generates a plot widget that has some logic to render only the data on screen for efficiency with large datasets.

    TODO: Autoscale functionality is not implemented. Default autoscale doesn't work great, but can turn that functionality back on if desired
    TODO: When dataset gets to be greater than 1,000,000-2,000,000 samples, plot chugs when bounds are fully zoomed out. Implement a "downsampling"-esque feature to only show reasonable number of datapoints
    """

    def __init__(self):
        # Reference to plot data. Set with the "set_data" method
        self.x_data = None
        self.y_data = None
        self.y_padding = DEFAULT_Y_PADDING_RATIO

        self.widget_container, self.plot_widget = self.setup_widget_container()

        # Keep reference of last update time, and keep timer for final update of graph after scrolling, zooming, etc.
        self.graph_update_time = time.time()
        self.graph_update_timer = QTimer()
        self.graph_update_timer.setSingleShot(True)
        self.graph_update_timer.timeout.connect(self.update_graph_based_on_bounds)

        # Plot initial data
        self.curve = self.plot_widget.plot([], pen='b')

    def set_data(self, x_data, y_data):
        # Call this method to enable autorange functionality
        self.x_data = x_data
        self.y_data = y_data

        self.curve.setData(self.x_data, self.y_data)

        # Disable autorange by default. Only allow autoranging from buttons
        self.plot_widget.getPlotItem().disableAutoRange()
        self.plot_widget.getPlotItem().getViewBox().setDefaultPadding(0)
        self.update_graph_based_on_bounds()

    def setup_widget_container(self):
        container = QWidget()
        vbox_layout = QVBoxLayout(container)

        # First row is the plot widget
        plot_widget = pg.PlotWidget()
        plot_widget.getPlotItem().hideButtons()  # Hide built in autoscale button
        vbox_layout.addWidget(plot_widget)
        plot_widget.getPlotItem().sigXRangeChanged.connect(self.update_plot_data)

        # Second row is the HBox containing the autorange buttons
        hbox_layout = QHBoxLayout()
        x_scale_button = QPushButton("Autoscale X-axis")
        y_scale_button = QPushButton("Autoscale Y-axis")

        # TODO: Connect autorange buttons

        hbox_layout.addWidget(x_scale_button)
        hbox_layout.addWidget(y_scale_button)

        # Add widget/layout to container widget
        vbox_layout.addWidget(plot_widget)
        vbox_layout.addLayout(hbox_layout)

        return container, plot_widget

    def update_plot_data(self):
        # Check if we can update the plot yet
        now = time.time()
        if now < self.graph_update_time + GRAPH_UPDATE_TIMEOUT:
            # Too soon, ignoring event
            return

        # Starts/restarts graph update timer for final update
        self.graph_update_timer.start(GRAPH_TIMER_UPDATE_TIMEOUT)

        # Update graph update time
        self.graph_update_time = now
        self.update_graph_based_on_bounds()

    def update_graph_based_on_bounds(self):
        # Filter data based on new X-axis range
        x_min, x_max = self.plot_widget.getViewBox().viewRange()[0]

        mask = (self.x_data >= x_min) & (self.x_data <= x_max)
        filtered_y = self.y_data[mask]
        self.curve.setData(self.x_data[mask], filtered_y)

        if len(filtered_y) > 0:
            y_min = float(np.min(filtered_y))
            y_max = float(np.max(filtered_y))

            self.plot_widget.setYRange(y_min - self.y_padding, y_max + self.y_padding)
