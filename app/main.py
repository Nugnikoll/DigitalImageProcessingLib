# -*- coding: utf-8 -*-

import wx;
import sys;
import os;
import time;
from matplotlib import pyplot as plt;
from PIL import Image as image;
import numpy as np;
from wx.lib import sized_controls

sys.path.append("../python");
import jpeg;

def img2numpy(wximg):
	buf = wximg.GetDataBuffer();
	data = np.frombuffer(buf, dtype="uint8");
	data = data.reshape((wximg.GetHeight(), wximg.GetWidth(), -1));
	data = data.astype(np.int32);
	return data;

def bitmap2numpy(wximg):
	img = wximg.ConvertToImage();
	buf = img.GetDataBuffer();
	data = np.frombuffer(buf, dtype="uint8");
	data = data.reshape((img.GetHeight(), img.GetWidth(), -1));
	data = data.astype(np.int32);
	return data;

def numpy2img(data):
	buf = data.ravel().astype(np.uint8).tobytes();
	wximg = wx.Image(data.shape[1], data.shape[0], buf);
	return wximg;

def numpy2bitmap(data):
	buf = data.ravel().astype(np.uint8).tobytes();
	wximg = wx.Image(data.shape[1], data.shape[0], buf).ConvertToBitmap();
	return wximg;

class dimage:
	def __init__(self, data = None, panel = None):
		self.data = data;
		self.pos = np.array([0, 0], dtype = np.int32);
		self.scale = np.array([1, 1], dtype = np.float64);
		self.panel = panel;

	def create(self, size):
		self.data = np.empty(size, dtype = np.int32);
		self.data[:] = 255;

	def load(self, filename):
		self.data = img2numpy(wx.Image(filename));

	def save(self, filename):
		numpy2img(self.data).SaveFile(filename);

	def display(self):
		dc = wx.ClientDC(self.panel);
		size = np.array(self.panel.GetSize())[::-1];

		shape = np.array(self.data.shape);
		pos1 = np.maximum(np.floor(-self.pos / self.scale).astype(np.int32), np.array([0, 0]));
		pos2 = np.minimum(np.ceil((size - self.pos) / self.scale).astype(np.int32), shape[:2]);
		#print(self.scale);
		#print("pos1", pos1, "pos2", pos2);
		if (pos2 - pos1 <= 0).any():
			return;

#		pos3 = np.minimum(np.array([0, 0]), self.pos.astype(np.int32));
#		pos4 = np.minimum(size, np.ceil(shape[:2] * self.scale + self.pos));

#		pos3 = np.minimum(np.array([0, 0]), self.pos.astype(np.int32));
#		pos4 = np.ceil((pos2 - pos1) * self.scale) + pos3;

		pos3 = np.floor(pos1 * self.scale + self.pos).astype(np.int32);
		pos4 = np.ceil(pos2 * self.scale + self.pos).astype(np.int32);

		#print("pos3", pos3, "pos4", pos4);
		shape2 = shape;
		shape2[:2] = pos4 - pos3;

		data = np.empty(shape2, dtype = np.int32);
		for i in range(shape[2]):
			data[:, :, i] = jpeg.resize_near(self.data[pos1[0]: pos2[0], pos1[1]: pos2[1], i].copy(), int(shape2[0]), int(shape2[1]));
		dc.DrawBitmap(numpy2bitmap(data), pos3[1], pos3[0]);
		

	def move(self, distance):
		self.pos += distance;

	def rescale(self, pos, scale):
		np_pos = np.array(pos);
		np_scale = np.array(scale);
		self.pos = (np_pos + np_scale * (self.pos - np_pos)).astype(np.int32);
		self.scale *= np_scale;

	def zoom_fit(self, size):
		h = self.data.shape[0];
		w = self.data.shape[1];
		(sh, sw) = size;
		if h * sw > w * sh:
			self.scale = np.array([sh / h, sh / h]);
			self.pos = np.array((0, (sw - sh * w / h) / 2), dtype = np.int32);
		else:
			self.scale = np.array([sw / w, sw / w]);
			self.pos = np.array(((sh - sw * h / w) / 2, 0), dtype = np.int32);

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

	def correlate(self, kernel):
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

