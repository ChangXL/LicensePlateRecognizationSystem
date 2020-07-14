#-*- coding:utf-8 -*-

from tkinter import *
from tkinter import ttk
import cv2 as cv
import numpy as np
from PIL import Image,ImageTk
from RecordMysql import *
import time
import serial
import os
from tkinter.filedialog import askopenfilename
import ContoursPlateLocate as cpl
import BluePlateLocate as bpl
import CutChar as cut
import RemoveUpDown as rud
import CallModel as cm


class Main(object):
    def __init__(self,master,id):
        self.id=id#记录此时的用户
        self.root = master  # 定义内部变量root
        self.root.geometry('1100x650')  # 设置窗口大小
        self.root.title('License Plates Recognizing System')
        # root.iconbitmap("./image/icon.ico")
        """
        核心变量初始化
        """
        self.result = StringVar()
        self.camera = cv.VideoCapture(0)
        self.camera_switch = FALSE
        self.takePhoto = FALSE
        self.video_play= FALSE
        """
        生成界面
        """
        self.createPage()


    def createPage(self):
        frame_pic = Frame(self.root)  # 图片模块
        frame_res = Frame(self.root)  # 结果显示

        """
        车牌图像区域
        """
        tip_label = Label(frame_pic,
                          text="车牌图片/监控：",
                          justify=LEFT,
                          padx=5,
                          pady=5,
                          font=("微软雅黑", 14)
                          )
        tip_label.pack(anchor=W)
        self.image_label = Label(frame_pic,
                            height=610,
                            width=700)
        self.set_pic(self.image_label, "/ui_source/img_bg.jpg")
        self.image_label.pack()

        """
        结果显示区域
        """
        zone_tip = Label(frame_res,
                         text="车牌区域(轮廓定位):",
                         padx=5,
                         pady=5,
                         font=("微软雅黑", 12)
                         ).pack(anchor=NW)
        self.zone_pic = Label(frame_res,
                         # text="暂无",
                         padx=5,
                         pady=5,
                         # height=3,
                         )
        self.set_pic(self.zone_pic, "/ui_source/null_img.jpg")
        self.zone_pic.pack(anchor=NW)

        color_tip = Label(frame_res,
                          text="车牌区域(颜色定位):",
                          padx=5,
                          pady=5,
                          font=("微软雅黑", 12)
                          ).pack(anchor=NW)

        self.color_pic = Label(frame_res,
                          # text="暂无",
                          padx=5,
                          pady=5,
                          # height=3,
                          )
        self.set_pic(self.color_pic, "/ui_source/null_img.jpg")
        self.color_pic.pack(anchor=NW)

        """
        字符分割结果显示
        """
        char_tip = Label(frame_res,
                         text="字符分割:",
                         padx=5,
                         pady=5,
                         font=("微软雅黑", 12)
                         ).pack(anchor=NW)
        char_pic_frame = Frame(frame_res)
        char_pic_frame.pack(anchor=N)

        self.pch1 = Label(char_pic_frame)
        self.pch1.grid(row=0, column=0, padx=1, pady=1)
        self.pch2 = Label(char_pic_frame)
        self.pch2.grid(row=0, column=1, padx=1, pady=1)
        self.pch3 = Label(char_pic_frame)
        self.pch3.grid(row=0, column=2, padx=1, pady=1)
        self.pch4 = Label(char_pic_frame)
        self.pch4.grid(row=0, column=3, padx=1, pady=1)
        self.pch5 = Label(char_pic_frame)
        self.pch5.grid(row=0, column=4, padx=1, pady=1)
        self.pch6 = Label(char_pic_frame)
        self.pch6.grid(row=0, column=5, padx=1, pady=1)
        self.pch7 = Label(char_pic_frame)
        self.pch7.grid(row=0, column=6, padx=1, pady=1)

        pch = [self.pch1, self.pch2, self.pch3, self.pch4, self.pch5, self.pch6, self.pch7]
        for i in range(7):
            self.set_pic(pch[i], "/ui_source/null_char.jpg")
        # set_pic(char_pic, "E:/ui_source/null_img.jpg")

        """
        识别结果显示
        """
        res_tip = Label(frame_res,
                        text="识别结果:",
                        padx=5,
                        pady=5,
                        font=("微软雅黑", 12)
                        ).pack(anchor=NW)

        # result.set("暂无")
        res_txt = Label(frame_res,
                        textvariable=self.result,
                        justify=LEFT,
                        padx=5,
                        pady=5,
                        font=("微软雅黑", 14)
                        ).pack(anchor=NW)

        """
        按键区域
        """
        frame_op = Frame(frame_res)  # 操作按钮框架
        frame_op.pack(anchor=N)

        choose_pic = Button(frame_op,
                            text="本地图片",
                            width=15,
                            font=("微软雅黑", 10),
                            command=self.choosepic
                            )
        choose_pic.grid(row=0, column=0, padx=5, pady=5)
        path = StringVar()
        file_entry = Entry(self.root, state='readonly', text=path)

        choose_vid = Button(frame_op,
                            text="本地视频",
                            width=15,
                            font=("微软雅黑", 10),
                            command=self.choosevid
                            )
        choose_vid.grid(row=0, column=1, padx=5, pady=5)

        choose_cam = Button(frame_op,
                            text="打开/关闭摄像头",
                            width=15,
                            font=("微软雅黑", 10),
                            command=self.video_start
                            )
        choose_cam.grid(row=1, column=0, padx=5, pady=5)

        take_photo = Button(frame_op,
                            text="拍照识别",
                            width=15,
                            font=("微软雅黑", 10),
                            command=self.capture_video
                            )
        take_photo.grid(row=1, column=1, padx=5, pady=5)

        record = Button(frame_op,
                            text="识别记录",
                            width=15,
                            font=("微软雅黑", 10),
                            command=self.show_record
                            )
        record.grid(row=2, column=0, padx=5, pady=5)

        hardware_use = Button(frame_op,
                            text="应用模拟",
                            width=15,
                            font=("微软雅黑", 10),
                            command=self.hard_ware
                            )
        hardware_use.grid(row=2, column=1, padx=5, pady=5)

        clear_btn = Button(frame_op,
                           text="清空数据",
                           width=15,
                           font=("微软雅黑", 10),
                           command=self.clear
                           )
        clear_btn.grid(row=3, column=0, padx=5, pady=5)

        quit_btn = Button(frame_op,
                          text="退出",
                          width=15,
                          font=("微软雅黑", 10),
                          command=self.quit_p
                          )
        quit_btn.grid(row=3, column=1, padx=5, pady=5)

        frame_pic.pack(side=LEFT, anchor=N)
        frame_res.pack(side=RIGHT, anchor=N)

    """
    图形显示函数，分为路径输入和cv图像输入
    """

    def set_pic(self,labelex, pathex):
        imgtk = ImageTk.PhotoImage(file=pathex)
        labelex.config(image=imgtk)
        labelex.image = imgtk

    def set_pic_cvimg(self,labelex, cv_img):
        cv_img = cv.cvtColor(cv_img, cv.COLOR_BGR2RGBA)
        img = Image.fromarray(cv_img)
        imgtk = ImageTk.PhotoImage(image=img)
        labelex.config(image=imgtk)
        labelex.image = imgtk



    """
    界面清空函数，恢复到初始界面
    """
    def clear(self):
        self.camera_switch = FALSE  # 关闭摄像头
        self.video_play=FALSE#停止视频播放
        self.set_pic(self.image_label, "/ui_source/img_bg.jpg")
        self.set_pic(self.zone_pic, "/ui_source/null_img.jpg")
        self.set_pic(self.color_pic, "/ui_source/null_img.jpg")
        pch = [self.pch1, self.pch2, self.pch3, self.pch4, self.pch5, self.pch6, self.pch7]
        for i in range(7):
            self.set_pic(pch[i], "/ui_source/null_char.jpg")
        self.result.set("        ")

    """
    本地图片选择
    """
    def choosepic(self):
        self.clear()
        path_ = askopenfilename()
        if path_ == '':
            img = cv.imread("/ui_source/img_bg_c1.jpg")
        else:
            img = cv.imdecode(np.fromfile(path_, dtype=np.uint8), -1)
        cvimg = cv.cvtColor(img, cv.COLOR_BGR2RGBA)
        # 图像大小等比例缩放
        shrink = max(img.shape[0] / 610, img.shape[1] / 700)
        if shrink > 1:
            imgsh = cv.resize(cvimg, (int(img.shape[1] / shrink), int(img.shape[0] / shrink)))
        else:
            imgsh = cvimg
        current_image = Image.fromarray(imgsh)
        imgtk = ImageTk.PhotoImage(image=current_image)
        self.image_label.config(image=imgtk)
        self.image_label.image = imgtk
        # 识别
        self.rec_type="本地图片"
        self.recognizingProcess(img)
    """
    本地视频
    """
    def choosevid(self):  # 视频
        self.clear()
        path_ = askopenfilename()
        if path_ != '':
            self.camera_vid = cv.VideoCapture(path_)
            self.video_play=TRUE
            success, img = self.camera_vid.read()
            if success:
                self.shrink = max(img.shape[0] / 610, img.shape[1] / 700)
            self.video_loop_path()

    def video_loop_path(self):
            success, img = self.camera_vid.read()
            if success and self.takePhoto:
                self.rec_type="本地视频"
                self.recognizingProcess(img)
                self.takePhoto = FALSE
            if success and self.video_play:
                # cv.waitKey(30)
                #img = cv.resize(img, (700, 610))
                if self.shrink > 1:
                    img = cv.resize(img, (int(img.shape[1] / self.shrink), int(img.shape[0] / self.shrink)))
                cvimage = cv.cvtColor(img, cv.COLOR_BGR2RGBA)  # 转换颜色从BGR到RGBA
                current_image = Image.fromarray(cvimage)  # 将图像转换成Image对象
                imgtk = ImageTk.PhotoImage(image=current_image)
                self.image_label.imgtk = imgtk
                self.image_label.config(image=imgtk)
                self.image_label.after(30, self.video_loop_path)


    """
    打开/关闭摄像头
    """
    def video_start(self):
        self.camera_switch = not self.camera_switch
        self.video_loop()

    def video_loop(self):
        success, img = self.camera.read()
        if success and self.takePhoto:
            self.rec_type="0号摄像头"
            self.recognizingProcess(img)
            self.takePhoto = FALSE
        if success and self.camera_switch:
            # cv.waitKey(30)
            cvimage = cv.cvtColor(img, cv.COLOR_BGR2RGBA)  # 转换颜色从BGR到RGBA
            current_image = Image.fromarray(cvimage)  # 将图像转换成Image对象
            imgtk = ImageTk.PhotoImage(image=current_image)
            self.image_label.imgtk = imgtk
            self.image_label.config(image=imgtk)
            self.image_label.after(30, self.video_loop)

    """
    拍照识别
    """
    def capture_video(self):
        self.set_pic(self.zone_pic, "/ui_source/null_img.jpg")
        self.set_pic(self.color_pic, "/ui_source/null_img.jpg")
        pch = [self.pch1, self.pch2, self.pch3, self.pch4, self.pch5, self.pch6, self.pch7]
        for i in range(7):
            self.set_pic(pch[i], "/ui_source/null_char.jpg")
        self.result.set("        ")
        self.takePhoto=TRUE
    """
    识别记录
    """
    def show_record(self):
        record=get_record(self.id)
        #print(record)
        self.recordPage=Toplevel()
        self.recordPage.title('识别记录')
        #self.recordPage.geometry('')

        """
        sbar= Scrollbar(self.recordPage)
        sbar.pack(side = RIGHT,fill = Y)
        recList = Listbox(self.recordPage, yscrollcommand=sbar.set)
        for i in range(1000):
            recList.insert(END, str(i),str(i+1))
        recList.pack(side=LEFT, fill=BOTH)
        sbar.config(command=recList.yview)  # 用config函数设置属性
        """
        label = Label(self.recordPage, text="识别记录", font=("Arial", 15)).grid(row=0, columnspan=3)
        # create Treeview with 3 columns
        cols = ('记录生成时间', '图像来源', '识别结果','用时(s)')
        listBox = ttk.Treeview(self.recordPage, columns=cols, show='headings')
        # set column headings
        for col in cols:
            listBox.heading(col, text=col)
        listBox.grid(row=1, column=0, columnspan=2)
        for i,rec in enumerate(record):
            listBox.insert("", "end", values=(rec[3], rec[1], rec[2],rec[4]))
        sbar = Scrollbar(self.recordPage, orient='vertical', command=listBox.yview)
        sbar.place(relx=0.971, rely=0.028, relwidth=0.024, relheight=0.958)
        # 给treeview添加配置
        listBox.configure(yscrollcommand=sbar.set)
        self.recordPage.mainloop()

    """"
    1号摄像头自动识别
    """
    def hard_ware(self):
        self.hardwarePage=Toplevel()
        #self.hardwarePage.geometry("500x700")
        self.rec_type="1号摄像头"
        self.camera1=cv.VideoCapture(1)
        self.hframe=Frame(self.hardwarePage)
        self.hframe.pack()
        Label(self.hframe,font=("微软雅黑", 14),text="自动识别模块").pack(anchor=N)
        self.auto_label=Label(self.hframe,
                              height=500,
                              width=500
                              )
        self.set_pic(self.auto_label, "/ui_source/img_bg.jpg")
        self.auto_label.pack()
        Label(self.hframe, font=("微软雅黑", 14),text="识别结果:").pack(anchor=NW)
        self.result.set("        ")
        Label(self.hframe, textvariable=self.result,font=("微软雅黑", 14)).pack(anchor=N)
        self.count=0
        self.auto_video_loop()#自动识别

        self.hardwarePage.mainloop()

    def auto_video_loop(self):
        success, img = self.camera1.read()
        if success and self.count>100:
            print("time up")
            self.recongnizingResult(img)
            self.count=0
        if success:
            # cv.waitKey(30)
            cvimage = cv.cvtColor(img, cv.COLOR_BGR2RGBA)  # 转换颜色从BGR到RGBA
            current_image = Image.fromarray(cvimage)  # 将图像转换成Image对象
            imgtk = ImageTk.PhotoImage(image=current_image)
            self.auto_label.imgtk = imgtk
            self.auto_label.config(image=imgtk)
            self.count+=1
            self.auto_label.after(30, self.auto_video_loop)
    """
    退出程序
    """
    def quit_p(self):
        root=self.root
        root.quit()
    """
    无过程识别（自动识别模块）
    """
    def recongnizingResult(self,img):
        self.start = cv.getTickCount()
        retb, color_zone = bpl.output_lp(img)
        if retb==True:
            zone=color_zone
        else:
            ret, zone_img = cpl.plate_zone(img)
            if ret==True:
                zone=zone_img
                retb == True
        if retb==True:
            temp_tresh = rud.remove_plate_upanddown_border(zone)
            noBorder, charList = cut.cutplate(temp_tresh)
            cur_dir = sys.path[0]
            ch_model_path = os.path.join(cur_dir, './model_ch/model.ckpt-530.meta')
            na_model_path = os.path.join(cur_dir, './model_na/model.ckpt-510.meta')
            ch_list = []
            na_list = []
            for i in range(len(charList)):
                cr = cv.resize(charList[i], (20, 20))
                if i == 0:
                    ch_list.append(cr)
                else:
                    na_list.append(cr)
            text = []
            text_ch = cm.cnn_recongnize_chinese(ch_list, ch_model_path)
            text_na = cm.cnn_recongnize_numalp(na_list, na_model_path)
            if len(text_ch)!=0:
                text.append(text_ch[0])
            for i in range(len(text_na)):
                text.append(text_na[i])
                if i == 0:
                    text.append("·")
            print(text)
            self.result.set(text)
            self.end = cv.getTickCount()
            cost_time = (self.end - self.start) / cv.getTickFrequency()
            print(cost_time)
            # print((self.end - self.start1) / cv.getTickFrequency())
            str_result = "".join(text)
            save_record(self.id, self.rec_type, str_result, str(cost_time))

            port_list = list(serial.tools.list_ports.comports())#查找串口
            if len(port_list)>0:#串口存在
                if len(text) == 7:  # 串口控制舵机
                    # 设置端口和波特率
                    s = serial.Serial(port='COM3', baudrate=9600)
                    myinput = bytes([0Xff, 0X09, 0X00, 0X00, 0X00])  # 需要发送的十六进制数据
                    # 端口写数
                    s.write(myinput)
                    # 关闭端口
                    s.close()
        else:
            print("未检测到车牌区域")


    """
    已获得图片信息，进行识别(输出过程信息)
    """

    def recognizingProcess(self,img):
        # 根据轮廓特征查找车牌区域
        self.start=cv.getTickCount()
        ret, zone_img = cpl.plate_zone(img)
        if ret == True:
            zone_img_cp = cv.resize(zone_img, (290, 80))
            self.set_pic_cvimg(self.zone_pic, zone_img_cp)
        else:
            print("未找到车牌区域(轮廓)")
        # 根据颜色定位查找车牌区域
        retb, color_zone = bpl.output_lp(img)
        if retb == True:
            color_zone_cp = cv.resize(color_zone, (275, 87))
            self.set_pic_cvimg(self.color_pic, color_zone_cp)
            self.cutRecognize(color_zone)
        else:
            print("未找到车牌区域(颜色)")
            if ret==True:
                self.cutRecognize(zone_img)



    def cutRecognize(self,img):  # 字符分割+识别
        #self.start1=cv.getTickCount()
        temp_tresh = rud.remove_plate_upanddown_border(img)
        noBorder, charList = cut.cutplate(temp_tresh)
        print(len(charList))
        #print(len(noBorder))
        if len(charList) != 0:
            pch = [self.pch1, self.pch2, self.pch3, self.pch4, self.pch5, self.pch6, self.pch7]
            for i in range(len(charList)):
                if i > 6:
                    break
                clt = cv.resize(charList[i], (40, 80))
                self.set_pic_cvimg(pch[i], clt)
        cur_dir = sys.path[0]
        # char_model_path = os.path.join(cur_dir, './model/model.ckpt-520.meta')
        ch_model_path = os.path.join(cur_dir, './model_ch/model.ckpt-530.meta')
        na_model_path = os.path.join(cur_dir, './model_na/model.ckpt-510.meta')
        #char_img_list = []
        ch_list = []
        na_list = []
        for i in range(len(charList)):
            cr = cv.resize(charList[i], (20, 20))
            # char_img_list.append(cr)
            if i == 0:
                ch_list.append(cr)
            else:
                na_list.append(cr)
        # text = cm.cnn_recongnize_char(char_img_list, char_model_path)
        # 识别
        #self.start1 = cv.getTickCount()
        text = []
        text_ch = cm.cnn_recongnize_chinese(ch_list, ch_model_path)
        text_na = cm.cnn_recongnize_numalp(na_list, na_model_path)
        if len(text_ch)!=0:
            text.append(text_ch[0])
        for i in range(len(text_na)):
            text.append(text_na[i])
            if i==0:
                text.append("·")
        print(text)
        self.result.set(text)
        self.end=cv.getTickCount()
        cost_time=(self.end-self.start)/cv.getTickFrequency()
        print(cost_time)
        #print((self.end - self.start1) / cv.getTickFrequency())
        str_result="".join(text)
        save_record(self.id,self.rec_type,str_result,str(cost_time))




if __name__=='__main__':
    root=Tk()
    Main(root,"admin1")
    root.mainloop()
