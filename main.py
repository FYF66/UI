# -*- coding: utf-8 -*-

import sys
import serial
import serial.tools.list_ports
import PyQt5.QtWidgets as qw
from mainwindow import Ui_mainwindow
from PyQt5.QtCore import QTimer


class myMainWindow(qw.QMainWindow, Ui_mainwindow):
    def __init__(self):
        super(myMainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('串口调试')
        self.ser = serial.Serial()
        self.init()

        self.data_num_receive = ''
        self.receiveTxt.setText(str(self.data_num_receive))
        self.data_num_send = ''
        self.sendTxt.setText(str(self.data_num_send))

    def init(self):
        # 绑定信号与槽
        # 串口检测按钮
        self.comTest.clicked.connect(self.comTest_cb)
        # 串口信息显示
        self.comboBox_com.currentIndexChanged.connect(self.comboBox_com_cb)
        # 打开串口
        self.openbotton.clicked.connect(self.openbotton_cb)
        # 关闭串口
        self.closebotton.clicked.connect(self.port_close)
        # 发送数据按钮
        self.sendbotton.clicked.connect(self.data_send)
        # 更改波特率
        self.comboBox_baud.currentIndexChanged.connect(self.comboBox_baud_cb)

        # 清空接收按钮
        self.qingkong.clicked.connect(self.qingkong_cb)

        # 定时发送数据
        self.timer_send = QTimer()
        self.timer_send.timeout.connect(self.data_send)
        # self.timer_send_cb.stateChanged.connect(self.data_send_timer)

        # 定时器接收数据
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.data_receive)

    # 串口检测按钮
    def comTest_cb(self):
        self.comboBox_com.clear()
        # 检测所有存在的串口，将信息存储在字典中
        self.Com_Dict = {}
        port_list = list(serial.tools.list_ports.comports())

        for port in port_list:
            print(port)
            self.Com_Dict["%s" % port[0]] = "%s" % port[1]
            self.comboBox_com.addItem(port[0])
        if len(self.Com_Dict) == 0:
            self.comboBox_com.addItem('无串口')

    def comboBox_com_cb(self):
        com = self.comboBox_com.currentText()

    # 打开串口按钮
    def openbotton_cb(self):
        self.ser.port = self.comboBox_com.currentText()
        self.ser.baudrate = int(self.comboBox_baud.currentText())
        self.ser.bytesize = int(self.comboBox_data.currentText())
        self.ser.stopbits = int(self.comboBox_stop.currentText())
        self.ser.parity = self.comboBox_odd.currentText()

        try:
            self.ser.open()
        except:
            qw.QMessageBox.critical(self, "Port Error", "此串口不能被打开！")
            return None
        self.timer.start(1)
        self.openbotton.setEnabled(False)
        self.closebotton.setEnabled(True)

    # 关闭串口按钮
    def port_close(self):
        self.timer.stop()
        self.timer_send.stop()
        try:
            self.ser.close()
        except:
            pass
        self.openbotton.setEnabled(True)
        self.closebotton.setEnabled(False)

    # 接收数据和发送数据数目置零
    def qingkong_cb(self):
        self.data_num_received = ''
        self.receiveTxt.setText(str(self.data_num_received))
        self.data_num_sended = ''
        self.sendTxt.setText(str(self.data_num_sended))

    def comboBox_baud_cb(self):
        content = self.comboBox_baud.currentText()
        self.ser.baudrate = int(content)
        qw.QMessageBox.information(self, '提示', '更改波特率为:%s？' % content)

    # def sendbotton_cb(self):
    #     print('send')
    #     send_text = self.sendTxt.toPlainText()
    #     print(send_text)
    #     #加载到串口combobox上
    #     self.comboBox_com.addItem(send_text)

    def data_send(self):
        if self.ser.isOpen():
            input_s = self.sendTxt.toPlainText()
            self.receiveTxt.insertPlainText(input_s)
            if input_s != "":
                # 非空字符串
                if self.hexSend.isChecked():
                    # hex发送
                    input_s = input_s.strip()
                    send_list = []
                    while input_s != '':
                        try:
                            num = int(input_s[0:2], 16)
                        except ValueError:
                            qw.QMessageBox.critical(self, 'wrong data', '请输入十六进制数据，以空格分开!')
                            return None
                        input_s = input_s[2:].strip()
                        send_list.append(num)
                    input_s = bytes(send_list)
                else:
                    # ascii发送
                    input_s = (input_s + '\r\n').encode('utf-8')

                num = self.ser.write(input_s)
                self.data_num_send += str(num)
                # self.lineEdit_2.setText(str(self.data_num_send))
        else:
            qw.QMessageBox.information(self, '提示', '串口未打开')

        # 接收数据

    def data_receive(self):
        try:
            num = self.ser.inWaiting()
        except:
            self.port_close()
            return None
        if num > 0:
            data = self.ser.read(num)
            num = len(data)
            # hex显示
            if self.hexDisplay.checkState():
                out_s = ''
                for i in range(0, len(data)):
                    out_s = out_s + '{:02X}'.format(data[i]) + ' '
                self.receiveTxt.insertPlainText(out_s)
            else:
                # 串口接收到的字符串为b'123',要转化成unicode字符串才能输出到窗口中去
                self.receiveTxt.insertPlainText(data.decode('iso-8859-1'))

            # 统计接收字符的数量
            # self.data_num_received += num
            # self.lineEdit.setText(str(self.data_num_received))

            # 获取到text光标
            textCursor = self.receiveTxt.textCursor()
            # 滚动到底部
            textCursor.movePosition(textCursor.End)
            # 设置光标到text中去
            self.receiveTxt.setTextCursor(textCursor)
        else:
            pass


if __name__ == '__main__':
    app = qw.QApplication(sys.argv)

    MainWindow = myMainWindow()
    MainWindow.show()

    sys.exit(app.exec_())
