# -*- coding: utf-8 -*-

import wx;
import sys;
import os;
import time;
from matplotlib import pyplot as plt;
from PIL import Image as image;
import numpy as np;
from jpeg import jpeg;

def img2numpy(wximg):
	img = wximg.ConvertToImage();
	buf = img.GetDataBuffer();
	data = np.frombuffer(buf, dtype="uint8");
	data = data.reshape((img.GetHeight(), img.GetWidth(), -1));
	data = data.astype(np.int32);
	return data;

def numpy2img(data):
	buf = data.ravel().astype(np.uint8).tobytes();
	wximg = wx.Image(data.shape[1], data.shape[0], buf).ConvertToBitmap();
	return wximg;

class dimage:
	def __init__(self, data = None):
		self.data = data;
		self.pos = np.array([0, 0], dtype = np.int32);
		self.scale = np.array([1, 1], dtype = np.float64);

	def load(self, filename):
		self.data = img2numpy(wx.Bitmap(filename));

	def save(self, filename):
		pass;

	def display(self, dc):
		dc.DrawBitmap(numpy2img(self.data), self.pos[0], self.pos[1]);

	def move(self, distance):
		self.pos += distance;

	def rescale(self, pos, scale):
		np_pos = np.array(pos);
		np_scale = np.array(scale);
		self.pos = (np_pos + np_scale * (self.pos - np_pos)).astype(np.int32);
		self.scale *= np_scale;

	def resize_near(self, size):
		result = np.empty((size[0], size[1], self.data.shape[2]), dtype = np.int32);
		for i in range(self.data.shape[2]):
			result[:, :, i] = jpeg.resize_near(self.data[:, :, i].copy(), int(size[0]), int(size[1]));
		self.data = result;

	def resize_linear(self, size):
		result = np.empty((size[0], size[1], self.data.shape[2]), dtype = np.int32);
		for i in range(self.data.shape[2]):
			result[:, :, i] = jpeg.resize_linear(self.data[:, :, i].copy(), int(size[0]), int(size[1]));
		self.data = result;

	def equalize(self):
		result = np.empty(self.data.shape, dtype = np.int32);
		for i in range(self.data.shape[2]):
			result[:, :, i] = jpeg.equalize(self.data[:, :, i].copy());
		self.data = result;

	def power_law(self, gamma):
		result = np.empty(self.data.shape, dtype = np.int32);
		for i in range(self.data.shape[2]):
			result[:, :, i] = jpeg.power_law(self.data[:, :, i].copy(), gamma);
		self.data = result;

	def convolute(self, kernel):
		shape = [i for i in self.data.shape];
		shape[0] += kernel.shape[0] - 1;
		shape[1] += kernel.shape[1] - 1;
		result = np.empty(shape, dtype = np.float64);
		for i in range(self.data.shape[2]):
			result[:, :, i] = jpeg.correlate2(self.data[:, :, i].astype(np.float64), kernel);
		result[result > 255] = 255;
		result[result < 0] = 0;
		result = result.astype(np.int32);
		self.data = result;

	def sharpen(self, alpha):
		result = np.empty(self.data.shape, dtype = np.int32);
		for i in range(self.data.shape[2]):
			result[:, :, i] = jpeg.laplacian(self.data[:, :, i].copy());
		result = self.data + result * alpha;
		result[result > 255] = 255;
		result[result < 0] = 0;
		result = result.astype(np.int32);
		self.data = result;

	def laplacian(self):
		result = np.empty(self.data.shape, dtype = np.int32);
		for i in range(self.data.shape[2]):
			result[:, :, i] = jpeg.laplacian(self.data[:, :, i].copy());
		result -= np.min(result);
		result = result.astype(np.float64) * 255 / np.max(result);
		result = result.astype(np.int32);
		self.data = result;

class dipl_frame(wx.Frame):
	def __init__(self, parent, id = -1, title = "", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_FRAME_STYLE | wx.SUNKEN_BORDER | wx.CLIP_CHILDREN):
		wx.Frame.__init__(self, parent, id, title, pos, size, style);

		font_text = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName = "consolas");
		self.SetFont(font_text)

		#set the icon of the frame
