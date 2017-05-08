# -*- coding: utf-8 -*-

#----------------------------------------------------------------------#
__author__ = "Katarinza"
__copyright__ = "Copyright (C) 2014, Katarinza"
__email__ = "katarina.zadraznik@gmail.com"
__version__ = "1.0"
########################################################################

#----------------------------------------------------------------------#
import pygtk
import threading
import time
import gtk, gobject, glib
import sys
import pango
import paint
import paint_style
########################################################################

# Global Parameters ---------------------------------------------------#
WIN_WIDTH = 750
WIN_HEIGHT = 550
########################################################################

# Interface For KatarinzArt -------------------------------------------#
class Interface(gtk.Window):
    """GTK GUI for KatarinzArt."""

    #------------------------------------------------------------------#
    def __init__(self):
        """Initialize the main window."""

        # Name, size, position, ... -----------------------------------#
        super(Interface, self).__init__()
        self.set_title("KatarinzArt")
        self.set_size_request(WIN_WIDTH, WIN_HEIGHT)
        self.set_border_width(5) # inner border
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#fff5ee"))
        self.set_icon_from_file("icones/katarinza.jpg")
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_resizable(False)
        ################################################################

        # Create Menu Bar ---------------------------------------------#
        self.create_menubar()
        ################################################################

        # Create title ------------------------------------------------#
        self.label_title = gtk.Label()
        self.label_title.set_no_show_all(True)
        self.label_title.set_alignment(xalign=0.5, yalign=0.5)
        self.label_title.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color("#9400d3"))
        self.label_title.set_markup("<big>{0}</big>".format(DEFAULT["label"]))
        ################################################################

        # Create new notebook -----------------------------------------#
        self.notebook = gtk.Notebook()
        self.notebook.set_show_tabs(False)
        # Create Home Page --------------#
        self.create_home_page()
        # Create Image Page -------------#
        self.create_image_page()
        # Create Paint Settings Page ----#
        self.create_paint_settings_page()
        ################################################################

        # Buttons -----------------------------------------------------#
        # Paint / Zoom button -----------#
        self.button_paint = self.create_button("icones/paint.jpg", "Paint")
        self.button_paint.connect("clicked", self.artist)
        self.button_paint.set_no_show_all(True)

        self.button_zoom = self.create_button("icones/zoom.jpg", "Zoom")
        self.button_zoom.connect("clicked", self.zoom)
        self.button_zoom.set_no_show_all(True)

        # Settings / Image button -------#
        self.button_settings = self.create_button("icones/paint.jpg", "Settings")
        self.button_settings.connect("clicked", self.settings)
        self.button_settings.set_no_show_all(True)

        self.button_image = self.create_button("icones/zoom.jpg", "Image")
        self.button_image.connect("clicked", self.show_image_page)
        self.button_image.set_no_show_all(True)
        ################################################################

        # Add widgets and other stuff ---------------------------------#
        self.table = gtk.Table(3, 3)
        self.table.set_row_spacings(3)
        # First row is menubar.
        self.table.attach(self.mb, 0, 3, 0, 1, gtk.FILL, gtk.SHRINK)
        # Second row are buttons and title.
        self.table.attach(self.button_paint, 0, 1, 1, 2, gtk.SHRINK, gtk.SHRINK)
        self.table.attach(self.button_zoom, 0, 1, 1, 2, gtk.SHRINK, gtk.SHRINK)
        self.table.attach(self.label_title, 1, 2, 1, 2, gtk.FILL|gtk.EXPAND, gtk.SHRINK)
        self.table.attach(self.button_settings, 2, 3, 1, 2, gtk.SHRINK, gtk.SHRINK)
        self.table.attach(self.button_image, 2, 3, 1, 2, gtk.SHRINK, gtk.SHRINK)
        # Third row is notebook.
        self.table.attach(self.notebook, 0, 3, 2, 3)
        self.add(self.table)
        ################################################################

        # Initial settings and window.
        self.notebook.set_current_page(0) # home page
        self.show_all()
        self.mb.hide() # hide menubar for home page
        self.connect("destroy", gtk.main_quit)
    ####################################################################
    def paint_play(self, widget):
        pass
    # Menubar widget --------------------------------------------------#
    def create_menubar(self):
        """Create menubar widget with all required tabs and functions.
        """
        self.mb = gtk.MenuBar()
        # File Menu ---------------------------------------------------#
        filemenu = gtk.Menu()
        filem = gtk.MenuItem("File")
        filem.set_submenu(filemenu)
        self.mb.append(filem)
        # Load image.
        load = gtk.MenuItem("Load Image")
        filemenu.append(load)
        load.connect("activate", self.browse_for_image)
        # Save image.
        save = gtk.MenuItem("Save Image")
        filemenu.append(save)
        # Exit from program.
        exit = gtk.MenuItem("Exit")
        exit.connect("activate", self.close_app)
        filemenu.append(exit)
        # Style Menu --------------------------------------------------#
        stylemenu = gtk.Menu()
        stylem = gtk.MenuItem("Choose Style")
        stylem.set_submenu(stylemenu)
        self.mb.append(stylem)
        # Submenu for painting. ---------#
        paintmenu = gtk.Menu()
        paintm = gtk.MenuItem("Painting Styles")
        paintm.set_submenu(paintmenu)
        stylemenu.append(paintm)
        ## Submenu for predesigned.
        prepaintmenu = gtk.Menu()
        prepaintm = gtk.MenuItem("Predesigned Styles")
        prepaintm.set_submenu(prepaintmenu)
        paintmenu.append(prepaintm)
        # Impressionist.
        style_imp = gtk.MenuItem("Impressionist")
        prepaintmenu.append(style_imp)
        style_imp.connect("activate", self.set_impressionist)
        # Expressionist.
        style_exp = gtk.MenuItem("Expressionist")
        prepaintmenu.append(style_exp)
        style_exp.connect("activate", self.set_expressionist)
        # Colorist Wash.
        style_wash = gtk.MenuItem("Colorist Wash")
        prepaintmenu.append(style_wash)
        style_wash.connect("activate", self.set_colorist_wash)
        # Pointillist.
        style_point = gtk.MenuItem("Pointillist")
        prepaintmenu.append(style_point)
        style_point.connect("activate", self.set_pointillist)
        ## Choose parameters.
        costum_paint = gtk.MenuItem("Choose Parameters")
        paintmenu.append(costum_paint)
        costum_paint.connect("activate", self.set_painting_parameters)
        # Submenu for drawing. ----------#
        drawmenu = gtk.Menu()
        drawm = gtk.MenuItem("Drawing Styles")
        drawm.set_submenu(drawmenu)
        stylemenu.append(drawm)
        ## Submenu for predesigned.
        predrawmenu = gtk.Menu()
        predrawm = gtk.MenuItem("Predesigned Styles")
        predrawm.set_submenu(predrawmenu)
        drawmenu.append(predrawm)
        # Pencil sketch.
        style_pencil = gtk.MenuItem("Pencil Style")
        predrawmenu.append(style_pencil)
        ## Choose parameters.
        costum_draw = gtk.MenuItem("Choose Parameters")
        drawmenu.append(costum_draw)
        # Painter ;) --------------------------------------------------#
        strokemenu = gtk.Menu()
        strokem = gtk.MenuItem("Play ;)")
        strokem.set_submenu(strokemenu)
        self.mb.append(strokem)
        # Paint.
        paint = gtk.MenuItem("Paint")
        paint.connect("activate", self.paint_play)
        # Help Menu ---------------------------------------------------#
        helpmenu = gtk.Menu()
        helpm = gtk.MenuItem("Help")
        helpm.set_submenu(helpmenu)
        self.mb.append(helpm)
        # How to (help).
        help = gtk.MenuItem("Help KatarinzArt")
        helpmenu.append(help)
        # About (c).
        about = gtk.MenuItem("About KatarinzArt")
        helpmenu.append(about)
    ####################################################################

    # Create home page ------------------------------------------------#
    def create_home_page(self):
        """Create home page.
        """
        table = gtk.Table(4, 2)
        # Label -------------------------#
        label = gtk.Label()
        label.set_alignment(xalign=0.5, yalign=0.5)
        label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color("#9400d3"))
        label.set_markup("<big>{0}</big>".format("Choose the style"))
        table.attach(label, 0, 2, 0, 1, gtk.SHRINK, gtk.SHRINK)
        # Left upper image ------------#
        pixbuflu = gtk.gdk.pixbuf_new_from_file("homepage/original.jpg")
        pixbuflu = pixbuflu.scale_simple(pixbuflu.get_width()/4, pixbuflu.get_height()/4, gtk.gdk.INTERP_BILINEAR)
        imagelu = gtk.image_new_from_pixbuf(pixbuflu)
        buttonlu = gtk.Button()
        buttonlu.add(imagelu)
        buttonlu.connect("clicked", self.make_art)
        table.attach(buttonlu, 0, 1, 1, 2, gtk.EXPAND, gtk.EXPAND)
        # Right upper image -----------#
        pixbufru = gtk.gdk.pixbuf_new_from_file("homepage/original.jpg")
        pixbufru = pixbufru.scale_simple(pixbufru.get_width()/4, pixbufru.get_height()/4, gtk.gdk.INTERP_BILINEAR)
        imageru = gtk.image_new_from_pixbuf(pixbufru)
        buttonru = gtk.Button()
        buttonru.add(imageru)
        buttonru.connect("clicked", self.make_art)
        table.attach(buttonru, 1, 2, 1, 2, gtk.EXPAND, gtk.EXPAND)
        # Left lower image ------------#
        pixbufll = gtk.gdk.pixbuf_new_from_file("homepage/original.jpg")
        pixbufll = pixbufll.scale_simple(pixbufll.get_width()/4, pixbufll.get_height()/4, gtk.gdk.INTERP_BILINEAR)
        imagell = gtk.image_new_from_pixbuf(pixbufll)
        buttonll = gtk.Button()
        buttonll.add(imagell)
        buttonll.connect("clicked", self.make_art)
        table.attach(buttonll, 0, 1, 2, 3, gtk.EXPAND, gtk.EXPAND)
        # Right lower image -----------#
        pixbufrl = gtk.gdk.pixbuf_new_from_file("homepage/original.jpg")
        pixbufrl = pixbufrl.scale_simple(pixbufrl.get_width()/4, pixbufrl.get_height()/4, gtk.gdk.INTERP_BILINEAR)
        imagerl = gtk.image_new_from_pixbuf(pixbufrl)
        buttonrl = gtk.Button()
        buttonrl.add(imagerl)
        buttonrl.connect("clicked", self.make_art)
        table.attach(buttonrl, 1, 2, 2, 3, gtk.EXPAND, gtk.EXPAND)
        # Label -------------------------#
        label = gtk.Label("""KatarinzArt (c) 2013/2014""")
        label.set_alignment(xalign=0.5, yalign=0.5)
        table.attach(label, 0, 2, 3, 4, gtk.SHRINK, gtk.SHRINK)
        # Add page. ---------------------#
        self.notebook.append_page(table)
    ####################################################################

    # Notebook page for settings --------------------------------------#
    def create_paint_settings_page(self):
        # Container for whole settings --------------------------------#
        box = gtk.HBox(True)
        # Container for left column -----------------------------------#
        box_left = gtk.VBox()
        box.add(box_left)
        # Frame for color settings ------------------------------------#
        frame_color = gtk.Frame(label = "Color Settings")
        box_left.add(frame_color)
        frame_color.set_label_align(0, 0.5)
        frame_color.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        # Box for frame_color -----------#
        box_color = gtk.VBox()
        frame_color.add(box_color)
        box_color.set_border_width(10)
        ### HSV color settings
        label_hsv = gtk.Label("""Factors to randomly add jitter to HSV color components.""")
        box_color.add(label_hsv)
        label_hsv.set_line_wrap(True)
        label_hsv.set_alignment(0, 0.5)
        ## Container for HSV stuff
        box_hsv = gtk.HBox(spacing = 10)
        align_hsv = gtk.Alignment(0, 0, 0, 1)
        align_hsv.add(box_hsv)
        box_color.add(align_hsv)
        # H component
        label_h = gtk.Label("H:")
        box_hsv.add(label_h)
        self.paint_h = gtk.SpinButton(gtk.Adjustment(value=0, lower=0, upper=1, step_incr=0.01), digits=2)
        box_hsv.add(self.paint_h)
        # S component
        label_s = gtk.Label("S:")
        box_hsv.add(label_s)
        self.paint_s = gtk.SpinButton(gtk.Adjustment(value=0, lower=0, upper=1, step_incr=0.01), digits=2)
        box_hsv.add(self.paint_s)
        # V component
        label_v = gtk.Label("V:")
        box_hsv.add(label_v)
        self.paint_v = gtk.SpinButton(gtk.Adjustment(value=0, lower=0, upper=1, step_incr=0.01), digits=2)
        box_hsv.add(self.paint_v)
        separator = gtk.HSeparator()
        box_color.add(separator)
        ### RGB color components
        label_rgb = gtk.Label("""Factors to randomly  add jitter to RGB color components.""")
        box_color.add(label_rgb)
        label_rgb.set_line_wrap(True)
        label_rgb.set_alignment(0, 0.5)
        ## Container for RGB stuff
        box_rgb = gtk.HBox()
        align_rgb = gtk.Alignment(0, 0, 0, 1)
        align_rgb.add(box_rgb)
        box_color.add(align_rgb)
        # R component
        label_r = gtk.Label("R:")
        box_rgb.add(label_r)
        self.paint_r = gtk.SpinButton(gtk.Adjustment(value=0, lower=0, upper=1, step_incr=0.01), digits=2)
        box_rgb.add(self.paint_r)
        # G component
        label_g = gtk.Label("G:")
        box_rgb.add(label_g)
        self.paint_g = gtk.SpinButton(gtk.Adjustment(value=0, lower=0, upper=1, step_incr=0.01), digits=2)
        box_rgb.add(self.paint_g)
        # B component
        label_b = gtk.Label("B:")
        box_rgb.add(label_b)
        self.paint_b = gtk.SpinButton(gtk.Adjustment(value=0, lower=0, upper=1, step_incr=0.01), digits=2)
        box_rgb.add(self.paint_b)
        separator1 = gtk.HSeparator()
        box_color.add(separator1)
        ### Opacity component
        label_opacity = gtk.Label("""Specify the paint opacity.""")
        box_color.add(label_opacity)
        label_opacity.set_line_wrap(True)
        label_opacity.set_alignment(0, 0.5)
        ## Container for opacity component
        box_opacity = gtk.HBox()
        align_opacity = gtk.Alignment(0, 0, 0, 1)
        align_opacity.add(box_opacity)
        box_color.add(align_opacity)
        # Opacity
        label_a = gtk.Label("Opacity:")
        box_opacity.add(label_a)
        self.paint_opacity = gtk.SpinButton(gtk.Adjustment(value=0, lower=0, upper=1, step_incr=0.01), digits=2)
        box_opacity.add(self.paint_opacity)
        # Frame for general settings ----------------------------------#
        frame_general = gtk.Frame(label = "General Settings")
        box_left.add(frame_general)
        frame_general.set_label_align(0, 0.5)
        frame_general.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        # Box for frame_general ---------#
        box_general = gtk.VBox()
        frame_general.add(box_general)
        ### Blur image
        label_blur = gtk.Label("""Control of the size of the blurring kernel.""")
        box_general.add(label_blur)
        label_blur.set_line_wrap(True)
        ## Container for sigma
        box_sigma = gtk.HBox()
        box_general.add(box_sigma)
        # Sigma
        label_sigma = gtk.Label("Blur factor:")
        box_sigma.add(label_sigma)
        self.paint_sigma = gtk.SpinButton(gtk.Adjustment(value=0, lower=0, upper=1, step_incr=0.01), digits=2)
        box_sigma.add(self.paint_sigma)
        ### Grid size
        label_grid = gtk.Label("""Control of the spacing of brush strokes.""")
        box_general.add(label_grid)
        label_grid.set_line_wrap(True)
        ## Container for grid
        box_grid = gtk.HBox()
        box_general.add(box_grid)
        # Grid
        label_gs = gtk.Label("Grid size:")
        box_grid.add(label_gs)
        self.paint_grid_size = gtk.SpinButton(gtk.Adjustment(value=1, lower=1, upper=10, step_incr=1), digits=0)
        box_grid.add(self.paint_grid_size)
        ### Treshold parameter
        label_treshold = gtk.Label("""How closely the painting must approximate the source image.""")
        box_general.pack_start(label_treshold)
        label_treshold.set_line_wrap(True)
        ## Container for treshold
        box_treshold = gtk.HBox()
        box_general.add(box_treshold)
        # Treshold
        label_t = gtk.Label("Approximation threshold:")
        box_treshold.add(label_t)
        self.paint_threshold = gtk.SpinButton(gtk.Adjustment(value=0, lower=0, upper=1, step_incr=0.01), digits=2)
        box_treshold.add(self.paint_threshold)
        # Container for buttons ---------------------------------------#
        box_buttons = gtk.HButtonBox()
        box_left.add(box_buttons)
        box_left.set_border_width(5)
        box_buttons.set_layout(gtk.BUTTONBOX_SPREAD)
        box_buttons.set_spacing(40)
        ## Buttons
        # OK button
        button_ok = gtk.Button("OK")
        box_buttons.add(button_ok)
        button_ok.connect("clicked", self.paint_ok)
        # RESET button
        button_reset = gtk.Button("Reset")
        box_buttons.add(button_reset)
        button_reset.connect("clicked", self.paint_reset)
        # Container for right column ----------------------------------#
        box_right = gtk.HBox()
        box.add(box_right)
        # Frame for stroke settings -----------------------------------#
        frame_stroke = gtk.Frame(label = "Strokes Settings")
        box_right.add(frame_stroke)
        frame_stroke.set_label_align(0, 0.5)
        frame_stroke.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        # Box for frame_stroke ----------#
        box_stroke = gtk.VBox()
        frame_stroke.add(box_stroke)
        ### Brush sizes
        label_brush = gtk.Label("""A list of brush sizes (from largest to smallest.)""")
        box_stroke.add(label_brush)
        label_brush.set_line_wrap(True)
        ## Container for brush sizes
        box_brush = gtk.HBox()
        box_stroke.add(box_brush)
        # Smallest brush
        label_brush_small = gtk.Label("Smallest:")
        box_brush.add(label_brush_small)
        self.paint_brush_small = gtk.SpinButton(gtk.Adjustment(value=2, lower=1, upper=32, step_incr=1), digits=0)
        box_brush.add(self.paint_brush_small)
        # Number of brushes
        label_brush_n = gtk.Label("Number:")
        box_brush.add(label_brush_n)
        self.paint_brush_n = gtk.SpinButton(gtk.Adjustment(value=1, lower=1, upper=6, step_incr=1), digits=0)
        box_brush.add(self.paint_brush_n)
        # Ratio of brushes
        label_brush_ratio = gtk.Label("Ratio:")
        box_brush.add(label_brush_ratio)
        self.paint_brush_ratio = gtk.SpinButton(gtk.Adjustment(value=2, lower=2, upper=5, step_incr=1), digits=0)
        box_brush.add(self.paint_brush_ratio)
        ### Lengths of strokes
        label_length = gtk.Label("""Specify the minimum and maximum stroke lengths.""")
        box_stroke.add(label_length)
        label_length.set_line_wrap(True)
        ## Container for length of strokes
        box_length = gtk.HBox()
        box_stroke.add(box_length)
        # Minimal length of stroke
        label_min = gtk.Label("Min length:")
        box_length.add(label_min)
        self.paint_length_min = gtk.SpinButton(gtk.Adjustment(value=4, lower=1, upper=30, step_incr=1), digits=0)
        box_length.add(self.paint_length_min)
        # Maximal length of stroke
        label_max = gtk.Label("Max length:")
        box_length.add(label_max)
        self.paint_length_max = gtk.SpinButton(gtk.Adjustment(value=16, lower=1, upper=30, step_incr=1), digits=0)
        box_length.add(self.paint_length_max)
        ### Curvature of stroke
        label_curvature = gtk.Label("""Limit or exaggerate stroke curvature.""")
        box_stroke.add(label_curvature)
        label_curvature.set_line_wrap(True)
        ## Container for curvature
        box_curvature = gtk.HBox()
        box_stroke.add(box_curvature)
        # Curvature
        label_curve = gtk.Label("Curvature flter:")
        box_curvature.add(label_curve)
        self.paint_curvature = gtk.SpinButton(gtk.Adjustment(value=1, lower=0, upper=1, step_incr=0.01), digits=2)
        box_curvature.add(self.paint_curvature)
        # Add page to the notebook ------------------------------------#
        self.notebook.append_page(box)
    ####################################################################

    # Notebook page for image -----------------------------------------#
    def create_image_page(self):
        self.frame_image = gtk.AspectFrame()
        self.notebook.append_page(self.frame_image)
    ####################################################################

    # Notebook page for paint -----------------------------------------#
    def create_paint_page(self):
        self.frame_paint = gtk.AspectFrame()
        self.notebook.append_page(self.frame_image)
    ####################################################################

    # Create cool buttons ... -----------------------------------------#
    def create_button(self, icon, label_button):
        """Creates cool button with label and image.
        """
        box = gtk.HBox(False, 0)
        box.set_border_width(2)

        image = gtk.Image()
        image.set_from_file(icon)
        image.show()
        label = gtk.Label(label_button)
        label.show()

        box.pack_start(image, False, False, 3)
        box.pack_start(label, False, False, 3)
        box.show()

        button = gtk.Button()
        button.add(box)
        button.set_size_request(100, 30)

        return button
    ####################################################################

    # Impressionist style (set parameters). ---------------------------#
    def set_impressionist(self, widget):
        style = paint_style.impressionist
        self.label_title.set_markup("<big>{0}</big>".format(style["label"]))
        self.painter = paint.PainterlyRendering()
        # We adjust parameters for impressionist style of painting.
        self.set_paint_pre_settings(style)
    ####################################################################

    # Expressionist style (set parameters). ---------------------------#
    def set_expressionist(self, widget):
        style = paint_style.expressionist
        self.label_title.set_markup("<big>{0}</big>".format(style["label"]))
        self.painter = paint.PainterlyRendering()
        # We adjust parameters for expressionist style of painting.
        self.set_paint_pre_settings(style)
    ####################################################################

    # Colorist wash style (set parameters). ---------------------------#
    def set_colorist_wash(self, widget):
        style = paint_style.colorist_wash
        self.label_title.set_markup("<big>{0}</big>".format(style["label"]))
        self.painter = paint.PainterlyRendering()
        # We adjust parameters for colorist wash style of painting.
        self.set_paint_pre_settings(style)
    ####################################################################

    # Pointillist style (set parameters). -----------------------------#
    def set_pointillist(self, widget):
        style = paint_style.pointillist
        self.label_title.set_markup("<big>{0}</big>".format(style["label"]))
        self.painter = paint.PainterlyRendering()
        # We adjust parameters for pointillist style of painting.
        self.set_paint_pre_settings(style)
    ####################################################################

    # Painting_parameters (set parameters). ---------------------------#
    def set_painting_parameters(self, widget):
        style = paint_style.default
        self.label_title.set_markup("<big>{0}</big>".format(style["label"]))
        self.painter = paint.PainterlyRendering()
        # We adjust parameters for pointillist style of painting.
        self.set_paint_pre_settings(style)
        self.button_settings.hide()
        self.button_image.show()
        self.notebook.set_current_page(2)
    ####################################################################

    def paint_ok(self, widget):
        """We set parameters for painting."""
        self.set_paint_parameters()

    def paint_reset(self, widget):
        pass

    def pulse_progress_bar(self):
        if threading.active_count() > 1:
            self.progress_bar.pulse()
            return True

        self.progress_bar.set_fraction(0.0)
        self.progress_bar_lock.release()
        return False

    def paint(self, widget):
        self.progress_bar_lock = threading.Lock()
        thread = threading.Thread(target=self.painter.paint)
        thread.start()

        if self.progress_bar_lock.acquire(False):
            glib.timeout_add(250, self.pulse_progress_bar)

    def artist(self, widget):
        self.painter.paint()

    def zoom(self, widget):
        pass

    def settings(self, widget):
        widget.hide()
        self.button_image.show()
        self.notebook.set_current_page(2)

    def show_image_page(self, widget):
        widget.hide()
        self.button_settings.show()
        self.notebook.set_current_page(1)

    # Browse for image ------------------------------------------------#
    def browse_for_image(self, widget):
        """This function is used to browse for an image. The path to the
        image will be returned if the user selects one, however a blank
        string will be returned if they cancel or do not select one.
        """
        file_open = gtk.FileChooserDialog(title="Select Image",
                                          action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                          buttons=(gtk.STOCK_CANCEL,
                                                   gtk.RESPONSE_CANCEL,
                                                   gtk.STOCK_OPEN,
                                                   gtk.RESPONSE_OK))
        # Create and add the Images filter
        filter = gtk.FileFilter()
        filter.set_name("Images")
        filter.add_mime_type("image/png")
        filter.add_mime_type("image/jpeg")
        filter.add_mime_type("image/gif")
        filter.add_pattern("*.png")
        filter.add_pattern("*.jpg")
        filter.add_pattern("*.gif")
        file_open.add_filter(filter)
        # Create and add the 'all files' filter
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        file_open.add_filter(filter)
        # Init the return value
        result = ""
        if file_open.run() == gtk.RESPONSE_OK:
                result = file_open.get_filename()
        file_open.destroy()
        self.input = result
        print result
    ####################################################################

    # Set parameters for painting -------------------------------------#
    def set_paint_parameters(self):
        """Sets all parameters. Image location and settings.
        """
        self.painter.file = self.input
        self.painter.brush_sizes = [self.paint_brush_small.get_value()]
        for i in range(int(self.paint_brush_n.get_value()) - 1):
            self.painter.brush_sizes.insert(0, self.painter.brush_sizes[-1]*self.paint_brush_ratio.get_value())
        self.painter.sigma = self.paint_sigma.get_value()
        self.painter.threshold = self.paint_threshold.get_value()
        self.painter.curvature = self.paint_curvature.get_value()
        self.painter.length_min = int(self.paint_length_min.get_value())
        self.painter.length_max = int(self.paint_length_max.get_value())
        self.painter.opacity = self.paint_opacity.get_value()
        self.painter.grid_size = int(self.paint_grid_size.get_value())
        self.painter.h = self.paint_h.get_value()
        self.painter.s = self.paint_s.get_value()
        self.painter.v = self.paint_v.get_value()
        self.painter.r = self.paint_r.get_value()
        self.painter.g = self.paint_g.get_value()
        self.painter.b = self.paint_b.get_value()
    ####################################################################

    # Set values for paint settings -----------------------------------#
    def set_paint_pre_settings(self, style):
        """Set Settings from known styles and also default
        """
        self.paint_brush_small.set_value(style["brush_small"])
        self.paint_brush_n.set_value(style["brush_n"])
        self.paint_brush_ratio.set_value(style["brush_ratio"])
        self.paint_sigma.set_value(style["sigma"])
        self.paint_threshold.set_value(style["treshold"])
        self.paint_curvature.set_value(style["curvature"])
        self.paint_length_min.set_value(style["length_min"])
        self.paint_length_max.set_value(style["length_max"])
        self.paint_opacity.set_value(style["opacity"])
        self.paint_grid_size.set_value(style["grid_size"])
        self.paint_h.set_value(style["h"])
        self.paint_s.set_value(style["s"])
        self.paint_v.set_value(style["v"])
        self.paint_r.set_value(style["r"])
        self.paint_g.set_value(style["g"])
        self.paint_b.set_value(style["b"])
    ####################################################################

    # Close application -----------------------------------------------#
    def close_app(self, widget):
        self.destroy()
        gtk.main_quit()
    ####################################################################

    # Make Art --------------------------------------------------------#
    def make_art(self, widget):
        """Set default style and settings.
        """
        self.mb.show() # menubar
        self.button_paint.show() # paint button
        self.button_settings.show() # settings button
        self.label_title.show() # title
        self.notebook.set_current_page(1)
########################################################################

####### Run application ################################################
if __name__ == "__main__":
    win = Interface()
    gtk.main()
