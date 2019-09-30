import sys;
import os;
import wx;
import math as m;
import numpy as np;
import time;

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

def bezier(trace, t):
	n = len(trace);
	x = 0;
	for i in range(n):
		ii = n - i - 1;
		x += (
			trace[i] * t ** i * (1 - t) ** ii
			* (m.factorial(n - 1) // m.factorial(i) // m.factorial(ii))
		);
	return x;

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
		def nop():
			pass;
		img.push = nop;
		img.pop = nop;
		img.undo = nop;
		img.redo = nop;
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
			pos = -pos;
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

	def draw_lines(self, pos_list, thick = None):
		self.push();
		pos_list = [i[::-1] for i in pos_list];

		img = numpy2bitmap(self.data);
		dc = wx.MemoryDC();
		dc.SelectObject(img);
		if thick is None:
			dc.SetPen(wx.Pen(self.panel.color_pen, self.panel.thick));
		else:
			dc.SetPen(wx.Pen(self.panel.color_pen, thick));
		if len(pos_list) > 1:
			dc.DrawLines(pos_list);
		else:
			dc.DrawPoint(pos_list[0]);
		self.data = bitmap2numpy(img);

		img = numpy2bitmap(np.tile(self.alpha.reshape(self.alpha.shape[0], self.alpha.shape[1], 1), (1, 1, 3)));
		dc = wx.MemoryDC();
		dc.SelectObject(img);
		if thick is None:
			dc.SetPen(wx.Pen(wx.WHITE, self.panel.thick));
		else:
			dc.SetPen(wx.Pen(wx.WHITE, thick));
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
		if(
			self.panel.status != self.panel.s_selector
			or self.panel.pos_list is None
			or len(self.panel.pos_list) < 2
		):
			return;
		pos1 = self.panel.pos_list[0];
		pos2 = self.panel.pos_list[1];
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
		self.panel.pos_list = None;

	def flood_fill(self, pos, color):
		self.push();

		img = numpy2bitmap(self.data);
		dc = wx.MemoryDC();
		dc.SelectObject(img);
		dc.SetBrush(wx.Brush(self.panel.color_brush));
		dc.FloodFill(pos[::-1], self.data[int(pos[0]), int(pos[1])]);
		self.data = bitmap2numpy(img);

	def draw_circle(self, pos, radius, thick = None):
		self.push();

		img = numpy2bitmap(self.data);
		dc = wx.MemoryDC();
		dc.SelectObject(img);
		if thick is None:
			dc.SetPen(wx.Pen(self.panel.color_pen[:3], self.panel.thick));
		else:
			dc.SetPen(wx.Pen(self.panel.color_pen[:3], thick));
		dc.SetBrush(wx.Brush(self.panel.color_brush[:3]));
		dc.DrawCircle(pos[::-1], radius);
		self.data = bitmap2numpy(img);

		img = numpy2bitmap(np.tile(self.alpha.reshape(self.alpha.shape[0], self.alpha.shape[1], 1), (1, 1, 3)));
		dc = wx.MemoryDC();
		dc.SelectObject(img);
		if thick is None:
			dc.SetPen(wx.Pen(wx.WHITE, self.panel.thick));
		else:
			dc.SetPen(wx.Pen(wx.WHITE, thick));
		color = wx.Colour((self.panel.color_brush[3]) * 3);
		dc.SetBrush(wx.Brush(color));
		dc.DrawCircle(pos[::-1], radius);
		self.alpha = bitmap2numpy(img)[:, :, 0].copy();

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
