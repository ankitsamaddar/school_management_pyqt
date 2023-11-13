from datetime import datetime
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import sys
from PyQt6.uic import loadUiType
import mysql.connector as con

from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog

ui, _ = loadUiType('schl_mgmt_app/qt_ui/school.ui')


class AspectRatioSizeGrip(QSizeGrip):
    def mouseMoveEvent(self, event):
        # Get the main window (parent of the size grip)
        window = self.window()

        # Calculate the new size of the window
        diff = event.globalPosition().toPoint() - window.geometry().topLeft()
        newSize = diff.boundedTo(
            window.maximumSize()).expandedTo(window.minimumSize())

        # Maintain the aspect ratio
        ratio = window.width() / window.height()
        newSize.setHeight(newSize.width() / ratio)

        # Resize the window
        window.resize(newSize)


class MainApp(QMainWindow, ui):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        # Fix Window Size
        self.setFixedSize(self.size())

        # login module
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.tabBar().setVisible(False)
        self.menubar.setVisible(False)
        self.b01.clicked.connect(self.login)

        # add student module
        self.menu_01_01.triggered.connect(self.show_add_new_student)
        self.b12.clicked.connect(self.save_student_details)
        self.b11.clicked.connect(
            lambda: self.calculateAge(self.tb13, self.tb14))  # calculate age

        # modify student module
        self.menu_01_02.triggered.connect(self.show_edit_or_delete_student)
        self.cb21.currentIndexChanged.connect(self.fetch_student_details)
        self.b21.clicked.connect(self.update_student_details)
        self.b22.clicked.connect(self.delete_student_details)
        self.b23.clicked.connect(
            lambda: self.calculateAge(self.tb22, self.tb23))  # calculate age

        # add or edit marks module
        self.menu_02_01.triggered.connect(self.show_add_or_edit_marks)
        self.b31.clicked.connect(self.save_marks_details)
        self.cb33.currentIndexChanged.connect(self.marks_fetch_exams)
        self.b32.clicked.connect(self.fetch_exam_marks)
        self.b33.clicked.connect(self.update_exam_marks)
        self.b34.clicked.connect(self.delete_exam_marks)

        # add or edit attendance module
        self.menu_03_01.triggered.connect(self.show_attendance)
        self.b41.clicked.connect(self.save_attendance_details)
        self.cb42.currentIndexChanged.connect(self.attendance_fetch_dates)
        self.b44.clicked.connect(self.fetch_attendance_details)
        self.b42.clicked.connect(self.update_attendance_details)
        self.b43.clicked.connect(self.delete_attendance_details)

        # add or edit fees module
        self.menu_04_01.triggered.connect(self.show_fees)
        self.b51.clicked.connect(self.save_fees_details)
        # Print Action
        self.b81.clicked.connect(self.print_receipt)
        self.b81.clicked.connect(lambda: self.tabWidget.setCurrentIndex(1))
        self.b82.clicked.connect(lambda: self.tabWidget.setCurrentIndex(1))
        self.cb52.currentIndexChanged.connect(self.fetch_receipt_details)
        self.b52.clicked.connect(self.update_fees_details)
        self.b53.clicked.connect(self.delete_fees_details)

        # Reports Module
        self.menu_05_01.triggered.connect(self.show_report)
        self.menu_05_02.triggered.connect(self.show_report)
        self.menu_05_03.triggered.connect(self.show_report)
        self.menu_05_04.triggered.connect(self.show_report)

        # Logout
        self.menu_06_01.triggered.connect(self.logout)

###### Login Form ######
    def login(self):
        un = self.tb01.text()
        pw = self.tb02.text()
        if (un == "admin" and pw == "admin"):
            self.menubar.setVisible(True)
            self.tabWidget.setCurrentIndex(1)
        else:
            QMessageBox.information(
                self, "School Management System", "Invalid Credentials! Try Again !")
            self.l01.setText("Invalid Credentials !!")

