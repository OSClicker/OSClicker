import time
import sys
import threading
from pynput.mouse import Controller, Button
from pynput.keyboard import Listener, KeyCode
from random import randint
from pyautogui import moveTo
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal
from PyQt5.QtGui import QDesktopServices, QIcon

TOGGLE_KEY = KeyCode(char="F8")
PATTERN_ENABLED = False
MOUSE_MOVEMENT = True
DELAY_FIXED = 1.0
DELAY_PATTERN_1 = 0.0
DELAY_PATTERN_2 = 0.0
DELAY_PATTERN_3 = 0.0
INFINITE_CLICK = True
MAX_CLICKS = 0

mouse = Controller()

def movement():
    moveX = randint(-3, 4)
    moveY = randint(-3, 4)
    originalPosition = mouse.position
    newPosition = (originalPosition[0] + moveX, originalPosition[1] + moveY)
    moveTo(newPosition[0], newPosition[1], duration=0.13)
    moveTo(originalPosition[0], originalPosition[1], duration=0.13) 

def delayTime():
    global PATTERN_ENABLED
    global DELAY_FIXED
    global DELAY_PATTERN_1
    global DELAY_PATTERN_2
    global DELAY_PATTERN_3

    if PATTERN_ENABLED == True:
        delay = randint(1, 4)
        match delay:
            case 1:
                delay = DELAY_FIXED
            case 2:
                delay = DELAY_PATTERN_1
            case 3:
                delay = DELAY_PATTERN_2
            case 4:
                delay = DELAY_PATTERN_3
    else:
        delay = DELAY_FIXED
    
    return delay

class ClickerThread(QThread):
    stopSignal = False

    def run(self):
        self.stopSignal = False
        clicks = 0
        global INFINITE_CLICK
        global MAX_CLICKS
        global MOUSE_MOVEMENT  

        while not self.stopSignal:
            if INFINITE_CLICK == False:
                if clicks >  MAX_CLICKS:
                    clicks = 0
                    self.stop()
            mouse.click(Button.left)
            clicks += 1
            
            if MOUSE_MOVEMENT:
                movement()
            delay = delayTime()
            time.sleep(delay)
    
    def stop(self):
        self.stopSignal = True


