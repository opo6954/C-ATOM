'''
Annotator python ocv
'''
import tkinter
from tkinter import ttk
import tkinter as tk
from tkinter import filedialog
import tkinter.messagebox
from PIL import ImageTk, Image
import os
import json
import requests
from MessageHandler import Msg
import base64
import cv2
import numpy as np
from utils import ui_coord_to_img_coord, is_pt_inside_the_circle



SERVER_URL = 'kolomverse.iptime.org'
SERVER_PORT = 20038



class AnnotatorUI(tkinter.Frame):
    def __init__(self, master):
        super(AnnotatorUI,self).__init__(master)
        self.canvas_width = 1280
        self.canvas_height = 720
        self.img_width = 0
        self.img_height = 0
        self.panel_width = 1500
        self.panel_height = 80
        self.current_ui = ''
        self.radius = 10
        self.define_all_widget()
        self.pack()
        self.curr_attention_pt = []
        self.curr_attention_obj = []
        # final obj
        self.curr_final_obj = []
        self.init_attention_pt_list()
        # pillow image
        self.img_pil = None
        # image load
        self.is_image_loaded = False
        
        
        server_full_address = 'http://{}:{}'.format(SERVER_URL, SERVER_PORT)
        self.AI_server = '{}/process_msg_img'.format(server_full_address)
        self.server_check = '{}/'

    def attention_done(self, img, attention_pt_list):
        
        
        
        
        img_cv = np.array(self.img_pil)
        img_str = base64.b64encode(cv2.imencode('.jpg', img_cv)[1]).decode()
        
        msg = Msg()
        msg.add_file_name('test.jpg')
        msg.add_img_size(img.size)
        for idx, each_att in enumerate(attention_pt_list):
            msg.add_attention_point(idx, each_att[0], each_att[1])
        
        msg.add_img_str(img_str)
        
        json_input = msg.convert_json_legacy()
        
        with open('test.json', 'w') as write_json:
            write_json.write(json_input)
        
        json_input = json.loads(json_input)
            
        
        
        try:
            res = requests.post('http://{}:{}/process_with_img'.format(SERVER_URL, SERVER_PORT), json=json_input)
        except requests.exceptions.Timeout as e:
            tkinter.messagebox.showinfo('Error', 'TimeOut Error to Server({})'.format(e))
        except requests.exceptions.ConnectionError as e:
            tkinter.messagebox.showinfo('Error', 'Connection Error to Server({})'.format(e))
        except requests.exceptions.HTTPError as e:
            tkinter.messagebox.showinfo('Error', 'HTTP Error to Server({})'.format(e))
        except requests.exceptions.RequestException as e:
            tkinter.messagebox.showinfo('Error', 'Error ({})'.format(e))
            
            
        
        
        msg = Msg()
        res_json = json.loads(res.text)
        
        msg.load_json_legacy(res_json)
        
        final_rect_list = []
        
        for each_att_id in msg.final_box_dic.keys():
            final_rect = msg.final_box_dic[each_att_id]
            final_rect_list.append(final_rect)
        
        return final_rect_list
        
        
    def delete_final_obj_with_idx(self, idx, canvas_instance):
        if idx < len(self.curr_final_obj):
            canvas_instance.delete(self.curr_final_obj[idx])
            del self.curr_final_obj[idx]
    def delete_attention_pt_with_idx(self, idx, canvas_instance):
        if idx < len(self.curr_attention_pt):
            # remove attention pt
            del self.curr_attention_pt[idx]

            # remove the circle element
            canvas_instance.delete(self.curr_attention_obj[idx])
            del self.curr_attention_obj[idx]
    def init_final_res_list(self):
        num_final_res = len(self.curr_final_obj)
        for _ in range(num_final_res):
            self.delete_final_obj_with_idx(0,self.canvas)
        self.curr_final_obj = []
    def init_attention_pt_list(self):
        num_attention_pt = len(self.curr_attention_pt)
        for idx in range(num_attention_pt):
            self.delete_attention_pt_with_idx(0, self.canvas)

        self.curr_attention_obj = []
        self.curr_attention_pt = []
        
    def attention_button_callback(self):
        # make attention_pt on image_coordi
        # send msg to server
        
        print('Send attention pt')
        if not self.is_image_loaded:
            tkinter.messagebox.showinfo('Error','No image loaded')
            return
        
        self.init_final_res_list()
        

        attention_pt_img_coord_list = []
        for each_attention_pt in self.curr_attention_pt:
            img_coord_x, img_coord_y = ui_coord_to_img_coord(each_attention_pt,self.canvas_width,self.canvas_height,self.img_width, self.img_height)
            attention_pt_img_coord_list.append((img_coord_x, img_coord_y))
        final_res = self.attention_done(self.img_pil, attention_pt_img_coord_list)

        self.draw_result(final_res)


    def draw_result(self, final_rect_list):
        color = 'blue'
        # draw final bbox
        for each_rect in final_rect_list:
            
            leftdown_pt = each_rect.x1, each_rect.y1
            rightup_pt = each_rect.x2, each_rect.y2

            leftdown_ui_coord = ui_coord_to_img_coord(leftdown_pt,self.img_width, self.img_height, self.canvas_width, self.canvas_height)
            rightup_ui_coord = ui_coord_to_img_coord(rightup_pt,self.img_width, self.img_height, self.canvas_width, self.canvas_height)

            self.curr_final_obj.append(self.canvas.create_rectangle(leftdown_ui_coord[0], leftdown_ui_coord[1], rightup_ui_coord[0], rightup_ui_coord[1] , outline=color, width=3))

    def attention_click_callback(self, event):
        # left click: add attention point
        ui_coord_x, ui_coord_y = event.x, event.y

        for idx, attention_pt in enumerate(self.curr_attention_pt):
            if is_pt_inside_the_circle(ui_coord_x, ui_coord_y, attention_pt[0], attention_pt[1],self.radius):
                self.delete_attention_pt_with_idx(idx, self.canvas)

        circle_pos = [ui_coord_x-0.5*self.radius, ui_coord_y-0.5*self.radius, ui_coord_x+0.5*self.radius, ui_coord_y+0.5*self.radius]
        circle_pos = list(map(int, circle_pos))
        circle_instance = self.canvas.create_oval(circle_pos[0], circle_pos[1],circle_pos[2],circle_pos[3], outline='red', width=3)

        self.curr_attention_pt.append((ui_coord_x, ui_coord_y))
        self.curr_attention_obj.append(circle_instance)

        print('Clicked UI at {}, {}'.format(ui_coord_x, ui_coord_y))

    def attention_delete_callback(self, event):
        # right button: delete attention point
        ui_coord_x, ui_coord_y = event.x, event.y

        for idx, attention_pt in enumerate(self.curr_attention_pt):
            if is_pt_inside_the_circle(ui_coord_x, ui_coord_y,attention_pt[0], attention_pt[1],self.radius):
                self.delete_attention_pt_with_idx(idx, self.canvas)

    def quit_button_callback(self):
        self.master.destroy()

    def load_image_attention(self, file_path, canvas_instance, image_instance, label_instance):
        if not os.path.exists(file_path):
            print("No image in the path {}".format(file_path))
            return 0
        
        self.init_attention_pt_list()
        self.init_final_res_list()
        
        self.img_pil = Image.open(file_path)
        self.img_width, self.img_height = self.img_pil.size
        img_pil_resized = self.img_pil.resize((self.canvas_width, self.canvas_height))
        self.imgtkAttention = ImageTk.PhotoImage(image=img_pil_resized)

        canvas_instance.itemconfig(image_instance, image=self.imgtkAttention)
        label_instance.config(text='Load file name: {}'.format(os.path.split(file_path)[-1]))
        
        self.is_image_loaded = True
        
        return 1
    
    def load_image(self):
        
        file_name = filedialog.askopenfilename(initialdir=os.curdir, title='Select Image file', filetypes=(('Image files(jpg', '*.jpg'), ('Image files(png)', '*.png')))
        self.load_image_attention(file_name, self.canvas, self.canvas_image, self.label)
                
    def define_attention_ui(self):
        # define attention ui
        self.label = tk.Label(self, text='filename')

        self.canvas = tk.Canvas(self, bg='blue', width=self.canvas_width, height=self.canvas_height)
        img_pil = Image.new('RGB', (self.canvas_width, self.canvas_height), color='red')
        self.imgtkAttention = ImageTk.PhotoImage(image=img_pil)

        self.canvas_image = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.imgtkAttention)

        button_load = ttk.Button(self, text='Load image', width=20, command = self.load_image)
        button_attention = ttk.Button(self, text='Send attention point(s)', width=20, command=self.attention_button_callback)

        self.label.grid(row=0, column=0)
        self.canvas.grid(row=1, column=0)
        button_load.grid(row=2, column=0)
        button_attention.grid(row=3, column=0)
        


        self.canvas.bind('<Button-1>', self.attention_click_callback)
        self.canvas.bind('<Button-3>', self.attention_delete_callback)





    def define_all_widget(self):
        self.define_attention_ui()
        
        
        

def annotator_main():
    root = tk.Tk()
    root.title('C-ATOM')
    root.geometry("1500x960")
    root.resizable(False, False)

    annotator = AnnotatorUI(root)
    root.mainloop()



def main():
    annotator_main()



if __name__ == '__main__':
    main()
