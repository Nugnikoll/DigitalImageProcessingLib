#include "jpeg.h"

int seg_base::load(const string& data, jpeg_decoder& jdecoder){
	mkr = marker(uint16_t((data.at(0) << 8) | data.at(1)));
	return 0;
}

void seg_base::print()const{
	cout << hex << setfill('0')
		<< setw(2) << (mkr >> 8) << ' '
		<< setw(2) << (mkr & 0xff) << ' ';

	switch(mkr){
	case m_soi:
		cout << "start of image\n";
		break;
	case m_eoi:
		cout << "end of image\n";
		break;
	default:
		cout << "unrecognized marker\n"
		;
	}
}

int seg_frame::load(const string& data, jpeg_decoder& jdecoder){
	mkr = marker(uint16_t((data.at(0) << 8) | data.at(1)));

	memcpy(&length, &data.at(2), 3);
	memcpy(&y, &data.at(5), 5);

	swap_endian(length);
	swap_endian(y);
	swap_endian(x);

	for(int i = 0; i != num; ++i){
		element ele;
		memcpy(&ele, &data.at(10) + i * 3, 3);
		param.push_back(ele);
	}

	jdecoder.frame_header = this;

	return 0;
}

void seg_frame::print()const{
	cout << hex << setfill('0')
		<< setw(2) << (mkr >> 8) << ' '
		<< setw(2) << (mkr & 0xff) << ' ';

	cout << "start of frame\n";

	cout << dec
		<< "length: " << length
		<< " precision: " << uint16_t(precision)
		<< " y: " << y
		<< " x: " << x
		<< " num: " << uint16_t(num)
		<< '\n';

	for(const element& ele: param){
		cout << "ele.id: " << uint16_t(ele.id)
			<< " ele.factor_h: " << uint16_t(ele.factor >> 4)
			<< " ele.factor_v: " << uint16_t(ele.factor & 0xf)
			<< " ele.select_q: " << uint16_t(ele.select_q)
			<< '\n';
	}
}

int seg_scan::load(const string& data, jpeg_decoder& jdecoder){

	mkr = marker(uint16_t((data.at(0) << 8) | data.at(1)));

	memcpy(&length, &data.at(2), 3);

	swap_endian(length);

	for(int i = 0; i != num; ++i){
		element ele;
		memcpy(&ele, &data.at(5) + i * 2, 2);
		param.push_back(ele);
	}

	memcpy(&spectral_start, &data.at(5) + num * 2, 3);

	this->data = data.substr(8 + num * 2, data.npos);

	jdecoder.scan_header = this;

	return 0;
}

void seg_scan::print()const{
	cout << hex << setfill('0')
		<< setw(2) << (mkr >> 8) << ' '
		<< setw(2) << (mkr & 0xff) << ' ';

	cout << "start of scan\n";

	cout << dec
		<< "length: " << length
		<< " num: " << uint16_t(num)
		<< '\n';

	for(const element& ele: param){
		cout << "ele.select_c: " << uint16_t(ele.select_c)
			<< " ele.select_e_dc: " << uint16_t(ele.select_e >> 4)
			<< " ele.select_e_ac: " << uint16_t(ele.select_e & 0xf)
			<< '\n';
	}

	cout << "spectral_start: " << uint16_t(spectral_start)
		<< " spectral_end: " << uint16_t(spectral_end)
		<< " approx_high: " << uint16_t(approx >> 4)
		<< " approx_low: " << uint16_t(approx & 0xf)
		<< '\n';
}

int seg_quanta::load(const string& data, jpeg_decoder& jdecoder){
	mkr = marker(uint16_t((data.at(0) << 8) | data.at(1)));

	memcpy(&length, &data.at(2), 67);
	swap_endian(length);

	for(int i = 0; i != 64; ++i){
		jdecoder.quanta_table.at(precision_id & 0xf).at(i) = table.at(i);
	}

	return 0;
}

