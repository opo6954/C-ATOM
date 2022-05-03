"""
Matching the bbox between OpenVINO and YOLO result
"""

import sys
import os

# bbox data:
# 1
# body,0,init,616,69,700,401

import numpy as np

def ui_coord_to_img_coord_1d(ui_coor, ui_width, img_width):
    ui_x = ui_coor

    norm_x = ui_x / ui_width

    img_x= norm_x * img_width

    return int(img_x)

def ui_coord_to_img_coord(ui_coor, ui_width, ui_height, img_width, img_height):
    ui_x, ui_y = ui_coor

    norm_x, norm_y = ui_x / ui_width, ui_y / ui_height

    img_x, img_y = norm_x * img_width, norm_y * img_height

    return int(img_x), int(img_y)

def is_pt_inside_the_circle(pt_x, pt_y, center_x, center_y, radius):
    if (pt_x - center_x)**2 + (pt_y - center_y)**2 < radius ** 2:
        return True
    else:
        return False


class Rect:
    def __init__(self, *args, **kwargs):
        if len(args) == 0:
            x1, y1, x2, y2 = 0,0,0,0
        # c, w, h
        if len(args) == 3:
            c, w, h = args
            x1 = c[0] - 0.5 * w
            x2 = c[0] + 0.5 * w
            y1 = c[1] - 0.5 * h
            y2 = c[1] + 0.5 * h

        if len(args) == 4:
            x1, y1, x2, y2 = args

        if type(x1) == str:
            x1 = float(x1)
        if type(y1) == str:
            y1 = float(y1)
        if type(x2) == str:
            x2 = float(x2)
        if type(y2) == str:
            y2 = float(y2)

        self.x1 = int(x1)
        self.x2 = int(x2)
        self.y1 = int(y1)
        self.y2 = int(y2)
        
        self.origin_width = None
        self.origin_height = None
        
        

    def __str__(self):
        return '{},{},{},{}'.format(self.x1, self.y1, self.x2, self.y2)
    def get_list(self):
        return [self.x1, self.y1, self.x2, self.y2]
    def set_size(self, width, height):
        self.origin_width = width
        self.origin_height = height
        self.get_norm()
    def get_norm(self):
        self.norm_x1 = float(self.x1 / self.origin_width)
        self.norm_x2 = float(self.x2 / self.origin_width)
        self.norm_y1 = float(self.y1 / self.origin_height)
        self.norm_y2 = float(self.y2 / self.origin_height)
    def set_norm(self, img_size, val_list):
        self.set_size(img_size[0], img_size[1])
        self.norm_x1 = val_list[0]
        self.norm_y1 = val_list[1]
        self.norm_x2 = val_list[2]
        self.norm_y2 = val_list[3]
        self.norm_width = self.norm_x2 - self.norm_x1
        self.norm_height = self.norm_y2 - self.norm_y1

        self.x1 = int(self.norm_x1 * self.origin_width)
        self.y1 = int(self.norm_y1 * self.origin_height)
        self.x2 = int(self.norm_x2 * self.origin_width)
        self.y2 = int(self.norm_y2 * self.origin_height)

    def __getitem__(self, item):
        if item > 4:
            return self.x1, self.y1, self.x2, self.y2
        if item == 0:
            return self.x1
        elif item == 1:
            return self.y1
        elif item == 2:
            return self.x2
        elif item == 3:
            return self.y2

    @property
    def point1(self):
        return self.x1, self.y1
    @property
    def point2(self):
        return self.x2, self.y2

    @property
    def center_point(self):
        return int((self.x2 + self.x1)/2.0) , int((self.y1 + self.y2)/2.0)

    @property
    def center_point_norm(self):
        return float((self.norm_x2 + self.norm_x1)/2.0) , float((self.norm_y1 + self.norm_y2)/2.0)


    @property
    def width(self):
        return self.x2 - self.x1

    @property
    def height(self):
        return self.y2 - self.y1

    @property
    def area(self):
        return self.width * self.height

    @property
    def x1(self):
        return self.__x1

    @property
    def y1(self):
        return self.__y1

    @property
    def x2(self):
        return self.__x2

    @property
    def y2(self):
        return self.__y2

    @x1.setter
    def x1(self, x1):
        if x1 < 0:
            x1 = 0
        self.__x1 = int(x1)

    @x2.setter
    def x2(self, x2):
        if x2 < 0:
            x2 = 0
        self.__x2 = int(x2)

    @y1.setter
    def y1(self, y1):
        if y1 < 0:
            y1 = 0
        self.__y1 = int(y1)

    @y2.setter
    def y2(self, y2):
        if y2 < 0:
            y2 = 0
        self.__y2 = int(y2)


    @staticmethod
    def str_to_rect(str_value):
        str_value_split = str_value.split(',')

        if len(str_value_split) != 4:
            raise ValueError('{} cannot be parsed into rect'.format(str_value))
        int_value_split = map(lambda x: int(float(x)), str_value_split)
        return Rect(int_value_split[0], int_value_split[1], int_value_split[2], int_value_split[3])

    @staticmethod
    def calc_overlap_raio(rect1, rect2):
        '''
        Calculate the overlapped ratio between given two rects
        '''

        if rect1.x2 > rect2.x2:
            max_x2 = rect1.x2
            min_x2 = rect2.x2
        else:
            max_x2 = rect2.x2
            min_x2 = rect1.x2
        if rect1.x1 > rect2.x1:
            max_x1 = rect1.x1
            min_x1 = rect2.x1
        else:
            max_x1 = rect2.x1
            min_x1 = rect1.x1

        if rect1.y1 > rect2.y1:
            max_y1 = rect1.y1
            min_y1 = rect2.y1
        else:
            max_y1 = rect2.y1
            min_y1 = rect1.y1

        if rect1.y2 > rect2.y2:
            max_y2 = rect1.y2
            min_y2 = rect2.y2
        else:
            max_y2 = rect2.y2
            min_y2 = rect1.y2

        intersection_width = min_x2 - max_x1
        intersection_height = min_y2 - max_y1

        if intersection_width < 0:
            return 0
        if intersection_height < 0:
            return 0

        # calc intersection of area
        intersection_area = intersection_width * intersection_height



        # overlapped area ratio calculated from each rect
        area_ratio1, area_ratio2 = float(intersection_area / rect1.area), float(intersection_area / rect2.area)

        return area_ratio1, area_ratio2

    @staticmethod
    def detect_including(rect1, rect2):
        def detect_including_inner(rect1, rect2):
            if rect1.x1 < rect2.x1 and rect1.x2 < rect2.x2 and rect1.y1 < rect2.y1 and rect1.y2 < rect2.y2:
                return True
            else:
                return False
        return detect_including_inner(rect1, rect2) or detect_including_inner(rect2, rect1)
    @staticmethod
    def detect_including_point(rect1, pt, is_norm=False):
        pt_x, pt_y = pt
        if not is_norm:
            if rect1.x1 <= pt_x and rect1.x2 >= pt_x and rect1.y1 <= pt_y and rect1.y2 >= pt_y:
                return True
        elif is_norm:
            if rect1.norm_x1 <= pt_x and rect1.norm_x2 >= pt_x and rect1.norm_y1 <= pt_y and rect1.norm_y2 >= pt_y:
                return True

        return False
    @staticmethod
    def detect_including_point_with_distance(rect1, pt):
        if Rect.detect_including_point(rect1, pt):
            dist = np.sqrt((rect1.center_point[0] - pt[0])**2 + (rect1.center_point[1] - pt[1])**2)
            return dist
        else:
            return -1




    @staticmethod
    def calc_IOU_in_voc(rect1, rect2):
        """
        Calculate the IOU value between the two rects
        VOC IOU CALCULATION(Add 1 for inter_w, inter_h)
        """

        if rect1.x2 > rect2.x2:
            max_x2 = rect1.x2
            min_x2 = rect2.x2
        else:
            max_x2 = rect2.x2
            min_x2 = rect1.x2
        if rect1.x1 > rect2.x1:
            max_x1 = rect1.x1
            min_x1 = rect2.x1
        else:
            max_x1 = rect2.x1
            min_x1 = rect1.x1

        if rect1.y1 > rect2.y1:
            max_y1 = rect1.y1
            min_y1 = rect2.y1
        else:
            max_y1 = rect2.y1
            min_y1 = rect1.y1

        if rect1.y2 > rect2.y2:
            max_y2 = rect1.y2
            min_y2 = rect2.y2
        else:
            max_y2 = rect2.y2
            min_y2 = rect1.y2

        intersection_width = min_x2 - max_x1 + 1
        intersection_height = min_y2 - max_y1 + 1

        if intersection_width < 0:
            return 0
        if intersection_height < 0:
            return 0

        # calc intersection of area
        intersection_area = intersection_width * intersection_height
        # calc union of area
        union_area = (rect1.width+1) * (rect1.height+1) + (rect2.width+1) * (rect2.height+1) - intersection_area

        if union_area == 0:
            raise ValueError('Union Area cannot be zero')

        # iou: intersection of area / union of area
        iou = intersection_area / union_area

        return iou

    @staticmethod
    def calc_IOU(rect1, rect2):
        """
        Calculate the IOU value between the two rects
        """

        if rect1.x2 > rect2.x2:
            max_x2 = rect1.x2
            min_x2 = rect2.x2
        else:
            max_x2 = rect2.x2
            min_x2 = rect1.x2
        if rect1.x1 > rect2.x1:
            max_x1 = rect1.x1
            min_x1 = rect2.x1
        else:
            max_x1 = rect2.x1
            min_x1 = rect1.x1

        if rect1.y1 > rect2.y1:
            max_y1 = rect1.y1
            min_y1 = rect2.y1
        else:
            max_y1 = rect2.y1
            min_y1 = rect1.y1

        if rect1.y2 > rect2.y2:
            max_y2 = rect1.y2
            min_y2 = rect2.y2
        else:
            max_y2 = rect2.y2
            min_y2 = rect1.y2

        intersection_width = min_x2 - max_x1
        intersection_height = min_y2 - max_y1

        if intersection_width < 0:
            return 0
        if intersection_height < 0:
            return 0

        # calc intersection of area
        intersection_area = intersection_width * intersection_height
        # calc union of area
        union_area = rect1.area + rect2.area - intersection_area

        if union_area == 0:
            print('Union Area cannot be zero')
            return 0

        # iou: intersection of area / union of area
        iou = intersection_area / union_area

        return iou

    @staticmethod
    def drawRectOnImg(rect, img, label=''):
        if label == '':
            img_draw = cv2.rectangle(img,(rect.x1, rect.y1),(rect.x2,rect.y2),(0,255,0))
            return img_draw
        else:
            pass