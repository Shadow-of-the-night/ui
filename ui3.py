from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *
import sys
import cv2
from voiceSynthesis import *
from recognize import *
import threading
from creatVoiceOfWav import *
from voiceRecognition import *

input_filename = "input.wav"               # 麦克风采集的语音输入
input_filepath = "C:\\Users\\黑夜的影子\\大创项目\\"              # 输入文件的path
in_path = input_filepath + input_filename

class Ui_MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)  # 父类的构造函数
        self.timer_getresult = QtCore.QTimer()  # 定义定时器，用于控制识别频率
        self.flag = 0  # 用于判断用户是否点击录制音频按钮
        self.getResult_time= 100 # 识别频率100ms
        self.set_ui()  # 初始化程序界面
        self.slot_init()  # 初始化槽函数

    '''程序界面布局'''

    def set_ui(self):
        self.__layout_main = QtWidgets.QHBoxLayout()  # 总布局
        self.__layout_data_show = QtWidgets.QVBoxLayout()  # 数据(视频)显示布局
        '''把按键加入到按键布局中'''
        #self.__layout_fun_button.addWidget(self.button_open_camera)  # 把打开摄像头的按键放到按键布局中
        '''总布局布置好后就可以把总布局作为参数传入下面函数'''
        self.setLayout(self.__layout_main)  # 到这步才会显示所有控件


        '''输入显示或参数调整区域布局'''
        # 图像转文字的结果显示框
        self.lb2 = QLabel(self)
        self.lb2.setGeometry(20, 10, 150, 30)
        self.lb2.setText('识别结果')
        self.lb2.setStyleSheet("color:blue")

        # 图像转文字的结果显示框
        self.lb22 = QLabel(self)
        self.lb22.setGeometry(20, 50, 300, 100)
        self.lb22.setStyleSheet('background-color: rgb(255, 255, 255)')
        self.lb22.setWordWrap(True)

        # 语音转文字的结果显示框
        self.lb2 = QLabel(self)
        self.lb2.setGeometry(20, 160, 150, 30)
        #self.lb2.setGeometry(720, 410, 150, 30)
        self.lb2.setText('语音转文字')
        self.lb2.setStyleSheet("color:blue")

        # 标签lb2的显示区域lb21（逻辑上的）
        self.lb21 = QLabel(self)
        self.lb21.setGeometry(20, 200, 300, 200)
        #self.lb21.setGeometry(720, 450, 300, 200)
        self.lb21.setStyleSheet('background-color: rgb(255, 255, 255)')
        self.lb21.setWordWrap(True)

        # 设置按钮 开始录音
        self.button_input_voice = QPushButton('点击开始录音', self)
        self.button_input_voice.setGeometry(100, 410, 130, 50)

        self.lb3 = QLabel(self)
        self.lb3.setGeometry(80, 450, 300, 50)
        self.lb3.setText('按钮变蓝表示正在录音')
        self.lb3.setStyleSheet("color:black")

        # 当前识别频率显示
        self.lb4 = QLabel(self)
        self.lb4.setGeometry(20, 500, 300, 30)
        self.lb4.setText('当前识别频率:' + str(self.getResult_time) + 'ms/per')
        self.lb4.setStyleSheet("color:black")

        self.lb3 = QLabel(self)
        self.lb3.setGeometry(20, 540, 300, 30)
        # self.lb3.setGeometry(720, 160, 200, 30)
        self.lb3.setText('请输入识别频率( ms/per)')
        self.lb3.setStyleSheet("color:black")

        self.frequency = QLineEdit(self)
        self.frequency.setGeometry(20, 570, 300, 50)
        # self.url.setGeometry(720, 200, 300, 50)
        self.frequency.setPlaceholderText("")

        # 设置ui界面位置大小
        self.setGeometry(1550, 50, 340, 700)
        # 不让用户ui界面调节大小
        self.setFixedSize(340, 700)
        # 设置按钮 开始识别
        self.button_begin_recognize = QPushButton('开始识别', self)
        self.button_begin_recognize.setGeometry(20,650,100, 50)

        self.button_change_frequently = QPushButton('修改参数', self)
        self.button_change_frequently.setGeometry(200, 650, 100, 50)
        # 设置窗口的标题
        self.setWindowTitle('ui界面')


    '''初始化所有槽函数'''

    def slot_init(self):
        self.button_begin_recognize.clicked.connect(self.button_begin_recognize_clicked)  # 若该按键被点击，则调用button_open_camera_clicked()
        self.button_change_frequently.clicked.connect(self.button_change_frequently_clicked)  # 若该按键被点击，则调用button_change_frequently_clicked()
        self.timer_getresult.timeout.connect(self.get_result)  # 若定时器结束，则调用get_result()
        if(self.flag==0):
            self.button_input_voice.clicked.connect(self.voice_to_text)
            self.flag=1
        else:
            self.lb3.setText('请点击开始录制')


    '''槽函数'''

    '''1.打开计时器调用识别函数得到识别结果显示'''
    def button_begin_recognize_clicked(self):
        if self.timer_getresult.isActive() == False:  # 若定时器未启动
                self.timer_getresult.start(self.getResult_time) # 启动定时器
                print("计时器已经启动")
                self.button_begin_recognize.setText('结束识别') #修改按钮信息
        else:
            self.timer_getresult.stop()  # 关闭定时器
            print("计时器已经关闭")
            self.button_begin_recognize.setText('打开识别') #修改按钮信息

    '''2.修改识别频率'''
    def button_change_frequently_clicked(self):
        frequency=self.frequency.text()
        self.getResult_time=int(frequency)
        self.lb4.setText('当前识别频率:' + frequency + 's/per')
        print("识别频率修改成功")

    '''3.每隔识别频率获取识别结果并播放识别结果音频
        self.getResult_time ---识别频率
    '''
    def get_result(self):
        pre_pic('D:\\1.8.0\\savepic\\pic.jpg')#预处理当前的图片    #注这里的路径读取的是小觅api保存的图片的路径
        word = test_one_image('temp.jpg')#获取当前图片识别的结果
        self.lb22.setText(word)#将识别结果放到ui界面显示
        time1 = word_to_voice(word)#播放识别出来的音频
        #开启线程来播放音频，以免阻碍识别
        music = threading.Thread(target=bofan, args=(time1,))
        music.start()
        #stop_thread(music)

    '''4.音频转文字'''
    def voice_to_text(self):
        get_audio(in_path,5) #录制4s的音频
        text = voice_to_context()
        self.lb21.setText(text)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)  # 固定的，表示程序应用
    ui = Ui_MainWindow()  # 实例化Ui_MainWindow
    ui.show()  # 调用ui的show()以显示。同样show()是源于父类QtWidgets.QWidget的
    sys.exit(app.exec_())  # 不加这句，程序界面会一闪而过