void seg_quanta::print()const{
	cout << hex << setfill('0')
		<< setw(2) << (mkr >> 8) << ' '
		<< setw(2) << (mkr & 0xff) << ' ';

	cout << "quantization table segment\n";

	cout << dec
		<< "length: " << length
		<< " precision: " << uint16_t(precision_id >> 4)
		<< " id: " << uint16_t(precision_id & 0xf)
		<< '\n';
	cout << "table: ";
	for(const uint8_t& i: table){
		cout << uint16_t(i) << ' ';
	}
	cout << '\n';
}

node* seg_huffman::element::to_tree()const{
	int index = 16;
	vector<uint8_t>::const_reverse_iterator iter = table_value.rbegin();
	int i = 0;
	vector<pair<int, node*>> vec;
	pair<int, node*> pr;

	do{
		--index;
	}while(!table_num.at(index));

	vec.push_back(make_pair(index + 1, new node{NULL, NULL, 0xff}));

	while(iter != table_value.rend()){
		pr = make_pair(index + 1, new node{NULL, NULL, *iter});
		while(!vec.empty() && vec.back().first == pr.first){
			--pr.first;
			pr.second = new node{pr.second, vec.back().second, 0x00};
			vec.pop_back();
		}
		vec.push_back(pr);
		++iter;
		++i;
		while(index > 0 && table_num.at(index) == i){
			--index;
			i = 0;
		}
	}

	assert(vec.size() == 1);
	return vec.back().second;
}

int seg_huffman::load(const string& data, jpeg_decoder& jdecoder){
	mkr = marker(uint16_t((data.at(0) << 8) | data.at(1)));

	memcpy(&length, &data.at(2), 2);

	swap_endian(length);

	int count = 2;
	while(count < length){
		element ele;
		memcpy(&ele, &data.at(2) + count, 17);
		count += 17;

		int sum = 0;
		for(const uint8_t& i: ele.table_num){
			sum += i;
		}

		ele.table_value.assign(sum, 0);
		memcpy(&ele.table_value.at(0), &data.at(2) + count, sum);
		count += sum;

		param.push_back(ele);

		node* huffman_tree = ele.to_tree();
		if(ele.class_id >> 4){
			jdecoder.huffman_tree_ac_table.at(ele.class_id & 0xf) = huffman_tree;
		}else{
			jdecoder.huffman_tree_dc_table.at(ele.class_id & 0xf) = huffman_tree;
		}
	}

	return 0;
}

void seg_huffman::print()const{
	cout << hex << setfill('0')
		<< setw(2) << (mkr >> 8) << ' '
		<< setw(2) << (mkr & 0xff) << ' ';

	cout << "huffman table segment\n";

	cout << dec
		<< "length: " << length
		<< '\n';

	for(const element& ele: param){
		cout << dec << "ele.class: " << uint16_t(ele.class_id >> 4)
			<< " ele.id: " << uint16_t(ele.class_id & 0xf)
			<< '\n';
		cout << "ele.table_num: ";

		for(const uint8_t& i: ele.table_num){
			cout << uint16_t(i) << ' ';
		}
		cout << '\n';

		cout << "ele.table_value: " << hex;
		for(const uint8_t& i: ele.table_value){
			cout << hex << setw(2) << uint16_t(i) << ' ';
		}
		cout << '\n';

//		node* huffman_tree = ele.to_tree();
//		cout << "huffman_tree:\n";
//		huffman_tree->print();
	}
}

void seg_restart::print()const{
	cout << hex << setfill('0')
		<< setw(2) << (mkr >> 8) << ' '
		<< setw(2) << (mkr & 0xff) << ' ';

	cout << "restart interval\n";
}

void seg_app::print()const{
	cout << hex << setfill('0')
		<< setw(2) << (mkr >> 8) << ' '
		<< setw(2) << (mkr & 0xff) << ' ';

	cout << "application segment\n";
}

