#ifndef JPEG_H
#define JPEG_H

#include <iostream>
#include <array>
#include <vector>
#include <string>
#include <cstring>
#include <cassert>
#include <iomanip>
#include <cmath>
#include <fstream>
#include <sstream>

using namespace std;

enum marker{
	m_sof0 = 0xffc0,
	m_sof1,
	m_sof2,
	m_sof3,
	m_sof5 = 0xffc5,
	m_sof6,
	m_sof7,
	m_jpg,
	m_sof9,
	m_sof10,
	m_sof11,
	m_sof13 = 0xffcd,
	m_sof14,
	m_sof15,
	m_dht = 0xffc4,
	m_dac = 0xffcc,
	m_rst0 = 0xffd0,
	m_rst1,
	m_rst2,
	m_rst3,
	m_rst4,
	m_rst5,
	m_rst6,
	m_rst7,
	m_soi = 0xffd8,
	m_eoi,
	m_sos,
	m_dqt,
	m_dnl,
	m_dri,
	m_dhp,
	m_exp,
	m_app0,
	m_app1,
	m_app2,
	m_app3,
	m_app4,
	m_app5,
	m_app6,
	m_app7,
	m_app8,
	m_app9,
	m_app10,
	m_app11,
	m_app12,
	m_app13,
	m_app14,
	m_app15,
	m_jpg0,
	m_jpg1,
	m_jpg2,
	m_jpg3,
	m_jpg4,
	m_jpg5,
	m_jpg6,
	m_jpg7,
	m_jpg8,
	m_jpg9,
	m_jpg10,
	m_jpg11,
	m_jpg12,
	m_jpg13,
	m_com,
	m_tem = 0xff01
};

enum seg_type{
	s_base,
	s_frame,
	s_scan,
	s_quanta,
	s_huffman,
	s_restart,
	s_app
};

const array<int, 64> table_zigzag = {
	 0,  1,  5,  6, 14, 15, 27, 28,
	 2,  4,  7, 13, 16, 26, 29, 42,
	 3,  8, 12, 17, 25, 30, 41, 43,
	 9, 11, 18, 24, 31, 40, 44, 53,
	10, 19, 23, 32, 39, 45, 52, 54,
	20, 22, 33, 38, 46, 51, 55, 60,
	21, 34, 37, 47, 50, 56, 59, 61,
	35, 36, 48, 49, 57, 58, 62, 63
};

class jpeg_decoder;

//数据的大尾小尾转换
//JPEG格式采用大尾存储，而C++这里采用小尾存储，所以需要转换
inline void swap_endian(uint16_t& n){
	n = ((n & 0x00ff) << 8) | ((n & 0xff00) >> 8);
}

//节点结构体，用于构造Huffman树
struct node{
	node* left;
	node* right;
	uint8_t value;

	void print(const string& prefix = ""){
		if(left){
			left->print(prefix + '0');
			right->print(prefix + '1');
		}else{
			cout << prefix << ' ' << setw(2) << uint16_t(value) << '\n';
		}
	}
};

struct seg_base{
	marker mkr;

	virtual ~seg_base(){}

	virtual int load(const string& data, jpeg_decoder& jdecoder);
	virtual void print()const;
};

struct seg_frame: public seg_base{
	uint16_t length;
	uint8_t precision;
	uint16_t y;
	uint16_t x;
	uint8_t num;

	struct element{
		uint8_t id;
		uint8_t factor;
		uint8_t select_q;
	};
	vector<element> param;

	virtual int load(const string& data, jpeg_decoder& jdecoder);
	virtual void print()const;
};

struct seg_scan: public seg_base{
	uint16_t length;
	uint8_t num;

	struct element{
		uint8_t select_c;
		uint8_t select_e;
	};
	vector<element> param;

	uint8_t spectral_start;
	uint8_t spectral_end;
	uint8_t approx;

	string data;

	virtual int load(const string& data, jpeg_decoder& jdecoder);
	virtual void print()const;
};

struct seg_quanta: public seg_base{
	uint16_t length;
	uint8_t precision_id;
	array<uint8_t, 64> table;

	virtual int load(const string& data, jpeg_decoder& jdecoder);
	virtual void print()const;
};

struct seg_huffman: public seg_base{
	uint16_t length;

	struct element{
		uint8_t class_id;
		array<uint8_t, 16> table_num;
		vector<uint8_t> table_value;

		//用Huffman表构造Huffman树
		node* to_tree()const;
	};

	vector<element> param;

	virtual int load(const string& data, jpeg_decoder& jdecoder);
	virtual void print()const;
};

struct seg_restart: public seg_base{
	uint16_t length;
	uint16_t interval;

	virtual void print()const;
};

struct seg_app: public seg_base{
	uint16_t length;
	vector<uint8_t> table;

	virtual void print()const;
};

class segment{
protected:
	seg_type seg_t;
	seg_base* ptr;

public:
	friend jpeg_decoder;

