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
	img = wximg.ConvertToImage()
	buf = img.GetDataBuffer();
	data = np.frombuffer(buf, dtype="uint8");
	data = data.reshape((img.GetHeight(), img.GetWidth(), -1));
	data = data.astype(np.int32);
	return data;

def numpy2img(data):
	buf = data.ravel().astype(np.uint8).tobytes();
	wximg = wx.Image(data.shape[1], data.shape[0], buf).ConvertToBitmap();
	return wximg;

class dipl_app(wx.App):

	#overload the initializer
	def OnInit(self):
		self.init_frame();
		return True;

	#initialize the frame
	def init_frame(self):

		#create a frame
		self.frame = wx.Frame();
		self.frame.Create(None, title = "Digital Image Processing", size = (600, 400));
		font_text = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName = "consolas");
		self.frame.SetFont(font_text)

		#set the icon of the frame
#		frame_icon = wx.Icon();
#		frame_icon.CopyFromBitmap(wx.Bitmap(wx.Image("../img/")));
#		self.frame.SetIcon(frame_icon);

		#create background elements
		sizer_base = wx.BoxSizer(wx.HORIZONTAL);
		self.frame.SetSizer(sizer_base);
		self.panel_base = wx.Panel(self.frame);
		self.panel_base.SetBackgroundColour(wx.BLACK);
		sizer_base.Add(self.panel_base, 1, wx.ALL | wx.EXPAND,5);
		sizer_main = wx.BoxSizer(wx.HORIZONTAL);
		self.panel_base.SetSizer(sizer_main);

		#create a menu bar
		self.menubar = wx.MenuBar();
		self.frame.SetMenuBar(self.menubar);
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
		menu_file.Append(menu_open);
		menu_save = wx.MenuItem(
			menu_file, id = wx.NewId(),
			text = "&Save File\tCtrl-S"
		);
		menu_file.Append(menu_save);

		#add items to menu_edit
		menu_resize = wx.Menu();
		menu_edit.Append(wx.NewId(), "&Resize Image", menu_resize);
		menu_equalize = wx.MenuItem(
			menu_edit, id = wx.NewId(),
			text = "&Histogram Equalization"
		);
		menu_edit.Append(menu_equalize);
		menu_power = wx.MenuItem(
			menu_edit, id = wx.NewId(),
			text = "&Power Transform"
		);
		menu_edit.Append(menu_power);
		menu_blur = wx.MenuItem(
			menu_edit, id = wx.NewId(),
			text = "&Blur Image"
		);
		menu_edit.Append(menu_blur);
		menu_sharpen = wx.MenuItem(
			menu_edit, id = wx.NewId(),
			text = "&Sharpen Image"
		);
		menu_edit.Append(menu_sharpen);
		menu_laplacian = wx.MenuItem(
			menu_edit, id = wx.NewId(),
			text = "&Laplacian"
		);
		menu_edit.Append(menu_laplacian);

		#add items to menu_resize
		self.menu_resize_near = wx.MenuItem(
			menu_resize, id = wx.NewId(),
			text = "&Nearest Point"
		);
		menu_resize.Append(self.menu_resize_near);
		self.menu_resize_linear = wx.MenuItem(
			menu_resize, id = wx.NewId(),
			text = "&Linear"
		);
		menu_resize.Append(self.menu_resize_linear);

		#add items to menu_help
		menu_about = wx.MenuItem(
			menu_help, id = wx.NewId(),
			text = "&About\tF1"
		);
		menu_help.Append(menu_about);

		#bind interaction events
		self.panel_base.Bind(wx.EVT_PAINT, self.on_panel_base_paint);
		self.Bind(wx.EVT_MENU, self.on_open, id = menu_open.GetId());
		#self.Bind(wx.EVT_MENU, self.on_save, id = menu_save.GetId());
		self.Bind(wx.EVT_MENU, self.on_resize, id = self.menu_resize_near.GetId());
		self.Bind(wx.EVT_MENU, self.on_resize, id = self.menu_resize_linear.GetId());
		self.Bind(wx.EVT_MENU, self.on_equalize, id = menu_equalize.GetId());
		self.Bind(wx.EVT_MENU, self.on_power, id = menu_power.GetId());
		self.Bind(wx.EVT_MENU, self.on_blur, id = menu_blur.GetId());
		self.Bind(wx.EVT_MENU, self.on_sharpen, id = menu_sharpen.GetId());
		self.Bind(wx.EVT_MENU, self.on_laplacian, id = menu_laplacian.GetId());
		self.Bind(wx.EVT_MENU, self.on_about, id = menu_about.GetId());

		#show the frame
		self.frame.Show(True);

		self.path = None;
		self.img = None;

	def on_quit(self, event):
		self.frame.Close();

	def on_about(self, event):
		wx.MessageBox("Digital Image Processing Library\nBy Rick", "About");

	def do_paint(self, dc):
		if not (self.img is None):
			dc.DrawBitmap(self.img, 0, 0);

	def on_panel_base_paint(self, event):
		dc = wx.ClientDC(self.panel_base);
		self.do_paint(dc);

	def on_open(self, event):
		dialog = wx.FileDialog(self.frame, message = "Open File", defaultDir = "../img/", wildcard = "Image Files(*.bmp;*.jpg;*.jpeg;*.png)|*.bmp;*.jpg;*.jpeg;*.png", style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST);
		if dialog.ShowModal() == wx.ID_OK:
			self.path = dialog.GetPath();
			self.img = wx.Bitmap(self.path);
			dc = wx.ClientDC(self.panel_base);
			self.do_paint(dc);

	def on_resize(self, event):
		if self.img is None:
			return;

		dialog = wx.TextEntryDialog(self.frame, message = "Please input the height of the image.", caption = "Resize", value = str(self.img.GetHeight()));
		if dialog.ShowModal() == wx.ID_OK:
			height = int(dialog.GetValue());
			if height <= 0:
				return;
		else:
			return;
		dialog = wx.TextEntryDialog(self.frame, message = "Please input the width of the image.", caption = "Resize", value = str(self.img.GetWidth()));
		if dialog.ShowModal() == wx.ID_OK:
			width = int(dialog.GetValue());
			if width <= 0:
				return;
		else:
			return;

		data = img2numpy(self.img);

		result = np.empty((height, width, data.shape[2]), dtype = np.int32);

		if event.GetId() == self.menu_resize_near.GetId():
			for i in range(data.shape[2]):
				result[:, :, i] = jpeg.resize_near(data[:, :, i].copy(), height, width);
		elif event.GetId() == self.menu_resize_linear.GetId():
			for i in range(data.shape[2]):
				result[:, :, i] = jpeg.resize_linear(data[:, :, i].copy(), height, width);
		else:
			return;

		self.img = numpy2img(result);
		dc = wx.ClientDC(self.panel_base);
		self.do_paint(dc);

	def on_equalize(self, event):
		if self.img is None:
			return;

		data = img2numpy(self.img);

		result = np.empty(data.shape, dtype = np.int32);

		for i in range(data.shape[2]):
			result[:, :, i] = jpeg.equalize(data[:, :, i].copy());

		self.img = numpy2img(result);
		dc = wx.ClientDC(self.panel_base);
		self.do_paint(dc);

	def on_power(self, event):
		if self.img is None:
			return;

		dialog = wx.TextEntryDialog(self.frame, message = "Please input the power.", caption = "Power Law", value = str(0.65));
		if dialog.ShowModal() == wx.ID_OK:
			gamma = float(dialog.GetValue());
		else:
			return;

		data = img2numpy(self.img);

		result = np.empty(data.shape, dtype = np.int32);

		for i in range(data.shape[2]):
			result[:, :, i] = jpeg.power_law(data[:, :, i].copy(), gamma);

		self.img = numpy2img(result);
		dc = wx.ClientDC(self.panel_base);
		self.do_paint(dc);

	def on_blur(self, event):
		if self.img is None:
			return;

		dialog = wx.TextEntryDialog(self.frame, message = "Please input the kernel size.", caption = "Blur", value = str(5));
		if dialog.ShowModal() == wx.ID_OK:
			kernel_size = int(dialog.GetValue());
			if kernel_size <= 0:
				return;
		else:
			return;

		data = img2numpy(self.img);
		kernel = np.array([[min([i + 1, j + 1, kernel_size - i, kernel_size - j]) for j in range(kernel_size)] for i in range(kernel_size)], dtype = np.float64);
		kernel /= np.sum(kernel);

		shape = [i for i in data.shape];
		shape[0] += kernel_size - 1;
		shape[1] += kernel_size - 1;
		result = np.empty(shape, dtype = np.float64);

		for i in range(data.shape[2]):
			result[:, :, i] = jpeg.correlate2(data[:, :, i].astype(np.float64), kernel);

		self.img = numpy2img(result);
		dc = wx.ClientDC(self.panel_base);
		self.do_paint(dc);

	def on_sharpen(self, event):
		if self.img is None:
			return;

		dialog = wx.TextEntryDialog(self.frame, message = "Please input the coefficient of laplacian.", caption = "Power Law", value = str(-0.65));
		if dialog.ShowModal() == wx.ID_OK:
			alpha = float(dialog.GetValue());
		else:
			return;

		data = img2numpy(self.img);

		result = np.empty(data.shape, dtype = np.int32);

		for i in range(data.shape[2]):
			result[:, :, i] = jpeg.laplacian(data[:, :, i].copy());
		result = data + result * alpha;
		result[result > 255] = 255;
		result[result < 0] = 0;

		self.img = numpy2img(result);
		dc = wx.ClientDC(self.panel_base);
		self.do_paint(dc);

	def on_laplacian(self, event):
		if self.img is None:
			return;

		data = img2numpy(self.img);

		result = np.empty(data.shape, dtype = np.int32);

		for i in range(data.shape[2]):
			result[:, :, i] = jpeg.laplacian(data[:, :, i].copy());
		result += np.min(result);
		#result[result > 255] = 255;
		#result[result < 0] = 0;
		#result = result.astype(np.float64) * 255 / np.max(result);

		self.img = numpy2img(result);
		dc = wx.ClientDC(self.panel_base);
		self.do_paint(dc);

if __name__ == "__main__":
	app = dipl_app(False);
	app.MainLoop();
