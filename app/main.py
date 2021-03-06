# -*- coding: utf-8 -*-

import wx;
import wx.aui as aui;
import wx.lib.scrolledpanel;
import sys;
import os;
import time;
import copy;
import math as m;
import traceback;
from matplotlib import pyplot as plt;

from net_mnist import *;
from WideResNet import *;
from net_signs import *;

from panel_draw import *;

class dialog_new(wx.Dialog):

	def __init__(self, parent, title = "", size = (250, 200)):
		super(dialog_new, self).__init__(parent = parent, title = title, size = size);
		panel_base = wx.Panel(self);
		sizer_base = wx.BoxSizer(wx.VERTICAL);
		panel_base.SetSizer(sizer_base);

		sizer_input = wx.GridSizer(2, 2, 5);
		sizer_base.Add(sizer_input, 0, wx.ALL | wx.ALIGN_CENTER, 5);
		label_width = wx.StaticText(panel_base, label = "width:");
		sizer_input.Add(label_width, 0, wx.ALL | wx.ALIGN_CENTER, 5);
		self.text_width = wx.TextCtrl(panel_base, value = "");
		sizer_input.Add(self.text_width, 0, wx.ALL | wx.ALIGN_CENTER, 5);
		label_height = wx.StaticText(panel_base, label = "height:");
		sizer_input.Add(label_height, 0, wx.ALL | wx.ALIGN_CENTER, 5);
		self.text_height = wx.TextCtrl(panel_base, value = "");
		sizer_input.Add(self.text_height, 0, wx.ALL | wx.ALIGN_CENTER, 5);

		sizer_button = wx.BoxSizer(wx.HORIZONTAL);
		sizer_base.Add(sizer_button, 0, wx.ALL | wx.ALIGN_RIGHT, 5);
		button_cancel = wx.Button(panel_base, wx.ID_CANCEL, label = "Cancel");
		sizer_button.Add(button_cancel, 0, wx.ALL | wx.EXPAND, 5);
		button_ok = wx.Button(panel_base, wx.ID_OK , label = "OK");
		sizer_button.Add(button_ok, 0, wx.ALL | wx.EXPAND, 5);

class button_color(wx.BitmapButton):
	def __init__(
		self, parent, id = -1,
		pos = wx.DefaultPosition, size = wx.DefaultSize,
		style = 0
	):
		wx.BitmapButton.__init__(self, parent = parent, id = id, pos = pos, size = size);

		data = np.array([[[20], [100]],[[100], [20]]]);
		data = data.repeat(3, 2).repeat(8, 0).repeat(8, 1);
		data = np.tile(data, (2, 2, 1));
		self.data = data;
		self.color = wx.Colour(0, 0, 0, 255);
		self.Bind(wx.EVT_PAINT, self.on_paint);
		self.display();

	def on_paint(self, event):
		self.display();

	def display(self):
		data = self.data.copy();
		data = data * (1 - self.color[3] / 255) + np.array(self.color[:3]) * self.color[3] / 255;
		img = numpy2bitmap(data); 
		self.SetBitmap(img);

class panel_line(wx.Panel):
	def __init__(self, parent, size = wx.DefaultSize):
		super(panel_line, self).__init__(parent = parent, size = size);
		self.frame = parent;
		self.SetBackgroundColour(wx.Colour(150, 150, 150));
		self.thick = 5;
		self.style = wx.PENSTYLE_SOLID;
		self.Bind(wx.EVT_PAINT, self.on_paint);

	def paint(self):
		dc = wx.ClientDC(self);
		dc.Clear();
		dc.SetPen(wx.Pen(wx.BLACK, self.thick, self.style));
		dc.DrawLine(0, 10, 200, 10);

	def on_paint(self, event):
		self.paint();

	def set_thick(self, thick):
		self.thick = thick;
		self.paint();

	def set_style(self, style):
		self.style = style;
		self.paint();

class panel_brush(wx.Panel):
	def __init__(self, parent, size = wx.DefaultSize):
		super(panel_brush, self).__init__(parent = parent, size = size);
		self.frame = parent;
		self.style = wx.BRUSHSTYLE_SOLID;
		self.Bind(wx.EVT_PAINT, self.on_paint);

	def paint(self):
		dc = wx.ClientDC(self);
		dc.SetBackground(wx.Brush(wx.Colour(150, 150, 150)));
		dc.Clear();
		dc.SetPen(wx.Pen(wx.BLACK, 0));
		dc.SetBrush(wx.Brush(wx.BLACK, self.style));
		dc.DrawRectangle(0, 0, 200, 20);

	def on_paint(self, event):
		self.paint();

	def set_style(self, style):
		self.style = style;
		self.paint();