	segment(): ptr(NULL){//cout << "segment construct\n";
	}
	segment(const segment& seg): seg_t(seg.seg_t){
		//cout << "segment copy construct\n";
		if(seg.ptr){
			switch(seg_t){
			case s_base:
				//cout << "allocate seg_base\n";
				ptr = new seg_base;
				break;
			case s_frame:
				//cout << "allocate seg_frame\n";
				ptr = new seg_frame;
				break;
			case s_scan:
				//cout << "allocate seg_scan\n";
				ptr = new seg_scan;
				break;
			case s_quanta:
				//cout << "allocate seg_quanta\n";
				ptr = new seg_quanta;
				break;
			case s_huffman:
				//cout << "allocate seg_huffman\n";
				ptr = new seg_huffman;
				break;
			case s_restart:
				//cout << "allocate seg_restart\n";
				ptr = new seg_restart;
				break;
			case s_app:
				//cout << "allocate seg_app\n";
				ptr = new seg_app;
				break;
			default:
				assert(false);
				;
			}
			*ptr = *seg.ptr;
		}else{
			ptr = NULL;
		}
	}
	segment(segment&& seg): seg_t(seg.seg_t), ptr(seg.ptr) {//cout << "segment move construct\n";
	}
	~segment(){
		//cout << "segment destroy\n";
		delete ptr;
	}
	segment operator=(const segment& seg){
		delete ptr;
		seg_t = seg.seg_t;
		//cout << "segment assign\n";
		if(seg.ptr){
			switch(seg_t){
			case s_base:
				//cout << "allocate seg_base\n";
				ptr = new seg_base;
				break;
			case s_frame:
				//cout << "allocate seg_frame\n";
				ptr = new seg_frame;
				break;
			case s_scan:
				//cout << "allocate seg_scan\n";
				ptr = new seg_scan;
				break;
			case s_quanta:
				//cout << "allocate seg_quanta\n";
				ptr = new seg_quanta;
				break;
			case s_huffman:
				//cout << "allocate seg_huffman\n";
				ptr = new seg_huffman;
				break;
			case s_restart:
				//cout << "allocate seg_restart\n";
				ptr = new seg_restart;
				break;
			case s_app:
				//cout << "allocate seg_app\n";
				ptr = new seg_app;
				break;
			default:
				assert(false);
				;
			}
			*ptr = *seg.ptr;
		}else{
			ptr = NULL;
		}
		return *this;
	}
	segment operator=(segment&& seg){
		//cout << "segment move assign\n";
		delete ptr;
		seg_t = seg.seg_t;
		ptr = seg.ptr;
		return *this;
	}

	int load(const string& data, jpeg_decoder& jdecoder){
		delete ptr;
		marker mkr = marker(uint16_t((data.at(0) << 8) | data.at(1)));
		//cout << " mkr: " << hex << uint16_t(mkr) << "\n";
		if(mkr < 0xffc0 || mkr == 0xffff){
			cout << "An invalid marker "
				<< hex << setfill('0')
				<< setw(2) << (unsigned short)(uint8_t)(data.at(0)) << ' '
				<< setw(2) << (unsigned short)(uint8_t)(data.at(1)) << ' '
				<< "is encountered.\n";
			return 1;
		}

		switch(mkr){
		case m_soi:
		case m_eoi:
			seg_t = s_base;
			ptr = new seg_base;
			break;
		case m_sof0:
			seg_t = s_frame;
			ptr = new seg_frame;
			break;
		case m_sos:
			seg_t = s_scan;
			ptr = new seg_scan;
			break;
		case m_dqt:
			seg_t = s_quanta;
			ptr = new seg_quanta;
			break;
		case m_dht:
			seg_t = s_huffman;
			ptr = new seg_huffman;
			break;
		case m_app0:
			seg_t = s_app;
			ptr = new seg_app;
			break;
		default:
			seg_t = s_base;
			ptr = new seg_base;
			//return 1;
			break;
		}
		return ptr->load(data, jdecoder);
	}

	void print()const{
		ptr->print();
	}
};

class jpeg_decoder{
protected:
	vector<segment> seg_table;
	seg_frame* frame_header;
	seg_scan* scan_header;
	array<array<uint8_t, 64>, 4> quanta_table;
	array<node*, 4> huffman_tree_dc_table;
	array<node*, 4> huffman_tree_ac_table;

public:
	jpeg_decoder() = default;
	jpeg_decoder(const jpeg_decoder&) = delete;
	jpeg_decoder& operator=(const jpeg_decoder&) = delete;

	friend struct seg_frame;
	friend struct seg_scan;
	friend struct seg_quanta;
	friend struct seg_huffman;

	int loadfile(const string& filename);
	int load(const string& data);

	void print()const{
		for(const segment& seg: seg_table){
			seg.print();
		}
	}

	void decode(int*& result, int& result_x, int& result_y, int& count, const bool& verbose = false);
	void decode(int** ptrm, int* m1, int* m2, int* m3, const bool& verbose = false);
};

#endif //JPEG_H
