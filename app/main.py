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
import numpy as np;

from net_mnist import *;
from WideResNet import *;
from net_signs import *;
sys.path.append("../python");
import dipl;

def img2numpy(wximg):
	buf = wximg.GetDataBuffer();
	data = np.array(buf, dtype = np.int32);
	data = data.reshape((wximg.GetHeight(), wximg.GetWidth(), -1));
	if wximg.HasAlpha():
		buf = wximg.GetAlpha();
		alpha = np.array(buf, dtype = np.int32);
		alpha = alpha.reshape((wximg.GetHeight(), wximg.GetWidth()));
	else:
		alpha = np.empty((wximg.GetHeight(), wximg.GetWidth()), dtype = np.int32);
		alpha[:] = 255;
	return data, alpha;

def bitmap2numpy(wximg):
	img = wximg.ConvertToImage();
	buf = img.GetDataBuffer();
	data = np.array(buf, dtype = np.int32);
	data = data.reshape((img.GetHeight(), img.GetWidth(), -1));
	return data;

def numpy2img(data, alpha):
	buf = data.ravel().astype(np.uint8).tobytes();
	buf_alpha = alpha.ravel().astype(np.uint8).tobytes();
	wximg = wx.Image(data.shape[1], data.shape[0], buf, buf_alpha);
	return wximg;

def numpy2bitmap(data):
	buf = data.ravel().astype(np.uint8).tobytes();
	wximg = wx.Image(data.shape[1], data.shape[0], buf).ConvertToBitmap();
	return wximg;

