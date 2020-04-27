#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module ...

__author__ = "Magnus Kvendseth Øye"
__copyright__ = "Copyright 2019, Sparkie Quadruped Robot"
__credits__ = ["Magnus Kvendseth Øye", "Petter Drønnen", "Vegard Solheim"]
__version__ = "1.0.0"
__license__ = "MIT"
__maintainer__ = "Magnus Kvendseth Øye"
__email__ = "magnus.oye@gmail.com"
__status__ = "Development"
"""

# Importing packages
from __future__ import print_function
from config import *
import rviz
from python_qt_binding import QtWidgets, QtCore, QtGui
from python_qt_binding.binding_helper import *
import cv2
from cv_bridge import CvBridge
import sys
import time
import rospy
import roslib
from sensor_msgs.msg import Image
from std_msgs.msg import String
roslib.load_manifest('rviz')


class ManualWindow(QtWidgets.QDialog):
    """doc"""

    activate = QtCore.pyqtSignal(bool)
    stop_camera = QtCore.pyqtSignal()
    stop_pose = QtCore.pyqtSignal()
    stop_serial = QtCore.pyqtSignal()
    stop_command = QtCore.pyqtSignal()
    stop_xbox_controller = QtCore.pyqtSignal()
    change_camera = QtCore.pyqtSignal(bool)

    def __init__(self):
        super(ManualWindow, self).__init__()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.ui = '../forms/manual.ui'
        loadUi(self.ui, self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.layout = self.findChild(
            QtWidgets.QGridLayout, 'layout')

        self.mode = JOYSTICK_ONLY_MODE

        # Image frames
        self.videoframe = self.findChild(QtWidgets.QLabel, 'videoframe')
        self.topImageLabel = self.findChild(QtWidgets.QLabel, 'topImageLabel')
        self.middelImageLabel = self.findChild(QtWidgets.QLabel, 'middelImageLabel')
        self.bottomImageLabel = self.findChild(QtWidgets.QLabel, 'bottomImageLabel')

        # Buttons
        self.startVideoStreamBtn = self.findChild(QtWidgets.QPushButton, 'startVideoStreamBtn')
        self.stopVideoStreamBtn = self.findChild(QtWidgets.QPushButton, 'stopVideoStreamBtn')
        self.abortMissionBtn = self.findChild(QtWidgets.QPushButton, 'abortMissionBtn')
        self.inspectStatusBtn = self.findChild(QtWidgets.QPushButton, 'inspectStatusBtn')
        self.pauseMissionBtn = self.findChild(QtWidgets.QToolButton, 'pauseMissionBtn')
        self.stopMissionBtn = self.findChild(QtWidgets.QToolButton, 'stopMissionBtn')
        self.startMissionBtn = self.findChild(QtWidgets.QToolButton, 'startMissionBtn')
        self.refreshSelectMissionAreaBtn = self.findChild(QtWidgets.QToolButton, 'refreshSelectMissionAreaBtn')
        self.refreshSelectMissionBtn = self.findChild(QtWidgets.QToolButton, 'refreshSelectMissionBtn')

        # Labels
        self.runninMissionLabel = self.findChild(QtWidgets.QLabel, 'runninMissionLabel')
        self.runningTaskLabel = self.findChild(QtWidgets.QLabel, 'runningTaskLabel')
        self.currentRunningMissionLabel = self.findChild(QtWidgets.QLabel, 'currentRunningMissionLabel')

        # Progressbars
        self.runningTaskProgressBar = self.findChild(QtWidgets.QProgressBar, 'runningTaskProgressBar')

        # Comboboxes
        self.videoSourceComboBox = self.findChild(QtWidgets.QComboBox, 'videoSourceCombox')
        self.selectMissionAreaComboBox = self.findChild(QtWidgets.QComboBox, 'selectMissionAreaCombox')
        self.selectMissionComboBox = self.findChild(QtWidgets.QComboBox, 'selectMissionComboBox')

        # RVIZ
        self.visual_frame = rviz.VisualizationFrame()
        self.visual_frame.setSplashPath("")
        self.visual_frame.initialize()
        self.add_rviz_config()

        self.visual_frame.setMenuBar(None)
        self.visual_frame.setStatusBar(None)
        self.visual_frame.setHideButtonVisibility(True)

        self.layout.addWidget(self.visual_frame)

        self.manager = self.visual_frame.getManager()
        self.grid_display = self.manager.getRootDisplayGroup().getDisplayAt(0)

        # Tables
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, 'tableWidget')
        self.tableWidget.setHorizontalHeaderLabels(['Time', 'Tag', 'Operation','Status', 'Value', 'Warning', 'Error'])
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)
    
        # Top Buttons
        self.change_mode_btn = self.findChild(
            QtWidgets.QPushButton, 'changeModeBtn')
        self.exit_btn = self.findChild(QtWidgets.QPushButton, 'exitBtn')
        self.powerBtn = self.findChild(QtWidgets.QPushButton, 'powerBtn')
        self.emergency_btn = self.findChild(
            QtWidgets.QPushButton, 'emergencyBtn')

        # Status indicators
        self.signal_btn = self.findChild(QtWidgets.QPushButton, 'signalBtn')
        self.controller_battery_btn = self.findChild(
            QtWidgets.QPushButton, 'controllerBatteryBtn')
        self.battery_btn = self.findChild(QtWidgets.QPushButton, 'batteryBtn')
        self.health_btn = self.findChild(QtWidgets.QPushButton, 'healthBtn')

        # Button connections
        self.emergency_btn.clicked.connect(self.turn_robot_off)
        self.powerBtn.clicked.connect(self.power_on)
        self.exit_btn.clicked.connect(self.close_window)

        # Button shortcuts
        self.exit_btn.setShortcut("Ctrl+Q")

        # Stylesheets
        self.powerBtn.setStyleSheet(
            "QPushButton#powerBtn:checked {color:black; background-color: red;}")
        self.signal_btn.setStyleSheet(
            "QPushButton#signalBtn:checked {color:black; background-color: green;}")
        
        rospy.init_node('listener', anonymous=True)
        rospy.Subscriber('chatter', String, self.callback)

        self.show()

    def add_rviz_config(self):
        reader = rviz.YamlConfigReader()
        config = rviz.Config()
        reader.readFile(config, "../instance/Sparkie.rviz")
        self.visual_frame.load(config)
    
    def callback(self, data):
        #rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data) 
        rgb_image = CvBridge().imgmsg_to_cv2(data, desired_encoding="rgb8")

    def power_on(self):
        active = self.powerBtn.isChecked()
        if active:
            self.activate.emit(True)
        else:
            self.activate.emit(False)

    def blink_connection(self):
        if not self.signal_btn.isChecked():
            self.signal_btn.setChecked(True)
        else:
            self.signal_btn.setChecked(False)

    def close_window(self):
        self.close()

    def turn_robot_off(self):
        pass


class VideoStreamSubscriber(QtCore.QThread):

    def __init__(self, topic, msg_type):
        QtCore.QThread.__init__(self)
        self.topic = topic
        self.msg_type = msg_type

    def callback(self, data):
        #rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data) 
        rgb_image = CvBridge().imgmsg_to_cv2(data, desired_encoding="rgb8")

    def run(self):
        rospy.init_node('listener', anonymous=True)
        rospy.Subscriber(self.topic, self.msg_type, self.callback)