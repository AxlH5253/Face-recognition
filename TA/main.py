from PyQt4 import QtGui, QtCore
from picamera.array import PiRGBArray
from picamera import PiCamera
from trainner import train
import moveservo as mservo
import numpy as np
import sqlite3 as sql
import sys
import time
import cv2
import os

class Window(QtGui.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(135,30,1080,720)
        self.setWindowTitle("Aplikasi Pengenalan Wajah")
        self.setWindowIcon(QtGui.QIcon("assets/img/icon.png"))
        self.SetApp()

    def SetApp(self):
        
        self.image = None
        self.option="none"
        self.sampleNum = 0
        self.rec = cv2.face.createLBPHFaceRecognizer()
        self.rec.load("recognizer/trainningData.yml")
        
        self.txtAppTitle = QtGui.QLabel("Aplikasi Pengenalan Wajah Untuk Membuka",self)
        self.txtAppTitle.move(290,40)
        self.txtAppTitle.resize(600,30)
        self.txtAppTitle.setStyleSheet("font:20pt Comic Sans MS")
        
        self.txtAppTitle2 = QtGui.QLabel("Pintu Berbasis Raspberry Pi",self)
        self.txtAppTitle2.move(400,90)
        self.txtAppTitle2.resize(600,30)
        self.txtAppTitle2.setStyleSheet("font:20pt Comic Sans MS")
        
        self.progressbar = QtGui.QProgressBar(self)
        self.progressbar.setGeometry(30,670,840,20)
        self.progressbar.hide()
        
        self.btnTutupPintu = QtGui.QPushButton("Tutup Pintu",self)
        self.btnTutupPintu.move(500,275)
        self.btnTutupPintu.clicked.connect(self.close_door)
        
        self.txtDoorOpen = QtGui.QLabel("Pintu Sedang Terbuka!!!",self)
        self.txtDoorOpen.move(500,245)
        self.txtDoorOpen.resize(600,30)
        
        self.btnTambahData = QtGui.QPushButton("Tambah/ Update",self)
        self.btnTambahData.move(50,375)
        self.btnTambahData.clicked.connect(self.add_data_display)
        self.btnTambahData.resize(140,30)
        
        self.btnHapusData = QtGui.QPushButton("Hapus",self)
        self.btnHapusData.move(200,375)
        self.btnHapusData.clicked.connect(self.DeleteData)
        
        self.imgLabel = QtGui.QLabel(self)
        self.imgLabel.move(30,60)
        self.imgLabel.resize(1020,600)
        self.imgLabel.hide()
        
        self.txtInputName = QtGui.QLabel("Masukan Nama",self)
        self.txtInputName.move(900,120)
        self.txtInputName.resize(200,20)
        self.txtInputName.hide()
        
        self.txtInputId = QtGui.QLabel("Masukan ID",self)
        self.txtInputId.move(900,60)
        self.txtInputId.hide()
        
        self.inputName = QtGui.QLineEdit(self)
        self.inputName.move(900,145)
        self.inputName.resize(100,20)
        self.inputName.hide()
        
        self.inputId = QtGui.QLineEdit(self)
        self.inputId.move(900,85)
        self.inputId.resize(100,20)
        self.inputId.hide()
        
        self.btnKembaliBeranda = QtGui.QPushButton("Kembali",self)
        self.btnKembaliBeranda.move(10,10)
        self.btnKembaliBeranda.clicked.connect(self.open_door_display)
        self.btnKembaliBeranda.hide()
        
        self.btnRekamWajah = QtGui.QPushButton("Rekam Wajah",self)
        self.btnRekamWajah.move(900,185)
        self.btnRekamWajah.clicked.connect(self.conf_add_data)
        self.btnRekamWajah.hide()
        
        self.txtTableTitle = QtGui.QLabel("Tabel Data User Yang Terdaftar",self)
        self.txtTableTitle.move(50,145)
        self.txtTableTitle.resize(600,30)
        
        self.tabledata = QtGui.QTableWidget(self)
        self.tabledata.setRowCount(5)
        self.tabledata.setColumnCount(2)
        self.tabledata.setGeometry(50,175,222,182)
        
        self.tabledata.setHorizontalHeaderLabels(QtCore.QString("ID User;Nama User;").split(";"))
        self.tabledata.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        
        self.camera = PiCamera()
        self.camera.resolution = (640, 480)
        self.camera.framerate = 32
        
        self.loadTableData()
        self.timer = QtCore.QTimer(self)
        mservo.opendoor()
        
        self.show()
        
    def start_camera(self):
        self.capture = PiRGBArray(self.camera, size=(640, 480))
        self.face_cascade = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier('./haarcascade_eye.xml')
        
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)
    
    def stop_camera(self):
        self.timer.stop()

   
    def update_frame(self):
        for frame in self.camera.capture_continuous(self.capture, format="bgr", use_video_port=True):
            self.image = frame.array
            self.image = cv2.flip(self.image,1)
            #recog_face = self.recog_face(self.image)
            if(self.option=="none"):
                return self.display_image(self.image,1)
            elif(self.option=="detect"):
                detect_face = self.add_data(self.image)
                return self.display_image(detect_face,1)
            elif(self.option=="recog"):
                recog_face = self.recog_face(self.image)
                return self.display_image(recog_face,1)
            
    def display_image(self,img,window=1):
       self.capture.truncate(0)
       qtformat = QtGui.QImage.Format_Indexed8
       if(len(img.shape)==3):
           if(img.shape[2]==4):
               qtformat = QtGui.QImage.Format_RGBA8888
           else:
               qtformat = QtGui.QImage.Format_RGB888
       
       outImage = QtGui.QImage(img,img.shape[1],img.shape[0],img.strides[0],qtformat)
       outImage = outImage.rgbSwapped()
       
       if (window ==1):
           self.imgLabel.setPixmap(QtGui.QPixmap.fromImage(outImage))
           self.imgLabel.setScaledContents(True)
       self.capture.truncate(0)
    
    def close_door(self):
        mservo.closedoor()
        
        self.option ="recog"
        self.start_camera()
        
        self.close_door_display()
    
    def loadTableData(self):
        conn = sql.connect('FaceBase.db')
        cmd = "SELECT * FROM people"
        cursor = conn.execute(cmd)
        self.tabledata.setRowCount(0)
        for row_number, row_data in enumerate(cursor):
            self.tabledata.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tabledata.setItem(row_number, column_number, QtGui.QTableWidgetItem(str(data)))
                self.tabledata.item(row_number,column_number).setTextAlignment(QtCore.Qt.AlignCenter)
    
    def add_data_display(self):
        
        self.txtAppTitle.hide()
        self.txtAppTitle2.hide()
        self.btnTambahData.hide()
        self.btnTutupPintu.hide()
        self.txtDoorOpen.hide()
        self.tabledata.hide()
        self.btnHapusData.hide()
        self.txtTableTitle.hide()
        
        self.txtInputName.show()
        self.imgLabel.show()
        self.txtInputId.show()
        self.inputName.show()
        self.inputId.show()
        self.btnKembaliBeranda.show()
        self.btnRekamWajah.show()
        
        self.imgLabel.resize(840,600)
        
        self.start_camera()
    
    def open_door_display(self):
        
        self.btnTambahData.hide()
        self.txtInputName.hide()
        self.txtInputId.hide()
        self.inputName.hide()
        self.inputId.hide()
        self.btnKembaliBeranda.hide()
        self.btnRekamWajah.hide()
        self.imgLabel.hide()
        
        self.txtAppTitle.show()
        self.txtAppTitle2.show()
        self.btnTutupPintu.show()
        self.txtDoorOpen.show()
        self.btnTambahData.show()
        self.txtDoorOpen.show()
        self.tabledata.show()
        self.btnHapusData.show()
        self.txtTableTitle.show()
        
        self.inputId.setText("") 
        self.inputName.setText("")
        self.option ="none"
        
        self.loadTableData()
        
        self.stop_camera()
    
    def close_door_display(self):
        
        self.txtAppTitle.hide()
        self.txtAppTitle2.hide()
        self.btnTambahData.hide()
        self.txtInputName.hide()
        self.txtInputId.hide()
        self.inputName.hide()
        self.inputId.hide()
        self.btnKembaliBeranda.hide()
        self.btnRekamWajah.hide()
        self.btnTutupPintu.hide()
        self.txtDoorOpen.hide()
        self.tabledata.hide()
        self.btnHapusData.hide()
        self.txtTableTitle.hide()
        
        self.imgLabel.show()
        self.imgLabel.resize(1020,600)
    
    def recog_face(self,img):
        id=0
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_dect = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in face_dect:
            rectangle = cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,255), 3)
            id,conf=self.rec.predict(gray[y:y+h,x:x+w])
            cv2.putText(img,str(int(conf)),(x,y+h+30),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),1)
            if((id!=None or id!=0) and conf<=60):
                mservo.opendoor()
                self.open_door_display()
                SecondWindow(self,id).show()
                
                
        return img
        
    def conf_add_data(self):
        if((self.inputName.text()=="")or(self.inputId.text()=="")):
            warning = QtGui.QMessageBox.warning(self,'Kesalahan','Nama dan ID tidak boleh kosong!')
        else:
            if (self.chekRecordExist(self.inputId.text())==0):
                self.option ="detect"
            else:
                choice = QtGui.QMessageBox.question(self,'Opsi',
                                                    'Id '+self.inputId.text()+' sudah ada, apakah ingin mengganti data dari id '+self.inputId.text(),
                                                    QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
                if (choice == QtGui.QMessageBox.Yes):
                    self.option ="detect"
                else:
                    pass
       
        
    def add_data(self,img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_dect = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        rectangle = cv2.rectangle(img, (225,50), (475,375), (255,255,255), 3)
        for (x,y,w,h) in face_dect:
            self.progressbar.setValue(self.sampleNum*2)
            self.progressbar.show()
            if ((x>=250)and(x+w<=450)and(y>=50)and(y+h<=375)):
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = img[y:y+h, x:x+w]
                
                self.sampleNum += 1
                cv2.imwrite("dataset/user."+str(self.inputId.text())+"."+str(self.sampleNum)+".jpg",gray[y:y+h,x:x+w])
                
                eye_dect = self.eye_cascade.detectMultiScale(roi_gray)
                for (ex,ey,ew,eh) in eye_dect:
                    cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(255,0,0),2)
                if self.sampleNum == 20:
                    capture = PiRGBArray(self.camera)
                    self.camera.capture(capture, format="bgr")
                    image = capture.array
                    cv2.imwrite("user_image/"+str(self.inputId.text())+".jpg",image)
                    
                if self.sampleNum > 49:
                    self.progressbar.hide()
                    self.trainner()
                    self.insertOrUpdate(str(self.inputId.text()),str(self.inputName.text()))
                    self.inputId.setText("")
                    self.inputName.setText("")
                    self.option ="none"
                    self.sampleNum = 0
                    informasi = QtGui.QMessageBox.information(self,'Informasi','Data sudah ditambahkan')
        return img
    
    def trainner(self):
        train()
        self.rec = cv2.face.createLBPHFaceRecognizer()
        self.rec.load("recognizer/trainningData.yml")
    
    def insertOrUpdate(self, Id, Name):
        conn=sql.connect("FaceBase.db")
        isRecordExist = self.chekRecordExist(Id)
        if(isRecordExist==1):
            conn.execute("UPDATE People SET Name=? WHERE ID =?",(str(Name),str(Id)))
        else:
            conn.execute("INSERT INTO People(ID,Name) VALUES (?,?)",(str(Id),str(Name)))
        conn.commit()
        conn.close()
    
    def chekRecordExist(self, Id):
        conn=sql.connect("FaceBase.db")
        cmd="SELECT * FROM People WHERE ID="+str(Id)
        cursor=conn.execute(cmd)
        isRecordExist=0
        for row in cursor:
            isRecordExist=1
        return isRecordExist
    
    def DeleteData(self):
        DeleteWindow(self).show()
    
class SecondWindow(QtGui.QMainWindow):
    def __init__(self,parent=None,id=0):
        super(SecondWindow, self).__init__(parent)
        self.setGeometry(400,100,320,400)
        self.setWindowTitle("Dikenali")
        self.SetApp(id)

    def SetApp(self,id):
        profile = self.getProfile(id)
        self.LabelName = QtGui.QLabel("ID : "+str(id),self)
        self.LabelName.move(10,20)
        self.LabelName.resize(200,20)
        
        self.LabelName = QtGui.QLabel("Nama : "+str(profile[1]),self)
        self.LabelName.move(10,40)
        self.LabelName.resize(200,20)
        
        self.LabelImage = QtGui.QLabel(self)
        self.LabelImage.setPixmap(QtGui.QPixmap("user_image/"+str(id)+".jpg"))
        self.LabelImage.setScaledContents(True)
        self.LabelImage.move(10,70)
        self.LabelImage.resize(290,280)
        
        self.btnOk = QtGui.QPushButton("OK",self)
        self.btnOk.move(190,360)
        self.btnOk.clicked.connect(self.exitwindow)
        
    def getProfile(self,id):
        conn=sql.connect("FaceBase.db")
        cmd="SELECT * FROM People WHERE ID="+str(id)
        cursor=conn.execute(cmd)
        profile=None
        for row in cursor:
            profile=row
        conn.close()
        return profile
    
    def exitwindow(self):
        self.close()

class DeleteWindow(QtGui.QMainWindow):
    def __init__(self,parent=None):
        super(DeleteWindow, self).__init__(parent)
        self.setGeometry(400,75,400,200)
        self.setWindowTitle("Hapus Data")
        self.wn = parent
        self.SetApp()
    
    def SetApp(self):
        self.LabelName = QtGui.QLabel("Masukan ID User Yang Akan Dihapus",self)
        self.LabelName.move(30,30)
        self.LabelName.resize(300,30)
        
        self.inputID = QtGui.QLineEdit(self)
        self.inputID.move(30,60)
        self.inputID.resize(100,20)
        
        self.progressbar = QtGui.QProgressBar(self)
        self.progressbar.setGeometry(30,150,350,20)
        self.progressbar.hide()
        
        self.btnHapus = QtGui.QPushButton("Hapus",self)
        self.btnHapus.move(30,150)
        self.btnHapus.clicked.connect(self.deleteData)
        
        self.btnBatal = QtGui.QPushButton("Batal",self)
        self.btnBatal.move(170,150)
        self.btnBatal.clicked.connect(self.exitwindow)
    
    def deleteData(self):
        conn=sql.connect("FaceBase.db")
        jmlh = conn.execute("select count(id) from people")
        for row in jmlh:
            jumlah = row
        if((self.inputID.text()!="") and (int(jumlah[0])>0)):
            valuepbar = 0
            self.progressbar.setValue(valuepbar)
            self.progressbar.show()
            self.btnHapus.hide()
            self.btnBatal.hide()
            try:
                os.remove('user_image/'+str(self.inputID.text())+'.jpg')
            except:
                pass
            for i in range(1,51):
                try:
                    os.remove('dataset/user.'+str(self.inputID.text())+'.'+str(i)+'.jpg')
                    valuepbar+=0.8
                    self.progressbar.setValue(valuepbar)
                except:
                    valuepbar+=0.8
                    self.progressbar.setValue(valuepbar)
            conn=sql.connect("FaceBase.db")
            cmd="DELETE FROM People WHERE ID="+str(self.inputID.text())
            cursor=conn.execute(cmd)
            conn.commit()
            valuepbar+=3
            self.progressbar.setValue(valuepbar)
            Window.trainner(self.wn)
            valuepbar+=7
            self.progressbar.setValue(valuepbar)
            Window.rec = cv2.face.createLBPHFaceRecognizer()
            valuepbar+=2
            self.progressbar.setValue(valuepbar)
            Window.rec.load("recognizer/trainningData.yml")
            valuepbar+=8
            self.progressbar.setValue(valuepbar)
            
            Window.loadTableData(self.wn)
            
            self.exitwindow()
        else:
            pass
        conn.close()
    
    def exitwindow(self):
        self.close()
               
def run():
    app = QtGui.QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())

run()