class panel_style(wx.lib.scrolledpanel.ScrolledPanel):
	def __init__(self, parent, size = wx.DefaultSize):
		super(panel_style, self).__init__(parent = parent, size = size);
		self.frame = parent;
		self.SetBackgroundColour(wx.Colour(150, 150, 150));

		sizer_base = wx.BoxSizer(wx.VERTICAL);
		self.SetSizer(sizer_base);

		sizer_pen = wx.BoxSizer(wx.HORIZONTAL);
		sizer_base.Add(sizer_pen, 0, wx.ALL | wx.ALIGN_CENTER, 5);
		self.button_color_pen = button_color(self, size = wx.Size(40,40), style = wx.SUNKEN_BORDER);
		self.button_color_pen.Bind(wx.EVT_BUTTON, self.on_color_pick);
		sizer_pen.Add(self.button_color_pen, 0, wx.ALL | wx.ALIGN_CENTER, 5);
		self.slider_pen = wx.Slider(self, size = wx.Size(90, 10), value = 255, minValue = 0, maxValue = 255);
		self.slider_pen.Bind(wx.EVT_SCROLL, self.on_slider_scroll);
		sizer_pen.Add(self.slider_pen, 0, wx.ALL | wx.ALIGN_CENTER, 5);

		sizer_brush = wx.BoxSizer(wx.HORIZONTAL);
		sizer_base.Add(sizer_brush, 0, wx.ALL | wx.ALIGN_CENTER, 5);
		self.button_color_brush = button_color(self, size = wx.Size(40,40), style = wx.SUNKEN_BORDER );
		self.button_color_brush.Bind(wx.EVT_BUTTON, self.on_color_pick);
		sizer_brush.Add(self.button_color_brush, 0, wx.ALL | wx.ALIGN_CENTER, 5);
		self.slider_brush = wx.Slider(self, size = wx.Size(90, 10), value = 255, minValue = 0, maxValue = 255);
		self.slider_brush.Bind(wx.EVT_SCROLL, self.on_slider_scroll);
		sizer_brush.Add(self.slider_brush, 0, wx.ALL | wx.ALIGN_CENTER, 5);

		self.panel_line = panel_line(self, size = (200, 20));
		sizer_base.Add(self.panel_line, 0, wx.ALL | wx.ALIGN_CENTER, 5);

		self.spin_line = wx.SpinCtrl(self, size = (200, -1), min = 0, max = 1000, initial = 5);
		self.spin_line.Bind(wx.EVT_SPINCTRL, self.on_spin_line);
		sizer_base.Add(self.spin_line, 0, wx.ALL | wx.ALIGN_CENTER, 5);

		self.choice_line = wx.Choice(
			self, size = (200, -1),
			choices = [
				"solid", "dot", "long_dash", "dot_dash",
				"user_dash", "transparent", "bdiagonal_hatch",
				"cross_diag_hatch", "fdiagonal_hatch", "cross_hatch",
				"horizontal_hatch", "vertical_hatch", "first_hatch",
				"last_hatch"
			],
		);
		self.choice_line.SetSelection(0);
		self.choice_line.Bind(wx.EVT_CHOICE, self.on_choice_line);
		sizer_base.Add(self.choice_line, 0, wx.ALL | wx.ALIGN_CENTER, 5);

		self.panel_brush = panel_brush(self, size = (200, 20));
		sizer_base.Add(self.panel_brush, 0, wx.ALL | wx.ALIGN_CENTER, 5);

		self.choice_brush = wx.Choice(
			self, size = (200, -1),
			choices = [
				"solid", "transparent", "bdiagonal_hatch",
				"cross_diag_hatch", "fdiagonal_hatch", "cross_hatch",
				"horizontal_hatch", "vertical_hatch", "first_hatch",
				"last_hatch"
			],
		);
		self.choice_brush.SetSelection(0);
		self.choice_brush.Bind(wx.EVT_CHOICE, self.on_choice_brush);
		sizer_base.Add(self.choice_brush, 0, wx.ALL | wx.ALIGN_CENTER, 5);

		self.fontctrl = wx.FontPickerCtrl(self, size = (200, -1));
		sizer_base.Add(self.fontctrl, 0, wx.ALL | wx.ALIGN_CENTER, 5);
		self.fontctrl.Bind(wx.EVT_FONTPICKER_CHANGED, self.on_fontctrl);

		self.SetAutoLayout(1);
		self.SetupScrolling();

	def on_color_pick(self, event):
		dialog = wx.ColourDialog(self);
		if event.GetId() == self.button_color_pen.GetId():
			self.frame.button_pick = self.button_color_pen;
			dialog.GetColourData().SetColour(self.frame.panel_draw.color_pen);
			if dialog.ShowModal() == wx.ID_OK:
				color = dialog.GetColourData().GetColour();
				self.frame.panel_draw.color_pen = wx.Colour(*color[:3], self.frame.panel_draw.color_pen[3]);
				self.button_color_pen.color = self.frame.panel_draw.color_pen;
				self.button_color_pen.display();
		else:
			self.frame.button_pick = self.button_color_brush;
			dialog.GetColourData().SetColour(self.frame.panel_draw.color_brush);
			if dialog.ShowModal() == wx.ID_OK:
				color = dialog.GetColourData().GetColour();
				self.frame.panel_draw.color_brush = wx.Colour(*color[:3], self.frame.panel_draw.color_brush[3]);
				self.button_color_brush.color = self.frame.panel_draw.color_brush;
				self.button_color_brush.display();

	def on_slider_scroll(self, event):
		if event.GetId() == self.slider_pen.GetId():
			value = self.slider_pen.GetValue();
			self.frame.panel_draw.color_pen = wx.Colour(*self.frame.panel_draw.color_pen[:3], value)
			self.button_color_pen.color = self.frame.panel_draw.color_pen;
			self.button_color_pen.display();
		else:
			value = self.slider_brush.GetValue();
			self.frame.panel_draw.color_brush = wx.Colour(*self.frame.panel_draw.color_brush[:3], value)
			self.button_color_brush.color = self.frame.panel_draw.color_brush;
			self.button_color_brush.display();

	def on_spin_line(self, event):
		thick = self.spin_line.GetValue();
		self.frame.panel_draw.thick = thick;
		self.panel_line.set_thick(thick);

	def on_choice_line(self, event):
		table_style = [
			wx.PENSTYLE_SOLID, wx.PENSTYLE_DOT, wx.PENSTYLE_LONG_DASH,
			wx.PENSTYLE_DOT_DASH, wx.PENSTYLE_USER_DASH, wx.PENSTYLE_TRANSPARENT,
			wx.PENSTYLE_BDIAGONAL_HATCH, wx.PENSTYLE_CROSSDIAG_HATCH, wx.PENSTYLE_FDIAGONAL_HATCH,
			wx.PENSTYLE_CROSS_HATCH, wx.PENSTYLE_HORIZONTAL_HATCH, wx.PENSTYLE_VERTICAL_HATCH,
			wx.PENSTYLE_FIRST_HATCH, wx.PENSTYLE_LAST_HATCH
		];
		sel = self.choice_line.GetSelection();
		style = table_style[sel];
		self.frame.panel_draw.style_pen = style;
		self.panel_line.set_style(style);

	def on_choice_brush(self, event):
		table_style = [
			wx.BRUSHSTYLE_SOLID, wx.BRUSHSTYLE_TRANSPARENT,
			wx.BRUSHSTYLE_BDIAGONAL_HATCH, wx.BRUSHSTYLE_CROSSDIAG_HATCH, wx.BRUSHSTYLE_FDIAGONAL_HATCH,
			wx.BRUSHSTYLE_CROSS_HATCH, wx.BRUSHSTYLE_HORIZONTAL_HATCH, wx.BRUSHSTYLE_VERTICAL_HATCH,
			wx.BRUSHSTYLE_FIRST_HATCH, wx.BRUSHSTYLE_LAST_HATCH
		];
		sel = self.choice_brush.GetSelection();
		style = table_style[sel];
		self.frame.panel_draw.style_brush = style;
		self.panel_brush.set_style(style);

	def on_fontctrl(self, event):
		self.frame.panel_draw.font = self.fontctrl.GetSelectedFont();