class dimage:
	def __init__(self, panel = None, data = None, alpha = None):
		self.data = data;
		self.alpha = alpha;
		self.pos = np.array([0, 0], dtype = np.int32);
		self.scale = np.array([1, 1], dtype = np.float64);
		self.panel = panel;
		self.backup = [];
		self.record = [];

	def copy(self):
		img = dimage(self.panel, self.data.copy(), self.alpha.copy());
		return img;

	def push(self):
		if not self.data is None:
			self.record = [];
			self.backup.append((self.data, self.alpha));

	def pop(self):
		self.data, self.alpha = self.backup.pop();

	def undo(self):
		if len(self.backup) != 0:
			self.record.append((self.data, self.alpha));
			self.pop();

	def redo(self):
		if len(self.record) != 0:
			self.backup.append((self.data, self.alpha));
			self.data, self.alpha = self.record.pop();

	def create(self, size):
		self.backup = [];
		self.record = [];
		self.data = np.empty(size, dtype = np.int32);
		self.data[:] = 255;
		self.alpha = np.empty(size[:2], dtype = np.int32);
		self.alpha[:] = 255;

	def load(self, filename):
		self.backup = [];
		self.record = [];
		self.data, self.alpha = img2numpy(wx.Image(filename));

	def save(self, filename):
		numpy2img(self.data, self.alpha).SaveFile(filename);

	def origin(self):
		self.pos = np.array([0, 0], dtype = np.int32);
		self.scale = np.array([1, 1], dtype = np.float64);

	def view(self):
		zero = np.array([0, 0]);
		size = np.array(self.panel.GetSize())[::-1];
		shape = np.array(self.data.shape);

		pos = self.pos.astype(np.int32);
		pos1 = np.maximum(zero, pos);
		pos2 = np.minimum(size, np.floor(shape[:2] * self.scale + pos).astype(np.int32));

		shape[:2] = pos2 - pos1;
		if (shape[:2] <= zero).any():
			return;
		pos = np.minimum(pos, np.array([0, 0]));

		data = dipl.map_linear3(self.data, int(shape[0]), int(shape[1]), int(pos[0]), int(pos[1]), self.scale[0]);
		alpha = dipl.map_linear(self.alpha, int(shape[0]), int(shape[1]), int(pos[0]), int(pos[1]), self.scale[0]);

		img = dimage(self.panel, data, alpha);
		img.move(pos1);
		return img;

	def display(self):
		dc = wx.ClientDC(self.panel);

		zero = np.array([0, 0]);
		size = np.array(self.panel.GetSize())[::-1];
		shape = np.array(self.data.shape);

		pos = self.pos.astype(np.int32);
		pos1 = np.maximum(zero, pos);
		pos2 = np.minimum(size, np.floor(shape[:2] * self.scale + pos).astype(np.int32));

		shape[:2] = pos2 - pos1;
		if (shape[:2] <= zero).any():
			return;
		pos = np.minimum(pos, np.array([0, 0]));

		if self.scale[0] == 1:
			data = self.data[pos[0]: pos[0] + shape[0], pos[1]: pos[1] + shape[1], :];
			alpha = self.alpha[pos[0]: pos[0] + shape[0], pos[1]: pos[1] + shape[1]];
		else:
			data = dipl.map_linear3(self.data, int(shape[0]), int(shape[1]), int(pos[0]), int(pos[1]), self.scale[0]);
			alpha = dipl.map_linear(self.alpha, int(shape[0]), int(shape[1]), int(pos[0]), int(pos[1]), self.scale[0]);
		alpha = (alpha / 255).reshape(shape[0], shape[1], 1);
		data = data * alpha + self.panel.data_background[pos1[0]: pos2[0], pos1[1]: pos2[1]] * (1 - alpha);
		dc.DrawBitmap(numpy2bitmap(data), pos1[1], pos1[0]);

		self.panel.display_select();

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

		img = numpy2bitmap(np.tile(self.alpha.reshape(self.alpha.shape[0], self.alpha.shape[1], 1), (1, 1, 3)));
		dc = wx.MemoryDC();
		dc.SelectObject(img);
		dc.SetPen(wx.Pen(wx.WHITE, self.panel.thick));
		if len(pos_list) > 1:
			dc.DrawLines(pos_list);
		else:
			dc.DrawPoint(pos_list[0]);
		self.alpha = bitmap2numpy(img)[:, :, 0].copy();

	def erase_lines(self, pos_list, thick = None):
		self.push();
		pos_list = [i[::-1] for i in pos_list];

		img = numpy2bitmap(np.tile(self.alpha.reshape(self.alpha.shape[0], self.alpha.shape[1], 1), (1, 1, 3)));
		dc = wx.MemoryDC();
		dc.SelectObject(img);
		if thick is None:
			dc.SetPen(wx.Pen(wx.BLACK, self.panel.thick));
		else:
			dc.SetPen(wx.Pen(wx.BLACK, thick));
		if len(pos_list) > 1:
			dc.DrawLines(pos_list);
		else:
			dc.DrawPoint(pos_list[0]);
		self.alpha = bitmap2numpy(img)[:, :, 0].copy();

	def trim(self):
		pos1 = self.panel.pos_select1;
		pos2 = self.panel.pos_select2;
		if pos1 is None or pos2 is None:
			return;
		self.push();
		pos1, pos2 = np.minimum(pos1, pos2), np.maximum(pos1, pos2);
		pos1 = np.floor((pos1 - self.pos) / self.scale);
		pos2 = np.floor((pos2 - self.pos) / self.scale);
		shape = self.data.shape[:2];
		pos1 = np.maximum(pos1, (0, 0));
		pos2 = np.minimum(pos2, shape);
		self.data = self.data[int(pos1[0]): int(pos2[0]), int(pos1[1]): int(pos2[1]), :].copy();
		self.alpha = self.alpha[int(pos1[0]): int(pos2[0]), int(pos1[1]): int(pos2[1])].copy();
		self.pos += (pos1 * self.scale).astype(np.int32);
		self.panel.pos_select1 = None;
		self.panel.pos_select2 = None;

	def resize_near(self, size):
		self.push();
		result = np.empty((size[0], size[1], self.data.shape[2]), dtype = np.int32);
		for i in range(self.data.shape[2]):
			result[:, :, i] = dipl.resize_near(self.data[:, :, i].copy(), int(size[0]), int(size[1])); 
		self.data = result;
		self.alpha = dipl.resize_near(self.alpha, int(size[0]), int(size[1]));

	def resize_linear(self, size):
		self.push();
		result = np.empty((size[0], size[1], self.data.shape[2]), dtype = np.int32);
		for i in range(self.data.shape[2]):
			result[:, :, i] = dipl.resize_linear(self.data[:, :, i].copy(), int(size[0]), int(size[1]));
		self.data = result;
		self.alpha = dipl.resize_linear(self.alpha, int(size[0]), int(size[1]));

	def equalize(self):
		self.push();
		result = np.empty(self.data.shape, dtype = np.int32);
		for i in range(self.data.shape[2]):
			result[:, :, i] = dipl.equalize(self.data[:, :, i].copy());
		self.data = result;

	def power_law(self, gamma):
		self.push();
		result = np.empty(self.data.shape, dtype = np.int32);
		for i in range(self.data.shape[2]):
			result[:, :, i] = dipl.power_law(self.data[:, :, i].copy(), gamma);
		self.data = result;

	def correlate(self, kernel):
		self.push();
		shape = [i for i in self.data.shape];
		shape[0] += kernel.shape[0] - 1;
		shape[1] += kernel.shape[1] - 1;
		result = np.empty(shape, dtype = np.float64);
		for i in range(self.data.shape[2]):
			result[:, :, i] = dipl.correlate2(self.data[:, :, i].astype(np.float64), kernel);
		result[result > 255] = 255;
		result[result < 0] = 0;
		result = result.astype(np.int32);
		shape2 = (np.array(kernel.shape) - 1) // 2;
		shape3 = (np.array(kernel.shape) - 1) - shape2;
