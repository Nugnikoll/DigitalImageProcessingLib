# -*- coding: utf-8 -*-

import wx;
import wx.aui as aui;
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

class panel_info(wx.Panel):
	def __init__(self, parent, size = wx.DefaultSize):
		super(panel_info, self).__init__(parent = parent, size = size);
		self.frame = parent;
		while type(self.frame) != dipl_frame:
			self.frame = self.frame.GetParent();
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
		str_menu_window = ["&Mouse Toolbar", "&Transform Toolbar", "&Drawing Toolbar", "Terminal &Panel"];
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

		self.button_color_pen = wx.Button(tool_draw, size = wx.Size(10,10), style = wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL);
		self.button_color_pen.SetBackgroundColour(wx.Colour((0, 0, 0)));
		self.button_color_pen.Bind(wx.EVT_BUTTON, self.on_color_pick);
		tool_draw.AddControl(self.button_color_pen);

		self.button_color_brush = wx.Button(tool_draw, size = wx.Size(10,10), style = wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL);
		self.button_color_brush.SetBackgroundColour(wx.Colour((0, 0, 0)));
		self.button_color_brush.Bind(wx.EVT_BUTTON, self.on_color_pick);
		tool_draw.AddControl(self.button_color_brush);

		self.id_icon_width = wx.NewId();
		self.icon_width = wx.Image("../icon/line.png");
		tool_draw.AddTool(
			self.id_icon_width, "line_width", self.icon_width.ConvertToBitmap(), shortHelp = "line width"
		);
		self.Bind(wx.EVT_TOOL, self.on_line_width, id = self.id_icon_width);

		self.id_tool_pencil = wx.NewId();
		self.icon_pencil = wx.Image("../icon/pencil.png");
		self.icon_pencil.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 6);
		self.icon_pencil.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 22);
		tool_draw.AddTool(
			self.id_tool_pencil, "pencil", self.icon_pencil.ConvertToBitmap(), shortHelp = "pencil"
		);
		self.icon_pencil = wx.Cursor(self.icon_pencil)
		self.Bind(wx.EVT_TOOL, self.on_pencil, id = self.id_tool_pencil);

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

		#create a panel to show infomation
		self.panel_info = panel_info(self);
		self.manager.AddPane(
			self.panel_info,
			aui.AuiPaneInfo().Name("panel_info").Caption("terminal").Right()
				.FloatingSize(self.panel_info.GetBestSize()).CloseButton(True)
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
		self.s_normal = 0;
		self.s_grab = 1;
		self.s_pencil = 2;
		self.s_eraser = 3;
		self.s_picker = 4;
		self.s_bucket = 5;
		self.s_selector = 6;
		self.s_zoom_in = 7;
		self.s_zoom_out = 8;
		self.button_pick = self.button_color_pen;

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
		self.panel_info.text_term.AppendText(text);

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
			pane = self.manager.GetPane("panel_info");
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

	def on_color_pick(self, event):
		dialog = wx.ColourDialog(self);
		if event.GetId() == self.button_color_pen.GetId():
			self.button_pick = self.button_color_pen;
			dialog.GetColourData().SetColour(self.panel_draw.color_pen);
			if dialog.ShowModal() == wx.ID_OK:
				self.panel_draw.color_pen = dialog.GetColourData().GetColour();
				self.button_color_pen.SetBackgroundColour(self.panel_draw.color_pen);
		else:
			self.button_pick = self.button_color_brush;
			dialog.GetColourData().SetColour(self.panel_draw.color_brush);
			if dialog.ShowModal() == wx.ID_OK:
				self.panel_draw.color_brush = dialog.GetColourData().GetColour();
				self.button_color_brush.SetBackgroundColour(self.panel_draw.color_brush);

	def on_line_width(self, event):
		#dialog = wx.NumberEntryDialog(self, message = "Please input the line width", prompt = "width:", caption = "line width", value = self.panel_draw.thick, min = 1);
		dialog = wx.TextEntryDialog(self, message = "Please input the line width", caption = "line width", value = str(self.panel_draw.thick));
		if dialog.ShowModal() == wx.ID_OK:
			thick = float(dialog.GetValue());
			if thick > 0:
				self.panel_draw.thick = thick;

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
			class_name = ('plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck');
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
			print(result)
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