###### Add Student ######
    def show_add_new_student(self):
        self.tabWidget.setCurrentIndex(2)
        self.fill_registration_number()

    def fill_registration_number(self):
        try:
            rn = 0
            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")
            cursor = mydb.cursor(buffered=True, dictionary=True)
            cursor.execute("select * from student")
            result = cursor.fetchall()
            if result:
                for stud in result:
                    rn += 1
            self.tb11.setText(str(rn+1))
        except con.Error as e:
            print("Error Occurred in Connecting to school_db" + str(e))

    def save_student_details(self):
        try:
            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")
            cursor = mydb.cursor(buffered=True, dictionary=True)

            # Now execute your actual SELECT query
            cursor.execute("SELECT * FROM student")

            registration_number = self.tb11.text()
            full_name = self.tb12.text()
            dob = self.tb13.text()
            age = self.tb14.text()
            phone = self.tb15.text()
            email = self.tb16.text()
            address = self.mtb11.toPlainText()
            gender = self.cb11.currentText()
            standard = self.cb12.currentText()

            qry = "INSERT INTO student (registration_number, full_name, gender, dob, age, address, phone, email, standard) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            value = (registration_number, full_name, gender,
                     dob, age, address, phone, email, standard)
            cursor.execute(qry, value)
            mydb.commit()

            self.l11.setText("Student Details Saved Successfully !!")
            QMessageBox.information(
                self, "School Management System", "Student Details Saved Successfully !!")
            # Reset Fields
            self.tb11.setText("")
            self.tb12.setText("")
            self.tb13.setDate(QDate())
            self.tb14.setText("")
            self.tb15.setText("")
            self.tb16.setText("")
            self.mtb11.setText("")
            self.l11.setText("")
            self.tabWidget.setCurrentIndex(1)

        except con.Error as e:
            self.l11.setText("Error! Could not Save Student Details ! ")
            print("Error Occurred in Connecting to school_db " + str(e))

    def calculateAge(self, dob, set_age):
        dob_text = dob.text()

        try:
            # dob_text string to datetime object
            dob_date = datetime.strptime(dob_text, "%d-%m-%Y").date()

            # Calculate age based on today's date
            today = QDate.currentDate().toPyDate()
            age = today.year - dob_date.year - \
                ((today.month, today.day) < (dob_date.month, dob_date.day))

            set_age.setText(str(age))  # set age
        except ValueError:
            print("Invalid DOB format")