#		result_next = np.empty((shape[0] - shape2[0], shape[1] - shape2[1], shape[2]));
#		for i in range(self.data.shape[2]):
#			result_next[:, :, i] = dipl.trim(result[:, :, i].copy(), int(shape3[0]), int(shape2[0]), int(shape3[1]), int(shape2[1]));
		self.data = result[shape3[0]: -shape2[0], shape3[1]: -shape2[1]].copy();

	def sharpen(self, alpha):
		self.push();
		result = np.empty(self.data.shape, dtype = np.int32);
		for i in range(self.data.shape[2]):
			result[:, :, i] = dipl.laplacian(self.data[:, :, i].copy());
		result = self.data + result * alpha;
		result[result > 255] = 255;
		result[result < 0] = 0;
		result = result.astype(np.int32);
		self.data = result;

	def laplacian(self):
		self.push();
		result = np.empty(self.data.shape, dtype = np.int32);
		for i in range(self.data.shape[2]):
			result[:, :, i] = dipl.laplacian(self.data[:, :, i].copy());
		result -= np.min(result);
		result = result.astype(np.float64) * 255 / max(np.max(result), 1);
		result = result.astype(np.int32);
		self.data = result;

	def noise_guass(self, variance):
		self.push();
		self.data = self.data.copy();
		for i in range(self.data.shape[2]):
			data = self.data[:, :, i].copy();
			dipl.noise_guass(data, variance);
			self.data[:, :, i] = data;
		self.data[self.data < 0] = 0;
		self.data[self.data > 255] = 255;

	def noise_salt(self, probability, value):
		self.push();
		self.data = self.data.copy();
		for i in range(self.data.shape[2]):
			data = self.data[:, :, i].copy();
			dipl.noise_salt(data, probability, value);
			self.data[:, :, i] = data;
		self.data[self.data < 0] = 0;
		self.data[self.data > 255] = 255;

	def filter_median(self, kernel_size):
		self.push();
		result = np.empty(self.data.shape, dtype = np.int32);
		for i in range(self.data.shape[2]):
			result[:, :, i] = dipl.filter_median(self.data[:, :, i].copy(), kernel_size);
		self.data = result;

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

