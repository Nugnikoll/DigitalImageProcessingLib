# -*- coding: utf-8 -*-

import wx;
import wx.aui as aui;
import sys;
import os;
import time;
import copy;
import math as m;
from matplotlib import pyplot as plt;
from PIL import Image as image;
import numpy as np;

from nn import *;
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
		self.backup = [];
		self.record = [];

	def copy(self):
		img = dimage(self.data.copy(), self.panel);
		return img;

	def push(self):
		if not self.data is None:
			self.record = [];
			self.backup.append(self.data);

	def pop(self):
		self.data = self.backup.pop();

	def undo(self):
		if len(self.backup) != 0:
			self.record.append(self.data);
			self.pop();

	def redo(self):
		if len(self.record) != 0:
			self.backup.append(self.data);
			self.data = self.record.pop();

	def create(self, size):
		self.push();
		self.data = np.empty(size, dtype = np.int32);
		self.data[:] = 255;

	def load(self, filename):
		self.push();
		self.data = img2numpy(wx.Image(filename));

	def save(self, filename):
		numpy2img(self.data).SaveFile(filename);

	def origin(self):
		self.pos = np.array([0, 0], dtype = np.int32);
		self.scale = np.array([1, 1], dtype = np.float64);

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

	def draw_lines(self, pos_list):
		self.push();
		pos_list = [i[::-1] for i in pos_list];
		img = numpy2bitmap(self.data);
		dc = wx.MemoryDC();
		dc.SelectObject(img);
		dc.SetPen(wx.Pen(self.panel.color, self.panel.thick));
		if len(pos_list) > 1:
			dc.DrawLines(pos_list);
		else:
			dc.DrawPoint(pos_list[0]);
		self.data = bitmap2numpy(img);

	def resize_near(self, size):
		self.push();
		result = np.empty((size[0], size[1], self.data.shape[2]), dtype = np.int32);
		for i in range(self.data.shape[2]):
			result[:, :, i] = jpeg.resize_near(self.data[:, :, i].copy(), int(size[0]), int(size[1]));
		self.data = result;

	def resize_linear(self, size):
		self.push();
		result = np.empty((size[0], size[1], self.data.shape[2]), dtype = np.int32);
		for i in range(self.data.shape[2]):
			result[:, :, i] = jpeg.resize_linear(self.data[:, :, i].copy(), int(size[0]), int(size[1]));
		self.data = result;

	def equalize(self):
		self.push();
		result = np.empty(self.data.shape, dtype = np.int32);
		for i in range(self.data.shape[2]):
			result[:, :, i] = jpeg.equalize(self.data[:, :, i].copy());
		self.data = result;

	def power_law(self, gamma):
		self.push();
		result = np.empty(self.data.shape, dtype = np.int32);
		for i in range(self.data.shape[2]):
			result[:, :, i] = jpeg.power_law(self.data[:, :, i].copy(), gamma);
		self.data = result;

	def correlate(self, kernel):
		self.push();
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
		self.push();
		result = np.empty(self.data.shape, dtype = np.int32);
		for i in range(self.data.shape[2]):
			result[:, :, i] = jpeg.laplacian(self.data[:, :, i].copy());
		result = self.data + result * alpha;
		result[result > 255] = 255;
		result[result < 0] = 0;
		result = result.astype(np.int32);
		self.data = result;

	def laplacian(self):
		self.push();
		result = np.empty(self.data.shape, dtype = np.int32);
		for i in range(self.data.shape[2]):
			result[:, :, i] = jpeg.laplacian(self.data[:, :, i].copy());
		result -= np.min(result);
		result = result.astype(np.float64) * 255 / max(np.max(result), 1);
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