int jpeg_decoder::load(const string& data){
	size_t pos, pos_next;
	vector<string> vec;

	for(pos = 0; pos != data.npos; pos = pos_next){
		pos_next = data.find('\xff', pos + 1);
		while(data.at(pos_next + 1) == 0){
			pos_next = data.find('\xff', pos_next + 1);
		}
		vec.push_back(data.substr(pos, pos_next - pos));
	}

	seg_table.reserve(20);
	for(const string& str: vec){
		segment seg;
		seg_table.push_back(seg);
		seg_table.back().load(str, *this);
	}

	return 0;
}

int jpeg_decoder::loadfile(const string& filename){
	ifstream in;
	ostringstream out;

	in.open(filename, ios::in | ios::binary);
	if(!in){
		return 1;
	}
	out << in.rdbuf();
	in.close();
	load(out.str());

	return 0;
}

//table_kernel[i][j] = cos((2 * i + 1) * j * pi / 16);
const double table_kernel[8][8] = {
	{ 1.        ,  0.98078528,  0.92387953,  0.83146961,  0.70710678,  0.55557023,  0.38268343,  0.19509032},
	{ 1.        ,  0.83146961,  0.38268343, -0.19509032, -0.70710678, -0.98078528, -0.92387953, -0.55557023},
	{ 1.        ,  0.55557023, -0.38268343, -0.98078528, -0.70710678,  0.19509032,  0.92387953,  0.83146961},
	{ 1.        ,  0.19509032, -0.92387953, -0.55557023,  0.70710678,  0.83146961, -0.38268343, -0.98078528},
	{ 1.        , -0.19509032, -0.92387953,  0.55557023,  0.70710678, -0.83146961, -0.38268343,  0.98078528},
	{ 1.        , -0.55557023, -0.38268343,  0.98078528, -0.70710678, -0.19509032,  0.92387953, -0.83146961},
	{ 1.        , -0.83146961,  0.38268343,  0.19509032, -0.70710678,  0.98078528, -0.92387953,  0.55557023},
	{ 1.        , -0.98078528,  0.92387953, -0.83146961,  0.70710678, -0.55557023,  0.38268343, -0.19509032}
};

void fdct(const array<int, 64>& src, array<int, 64>& des){
	//const double pi = 3.141592653589793238462643383279502884197175105;
	const array<double, 8> c = {1.0 / sqrt(2.0), 1, 1, 1, 1, 1, 1, 1};
	double temp;

	for(int k = 0; k != 8; ++k){
		for(int l = 0; l != 8; ++l){
			temp = 0;
			for(int i = 0; i != 8; ++i){
				for(int j = 0; j != 8; ++j){
					temp +=
						//src.at((i << 3) | j)
						src[(i << 3) | j]
						//* cos((2 * i + 1) * k * pi / 16)
						//* cos((2 * j + 1) * l * pi / 16);
						* table_kernel[i][k] * table_kernel[j][l];
				}
			}
			temp *= c[k] * c[l];
			temp /= 4;
			//des.at((k << 3) | l) = temp;
			des[(k << 3) | l] = temp;
		}
	}
}

void idct(const array<int, 64>& src, array<int, 64>& des){
	//const double pi = 3.141592653589793238462643383279502884197175105;
	const array<double, 8> c = {1.0 / sqrt(2.0), 1, 1, 1, 1, 1, 1, 1};
	double temp;

	for(int i = 0; i != 8; ++i){
		for(int j = 0; j != 8; ++j){
			temp = 0;
			for(int k = 0; k != 8; ++k){
				for(int l = 0; l != 8; ++l){
					temp +=
						//src.at((k << 3) | l)
						src[(k << 3) | l]
						* c[k] * c[l]
						//* cos((2 * i + 1) * k * pi / 16)
						//* cos((2 * j + 1) * l * pi / 16);
						* table_kernel[i][k] * table_kernel[j][l];
				}
			}
			temp /= 4;
			//des.at((i << 3) | j) = temp;
			des[(i << 3) | j] = temp;
		}
	}
}