class panel_draw(wx.Panel):

	def __init__(self, parent, size = wx.DefaultSize):
		super(panel_draw, self).__init__(parent = parent, size = size);
		self.frame = parent;
		while type(self.frame) != dipl_frame:
			self.frame = self.frame.GetParent();
		self.SetBackgroundColour(wx.BLACK);

		self.SetCursor(self.frame.icon_normal);

		self.Bind(wx.EVT_PAINT, self.on_paint);
		self.Bind(wx.EVT_LEFT_UP, self.on_leftup);
		self.Bind(wx.EVT_MOTION, self.on_motion);
		self.Bind(wx.EVT_LEFT_DOWN, self.on_leftdown);

		self.path = None;
		self.img = None;
		self.cache = None;
		self.pos_select1 = None;
		self.pos_select2 = None;

		self.flag_down = False;
		self.thick = 5;
		self.color = wx.Colour(0, 0, 0);
		self.pos = (0, 0);
		self.pos_img = (0, 0);

		self.s_normal = 0;
		self.s_grab = 1;
		self.s_pencil = 2;
		self.s_eraser = 3;
		self.s_picker = 4;
		self.s_selector = 5;
		self.s_zoom_in = 6;
		self.s_zoom_out = 7;
		self.status = self.s_normal;

		screen_w = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X) // 8 + 1;
		screen_h = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y) // 8 + 1;

		data = np.array([[[20], [100]],[[100], [20]]]);
		data = data.repeat(3, 2).repeat(8, 0).repeat(8, 1);
		data = np.tile(data, (screen_h, screen_w, 1));
		self.data_background = data;
		self.img_background = numpy2bitmap(data);

	def clear(self):
		dc = wx.ClientDC(self);
		
		if self.img is None:
			dc.DrawBitmap(self.img_background, (0, 0));
		else:
			sw, sh = self.GetSize();
			h = self.img.pos[0] + m.floor(self.img.data.shape[0] * self.img.scale[0]); 
			w = self.img.pos[1] + m.floor(self.img.data.shape[1] * self.img.scale[1]);
			dc.SetClippingRegion(0, 0, self.img.pos[1], sh);
			dc.DrawBitmap(self.img_background, (0, 0));
			dc.DestroyClippingRegion();
			dc.SetClippingRegion(0, 0, sw, self.img.pos[0]);
			dc.DrawBitmap(self.img_background, (0, 0));
			dc.DestroyClippingRegion();
			dc.SetClippingRegion(w, 0, sw - w, sh);
			dc.DrawBitmap(self.img_background, (0, 0));
			dc.DestroyClippingRegion();
			dc.SetClippingRegion(0, h, sw, sh - h);
			dc.DrawBitmap(self.img_background, (0, 0));

	def display_select(self):
		if self.pos_select1 is None or self.pos_select2 is None:
			return;
		dc = wx.ClientDC(self);
		dc.SetBrush(wx.Brush(wx.TransparentColour));
		dc.SetPen(wx.Pen(wx.WHITE, 2));
		dc.DrawRectangle(self.pos_select1[::-1], (self.pos_select2 - self.pos_select1)[::-1]);
		dc.SetPen(wx.Pen(wx.BLACK, 2, wx.SHORT_DASH));
		dc.DrawRectangle(self.pos_select1[::-1], (self.pos_select2 - self.pos_select1)[::-1]);

	def new_image(self, size):
		assert(size[0] > 0 and size[1] > 0);
		if self.img is None:
			self.img = dimage(panel = self);
		else:
			self.img.origin();
		self.img.create([size[0], size[1], 3]);
		self.clear();
		self.img.display();
		self.frame.SetStatusText(str(self.img.scale[0]), 1);

	def open_image(self, path):
		self.path = path;
		if self.img is None:
			self.img = dimage(panel = self);
		else:
			self.img.origin();
		self.img.load(self.path);
		self.clear();
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
		elif status == self.s_eraser:
			self.SetCursor(self.frame.icon_eraser);
		elif status == self.s_picker:
			self.SetCursor(self.frame.icon_picker);
		elif status == self.s_selector:
			self.SetCursor(self.frame.icon_selector);
		elif status == self.s_zoom_in:
			self.SetCursor(self.frame.icon_zoom_in);
		elif status == self.s_zoom_out:
			self.SetCursor(self.frame.icon_zoom_out);

	def on_paint(self, event):
		self.clear();
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
		elif self.status == self.s_eraser:
			pos = np.array(event.GetPosition())[::-1];
			pos_img = (pos - self.img.pos) / self.img.scale;
			self.pos = pos;
			self.pos_list = [pos_img];
			self.cache = self.img.view();
		elif self.status == self.s_selector:
			pos = np.array(event.GetPosition())[::-1];
			self.pos_select1 = pos;
			self.pos_select2 = None;
			self.cache = self.img.view();

	def on_motion(self, event):
		if self.img is None:
			return;

		pos = np.array(event.GetPosition())[::-1];
		pos_img = np.floor((pos - self.img.pos) / self.img.scale);
		self.frame.SetStatusText("(%d,%d)->(%d,%d)" % (pos_img[1], pos_img[0], pos[1], pos[0]), 2);

		if self.flag_down:
			if self.status == self.s_pencil:
				dc = wx.ClientDC(self);
				dc.SetClippingRegion(
					self.img.pos[1], self.img.pos[0],
					m.floor(self.img.data.shape[1] * self.img.scale[0]),
					m.floor(self.img.data.shape[0] * self.img.scale[0])
				);
				dc.SetPen(wx.Pen(self.color, self.thick * self.img.scale[0]));
				dc.DrawLine(self.pos[::-1], pos[::-1]);
				self.pos_list.append(pos_img);
			elif self.status == self.s_eraser:
				self.pos_list.append(pos_img);
				self.cache.erase_lines(
					[self.pos - self.cache.pos, pos - self.cache.pos],
					thick = self.thick * self.img.scale[0]
				);
				self.cache.display();
			elif self.status == self.s_grab:
				self.img.move((np.array(pos) - np.array(self.pos)));
				self.clear();
				self.img.display();
			elif self.status == self.s_selector:
				self.pos_select2 = pos;
				self.clear();
				self.cache.display();

		self.pos = pos;
		self.pos_img = pos_img;

	def on_leftup(self, event):
		self.flag_down = False;

		if self.img is None:
			return;

		if self.status == self.s_grab:
			self.SetCursor(self.frame.icon_grab);
		if self.status == self.s_zoom_in:
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
			self.img.display();
		elif self.status == self.s_eraser:
			self.img.erase_lines(self.pos_list);
			self.img.display();

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
		self.frame.execute(self.text_input.GetValue());

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

		self.s_normal = 0;
		self.s_grab = 1;
		self.s_pencil = 2;
		self.s_eraser = 3;
		self.s_picker = 4;
		self.s_selector = 5;
		self.s_zoom_in = 6;
		self.s_zoom_out = 7;

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

	def execute(self, script):
		frame = self;
		class io_term:
			def write(self, text):
				frame.print_term(text);
		buf = io_term();
		out_save = sys.stdout;
		sys.stdout = buf;
		try:
			exec(script);
			sys.stdout = out_save;
		except:
			traceback.print_exc(limit = 10, file = buf);
		finally:
			sys.stdout = out_save;

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
		if dialog.ShowModal() == wx.ID_OK:
			self.panel_draw.open_image(dialog.GetPath());
		self.path_image = dialog.GetDirectory();
		dialog.Destroy();

	def on_save(self, event):
		if self.panel_draw.img is None:
			return;
		if not hasattr(self, "path_image"):
			self.path_image = "../img/";
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
		if dialog.ShowModal() == wx.ID_OK:
			self.panel_draw.save_image(dialog.GetPath());
		self.path_image = dialog.GetDirectory();
		dialog.Destroy();

	def on_script(self, event):
		if not hasattr(self, "path_script"):
			self.path_script = "../sample/";
		dialog = wx.FileDialog(self, message = "Load Python Script", defaultDir = self.path_script, wildcard = "Python Scripts(*.py)|*.py", style = wx.FD_OPEN);
		if dialog.ShowModal() == wx.ID_OK:
			with open(dialog.GetPath()) as fobj:
				script = fobj.read();
			self.execute(script);
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

	def on_selector(self, event):
		self.panel_draw.set_status(self.panel_draw.s_selector);

	def on_trim(self, event):
		if (
			self.panel_draw.img is None
			or self.panel_draw.pos_select1 is None
			or self.panel_draw.pos_select2 is None
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