###### Edit / Delete Student ######
    def show_edit_or_delete_student(self):
        self.tabWidget.setCurrentIndex(3)
        self.fetch_registration_number()

    def fetch_registration_number(self):
        try:
            self.cb21.clear()
            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")
            cursor = mydb.cursor(buffered=True, dictionary=True)
            cursor.execute("select * from student")
            result = cursor.fetchall()
            if result:
                for stud in result:
                    # print(stud.keys())
                    self.cb21.addItem(str(stud['registration_number']))

        except con.Error as e:
            print("Error Occurred in Connecting to school_db " + str(e))

    def fetch_student_details(self):
        try:
            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")
            cursor = mydb.cursor(buffered=True, dictionary=True)
            cursor.execute(
                "select * from student where registration_number = '"+self.cb21.currentText()+"'")
            result = cursor.fetchall()
            if result:
                for stud in result:
                    self.tb21.setText(str(stud['full_name']))
                    self.tb22.setDate(QDate.fromString(
                        str(stud['dob']), "dd-MM-yyyy"))
                    self.tb23.setText(str(stud['age']))
                    self.tb24.setText(str(stud['phone']))
                    self.tb25.setText(str(stud['email']))
                    self.mtb21.setText(str(stud['address']))
                    self.cb22.setCurrentText(str(stud['gender']))
                    self.cb23.setCurrentText(str(stud['standard']))

        except con.Error as e:
            print("Error Occurred in Connecting to school_db " + str(e))

    def update_student_details(self):
        try:
            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")
            cursor = mydb.cursor(buffered=True, dictionary=True)

            registration_number = self.cb21.currentText()
            full_name = self.tb21.text()
            dob = self.tb22.text()
            age = self.tb23.text()
            phone = self.tb24.text()
            email = self.tb25.text()
            address = self.mtb21.toPlainText()
            gender = self.cb22.currentText()
            standard = self.cb23.currentText()

            qry = "UPDATE student set full_name = '" + full_name + "', gender = '" + gender + "', dob = '" + dob + "', age = '" + age + "', address = '" + \
                address + "', phone = '" + phone + "', email = '" + email + "', standard = '" + \
                standard + "' where registration_number = '" + registration_number + "'"

            cursor.execute(qry)
            mydb.commit()

            self.l21.setText("Student Details Modified Successfully !!")
            QMessageBox.information(
                self, "School Management System", "Student Details Modified Successfully !!")
            # Reset Fields
            self.cb21.clear()
            self.tb11.setText("")
            self.tb12.setText("")
            self.tb13.setDate(QDate())
            self.tb14.setText("")
            self.tb15.setText("")
            self.tb16.setText("")
            self.mtb11.setText("")
            self.l21.setText("")
            self.tabWidget.setCurrentIndex(1)

        except con.Error as e:
            self.l21.setText("Error! Could not Modify Student Details ! ")
            print("Error Occurred in Connecting to school_db " + str(e))

    def delete_student_details(self):
        query = QMessageBox.question(
            self, "Delete", "Are you sure you\nWant to delete This Student details?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if query == QMessageBox.StandardButton.Yes:
            try:
                mydb = con.connect(host="localhost", user="root",
                                   password="", db="school_db")

                cursor = mydb.cursor(buffered=True, dictionary=True)
                registration_number = self.cb21.currentText()

                qry = "delete from student where registration_number = '" + registration_number + "'"
                cursor.execute(qry)
                mydb.commit()
                self.l21.setText("Student Details Deleted Successfully !!")
                QMessageBox.information(
                    self, "School Management System", "Student Details Deleted Successfully !!")
                # Reset fields
                self.cb21.clear()
                self.l21.setText("")
                self.tabWidget.setCurrentIndex(1)
            except con.Error as e:
                self.l21.setText("Error! Could not Modify Student Details ! ")
                print("Error Occurred in Connecting to school_db " + str(e))

###### Add / Update Marks Details ######
    def show_add_or_edit_marks(self):
        self.tabWidget.setCurrentIndex(4)
        self.marks_fetch_registration_number()

    def marks_fetch_registration_number(self):
        try:
            self.cb31.clear()
            self.cb33.clear()
            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")
            cursor = mydb.cursor(buffered=True, dictionary=True)
            cursor.execute("select * from student")
            result = cursor.fetchall()
            if result:
                for stud in result:
                    # print(stud.keys())
                    self.cb31.addItem(str(stud['registration_number']))
                    self.cb33.addItem(str(stud['registration_number']))

        except con.Error as e:
            print("Error Occurred in Connecting to school_db " + str(e))

    def save_marks_details(self):
        try:
            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")
            cursor = mydb.cursor(buffered=True, dictionary=True)

            registration_number = self.cb31.currentText()
            exam_name = self.cb32.currentText()
            language = self.tb31.text()
            maths = self.tb32.text()
            science = self.tb33.text()
            arts = self.tb34.text()

            qry = "INSERT INTO marks (registration_number, exam_name, language, maths, science, arts) VALUES (%s, %s, %s, %s, %s, %s)"
            value = (registration_number, exam_name,
                     language, maths, science, arts)
            cursor.execute(qry, value)
            mydb.commit()

            self.l31.setText("Marks Saved Successfully !!")
            QMessageBox.information(
                self, "School Management System", "Marks Saved Successfully !!")
            # Reset Fields
            self.cb31.currentText()
            self.cb32.setCurrentIndex(-1)
            self.tb31.setText("")
            self.tb32.setText("")
            self.tb33.setText("")
            self.tb34.setText("")
            self.l31.setText("")
            self.tabWidget.setCurrentIndex(1)

        except con.Error as e:
            self.l31.setText("Error! Marks Not Saved ! ")
            print("Error Occurred in Connecting to school_db " + str(e))

    def marks_fetch_exams(self):
        try:
            self.cb34.clear()
            registration_number = self.cb33.currentText()
            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")
            cursor = mydb.cursor(buffered=True, dictionary=True)
            cursor.execute(
                "select * from marks where registration_number = '" + registration_number + "'")
            result = cursor.fetchall()
            if result:
                for stud in result:
                    self.cb34.addItem(stud.get('exam_name', ''))

        except con.Error as e:
            print("Error Occurred in Connecting to school_db " + str(e))

    def fetch_exam_marks(self):
        try:
            registration_number = self.cb33.currentText()
            exam_name = self.cb34.currentText()
            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")
            cursor = mydb.cursor(buffered=True, dictionary=True)
            cursor.execute(
                "select * from marks where registration_number = '" + registration_number + "' and exam_name='" + exam_name + "'")
            result = cursor.fetchall()
            if result:
                for stud in result:
                    self.tb35.setText(str(stud['language']))
                    self.tb36.setText(str(stud['maths']))
                    self.tb37.setText(str(stud['science']))
                    self.tb38.setText(str(stud['arts']))

        except con.Error as e:
            print("Error Occurred in Connecting to school_db " + str(e))

    def update_exam_marks(self):
        try:
            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")
            cursor = mydb.cursor(buffered=True, dictionary=True)

            registration_number = self.cb33.currentText()
            exam_name = self.cb34.currentText()

            language = self.tb35.text()
            maths = self.tb36.text()
            science = self.tb37.text()
            arts = self.tb38.text()

            qry = "UPDATE marks set language = '" + language + "', maths = '" + maths + "', science = '" + science + \
                "', arts = '" + arts + "' where registration_number = '" + \
                registration_number + "' and exam_name='" + exam_name + "'"

            cursor.execute(qry)
            mydb.commit()

            self.l32.setText("Marks Modified Successfully !!")
            QMessageBox.information(
                self, "School Management System", "Marks Modified Successfully !!")
            # Reset Fields
            self.tb35.setText("")
            self.tb36.setText("")
            self.tb37.setText("")
            self.tb38.setText("")
            self.l32.setText("")
            self.tabWidget.setCurrentIndex(1)

        except con.Error as e:
            self.l21.setText("Error! Modification Unsuccessful ! ")
            print("Error Occurred in Connecting to school_db " + str(e))

    def delete_exam_marks(self):
        query = QMessageBox.question(
            self, "Delete", "Are you sure you\nWant to delete This Exam Marks?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if query == QMessageBox.StandardButton.Yes:
            try:
                mydb = con.connect(host="localhost", user="root",
                                   password="", db="school_db")

                cursor = mydb.cursor(buffered=True, dictionary=True)
                registration_number = self.cb33.currentText()
                exam_name = self.cb34.currentText()

                qry = "delete from marks where registration_number = '" + \
                    registration_number + "' and exam_name='" + exam_name + "'"
                cursor.execute(qry)
                mydb.commit()
                self.l32.setText("Marks Deleted Successfully !!")
                QMessageBox.information(
                    self, "School Management System", "Marks Deleted Successfully !!")
                # Reset fields
                self.tb35.setText("")
                self.tb36.setText("")
                self.tb37.setText("")
                self.tb38.setText("")
                self.l32.setText("")
                self.tabWidget.setCurrentIndex(1)
            except con.Error as e:
                self.l32.setText("Error! Could not Delete Marks ! ")
                print("Error Occurred in Connecting to school_db " + str(e))

###### Add / Update Attendance ######
    def show_attendance(self):
        self.tabWidget.setCurrentIndex(5)
        self.attendance_fetch_registration_number()
        self.tb41.setDate(QDate.currentDate())  # Set Date to current Date
        # Empty Attendance Fields
        self.tb42.setCurrentIndex(-1)
        self.tb43.setCurrentIndex(-1)
        self.tb44.setCurrentIndex(-1)
        self.tb45.setCurrentIndex(-1)

    def attendance_fetch_registration_number(self):
        try:
            self.cb41.clear()
            self.cb42.clear()
            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")
            cursor = mydb.cursor(buffered=True, dictionary=True)
            cursor.execute("select * from student")
            result = cursor.fetchall()
            if result:
                for stud in result:
                    # print(stud.keys())
                    self.cb41.addItem(str(stud['registration_number']))
                    self.cb42.addItem(str(stud['registration_number']))

        except con.Error as e:
            print("Error Occurred in Connecting to school_db " + str(e))

    def save_attendance_details(self):
        try:
            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")
            cursor = mydb.cursor(buffered=True, dictionary=True)

            registration_number = self.cb41.currentText()
            attendance_date = self.tb41.text()
            morning = self.tb42.currentText()
            evening = self.tb43.currentText()

            qry = "INSERT INTO attendance (registration_number, attendance_date, morning, evening) VALUES (%s, %s, %s, %s)"
            value = (registration_number, attendance_date, morning, evening)
            cursor.execute(qry, value)
            mydb.commit()

            self.l41.setText("Attendance Saved Successfully !!")
            QMessageBox.information(
                self, "School Management System", "Attendance Saved Successfully !!")
            # Reset Fields
            self.tb42.setCurrentIndex(0)
            self.tb43.setCurrentIndex(0)
            self.l41.setText("")
            self.tabWidget.setCurrentIndex(1)

        except con.Error as e:
            self.l41.setText("Error! Attendance Not Saved ! ")
            print("Error Occurred in Connecting to school_db " + str(e))

    def attendance_fetch_dates(self):
        try:
            self.cb43.clear()
            registration_number = self.cb42.currentText()

            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")
            cursor = mydb.cursor(buffered=True, dictionary=True)
            cursor.execute(
                "select * from attendance where registration_number = '" + registration_number + "'")
            result = cursor.fetchall()
            if result:
                for stud in result:
                    self.cb43.addItem(stud.get('attendance_date', ''))

        except con.Error as e:
            print("Error Occurred in Connecting to school_db " + str(e))

    def fetch_attendance_details(self):
        try:
            registration_number = self.cb42.currentText()
            attendance_date = self.cb43.currentText()

            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")
            cursor = mydb.cursor(buffered=True, dictionary=True)
            cursor.execute(
                "select * from attendance where registration_number = '" + registration_number + "' and attendance_date='" + attendance_date + "'")
            result = cursor.fetchall()
            if result:
                for stud in result:
                    self.tb44.setCurrentText(str(stud['morning']))
                    self.tb45.setCurrentText(str(stud['evening']))

        except con.Error as e:
            print("Error Occurred in Connecting to school_db " + str(e))

    def update_attendance_details(self):
        try:
            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")
            cursor = mydb.cursor(buffered=True, dictionary=True)

            registration_number = self.cb42.currentText()
            attendance_date = self.cb43.currentText()

            morning = self.tb44.currentText()
            evening = self.tb45.currentText()

            qry = "UPDATE attendance set morning = '" + morning + "', evening = '" + evening + "' where registration_number = '" + \
                registration_number + "' and attendance_date='" + attendance_date + "'"

            cursor.execute(qry)
            mydb.commit()

            self.l42.setText("Attendance Modified Successfully !!")
            QMessageBox.information(
                self, "School Management System", "Attendance Modified Successfully !!")
            # Reset Fields
            self.tb44.setCurrentIndex(-1)
            self.tb45.setCurrentIndex(-1)
            self.l42.setText("")
            self.tabWidget.setCurrentIndex(1)

        except con.Error as e:
            self.l42.setText("Error! Modification Unsuccessful ! ")
            print("Error Occurred in Connecting to school_db " + str(e))

    def delete_attendance_details(self):
        query = QMessageBox.question(
            self, "Delete", "Are you sure you\nWant to delete This Attendance Details?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if query == QMessageBox.StandardButton.Yes:
            try:
                mydb = con.connect(host="localhost", user="root",
                                   password="", db="school_db")
                cursor = mydb.cursor(buffered=True, dictionary=True)
                registration_number = self.cb42.currentText()
                attendance_date = self.cb43.currentText()

                qry = "delete from attendance where registration_number = '" + \
                    registration_number + "' and attendance_date='" + attendance_date + "'"
                cursor.execute(qry)
                mydb.commit()
                self.l42.setText("Attendance Deleted Successfully !!")
                QMessageBox.information(
                    self, "School Management System", "Attendance Deleted Successfully !!")
                # Reset fields
                self.tb44.setCurrentIndex(-1)
                self.tb45.setCurrentIndex(-1)
                self.l42.setText("")
                self.tabWidget.setCurrentIndex(1)
            except con.Error as e:
                self.l42.setText("Error! Could not Delete Attendance ! ")
                print("Error Occurred in Connecting to school_db " + str(e))

###### Add Fees ######
    def show_fees(self):
        self.tabWidget.setCurrentIndex(6)
        self.fees_fetch_registration_number()
        self.fill_next_receipt_number()
        # Set Current Date and Month
        self.db51.setDate(QDate.currentDate())  # Set Date to current Date
        self.cb53.setCurrentIndex(
            datetime.now().month - 1)  # Choose Current Month
        # Fetch Receipt
        self.fees_fetch_receipt_number()

    def fees_fetch_registration_number(self):
        try:
            self.cb51.clear()

            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")
            cursor = mydb.cursor(buffered=True, dictionary=True)
            cursor.execute("select * from student")
            result = cursor.fetchall()
            if result:
                for stud in result:
                    self.cb51.addItem(str(stud['registration_number']))

        except con.Error as e:
            print("Error Occurred in Connecting to school_db " + str(e))

    def fill_next_receipt_number(self):
        try:
            rn = 0
            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")
            cursor = mydb.cursor(buffered=True, dictionary=True)
            cursor.execute("select * from fees")
            result = cursor.fetchall()
            if result:
                for stud in result:
                    rn += 1
            self.tb51.setText(str(rn+1))
            self.tb51.setReadOnly(True)  # Receipt Number Filed is READ_ONLY

        except con.Error as e:
            print("Error Occurred in Connecting to school_db" + str(e))

    def save_fees_details(self):
        try:
            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")

            # Use MySQLCursorBuffered
            cursor = mydb.cursor(buffered=True, dictionary=True)

            receipt_number = self.tb51.text()
            registration_number = self.cb51.currentText()
            month = self.cb53.currentText()
            amount = self.tb52.text()
            fees_date = self.db51.text()

            qry = "INSERT INTO fees (receipt_number, registration_number, month, amount, fees_date) VALUES (%s, %s, %s, %s, %s)"
            value = (receipt_number, registration_number,
                     month, amount, fees_date)
            cursor.execute(qry, value)
            mydb.commit()

            self.l51.setText("Fees Details Saved Successfully !!")
            self.l51.adjustSize()
            QMessageBox.information(
                self, "School Management System", "Fees Details Saved Successfully !!")
            # Reset Fields
            self.tb52.setText("")
            self.l51.setText("")

            # Set RECEIPT fields
            self.l81.setText(str(receipt_number))
            self.l82.setText(str(fees_date))
            self.l84.setText(str(amount))
            self.l85.setText(str(month))
            self.l86.setText(str(registration_number))
            cursor.execute(
                "select * from student where registration_number = '"+registration_number+"'")
            result = cursor.fetchall()
            if result:
                for stud in result:
                    self.l83.setText(str(stud['full_name']))
                    self.l87.setText(str(stud['phone']))
                    self.l88.setText(str(stud['email']))
                    self.l89.setText(str(stud['standard']))

            self.tabWidget.setCurrentIndex(8)

        except con.Error as e:
            self.l51.setText("Error! Fees Details Not Saved ! ")
            self.l51.adjustSize()
            print("Error Occurred in Connecting to school_db " + str(e))

###### Print Modules ######
    def print_receipt(self):
        printer = QPrinter()
        printer.setResolution(300)

        # Set the page layout to landscape and margins to 0
        layout = QPageLayout()
        layout.setOrientation(QPageLayout.Orientation.Landscape)
        layout.setMargins(QMarginsF(0, 0, 0, 0))
        printer.setPageLayout(layout)

        # Create a QPrintPreviewDialog
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(self.print_preview)
        preview.exec()

    def print_preview(self, printer):
        # Access the current tab's content
        original_widget = self.tabWidget.currentWidget()
        if original_widget:
            # Create a copy of the current_widget
            current_widget = QWidget()
            current_widget.resize(original_widget.size())
            current_widget.setStyleSheet("background-color: white;")

            # Set all QLabel to black and remove all QPushButton
            for child in original_widget.findChildren((QLabel, QPushButton)):
                if isinstance(child, QLabel):
                    label = QLabel(current_widget)
                    label.setText(child.text())
                    label.setGeometry(child.geometry())
                    label.setFont(child.font())
                    label.setLayoutDirection(child.layoutDirection())
                    label.setStyleSheet("color: black;")

            # Create a QPixmap and render the current_widget onto it
            pixmap = QPixmap(current_widget.size())
            current_widget.render(pixmap)

            # Scale the pixmap to fit the page
            width = printer.width()
            aspect_ratio = pixmap.width() / pixmap.height()
            height = int(width / aspect_ratio)
            scaled_pixmap = pixmap.scaled(
                width, height, Qt.AspectRatioMode.KeepAspectRatio)

            # Create a QPainter for the QPrinter
            painter = QPainter(printer)

            # Draw the QPixmap onto the QPrinter
            painter.drawPixmap(0, 0, scaled_pixmap)

            # End the QPainter
            painter.end()

###### Edit / Delete Fees ######
    def fees_fetch_receipt_number(self):
        try:
            self.cb52.clear()
            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")
            cursor = mydb.cursor(buffered=True, dictionary=True)
            cursor.execute("select * from fees")
            result = cursor.fetchall()
            if result:
                for stud in result:
                    self.cb52.addItem(str(stud['receipt_number']))

        except con.Error as e:
            print("Error Occurred in Connecting to school_db " + str(e))

    def fetch_receipt_details(self):
        try:
            receipt_number = self.cb52.currentText()

            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")
            cursor = mydb.cursor(buffered=True, dictionary=True)
            cursor.execute(
                "select * from fees where receipt_number = '" + receipt_number + "'")
            result = cursor.fetchall()
            if result:
                for stud in result:
                    self.tb53.setText(str(stud['registration_number']))
                    self.tb53.setReadOnly(True)

                    self.cb54.setCurrentText(str(stud['month']))
                    self.tb54.setText(str(stud['amount']))
                    self.db52.setDate(QDate.fromString(
                        str(stud['fees_date']), "dd-MM-yyyy"))

        except con.Error as e:
            print("Error Occurred in Connecting to school_db " + str(e))

    def update_fees_details(self):
        try:
            mydb = con.connect(host="localhost", user="root",
                               password="", db="school_db")
            cursor = mydb.cursor(buffered=True, dictionary=True)

            registration_number = self.tb53.text()

            receipt_number = self.tb52.text()
            month = self.cb54.currentText()
            amount = self.tb54.text()
            fees_date = self.db52.text()

            qry = "UPDATE fees SET month = %s, amount = %s, fees_date = %s WHERE receipt_number = %s"
            values = (month, amount, fees_date, receipt_number)
            cursor.execute(qry, values)
            mydb.commit()

            self.l52.setText("Fees Details Modified Successfully !!")
            self.l52.adjustSize()
            QMessageBox.information(
                self, "School Management System", "Fees Details Modified Successfully !!")
            # Reset Fields
            self.tb53.setText("")
            self.tb54.setText("")
            self.l52.setText("")

            # Set RECEIPT fields for PRINT PREVIEW
            self.l81.setText(str(receipt_number))
            self.l82.setText(str(fees_date))
            self.l84.setText(str(amount))
            self.l85.setText(str(month))
            self.l86.setText(str(registration_number))
            cursor.execute(
                "select * from student where registration_number = '"+registration_number+"'")
            result = cursor.fetchall()
            if result:
                for stud in result:
                    self.l83.setText(str(stud['full_name']))
                    self.l87.setText(str(stud['phone']))
                    self.l88.setText(str(stud['email']))
                    self.l89.setText(str(stud['standard']))

            # Go To Printer Page
            self.tabWidget.setCurrentIndex(8)

        except con.Error as e:
            self.l52.setText("Error! Fees Details Not Modified ! ")
            self.l52.adjustSize()
            print("Error Occurred in Connecting to school_db " + str(e))

    def delete_fees_details(self):
        query = QMessageBox.question(
            self, "Delete", "Are you sure you\nWant to delete This Fees Details?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if query == QMessageBox.StandardButton.Yes:
            try:
                mydb = con.connect(host="localhost", user="root",
                                   password="", db="school_db")

                cursor = mydb.cursor(buffered=True, dictionary=True)
                receipt_number = self.cb52.currentText()

                qry = "delete from fees where receipt_number = '" + \
                    receipt_number + "'"
                cursor.execute(qry)
                mydb.commit()
                self.l52.setText("Fees Details Deleted Successfully !!")
                self.l52.adjustSize()
                QMessageBox.information(
                    self, "School Management System", "Fees Details Deleted Successfully !!")
                # Reset fields
                self.tb53.setText("")
                self.tb54.setText("")
                self.cb54.setCurrentIndex(0)

                self.l52.setText("")
                self.tabWidget.setCurrentIndex(1)
            except con.Error as e:
                self.l52.setText("Error! Could not Delete Fees Details ! ")
                self.l52.adjustSize()
                print("Error Occurred in Connecting to school_db " + str(e))

###### Report Module ######
    def show_report(self):
        table_name = self.sender()
        self.l61.setText(table_name.text())  # Set the table Name
        self.tabWidget.setCurrentIndex(7)
        try:
            self.tableReport.setRowCount(0)

            # Students Reports
            if (table_name.text() == "Students Reports"):

                mydb = con.connect(host="localhost", user="root",
                                   password="", db="school_db")
                cursor = mydb.cursor(buffered=True, dictionary=True)
                qry = "select registration_number, full_name, gender, dob, age, address, phone, email, standard from student"
                cursor.execute(qry)
                result = cursor.fetchall()

                self.tableReport.clear() # clear table

                # Set the row count and column count
                self.tableReport.setRowCount(len(result))
                self.tableReport.setColumnCount(len(result[0]))

                # Populate the table with data
                for row_number, row_data in enumerate(result):
                    for column_number, data in enumerate(row_data.values()):
                        self.tableReport.setItem(
                            row_number, column_number, QTableWidgetItem(str(data)))

                # Set header labels
                self.tableReport.setHorizontalHeaderLabels(
                    ['REG NO', 'NAME', 'GENDER', 'DOB', 'AGE', 'ADDRESS', 'PHONE NO', 'EMAIL ID', 'STANDARD'])

                # Resize columns and rows to fit content
                self.tableReport.resizeColumnsToContents()
                self.tableReport.resizeRowsToContents()

            # Marks Reports
            if (table_name.text() == "Marks Reports"):

                mydb = con.connect(host="localhost", user="root",
                                   password="", db="school_db")

                cursor = mydb.cursor(buffered=True, dictionary=True)
                qry = "select registration_number, exam_name, language, maths, science, arts from marks"
                cursor.execute(qry)
                result = cursor.fetchall()
                # Clear the table
                self.tableReport.clear()

                # Set the row count and column count
                self.tableReport.setRowCount(len(result))
                self.tableReport.setColumnCount(len(result[0]))

                # Populate the table with data
                for row_number, row_data in enumerate(result):
                    for column_number, data in enumerate(row_data.values()):
                        self.tableReport.setItem(
                            row_number, column_number, QTableWidgetItem(str(data)))

                # Set header labels
                self.tableReport.setHorizontalHeaderLabels(
                    ['REG NO', 'EXAM NAME', 'LANGUAGE', 'MATHS', 'SCIENCE', 'ARTS'])

                # Resize columns and rows to fit content
                self.tableReport.resizeColumnsToContents()
                self.tableReport.resizeRowsToContents()

            # Attendance Reports
            if (table_name.text() == "Attendance Reports"):
                mydb = con.connect(host="localhost", user="root",
                                   password="", db="school_db")

                cursor = mydb.cursor(buffered=True, dictionary=True)
                qry = "select registration_number, attendance_date, morning, evening from attendance"
                cursor.execute(qry)
                result = cursor.fetchall()
                # Clear the table
                self.tableReport.clear()

                # Set the row count and column count
                self.tableReport.setRowCount(len(result))
                self.tableReport.setColumnCount(len(result[0]))

                # Populate the table with data
                for row_number, row_data in enumerate(result):
                    for column_number, data in enumerate(row_data.values()):
                        self.tableReport.setItem(
                            row_number, column_number, QTableWidgetItem(str(data)))

                # Set header labels
                self.tableReport.setHorizontalHeaderLabels(
                    ['REG NO', 'ATTENDANCE DATE', 'MORNING', 'EVENING'])

                # Resize columns and rows to fit content
                self.tableReport.resizeColumnsToContents()
                self.tableReport.resizeRowsToContents()

            # Fees Reports
            if (table_name.text() == "Fees Reports"):
                mydb = con.connect(host="localhost", user="root",
                                   password="", db="school_db")

                cursor = mydb.cursor(buffered=True, dictionary=True)
                qry = "select receipt_number, registration_number, month, amount, fees_date from fees"
                cursor.execute(qry)
                result = cursor.fetchall()
                # Clear the table
                self.tableReport.clear()

                # Set the row count and column count
                self.tableReport.setRowCount(len(result))
                self.tableReport.setColumnCount(len(result[0]))

                # Populate the table with data
                for row_number, row_data in enumerate(result):
                    for column_number, data in enumerate(row_data.values()):
                        self.tableReport.setItem(
                            row_number, column_number, QTableWidgetItem(str(data)))

                # Set header labels
                self.tableReport.setHorizontalHeaderLabels(
                    ['RECEIPT NO', 'REG NO', 'MONTH', 'AMOUNT', 'FEES DATE'])

                # Resize columns and rows to fit content
                self.tableReport.resizeColumnsToContents()
                self.tableReport.resizeRowsToContents()

        except con.Error as e:
            print("Error Occurred in Connecting to school_db " + str(e))

###### Logout Module ######
    def logout(self):
        self.menubar.setVisible(False)
        self.tb01.setText("")
        self.tb02.setText("")
        self.l01.setText("")
        self.tabWidget.setCurrentIndex(0)
        QMessageBox.information(
            self, "School Management System", "Logged Out Successfully !")


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
