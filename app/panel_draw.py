import wx;
import math as m;
from scipy.ndimage import gaussian_filter1d;
from dimage import *;

class panel_draw(wx.Panel):

	def __init__(self, parent, size = wx.DefaultSize):
		super(panel_draw, self).__init__(parent = parent, size = size);
		self.frame = parent;
		self.SetBackgroundColour(wx.BLACK);

		self.SetCursor(self.frame.icon_normal);

		self.Bind(wx.EVT_PAINT, self.on_paint);
		self.Bind(wx.EVT_LEFT_UP, self.on_leftup);
		self.Bind(wx.EVT_MOTION, self.on_motion);
		self.Bind(wx.EVT_LEFT_DOWN, self.on_leftdown);
		self.Bind(wx.EVT_RIGHT_DOWN, self.on_rightdown);

		self.path = None;
		self.img = None;
		self.cache = None;

		self.flag_down = False;
		self.thick = 5;
		self.color_pen = wx.Colour(0, 0, 0);
		self.color_brush = wx.Colour(0, 0, 0);
		self.pos = (0, 0);
		self.pos_list = None;

		self.s_normal = 0;
		self.s_grab = 1;
		self.s_pencil = 2;
		self.s_smooth = 3;
		self.s_eraser = 4;
		self.s_picker = 5;
		self.s_bucket = 6;
		self.s_selector = 7;
		self.s_draw = 8;
		self.s_zoom_in = 9;
		self.s_zoom_out = 10;
		self.status = self.s_normal;

		self.sd_line = 0;
		self.sd_rect = 1;
		self.sd_circle = 2;
		self.sd_curve = 3;
		self.status_draw = None;

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
		if(
			self.status != self.s_selector
			or self.pos_list is None
			or len(self.pos_list) < 2
		):
			return;
		pos1 = self.pos_list[0];
		pos2 = self.pos_list[1];
		if pos1 is None or pos2 is None:
			return;
		pos1 = pos1[::-1];
		pos2 = pos2[::-1];
		dc = wx.ClientDC(self);
		dc.SetBrush(wx.Brush(wx.TransparentColour));
		dc.SetPen(wx.Pen(wx.WHITE, 2));
		dc.DrawRectangle(pos1, pos2 - pos1);
		dc.SetPen(wx.Pen(wx.BLACK, 2, wx.SHORT_DASH));
		dc.DrawRectangle(pos1, pos2 - pos1);

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

	def set_status(self, status, status_draw = None):
		self.status = status;
		self.status_draw = status_draw;
		if status == self.s_normal:
			#self.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT));
			self.SetCursor(self.frame.icon_normal);
		elif status == self.s_grab:
			self.SetCursor(self.frame.icon_grab);
		elif status == self.s_pencil:
			#self.SetCursor(wx.Cursor(wx.CURSOR_PENCIL));
			self.SetCursor(self.frame.icon_pencil);
		elif status == self.s_smooth:
			self.SetCursor(self.frame.icon_pencil);
		elif status == self.s_eraser:
			self.SetCursor(self.frame.icon_eraser);
		elif status == self.s_picker:
			self.SetCursor(self.frame.icon_picker);
		elif status == self.s_bucket:
			self.SetCursor(self.frame.icon_bucket);
		elif status == self.s_selector:
			self.SetCursor(self.frame.icon_selector);
		elif status == self.s_draw:
			self.SetCursor(self.frame.icon_selector);
			self.pos_list = None;
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
				if self.frame.button_pick is self.frame.panel_style.button_color_pen:
					self.color_pen = wx.Colour(*color[:3], self.color_pen[3]);
					self.frame.button_pick.color = self.color_pen;
					self.frame.button_pick.display();
				else:
					self.color_brush = wx.Colour(*color[:3], self.color_brush[3]);
					self.frame.button_pick.color = self.color_brush;
					self.frame.button_pick.display();
				self.frame.SetStatusText(str(color), 0);
		elif self.status == self.s_pencil or self.status == self.s_smooth:
			pos = np.array(event.GetPosition())[::-1];
			pos_img = (pos - self.img.pos) / self.img.scale;
			self.pos_list = [pos_img];
		elif self.status == self.s_eraser:
			pos = np.array(event.GetPosition())[::-1];
			pos_img = (pos - self.img.pos) / self.img.scale;
			self.pos = pos;
			self.pos_list = [pos_img];
			self.cache = self.img.view();
		elif self.status == self.s_bucket:
			pos = np.array(event.GetPosition())[::-1];
			pos_img = (pos - self.img.pos) / self.img.scale;
			self.img.flood_fill(pos_img);
			self.img.display();
		elif self.status == self.s_selector:
			pos = np.array(event.GetPosition())[::-1];
			self.pos_list = [pos, None];
			self.cache = self.img.view();
		elif self.status == self.s_draw:
			pos = np.array(event.GetPosition())[::-1];
			if(
				self.status_draw == self.sd_line
				or self.status_draw == self.sd_rect
				or self.status_draw == self.sd_circle
			):
				if self.pos_list is None or len(self.pos_list) == 2:
					self.pos_list = [pos];
				else:
					self.pos_list.append(pos);
			elif(self.status_draw == self.sd_curve):
				if self.pos_list is None:
					self.pos_list = [pos];
				elif len(self.pos_list) <= 20:
					self.pos_list.append(pos);
			self.cache = self.img.view();

	def on_motion(self, event):
		if self.img is None:
			return;

		pos = np.array(event.GetPosition())[::-1];
		pos_img = np.floor((pos - self.img.pos) / self.img.scale);
		self.frame.SetStatusText("(%d,%d)->(%d,%d)" % (pos_img[1], pos_img[0], pos[1], pos[0]), 2);

		if self.flag_down:
			if self.status == self.s_pencil or self.status == self.s_smooth:
				dc = wx.ClientDC(self);
				dc.SetClippingRegion(
					self.img.pos[1], self.img.pos[0],
					m.floor(self.img.data.shape[1] * self.img.scale[0]),
					m.floor(self.img.data.shape[0] * self.img.scale[0])
				);
				dc.SetPen(wx.Pen(self.color_pen, self.thick * self.img.scale[0]));
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
				self.pos_list[1] = pos;
				self.clear();
				self.cache.display();

		if self.status == self.s_draw:
			if not self.pos_list is None:
				self.clear();
				self.cache.display();
				dc = wx.ClientDC(self);
				dc.SetPen(wx.Pen(self.color_pen, self.thick * self.img.scale[0]));
				dc.SetBrush(wx.Brush(self.color_brush));
				if self.status_draw == self.sd_line:
					if len(self.pos_list) == 1:
						dc.DrawLine(self.pos_list[0][::-1], pos[::-1]);
				elif self.status_draw == self.sd_rect:
					if len(self.pos_list) == 1:
						dc.DrawRectangle(self.pos_list[0][::-1], pos[::-1] - self.pos_list[0][::-1]);
				elif self.status_draw == self.sd_circle:
					if len(self.pos_list) == 1:
						radius = np.sum((self.pos_list[0] - pos) ** 2);
						radius = m.sqrt(float(radius));
						dc.DrawCircle(self.pos_list[0][::-1], radius);
				elif self.status_draw == self.sd_curve:
					pos_list = self.pos_list.copy();
					pos_list.append(pos);
					x = np.array([i[0] for i in pos_list], dtype = np.float64);
					y = np.array([i[1] for i in pos_list], dtype = np.float64);
					num = (len(pos_list) - 1) * 10;
					xx = dipl.bezier(x, num);
					yy = dipl.bezier(y, num);
					pos_list = [[yy[i], xx[i]] for i in range(len(xx))];
					dc.DrawLines(pos_list);
					pos_list = [[i[1], i[0]] for i in self.pos_list];
					dc.DrawPointList(pos_list);

		self.pos = pos;

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
		elif self.status == self.s_smooth:
			pos_list = self.pos_list.copy();
			pos_list = [pos_list[0]] + pos_list + [pos_list[-1]];
			x = np.array([i[0] for i in pos_list]);
			y = np.array([i[1] for i in pos_list]);
			xx = gaussian_filter1d(x, 3);
			yy = gaussian_filter1d(y, 3);
			pos_list = [pos_list[0]] + [[xx[i], yy[i]] for i in range(len(x))] + [pos_list[-1]];
			self.img.draw_lines(pos_list);
			self.img.display();
		elif self.status == self.s_eraser:
			self.img.erase_lines(self.pos_list);
			self.img.display();
		elif self.status == self.s_selector:
			self.clear();
			self.cache.display();

		elif self.status == self.s_draw:
			flag_display = False;
			if self.status_draw == self.sd_line:
				if not self.pos_list is None and len(self.pos_list) == 2:
					pos_list = [(i - self.img.pos) / self.img.scale for i in self.pos_list];
					self.img.draw_lines(pos_list);
					flag_display = True;
			elif self.status_draw == self.sd_circle:
				if not self.pos_list is None and len(self.pos_list) == 2:
					pos_list = [(i - self.img.pos) / self.img.scale for i in self.pos_list];
					radius = np.sum((pos_list[0] - pos_list[1]) ** 2);
					radius = m.sqrt(float(radius));
					self.img.draw_circle(pos_list[0], radius);
					flag_display = True;
			elif self.status_draw == self.sd_rect:
				if not self.pos_list is None and len(self.pos_list) == 2:
					pos_list = [(i - self.img.pos) / self.img.scale for i in self.pos_list];
					self.img.draw_rect(pos_list[0], pos_list[1]);
					flag_display = True;

			if flag_display:
				self.pos_list = None;
				self.clear();
				self.img.display();

	def on_rightdown(self, event):
		if self.img is None or self.pos_list is None:
			return;

		pos = np.array(event.GetPosition())[::-1];

		if self.status == self.s_draw:
			if self.status_draw == self.sd_curve:
				pos_list = self.pos_list;
				pos_list.append(pos);
				pos_list = [(i - self.img.pos) / self.img.scale for i in pos_list];
				x = np.array([i[0] for i in pos_list], dtype = np.float64);
				y = np.array([i[1] for i in pos_list], dtype = np.float64);
				num = (len(pos_list) - 1) * 10;
				xx = dipl.bezier(x, num);
				yy = dipl.bezier(y, num);
				pos_list = [[xx[i], yy[i]] for i in range(len(xx))];
				self.img.draw_lines(pos_list);
				self.pos_list = None;
				self.clear();
				self.img.display();
