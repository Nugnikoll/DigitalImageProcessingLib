from __future__ import print_function;
import numpy as np;
import torch;
import torch.nn as nn;
import torch.nn.functional as fun;
from torch.autograd import Variable;

class net_mnist(nn.Module):
	def __init__(self):
		super(net_mnist, self).__init__()
		self.relu = nn.ReLU(inplace = True);
		self.bn1 = nn.BatchNorm2d(10);
		self.bn2 = nn.BatchNorm2d(20);
		self.bn3 = nn.BatchNorm1d(50);
		self.bn4 = nn.BatchNorm1d(10);
		self.conv1 = nn.Conv2d(1, 10, kernel_size = 5);
		self.conv2 = nn.Conv2d(10, 20, kernel_size = 5);
		self.fc1 = nn.Linear(320, 50);
		self.fc2 = nn.Linear(50, 10);

	def forward(self, x):
		x = self.conv1(x);
		x = fun.max_pool2d(x, 2);
		x = self.bn1(x);
		self.relu(x);
		x = self.conv2(x);
		x = fun.max_pool2d(x, 2);
		x = self.bn2(x);
		self.relu(x);
		x = x.view(-1, 320);
		x = self.fc1(x);
		x = self.bn3(x);
		self.relu(x);
		x = self.fc2(x);
		x = self.bn4(x);
		x = fun.log_softmax(x, dim = 1);
		return x;