#		frame_icon = wx.Icon();
#		frame_icon.CopyFromBitmap(wx.Bitmap(wx.Image("../img/")));
#		self.SetIcon(frame_icon);

		#create a menu bar
		self.menubar = wx.MenuBar();
		self.SetMenuBar(self.menubar);
		menu_file = wx.Menu();
		self.menubar.Append(menu_file, "&File");
		menu_edit = wx.Menu();
		self.menubar.Append(menu_edit, "&Edit");
		menu_help = wx.Menu();
		self.menubar.Append(menu_help, "&Help");

		#add items to menu_file
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
		#self.Bind(wx.EVT_MENU, self.on_save, id = menu_save.GetId());
		menu_file.Append(menu_save);

		#add items to menu_edit
		menu_resize = wx.Menu();
		menu_edit.Append(wx.NewId(), "&Resize Image", menu_resize);
		menu_equalize = wx.MenuItem(
			menu_edit, id = wx.NewId(),
			text = "&Histogram Equalization"
		);
		self.Bind(wx.EVT_MENU, self.on_equalize, id = menu_equalize.GetId());
		menu_edit.Append(menu_equalize);
		menu_power = wx.MenuItem(
			menu_edit, id = wx.NewId(),
			text = "&Power Transform"
		);
		self.Bind(wx.EVT_MENU, self.on_power, id = menu_power.GetId());
		menu_edit.Append(menu_power);
		menu_blur = wx.MenuItem(
			menu_edit, id = wx.NewId(),
			text = "&Blur Image"
		);
		self.Bind(wx.EVT_MENU, self.on_blur, id = menu_blur.GetId());
		menu_edit.Append(menu_blur);
		menu_sharpen = wx.MenuItem(
			menu_edit, id = wx.NewId(),
			text = "&Sharpen Image"
		);
		self.Bind(wx.EVT_MENU, self.on_sharpen, id = menu_sharpen.GetId());
		menu_edit.Append(menu_sharpen);
		menu_laplacian = wx.MenuItem(
			menu_edit, id = wx.NewId(),
			text = "&Laplacian"
		);
		self.Bind(wx.EVT_MENU, self.on_laplacian, id = menu_laplacian.GetId());
		menu_edit.Append(menu_laplacian);

		#add items to menu_resize
		self.menu_resize_near = wx.MenuItem(
			menu_resize, id = wx.NewId(),
			text = "&Nearest Point"
		);
		self.Bind(wx.EVT_MENU, self.on_resize, id = self.menu_resize_near.GetId());
		menu_resize.Append(self.menu_resize_near);
		self.menu_resize_linear = wx.MenuItem(
			menu_resize, id = wx.NewId(),
			text = "&Linear"
		);
		self.Bind(wx.EVT_MENU, self.on_resize, id = self.menu_resize_linear.GetId());
		menu_resize.Append(self.menu_resize_linear);

		#add items to menu_help
		menu_about = wx.MenuItem(
			menu_help, id = wx.NewId(),
			text = "&About\tF1"
		);
		self.Bind(wx.EVT_MENU, self.on_about, id = menu_about.GetId());
		menu_help.Append(menu_about);

		#create background elements
		sizer_base = wx.BoxSizer(wx.HORIZONTAL);
		self.SetSizer(sizer_base);
		self.panel_base = wx.Panel(self);
		self.panel_base.SetBackgroundColour(wx.BLACK);
		sizer_base.Add(self.panel_base, 1, wx.ALL | wx.EXPAND,5);
		sizer_main = wx.BoxSizer(wx.VERTICAL);
		self.panel_base.SetSizer(sizer_main);

		#create a toolbar
		tool_mouse = wx.ToolBar(self, style = wx.TB_FLAT | wx.TB_NODIVIDER);
		tool_mouse.SetToolBitmapSize((24, 24));
		self.id_tool_normal = wx.NewId();
		self.icon_normal = wx.Bitmap("../icon/default.png");
		tool_mouse.AddTool(
			self.id_tool_normal, "normal", self.icon_normal, shortHelp = "normal"
		);
		self.Bind(wx.EVT_TOOL, self.on_normal, id = self.id_tool_normal);
		self.id_tool_grab = wx.NewId();
		self.icon_grab = wx.Bitmap("../icon/grab.png");
		self.icon_grabbing = wx.Bitmap("../icon/grabbing.png");
		tool_mouse.AddTool(
			self.id_tool_grab, "grab", self.icon_grab, shortHelp = "grab"
		);
		self.Bind(wx.EVT_TOOL, self.on_grab, id = self.id_tool_grab);
		self.id_tool_pencil = wx.NewId();
		self.icon_pencil = wx.Bitmap("../icon/pencil.png");
		tool_mouse.AddTool(
			self.id_tool_pencil, "pencil", self.icon_pencil, shortHelp = "pencil"
		);
		self.Bind(wx.EVT_TOOL, self.on_pencil, id = self.id_tool_pencil);
		self.id_zoom_in = wx.NewId();
		self.icon_zoom_in = wx.Bitmap("../icon/zoom-in.png");
		tool_mouse.AddTool(
			self.id_zoom_in, "zoom_in", self.icon_zoom_in, shortHelp = "zoom in"
		);
		self.Bind(wx.EVT_TOOL, self.on_zoom_in, id = self.id_zoom_in);
		self.id_zoom_out = wx.NewId();
		self.icon_zoom_out = wx.Bitmap("../icon/zoom-out.png");
		tool_mouse.AddTool(
			self.id_zoom_out, "zoom_out", self.icon_zoom_out, shortHelp = "zoom out"
		);
		self.Bind(wx.EVT_TOOL, self.on_zoom_out, id = self.id_zoom_out);
		tool_mouse.Realize();
		sizer_main.Add(tool_mouse, 0, wx.ALL | wx.EXPAND, 5);

		#create a panel to draw pictures
		self.panel_draw = wx.Panel(self.panel_base);
		self.panel_draw.SetBackgroundColour(wx.BLACK);
		sizer_main.Add(self.panel_draw, 1, wx.ALL | wx.EXPAND, 5);
		self.panel_draw.Bind(wx.EVT_PAINT, self.on_panel_draw_paint);

		#show the frame
		self.Show(True);

		self.path = None;
		self.img = None;

	def on_quit(self, event):
		self.Close();

	def on_about(self, event):
		wx.MessageBox("Digital Image Processing Library\nBy Rick", "About");

	def on_panel_draw_paint(self, event):
		if not (self.img is None):
			self.img.display(wx.ClientDC(self.panel_draw));

	def on_open(self, event):
		dialog = wx.FileDialog(self, message = "Open File", defaultDir = "../img/", wildcard = "Image Files(*.bmp;*.jpg;*.jpeg;*.png)|*.bmp;*.jpg;*.jpeg;*.png", style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST);
		if dialog.ShowModal() == wx.ID_OK:
			self.path = dialog.GetPath();
