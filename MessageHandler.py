'''
Message Handler between C-ATOM client and C-ATOM server
'''
'''
Message handler
calculate engine -> msg -> flask json
flask json -> msg -> calculate engine
'''
from utils import Rect
import json
import os
import base64

class Msg:
    def __init__(self, isVottDot=True):
        self.file_name = ''
        self.file_path = ''
        self.attention_point_dic = {}
        self.final_box_dic = {}
        self.img_size = None
        self.tag='ship'
        self.isVottDot = isVottDot
        self.img_str = None
        self.format=''
        self.version = '0.1'
        
        
    # Add image
    
    def add_img_str(self, img_str):
        self.img_str = img_str
    
    # Add input source; attention point
    def add_attention_point(self, id, attention_x, attention_y):
        self.attention_point_dic[id] = [attention_x, attention_y]

    # Add input file name
    def add_file_name(self, file_name):
        self.file_name = os.path.split(file_name)[-1]
        self.format = self.file_name.split('.')[-1]
        self.file_path = file_name
        self.id = 0
        
    
    # Add img size
    def add_img_size(self, img_size):
        self.img_size = img_size
    
    # Add output source: final box(Rect)
    def add_final_box(self, id, final_rect):
        self.final_box_dic[id] = final_rect

    '''
    		"id": "9d224efdeb971d10cc7cda321e387053",
		"name": "대명항_맑음_20201112_0001_02083.jpg",
    	"path": "ftp://lhw@10.7.40.71//home/lhw/storage1/kriso/ship_detection/kriso_attention_based_annotation/data_kriso/data/대명항_1차/3.Test/원천데이터_BOX/대명항/20201112/0001/대명항_맑음_20201112_0001_02083.jpg",
		"size": {
			"width": 3840,
			"height": 2160
		},
		"type": 1,
		"state": 2,
		"format": "jpeg",
		"approved": false,
		"completed": false,
		"isDisabled": false
    '''
    def load_json_legacy(self, str_data):
        self.id = str_data['asset']['id']
        self.file_name = str_data['asset']['name']
        self.file_path = str_data['asset']['path']
        self.format = str_data['asset']['format']
        
        
        region_list = str_data['regions']
        self.img_size = str_data['asset']['size']['width'], str_data['asset']['size']['height']

        # Load attention points or final box
        for each_obj in region_list:
            id = each_obj['id']
            obj_type = each_obj['type']
            tag = each_obj['tags']
            
            
            left = each_obj['boundingBox']['left']
            top = each_obj['boundingBox']['top']

            if obj_type == 'RECTANGLE':
                width = each_obj['boundingBox']['width']
                height = each_obj['boundingBox']['height']
                x1,y1,x2,y2 = left, top, left + width, top + height
                final_box = Rect(x1, y1, x2, y2)
                self.final_box_dic[id] = final_box

            elif obj_type == 'POINT':
                self.attention_point_dic[id] = [left, top]
    
   
    def convert_json_legacy(self):
        json_data = {}
        
        if not self.img_str is None:
            json_data['img'] = self.img_str
        
        json_data['asset'] = {'id':self.id, 'name':self.file_name, 
                              'path':self.file_path, 'size':{'width':self.img_size[0], 'height':self.img_size[1]},
                              'format':self.format}
        json_data['regions'] = []
        json_data['version'] = {'version':self.version}

        #for attention_point_list
        

        for each_id in self.attention_point_dic.keys():
            left, top = self.attention_point_dic[each_id]
            region_instance = {'id':each_id, 'type':'POINT', 'tags':[self.tag],
                            'points':{'x':left, 'y':top}, 'boundingBox':{'top':top, 'left':left, 'width':0, 'height':0}}
            json_data['regions'].append(region_instance)

        #for final_box_list

        for each_id in self.final_box_dic.keys():
            final_rect = self.final_box_dic[each_id]
            x1 = final_rect.x1
            y1 = final_rect.y1
            x2 = final_rect.x2
            y2 = final_rect.y2
            if self.isVottDot:
                id_final = each_id
            else:
                id_final = '{}_gen'.format(each_id)
            region_instance = {'id': '{}'.format(id_final), 'tags':[self.tag], 'type':'RECTANGLE',
                               'points': [{'x':x1, 'y':y1},
                                          {'x':x2, 'y':y1},
                                          {'x':x2, 'y':y2},
                                          {'x':x1, 'y':y2}],
                               'boundingBox': {'top':final_rect.y1, 'left':final_rect.x1, 'width':final_rect.width, 'height':final_rect.height}
                               }
            json_data['regions'].append(region_instance)

        return json.dumps(json_data, indent=2, ensure_ascii=False)