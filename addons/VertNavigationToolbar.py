from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import tkinter as tk

class VerticalNavigationToolbar2Tk(NavigationToolbar2Tk):
    def __init__(self, canvas, window):
        super().__init__(canvas, window, pack_toolbar=True)

    #Override pan function so it would return to original autoscale after releasing the button
    def pan(self, *args):
        
        from enum import Enum
        
        class _Mode(str, Enum):
            NONE = ""
            PAN = "pan/zoom"
            ZOOM = "zoom rect"
            
            def __init__(self, NONE):
                self.N = NONE

            def __str__(self):
                return self.value

            @property
            def _navigate_mode(self):
                return self.name if self is not self.N else None
        
        """
        Toggle the pan/zoom tool.

        Pan with left button, zoom with right.
        """
        if self.mode == _Mode.PAN:
            self.mode = _Mode.NONE
            self.canvas.widgetlock.release(self)
            n = globals()['cur_animation_num'] - 3
            autoscale_x = bool(globals()[f'x{n}_autoscale'])
            autoscale_y = bool(globals()[f'y{n}_autoscale'])
            ax = globals()[f'ax{n}']
            ax.autoscale(enable = autoscale_x, axis = 'x')
            ax.autoscale(enable = autoscale_y, axis = 'y')
        else:
            self.mode = _Mode.PAN
            self.canvas.widgetlock(self)
        for a in self.canvas.figure.get_axes():
            a.set_navigate_mode(self.mode._navigate_mode)
        self.set_message(self.mode)

    #Override zoom function so it would return to original autoscale after releasing the button
    def zoom(self, *args):
        
        from enum import Enum
        
        class _Mode(str, Enum):
            NONE = ""
            PAN = "pan/zoom"
            ZOOM = "zoom rect"
            
            def __init__(self, NONE):
                self.N = NONE

            def __str__(self):
                return self.value

            @property
            def _navigate_mode(self):
                return self.name if self is not self.N else None
        
        """Toggle zoom to rect mode."""
        if self.mode == _Mode.ZOOM:
            self.mode = _Mode.NONE
            self.canvas.widgetlock.release(self)
            n = globals()['cur_animation_num'] - 3
            autoscale_x = bool(globals()[f'x{n}_autoscale'])
            autoscale_y = bool(globals()[f'y{n}_autoscale'])
            ax = globals()[f'ax{n}']
            ax.autoscale(enable = autoscale_x, axis = 'x')
            ax.autoscale(enable = autoscale_y, axis = 'y')
        else:
            self.mode = _Mode.ZOOM
            self.canvas.widgetlock(self)
        for a in self.canvas.figure.get_axes():
            a.set_navigate_mode(self.mode._navigate_mode)
        self.set_message(self.mode)

    def drag_pan(self, event):
        """Callback for dragging in pan/zoom mode."""
        for ax in self._pan_info.axes:
            # Using the recorded button at the press is safer than the current
            # button, as multiple buttons can get pressed during motion.
            ax.drag_pan(self._pan_info.button, event.key, event.x, event.y)
            ax.autoscale(enable = False, axis = 'x')
            ax.autoscale(enable = False, axis = 'y')
        self.canvas.draw_idle()
        
    def drag_zoom(self, event):
        """Callback for dragging in zoom mode."""
        start_xy = self._zoom_info.start_xy
        self._zoom_info.axes[0].autoscale(enable = False, axis = 'x')
        self._zoom_info.axes[0].autoscale(enable = False, axis = 'y')
        (x1, y1), (x2, y2) = np.clip(
            [start_xy, [event.x, event.y]], self._zoom_info.axes[0].bbox.min, self._zoom_info.axes[0].bbox.max)
        key = event.key
        # Force the key on colorbars to extend the short-axis bbox
        if self._zoom_info.cbar == "horizontal":
            key = "x"
        elif self._zoom_info.cbar == "vertical":
            key = "y"
        if key == "x":
            y1, y2 = self._zoom_info.axes[0].bbox.intervaly
        elif key == "y":
            x1, x2 = self._zoom_info.axes[0].bbox.intervalx

        self.draw_rubberband(event, x1, y1, x2, y2)

    # override _Button() to re-pack the toolbar button in vertical direction
    def _Button(self, text, image_file, toggle, command):
        b = super()._Button(text, image_file, toggle, command)
        b.pack(side=tk.TOP)  # re-pack button in vertical direction
        return b

    # override _Spacer() to create vertical separator
    def _Spacer(self):
        s = tk.Frame(self, width=26, relief=tk.RIDGE, bg="White", padx=2)
        s.pack(side=tk.TOP, pady = 5, fill="both", expand=True)  # pack in vertical direction
        return s

    # disable showing mouse position in toolbar
    def set_message(self, s):
        pass