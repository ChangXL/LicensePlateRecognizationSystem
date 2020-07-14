
from tkinter.messagebox import *
from Main import *
from LoginMysql import *

class Login(object):
    def __init__(self, master=None):
        self.root = master  # 定义内部变量root
        self.root.title('License Plates Recognizing System-Login')
        self.root.geometry('450x270')  # 设置窗口大小
        self.username = StringVar()
        self.password = StringVar()
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root)  # 创建Frame
        self.page.pack()
        Label(self.page,height=2,font=("微软雅黑",16),text="欢迎使用").grid(row=0, column=0,stick=N)
        Label(self.page,height=2,font=("微软雅黑", 16),text="P&O车牌识别系统").grid(row=0, column=1, stick=W)
        Label(self.page, text='用户名: ',font=("微软雅黑",12)).grid(row=1, stick=W, pady=10)
        Entry(self.page,font=("微软雅黑",12),textvariable=self.username).grid(row=1, column=1, stick=E)
        Label(self.page, text='密码: ',font=("微软雅黑",12)).grid(row=2, stick=W, pady=10)
        Entry(self.page ,font=("微软雅黑",12),textvariable=self.password, show='*').grid(row=2, column=1, stick=E)
        Button(self.page, text='登陆',width=7,font=("微软雅黑",12), command=self.loginCheck).grid(row=3, stick=W, pady=10)
        Button(self.page, text='注册',width=7,font=("微软雅黑", 12), command=self.registerCheck).grid(row=3, column=1, stick=E)
        #Button(self.page, text='退出',font=("微软雅黑",12), command=self.page.quit).grid(row=3, column=1, stick=E)


    def loginCheck(self):
        id = self.username.get()
        password = self.password.get()
        if login_check(id,password):
            self.page.destroy()
            Main(self.root,id)
        else:
            showinfo(title='错误', message='账号不存在或密码错误！')


    def registerCheck(self):
        id = self.username.get()
        password = self.password.get()
        ret,res=register_check(id,password)
        if ret:
            showinfo(title='成功', message=res)
        else:
            showinfo(title='错误', message=res)



if __name__=='__main__':
    root=Tk()
    Login(root)
    root.mainloop()