class dialog_new(wx.Dialog):

	def __init__(self, parent, title = "", size = (250, 150)):
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

		#self.Fit();


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
#		menu_edit = wx.Menu();
#		self.menubar.Append(menu_edit, "&Edit");
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
		sizer_base.Add(self.panel_base, 1, wx.ALL | wx.EXPAND, 0);
		sizer_main = wx.BoxSizer(wx.VERTICAL);
		self.panel_base.SetSizer(sizer_main);

		#create a panel to hold toolbars
		panel_tool = wx.Panel(self.panel_base);
		panel_tool.SetBackgroundColour(wx.Colour(240,240,240));
		sizer_main.Add(panel_tool, 0, wx.ALL | wx.EXPAND, 5);
		sizer_tool = wx.BoxSizer(wx.HORIZONTAL);
		panel_tool.SetSizer(sizer_tool);

		#create a toolbar
		tool_mouse = wx.ToolBar(panel_tool, style = wx.TB_FLAT | wx.TB_NODIVIDER);

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

		self.id_tool_picker = wx.NewId();
		self.icon_picker = wx.Bitmap("../icon/picker.png");
		tool_mouse.AddTool(
			self.id_tool_picker, "picker", self.icon_picker, shortHelp = "picker"
		);
		self.Bind(wx.EVT_TOOL, self.on_picker, id = self.id_tool_picker);

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

		self.color_pick = np.array((0, 0, 0));
		self.button_color = wx.Button(tool_mouse, size = wx.Size(10,10), style = wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL);
		self.button_color.SetBackgroundColour(wx.Colour(self.color_pick));
		tool_mouse.AddControl(self.button_color);

		tool_mouse.AddSeparator();
		tool_mouse.Realize();
		sizer_tool.Add(tool_mouse, 0, wx.ALL | wx.EXPAND, 1);

		#create a toolbar
		tool_transform = wx.ToolBar(panel_tool, style = wx.TB_FLAT | wx.TB_NODIVIDER);

		self.choice_transform = wx.Choice(
			tool_transform, wx.NewId(), choices = [
				"Set Color",
				"Resize Image (Nearest Point)",
				"Resize Image (Bilinear)",
				"Histogram Equalization",
				"Power Law",
				"Blur Image",
				"Sharpen Image",
				"Laplacian"
			],
			size = (180,-1)
		);
		self.choice_transform.SetSelection(0);
		self.choice_transform.Bind(wx.EVT_CHOICE, self.on_choice_transform);
		tool_transform.AddControl(self.choice_transform);

		self.text_input_info1 = wx.StaticText(tool_transform, label = " red:");
		tool_transform.AddControl(self.text_input_info1);
		self.text_input1 = wx.TextCtrl(tool_transform, value = "0");
		tool_transform.AddControl(self.text_input1);
		self.text_input_info2 = wx.StaticText(tool_transform, label = " green:");
		tool_transform.AddControl(self.text_input_info2);
		self.text_input2 = wx.TextCtrl(tool_transform, value = "0");
		tool_transform.AddControl(self.text_input2);
		self.text_input_info3 = wx.StaticText(tool_transform, label = " blue:");
		tool_transform.AddControl(self.text_input_info3);
		self.text_input3 = wx.TextCtrl(tool_transform, value = "0");
		tool_transform.AddControl(self.text_input3);

		self.id_tool_run = wx.NewId();
		tool_transform.AddTool(
			self.id_tool_run, "transform", wx.Bitmap("../icon/right_arrow.png"), shortHelp = "transform"
		);
		self.Bind(wx.EVT_TOOL, self.on_transform, id = self.id_tool_run);

		tool_transform.AddSeparator();
		tool_transform.Realize();
		sizer_tool.Add(tool_transform, 0, wx.ALL | wx.EXPAND, 1);

		#create a panel to draw pictures
		self.panel_draw = wx.Panel(self.panel_base);
		self.panel_draw.SetBackgroundColour(wx.BLACK);
		sizer_main.Add(self.panel_draw, 1, wx.ALL | wx.EXPAND, 5);
		self.panel_draw.flag_down = False;
		self.panel_draw.thick = 5;
		self.panel_draw.color = wx.Colour(0, 0, 0);
		self.panel_draw.pos = (0, 0);
		self.panel_draw.pos_img = (0, 0);
		self.panel_draw.Bind(wx.EVT_PAINT, self.on_panel_draw_paint);
		self.panel_draw.Bind(wx.EVT_LEFT_DOWN, self.on_panel_draw_leftdown);
		self.panel_draw.Bind(wx.EVT_LEFT_UP, self.on_panel_draw_leftup);
		self.panel_draw.Bind(wx.EVT_MOTION, self.on_panel_draw_motion);

		#add a status bar
		self.status_bar = wx.StatusBar(self, wx.NewId());
		self.status_bar.SetFieldsCount(3);
		self.status_bar.SetStatusWidths([-1, -1, -1]);
		self.SetStatusBar(self.status_bar);

		#show the frame
		self.Show(True);

		self.path = None;
		self.img = None;

		self.s_normal = 0;
		self.s_grab = 1;
		self.s_pencil = 2;
		self.s_picker = 3;
		self.s_zoom_in = 4;
		self.s_zoom_out = 5;
		self.status = self.s_normal;

	def on_quit(self, event):
		self.Close();

	def on_about(self, event):
		wx.MessageBox("Digital Image Processing Library\nBy Rick", "About");

	def on_panel_draw_paint(self, event):
		if not (self.img is None):
			self.img.display();

	def on_new(self, event):
		dialog = dialog_new(self);
		if dialog.ShowModal() == wx.ID_OK:
			height = int(dialog.text_height.GetValue());
			width = int(dialog.text_width.GetValue());
			if height > 0 and width > 0:
				self.img = dimage(panel = self.panel_draw);
				self.img.create([height, width, 3]);
				self.img.display();
				self.SetStatusText(str(self.img.scale[0]), 1);
		dialog.Destroy();

	def on_open(self, event):
		dialog = wx.FileDialog(self, message = "Open File", defaultDir = "../img/", wildcard = "Image Files(*.bmp;*.jpg;*.jpeg;*.png;*.tiff;*.xpm)|*.bmp;*.jpg;*.jpeg;*.png;*.tiff;*.xpm", style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST);
		if dialog.ShowModal() == wx.ID_OK:
			self.path = dialog.GetPath();
			self.img = dimage(panel = self.panel_draw);
			self.img.load(self.path);
			self.img.display();
			self.SetStatusText(str(self.img.scale[0]), 1);
		dialog.Destroy();

	def on_save(self, event):
		if self.img is None:
			return;
		dialog = wx.FileDialog(self, message = "Save File", defaultDir = "../img/", wildcard = "Image Files(*.bmp;*.jpg;*.jpeg;*.png;*.tiff;*.xpm)|*.bmp;*.jpg;*.jpeg;*.png;*.tiff;*.xpm", style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT);
		if dialog.ShowModal() == wx.ID_OK:
			self.path = dialog.GetPath();
			self.img.save(self.path);
		dialog.Destroy();

	def on_normal(self, event):
		self.status = self.s_normal;
		self.panel_draw.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT));

	def on_grab(self, event):
		self.status = self.s_grab;
		self.panel_draw.SetCursor(wx.Cursor(self.icon_grab.ConvertToImage()));

	def on_pencil(self, event):
		self.status = self.s_pencil;
		self.panel_draw.SetCursor(wx.Cursor(wx.CURSOR_PENCIL));

	def on_picker(self, event):
		self.status = self.s_picker;
		#self.panel_draw.SetCursor(wx.Cursor(self.icon_picker.ConvertToImage()));
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
		self.SetStatusText(str(self.img.scale[0]), 1);
		dc = wx.ClientDC(self.panel_draw);
		dc.Clear();
		self.img.display();

	def on_panel_draw_leftdown(self, event):
		self.panel_draw.flag_down = True;
		if self.img is None:
			return;
		if self.status == self.s_grab:
			self.panel_draw.SetCursor(wx.Cursor(self.icon_grabbing.ConvertToImage()));
		elif self.status == self.s_picker:
			pos1 = np.array(event.GetPosition())[::-1];
			pos2 = (pos1 - self.img.pos) / self.img.scale;
			pos2 = pos2.astype(np.int32);
			if pos2[0] >= 0 and pos2[0] < self.img.data.shape[0] and pos2[1] >= 0 and pos2[1] < self.img.data.shape[1]:
				color = self.img.data[pos2[0], pos2[1], :];
				self.panel_draw.color = wx.Colour(color);
				self.button_color.SetBackgroundColour(self.panel_draw.color);
				self.SetStatusText(str(color), 0);

	def on_panel_draw_motion(self, event):
		if self.img is None:
			return;

		pos = np.array(event.GetPosition())[::-1];
		pos_img = (pos - self.img.pos) / self.img.scale;
		self.SetStatusText("(%d,%d)->(%d,%d)" % (pos_img[1], pos_img[0], pos[1], pos[0]), 2);

		if self.panel_draw.flag_down:
			if self.status == self.s_pencil:
				img = numpy2bitmap(self.img.data);
				dc = wx.MemoryDC();
				dc.SelectObject(img);
				dc.SetPen(wx.Pen(self.panel_draw.color, self.panel_draw.thick));
				dc.DrawLine(self.panel_draw.pos_img[::-1], pos_img[::-1]);
				self.img.data = bitmap2numpy(img);
				self.img.display();
			elif self.status == self.s_grab:
				self.img.move((np.array(pos) - np.array(self.panel_draw.pos)));
				self.img.display();
		self.panel_draw.pos = pos;
		self.panel_draw.pos_img = pos_img;

	def on_panel_draw_leftup(self, event):
		self.panel_draw.flag_down = False;

		if self.img is None:
			return;

		if self.status == self.s_grab:
			self.panel_draw.SetCursor(wx.Cursor(self.icon_grab.ConvertToImage()));
			dc = wx.ClientDC(self.panel_draw);
			dc.Clear();
			self.img.display();
		elif self.status == self.s_zoom_in:
			if self.img.scale[0] > 450:
				return;
			self.img.rescale(np.array(event.GetPosition())[::-1], 1.2);
			self.SetStatusText(str(self.img.scale[0]), 1);
			dc = wx.ClientDC(self.panel_draw);
			dc.Clear();
			self.img.display();
		elif self.status == self.s_zoom_out:
			if self.img.scale[0] < 1e-5:
				return;
			self.img.rescale(np.array(event.GetPosition())[::-1], 1/1.2);
			self.SetStatusText(str(self.img.scale[0]), 1);
			dc = wx.ClientDC(self.panel_draw);
			dc.Clear();
			self.img.display();

	def on_choice_transform(self, event):
		sel = self.choice_transform.GetCurrentSelection();
		num = 0;

		if sel == num:
			self.text_input_info1.Show();
			self.text_input_info1.SetLabel(" red:");
			self.text_input1.Show();
			self.text_input1.SetValue(str(self.panel_draw.color.red));
			self.text_input_info2.Show();
			self.text_input_info2.SetLabel(" green:");
			self.text_input2.Show();
			self.text_input2.SetValue(str(self.panel_draw.color.green));
			self.text_input_info3.Show();
			self.text_input_info3.SetLabel(" blue:");
			self.text_input3.Show();
			self.text_input3.SetValue(str(self.panel_draw.color.blue));
			return;
		num += 1;

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

	def on_transform(self, event):
		if self.img is None:
			return;

		sel = self.choice_transform.GetCurrentSelection();
		num = 0;

		if sel == num:
			red = int(self.text_input1.GetValue());
			green = int(self.text_input2.GetValue());
			blue = int(self.text_input3.GetValue()); 
			if red < 0 or red > 255 or green < 0 or green > 255 or blue < 0 or blue > 255:
				return;
			self.panel_draw.color = wx.Colour(red, green, blue);
			self.button_color.SetBackgroundColour(self.panel_draw.color);
			return;
		num += 1;

		if sel == num:
			height = int(self.text_input1.GetValue());
			width = int(self.text_input2.GetValue());
			if height <= 0 or width <= 0:
				return;
			self.img.resize_near(np.array((height, width)));
			dc = wx.ClientDC(self.panel_draw);
			dc.Clear();
			self.img.display();
			return;
		num += 1;

		if sel == num:
			height = int(self.text_input1.GetValue());
			width = int(self.text_input2.GetValue());
			if height <= 0 or width <= 0:
				return;
			self.img.resize_linear(np.array((height, width)));
			dc = wx.ClientDC(self.panel_draw);
			dc.Clear();
			self.img.display();
			return;
		num += 1;

		if sel == num:
			self.img.equalize();
			self.img.display();
			return;
		num += 1;

		if sel == num:
			gamma = float(self.text_input1.GetValue());
			if gamma <= 0:
				return;
			self.img.power_law(gamma);
			self.img.display();
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
			self.img.correlate(kernel);
			self.img.display();
			return;
		num += 1;

		if sel == num:
			alpha = float(self.text_input1.GetValue());
			self.img.sharpen(alpha);
			self.img.display();
			return;
		num += 1;

		if sel == num:
			self.img.laplacian();
			self.img.display();
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
