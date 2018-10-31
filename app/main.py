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
		shape = np.array(self.data.shape);
		shape[:2] = (shape[:2] * self.scale).astype(shape.dtype);
		data = np.empty(shape, dtype = np.int32);
		for i in range(shape[2]):
			data[:,:,i] = jpeg.resize_near(self.data[:, :, i].copy(), int(shape[0]), int(shape[1]));
		dc.DrawBitmap(numpy2img(data), self.pos[1], self.pos[0]);

	def move(self, distance):
		self.pos += distance;

	def rescale(self, pos, scale):
		np_pos = np.array(pos);
		np_scale = np.array(scale);
		self.pos = (np_pos + np_scale * (self.pos - np_pos)).astype(np.int32);
		self.scale *= np_scale;

	def zoom_fit(self, size):
		print(self.data.shape, size);
		h = self.data.shape[0];
		w = self.data.shape[1];
		(sh, sw) = size;
		if h * sw > w * sh:
			self.scale = np.array((sh / h));
			self.pos = np.array((0, (sw - sh * w / h) / 2), dtype = np.int32);
		else:
			self.scale = np.array((sw / w));
			self.pos = np.array(((sh - sw * h / w) / 2, 0), dtype = np.int32);
		#self.pos = self.pos[::-1];
		print(self.pos, self.scale)

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
		self.panel_base.SetBackgroundColour(wx.Colour(50,50,50));
		sizer_base.Add(self.panel_base, 1, wx.ALL | wx.EXPAND,5);
		sizer_main = wx.BoxSizer(wx.VERTICAL);
		self.panel_base.SetSizer(sizer_main);

		#create a panel to hold toolbars
		panel_tool = wx.Panel(self.panel_base);
		panel_tool.SetBackgroundColour(wx.Colour(240,240,240));
		sizer_main.Add(panel_tool, 0, wx.ALL | wx.EXPAND,5);
		sizer_tool = wx.BoxSizer(wx.HORIZONTAL);
		panel_tool.SetSizer(sizer_tool);

		#create a toolbar
		tool_mouse = wx.ToolBar(panel_tool, style = wx.TB_FLAT | wx.TB_NODIVIDER);
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

		self.id_zoom_fit = wx.NewId();
		tool_mouse.AddTool(
			self.id_zoom_fit, "zoom_fit", wx.Bitmap("../icon/square_box.png"), shortHelp = "zoom fit"
		);
		self.Bind(wx.EVT_TOOL, self.on_zoom_fit, id = self.id_zoom_fit);

		tool_mouse.AddSeparator();
		tool_mouse.Realize();
		sizer_tool.Add(tool_mouse, 0, wx.ALL | wx.EXPAND, 5);

		#create a toolbar
		tool_transform = wx.ToolBar(panel_tool, style = wx.TB_FLAT | wx.TB_NODIVIDER);
		self.choice_transform = wx.Choice(
			tool_transform, wx.NewId(), choices = [
				"Resize Image (Nearest Point)",
				"Resize Image (Bilinear)",
				"Histogram Equalization",
				"Power Law",
				"Blur Image",
				"Sharpen Image",
				"Laplacian"
			],
			size=(180,-1)
		);
		self.choice_transform.SetSelection(0);
		self.choice_transform.Bind(wx.EVT_CHOICE, self.on_choice_transform);
		tool_transform.AddControl(self.choice_transform);

		self.text_input_info1 = wx.StaticText(tool_transform, label = " height:");
		tool_transform.AddControl(self.text_input_info1);
		self.text_input1 = wx.TextCtrl(tool_transform, value = "300");
		tool_transform.AddControl(self.text_input1);
		self.text_input_info2 = wx.StaticText(tool_transform, label = " width:");
		tool_transform.AddControl(self.text_input_info2);
		self.text_input2 = wx.TextCtrl(tool_transform, value = "400");
		tool_transform.AddControl(self.text_input2);

		self.id_tool_run = wx.NewId();
		tool_transform.AddTool(
			self.id_tool_run, "transform", wx.Bitmap("../icon/right_arrow.png"), shortHelp = "transform"
		);

		tool_transform.AddSeparator();
		tool_transform.Realize();
		sizer_tool.Add(tool_transform, 0, wx.ALL | wx.EXPAND, 5);

		#create a panel to draw pictures
		self.panel_draw = wx.Panel(self.panel_base);
		self.panel_draw.SetBackgroundColour(wx.BLACK);
		sizer_main.Add(self.panel_draw, 1, wx.ALL | wx.EXPAND, 5);
		self.panel_draw.flag_down = False;
		self.panel_draw.pos = (0, 0);
		self.panel_draw.Bind(wx.EVT_PAINT, self.on_panel_draw_paint);
		self.panel_draw.Bind(wx.EVT_LEFT_DOWN, self.on_panel_draw_leftdown);
		self.panel_draw.Bind(wx.EVT_LEFT_UP, self.on_panel_draw_leftup);
		self.panel_draw.Bind(wx.EVT_MOTION, self.on_panel_draw_motion);

		#show the frame
		self.Show(True);

		self.path = None;
		self.img = None;

		self.s_normal = 0;
		self.s_grab = 1;
		self.s_pencil = 2;
		self.s_zoom_in = 3;
		self.s_zoom_out = 4;
		self.status = self.s_normal;

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
			self.img = dimage();
			self.img.load(self.path);
			self.img.display(wx.ClientDC(self.panel_draw));
		dialog.Destroy();

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
		self.status = self.s_normal;
		self.panel_draw.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT));

	def on_grab(self, event):
		self.status = self.s_grab;
		self.panel_draw.SetCursor(wx.Cursor(self.icon_grab.ConvertToImage()));

	def on_pencil(self, event):
		self.status = self.s_pencil;
		self.panel_draw.SetCursor(wx.Cursor(wx.CURSOR_PENCIL));

	def on_zoom_in(self, event):
		self.status = self.s_zoom_in;
		self.panel_draw.SetCursor(wx.Cursor(self.icon_zoom_in.ConvertToImage()));

	def on_zoom_out(self, event):
		self.status = self.s_zoom_out;
		self.panel_draw.SetCursor(wx.Cursor(self.icon_zoom_out.ConvertToImage()));

	def on_zoom_fit(self, event):
		if self.img is None:
			return;
		self.img.zoom_fit(np.array(self.panel_draw.GetSize())[::-1]);
		dc = wx.ClientDC(self.panel_draw);
		dc.Clear();
		self.img.display(dc);

	def on_panel_draw_leftdown(self, event):
		self.panel_draw.flag_down = True;
		if self.img is None:
			return;
		if self.status == self.s_grab:
			self.panel_draw.SetCursor(wx.Cursor(self.icon_grabbing.ConvertToImage()));

	def on_panel_draw_motion(self, event):
		if self.img is None:
			return;
		if self.panel_draw.flag_down:
			if self.status == self.s_pencil:
				dc = wx.ClientDC(self.panel_draw);
				dc.SetBrush(wx.BLACK_BRUSH);
				dc.SetPen(wx.Pen(wx.BLACK, 10));
				dc.DrawLine(event.GetPosition(), self.panel_draw.pos);
			elif self.status == self.s_grab:
				self.img.move((np.array(event.GetPosition()) - np.array(self.panel_draw.pos))[::-1]);
				self.img.display(wx.ClientDC(self.panel_draw));
		self.panel_draw.pos = event.GetPosition();

	def on_panel_draw_leftup(self, event):
		self.panel_draw.flag_down = False;
		if self.img is None:
			return;
		if self.status == self.s_grab:
			self.panel_draw.SetCursor(wx.Cursor(self.icon_grab.ConvertToImage()));
			dc = wx.ClientDC(self.panel_draw);
			dc.Clear();
			self.img.display(dc);
		elif self.status == self.s_zoom_in:
			self.img.rescale(np.array(event.GetPosition())[::-1], 1.2);
			dc = wx.ClientDC(self.panel_draw);
			dc.Clear();
			self.img.display(dc);
		elif self.status == self.s_zoom_out:
			self.img.rescale(np.array(event.GetPosition())[::-1], 0.8);
			dc = wx.ClientDC(self.panel_draw);
			dc.Clear();
			self.img.display(dc);

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
			if not (self.img is None):
				self.text_input1.SetValue(str(self.img.data.shape[0]));
				self.text_input2.SetValue(str(self.img.data.shape[1]));
			else:
				self.text_input1.SetValue(str(300));
				self.text_input2.SetValue(str(400));
			return;
		else:
			num += 2;

		if sel == num:
			self.text_input_info1.Hide();
			self.text_input_info2.Hide();
			self.text_input1.Hide();
			self.text_input2.Hide();
			return;
		else:
			num += 1;

		if sel == num:
			self.text_input_info1.Show();
			self.text_input_info2.Hide();
			self.text_input_info1.SetLabel(" gamma:");
			self.text_input1.Show();
			self.text_input2.Hide();
			self.text_input1.SetValue(str(0.65));
			return;
		else:
			num += 1;

		if sel == num:
			self.text_input_info1.Show();
			self.text_input_info2.Hide();
			self.text_input_info1.SetLabel(" kernel size:");
			self.text_input1.Show();
			self.text_input2.Hide();
			self.text_input1.SetValue(str(3));
			return;
		else:
			num += 1;

		if sel == num:
			self.text_input_info1.Show();
			self.text_input_info2.Hide();
			self.text_input_info1.SetLabel(" alpha:");
			self.text_input1.Show();
			self.text_input2.Hide();
			self.text_input1.SetValue(str(-0.65));
			return;
		else:
			num += 1;

		if sel == num:
			self.text_input_info1.Hide();
			self.text_input_info2.Hide();
			self.text_input1.Hide();
			self.text_input2.Hide();
			return;
		else:
			num += 1;

	def on_transform():
		pass;

class dipl_app(wx.App):

	#overload the initializer
	def OnInit(self):
		self.frame = dipl_frame(None, title = "Digital Image Processing", size = (900, 650));
		return True;

if __name__ == "__main__":
	app = dipl_app(False);
	app.MainLoop();