class panel_term(wx.Panel):
	def __init__(self, parent, size = wx.DefaultSize):
		super(panel_term, self).__init__(parent = parent, size = size);
		self.frame = parent;
		self.SetBackgroundColour(wx.BLACK);

		sizer_base = wx.BoxSizer(wx.VERTICAL);
		self.SetSizer(sizer_base);

		self.text_term = wx.TextCtrl(self, wx.NewId(), size = (300, 200), style = wx.TE_READONLY | wx.TE_MULTILINE | wx.HSCROLL);
		self.text_term.SetBackgroundColour(wx.Colour(20, 20, 20));
		self.text_term.SetForegroundColour(wx.Colour(210, 210, 210));
		sizer_base.Add(self.text_term, 1, wx.CENTER | wx.EXPAND, 0);
		self.text_input = wx.TextCtrl(self, wx.NewId(), size = (300, -1), style = wx.TE_PROCESS_ENTER);
		self.text_input.SetBackgroundColour(wx.Colour(20, 20, 20));
		self.text_input.SetForegroundColour(wx.Colour(210, 210, 210));
		self.text_input.Bind(wx.EVT_TEXT_ENTER, self.on_enter);
		sizer_base.Add(self.text_input, 0, wx.CENTER | wx.EXPAND, 0);

	def on_enter(self, event):
		self.text_term.AppendText(">>" + self.text_input.GetValue() + "\n");
		self.frame.process(self.text_input.GetValue());