class GUI(QMainWindow):
    global clicking

    def __init__(self):
        super(GUI, self).__init__()
        uic.loadUi("ui/base.ui", self)
        self.setWindowIcon(QIcon("images/icon.ico"))
        self.show()

        # Assign Toggles

        self.customHotkey.clicked.connect(self.customTrigger)
        self.randomIntervals.clicked.connect(self.enableRandomIntervals)
        self.startButton.clicked.connect(self.startClicking)
        self.setClicks.clicked.connect(self.setClicksAmount)
        self.infiniteClick.clicked.connect(self.enableInfiniteClick)

        self.actionClose.triggered.connect(self.close)
        self.actionMinimize.triggered.connect(self.showMinimized)
        self.actionPin.triggered.connect(self.togglePin)
        self.actionFAQ.triggered.connect(self.openHelp)

        self.isPinned = False

        # Threads & Listeners

        self.clickThread = ClickerThread()

        self.startButton.setText("Start (" + TOGGLE_KEY.char + ")")

        self.listenerThread = threading.Thread(target=self.setupListener)
        self.listenerThread.start()

        # Assign every button to a function

        # Anti-Ban Interval
        self.intv1.editingFinished.connect(self.updateInt1)
        self.intv2.editingFinished.connect(self.updateInt2)
        self.intv3.editingFinished.connect(self.updateInt3)
        # Anti-Ban Mouse movement
        self.moveClick.stateChanged.connect(self.updateMovement)
        # Anti-Ban Interval Enable/Disable
        self.randomIntervals.stateChanged.connect(self.updateRandom)
        # Set Clicks
        self.clickAmount.editingFinished.connect(self.setClicksMax)
        # Custom Hotkey
        self.triggerKey.keySequenceChanged.connect(self.setHotkey)
        # Hours, Minutes, Seconds and Milliseconds
        self.hours.editingFinished.connect(self.updateTime)
        self.minutes.editingFinished.connect(self.updateTime)
        self.seconds.editingFinished.connect(self.updateTime)
        self.milliseconds.editingFinished.connect(self.updateTime)


    def customTrigger(self):
        if self.customHotkey.isChecked():
            self.hotkeyLabel.setEnabled(True)
            self.triggerKey.setEnabled(True)
        else:
            self.hotkeyLabel.setEnabled(False)
            self.triggerKey.setEnabled(False)
    
    def enableRandomIntervals(self):
        if self.randomIntervals.isChecked():
            self.intv1.setEnabled(True)
            self.intv2.setEnabled(True)
            self.intv3.setEnabled(True)

            self.intv1l.setEnabled(True)
            self.intv2l.setEnabled(True)
            self.intv3l.setEnabled(True)
        else:
            self.intv1.setEnabled(False)
            self.intv2.setEnabled(False)
            self.intv3.setEnabled(False)

            self.intv1l.setEnabled(False)
            self.intv2l.setEnabled(False)
            self.intv3l.setEnabled(False)
    
    def startClicking(self):
        global clicking
        global TOGGLE_KEY

        if not self.clickThread.isRunning():
            time.sleep(1)
            self.startButton.setText("Stop (" + TOGGLE_KEY.char + ")")
            self.clickThread.start()
        else:
            self.startButton.setText("Start (" + TOGGLE_KEY.char + ")")
            self.clickThread.stop()
            
    
    def setClicksAmount(self):
        global INFINITE_CLICK

        if self.setClicks.isChecked():
            self.clickAmount.setEnabled(True)
            self.clickAmountL.setEnabled(True)
            INFINITE_CLICK = False
        else:
            self.clickAmount.setEnabled(False)
            self.clickAmountL.setEnabled(False)
            INFINITE_CLICK = True

    def enableInfiniteClick(self):
        global INFINITE_CLICK

        if self.infiniteClick.isChecked():
            INFINITE_CLICK = True
            self.clickAmount.setEnabled(False)
            self.clickAmountL.setEnabled(False)
        else:
            INFINITE_CLICK = False
    
    def togglePin(self):
        self.isPinned = not self.isPinned
        if self.isPinned:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()
    
    def openHelp(self):
        QDesktopServices.openUrl(QUrl("https://osclicker.github.io/faq"))

    def toggleKey(self, key):
        global TOGGLE_KEY
        if key == TOGGLE_KEY:
            self.startClicking()

    def setupListener(self):
        with Listener(on_press=self.toggleKey) as listener:
            listener.join()
    
    # Button functions

    def updateInt1(self):
        global DELAY_PATTERN_1

        DELAY_PATTERN_1 = self.intv1.value()
    
    def updateInt2(self):
        global DELAY_PATTERN_2

        DELAY_PATTERN_2 = self.intv2.value()
    
    def updateInt3(self):
        global DELAY_PATTERN_3

        DELAY_PATTERN_3 = self.intv3.value()
    
    def updateMovement(self):
        global MOUSE_MOVEMENT

        MOUSE_MOVEMENT = not MOUSE_MOVEMENT
    
    def updateRandom(self):
        global PATTERN_ENABLED

        PATTERN_ENABLED = not PATTERN_ENABLED
    
    def setClicksMax(self):
        global MAX_CLICKS

        MAX_CLICKS = self.clickAmount.value()
    
    def setHotkey(self):
        global TOGGLE_KEY

        hotkeySequence = self.triggerKey.keySequence()
        # modifiers = hotkeySequence[0].modifiers() //  self.triggerKey.keyboardModifiers()
        hotkey = hotkeySequence.toString()

        TOGGLE_KEY = KeyCode(char=KeyCode.from_char(hotkey))
    
    def updateTime(self):
        global DELAY_FIXED

        seconds = self.seconds.value()
        minutes = self.minutes.value() * 60
        hours = self.hours.value() * 3600
        milliseconds = self.milliseconds.value() / 1000

        totalTime = seconds + minutes + hours + milliseconds

        DELAY_FIXED = totalTime

def main():
    app = QApplication([])
    window = GUI()
    app.exec_()
    sys.exit()

if __name__ == '__main__':
    main()