#			self.img = wx.Bitmap(self.path);
#			dc = wx.ClientDC(self.panel_draw);
#			self.do_paint(dc);
			self.img = dimage();
			self.img.load(self.path);
			self.img.display(wx.ClientDC(self.panel_draw));

	def on_resize(self, event):
		if self.img is None:
			return;

		dialog = wx.TextEntryDialog(self, message = "Please input the height of the image.", caption = "Resize", value = str(self.img.data.shape[0]));
		if dialog.ShowModal() == wx.ID_OK:
			height = int(dialog.GetValue());
			if height <= 0:
				return;
		else:
			return;
		dialog = wx.TextEntryDialog(self, message = "Please input the width of the image.", caption = "Resize", value = str(self.img.data.shape[1]));
		if dialog.ShowModal() == wx.ID_OK:
			width = int(dialog.GetValue());
			if width <= 0:
				return;
		else:
			return;

		if event.GetId() == self.menu_resize_near.GetId():
			self.img.resize_near(np.array((height, width)));
		elif event.GetId() == self.menu_resize_linear.GetId():
			self.img.resize_linear(np.array((height, width)));
		else:
			return;
		self.img.display(wx.ClientDC(self.panel_draw));

	def on_equalize(self, event):
		if self.img is None:
			return;

		self.img.equalize();
		self.img.display(wx.ClientDC(self.panel_draw));

	def on_power(self, event):
		if self.img is None:
			return;

		dialog = wx.TextEntryDialog(self, message = "Please input the power.", caption = "Power Law", value = str(0.65));
		if dialog.ShowModal() == wx.ID_OK:
			gamma = float(dialog.GetValue());
		else:
			return;

		self.img.power_law(gamma);
		self.img.display(wx.ClientDC(self.panel_draw));

	def on_blur(self, event):
		if self.img is None:
			return;

		dialog = wx.TextEntryDialog(self, message = "Please input the kernel size.", caption = "Blur", value = str(5));
		if dialog.ShowModal() == wx.ID_OK:
			kernel_size = int(dialog.GetValue());
			if kernel_size <= 0:
				return;
		else:
			return;

		kernel = np.array([[min([i + 1, j + 1, kernel_size - i, kernel_size - j]) for j in range(kernel_size)] for i in range(kernel_size)], dtype = np.float64);
		kernel /= np.sum(kernel);

		self.img.convolute(kernel);
		self.img.display(wx.ClientDC(self.panel_draw));

	def on_sharpen(self, event):
		if self.img is None:
			return;

		dialog = wx.TextEntryDialog(self, message = "Please input the coefficient of laplacian.", caption = "Power Law", value = str(-0.65));
		if dialog.ShowModal() == wx.ID_OK:
			alpha = float(dialog.GetValue());
		else:
			return;

		self.img.sharpen(alpha);
		self.img.display(wx.ClientDC(self.panel_draw));

	def on_laplacian(self, event):
		if self.img is None:
			return;

		self.img.laplacian();
		self.img.display(wx.ClientDC(self.panel_draw));

	def on_normal(self, event):
		self.panel_draw.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT));

	def on_grab(self, event):
		self.panel_draw.SetCursor(wx.Cursor(self.icon_grab.ConvertToImage()));

	def on_pencil(self, event):
		self.panel_draw.SetCursor(wx.Cursor(wx.CURSOR_PENCIL));

	def on_zoom_in(self, event):
		self.panel_draw.SetCursor(wx.Cursor(self.icon_zoom_in.ConvertToImage()));

	def on_zoom_out(self, event):
		self.panel_draw.SetCursor(wx.Cursor(self.icon_zoom_out.ConvertToImage()));

class dipl_app(wx.App):

	#overload the initializer
	def OnInit(self):
		self.frame = dipl_frame(None, title = "Digital Image Processing", size = (800, 600));
		return True;

if __name__ == "__main__":
	app = dipl_app(False);
	app.MainLoop();