class dipl_frame(wx.Frame):
	def __init__(self, parent, id = -1, title = "", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_FRAME_STYLE | wx.SUNKEN_BORDER | wx.CLIP_CHILDREN):
		wx.Frame.__init__(self, parent, id, title, pos, size, style);

		font_text = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName = "consolas");
		self.SetFont(font_text)

		#set the icon of the frame
		frame_icon = wx.Icon();
		frame_icon.CopyFromBitmap(wx.Bitmap(wx.Image("../icon/dipl.png")));
		self.SetIcon(frame_icon);

		# tell FrameManager to manage this frame
		self.manager = aui.AuiManager();
		self.manager.SetManagedWindow(self);
		self.manager.GetArtProvider().SetMetric(aui.AUI_DOCKART_CAPTION_SIZE, 24);
		font_caption = wx.Font(14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName = "consolas");
		self.manager.GetArtProvider().SetFont(aui.AUI_DOCKART_CAPTION_FONT, font_caption);

		#create a menu bar
		self.menubar = wx.MenuBar();
		self.SetMenuBar(self.menubar);
		menu_file = wx.Menu();
		self.menubar.Append(menu_file, "&File");
		menu_edit = wx.Menu();
		self.menubar.Append(menu_edit, "&Edit");
		menu_window = wx.Menu();
		self.menubar.Append(menu_window, "&Window");
		menu_help = wx.Menu();
		self.menubar.Append(menu_help, "&Help");

		#add items to menu_file
		menu_new = wx.MenuItem(
			menu_file, id = wx.NewId(),
			text = "&New File\tCtrl-N"
		);
		self.Bind(wx.EVT_MENU, self.on_new, id = menu_new.GetId());
		menu_file.Append(menu_new);
		menu_open = wx.MenuItem(
			menu_file, id = wx.NewId(),
			text = "&Open File\tCtrl-O"
		);
		self.Bind(wx.EVT_MENU, self.on_open, id = menu_open.GetId());
		menu_file.Append(menu_open);
		menu_save = wx.MenuItem(
			menu_file, id = wx.NewId(),
			text = "&Save File\tCtrl-S"
		);
		self.Bind(wx.EVT_MENU, self.on_save, id = menu_save.GetId());
		menu_file.Append(menu_save);
		menu_script = wx.MenuItem(
			menu_file, id = wx.NewId(),
			text = "&Load Script\tCtrl-R"
		);
		self.Bind(wx.EVT_MENU, self.on_script, id = menu_script.GetId());
		menu_file.Append(menu_script);
		menu_quit = wx.MenuItem(
			menu_file, id = wx.NewId(),
			text = "&Quit\tAlt-F4"
		);
		self.Bind(wx.EVT_MENU, self.on_quit, id = menu_quit.GetId());
		menu_file.Append(menu_quit);

		#add items to menu_edit
		menu_undo = wx.MenuItem(
			menu_edit, id = wx.NewId(),
			text = "&Undo\tCtrl-Z"
		);
		self.Bind(wx.EVT_MENU, self.on_undo, id = menu_undo.GetId());
		menu_edit.Append(menu_undo);
		menu_redo = wx.MenuItem(
			menu_edit, id = wx.NewId(),
			text = "&Redo\tCtrl-Y"
		);
		self.Bind(wx.EVT_MENU, self.on_redo, id = menu_redo.GetId());
		menu_edit.Append(menu_redo);

		#add items to menu_window
		str_menu_window = [
			"&Mouse Toolbar", "&Transform Toolbar",
			"&Drawing Toolbar", "&Style Panel",
			"Ter&minal Panel"
		];
		self.list_menu_window = [];
		for item in str_menu_window:
			menu = wx.MenuItem(
				menu_window, id = wx.NewId(),
				text = item
			);
			self.Bind(wx.EVT_MENU, self.on_menu_window, id = menu.GetId());
			menu_window.Append(menu);
			self.list_menu_window.append(menu);

		#add items to menu_help
		menu_about = wx.MenuItem(
			menu_help, id = wx.NewId(),
			text = "&About\tF1"
		);
		self.Bind(wx.EVT_MENU, self.on_about, id = menu_about.GetId());
		menu_help.Append(menu_about);

		#create a toolbar
		self.tool_transform = wx.ToolBar(self, style = wx.TB_FLAT | wx.TB_NODIVIDER);
		self.tool_transform.SetToolBitmapSize(wx.Size(40,40));

		self.choice_transform = wx.Choice(
			self.tool_transform, wx.NewId(), choices = [
				"Resize Image (Nearest Point)",
				"Resize Image (Bilinear)",
				"Histogram Equalization",
				"Power Law",
				"Blur Image",
				"Sharpen Image",
				"Laplacian",
				"Guassian Noise",
				"Salt-and-pepper Noise",
				"Median Filter",
				"MNIST CNN classification",
				"CIFAR-10 classification",
				"SIGNS hand guesture classification"
			],
		);
		self.choice_transform.SetSelection(0);
		self.choice_transform.Bind(wx.EVT_CHOICE, self.on_choice_transform);
		self.tool_transform.AddControl(self.choice_transform);

		self.text_input_info1 = wx.StaticText(self.tool_transform, label = " height:");
		self.tool_transform.AddControl(self.text_input_info1);
		self.text_input1 = wx.TextCtrl(self.tool_transform, value = "300");
		self.tool_transform.AddControl(self.text_input1);
		self.text_input_info2 = wx.StaticText(self.tool_transform, label = " width:");
		self.tool_transform.AddControl(self.text_input_info2);
		self.text_input2 = wx.TextCtrl(self.tool_transform, value = "400");
		self.tool_transform.AddControl(self.text_input2);
		self.text_input_info3 = wx.StaticText(self.tool_transform);
		self.tool_transform.AddControl(self.text_input_info3);
		self.text_input3 = wx.TextCtrl(self.tool_transform);
		self.tool_transform.AddControl(self.text_input3);

		self.id_tool_run = wx.NewId();
		self.tool_transform.AddTool(
			self.id_tool_run, "transform", wx.Bitmap("../icon/right_arrow.png"), shortHelp = "transform"
		);
		self.Bind(wx.EVT_TOOL, self.on_transform, id = self.id_tool_run);

		self.tool_transform.Realize();
		self.manager.AddPane(
			self.tool_transform, aui.AuiPaneInfo().
			Name("tool_transform").Caption("tool transform").
			ToolbarPane().Top().Row(1).Position(2).
			LeftDockable(False).RightDockable(False).
			TopDockable(True).BottomDockable(False)
		);

		self.text_input_info3.Hide();
		self.text_input3.Hide();

		#create a toolbar
		self.tool_mouse = wx.ToolBar(self, size = wx.DefaultSize, style = wx.TB_FLAT | wx.TB_NODIVIDER);
		self.tool_mouse.SetToolBitmapSize(wx.Size(40,40));

		self.id_tool_normal = wx.NewId();
		self.icon_normal = wx.Image("../icon/default.png");
		self.icon_normal.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 6);
		self.icon_normal.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 2);
		self.tool_mouse.AddTool(
			self.id_tool_normal, "normal", self.icon_normal.ConvertToBitmap(), shortHelp = "normal"
		);
		self.icon_normal = wx.Cursor(self.icon_normal);
		self.Bind(wx.EVT_TOOL, self.on_normal, id = self.id_tool_normal);

		self.id_tool_grab = wx.NewId();
		self.icon_grab = wx.Image("../icon/grab.png");
		self.icon_grab.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 12);
		self.icon_grab.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 14);
		self.icon_grabbing = wx.Image("../icon/grabbing.png");
		self.icon_grabbing.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 12);
		self.icon_grabbing.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 14);
		self.tool_mouse.AddTool(
			self.id_tool_grab, "grab", self.icon_grab.ConvertToBitmap(), shortHelp = "grab"
		);
		self.icon_grab = wx.Cursor(self.icon_grab);
		self.icon_grabbing = wx.Cursor(self.icon_grabbing);
		self.Bind(wx.EVT_TOOL, self.on_grab, id = self.id_tool_grab);

		self.id_zoom_in = wx.NewId();
		self.icon_zoom_in = wx.Image("../icon/zoom-in.png");
		self.icon_zoom_in.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 10);
		self.icon_zoom_in.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 9);
		self.tool_mouse.AddTool(
			self.id_zoom_in, "zoom_in", self.icon_zoom_in.ConvertToBitmap(), shortHelp = "zoom in"
		);
		self.icon_zoom_in = wx.Cursor(self.icon_zoom_in);
		self.Bind(wx.EVT_TOOL, self.on_zoom_in, id = self.id_zoom_in);

		self.id_zoom_out = wx.NewId();
		self.icon_zoom_out = wx.Image("../icon/zoom-out.png");
		self.icon_zoom_out.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 10);
		self.icon_zoom_out.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 9);
		self.tool_mouse.AddTool(
			self.id_zoom_out, "zoom_out", self.icon_zoom_out.ConvertToBitmap(), shortHelp = "zoom out"
		);
		self.icon_zoom_out = wx.Cursor(self.icon_zoom_out);
		self.Bind(wx.EVT_TOOL, self.on_zoom_out, id = self.id_zoom_out);

		self.id_zoom_fit = wx.NewId();
		self.tool_mouse.AddTool(
			self.id_zoom_fit, "zoom_fit", wx.Bitmap("../icon/square_box.png"), shortHelp = "zoom fit"
		);
		self.Bind(wx.EVT_TOOL, self.on_zoom_fit, id = self.id_zoom_fit);

		self.tool_mouse.Realize();
		self.manager.AddPane(
			self.tool_mouse, aui.AuiPaneInfo().
			Name("tool_mouse").Caption("tool mouse").
			ToolbarPane().Top().Row(1).Position(1).
			LeftDockable(False).RightDockable(False).
			TopDockable(True).BottomDockable(False)
		);

		#create a toolbar
		tool_draw = wx.ToolBar(self, size = wx.DefaultSize, style = wx.TB_FLAT | wx.TB_NODIVIDER | wx.TB_VERTICAL);
		tool_draw.SetToolBitmapSize(wx.Size(40,40));

		self.id_tool_pencil = wx.NewId();
		self.icon_pencil = wx.Image("../icon/pencil.png");
		self.icon_pencil.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 6);
		self.icon_pencil.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 22);
		tool_draw.AddTool(
			self.id_tool_pencil, "pencil", self.icon_pencil.ConvertToBitmap(), shortHelp = "pencil"
		);
		self.icon_pencil = wx.Cursor(self.icon_pencil)
		self.Bind(wx.EVT_TOOL, self.on_pencil, id = self.id_tool_pencil);

		self.id_draw_smooth = wx.NewId();
		self.icon_smooth = wx.Image("../icon/draw_smooth.png");
		tool_draw.AddTool(
			self.id_draw_smooth, "smooth", self.icon_smooth.ConvertToBitmap(), shortHelp = "draw smooth curves"
		);
		self.Bind(wx.EVT_TOOL, self.on_smooth, id = self.id_draw_smooth);

		self.id_tool_eraser = wx.NewId();
		self.icon_eraser = wx.Image("../icon/eraser.png");
		self.icon_eraser.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 3);
		self.icon_eraser.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 18);
		tool_draw.AddTool(
			self.id_tool_eraser, "eraser", self.icon_eraser.ConvertToBitmap(), shortHelp = "eraser"
		);
		self.icon_eraser = wx.Cursor(self.icon_eraser)
		self.Bind(wx.EVT_TOOL, self.on_eraser, id = self.id_tool_eraser);

		self.id_tool_picker = wx.NewId();
		self.icon_picker = wx.Image("../icon/picker.png");
		self.icon_picker.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 5);
		self.icon_picker.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 19);
		tool_draw.AddTool(
			self.id_tool_picker, "picker", self.icon_picker.ConvertToBitmap(), shortHelp = "picker"
		);
		self.icon_picker = wx.Cursor(self.icon_picker);
		self.Bind(wx.EVT_TOOL, self.on_picker, id = self.id_tool_picker);

		self.id_tool_bucket = wx.NewId();
		self.icon_bucket = wx.Image("../icon/bucket.png");
		self.icon_bucket.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 2);
		self.icon_bucket.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 17);
		tool_draw.AddTool(
			self.id_tool_bucket, "bucket", self.icon_bucket.ConvertToBitmap(), shortHelp = "bucket"
		);
		self.icon_bucket = wx.Cursor(self.icon_bucket)
		self.Bind(wx.EVT_TOOL, self.on_bucket, id = self.id_tool_bucket);

		self.id_tool_selector = wx.NewId();
		self.icon_selector = wx.Image("../icon/select.png");
		tool_draw.AddTool(
			self.id_tool_selector, "selector", self.icon_selector.ConvertToBitmap(), shortHelp = "selector"
		);
		self.icon_selector = wx.Image("../icon/cross.png");
		self.icon_selector.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 11);
		self.icon_selector.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 11);
		self.icon_selector = wx.Cursor(self.icon_selector);
		self.Bind(wx.EVT_TOOL, self.on_selector, id = self.id_tool_selector);

		self.id_trim = wx.NewId();
		self.icon_trim = wx.Image("../icon/trim.png");
		tool_draw.AddTool(
			self.id_trim, "trim", self.icon_trim.ConvertToBitmap(), shortHelp = "trim"
		);
		self.icon_trim = wx.Cursor(self.icon_trim);
		self.Bind(wx.EVT_TOOL, self.on_trim, id = self.id_trim);

		self.id_draw_line = wx.NewId();
		self.icon_line = wx.Image("../icon/draw_line.png");
		tool_draw.AddTool(
			self.id_draw_line, "line", self.icon_line.ConvertToBitmap(), shortHelp = "draw lines"
		);
		self.Bind(wx.EVT_TOOL, self.on_draw, id = self.id_draw_line);

		self.id_draw_circle = wx.NewId();
		self.icon_circle = wx.Image("../icon/draw_circle.png");
		tool_draw.AddTool(
			self.id_draw_circle, "circle", self.icon_circle.ConvertToBitmap(), shortHelp = "draw circles"
		);
		self.Bind(wx.EVT_TOOL, self.on_draw, id = self.id_draw_circle);

		self.id_draw_rect = wx.NewId();
		self.icon_rect = wx.Image("../icon/draw_rect.png");
		tool_draw.AddTool(
			self.id_draw_rect, "rectangle", self.icon_rect.ConvertToBitmap(), shortHelp = "draw rectangles"
		);
		self.Bind(wx.EVT_TOOL, self.on_draw, id = self.id_draw_rect);

		self.id_draw_curve = wx.NewId();
		self.icon_curve = wx.Image("../icon/draw_curve.png");
		tool_draw.AddTool(
			self.id_draw_curve, "curve", self.icon_curve.ConvertToBitmap(), shortHelp = "draw bezier curves"
		);
		self.Bind(wx.EVT_TOOL, self.on_draw, id = self.id_draw_curve);

		self.id_draw_text = wx.NewId();
		self.icon_text = wx.Image("../icon/draw_text.png");
		tool_draw.AddTool(
			self.id_draw_text, "text", self.icon_text.ConvertToBitmap(), shortHelp = "draw text"
		);
		self.Bind(wx.EVT_TOOL, self.on_draw_text, id = self.id_draw_text);

		tool_draw.Realize();
		self.manager.AddPane(
			tool_draw, aui.AuiPaneInfo().
			Name("tool_draw").Caption("tool draw").
			ToolbarPane().Left().
			LeftDockable(True).RightDockable(False).
			TopDockable(False).BottomDockable(False)
		);

		#create a panel to draw pictures
		self.panel_draw = panel_draw(self, size = (1000, 600));
		self.manager.AddPane(self.panel_draw, aui.AuiPaneInfo().Name("panel draw").CenterPane());

		#create a panel to set styles
		self.panel_style = panel_style(self);
		self.manager.AddPane(
			self.panel_style,
			aui.AuiPaneInfo().Name("panel_style").Caption("style").Right().Position(0)
				.FloatingSize(self.panel_style.GetBestSize()).CloseButton(True)
				.MinSize((300, 100))
		);

		#create a panel to show terminal
		self.panel_term = panel_term(self);
		self.manager.AddPane(
			self.panel_term,
			aui.AuiPaneInfo().Name("panel_term").Caption("terminal").Right().Position(1)
				.FloatingSize(self.panel_term.GetBestSize()).CloseButton(True)
				.MinSize((300, 100))
		);

		#add a status bar
		self.status_bar = wx.StatusBar(self, wx.NewId());
		self.status_bar.SetFieldsCount(3);
		self.status_bar.SetStatusWidths([-1, -1, -1]);
		self.SetStatusBar(self.status_bar);

		#show the frame
		self.manager.Update()
		self.Show(True);

		#declare some variables
		self.button_pick = self.panel_style.button_color_pen;

		#redirect io stream
		class redirect:
			frame = self;
			def write(self, buf):
				self.frame.print_term(buf);

		stdout_save = sys.stdout;
		stderr_save = sys.stderr;
		sys.stdout = redirect();
		sys.stderr = redirect();

		#load models
		self.net_mnist = net_mnist();
		self.net_mnist.load_state_dict(torch.load("model_mnist.pt"));
		self.net_mnist.eval();

		self.net_cifar = WideResNet(depth = 28, num_classes = 10);
		self.net_cifar.load_state_dict(torch.load("model_cifar10.pt"));
		self.net_cifar.eval();

		class empty: pass;
		param = empty();
		param.learning_rate = 1e-3;
		param.batch_size = 64;
		param.num_epochs = 100;
		param.dropout_rate = 0.8; 
		param.num_channels = 32;
		param.save_summary_steps = 100;
		param.num_workers = 8;
		self.net_signs = net_signs(param);
		self.net_signs.load_state_dict(torch.load("model_signs.pt")["state_dict"]);
		self.net_signs.eval();

	def Destroy(self):
		self.manager.UnInit();
		del self.manager;
		return super(dipl_frame, self).Destroy();

	def print_term(self, text):
		self.panel_term.text_term.AppendText(text);

	def process(self, script):
		exec(script);

	def on_quit(self, event):
		self.Close();

	def on_about(self, event):
		wx.MessageBox("Digital Image Processing Library\nBy Rick", "About");

	def on_new(self, event):
		dialog = dialog_new(self);
		if dialog.ShowModal() == wx.ID_OK:
			height = int(dialog.text_height.GetValue());
			width = int(dialog.text_width.GetValue());
			if height > 0 and width > 0:
				self.panel_draw.new_image((height, width));
		dialog.Destroy();

	def on_open(self, event):
		if not hasattr(self, "path_image"):
			self.path_image = "../img/";
		if not hasattr(self, "index_image"):
			self.index_image = 1;
		dialog = wx.FileDialog(
			self, message = "Open File", defaultDir = self.path_image,
			wildcard = (
				"Joint Photographic Experts Group files(*.jpg;*.jpeg)|*.jpg;*.jpeg"
				"|Portable Network Graphics Files(*.png)|*.png"
				"|Bitmap Image Files(*.bmp)|*.bmp"
				"|Tagged Image Files(*.tif;*.tiff)|*.tif;*.tiff"
				"|X PixMap Files(*.xpm)|*.xpm"
			),
			style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
		);
		dialog.SetFilterIndex(self.index_image);
		if dialog.ShowModal() == wx.ID_OK:
			self.panel_draw.open_image(dialog.GetPath());
		self.path_image = dialog.GetDirectory();
		self.index_image = dialog.GetFilterIndex();
		dialog.Destroy();

	def on_save(self, event):
		if self.panel_draw.img is None:
			return;
		if not hasattr(self, "path_image"):
			self.path_image = "../img/";
		if not hasattr(self, "index_image"):
			self.index_image = 1;
		dialog = wx.FileDialog(
			self, message = "Save File",
			defaultDir = self.path_image,
			wildcard = (
				"Joint Photographic Experts Group files(*.jpg;*.jpeg)|*.jpg;*.jpeg"
				"|Portable Network Graphics Files(*.png)|*.png"
				"|Bitmap Image Files(*.bmp)|*.bmp"
				"|Tagged Image Files(*.tif;*.tiff)|*.tif;*.tiff"
				"|X PixMap Files(*.xpm)|*.xpm"
			),
			style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
		);
		dialog.SetFilterIndex(self.index_image);
		if dialog.ShowModal() == wx.ID_OK:
			self.panel_draw.save_image(dialog.GetPath());
		self.path_image = dialog.GetDirectory();
		self.index_image = dialog.GetFilterIndex();
		dialog.Destroy();

	def on_script(self, event):
		if not hasattr(self, "path_script"):
			self.path_script = "../sample/";
		dialog = wx.FileDialog(self, message = "Load Python Script", defaultDir = self.path_script, wildcard = "Python Scripts(*.py)|*.py", style = wx.FD_OPEN);
		if dialog.ShowModal() == wx.ID_OK:
			with open(dialog.GetPath()) as fobj:
				script = fobj.read();
			self.process(script);
		self.path_script = dialog.GetDirectory();
		dialog.Destroy();

	def on_undo(self, event):
		if self.panel_draw.img is None:
			return;
		self.panel_draw.img.undo();
		self.panel_draw.clear();
		self.panel_draw.img.display();

	def on_redo(self, event):
		if self.panel_draw.img is None:
			return;
		self.panel_draw.img.redo();
		self.panel_draw.clear();
		self.panel_draw.img.display();

	def on_menu_window(self, event):
		mid = event.GetId();
		num = 0;
		if mid == self.list_menu_window[num].GetId():
			pane = self.manager.GetPane("tool_mouse");
			if pane.IsShown():
				pane.Hide();
			else:
				pane.Show();
		num += 1;

		if mid == self.list_menu_window[num].GetId():
			pane = self.manager.GetPane("tool_transform");
			if pane.IsShown():
				pane.Hide();
			else:
				pane.Show();
		num += 1;

		if mid == self.list_menu_window[num].GetId():
			pane = self.manager.GetPane("tool_draw");
			if pane.IsShown():
				pane.Hide();
			else:
				pane.Show();
		num += 1;

		if mid == self.list_menu_window[num].GetId():
			pane = self.manager.GetPane("panel_style");
			if pane.IsShown():
				pane.Hide();
			else:
				pane.Show();
		num += 1;

		if mid == self.list_menu_window[num].GetId():
			pane = self.manager.GetPane("panel_term");
			if pane.IsShown():
				pane.Hide();
			else:
				pane.Show();
		num += 1;

		self.manager.Update();

	def on_normal(self, event):
		self.panel_draw.set_status(self.panel_draw.s_normal);

	def on_grab(self, event):
		self.panel_draw.set_status(self.panel_draw.s_grab);

	def on_pencil(self, event):
		self.panel_draw.set_status(self.panel_draw.s_pencil);

	def on_smooth(self, event):
		self.panel_draw.set_status(self.panel_draw.s_smooth);

	def on_eraser(self, event):
		self.panel_draw.set_status(self.panel_draw.s_eraser);

	def on_picker(self, event):
		self.panel_draw.set_status(self.panel_draw.s_picker);

	def on_bucket(self, event):
		self.panel_draw.set_status(self.panel_draw.s_bucket);

	def on_selector(self, event):
		self.panel_draw.set_status(self.panel_draw.s_selector);

	def on_trim(self, event):
		if (
			self.panel_draw.img is None
			or self.panel_draw.pos_list is None
			or len(self.panel_draw.pos_list) < 2
		):
			return;
		self.panel_draw.img.trim();
		self.panel_draw.clear();
		self.panel_draw.img.display();

	def on_draw(self, event):
		event_id = event.GetId();
		if event_id == self.id_draw_line:
			status_draw = self.panel_draw.sd_line;
		elif event_id == self.id_draw_rect:
			status_draw = self.panel_draw.sd_rect;
		elif event_id == self.id_draw_circle:
			status_draw = self.panel_draw.sd_circle
		elif event_id == self.id_draw_curve:
			status_draw = self.panel_draw.sd_curve;
		self.panel_draw.set_status(self.panel_draw.s_draw, status_draw);

	def on_draw_text(self, event):
		self.panel_draw.set_status(self.panel_draw.s_text);
		dialog = wx.TextEntryDialog(self, "Text:", caption = "Draw Text", value = self.panel_draw.text);
		if dialog.ShowModal() == wx.ID_OK:
			self.panel_draw.text = dialog.GetValue();

	def on_zoom_in(self, event):
		self.panel_draw.set_status(self.panel_draw.s_zoom_in);

	def on_zoom_out(self, event):
		self.panel_draw.set_status(self.panel_draw.s_zoom_out);

	def on_zoom_fit(self, event):
		if self.panel_draw.img is None:
			return;
		self.panel_draw.img.zoom_fit(np.array(self.panel_draw.GetSize())[::-1]);
		self.SetStatusText(str(self.panel_draw.img.scale[0]), 1);
		self.panel_draw.clear();
		self.panel_draw.img.display();

	def on_choice_transform(self, event):
		sel = self.choice_transform.GetCurrentSelection();
		num = 0;

		if sel == num or sel == num + 1:
			self.text_input_info1.Show();
			self.text_input_info2.Show();
			self.text_input_info1.SetLabel(" height:");
			self.text_input_info2.SetLabel(" width:");
			self.text_input1.Show();
			self.text_input2.Show();
			if not (self.panel_draw.img is None):
				self.text_input1.SetValue(str(self.panel_draw.img.data.shape[0]));
				self.text_input2.SetValue(str(self.panel_draw.img.data.shape[1]));
			else:
				self.text_input1.SetValue(str(300));
				self.text_input2.SetValue(str(400));
			self.text_input_info3.Hide();
			self.text_input3.Hide();
			return;
		num += 2;

		if sel == num:
			self.text_input_info1.Hide();
			self.text_input_info2.Hide();
			self.text_input1.Hide();
			self.text_input2.Hide();
			self.text_input_info3.Hide();
			self.text_input3.Hide();
			return;
		num += 1;

		if sel == num:
			self.text_input_info1.Show();
			self.text_input_info2.Hide();
			self.text_input_info1.SetLabel(" gamma:");
			self.text_input1.Show();
			self.text_input2.Hide();
			self.text_input1.SetValue(str(0.65));
			self.text_input_info3.Hide();
			self.text_input3.Hide();
			return;
		num += 1;

		if sel == num:
			self.text_input_info1.Show();
			self.text_input_info2.Hide();
			self.text_input_info1.SetLabel(" kernel size:");
			self.text_input1.Show();
			self.text_input2.Hide();
			self.text_input1.SetValue(str(3));
			self.text_input_info3.Hide();
			self.text_input3.Hide();
			return;
		num += 1;

		if sel == num:
			self.text_input_info1.Show();
			self.text_input_info2.Hide();
			self.text_input_info1.SetLabel(" alpha:");
			self.text_input1.Show();
			self.text_input2.Hide();
			self.text_input1.SetValue(str(-0.65));
			self.text_input_info3.Hide();
			self.text_input3.Hide();
			return;
		num += 1;

		if sel == num:
			self.text_input_info1.Hide();
			self.text_input_info2.Hide();
			self.text_input1.Hide();
			self.text_input2.Hide();
			self.text_input_info3.Hide();
			self.text_input3.Hide();
			return;
		num += 1;

		if sel == num:
			self.text_input_info1.Show();
			self.text_input_info2.Hide();
			self.text_input_info1.SetLabel(" variance:");
			self.text_input1.Show();
			self.text_input2.Hide();
			self.text_input1.SetValue(str(5.0));
			self.text_input_info3.Hide();
			self.text_input3.Hide();
			return;
		num += 1;

		if sel == num:
			self.text_input_info1.Show();
			self.text_input_info2.Show();
			self.text_input_info1.SetLabel(" probability:");
			self.text_input_info2.SetLabel(" value:")
			self.text_input1.Show();
			self.text_input2.Show();
			self.text_input1.SetValue(str(0.1));
			self.text_input2.SetValue(str(10))
			self.text_input_info3.Hide();
			self.text_input3.Hide();
			return;
		num += 1;

		if sel == num:
			self.text_input_info1.Show();
			self.text_input_info2.Hide();
			self.text_input_info3.Hide();
			self.text_input_info1.SetLabel(" kernel size:");
			self.text_input1.Show();
			self.text_input2.Hide();
			self.text_input3.Hide();
			self.text_input1.SetValue(str(5));
			return;
		num += 1;

		if sel == num:
			self.text_input_info1.Show();
			self.text_input_info1.SetLabel(" number:  ")
			self.text_input_info2.Hide();
			self.text_input1.Hide();
			self.text_input2.Hide();
			self.text_input_info3.Hide();
			self.text_input3.Hide();
			return;
		num += 1;

		if sel == num:
			self.text_input_info1.Show();
			self.text_input_info1.SetLabel(" object:  ")
			self.text_input_info2.Hide();
			self.text_input1.Hide();
			self.text_input2.Hide();
			self.text_input_info3.Hide();
			self.text_input3.Hide();
			return;
		num += 1;

		if sel == num:
			self.text_input_info1.Show();
			self.text_input_info1.SetLabel(" number:  ")
			self.text_input_info2.Hide();
			self.text_input1.Hide();
			self.text_input2.Hide();
			self.text_input_info3.Hide();
			self.text_input3.Hide();
			return;
		num += 1;

	def on_transform(self, event):
		if self.panel_draw.img is None:
			return;

		sel = self.choice_transform.GetCurrentSelection();
		num = 0;

		if sel == num:
			height = int(self.text_input1.GetValue());
			width = int(self.text_input2.GetValue());
			if height <= 0 or width <= 0:
				return;
			self.panel_draw.img.resize_near(np.array((height, width)));
			self.panel_draw.clear();
			self.panel_draw.img.display();
			return;
		num += 1;

		if sel == num:
			height = int(self.text_input1.GetValue());
			width = int(self.text_input2.GetValue());
			if height <= 0 or width <= 0:
				return;
			self.panel_draw.img.resize_linear(np.array((height, width)));
			self.panel_draw.clear();
			self.panel_draw.img.display();
			return;
		num += 1;

		if sel == num:
			self.panel_draw.img.equalize();
			self.panel_draw.img.display();
			return;
		num += 1;

		if sel == num:
			gamma = float(self.text_input1.GetValue());
			if gamma <= 0:
				return;
			self.panel_draw.img.power_law(gamma);
			self.panel_draw.img.display();
			return;
		num += 1;

		if sel == num:
			kernel_size = int(self.text_input1.GetValue());
			if kernel_size < 0:
				return;
			kernel = np.array([
				[
					min([i + 1, j + 1, kernel_size - i, kernel_size - j]) for j in range(kernel_size)
				] for i in range(kernel_size)
			], dtype = np.float64);
			kernel /= np.sum(kernel);
			self.panel_draw.img.correlate(kernel);
			self.panel_draw.img.display();
			return;
		num += 1;

		if sel == num:
			alpha = float(self.text_input1.GetValue());
			self.panel_draw.img.sharpen(alpha);
			self.panel_draw.img.display();
			return;
		num += 1;

		if sel == num:
			self.panel_draw.img.laplacian();
			self.panel_draw.img.display();
			return;
		num += 1;

		if sel == num:
			variance = float(self.text_input1.GetValue());
			if variance <= 0:
				return;
			self.panel_draw.img.noise_guass(variance);
			self.panel_draw.img.display();
			return;
		num += 1;

		if sel == num:
			probability = float(self.text_input1.GetValue());
			value = int(self.text_input2.GetValue());
			if probability <= 0 or probability > 1 or value < -255 or value > 255:
				return;
			self.panel_draw.img.noise_salt(probability, value);
			self.panel_draw.img.display();
			return;
		num += 1;

		if sel == num:
			kernel_size = int(self.text_input1.GetValue());
			if kernel_size <= 0:
				return;
			self.panel_draw.img.filter_median(kernel_size);
			self.panel_draw.img.display();
			return;
		num += 1;

		if sel == num:
			img = self.panel_draw.img.copy();
			img.resize_linear((28, 28));
			data = (np.mean(img.data, axis = 2) / 255);
			if np.mean(data) > 0.5:
				data = 1 - data;
			data = data.reshape((1, 1, 28, 28));
			data = Variable(torch.Tensor(data));
			result = self.net_mnist(data).reshape(10);
			prob, result = result.max(dim = 0);
			self.text_input_info1.SetLabel(" number: %d value: %.4f" % (result.data.item(), prob.data.item()));
			return;
		num += 1;

		if sel == num:
			img = self.panel_draw.img.copy();
			img.resize_linear((32, 32));
			data = img.data / 255;
			data = data.reshape((1, 32, 32, 3));
			data = np.rollaxis(data, 3, 1);
			data = Variable(torch.Tensor(data));
			result = self.net_cifar(data).reshape(10);
			prob, result = result.max(dim = 0);
			class_name = ("plane", "car", "bird", "cat", "deer", "dog", "frog", "horse", "ship", "truck");
			self.text_input_info1.SetLabel(" object: %s value: %.4f" % (class_name[result.data.item()], prob.data.item()));
			return;
		num += 1;

		if sel == num:
			img = self.panel_draw.img.copy();
			img.resize_linear((64, 64));
			data = img.data / 255;
			data = data.reshape((1, 64, 64, 3));
			data = np.rollaxis(data, 3, 1)
			data = Variable(torch.Tensor(data));
			result = self.net_signs(data).reshape(6);
			prob, result = result.max(dim = 0);
			self.text_input_info1.SetLabel(" number: %d value: %.4f" % (result.data.item(), prob.data.item()));
			return;
		num += 1;

class dipl_app(wx.App):

	#overload the initializer
	def OnInit(self):
		self.frame = dipl_frame(None, title = "Digital Image Processing", size = (1100, 700));
		return True;

if __name__ == "__main__":
	app = dipl_app(False);
	app.MainLoop();