class panel_draw(wx.Panel):

	def __init__(self, parent, size = wx.DefaultSize):
		super(panel_draw, self).__init__(parent = parent, size = size);
		self.frame = parent;
		while type(self.frame) != dipl_frame:
			self.frame = self.frame.GetParent();
		self.SetBackgroundColour(wx.BLACK);

		self.Bind(wx.EVT_PAINT, self.on_paint);
		self.Bind(wx.EVT_LEFT_DOWN, self.on_leftdown);
		self.Bind(wx.EVT_LEFT_UP, self.on_leftup);
		self.Bind(wx.EVT_MOTION, self.on_motion);

		self.path = None;
		self.img = None;

		self.flag_down = False;
		self.thick = 5;
		self.color = wx.Colour(0, 0, 0);
		self.pos = (0, 0);
		self.pos_img = (0, 0);

		self.s_normal = 0;
		self.s_grab = 1;
		self.s_pencil = 2;
		self.s_picker = 3;
		self.s_zoom_in = 4;
		self.s_zoom_out = 5;
		self.status = self.s_normal;

	def clear(self):
		dc = wx.ClientDC(self);
		dc.Clear();

	def new_image(self, size):
		assert(size[0] > 0 and size[1] > 0);
		if self.img is None:
			self.img = dimage(panel = self);
		else:
			self.img.origin();
		self.img.create([size[0], size[1], 3]);
		self.img.display();
		self.frame.SetStatusText(str(self.img.scale[0]), 1);

	def open_image(self, path):
		self.path = path;
		if self.img is None:
			self.img = dimage(panel = self);
		else:
			self.img.origin();
		self.img.load(self.path);
		self.img.display();
		self.frame.SetStatusText(str(self.img.scale[0]), 1);

	def save_image(self, path):
		self.path = path;
		self.img.save(self.path);

	def set_status(self, status):
		self.status = status;
		if status == self.s_normal:
			#self.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT));
			self.SetCursor(self.frame.icon_normal);
		elif status == self.s_grab:
			self.SetCursor(self.frame.icon_grab);
		elif status == self.s_pencil:
			#self.SetCursor(wx.Cursor(wx.CURSOR_PENCIL));
			self.SetCursor(self.frame.icon_pencil);
		elif status == self.s_picker:
			self.SetCursor(self.frame.icon_picker);
		elif status == self.s_zoom_in:
			self.SetCursor(self.frame.icon_zoom_in);
		elif status == self.s_zoom_out:
			self.SetCursor(self.frame.icon_zoom_out);

	def on_paint(self, event):
		if not (self.img is None):
			self.img.display();

	def on_leftdown(self, event):
		self.flag_down = True;
		if self.img is None:
			return;
		if self.status == self.s_grab:
			self.SetCursor(self.frame.icon_grabbing);
		elif self.status == self.s_picker:
			pos1 = np.array(event.GetPosition())[::-1];
			pos2 = (pos1 - self.img.pos) / self.img.scale;
			pos2 = pos2.astype(np.int32);
			if pos2[0] >= 0 and pos2[0] < self.img.data.shape[0] and pos2[1] >= 0 and pos2[1] < self.img.data.shape[1]:
				color = self.img.data[pos2[0], pos2[1], :];
				self.color = wx.Colour(color);
				self.frame.button_color.SetBackgroundColour(self.color);
				self.frame.SetStatusText(str(color), 0);
		elif self.status == self.s_pencil:
			pos = np.array(event.GetPosition())[::-1];
			pos_img = (pos - self.img.pos) / self.img.scale;
			self.pos_list = [pos_img];

	def on_motion(self, event):
		if self.img is None:
			return;

		pos = np.array(event.GetPosition())[::-1];
		pos_img = (pos - self.img.pos) / self.img.scale;
		self.frame.SetStatusText("(%d,%d)->(%d,%d)" % (pos_img[1], pos_img[0], pos[1], pos[0]), 2);

		if self.flag_down:
			if self.status == self.s_pencil:
				img = numpy2bitmap(self.img.data);
				dc = wx.ClientDC(self);
				dc.SetClippingRegion(
					self.img.pos[1], self.img.pos[0],
					m.ceil(self.img.data.shape[1] * self.img.scale[0]),
					m.ceil(self.img.data.shape[0] * self.img.scale[0])
				);
				dc.SetPen(wx.Pen(self.color, self.thick * self.img.scale[0]));
				dc.DrawLine(self.pos[::-1], pos[::-1]);
				self.pos_list.append(pos_img);
			elif self.status == self.s_grab:
				self.img.move((np.array(pos) - np.array(self.pos)));
				self.img.display();
		self.pos = pos;
		self.pos_img = pos_img;

	def on_leftup(self, event):
		self.flag_down = False;

		if self.img is None:
			return;

		if self.status == self.s_grab:
			self.SetCursor(self.frame.icon_grab);
			self.clear();
			self.img.display();
		elif self.status == self.s_zoom_in:
			if self.img.scale[0] > 450:
				return;
			self.img.rescale(np.array(event.GetPosition())[::-1], 1.2);
			self.frame.SetStatusText(str(self.img.scale[0]), 1);
			self.clear();
			self.img.display();
		elif self.status == self.s_zoom_out:
			if self.img.scale[0] < 1e-5:
				return;
			self.img.rescale(np.array(event.GetPosition())[::-1], 1/1.2);
			self.frame.SetStatusText(str(self.img.scale[0]), 1);
			self.clear();
			self.img.display();
		elif self.status == self.s_pencil:
			self.img.draw_lines(self.pos_list);
			self.img.display()

