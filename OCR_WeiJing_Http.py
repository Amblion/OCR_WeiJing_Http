#coding=utf-8
#import libs 
import sys
import os
from   os.path import abspath, dirname
sys.path.insert(0,abspath(dirname(__file__)))
import OCR_WeiJing_Http_cmd
import OCR_WeiJing_Http_sty
import Fun
import EXUIControl
EXUIControl.FunLib = Fun
EXUIControl.G_ExeDir = Fun.G_ExeDir
EXUIControl.G_ResDir = Fun.G_ResDir
import tkinter
from   tkinter import *
import tkinter.ttk
import tkinter.font
from   PIL import Image,ImageTk

#Add your Varial Here: (Keep This Line of comments)
#Define UI Class
class  OCR_WeiJing_Http:
    def __init__(self,root,isTKroot = True,params=None):
        uiName = Fun.GetUIName(root,self.__class__.__name__)
        self.uiName = uiName
        Fun.Register(uiName,'UIClass',self)
        self.root = root
        self.configure_event = None
        self.isTKroot = isTKroot
        self.firstRun = True
        self.rootZoomed = False
        Fun.G_UIParamsDictionary[uiName]=params
        Fun.G_UICommandDictionary[uiName]=OCR_WeiJing_Http_cmd
        Fun.Register(uiName,'root',root)
        style = OCR_WeiJing_Http_sty.SetupStyle(isTKroot)
        self.UIJsonString = '{"Version": "1.0.0", "UIName": "OCR_WeiJing_Http", "Description": "", "WindowSize": [1102, 526], "WindowPosition": "Center", "WindowHide": false, "WindowResizable": false, "WindowTitle": "资源导出 v2025042902", "DarkMode": false, "BorderWidth": 0, "BorderColor": "#ffffff", "DropTitle": false, "DragWindow": false, "MinSize": [0, 0], "ResolutionScaling": true, "PopupDebugDialog": false, "TransparentColor": null, "RootTransparency": 255, "ICOFile": "E:/App/OCR_WeiJing_Http/Resources/全屏播放_full-screen-play.png", "ICOMode": "File", "WinState": 1, "WinTopMost": false, "BGColor": "#EFEFEF", "GroupList": {}, "WidgetList": [{"Type": "Form", "Index": 1, "AliasName": "Form_1", "BGColor": "#EFEFEF", "Size": [1102, 526], "PlaceInfo": null, "EventList": {"Load": "Form_1_onLoad"}}, {"Type": "Button", "Index": 2, "AliasName": "Button_1", "ParentName": "Form_1", "PlaceInfo": [25, 13, 88, 33, "nw", true, true], "Visible": true, "Size": [88, 33], "BGColor": "#EFEFEF", "Text": "开始统计", "FGColor": "#000000", "Relief": "raised", "EventList": {"Command": "Button_1_onCommand"}}, {"Type": "Button", "Index": 9, "AliasName": "Button_2", "ParentName": "Form_1", "PlaceInfo": [525, 13, 88, 33, "nw", false, true], "Visible": false, "Size": [1, 1], "BGColor": "#EFEFEF", "Text": "全部导出", "FGColor": "#000000", "Relief": "raised", "State": "disabled", "EventList": {"Command": "Button_2_onCommand"}}, {"Type": "Button", "Index": 12, "AliasName": "Button_3", "ParentName": "Form_1", "Layer": "lift", "PlaceInfo": [1049, 25, 41, 25, "nw", true, true], "Visible": true, "Size": [41, 25], "BGColor": "#EFEFEF", "Text": "更新", "FGColor": "#000000", "Relief": "raised", "EventList": {"Command": "Button_3_onCommand"}}, {"Type": "Button", "Index": 15, "AliasName": "Button_4", "ParentName": "Form_1", "PlaceInfo": [225, 13, 88, 33, "nw", true, true], "Visible": true, "Size": [88, 33], "BGColor": "#EFEFEF", "Text": "导出选中", "FGColor": "#000000", "Relief": "raised", "EventList": {"Command": "Button_4_onCommand"}}, {"Type": "Button", "Index": 16, "AliasName": "Button_5", "ParentName": "Form_1", "PlaceInfo": [325, 13, 88, 33, "nw", true, true], "Visible": true, "Size": [88, 33], "BGColor": "#EFEFEF", "Text": "清空数据", "FGColor": "#000000", "Relief": "raised", "EventList": {"Command": "Button_5_onCommand"}}, {"Type": "ListView", "Index": 7, "AliasName": "ListView_1", "ParentName": "Form_1", "PlaceInfo": [4, 65, 1094, 458, "nw", true, true], "Visible": true, "Size": [1094, 458], "SelectMode": "EXTENDED", "RowHeight": 28, "ColumnList": [["☐", "center", 30, false], ["模拟器编号", "w", 100, false], ["食物(角色)", "center", 80, false], ["食物(背包)", "center", 80, false], ["食物(总额)", "center", 80, false], ["木材(角色)", "center", 80, false], ["木材(背包)", "center", 80, false], ["木材(总额)", "center", 80, false], ["石材(角色)", "center", 80, false], ["石材(背包)", "center", 80, false], ["石材(总额)", "center", 80, false], ["金币(角色)", "center", 80, false], ["金币(背包)", "center", 80, false], ["金币(总额)", "center", 80, false]], "EventList": {"CellClicked": "ListView_1_onCellClicked", "HeadingClicked": "ListView_1_onHeadingClicked"}}, {"Type": "LabelFrame", "Index": 10, "AliasName": "LabelFrame_1", "ParentName": "Form_1", "PlaceInfo": [966, 4, 132, 54, "nw", true, true], "Visible": true, "Size": [132, 54], "BGColor": "#EFEFEF", "Text": "版本更新", "Anchor": "nw", "Relief": "groove", "ScrollRegion": null}, {"Type": "Label", "Index": 11, "AliasName": "Label_2", "ParentName": "Form_1", "Layer": "lift", "PlaceInfo": [973, 24, 67, 27, "nw", true, true], "Visible": true, "Size": [67, 27], "BGColor": "#EFEFEF", "Text": "", "FGColor": "#000000", "Anchor": "w"}, {"Type": "Frame", "Index": 13, "AliasName": "Frame_1", "ParentName": "Form_1", "Layer": "lower", "PlaceInfo": [0, 0, 1.0, 100, "nw", true, true], "Visible": true, "Size": [1102, 100], "BGColor": "#EFEFEF", "Relief": "flat", "ScrollRegion": null}]}'
        Form_1 = Fun.CreateUIFormJson(uiName,root,isTKroot,style,self.UIJsonString)
        #Inital all element's Data 
        Fun.InitElementData(uiName)
        #Call Form_1's OnLoad Function
        Fun.RunForm1_CallBack(uiName,"Load",OCR_WeiJing_Http_cmd.Form_1_onLoad)
        #Add Some Logic Code Here: (Keep This Line of comments)



        #Exit Application: (Keep This Line of comments)
        if self.isTKroot == True and Fun.GetElement(self.uiName,"root"):
            self.root.protocol('WM_DELETE_WINDOW', self.Exit)
            self.root.bind('<Configure>', self.Configure)
            if self.rootZoomed == True and isinstance(self.root,tkinter.Tk) == True:
                self.root.state("zoomed")
                Fun.SetUIState(uiName,"zoomed")
                self.rootZoomed = False
            
    def GetRootSize(self):
        return Fun.GetUIRootSize(self.uiName)
    def GetAllElement(self):
        return Fun.G_UIElementDictionary[self.uiName]
    def Escape(self,event):
        if Fun.AskBox('提示','确定退出程序？') == True:
            self.Exit()
    def Exit(self):
        if self.isTKroot == True:
            Fun.DestroyUI(self.uiName,0,'')

    def Configure(self,event):
        Form_1 = Fun.GetElement(self.uiName,'Form_1')
        if Form_1 == event.widget:
            Fun.ReDrawCanvasRecord(self.uiName)
        if self.root == event.widget and (self.configure_event is None or self.configure_event[2]!= event.width or self.configure_event[3]!= event.height):
            uiName = self.uiName
            self.configure_event = [event.x,event.y,event.width,event.height]
            Fun.ResizeRoot(self.uiName,self.root,event)
            Fun.ResizeAllChart(self.uiName)
            pass
#Create the root of tkinter 
if  __name__ == '__main__':
    Fun.RunApplication(OCR_WeiJing_Http)