void jpeg_decoder::decode(int*& result, int& result_y, int& result_x, int& count, const bool& verbose){
	string data = scan_header->data;
	array<array<int, 4>, 3> table_size;
	array<array<int, 3>, 3> table_select;
	int x, y;
	int h_max, v_max;
	int h, v;
	
	bool flag;
	size_t pos = 0;
	uint8_t mask = 0x80;
	int com_i = 0, com_h = 0, com_v = 0;
	node* huffman_tree_dc;
	node* huffman_tree_ac;
	node* ptr;
	int length;
	int temp;
	array<int, 64> mcu, mcu_next;
	int index;
	int num;
	array<int, 3> dc_prev;

	count = frame_header->num;

	auto increase_pos = [&](){
		mask >>= 1;
		if(!mask){
			++pos;
			mask = 0x80;
		}
	};

	auto increase_com = [&](){
		++com_h;
		if(com_h == table_size.at(com_i).at(0)){
			com_h = 0;
			++com_v;
			if(com_v == table_size.at(com_i).at(1)){
				com_v = 0;
				++com_i;
				if(com_i == count){
					com_i = 0;
					++num;
				}
			}
		}
	};

	result_x = frame_header->x;
	result_y = frame_header->y;

	x = result_x >> 3;
	if(result_x & 0x7){
		++x;
	}
	y = result_y >> 3;
	if(result_y & 0x7){
		++y;
	}
	result = new int[count * result_x * result_y];

	for(auto ele: frame_header->param){
		table_size.at(ele.id - 1).at(0) = ele.factor >> 4;
		table_size.at(ele.id - 1).at(1) = ele.factor & 0xf;
		table_select.at(ele.id - 1).at(0) = ele.select_q;
	}
	h_max = 0;
	v_max = 0;
	for(int i = 0; i != count; ++i){
		h_max = max(h_max, table_size.at(i).at(0));
		v_max = max(v_max, table_size.at(i).at(1));
	}
	for(int i = 0; i != count; ++i){
		table_size.at(i).at(2) = h_max / table_size.at(i).at(0);
		table_size.at(i).at(3) = v_max / table_size.at(i).at(1);
	}

	h = x / h_max;
	if(x % h_max){
		++h;
	}
	v = y / v_max;
	if(y % v_max){
		++v;
	}

	for(auto ele: scan_header->param){
		table_select.at(ele.select_c - 1).at(1) = ele.select_e >> 4;
		table_select.at(ele.select_c - 1).at(2) = ele.select_e & 0xf;
	}

	//将转义的\xff\x00替换为\xff
	string dumb_mark;
	dumb_mark += '\xff';
	dumb_mark += '\x00';
	for(pos = data.find(dumb_mark, pos + 1); pos != data.npos; pos = data.find(dumb_mark, pos + 1)){
		data.replace(pos, 2, "\xff");
	}

	pos = 0;
	num = 0;
	dc_prev = {0, 0, 0};

	while(pos < data.size() && num < h * v){

		if(verbose){
	//		for(size_t p = pos; p != pos + 40 && p < data.size(); ++p){
	//			cout << hex << setw(2) << (uint16_t)(uint8_t) data.at(p) << ' ';
	//		}cout << '\n';
			cout << "num: " << dec << num << " component: " << com_i << ' ' << com_h << ' ' << com_v << '\n';
			cout << "pos: " << pos << " mask: " << hex << (uint16_t)(uint8_t)mask << '\n';
		}

		huffman_tree_dc = huffman_tree_dc_table.at(table_select.at(com_i).at(1));
		huffman_tree_ac = huffman_tree_ac_table.at(table_select.at(com_i).at(2));

		if(verbose){
			cout << "huffman decoding\n" << setfill('0');
		}

		flag = true;
		for(index = 0; index != 64; ++index){
			if(flag){
				ptr = huffman_tree_dc;
			}else{
				ptr = huffman_tree_ac;
			}

			for(; ptr->left || ptr->right; increase_pos()){
				if(data.at(pos) & mask){
					ptr = ptr->right;
				}else{
					ptr = ptr->left;
				}
			}

			assert(ptr->value != 0xff);
			if(ptr->value == 0x00 && !flag){
				break;
			}

			if(verbose){
				cout << hex << setw(2) << (uint16_t)ptr->value << ' ';
			}
			length = ptr->value & 0xf;
			temp = 0;
			for(int i = 0; i != length; ++i){
				temp <<= 1;
				if(data.at(pos) & mask){
					++temp;
				}
				increase_pos();
			}
			if(!(temp & (1 << (length - 1)))){
				temp ^= ((1 << length) - 1);
				temp = -temp;
			}

			for(int i = uint8_t(ptr->value >> 4); i != 0; --i){
				mcu.at(index) = 0;
				++index;
			}
			mcu.at(index) = temp;

			if(verbose){
				cout << dec << '(' << (uint16_t)(uint8_t)(ptr->value >> 4) << ',' << temp << ") ";
			}

			if(flag){
				flag = false;
			}
		}
		if(verbose){
			cout << '\n';

			cout << "differential dc decoding\n";
			cout << mcu.at(0) << " -> " << mcu.at(0) + dc_prev.at(com_i) << '\n';
		}

		dc_prev.at(com_i) += mcu.at(0);
		mcu.at(0) = dc_prev.at(com_i);

		if(verbose){
			cout << "run length decoding\n";
		}
		for(; index < 64; ++index){
			mcu.at(index) = 0;
		}

		if(verbose){
			for(const auto& i: mcu){
				cout << i << ' ';
			}cout << '\n';

			cout << "coefficient dequantization\n";
		}

		for(int i = 0; i != 64; ++i){
			mcu.at(i) *= quanta_table.at(table_select.at(com_i).at(0)).at(i);
		}

		if(verbose){
			for(const auto& i: mcu){
				cout << i << ' ';
			}cout << '\n';

			cout << "zigzag decoding\n";
		}
		for(int i = 0; i != 64; ++i){
			mcu_next.at(i) = mcu.at(table_zigzag.at(i));
		}

		if(verbose){
			cout << setfill(' ');
			for(int i = 0; i != 8; ++i){
				for(int j = 0; j != 8; ++j){
					cout << setw(4) << mcu_next.at((i << 3) | j) << ' ';
				}cout << '\n';
			}

			cout << "inverse discrete cosine transform\n";
		}
		idct(mcu_next, mcu);

		if(verbose){
			for(int i = 0; i != 8; ++i){
				for(int j = 0; j != 8; ++j){
					cout << setw(4) << mcu.at((i << 3) | j) << ' ';
				}cout << '\n';
			}
		}

		int h_div = table_size.at(com_i).at(2);
		int v_div = table_size.at(com_i).at(3);
		int pos_x, pos_y;
		for(int i = 0; i != v_div; ++i){
			for(int j = 0; j != h_div; ++j){
				for(int k = 0; k != 8; ++k){
					for(int l = 0; l != 8; ++l){
						pos_x = ((num % h) * h_max + com_h * h_div) * 8 + l * h_div + j;
						pos_y = ((num / h) * v_max + com_v * v_div) * 8 + k * v_div + i;
						if(pos_x < result_x && pos_y < result_y){
							result[(pos_y * result_x + pos_x) * count + com_i] = mcu.at((k << 3) | l);
						}
					}
				}
			}
		}

		if(verbose){
			cout << '\n';
		}

		increase_com();
	}
}

void jpeg_decoder::decode(int** ptrm, int* m1, int* m2, int* m3, const bool& verbose){
	return this->decode(*ptrm, *m1, *m2, *m3, verbose);
}