class dipl_frame(wx.Frame):
	def __init__(self, parent, id = -1, title = "", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_FRAME_STYLE | wx.SUNKEN_BORDER | wx.CLIP_CHILDREN):
		wx.Frame.__init__(self, parent, id, title, pos, size, style);

		font_text = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName = "consolas");
		self.SetFont(font_text)

		#set the icon of the frame
#		frame_icon = wx.Icon();
#		frame_icon.CopyFromBitmap(wx.Bitmap(wx.Image("../img/")));
#		self.SetIcon(frame_icon);

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

		#add items to menu_help
		menu_about = wx.MenuItem(
			menu_help, id = wx.NewId(),
			text = "&About\tF1"
		);
		self.Bind(wx.EVT_MENU, self.on_about, id = menu_about.GetId());
		menu_help.Append(menu_about);

		#create a toolbar
		tool_transform = wx.ToolBar(self, size = wx.DefaultSize, style = wx.TB_FLAT | wx.TB_NODIVIDER);
		tool_transform.SetToolBitmapSize(wx.Size(40,40));

		self.choice_transform = wx.Choice(
			tool_transform, wx.NewId(), choices = [
				"Resize Image (Nearest Point)",
				"Resize Image (Bilinear)",
				"Histogram Equalization",
				"Power Law",
				"Blur Image",
				"Sharpen Image",
				"Laplacian",
				"MNIST CNN classification"
			],
			size = (180,-1)
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
		self.text_input_info3 = wx.StaticText(tool_transform);
		tool_transform.AddControl(self.text_input_info3);
		self.text_input3 = wx.TextCtrl(tool_transform);
		tool_transform.AddControl(self.text_input3);

		self.text_input_info3.Hide();
		self.text_input3.Hide();

		self.id_tool_run = wx.NewId();
		tool_transform.AddTool(
			self.id_tool_run, "transform", wx.Bitmap("../icon/right_arrow.png"), shortHelp = "transform"
		);
		self.Bind(wx.EVT_TOOL, self.on_transform, id = self.id_tool_run);

		tool_transform.Realize();
		self.manager.AddPane(
			tool_transform, aui.AuiPaneInfo().
			Name("tool_transform").Caption("tool transform").
			ToolbarPane().Top().Row(1).
			LeftDockable(False).RightDockable(False).
			TopDockable(True).BottomDockable(False)
		);

		#create a toolbar
		tool_mouse = wx.ToolBar(self, size = wx.DefaultSize, style = wx.TB_FLAT | wx.TB_NODIVIDER);
		tool_mouse.SetToolBitmapSize(wx.Size(40,40));

		self.id_tool_normal = wx.NewId();
		self.icon_normal = wx.Image("../icon/default.png");
		tool_mouse.AddTool(
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
		tool_mouse.AddTool(
			self.id_tool_grab, "grab", self.icon_grab.ConvertToBitmap(), shortHelp = "grab"
		);
		self.icon_grab = wx.Cursor(self.icon_grab);
		self.icon_grabbing = wx.Cursor(self.icon_grabbing);
		self.Bind(wx.EVT_TOOL, self.on_grab, id = self.id_tool_grab);

		self.id_zoom_in = wx.NewId();
		self.icon_zoom_in = wx.Image("../icon/zoom-in.png");
		self.icon_zoom_in.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 10);
		self.icon_zoom_in.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 9);
		tool_mouse.AddTool(
			self.id_zoom_in, "zoom_in", self.icon_zoom_in.ConvertToBitmap(), shortHelp = "zoom in"
		);
		self.icon_zoom_in = wx.Cursor(self.icon_zoom_in);
		self.Bind(wx.EVT_TOOL, self.on_zoom_in, id = self.id_zoom_in);

		self.id_zoom_out = wx.NewId();
		self.icon_zoom_out = wx.Image("../icon/zoom-out.png");
		self.icon_zoom_out.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 10);
		self.icon_zoom_out.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 9);
		tool_mouse.AddTool(
			self.id_zoom_out, "zoom_out", self.icon_zoom_out.ConvertToBitmap(), shortHelp = "zoom out"
		);
		self.icon_zoom_out = wx.Cursor(self.icon_zoom_out);
		self.Bind(wx.EVT_TOOL, self.on_zoom_out, id = self.id_zoom_out);

		self.id_zoom_fit = wx.NewId();
		tool_mouse.AddTool(
			self.id_zoom_fit, "zoom_fit", wx.Bitmap("../icon/square_box.png"), shortHelp = "zoom fit"
		);
		self.Bind(wx.EVT_TOOL, self.on_zoom_fit, id = self.id_zoom_fit);

		tool_mouse.Realize();
		self.manager.AddPane(
			tool_mouse, aui.AuiPaneInfo().
			Name("tool_mouse").Caption("tool mouse").
			ToolbarPane().Top().Row(1).
			LeftDockable(False).RightDockable(False).
			TopDockable(True).BottomDockable(False)
		);

		#create a toolbar
		tool_draw = wx.ToolBar(self, size = wx.DefaultSize, style = wx.TB_FLAT | wx.TB_NODIVIDER | wx.TB_VERTICAL);
		tool_draw.SetToolBitmapSize(wx.Size(40,40));

		self.button_color = wx.Button(tool_draw, size = wx.Size(10,10), style = wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL);
		self.button_color.SetBackgroundColour(wx.Colour((0, 0, 0)));
		self.button_color.Bind(wx.EVT_BUTTON, self.on_color_pick);
		tool_draw.AddControl(self.button_color);

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

		self.id_tool_picker = wx.NewId();
		self.icon_picker = wx.Image("../icon/picker.png");
		self.icon_picker.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 5);
		self.icon_picker.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 19);
		tool_draw.AddTool(
			self.id_tool_picker, "picker", self.icon_picker.ConvertToBitmap(), shortHelp = "picker"
		);
		self.icon_picker = wx.Cursor(self.icon_picker);
		self.Bind(wx.EVT_TOOL, self.on_picker, id = self.id_tool_picker);

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

		#add a status bar
		self.status_bar = wx.StatusBar(self, wx.NewId());
		self.status_bar.SetFieldsCount(3);
		self.status_bar.SetStatusWidths([-1, -1, -1]);
		self.SetStatusBar(self.status_bar);

		#show the frame
		self.manager.Update()
		self.Show(True);

		self.s_normal = 0;
		self.s_grab = 1;
		self.s_pencil = 2;
		self.s_picker = 3;
		self.s_zoom_in = 4;
		self.s_zoom_out = 5;
		self.status = self.s_normal;

		self.net = cnn();
		with open("cnn.dat", "rb") as fobj:
			param = pickle.load(fobj);
		self.net.load_state_dict(param);

	def Destroy(self):
		self.manager.UnInit();
		del self.manager;
		return super(dipl_frame, self).Destroy();

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
		dialog = wx.FileDialog(self, message = "Open File", defaultDir = "../img/", wildcard = "Image Files(*.bmp;*.jpg;*.jpeg;*.png;*.tiff;*.xpm)|*.bmp;*.jpg;*.jpeg;*.png;*.tiff;*.xpm", style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST);
		if dialog.ShowModal() == wx.ID_OK:
			self.panel_draw.open_image(dialog.GetPath());
		dialog.Destroy();

	def on_save(self, event):
		if self.panel_draw.img is None:
			return;
		dialog = wx.FileDialog(self, message = "Save File", defaultDir = "../img/", wildcard = "Image Files(*.bmp;*.jpg;*.jpeg;*.png;*.tiff;*.xpm)|*.bmp;*.jpg;*.jpeg;*.png;*.tiff;*.xpm", style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT);
		if dialog.ShowModal() == wx.ID_OK:
			self.panel_draw.save_image(dialog.GetPath());
		dialog.Destroy();

	def on_script(self, event):
		dialog = wx.FileDialog(self, message = "Load Python Script", defaultDir = "../", wildcard = "Python Scripts(*.py)|*.py", style = wx.FD_OPEN);
		if dialog.ShowModal() == wx.ID_OK:
			with open(dialog.GetPath()) as fobj:
				script = fobj.read();
			try:
				exec(script);
			except:
				info = sys.exc_info();
				print("File \"%s\", line %d, column %d" % (info[1].args[1][0], info[1].args[1][1], info[1].args[1][2]));
				print("    " + info[1].args[1][3])
				print(info[1].args[0]);
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

	def on_normal(self, event):
		self.panel_draw.set_status(self.panel_draw.s_normal);

	def on_grab(self, event):
		self.panel_draw.set_status(self.panel_draw.s_grab);

	def on_pencil(self, event):
		self.panel_draw.set_status(self.panel_draw.s_pencil);

	def on_picker(self, event):
		self.panel_draw.set_status(self.panel_draw.s_picker);

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
		dialog.GetColourData().SetColour(self.panel_draw.color);
		if dialog.ShowModal() == wx.ID_OK:
			self.panel_draw.color = dialog.GetColourData().GetColour();
			self.button_color.SetBackgroundColour(self.panel_draw.color);

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
			img = self.panel_draw.img.copy();
			img.resize_linear((28, 28));
			data = 1 - (np.mean(img.data, axis = 2) / 255);
			data = data.reshape((1, 1, 28, 28));
			data = Variable(torch.Tensor(data));
			result = self.net(data).reshape(10);
			prob, result = result.max(dim = 0);
			self.text_input_info1.SetLabel(" number: %d probability: %.4f" % (result.data.item(), prob.data.item()));
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
