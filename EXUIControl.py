# 版权声明：日历控件参考CSDN博主「我的眼_001」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原作者出处链接及声明
# 原文链接：https://blog.csdn.net/wodeyan001/article/details/86703034
# -*- coding: utf-8 -*- 
import os
import tkinter
import tkinter.ttk
import tkinter.font
from   PIL import Image,ImageTk
from   functools import partial
import win32gui
import inspect
import threading
G_ExeDir = None
G_ResDir = None
FunLib = None
SCALE_FACTOR = 1.5
def EventFunction_Adaptor(fun,  **params):
    """重新定义消息映射函数,自定义参数。"""
    return lambda event, fun=fun, params=params: fun(event, **params)
#判读是否多线程调用
def onThreadingCallFunction(fun,FunctionThreadDict,uiName,widgetName,value=None):
    threadingvalue = 0
    argspec = inspect.getfullargspec(fun)
    if "threadings" in argspec.args:
        threadingindex = argspec.args.index('threadings')
        threadingvalue = argspec[threadingindex+1]
        if type(threadingvalue) == type(()) or type(threadingvalue) == type([]):
            if len(threadingvalue) == 0:
                threadingvalue = 0
            else:
                threadingvalue = threadingvalue[0]
        if threadingvalue > 0:
            EventFunctionNameKey = fun.__module__+'.'+fun.__name__
            if EventFunctionNameKey in FunctionThreadDict:
                for thread in FunctionThreadDict[EventFunctionNameKey]:
                    if not thread.is_alive():
                        FunctionThreadDict[EventFunctionNameKey].remove(thread)
                if len(FunctionThreadDict[EventFunctionNameKey]) >= threadingvalue:
                    return
            function_args = [uiName,widgetName]
            if value != None:
                function_args.append(value)
            run_thread = threading.Thread(target=fun, args=function_args)
            run_thread.Daemon = True
            run_thread.start()
            if threadingvalue > 0:
                if EventFunctionNameKey not in FunctionThreadDict:
                    FunctionThreadDict[EventFunctionNameKey] = [run_thread]
                else:
                    FunctionThreadDict[EventFunctionNameKey].append(run_thread)
            return
    if value:
        fun(uiName,widgetName,value)
    else:
        fun(uiName,widgetName)
import calendar
datetime = calendar.datetime.datetime
timedelta = calendar.datetime.timedelta
#日历控件
class Calendar:
    def __init__(self, widget, hideBtn = False,year=None,month=None,day=None):
        self.ParentWidget = widget
        self.HideButton = hideBtn
        fwday = calendar.SUNDAY
        show_year = year
        if show_year is None:
            show_year = datetime.now().year
        show_month = month
        if show_month is None:
            show_month = datetime.now().month
        show_day = day
        if show_day is None:
            show_day = datetime.now().day
        locale = None
        self.Btn_callbackFun = None
        self.uiName = None
        self.widgetName = None
        self.datebar_bg = 'black'
        self.datebar_fg = 'white'
        self.sel_bg = '#ecffc4'
        self.sel_fg = '#05640e'
        self._date = datetime(show_year, show_month, show_day)
        self._selection = None # 设置为未选中日期
        self.Canvas = tkinter.Canvas(self.ParentWidget,width=240,height=240,bg = self.datebar_bg,highlightthickness=0,bd=0)
        self.Canvas.place(x=0, y=0,width=240,height=240)
        self._cal = self.__get_calendar(locale, fwday)
        self.__setup_styles()       # 创建自定义样式
        self.__place_widgets()      # pack/grid 小部件
        self.__config_calendar()    # 调整日历列和安装标记
        # 配置画布和正确的绑定，以选择日期。
        self.__setup_selection()
        # 存储项ID，用于稍后插入。
        self._items = [self._calendar.insert('', 'end', values='') for _ in range(6)]
        # 在当前空日历中插入日期
        self._update()
    def GetWidget(self):
        return self.Canvas
    #传递绑定事件
    def bind(self,EventName,callBack):
        if self.Canvas:
            self.Canvas.bind(EventName,callBack)
    #取得边框样式
    def Hide(self,layout="place"):
        if layout == "pack":
            self.Canvas.pack_forget()
        elif layout == "grid":
            self.Canvas.grid_forget()
        else:
            self.Canvas.place_forget()
    #传递pack_forget事件
    def pack_forget(self):
        if self.Canvas:
            self.Canvas.pack_forget()
    #传递grid_forget事件
    def grid_forget(self):
        if self.Canvas:
            self.Canvas.grid_forget()
    #传递place_forget事件
    def place_forget(self):
        if self.Canvas:
            self.Canvas.place_forget()
    def keepbgColor(self):
        frame_bg = self.Canvas.cget('bg')
        self.hframe.configure(bg=frame_bg)
        self.gframe.configure(bg=frame_bg)
        self.bframe.configure(bg=frame_bg)
        self.YearLabel.configure(bg=frame_bg)
        self.MonthLabel.configure(bg=frame_bg)
        if self.okbtn:
            self.okbtn.configure(bg=frame_bg)
        if self.cancelbtn:
            self.cancelbtn.configure(bg=frame_bg)
        if self.lastbtn:
            self.lastbtn.configure(bg=frame_bg)
        if self.nextbtn:
            self.nextbtn.configure(bg=frame_bg)
    #设置背景色
    def SetBGColor(self,bgcolor):
        self.Canvas.configure(bg = bgcolor)
        self.keepbgColor()
    #获取背景色
    def GetBGColor(self):
        return self.Canvas.cget('bg')
    #设置窗体样式
    def SetRelief(self,relief):
        self.Canvas.configure(relief = relief)
    #获取窗体样式
    def GetRelief(self):
        return self.Canvas.cget('relief')
    #设置日期栏的背景色
    def SetDatebarBGColor(self,bgColor):
        self.datebar_bg = bgColor
        self._calendar.tag_configure('header', background=self.datebar_bg,foreground=self.datebar_fg)
    #获取日期栏的背景色
    def GetDatebarBGColor(self):
        return self.datebar_bg
    #设置日期栏的前景色
    def SetDatebarFGColor(self,fgColor):
        self.datebar_fg = fgColor
        self._calendar.tag_configure('header', background=self.datebar_bg,foreground=self.datebar_fg)
    #获取日期栏的前景色
    def GetDatebarFGColor(self):
        return self.datebar_fg
    #设置选中时的背景色
    def SetSelectedBGColor(self,bgColor):
        self.sel_bg = bgColor
        self.__setup_selection()
    #获取选中时的背景色
    def GetSelectedBGColor(self):
        return self.sel_bg
    #设置选中时的前景色
    def SetSelectedFGColor(self,fgColor):
        self.sel_fg = fgColor
        self.__setup_selection()
    #获取选中时的前景色
    def GetSelectedFGColor(self):
        return self.sel_fg
    #设置点击确定时的回调函数
    def SetBtnCallBackFunction(self,callBackFun,uiName,widgetName):
        self.Btn_callbackFun = callBackFun
        self.uiName = uiName
        self.widgetName = widgetName
    #获取点击确定时的回调函数
    def GetBtnCallBackFunction(self):
        return self.Btn_callbackFun
    #取得选中日期值
    def GetDate(self):
        return self.selection()
    #设置显示日期值
    def SetDate(self,year,month,day):
        self._date = datetime(year, month, day)
        self._canvas.place_forget()
        self._build_calendar()
        for _item, day_list in enumerate(self._cal.monthdayscalendar(year, month)):
            if day in day_list:
                item = 'I00' + str(_item + 2)
                column = '#' + str(day_list.index(day)+1)
                text = '%02d' % day
                self._selection = (text, item, column)
                self.Canvas.after(100, lambda :self._pressed(item = item, column = column, widget = self._calendar))
        self.CB_year.set(str(year))
        self.CB_month.set(str(month))
    #设置年的可选范围
    def SetRangeOfYears(self,year_from,year_to):
        self.CB_year.configure(values = [str(year) for year in range(year_to, year_from-1,-1)])
    def __get_calendar(self, locale, fwday):
        # 实例化适当的日历类
        if locale is None:
            return calendar.TextCalendar(fwday)
        else:
            return calendar.LocaleTextCalendar(fwday, locale)
    def __setitem__(self, item, value):
        if item in ('year', 'month'):
            raise AttributeError("attribute '%s' is not writeable" % item)
        elif item == 'selectbackground':
            self._canvas['background'] = value
        elif item == 'selectforeground':
            self._canvas.itemconfigure(self._canvas.text, item=value)
        else:
            self.Canvas.__setitem__(self, item, value)
    def __getitem__(self, item):
        if item in ('year', 'month'):
            return getattr(self._date, item)
        elif item == 'selectbackground':
            return self._canvas['background']
        elif item == 'selectforeground':
            return self._canvas.itemcget(self._canvas.text, 'fill')
        else:
            r = tkinter.ttk.tclobjs_to_py({item: tkinter.ttk.Frame.__getitem__(self, item)})
            return r[item]
    def __setup_styles(self):
        # 自定义TTK风格
        style = tkinter.ttk.Style(self.Canvas)
        arrow_layout = lambda dir: (
            [('Button.focus', {'children': [('Button.%sarrow' % dir, None)]})]
        )
        style.layout('L.TButton', arrow_layout('left'))
        style.layout('R.TButton', arrow_layout('right'))
    def __place_widgets(self):
        # 标头框架及其小部件
        Input_judgment_num = self.Canvas.register(self.Input_judgment)  # 需要将函数包装一下，必要的
        frame_bg = self.Canvas.cget('bg')
        self.hframe = tkinter.Frame(self.Canvas,bg=frame_bg)
        self.gframe = tkinter.Frame(self.Canvas,bg=frame_bg)
        self.bframe = tkinter.Frame(self.Canvas,bg=frame_bg)
        self.hframe.pack(in_=self.Canvas, side='top', pady=18, anchor='center')
        self.gframe.pack(in_=self.Canvas, fill=tkinter.X, pady=5)
        self.bframe.pack(in_=self.Canvas, side='bottom', pady=10)
        self.BtnFont = tkinter.font.Font(size=12)
        self.lastbtn = tkinter.Button(self.hframe,text='◀',  font = self.BtnFont, relief = 'flat',  command=self._prev_month)
        self.lastbtn.grid(in_=self.hframe, column=0, row=0, padx=5)
        self.nextbtn = tkinter.Button(self.hframe, text='▶', font = self.BtnFont, relief = 'flat', command=self._next_month)
        self.nextbtn.grid(in_=self.hframe, column=5, row=0, padx=5)
        self.CB_year = tkinter.ttk.Combobox(self.hframe, width = 5, values = [str(year) for year in range(datetime.now().year, datetime.now().year-11,-1)], validate = 'key', validatecommand = (Input_judgment_num, '%P'))
        self.CB_year.current(0)
        self.CB_year.grid(in_=self.hframe, column=1, row=0)
        self.CB_year.bind('<KeyPress>', lambda event:self._update(event, True))
        self.CB_year.bind("<<ComboboxSelected>>", self._update)
        self.YearLabel = tkinter.Label(self.hframe, text = '年', justify = 'left',bg=frame_bg)
        self.YearLabel.grid(in_=self.hframe, column=2, row=0, padx=(0,5))
        self.CB_month = tkinter.ttk.Combobox(self.hframe, width = 3, values = ['%02d' % month for month in range(1,13)], state = 'readonly')
        self.CB_month.current(datetime.now().month - 1)
        self.CB_month.grid(in_=self.hframe, column=3, row=0)
        self.CB_month.bind("<<ComboboxSelected>>", self._update)
        self.MonthLabel = tkinter.Label(self.hframe, text = '月', justify = 'left',bg=frame_bg)
        self.MonthLabel.grid(in_=self.hframe, column=4, row=0)
        # 日历部件
        self._calendar = tkinter.ttk.Treeview(self.gframe, show='', selectmode='none', height=7)
        self._calendar.pack(expand=1, fill='both', side='bottom', padx=5)
        styleName = "Calendar.Treeview"
        style = tkinter.ttk.Style()
        style.configure(styleName, rowheight=24)
        self._calendar.configure(style = styleName)
        self.okbtn = None
        self.cancelbtn = None
        if self.HideButton == False:
            self.okbtn = tkinter.Button(self.bframe, text = '确定', width = 6, relief = 'flat', command = lambda: self._exit(True))
            self.okbtn.grid(row = 0, column = 0, sticky = 'ns', padx = 20)
            self.cancelbtn = tkinter.Button(self.bframe, text = '取消', width = 6,relief = 'flat',  command = self._exit)
            self.cancelbtn.grid(row = 0, column = 1, sticky = 'ne', padx = 20)
        else:
            self.Canvas.place(x=0, y=0,width=320,height=240)
        tkinter.Frame(self.Canvas, bg = '#565656').place(x = 0, y = 0, relx = 0, rely = 0, relwidth = 1, relheigh = 2/200)
        tkinter.Frame(self.Canvas, bg = '#565656').place(x = 0, y = 0, relx = 0, rely = 198/200, relwidth = 1, relheigh = 2/200)
        tkinter.Frame(self.Canvas, bg = '#565656').place(x = 0, y = 0, relx = 0, rely = 0, relwidth = 2/200, relheigh = 1)
        tkinter.Frame(self.Canvas, bg = '#565656').place(x = 0, y = 0, relx = 198/200, rely = 0, relwidth = 2/200, relheigh = 1)
    def __config_calendar(self):
        # cols = self._cal.formatweekheader(3).split()
        cols = ['日','一','二','三','四','五','六']
        self._calendar['columns'] = cols
        self._calendar.tag_configure('header', background=self.datebar_bg,foreground=self.datebar_fg)
        self._calendar.insert('', 'end', values=cols, tag='header')
        # 调整其列宽
        font = tkinter.font.Font()
        maxwidth = max(font.measure(col) for col in cols)
        for col in cols:
            self._calendar.column(col, width=maxwidth, minwidth=maxwidth,
                anchor='center')
    def __setup_selection(self):
        def __canvas_forget(evt):
            canvas.place_forget()
            self._selection = None
        self._font = tkinter.font.Font()
        self._canvas = canvas = tkinter.Canvas(self._calendar, background=self.sel_bg, borderwidth=0, highlightthickness=0)
        canvas.text = canvas.create_text(0, 0, fill=self.sel_fg, anchor='w')
        canvas.bind('<Button-1>', __canvas_forget)
        self._calendar.bind('<Configure>', __canvas_forget)
        self._calendar.bind('<Button-1>', self._click)
    def _build_calendar(self):
        year, month = self._date.year, self._date.month
        # update header text (Month, YEAR)
        header = self._cal.formatmonthname(year, month, 0)
        # 更新日历显示的日期
        cal = self._cal.monthdayscalendar(year, month)
        for indx, item in enumerate(self._items):
            week = cal[indx] if indx < len(cal) else []
            fmt_week = [('%02d' % day) if day else '' for day in week]
            self._calendar.item(item, values=fmt_week)
    def _show_select(self, text, bbox):
        """为新的选择配置画布。"""
        x, y, width, height = bbox
        textw = self._font.measure(text)
        canvas = self._canvas
        canvas.configure(width = width, height = height)
        canvas.coords(canvas.text, (width - textw)/2, height / 2 - 1)
        canvas.itemconfigure(canvas.text, text=text)
        canvas.place(in_=self._calendar, x=x, y=y)
    def _pressed(self, evt = None, item = None, column = None, widget = None):
        """在日历的某个地方点击。"""
        if not item:
            x, y, widget = evt.x, evt.y, evt.widget
            item = widget.identify_row(y)
            column = widget.identify_column(x)
        if not column or not item in self._items:
            # 在工作日行中单击或仅在列外单击。
            return
        item_values = widget.item(item)['values']
        if not len(item_values): # 这个月的行是空的。
            return
        text = item_values[int(column[1]) - 1]
        if not text: # 日期为空
            return
        bbox = widget.bbox(item, column)
        if not bbox: # 日历尚不可见
            self.Canvas.after(20, lambda : self._pressed(item = item, column = column, widget = widget))
            return
        # 更新，然后显示选择
        text = '%02d' % text
        self._selection = (text, item, column)
        self._show_select(text, bbox)
    def _click(self,event):
        self._pressed(event)
        self._exit(True)
    def _prev_month(self):
        """更新日历以显示前一个月。"""
        self._canvas.place_forget()
        self._selection = None
        self._date = self._date - timedelta(days=1)
        self._date = datetime(self._date.year, self._date.month, 1)
        self.CB_year.set(self._date.year)
        self.CB_month.set(self._date.month)
        self._update()
    def _next_month(self):
        """更新日历以显示下一个月。"""
        self._canvas.place_forget()
        self._selection = None
        year, month = self._date.year, self._date.month
        self._date = self._date + timedelta(
            days=calendar.monthrange(year, month)[1] + 1)
        self._date = datetime(self._date.year, self._date.month, 1)
        self.CB_year.set(self._date.year)
        self.CB_month.set(self._date.month)
        self._update()
    def _update(self, event = None, key = None):
        """刷新界面"""
        if key and event.keysym != 'Return': return
        year = int(self.CB_year.get())
        month = int(self.CB_month.get())
        if year == 0 or year > 9999: return
        self._canvas.place_forget()
        self._date = datetime(year, month, 1)
        self._build_calendar() # 重建日历
        if year == datetime.now().year and month == datetime.now().month:
            day = datetime.now().day
            for _item, day_list in enumerate(self._cal.monthdayscalendar(year, month)):
                if day in day_list:
                    item = 'I00' + str(_item + 2)
                    column = '#' + str(day_list.index(day)+1)
                    self.Canvas.after(100, lambda :self._pressed(item = item, column = column, widget = self._calendar))
    def _exit(self, confirm = False):
        if  self.Btn_callbackFun != None:
            self.Btn_callbackFun(self.uiName,self.widgetName,self.selection())
        """退出窗口"""
        # if not confirm: self._selection = None
        # self.Canvas.destroy()
    def selection(self):
        """返回表示当前选定日期的日期时间。"""
        if not self._selection: return None
        year, month = self._date.year, self._date.month
        return str(datetime(year, month, int(self._selection[0])))[:10]
    def Input_judgment(self, content):
        """输入判断"""
        # 如果不加上==""的话，就会发现删不完。总会剩下一个数字
        if content.isdigit() or content == "":
            return True
        else:
            return False
#时间选择框 ，由我基于Calendar创作。
class DatePicker:
    def __init__(self, widget):
        self.ParentWidget = widget
        self.currYear = datetime.now().year
        self.currMonth = datetime.now().month
        self.currDay = datetime.now().day 
        self.currDate = str("%d/%02d/%02d"%(self.currYear,self.currMonth,self.currDay))
        self.Canvas = tkinter.Canvas(self.ParentWidget,width=100,height=20,bg = '#EFEFEF',highlightthickness=0,bd=0)
        self.Canvas.place(x=0, y=0,width=100,height=20)
        self.EntryValue = tkinter.StringVar()
        self.EntryValue.set(self.currDate)
        self.dateEntry =  tkinter.Entry(self.Canvas,width=12, state='readonly',textvariable=self.EntryValue,relief=tkinter.SUNKEN)
        self.dateEntry.pack(expand=1, fill='both', side='top')
        self.dateEntry.bind("<Button-1>", self.PopupCalendar)
        self.selectButton = tkinter.Button(self.dateEntry,text='▼',fg='#000000',relief=tkinter.FLAT,command=self.PopupCalendar)
        self.selectButton.pack(expand=0, fill='y', side='right')
        self.calendar = None
        self.calendar_bg = '#efefef'
        self.datebar_bg = '#efefef'
        self.datebar_fg = '#000000'
        self.separatorChar = '-'
        self.sel_bg = '#ecffc4'
        self.sel_fg = '#05640e'
        self.year_begin = datetime.now().year-11
        self.year_end = datetime.now().year
        self.Btn_callbackFun = None
        self.uiName = None
        self.widgetName = None
    #重载一下cget
    def cget(self,attrib):
        return self.dateEntry.cget(attrib)
    #设置属性
    def configure(self,**kw):
        self.dateEntry.configure(kw)
    #取得所属窗体
    def GetWidget(self):
        return self.Canvas
    #传递绑定事件
    def bind(self,EventName,callBack):
        if self.Canvas:
            self.Canvas.bind(EventName,callBack)
    #取得边框样式
    def Hide(self,layout="place"):
        if layout == "pack":
            self.Canvas.pack_forget()
        elif layout == "grid":
            self.Canvas.grid_forget()
        else:
            self.Canvas.place_forget()
    #传递pack_forget事件
    def pack_forget(self):
        if self.Canvas:
            self.Canvas.pack_forget()
    #传递grid_forget事件
    def grid_forget(self):
        if self.Canvas:
            self.Canvas.grid_forget()
    #传递place_forget事件
    def place_forget(self):
        if self.Canvas:
            self.Canvas.place_forget()
    #设置背景色
    def SetBGColor(self,bgColor):
        self.dateEntry.configure(bg = bgColor)
        self.dateEntry.config({'readonlybackground':bgColor})
    #获取背景色
    def GetBGColor(self):
        return self.dateEntry.cget('bg')
    #设置文字颜色
    def SetFGColor(self,fgColor):
        self.dateEntry.configure(fg = fgColor)
    #获取文字颜色n    def GetFGColor(self):
        return self.dateEntry.cget('fg')
    #设置的字体
    def SetFont(self,font):
        self.Font = font
        if self.dateEntry:
            self.dateEntry.configure(font = self.Font)
    #取得字体
    def GetFont(self):
        return self.Font
    #设置窗体样式
    def SetRelief(self,relief):
        self.dateEntry.configure(relief = relief)
    #获取窗体样式
    def GetRelief(self):
        return self.dateEntry.cget('relief')
    #设置日历背景色
    def SetCalendarBGColor(self,bgColor):
        self.calendar_bg = bgColor
        if self.calendar:
            self.calendar.SetBGColor(self.calendar_bg)
    #获取日历背景色
    def GetCalendarBGColor(self):
        if self.calendar:
           return self._calendar.GetBGColor()
    #设置日期栏的背景色
    def SetDatebarBGColor(self,bgColor):
        self.datebar_bg = bgColor
        if self.calendar:
            self.calendar.SetDatebarBGColor(self.datebar_bg)
    #获取日期栏的背景色
    def GetDatebarBGColor(self):
        return self.datebar_bg
    #设置日期栏的前景色
    def SetDatebarFGColor(self,fgColor):
        self.datebar_fg = fgColor
        if self.calendar:
            self.calendar.SetDatebarFGColor(self.datebar_fg)
    #获取日期栏的前景色
    def GetDatebarFGColor(self):
        return self.datebar_fg
    #设置选中时的背景色
    def SetSelectedBGColor(self,bgColor):
        self.sel_bg = bgColor
        if self.calendar:
            self.calendar.SetSelectedBGColor(self.sel_bg)
    #获取选中时的背景色
    def GetSelectedBGColor(self):
        return self.sel_bg
    #设置选中时的前景色
    def SetSelectedFGColor(self,fgColor):
        self.sel_fg = fgColor
        if self.calendar:
            self.calendar.SetSelectedFGColor(self.sel_fg)
    #获取选中时的前景色
    def GetSelectedFGColor(self):
        return self.sel_fg
    #设置年的可选范围
    def SetRangeOfYears(self,year_from,year_to):
        if self.calendar:
            self.calendar.SetRangeOfYears(year_from,year_to)
        self.year_begin = year_from
        self.year_end = year_to
    #设置日期的格式
    def SetSeparatorChar(self,char):
        self.separatorChar = char
        if char == '-':
            self.currDate = str("%d-%02d-%02d"%(self.currYear,self.currMonth,self.currDay))
        else:
            self.currDate = str("%d/%02d/%02d"%(self.currYear,self.currMonth,self.currDay))
        self.EntryValue.set(self.currDate)
    #设置点击确定时的回调函数
    def SetBtnCallBackFunction(self,callBackFun,uiName,widgetName):
        self.Btn_callbackFun = callBackFun
        self.uiName = uiName
        self.widgetName = widgetName
    #获取点击确定时的回调函数
    def GetBtnCallBackFunction(self):
        return self.Btn_callbackFun
    #弹出日期选择框
    def PopupCalendar(self,event = None):
        if self.calendar is None:
            self.ShowCalendar()
        else:
            self.HideCalendar()
            self.Dialog = None
    #显示日期选择框
    def ShowCalendar(self):
        self.Dialog = tkinter.Toplevel()
        self.Dialog.attributes("-toolwindow", 0)
        self.Dialog.resizable(0,0) 
        self.Dialog.grab_set()
        self.Dialog.overrideredirect(1)
        self.Dialog.wm_attributes("-topmost", 1)
        sx = self.Canvas.winfo_rootx()
        sy = self.Canvas.winfo_rooty()+self.Canvas.winfo_height()
        geoinfo = str('%dx%d+%d+%d'%(320,240,sx,sy))
        self.Dialog.geometry(geoinfo)  
        self.calendar = Calendar(self.Dialog,True,self.currYear,self.currMonth,self.currDay)
        self.calendar.SetRangeOfYears(self.year_begin,self.year_end)
        self.calendar.SetBGColor(self.calendar_bg)
        self.calendar.SetDatebarBGColor(self.datebar_bg)
        self.calendar.SetDatebarFGColor(self.datebar_fg)
        self.calendar.SetSelectedBGColor(self.sel_bg)
        self.calendar.SetSelectedFGColor(self.sel_fg)
        self.calendar.SetBtnCallBackFunction(self.ChooseDate,"DatePicker","calendar")
        tkinter.Tk.wait_window(self.Dialog)   
    #隐藏日期选择框
    def HideCalendar(self):
        self.calendar = None
        self.Dialog.destroy()
    #选择日期的响应
    def ChooseDate(self,uiName,widgetName,selection):
        self.HideCalendar()
        print(selection)
        textSplit = selection.split('-')
        if self.separatorChar == '-':
            self.currDate = str("%s-%s-%s"%(textSplit[0],textSplit[1],textSplit[2]))
        else:
            self.currDate = str("%s/%s/%s"%(textSplit[0],textSplit[1],textSplit[2]))
        self.EntryValue.set(self.currDate)
        if  self.Btn_callbackFun != None:
            self.Btn_callbackFun(self.uiName,self.widgetName,selection)
    #取得选中日期值
    def GetDate(self):
        return self.currDate
    #设置显示日期值
    def SetDate(self,year,month,day):
        self.currYear = year
        self.currMonth = month
        self.currDay = day 
        if self.separatorChar == '-':
            self.currDate = str("%d-%02d-%02d"%(self.currYear,self.currMonth,self.currDay))
        else:
            self.currDate = str("%d/%02d/%02d"%(self.currYear,self.currMonth,self.currDay))
        self.EntryValue.set(self.currDate)
    #获取点击确定时的回调函数
    def GetBtnCallBackFunction(self):
        return self.Btn_callbackFun
#图片按钮
class LabelButton:
    def __init__(self, widget):
        self.ParentWidget = widget
        self.Text = 'LabelButton'
        self.BGColor = '#333333'
        self.FGColor = '#FFFFFF'
        self.Font = None 
        self.Image = None
        self.ImageFile = None
        self.BGColor_Hover = None
        self.FGColor_Hover = None
        self.Font_Hover = None 
        self.Image_Hover = None
        self.ImageFile_Hover = None
        self.BGColor_Click = None
        self.FGColor_Click = None
        self.Font_Click = None 
        self.Image_Click = None
        self.ImageFile_Click = None
        self.LabelWidth = 100
        self.LabelHeight = 24
        self.commandFunction = None
        self.FunctionThreadDict={}
        self.droplistFunction = None
        self.uiName = None
        self.widgetName = None
        self.Compound = "center"
        self.Anchor = "center"
        self.State = "normal"
        self.Relief = "flat"
        self.DropListUI = None
        self.DropList = None
        self.DropBtn = None
        self.Label = tkinter.Label(self.ParentWidget,text=self.Text,width=self.LabelWidth,height=self.LabelHeight,bg = self.BGColor)
        self.Label.place(x=0, y=0,width=self.LabelWidth,height=self.LabelHeight)
        self.Label.configure(compound=self.Compound)
        self.Label.bind('<Configure>',self.Configure)
        self.Label.bind('<Enter>',self.onEnter)
        self.Label.bind('<Leave>',self.onLeave)
        self.Label.bind('<Button-1>',self.onClick)
        self.Label.bind('<ButtonRelease-1>',self.onEnter)
    #取得边框样式
    def Hide(self,layout="place"):
        if layout == "pack":
            self.Label.pack_forget()
        elif layout == "grid":
            self.Label.grid_forget()
        else:
            self.Label.place_forget()
    #鼠标进入时的处理
    def onEnter(self,event):
        try:
            if self.State == "normal":
                event.widget.configure(cursor='hand2')
                if self.Image_Hover:
                    event.widget.configure(image = self.Image_Hover)
                elif self.BGColor_Hover:
                    event.widget.configure(bg = self.BGColor_Hover)
                if self.FGColor_Hover:
                    event.widget.configure(fg = self.FGColor_Hover)
                if self.Font_Hover:
                    event.widget.configure(font = self.Font_Hover)
                event.widget.update()
                if self.DropBtn:
                    self.DropBtn.pack_forget()
                    self.DropBtn.pack(side='right',fill=tkinter.Y)
                    self.DropBtn.configure(bg = self.BGColor_Hover)
        except:
            pass
    #鼠标离开时的处理
    def onLeave(self,event):
        try:
            if self.State == "normal":
                event.widget.configure(cursor='arrow')
                if self.Image:
                    event.widget.configure(image = self.Image)
                elif self.BGColor:
                    event.widget.configure(bg = self.BGColor)
                if self.FGColor:
                    event.widget.configure(fg = self.FGColor)
                if self.Font:
                    event.widget.configure(font = self.Font)
                event.widget.update()
                if self.DropBtn:
                    self.DropBtn.pack_forget()
                    self.DropBtn.pack(side='right',fill=tkinter.Y)
                    self.DropBtn.configure(bg = self.BGColor)
        except:
            pass
    #鼠标按下时的处理
    def onClick(self,event):
        try:
            if self.State == "normal":
                event.widget.configure(cursor='hand2')
                if self.Image_Click:
                    event.widget.configure(image = self.Image_Click)
                elif self.BGColor_Click:
                    event.widget.configure(bg = self.BGColor_Click)
                if self.FGColor_Click:
                    event.widget.configure(fg = self.FGColor_Click)
                if self.Font_Click:
                    event.widget.configure(font = self.Font_Click)
                event.widget.update()
                if self.DropBtn:
                    self.DropBtn.pack_forget()
                    self.DropBtn.pack(side='right',fill=tkinter.Y)
                    self.DropBtn.configure(bg = self.BGColor_Click)
                if self.commandFunction:
                    onThreadingCallFunction(self.commandFunction,self.FunctionThreadDict,self.uiName,self.widgetName)
        except:
            pass
    #设置点击事件回调处理
    def SetCommandFunction(self,Func,uiName,widgetName):
        self.commandFunction = Func
        self.uiName = uiName
        self.widgetName = widgetName
    #设置下拉列表按钮点击事件回调处理
    def SetDropListCallBackFunction(self,Func,uiName,widgetName):
        self.droplistFunction = Func
        self.uiName = uiName
        self.widgetName = widgetName
    #取得当前画布
    def GetWidget(self):
        return self.Label
    #传递绑定事件
    def bind(self,EventName,callBack):
        if self.Label:
            self.Label.bind(EventName,callBack)
    #窗口大小变化
    def Configure(self,event):
        self.Redraw()
    #设置属性
    def configure(self,**kw):
        try:
           self.Label.configure(kw)
        except:
           pass
    #隐藏(兼容原Text控件)
    def pack_forget(self):
        return self.Label.pack_forget()
    #隐藏(兼容原Text控件)
    def grid_forget(self):
        return self.Label.grid_forget()
    #隐藏(兼容原Text控件)
    def place_forget(self):
        return self.Label.place_forget()
    #设置文字内容
    def SetText(self,text):
        self.Text = text
        if self.Label:
            self.Label.configure(text = self.Text)
    #取得文字内容
    def GetText(self):
        return self.Text
    #设置文字对齐
    def SetAnchor(self,anchor):
        self.Anchor = anchor
        if self.Label:
            self.Label.configure(anchor = self.Anchor)
    #取得文字对齐
    def GetAnchor(self):
        return self.Anchor
    #鼠标进入时的处理
    def onDropBtn_Enter(self,event):
        event.widget.configure(bg = self.BGColor_Hover)
        event.widget.itemconfig('text',fill=self.FGColor_Hover)
    #鼠标离开时的处理
    def onDropBtn_Leave(self,event):
        if event.x < 0:
            event.widget.configure(bg = self.BGColor_Hover)
        else:
            event.widget.configure(bg = self.BGColor)
        event.widget.itemconfig('text',fill=self.FGColor)
    #鼠标点击时的处理
    def onDropBtn_Button1(self,event):
        event.widget.configure(bg = self.BGColor_Click)
        event.widget.itemconfig('text',fill=self.FGColor_Click)
    #鼠标松开时的处理
    def onDropBtn_ButtonRelease1(self,event):
        if self.DropList:
            if self.DropListUI:
                self.DropListUI.destroy()
                self.DropListUI = None
            else:
                self.DropListUI = tkinter.Toplevel(self.Label)
                self.DropListUI.overrideredirect(True)
                self.DropListUI.wm_attributes("-topmost", 1)
                self.DropListUI.configure(bg = '#FFFFFF')
                self.DropListUIForm = tkinter.Canvas(self.DropListUI,highlightthickness=1,bd=1)
                self.DropListUIForm.configure(relief='solid')
                self.DropListUIForm.pack(fill=tkinter.BOTH,expand=1)
                def onDropListUI_Item_Enter(event):
                    event.widget.configure(bg = '#F0F0F0')
                def onDropListUI_Item_Leave(event):
                    event.widget.configure(bg = '#FFFFFF')
                def onDropListUI_Item_Button1(event):
                    event.widget.configure(bg = '#CCCCCC')
                def onDropListUI_Item_ButtonRelease1(event):
                    text = event.widget.cget('text')
                    self.SetText(text)
                    if self.droplistFunction:
                        onThreadingCallFunction(self.droplistFunction,self.FunctionThreadDict,self.uiName,self.widgetName,text)
                    self.DropListUI.destroy()
                    self.DropListUI = None
                    if self.DropBtn:
                        self.DropBtn.pack_forget()
                        self.DropBtn.pack(side='right',fill=tkinter.Y)
                        self.DropBtn.configure(bg = self.BGColor)
                DropListHeight = 4
                for itemText in self.DropList:
                    if self.Font:
                        itemButton = tkinter.Label(self.DropListUIForm,text=itemText,bg = '#FFFFFF',fg = '#000000',font=self.Font,width=self.LabelWidth,height=24)
                    else:
                        itemButton = tkinter.Label(self.DropListUIForm,text=itemText,bg = '#FFFFFF',fg = '#000000',width=self.LabelWidth,height=24)
                    itemButton.place(x = 4, y = DropListHeight , width=self.LabelWidth-8,height=self.LabelHeight)
                    itemButton.configure(cursor='hand2')
                    itemButton.configure(relief='flat')
                    itemButton.bind('<Enter>',onDropListUI_Item_Enter)
                    itemButton.bind('<Leave>',onDropListUI_Item_Leave)
                    itemButton.bind('<Button-1>',onDropListUI_Item_Button1)
                    itemButton.bind('<ButtonRelease-1>',onDropListUI_Item_ButtonRelease1)
                    DropListHeight = DropListHeight + self.LabelHeight + 4
                abs_x = self.Label.winfo_rootx()
                abs_y = self.Label.winfo_rooty()
                geoinfo = str('%dx%d+%d+%d'%(self.LabelWidth,DropListHeight,abs_x,abs_y+self.LabelHeight))
                self.DropListUI.geometry(geoinfo)
        event.widget.configure(bg = self.BGColor_Hover)
        event.widget.itemconfig('text',fill=self.FGColor_Hover)
    #设置下拉菜单
    def SetDropList(self,dropList):
        self.DropList = dropList
        if self.DropBtn is None:
            self.DropBtn = tkinter.Canvas(self.Label,width=24,height=self.LabelHeight,bg = self.BGColor,highlightthickness=0,bd=0)
            self.DropBtn.pack(side='right',fill=tkinter.Y)
            self.DropBtn.create_text(12,int(self.LabelHeight/2),text='▼',fill=self.FGColor,font=('宋体',12),anchor='center',tag='text')
            self.DropBtn.configure(relief='solid')
            self.DropBtn.bind('<Enter>',self.onDropBtn_Enter)
            self.DropBtn.bind('<Leave>',self.onDropBtn_Leave)
            self.DropBtn.bind('<Button-1>',self.onDropBtn_Button1)
            self.DropBtn.bind('<ButtonRelease-1>',self.onDropBtn_ButtonRelease1)
        elif self.DropList is None:
            self.DropBtn.destroy()
            self.DropBtn = None
    #取得下拉菜单
    def GetDropList(self):
        return self.DropList
    #设置当前是否可用
    def SetState(self,state):
        self.State = state
        if self.Label:
            self.Label.configure(state = self.State)
    #取得是否可用
    def GetState(self):
        return self.State
    #设置边框样式
    def SetRelief(self,relief):
        self.Relief = relief
        if self.Label:
            self.Label.configure(relief = self.Relief)
    #取得边框样式
    def GetRelief(self):
        return self.Relief
    #设置当前画布的背景色
    def SetBGColor(self,color):
        self.BGColor = color
        if self.Label:
            self.Label.configure(bg = self.BGColor)
    #取得当前画布的背景色
    def GetBGColor(self):
        return self.BGColor
    #设置标题栏的文字色
    def SetFGColor(self,color):
        self.FGColor = color
        if self.Label:
            self.Label.configure(fg = self.FGColor)
    #取得标题栏的文字色
    def GetFGColor(self):
        return self.FGColor
    #设置标题栏的字体
    def SetFont(self,font):
        self.Font = font
        if self.Label:
            self.Label.configure(font = self.Font)
    #取得标题栏的字体
    def GetFont(self):
        return self.Font
    #设置标题栏的字体
    def SetBGImage(self,fileName):
        global G_ExeDir
        global G_ResDir
        self.Image = None
        filePath = fileName
        if filePath and os.path.exists(filePath) == False:
            filePath = "Resources\\" + fileName
            if os.path.exists(filePath) == False:
                filePath = os.path.join(G_ExeDir,fileName)
                if os.path.exists(filePath) == False:
                    filePath = os.path.join(G_ResDir,fileName)
        if filePath and os.path.exists(filePath) == True:
            try:
                Image_Temp = Image.open(filePath).convert('RGBA')
                ImageWidth,ImageHeight = Image_Temp.size
                if self.Compound == 'none' or self.Compound == 'center':
                    ImageWidth = self.LabelWidth
                    ImageHeight = self.LabelHeight
                Image_Resize = Image_Temp.resize((ImageWidth, ImageHeight),Image.LANCZOS)
                self.Image = ImageTk.PhotoImage(Image_Resize)
                self.ImageFile = filePath
                if self.Label:
                    self.Label.configure(image = self.Image,compound=self.Compound)
            except:
                self.Image = None
    #取得标题栏的图片文件
    def GetBGImageFile(self):
        return self.ImageFile
    #设置图标的位置
    def SetCompound(self,compound):
        self.Compound = compound
        if self.Label:
            if self.ImageFile:
                self.SetBGImage(self.ImageFile)
            if self.ImageFile_Hover:
                self.SetBGImage_Hover(self.ImageFile_Hover)
            if self.ImageFile_Click:
                self.SetBGImage_Click(self.ImageFile_Click)
    #取得设置图标的位置
    def GetCompound(self):
        return self.Compound
    #设置鼠标悬停在标题栏时的背景色
    def SetBGColor_Hover(self,color):
        self.BGColor_Hover = color
    #取得鼠标悬停在标题栏时背景色
    def GetBGColor_Hover(self):
        return self.BGColor_Hover
    #设置鼠标悬停在标题栏时的文字色
    def SetFGColor_Hover(self,color):
        self.FGColor_Hover = color
    #取得鼠标悬停在标题栏时文字色
    def GetFGColor_Hover(self):
        return self.FGColor_Hover
    #设置标题栏的字体
    def SetFont_Hover(self,font):
        self.Font_Hover = font
    #取得标题栏的字体
    def GetFont_Hover(self):
        return self.Font_Hover
    #设置标题栏的字体
    def SetBGImage_Hover(self,fileName):
        global G_ExeDir
        global G_ResDir
        self.ImageFile_Hover = None
        filePath = fileName
        if filePath and os.path.exists(filePath) == False:
            filePath = "Resources\\" + fileName
            if os.path.exists(filePath) == False:
                filePath = os.path.join(G_ExeDir,fileName)
                if os.path.exists(filePath) == False:
                    filePath = os.path.join(G_ResDir,fileName)
        if filePath and os.path.exists(filePath) == True:
            try:
                Image_Temp = Image.open(filePath).convert('RGBA')
                ImageWidth,ImageHeight = Image_Temp.size
                if self.Compound == 'none' or self.Compound == 'center':
                    ImageWidth = self.LabelWidth
                    ImageHeight = self.LabelHeight
                Image_Resize = Image_Temp.resize((ImageWidth, ImageHeight),Image.LANCZOS)
                self.Image_Hover = ImageTk.PhotoImage(Image_Resize)
                self.ImageFile_Hover = filePath
            except:
                self.Image_Hover = None
    #取得标题栏的图片文件
    def GetBGImageFile_Hover(self):
        return self.ImageFile_Hover
    #设置鼠标按下标题栏时的背景色
    def SetBGColor_Click(self,color):
        self.BGColor_Click = color
    #取得鼠标按下标题栏时背景色
    def GetBGColor_Click(self):
        return self.BGColor_Click
    #设置鼠标按下标题栏时的文字色
    def SetFGColor_Click(self,color):
        self.FGColor_Click = color
    #取得鼠标按下标题栏时文字色
    def GetFGColor_Click(self):
        return self.FGColor_Click
    #设置鼠标按下标题栏时字体
    def SetFont_Click(self,font):
        self.Font_Click = font
    #取得鼠标按下标题栏时字体
    def GetFont_Click(self):
        return self.Font_Click
    #设置标题栏的字体
    def SetBGImage_Click(self,fileName):
        global G_ExeDir
        global G_ResDir
        self.ImageFile_Click = None
        filePath = fileName
        if filePath and os.path.exists(filePath) == False:
            filePath = "Resources\\" + fileName
            if os.path.exists(filePath) == False:
                filePath = os.path.join(G_ExeDir,fileName)
                if os.path.exists(filePath) == False:
                    filePath = os.path.join(G_ResDir,fileName)
        if filePath and os.path.exists(filePath) == True:
            try:
                Image_Temp = Image.open(filePath).convert('RGBA')
                ImageWidth,ImageHeight = Image_Temp.size
                if self.Compound == 'none' or self.Compound == 'center':
                    ImageWidth = self.LabelWidth
                    ImageHeight = self.LabelHeight
                Image_Resize = Image_Temp.resize((ImageWidth, ImageHeight),Image.LANCZOS)
                self.Image_Click = ImageTk.PhotoImage(Image_Resize)
                self.ImageFile_Click = filePath
            except:
                self.Image_Click = None
    #取得标题栏的图片文件
    def GetBGImageFile_Click(self):
        return self.ImageFile_Click
    #展开
    def Redraw(self):
        self.LabelWidth = self.Label.winfo_width()
        self.LabelHeight = self.Label.winfo_height()
        if self.LabelWidth == 1 and self.LabelHeight == 1:
            self.LabelHeight = 100
            self.LabelHeight = 24
        if self.ImageFile and os.path.exists(self.ImageFile) == True:
            if self.Image is None or (self.Image.width() != self.LabelWidth or self.Image.height() != self.LabelHeight):
                try:
                    Image_Temp = Image.open(self.ImageFile).convert('RGBA')
                    ImageWidth,ImageHeight = Image_Temp.size
                    if self.Compound == 'none' or self.Compound == 'center':
                        ImageWidth = self.LabelWidth
                        ImageHeight = self.LabelHeight
                    Image_Resize = Image_Temp.resize((ImageWidth, ImageHeight),Image.LANCZOS)
                    self.Image = ImageTk.PhotoImage(Image_Resize)
                    if self.Label:
                        self.Label.configure(image = self.Image)
                except:
                    self.Image = None
        if self.ImageFile_Hover and os.path.exists(self.ImageFile_Hover) == True:
            if self.Image_Hover is None or (self.Image_Hover.width() != self.LabelWidth or self.Image_Hover.height() != self.LabelHeight):
                try:
                    Image_Temp = Image.open(self.ImageFile_Hover).convert('RGBA')
                    ImageWidth,ImageHeight = Image_Temp.size
                    if self.Compound == 'none' or self.Compound == 'center':
                        ImageWidth = self.LabelWidth
                        ImageHeight = self.LabelHeight
                    Image_Resize = Image_Temp.resize((ImageWidth, ImageHeight),Image.LANCZOS)
                    self.Image_Hover = ImageTk.PhotoImage(Image_Resize)
                except:
                    self.Image_Hover = None
        if self.ImageFile_Click and os.path.exists(self.ImageFile_Click) == True:
            if self.Image_Click is None or (self.Image_Click.width() != self.LabelWidth or self.Image_Click.height() != self.LabelHeight):
                try:
                    Image_Temp = Image.open(self.ImageFile_Click).convert('RGBA')
                    ImageWidth,ImageHeight = Image_Temp.size
                    if self.Compound == 'none' or self.Compound == 'center':
                        ImageWidth = self.LabelWidth
                        ImageHeight = self.LabelHeight
                    Image_Resize = Image_Temp.resize((ImageWidth, ImageHeight),Image.LANCZOS)
                    self.Image_Click = ImageTk.PhotoImage(Image_Resize)
                except:
                    self.Image_Click = None
        if self.Label:
            self.Label.configure(fg = self.FGColor)
#圆角编辑框 
class CustomEntry:
    def __init__(self, widget):
        self.ParentWidget = widget
        self.EntryValue = tkinter.StringVar()
        self.EntryValue.set('')
        self.Canvas_width = 100
        self.Canvas_height = 24
        self.Canvas = tkinter.Canvas(self.ParentWidget,width=self.Canvas_width,height=self.Canvas_height,bg = '#FFFFFF',highlightthickness=0,bd=0)
        self.Entry = tkinter.Entry(self.Canvas,textvariable=self.EntryValue,background='#FFFFFF')
        self.Font = tkinter.font.Font(font='TkDefaultFont')
        self.TipText = ''
        self.TipTextColor = '#777777'
        self.TipLabel = tkinter.Label(self.Entry, text = '', justify = 'left',anchor=tkinter.W,bg='#FFFFFF')
        self.TipLabel.configure(fg = self.TipTextColor)
        self.TipLabel.bind('<Button-1>',self.onLeftClickTip)
        self.TipLabel.bind('<B1-Motion>',self.onLeftMotionTip)
        self.TipLabel.bind('<ButtonRelease-1>',self.onLeftReleaseTip)
        self.TipLabel.bind('<Double-1>',self.onDoubleClickTip)
        self.TipLabel.bind('<Button-3>',self.onRightClickTip)
        self.Entry.bind('<FocusOut>',self.onResetTip)
        self.Canvas.bind('<Configure>',self.Configure)
        self.LeftIconImage = None
        self.LeftPhotoIconImage = None
        self.LeftIconImageFile = None
        self.LeftIconClickedFunction = None
        self.RightIconImage = None
        self.RightPhotoIconImage = None
        self.RightIconImageFile = None
        self.RightIconClickedFunction = None
        self.TextChangedFunction = None
        self.uiName = None
        self.widgetName = None
        self.RoundRadius = 0
        self.Restriction = ''
        self.InnerSpacingX = 0
        self.InnerSpacingY = 0
        self.InnerBorderType = None
        self.InnerBorderWidth = 0
        self.InnerBorderDash = None
        self.InnerBorderColor = '#000000'
    #取得当前编辑框宽度
    def GetWidth(self):
        return self.Canvas.winfo_width()
    #传递绑定事件
    def bind(self,EventName,callBack):
        if self.Entry:
            self.Entry.bind(EventName,callBack)
    #取得当前编辑框高度
    def GetHeight(self):
        return self.Canvas.winfo_height()
    #取得Canvas
    def GetWidget(self):
        return self.Canvas
    #取得Entry
    def GetEntry(self):
        return self.Entry
    #窗口大小变化
    def Configure(self,event):
        self.Rebuild()
    #取得边框样式
    def Hide(self,layout="place"):
        if layout == "pack":
            self.Canvas.pack_forget()
        elif layout == "grid":
            self.Canvas.grid_forget()
        else:
            self.Canvas.place_forget()
    #重载一下cget
    def cget(self,attrib):
        return self.Entry.cget(attrib)
    #设置属性
    def configure(self,**kw):
        if 'text' in kw:
            self.SetText(kw['text'])
        else:
            try:
               self.Entry.configure(kw)
            except:
               pass
    #设置焦点
    def focus_set(self):
        return self.Entry.focus_set()
    #隐藏(兼容原Text控件)
    def pack_forget(self):
        return self.Canvas.pack_forget()
    #隐藏(兼容原Text控件)
    def grid_forget(self):
        return self.Canvas.grid_forget()
    #隐藏(兼容原Text控件)
    def place_forget(self):
        return self.Canvas.place_forget()
    #鼠标进入和离开图标时的处理
    def onIconEnter(self,event):
        event.widget.configure(cursor='hand2')
    def onIconLeave(self,event):
        try:
            event.widget.configure(cursor='arrow')
        except:
            pass
    def onIconClick(self,event,tagName):
        print("Click " + tagName)
        if tagName == "left_icon":
            if self.LeftIconClickedFunction:
                self.LeftIconClickedFunction(self.uiName,self.widgetName)
        else:
            if self.RightIconClickedFunction:
                self.RightIconClickedFunction(self.uiName,self.widgetName)
    #鼠标左键单击
    def onLeftClickTip(self,event):
        self.TipLabel.place_forget()
        self.Entry.focus_set()
    #鼠标左键拖动Tip
    def onLeftMotionTip(self,event):
        self.TipLabel.place_forget()
        self.Entry.focus_set()
    #鼠标左键松开Tip
    def onLeftReleaseTip(self,event):
        self.TipLabel.place_forget()
        self.Entry.focus_set()
    #鼠标左键双击Tip
    def onDoubleClickTip(self,event):
        pass
    #鼠标右键单击
    def onRightClickTip(self,event):
        self.TipLabel.place_forget()
        self.Entry.focus_set()
        self.Entry.event_generate("<Button-3>",x = event.x,y = event.y)
    #点击Tiip
    def onResetTip(self,event):
        text =  self.EntryValue.get()
        if text == '':
            self.SetTipText(self.TipText)
    #设置左边的图标按钮
    def SetLeftIcon(self,IconFile):
        global G_ExeDir
        global G_ResDir
        filePath = IconFile
        if IconFile:
            if filePath and os.path.exists(filePath) == False:
                 filePath = "Resources\\" + IconFile
                 if os.path.exists(filePath) == False:
                    filePath = os.path.join(G_ExeDir,IconFile)
                    if os.path.exists(filePath) == False:
                        filePath = os.path.join(G_ResDir,IconFile)
            if filePath and os.path.exists(filePath) == True:
                imagePath,imageFile = os.path.split(filePath)
                try:
                    self.LeftIconImage = Image.open(filePath).convert('RGBA')
                    IconSize = self.GetHeight() - 2 * self.InnerSpacingY
                    Image_Resize = self.LeftIconImage.resize((IconSize, IconSize),Image.LANCZOS)
                    self.LeftPhotoIconImage = ImageTk.PhotoImage(Image_Resize)
                    self.LeftIconImageFile = imageFile
                except:
                    self.LeftIconImage = None
                    self.LeftPhotoIconImage = None
                    self.LeftIconImageFile = None
        self.Redraw()
    #设置左边的图标按钮回调函数
    def SetLeftIconClickFunction(self,callBackFunc,uiName,widgetName):
        self.LeftIconClickedFunction = callBackFunc
        self.uiName = uiName
        self.widgetName = widgetName
        self.Canvas.tag_bind('left_icon','<Enter>',self.onIconEnter)
        self.Canvas.tag_bind('left_icon','<Leave>',self.onIconLeave)
        self.Canvas.tag_bind('left_icon','<ButtonRelease-1>',EventFunction_Adaptor(self.onIconClick,tagName='left_icon'))
    #设置右边的图标按钮
    def SetRightIcon(self,IconFile):
        global G_ExeDir
        global G_ResDir
        filePath = IconFile
        if IconFile:
            if filePath and os.path.exists(filePath) == False:
                filePath = "Resources\\" + IconFile
                if os.path.exists(filePath) == False:
                    filePath = os.path.join(G_ExeDir,IconFile)
                    if os.path.exists(filePath) == False:
                        filePath = os.path.join(G_ResDir,IconFile)
            if filePath and os.path.exists(filePath) == True:
                imagePath,imageFile = os.path.split(filePath)
                try:
                    self.RightIconImage = Image.open(filePath).convert('RGBA')
                    IconSize = self.GetHeight() - 2 * self.InnerSpacingY
                    Image_Resize = self.RightIconImage.resize((IconSize, IconSize),Image.LANCZOS)
                    self.RightPhotoIconImage = ImageTk.PhotoImage(Image_Resize)
                    self.RightIconImageFile = imageFile
                except:
                    self.RightIconImage = None
                    self.RightPhotoIconImage = None
                    self.RightIconImageFile = None
        self.Redraw()
    #设置左边的图标按钮回调函数
    def SetRightIconClickFunction(self,callBackFunc,uiName,widgetName):
        self.RightIconClickedFunction = callBackFunc
        self.uiName = uiName
        self.widgetName = widgetName
        self.Canvas.tag_bind('right_icon','<Enter>',self.onIconEnter)
        self.Canvas.tag_bind('right_icon','<Leave>',self.onIconLeave)
        self.Canvas.tag_bind('right_icon','<ButtonRelease-1>',EventFunction_Adaptor(self.onIconClick,tagName='right_icon'))
    #内置的输入文本被修改时的回调函数
    def onTextChangedCallBack(self,*args):
        if self.TextChangedFunction:
            Text = self.EntryValue.get()
            print("TextChanged:"+Text)
            self.TextChangedFunction(self.uiName,self.widgetName,Text)
    #设置输入文本被修改时的回调函数
    def SetTextChangedFunction(self,callBackFunc,uiName,widgetName):
        self.TextChangedFunction = callBackFunc
        self.uiName = uiName
        self.widgetName = widgetName
        self.EntryValue.trace('w',self.onTextChangedCallBack)
    #设置边角半径
    def SetRoundRadius(self,radius):
        self.RoundRadius = radius
        w = self.GetWidth()
        h = self.GetHeight()
        if radius > 0 and w > 1 and h > 1:
            HRGN = win32gui.CreateRoundRectRgn(0,0,w,h,radius,radius)
            win32gui.SetWindowRgn(self.Canvas.winfo_id(), HRGN,1)
    #取得边角半径
    def GetRoundRadius(self):
        return self.RoundRadius
    #按键响应函数
    def onKey(self,event):
        text = event.char
        if text != "" and text != "\x08":
            if hasattr(FunLib,"GetElementName") == True:
                uiName,elementName = FunLib.GetElementName(self)
            if self.Restriction != "":
                if self.Restriction == "letter":
                    if text.isalpha() == False:
                        FunLib.MessageBox(elementName+"请输入字母","类型限制")
                        return "break"
                if self.Restriction == "number":
                    if FunLib.IsNumeric(text) == False:
                        FunLib.MessageBox(elementName+"请输入数字","类型限制")
                        return "break"
                if self.Restriction == "letter":
                    if text.isalpha() == False:
                        FunLib.MessageBox(elementName+"请输入字母","类型限制")
                        return "break"
                if self.Restriction == "alphanumeric":
                    if FunLib.IsAlphanumeric(text) == False:
                        FunLib.MessageBox(elementName+"请输入字母或数字","类型限制")
                        return "break"
                if self.Restriction == "integer":
                    if FunLib.IsInt(text) == False:
                        FunLib.MessageBox(elementName+"请输入整数","类型限制")
                        return "break"
                if self.Restriction == "phone":
                    if FunLib.IsMobilePhone(text) == False:
                        FunLib.MessageBox(elementName+"请输入手机号码","类型限制")
                        return "break"
                if self.Restriction == "email":
                    if FunLib.IsEmail(text) == False:
                        FunLib.MessageBox(elementName+"请输入电子邮件","类型限制")
                        return "break"
    #设置类型限制
    def SetRestriction(self,restriction):
        self.Restriction = restriction
        self.Entry.bind('<Key>',self.onKey,add=True)
    #取得类型限制
    def GetRestriction(self):
        return self.Restriction
    #设置横向间距
    def SetInnerSpacingX(self,InnerSpacingX):
        self.InnerSpacingX = InnerSpacingX
    #取得横向间距
    def GetInnerSpacingX(self):
        return self.InnerSpacingX
    #设置纵向间距
    def SetInnerSpacingY(self,InnerSpacingY):
        self.InnerSpacingY = InnerSpacingY
    #取得纵向间距
    def GetInnerSpacingY(self):
        return self.InnerSpacingY
    #设置内边框类型
    def SetInnerBorderType(self,InnerBorderType):
        self.InnerBorderType = InnerBorderType
    #取得内边框类型
    def GetInnerBorderType(self):
        return self.InnerBorderType
    #设置内边框宽度
    def SetInnerBorderWidth(self,InnerBorderWidth):
        self.InnerBorderWidth = InnerBorderWidth
    #取得内边框宽度
    def GetInnerBorderWidth(self):
        return self.InnerBorderWidth
    #设置内边框Dash
    def SetInnerBorderDash(self,InnerBorderDash):
        self.InnerBorderDash = InnerBorderDash
    #取得内边框Dash
    def GetInnerBorderDash(self):
        return self.InnerBorderDash
    #设置内边框颜色
    def SetInnerBorderColor(self,InnerBorderColor):
        self.InnerBorderColor = InnerBorderColor
    #取得内边框颜色
    def GetInnerBorderColor(self):
        return self.InnerBorderColor
    #设置文字
    def SetText(self,text):
        if text != "":
            self.TipLabel.place_forget()
        else:
            self.SetTipText(self.TipText)
        self.EntryValue.set(text)
    #取得文字
    def GetText(self):
        text =  self.EntryValue.get()
        if text != "":
            if hasattr(FunLib,"GetElementName") == True:
                uiName,elementName = FunLib.GetElementName(self)
                if self.Restriction == "letter":
                    if text.isalpha() == False:
                        FunLib.MessageBox(elementName+"请输入字母","类型限制")
                        return None
                if self.Restriction == "number":
                    if FunLib.IsNumeric(text) == False:
                        FunLib.MessageBox(elementName+"请输入数字","类型限制")
                        return None
                if self.Restriction == "letter":
                    if text.isalpha() == False:
                        FunLib.MessageBox(elementName+"请输入字母","类型限制")
                        return None
                if self.Restriction == "alphanumeric":
                    if FunLib.IsAlphanumeric(text) == False:
                        FunLib.MessageBox(elementName+"请输入字母或数字","类型限制")
                        return None
                if self.Restriction == "integer":
                    if FunLib.IsInt(text) == False:
                        FunLib.MessageBox(elementName+"请输入整数","类型限制")
                        return None
                if self.Restriction == "phone":
                    if FunLib.IsMobilePhone(text) == False:
                        FunLib.MessageBox(elementName+"请输入手机号码","类型限制")
                        return None
                if self.Restriction == "email":
                    if FunLib.IsEmail(text) == False:
                        FunLib.MessageBox(elementName+"请输入电子邮件","类型限制")
                        return None
        return text
    #设置字体
    def SetFont(self,font):
        self.Font = font
        self.Entry.configure(font = self.Font)
        self.TipLabel.configure(font = self.Font)
    #取得字体
    def GetFont(self):
        return self.Font
    #设置提示文字
    def SetTipText(self,text):
        self.TipText = text
        if text != '':
            TipLabelWidth = self.Entry.winfo_width()
            if self.LeftIconImage:
                TipLabelWidth = TipLabelWidth - self.Entry.winfo_height() - 2 * self.InnerSpacingX
            if self.RightIconImage:
                TipLabelWidth = TipLabelWidth - self.Entry.winfo_height() - 2 * self.InnerSpacingX
            self.TipLabel.place(x=2,y=2,width=TipLabelWidth-4,height=self.Entry.winfo_height()-4)
            self.TipLabel.configure(bg = self.GetBGColor())
            self.TipLabel.configure(fg = self.TipTextColor)
            self.TipLabel.configure(text = self.TipText)
        else:
            self.TipLabel.place_forget()
    #取得提示文字
    def GetTipText(self):
        return self.TipText
    #设置提示文字颜色
    def SetTipFGColor(self,color):
        self.TipTextColor = color
        self.TipLabel.configure(fg=color)
    #取得提示文字颜色
    def GetTipFGColor(self):
        return self.TipTextColor
    #设置背景色
    def SetBGColor(self,bgColor):
        self.Entry.configure(bg = bgColor)
        self.TipLabel.configure(bg = bgColor)
    #取得背景色
    def GetBGColor(self):
        return self.Entry.cget('bg')
    #设置文字色
    def SetFGColor(self,fgColor):
        self.Entry.configure(fg = fgColor)
    #取得文字色
    def GetFGColor(self):
        return self.Entry.cget('fg')
    #设置只读状态的背景色
    def SetBGColor_ReadOnly(self,bgColor):
        self.Entry.configure(readonlybackground = bgColor)
    #取得只读状态的背景色
    def GetBGColor_ReadOnly(self):
        return self.Entry.cget('readonlybackground')
    #设置替代符
    def SetShowChar(self,showChar):
        self.Entry.configure(show = showChar)
    #取得替代符
    def GetShowChar(self):
        return self.Entry.cget('show')
    #设置对齐方式
    def SetJustify(self,justify):
        self.Entry.configure(justify = justify)
    #取得对齐方式
    def GetJustify(self):
        return self.Entry.cget('justify')
    #设置样式
    def SetRelief(self,relief):
        self.Entry.configure(relief = relief)
    #取得样式
    def GetRelief(self):
        return self.Entry.cget('relief')
    #设置状态
    def SetState(self,state):
        self.Entry.configure(state = state)
    #取得状态
    def GetState(self):
        return self.Entry.cget('state')
    #重置
    def Rebuild(self):
        if self.RoundRadius > 0:
            self.SetRoundRadius(self.RoundRadius)
        IconSize = self.GetHeight()
        if self.LeftIconImage:
            Image_Resize = self.LeftIconImage.resize((IconSize, IconSize),Image.LANCZOS)
            self.LeftPhotoIconImage = ImageTk.PhotoImage(Image_Resize)
        if self.RightIconImage:
            Image_Resize = self.RightIconImage.resize((IconSize, IconSize),Image.LANCZOS)
            self.RightPhotoIconImage = ImageTk.PhotoImage(Image_Resize)
        self.Redraw()
    #重绘
    def Redraw(self):
        AllWidth = self.GetWidth()
        IconWidth = self.GetHeight()
        if AllWidth == 1 or IconWidth == 1:
            AllWidth = 160
            IconWidth = 24
        EntryWidth = AllWidth
        EntryLeft = 0
        #左图标
        if self.LeftPhotoIconImage:
            self.Canvas.create_image(self.InnerSpacingX,self.InnerSpacingY,anchor=tkinter.NW,image=self.LeftPhotoIconImage,tag="left_icon")
            EntryWidth = EntryWidth - 2 * self.InnerSpacingX - IconWidth
            EntryLeft = 2 * self.InnerSpacingX + IconWidth
        #左图标
        if self.RightPhotoIconImage:
            self.Canvas.create_image(AllWidth - self.InnerSpacingX,self.InnerSpacingY,anchor=tkinter.NE,image=self.RightPhotoIconImage,tag="right_icon")
            EntryWidth = EntryWidth - 2 * self.InnerSpacingX - IconWidth
        self.Canvas.delete('border')
        if self.InnerBorderType =='borderline':
            self.Entry.place(x = EntryLeft+self.InnerBorderWidth , y = self.InnerBorderWidth , width = EntryWidth-2*self.InnerBorderWidth + 1 ,height=IconWidth-2*self.InnerBorderWidth + 1)
            if self.InnerBorderDash and self.InnerBorderDash != [0,0] and self.InnerBorderDash != (0,0):
                self.Canvas.create_line(EntryLeft,0,EntryWidth,0,width=self.InnerBorderWidth,fill = self.InnerBorderColor,dash=self.InnerBorderDash,tag='border')
                self.Canvas.create_line(EntryLeft,0,EntryLeft,IconWidth,width=self.InnerBorderWidth,fill = self.InnerBorderColor,dash=self.InnerBorderDash,tag='border')
                self.Canvas.create_line(EntryLeft+EntryWidth,0,EntryLeft+EntryWidth,IconWidth,width=self.InnerBorderWidth,fill = self.InnerBorderColor,dash=self.InnerBorderDash,tag='border')
                self.Canvas.create_line(EntryLeft,IconWidth,EntryWidth,IconWidth,width=self.InnerBorderWidth,fill = self.InnerBorderColor,dash=self.InnerBorderDash,tag='border')
            else:
               self.Canvas.create_line(EntryLeft,0,EntryWidth,0,width=self.InnerBorderWidth,fill = self.InnerBorderColor,tag='border')
               self.Canvas.create_line(EntryLeft,0,EntryLeft,IconWidth,width=self.InnerBorderWidth,fill = self.InnerBorderColor,tag='border')
               self.Canvas.create_line(EntryLeft+EntryWidth,0,EntryLeft+EntryWidth,IconWidth,width=self.InnerBorderWidth,fill = self.InnerBorderColor,tag='border')
               self.Canvas.create_line(EntryLeft,IconWidth,EntryWidth,IconWidth,width=self.InnerBorderWidth,fill = self.InnerBorderColor,tag='border')
        elif self.InnerBorderType =='underline':
            if self.InnerBorderDash and self.InnerBorderDash != [0,0] and self.InnerBorderDash != (0,0):
               self.Canvas.create_line(EntryLeft,IconWidth-self.InnerBorderWidth,EntryLeft+EntryWidth,IconWidth-self.InnerBorderWidth,width=self.InnerBorderWidth,fill = self.InnerBorderColor,dash=self.InnerBorderDash,tag='border')
            else:
               self.Canvas.create_line(EntryLeft,IconWidth-self.InnerBorderWidth,EntryLeft+EntryWidth,IconWidth-self.InnerBorderWidth,width=self.InnerBorderWidth,fill = self.InnerBorderColor,tag='border')
            self.Entry.place(x = EntryLeft , y = 0 , width = EntryWidth ,height=IconWidth-self.InnerBorderWidth)
        else:
            self.Entry.place(x = EntryLeft , y = 0 , width = EntryWidth ,height=IconWidth)
        if self.GetText() == '' and self.TipText != '':
            self.SetTipText(self.TipText)
#圆角编辑框 
class CustomText:
    def __init__(self, widget ,autowrap = None):
        self.ParentWidget = widget
        self.Canvas_width = 400
        self.Canvas_height = 200
        try:
            ParentColor = self.ParentWidget.cget('bg')
        except:
            ParentColor = '#EFEFEF'
        self.Canvas = tkinter.Canvas(self.ParentWidget,width=self.Canvas_width,height=self.Canvas_height,bg = ParentColor,highlightthickness=0,bd=0)
        if autowrap is True:
            self.Text = tkinter.Text(self.Canvas,background='#FFFFFF',undo=True,wrap=tkinter.WORD)
        elif autowrap is False:
            self.Text = tkinter.Text(self.Canvas,background='#FFFFFF',undo=True,wrap=tkinter.NONE)
        else:
            self.Text = tkinter.Text(self.Canvas,background='#FFFFFF',undo=True)
        self.Text.place(x=0, y=0,width=self.Canvas_width,height=self.Canvas_height)
        self.Relief = self.Text.cget('relief')
        self.yview = self.Text.yview
        self.Font = tkinter.font.Font(font='TkDefaultFont')
        self.Canvas.bind('<Configure>',self.Configure)
        self.HScrollbar = None
        self.HScrollbar_Visible = False
        self.VScrollbar = None
        self.VScrollbar_Visible = False
        self.uiName = None
        self.widgetName = None
    #取得当前编辑框宽度
    def GetWidth(self):
        return self.Canvas.winfo_width()
    #传递绑定事件
    def bind(self,EventName,callBack):
        if self.Text:
            self.Text.bind(EventName,callBack)
    #取得当前编辑框高度
    def GetHeight(self):
        return self.Canvas.winfo_height()
    #取得Canvas
    def GetWidget(self):
        return self.Canvas
    #取得Text
    def GetEntry(self):
        return self.Text
    #窗口大小变化
    def Configure(self,event):
        self.Rebuild()
    #Text移动到相应位置
    def moveto(self,yview):
        if self.Text:
            self.Text.yview.moveto(yview)
    #取得边框样式
    def Hide(self,layout="place"):
        if layout == "pack":
            self.Canvas.pack_forget()
        elif layout == "grid":
            self.Canvas.grid_forget()
        else:
            self.Canvas.place_forget()
    #重载一下cget
    def cget(self,attrib):
        return self.Text.cget(attrib)
    #定位当前光标位置
    def see(self,position):
        return self.Text.see(position)
    #取得索引位置
    def index(self,position):
        return self.Text.index(position)
    #设置当前处于焦点
    def focus_set(self):
        return self.Text.focus_set()
    #清空缓冲(兼容原Text控件)
    def edit_reset(self):
        return self.Text.edit_reset()
    #隐藏(兼容原Text控件)
    def pack_forget(self):
        return self.Canvas.pack_forget()
    #隐藏(兼容原Text控件)
    def grid_forget(self):
        return self.Canvas.grid_forget()
    #隐藏(兼容原Text控件)
    def place_forget(self):
        return self.Canvas.place_forget()
    #清空缓冲
    def ClearCache(self):
        return self.Text.edit_reset()
    #设置属性
    def configure(self,**kw):
        if 'text' in kw:
            self.SetText(kw['text'])
        else:
            try:
               self.Text.configure(kw)
            except:
               pass
    #设置焦点
    def focus_set(self):
        return self.Text.focus_set()
    #设置文字
    def SetText(self,text):
        self.Text.delete('0.0', tkinter.END)
        self.Text.insert(tkinter.END,text)
    #取得文字
    def GetText(self):
        return self.Text.get('0.0', tkinter.END)
    #设置自动换行
    def SetAutoWrap(self,autoWrap):
        self.AutoWrap = autoWrap
        if autoWrap == True:
            self.Text.configure(wrap=tkinter.WORD)
        else:
            self.Text.configure(wrap=tkinter.NONE)
    #取得自动换行
    def GetAutoWrap(self):
        return self.AutoWrap
    #退格
    def BackSpace(self):
        self.Text.delete('insert-1c', 'insert')
    #设置字体
    def SetFont(self,font):
        self.Font = font
        self.Text.configure(font = self.Font)
    #取得字体
    def GetFont(self):
        return self.Font
    #设置背景色
    def SetBGColor(self,bgColor):
        self.Text.configure(bg = bgColor)
    #取得背景色
    def GetBGColor(self):
        return self.Text.cget('bg')
    #设置文字色
    def SetFGColor(self,fgColor):
        self.Text.configure(fg = fgColor)
    #取得文字色
    def GetFGColor(self):
        return self.Text.cget('fg')
    #设置样式
    def SetRelief(self,relief):
        self.Relief = relief
        CanvasWidth = self.GetWidth()
        CanvasHeight = self.GetHeight()
        if CanvasWidth > 1 and CanvasHeight > 1: 
            if self.Relief == "flat":
                self.Text.place(x = 0, y = 0,width = CanvasWidth,height=CanvasHeight)
            else:
                self.Text.place(x = 2, y = 2,width = CanvasWidth-4,height=CanvasHeight-4)
        self.Text.configure(relief = relief)
    #取得样式
    def GetRelief(self):
        return self.Relief
    #设置状态
    def SetState(self,state):
        self.Text.configure(state = state)
    #取得状态
    def GetState(self):
        return self.Text.cget('state')
    #设置标记状态
    def tag_config(self,tag,**kw):
        self.Text.tag_config(tag,kw)
    #取得属性
    def cget(self,attrib):
        return self.Text.cget(attrib)
    #设置属性
    def configure(self,**kw):
        self.Text.configure(kw)
    #使用横向滚动条
    def SetHScrollBar(self):
        if self.HScrollbar is None:
            self.HScrollbar = tkinter.ttk.Scrollbar(self.Canvas,orient=tkinter.HORIZONTAL)
        CanvasWidth = self.GetWidth()
        CanvasHeight = self.GetHeight()
        if self.Relief == "flat":
            self.Text.place(height = CanvasHeight - 20)
        else:
            self.Text.place(height = CanvasHeight - 24)
        if self.VScrollbar_Visible:
            self.Text.place(x=0, y=0,width=CanvasWidth-20,height=CanvasHeight-20)
            self.HScrollbar.place(x = 0,y = CanvasHeight - 20,width = CanvasWidth - 20,height = 20)
            self.VScrollbar.place(x = CanvasWidth - 20,y = 0,width = 20,height = CanvasHeight-20)
        else:
            self.Text.place(x=0, y=0,width=CanvasWidth,height=CanvasHeight-20)
            self.HScrollbar.place(x = 0,y = CanvasHeight - 20,width = CanvasWidth,height = 20)
        self.HScrollbar.config(command = self.Text.xview)
        self.Text.config(xscrollcommand = self.HScrollbar.set)
        self.HScrollbar_Visible = True
    #不使用横向滚动条
    def RemoveHScrollBar(self):
        if self.HScrollbar:
            CanvasWidth = self.GetWidth()
            CanvasHeight = self.GetHeight()
            if self.Relief == "flat":
                self.Text.place(height = CanvasHeight)
            else:
                self.Text.place(height = CanvasHeight-4)
            self.HScrollbar.place_forget()
            self.HScrollbar.config(command = None)
            self.Text.config(xscrollcommand = None)
            self.HScrollbar_Visible = False
    #使用纵向滚动条
    def SetVScrollBar(self):
        if self.VScrollbar is None:
            self.VScrollbar = tkinter.ttk.Scrollbar(self.Canvas,orient=tkinter.VERTICAL)
        CanvasWidth = self.GetWidth()
        CanvasHeight = self.GetHeight()
        if self.Relief == "flat":
            self.Text.place(width = CanvasWidth - 20)
        else:
            self.Text.place(width = CanvasWidth - 20 - 4)
        if self.HScrollbar_Visible:
            self.Text.place(x=0, y=0,width=CanvasWidth-20,height=CanvasHeight-20)
            self.HScrollbar.place(x = 0,y = CanvasHeight - 20,width = CanvasWidth - 20,height = 20)
            self.VScrollbar.place(x = CanvasWidth - 20,y = 0,width = 20,height = CanvasHeight-20)
        else:
            self.Text.place(x=0, y=0,width=CanvasWidth-20,height=CanvasHeight)
            self.VScrollbar.place(x = CanvasWidth - 20,y = 0,width = 20,height = CanvasHeight)
        self.VScrollbar.config(command = self.Text.yview)
        self.Text.config(yscrollcommand = self.VScrollbar.set)
        self.VScrollbar_Visible = True
    #滚动条横向移动
    def MovingScrollXOffset(self,step=0.1):
        self.Text.xview("scroll",step,"units")
    #滚动条纵向移动
    def MovingScrollYOffset(self,step=0.1):
        self.Text.yview("scroll",step,"units")
    #滚动条横向移动到目标值
    def MovingScrollXTo(self,x=1.0):
        self.Text.xview_moveto(x)
    #滚动条纵向移动到目标值
    def MovingScrollYTo(self,y=1.0):
        self.Text.yview_moveto(y)
    #不使用纵向滚动条
    def RemoveVScrollBar(self):
        if self.VScrollbar:
            CanvasWidth = self.GetWidth()
            CanvasHeight = self.GetHeight()
            if self.Relief == "flat":
                self.Text.place(width = CanvasWidth)
            else:
                self.Text.place(width = CanvasWidth-4)
            self.VScrollbar.place_forget()
            self.VScrollbar.config(command = None)
            self.Text.config(yscrollcommand = None)
            self.VScrollbar_Visible = False
    #重置
    def Rebuild(self):
        self.Redraw()
    #重绘
    def Redraw(self):
        CanvasWidth = self.GetWidth()
        CanvasHeight = self.GetHeight()
        if self.HScrollbar_Visible and self.VScrollbar_Visible:
            self.SetHScrollBar()
            self.SetVScrollBar()
            CanvasWidth = CanvasWidth - 20
            CanvasHeight = CanvasHeight - 20
        elif self.HScrollbar_Visible:
            self.SetHScrollBar()
            CanvasHeight = CanvasHeight - 20
        elif self.VScrollbar_Visible:
            self.SetVScrollBar()
            CanvasWidth = CanvasWidth - 20
        if self.Relief == "flat":
            self.Text.place(x = 0, y = 0,width = CanvasWidth,height=CanvasHeight)
        else:
            self.Text.place(x = 2, y = 2,width = CanvasWidth-4,height=CanvasHeight-4)
class SwitchButton:
    def __init__(self, widget):
        self.ParentWidget = widget
        self.Shape = 'circular'
        self.CurrValue = False
        self.OnText = ""
        self.OnTextColor = '#FFFFFF'
        self.OffText = ""
        self.OffTextColor = '#FFFFFF'
        self.TextFont = tkinter.font.Font(font='TkDefaultFont')
        self.SwitchMode = 1 #立即和动画模式
        self.FrameDelay = 1
        self.BGColor = '#EFEFEF'
        self.OffBGColor = '#333333'
        self.OnBGColor = '#2F9F00'
        self.OnButtonColor = '#FFFFFF'
        self.OffButtonColor = '#FFFFFF'
        self.ButtonX = 0
        self.StopMove = False
        self.Canvas_width = 60
        self.Canvas_height = 20
        self.Canvas_radius = int(self.Canvas_height / 2)
        self.Canvas = tkinter.Canvas(self.ParentWidget,width=self.Canvas_width,height=self.Canvas_height,bg = self.BGColor,highlightthickness=0,bd=0)
        self.Canvas.create_oval(0, 0, self.Canvas_height, self.Canvas_height-1,fill=self.OffBGColor,width=0, tag='bg')
        self.Canvas.create_rectangle(self.Canvas_radius,0,(self.Canvas_width-self.Canvas_radius),self.Canvas_height,fill=self.OffBGColor,width=0, tag='bg')
        self.Canvas.create_oval((self.Canvas_width-self.Canvas_height), 0, self.Canvas_width, self.Canvas_height-1,fill=self.OffBGColor,width=0, tag='bg')
        self.Canvas.create_text(self.Canvas_height+2, 2, fill=self.OffTextColor,text=self.OffText,font = self.TextFont,anchor='nw',tag='text')
        self.Canvas.create_oval(2, 2, (self.Canvas_height-3), (self.Canvas_height-3),fill=self.OffButtonColor,width=0,tag='button')
        self.Canvas.bind("<ButtonRelease-1>",self.onSwitch)
        self.Canvas.bind('<Configure>',self.Configure)
        self.Canvas.place(x=0, y=0,width=40,height=20)
        self.SwitchCallBackFunction = None
        self.SwitchUIName = None
        self.SwitchName =  None
        self.HRGN = None
        self.State = True
    #设置形状
    def SetShape(self,shape):
        self.Shape = shape
    #取得形状
    def GetShape(self):
        return self.Shape
    #取得当前值
    def GetCurrValue(self):
        return self.CurrValue
    #设置当前值
    def SetCurrValue(self,value):
        if value == True:
            self.SwithOn()
        else:
            self.SwitchOff()
    #取得所属窗体
    def GetWidget(self):
        return self.Canvas
    #窗口大小变化
    def Configure(self,event):
        self.Canvas_width = event.width
        if self.Canvas_width == 1:
            uiName,ElementName = FunLib.GetElementName(self,False)
            if uiName in FunLib.G_UIElementPlaceDictionary:
                if ElementName in FunLib.G_UIElementPlaceDictionary[uiName]:
                    self.Canvas_width = FunLib.G_UIElementPlaceDictionary[uiName][ElementName]["relwidth"]
        if type(self.Canvas_width) == type(0.2):
            ParentWidth = self.ParentWidget.winfo_width()
            if ParentWidth == 1 and FunLib:
                uiName,ElementName = FunLib.GetElementName(self.ParentWidget,False)
                if uiName in FunLib.G_UIElementPlaceDictionary:
                    if ElementName == "Form_1":
                        ParentWidth = FunLib.G_UIRootSizeDictionary[uiName]['width']
                    elif ElementName in FunLib.G_UIElementPlaceDictionary[uiName]:
                        ParentWidth = FunLib.G_UIElementPlaceDictionary[uiName][ElementName]["relwidth"]
            self.Canvas_width = int(self.Canvas_width*ParentWidth)
        self.Canvas_height = event.height
        if self.Canvas_height == 1:
            uiName,ElementName = FunLib.GetElementName(self,False)
            if uiName in FunLib.G_UIElementPlaceDictionary:
                if ElementName in FunLib.G_UIElementPlaceDictionary[uiName]:
                    self.Canvas_height = FunLib.G_UIElementPlaceDictionary[uiName][ElementName]["relheight"]
        if type(self.Canvas_height) == type(0.2):
            ParentHeight = self.ParentWidget.winfo_height()
            if ParentHeight == 1 and FunLib:
                uiName,ElementName = FunLib.GetElementName(self.ParentWidget,False)
                if uiName in FunLib.G_UIElementPlaceDictionary:
                    if ElementName == "Form_1":
                        ParentHeight = FunLib.G_UIRootSizeDictionary[uiName]['height']
                    elif ElementName in FunLib.G_UIElementPlaceDictionary[uiName]:
                        ParentHeight = FunLib.G_UIElementPlaceDictionary[uiName][ElementName]["relheight"]
            self.Canvas_height = int(self.Canvas_height*ParentHeight)
        self.Canvas_radius = int(self.Canvas_height / 2)
        if self.Shape == 'circular' and self.HRGN is None:
            import win32gui
            if self.Canvas_width > 1 and self.Canvas_height > 1:
                self.HRGN = win32gui.CreateRoundRectRgn(0,0,self.Canvas_width,self.Canvas_height,self.Canvas_height,self.Canvas_height)
                win32gui.SetWindowRgn(self.Canvas.winfo_id(),self.HRGN,1)
        self.Redraw()
    #取得边框样式
    def Hide(self,layout="place"):
        if layout == "pack":
            self.Canvas.pack_forget()
        elif layout == "grid":
            self.Canvas.grid_forget()
        else:
            self.Canvas.place_forget()
    #传递绑定事件
    def bind(self,EventName,callBack):
        if self.Canvas:
            self.Canvas.bind(EventName,callBack)
    #传递pack_forget事件
    def pack_forget(self):
        if self.Canvas:
            self.Canvas.pack_forget()
    #传递grid_forget事件
    def grid_forget(self):
        if self.Canvas:
            self.Canvas.grid_forget()
    #传递place_forget事件
    def place_forget(self):
        if self.Canvas:
            self.Canvas.place_forget()
    #设置切换事件回调函数
    def SetSwitchCallBackFunction(self,callBack,uiName,widgetName):
        self.SwitchCallBackFunction = callBack 
        self.SwitchUIName = uiName
        self.SwitchName = widgetName
    #设置透明色
    def SetBGColor(self,color):
        self.BGColor = color
    #设置打开时背景色
    def SetOnStateBGColor(self,color):
        self.OnBGColor = color
        self.MoveTo(self.CurrValue)
    #设置OFF时背景色
    def SetOffStateBGColor(self,color):
        self.OffBGColor = color
        self.MoveTo(self.CurrValue)
    #设置打开时按钮色
    def SetOnStateButtonColor(self,color):
        self.OnButtonColor = color
        self.MoveTo(self.CurrValue)
    #设置关闭时按钮色
    def SetOffStateButtonColor(self,color):
        self.OffButtonColor = color
        self.MoveTo(self.CurrValue)
    #设置打开时显示文字
    def SetOnStateText(self,text):
        self.OnText = text
    #取得文字宽度
    def GetOnStateTextWidth(self):
        return self.TextFont.measure(self.OnText)
    #设置打开时文字颜色
    def SetOnStateTextColor(self,color='#FFFFFF'):
        self.OnTextColor = color
        self.MoveTo(self.CurrValue)
    #设置关闭时显示文字
    def SetOffStateText(self,text):
        self.OffText = text
        self.MoveTo(self.CurrValue)
    #取得文字宽度
    def GetOffStateTextWidth(self):
        return self.TextFont.measure(self.OffText)
    #设置关闭时文字颜色
    def SetOffStateTextColor(self,color='#FFFFFF'):
        self.OffTextColor = color
        self.MoveTo(self.CurrValue)
    #设置当前是否可用
    def SetState(self,state):
        self.State = state
    #取得是否可用
    def GetState(self):
        return self.State
    #设置文字字体
    def SetFont(self,font):
        self.TextFont = font
    #移动动画
    #mode:0:"immediate",1:"animation"
    #framedelay:帧切换的时间间隔
    def SetSwitchMode(self,mode=0,framedelay=1):
        self.SwitchMode = mode
        self.FrameDelay = framedelay
        self.StopMove = False
    def GetSwitchMode(self):
        return self.SwitchMode
    #切换开关
    def onSwitch(self,event):
        if self.State == True:
            if self.CurrValue == False:
                self.SwithOn()
                if self.SwitchCallBackFunction:
                    self.SwitchCallBackFunction(self.SwitchUIName,self.SwitchName,True)
            else:
                self.SwitchOff()
                if self.SwitchCallBackFunction:
                    self.SwitchCallBackFunction(self.SwitchUIName,self.SwitchName,False)
    #设置切换到打开
    def SwithOn(self):
        if self.CurrValue == False:
            self.CurrValue = True
            self.StopMove = False
            #如果是动画模式
            if self.SwitchMode == 1:
                self.Canvas.after(4, lambda: self.MoveTo(self.CurrValue))
            else:
                self.ButtonX = (self.Canvas_width-self.Canvas_height)
                self.MoveTo(self.CurrValue)
    #切换到关
    def SwitchOff(self):
        if self.CurrValue == True:
            self.CurrValue = False
            self.StopMove = False
            #如果是动画模式
            if self.SwitchMode == 1:
                self.Canvas.after(4, lambda: self.MoveTo(self.CurrValue))
            else:
                self.ButtonX = 2
                self.MoveTo(self.CurrValue)
    #动画
    def MoveTo(self,currValue):
        if self.StopMove == False:
            if currValue == True:
                self.Canvas.delete('bg')
                self.Canvas.delete('text')
                self.Canvas.delete('button')
                radius = int(self.Canvas_height/2)
                border = int(self.Canvas_height * 0.1)
                if border < 2:
                    border = 2
                if self.ButtonX <= (self.Canvas_width - self.Canvas_height):
                    self.ButtonX = self.ButtonX + 1
                if self.ButtonX >= (self.Canvas_width - self.Canvas_height):
                    self.ButtonX = (self.Canvas_width - self.Canvas_height)
                    self.StopMove = True
                if self.Shape == 'circular':
                    self.Canvas.create_oval(0, 0, self.Canvas_height, self.Canvas_height,fill=self.OnBGColor,width=0, tag='bg')
                    self.Canvas.create_rectangle(radius,0,self.Canvas_width-radius,self.Canvas_height+1,fill=self.OnBGColor,width=0, tag='bg')
                    self.Canvas.create_oval(self.Canvas_width-self.Canvas_height, 0, self.Canvas_width, self.Canvas_height,fill=self.OnBGColor,width=0, tag='bg')
                    self.Canvas.create_oval(self.ButtonX, border, self.ButtonX + (self.Canvas_height - border), self.Canvas_height - border,fill=self.OnButtonColor, tag='button')    
                    self.Canvas.create_text(self.ButtonX-border-self.GetOnStateTextWidth(), self.Canvas_radius, fill=self.OnTextColor,text=self.OnText,font = self.TextFont,anchor='w',tag='text')
                    self.Canvas.create_text(self.ButtonX+self.Canvas_height+border, self.Canvas_radius, fill=self.OffTextColor,text=self.OffText,font = self.TextFont,anchor='w',tag='text')
                else:
                    self.Canvas.create_rectangle(0,0,self.Canvas_width,self.Canvas_height,fill=self.OnBGColor,width=0, tag='bg')
                    self.Canvas.create_rectangle(self.ButtonX, border, self.ButtonX + (self.Canvas_height - border), self.Canvas_height - border,fill=self.OnButtonColor, tag='button')    
                    self.Canvas.create_text(self.ButtonX-border-self.GetOnStateTextWidth(), self.Canvas_radius, fill=self.OnTextColor,text=self.OnText,font = self.TextFont,anchor='w',tag='text')
                    self.Canvas.create_text(self.ButtonX+self.Canvas_height+border, self.Canvas_radius, fill=self.OffTextColor,text=self.OffText,font = self.TextFont,anchor='w',tag='text')
                if self.StopMove == False:
                    self.Canvas.after(self.FrameDelay, lambda: self.MoveTo(currValue))
                else:
                    self.Canvas.after_cancel(self.MoveTo)
            else:
                self.Canvas.delete('bg')
                self.Canvas.delete('text')
                self.Canvas.delete('button')
                radius = int(self.Canvas_height/2)
                border = int(self.Canvas_height * 0.1)
                if border < 2:
                    border = 2
                if self.ButtonX >= border:
                    self.ButtonX = self.ButtonX - 1
                if self.ButtonX < border:
                    self.ButtonX = border
                    self.StopMove = True
                if self.Shape == 'circular':
                    self.Canvas.create_oval(0, 0, self.Canvas_height, self.Canvas_height,fill=self.OffBGColor,width=0, tag='bg')
                    self.Canvas.create_rectangle(radius,0,self.Canvas_width-radius,self.Canvas_height+1,fill=self.OffBGColor,width=0, tag='bg')
                    self.Canvas.create_oval(self.Canvas_width-self.Canvas_height, 0, self.Canvas_width, self.Canvas_height,fill=self.OffBGColor,width=0, tag='bg')
                    self.Canvas.create_oval(self.ButtonX, border, self.ButtonX + (self.Canvas_height - border), self.Canvas_height - border,fill=self.OffButtonColor, tag='button')    
                    self.Canvas.create_text(self.ButtonX-border-self.GetOnStateTextWidth(), self.Canvas_radius, fill=self.OnTextColor,text=self.OnText,font = self.TextFont,anchor='w',tag='text')
                    self.Canvas.create_text(self.ButtonX+self.Canvas_height+border, self.Canvas_radius, fill=self.OffTextColor,text=self.OffText,font = self.TextFont,anchor='w',tag='text')
                else:
                    self.Canvas.create_rectangle(0,0,self.Canvas_width,self.Canvas_height,fill=self.OffBGColor,width=0, tag='bg')
                    self.Canvas.create_rectangle(self.ButtonX, border, self.ButtonX + (self.Canvas_height - border), self.Canvas_height - border,fill=self.OffButtonColor, tag='button')    
                    self.Canvas.create_text(self.ButtonX-border-self.GetOnStateTextWidth(), self.Canvas_radius, fill=self.OnTextColor,text=self.OnText,font = self.TextFont,anchor='w',tag='text')
                    self.Canvas.create_text(self.ButtonX+self.Canvas_height+border, self.Canvas_radius, fill=self.OffTextColor,text=self.OffText,font = self.TextFont,anchor='w',tag='text')
                if self.StopMove == False:
                    self.Canvas.after(self.FrameDelay, lambda: self.MoveTo(currValue))
                else:
                    self.Canvas.after_cancel(self.MoveTo)
    #重新绘制
    def Redraw(self):
        self.MoveTo(self.CurrValue)
#滑动条
class Slider:
    def __init__(self, widget):
        self.ParentWidget = widget
        self.MinValue = 0
        self.MaxValue = 100
        self.CurrValue = 50
        self.ValueChangeFunction = None
        self.BarBGColor1 = '#777777'
        self.BarBGColor2 = '#226699'
        self.BarButtonColor = '#22AAFF'
        self.BarImage1 = None
        self.BarImageFile1 = None
        self.BarImage1_Resize = None
        self.BarImage1_PT = None
        self.BarImage1Crop = None
        self.BarImage2 = None
        self.BarImageFile2 = None
        self.BarImage2_Resize = None
        self.BarImage2_PT = None
        self.BarImage2Crop = None
        self.ButtonImage= None
        self.ButtonImageFile = None
        self.ButtonImage_Resize = None
        self.ButtonImage_PT = None
        self.ButtonImage_Hover = None
        self.ButtonImageFile_Hover = None
        self.ButtonImage_PT_Hover = None
        self.ButtonImage_Click = None
        self.ButtonImageFile_Click = None
        self.ButtonImage_PT_Click = None
        self.TextFont = tkinter.font.Font(font='TkDefaultFont')
        self.TransparentColor = self.ParentWidget.cget('bg')
        self.Canvas_width = 400
        self.Canvas_height = 40
        self.SpaceY = 2
        self.Canvas = tkinter.Canvas(self.ParentWidget,width=self.Canvas_width,height=self.Canvas_height,bg = self.TransparentColor,highlightthickness=0,bd=0)
        self.Canvas.bind('<Configure>',self.Configure)
        self.Redraw()
    def GetWidget(self):
        return self.Canvas
    #窗口大小变化
    def Configure(self,event):
        self.Canvas_width = event.width
        self.Canvas_height = event.height
        self.Redraw()
    #取得边框样式
    def Hide(self,layout="place"):
        if layout == "pack":
            self.Canvas.pack_forget()
        elif layout == "grid":
            self.Canvas.grid_forget()
        else:
            self.Canvas.place_forget()
    #传递绑定事件
    def bind(self,EventName,callBack):
        if self.Canvas:
            self.Canvas.bind(EventName,callBack)
    #传递pack_forget事件
    def pack_forget(self):
        if self.Canvas:
            self.Canvas.pack_forget()
    #传递grid_forget事件
    def grid_forget(self):
        if self.Canvas:
            self.Canvas.grid_forget()
    #传递place_forget事件
    def place_forget(self):
        if self.Canvas:
            self.Canvas.place_forget()
    def Rebuild(self):
        self.Canvas_width = self.Canvas.winfo_width()
        self.Canvas_height =self.Canvas.winfo_height()
        self.Redraw()
    #设置最小值
    def SetMinValue(self,min,redraw = True):
        self.MinValue = min
        if redraw == True:
            self.Redraw()
    #取得最小值
    def GetMinValue(self):
        return self.MinValue
    #设置最大值
    def SetMaxValue(self,max,redraw = True):
        self.MaxValue = max
        if redraw == True:
            self.Redraw()
    #取得最大值
    def GetMaxValue(self):
        return self.MaxValue
    #设置当前值
    def SetCurrValue(self,value,redraw = True):
        self.CurrValue = value
        if redraw == True:
            self.Redraw()
    #取得当前值
    def GetCurrValue(self):
        return self.CurrValue
    #设置滑块右边的背景色
    def SetBarBGColor1(self,color):
        self.BarBGColor1 = color
        self.Canvas.itemconfig('bar_2',fill=color)
        self.Canvas.itemconfig('bar_2_bg',fill=color)
        self.Canvas.itemconfig('bar_2_oval',fill=color)
    #获取滑块右边背景色
    def GetBarBGColor1(self):
        return self.BarBGColor1
    #设置滑块左边的背景色
    def SetBarBGColor2(self,color):
        self.BarBGColor2 = color
        self.Canvas.itemconfig('bar_1',fill=color)
        self.Canvas.itemconfig('bar_1_bg',fill=color)
        self.Canvas.itemconfig('bar_1_oval',fill=color)
    #获取滑块左边背景色
    def GetBarBGColor2(self):
        return self.BarBGColor2
    #设置滑块颜色
    def SetBarButtonColor(self,color):
        self.BarButtonColor = color
        self.Canvas.itemconfig('button',fill=color)
    #获取滑块颜色
    def GetBarButtonColor(self):
        return self.BarButtonColor
    #设置滑动条左边的背景图
    def SetBarImage1(self,fileName,redraw = True):
        global G_ExeDir
        global G_ResDir
        self.BarImage1 = None
        filePath = fileName
        if filePath and os.path.exists(filePath) == False:
            filePath = os.path.join(G_ExeDir,fileName)
            if os.path.exists(filePath) == False:
                filePath = os.path.join(G_ResDir,fileName)
        if filePath and os.path.exists(filePath) == True:
            try:
                imagePath,imageFile = os.path.split(filePath)
                self.BarImage1 = Image.open(filePath).convert('RGBA')
                self.BarImageFile1 = imageFile
                self.BarImage1Crop = None
                self.BarImage1_Resize = self.BarImage1.resize((self.Bar_width, self.Bar_height),Image.LANCZOS)
                self.BarImage1_PT = ImageTk.PhotoImage(self.BarImage1_Resize)
            except:
                self.BarImage1 = None
        if redraw == True:
            self.Redraw()
    #取得滑滑动条左边的背景图
    def GetBarImage1(self):
        return self.BarImageFile1
    #设置滑动条右边的背景图
    def SetBarImage2(self,fileName,redraw = True):
        global G_ExeDir
        global G_ResDir
        self.BarImage2 = None
        filePath = fileName
        if filePath and os.path.exists(filePath) == False:
            filePath = os.path.join(G_ExeDir,fileName)
            if os.path.exists(filePath) == False:
                filePath = os.path.join(G_ResDir,fileName)
        if filePath and os.path.exists(filePath) == True:
            try:
                imagePath,imageFile = os.path.split(filePath)
                self.BarImage2 = Image.open(filePath).convert('RGBA')
                self.BarImageFile2 = imageFile
                self.BarImage2Crop = None
                self.BarImage2_Resize = self.BarImage2.resize((self.Bar_width, self.Bar_height),Image.LANCZOS)
                self.BarImage2_PT = ImageTk.PhotoImage(self.BarImage2_Resize)
            except:
                self.BarImage2 = None
        if redraw == True:
            self.Redraw()
    #取得滑动条右边的背景图
    def GetBarImage2(self):
        return self.BarImageFile2
    #设置滑块的背景图
    def SetButtonBGImage(self,fileName,redraw = True):
        global G_ExeDir
        global G_ResDir
        self.ButtonImage = None
        filePath = fileName
        if filePath and os.path.exists(filePath) == False:
            filePath = os.path.join(G_ExeDir,fileName)
            if os.path.exists(filePath) == False:
                filePath = os.path.join(G_ResDir,fileName)
        if filePath and os.path.exists(filePath) == True:
            try:
                imagePath,imageFile = os.path.split(filePath)
                self.ButtonImage = Image.open(filePath).convert('RGBA')
                self.ButtonImageFile = imageFile
                self.ButtonImage_Resize = self.ButtonImage.resize((2 * self.ButtonRadius, 2 * self.ButtonRadius),Image.LANCZOS)
                self.ButtonImage_PT = ImageTk.PhotoImage(self.ButtonImage_Resize)
            except:
                self.ButtonImage = None
        if redraw == True:
            self.Redraw()
    #取得滑块的背景图片文件
    def GetButtonBGImage(self):
        return self.ButtonImageFile
    #设置滑块在鼠标悬停状态的背景图
    def SetButtonBGImage_Hover(self,fileName):
        global G_ExeDir
        global G_ResDir
        self.ButtonImage_Hover = None
        filePath = fileName
        if filePath and os.path.exists(filePath) == False:
            filePath = os.path.join(G_ExeDir,fileName)
            if os.path.exists(filePath) == False:
                filePath = os.path.join(G_ResDir,fileName)
        if filePath and os.path.exists(filePath) == True:
            try:
                imagePath,imageFile = os.path.split(filePath)
                self.ButtonImage_Hover = Image.open(filePath).convert('RGBA')
                self.ButtonImageFile_Hover = imageFile
                self.ButtonImage_Resize_Hover = self.ButtonImage_Hover.resize((2 * self.ButtonRadius, 2 * self.ButtonRadius),Image.LANCZOS)
                self.ButtonImage_PT_Hover = ImageTk.PhotoImage(self.ButtonImage_Resize_Hover)
            except:
                self.ButtonImage_Hover = None
    #取得滑块在鼠标悬停状态的背景图片文件
    def GetButtonBGImage_Hover(self):
        return self.ButtonImageFile_Hover
    #设置滑块在按下状态的背景图
    def SetButtonBGImage_Click(self,fileName):
        global G_ExeDir
        global G_ResDir
        self.Image_Button_Click = None
        filePath = fileName
        if filePath and os.path.exists(filePath) == False:
            filePath = os.path.join(G_ExeDir,fileName)
            if os.path.exists(filePath) == False:
                filePath = os.path.join(G_ResDir,fileName)
        if filePath and os.path.exists(filePath) == True:
            try:
                imagePath,imageFile = os.path.split(filePath)
                self.ButtonImage_Click = Image.open(filePath).convert('RGBA')
                self.ButtonImageFile_Click = imageFile
                self.ButtonImage_Resize_Click = self.ButtonImage_Click.resize((2 * self.ButtonRadius, 2 * self.ButtonRadius),Image.LANCZOS)
                self.ButtonImage_PT_Click = ImageTk.PhotoImage(self.ButtonImage_Resize_Click)
            except:
                self.ButtonImage_Click = None
    #取得滑块在按下状态的背景图片文件
    def GetButtonBGImage_Click(self):
        return self.ButtonImageFile_Click
    #设置切换状态的回调函数
    def SetValueChangedFunction(self,callBackFunction,uiName,widgetName):
        self.ValueChangeFunction = callBackFunction
        self.uiName = uiName
        self.widgetName = widgetName
    #设置切换状态的回调函数，计划命名去掉CallBack，准备弃用。
    def SetValueChangeCallBackFunction(self,callBackFunction,uiName,widgetName):
        self.SetValueChangedFunction(callBackFunction,uiName,widgetName)
    #开始拖动
    def onBeginDraging(self,event):
        self.onDraging(event)
        #按钮图片
        if self.ButtonImage_PT_Click:
            self.Canvas.itemconfig("button",image=self.ButtonImage_PT_Click)
    #拖动中
    def onDraging(self,event):
        barWidth = (self.Canvas_width - 2 * self.Bar_height)
        Percent = (event.x - self.Bar_height) / barWidth
        if Percent < 0:
            Percent = 0
        if Percent > 1.0:
            Percent = 1.0
        self.CurrValue = self.MinValue + int(Percent * (self.MaxValue - self.MinValue))
        ButtonXInBar =  int(Percent * self.Bar_width )
        self.ButtonX = self.Bar_height + int((self.CurrValue - self.MinValue) / (self.MaxValue - self.MinValue) * barWidth)
        self.ButtonY = int(self.Canvas_height/2)
        #左边的图片
        if self.BarImage1:
            self.BarImage1Crop = self.BarImage1_Resize.crop((0, 0, ButtonXInBar, self.Bar_height))
            self.BarImage1_PT = ImageTk.PhotoImage(self.BarImage1Crop)
            self.Canvas.itemconfig("bar_1_img",image=self.BarImage1_PT)
            self.Canvas.coords('bar_1_img',(self.Bar_height,self.BarY))
        else:
            #左边的图形
            self.Canvas.coords('bar_1_bg',(self.Bar_height,self.BarY,self.ButtonX,self.BarY + self.Bar_height))
        #右边的图片
        if self.BarImage2:
            self.BarImage2Crop = self.BarImage2_Resize.crop((ButtonXInBar, 0, self.Bar_width, self.Bar_height))
            self.BarImage2_PT = ImageTk.PhotoImage(self.BarImage2Crop)
            self.Canvas.itemconfig("bar_2_img",image=self.BarImage2_PT)
            self.Canvas.coords('bar_2_img',(self.ButtonX,self.BarY))
        else:
            #右边的图形
            self.Canvas.coords('bar_2_bg',(self.ButtonX,self.BarY,(self.Canvas_width-self.Bar_height),self.BarY + self.Bar_height))
        #滑块
        self.Canvas.moveto('button',x=self.ButtonX-self.Bar_height,y=self.ButtonY - self.ButtonRadius)
        if self.ValueChangeFunction:
            self.ValueChangeFunction(self.uiName,self.widgetName,self.CurrValue)
    #结束拖动
    def onEndDraging(self,event):
        self.onDraging(event)
        #按钮图片
        if self.ButtonImage_PT_Hover:
            self.Canvas.itemconfig("button",image=self.ButtonImage_PT_Hover)
        elif self.ButtonImage_PT:
            self.Canvas.itemconfig("button",image=self.ButtonImage_PT)
    #鼠标进入按钮
    def onEnter(self,event):
        #按钮图片
        if self.ButtonImage_PT_Hover:
            self.Canvas.itemconfig("button",image=self.ButtonImage_PT_Hover)
    #鼠标离开按钮
    def onLeave(self,event):
        #按钮图片
        if self.ButtonImage_PT:
            self.Canvas.itemconfig("button",image=self.ButtonImage_PT)
    #重新绘制           
    def Redraw(self):
        self.TransparentColor = self.ParentWidget.cget('bg')
        self.Canvas.configure(bg = self.TransparentColor)
        self.Canvas.delete('bar_1_oval')
        self.Canvas.delete('bar_2_oval')
        self.Canvas.delete('bar_1_bg')
        self.Canvas.delete('bar_2_bg')
        self.Canvas.delete('bar_1_img')
        self.Canvas.delete('bar_2_img')
        self.Canvas.delete('text')
        self.Canvas.delete('button')
        self.Bar_height = int(self.Canvas_height / 2)
        self.ButtonRadius = (self.Bar_height - self.SpaceY)
        self.Canvas_radius = int((self.Bar_height - self.SpaceY) / 2)
        self.BarY = int((self.Canvas_height - self.Bar_height)/2)
        self.Bar_height = int(self.Canvas_height / 2)
        self.Bar_width = int(self.Canvas_width - 2 * self.Bar_height)
        Percent = (self.CurrValue - self.MinValue) / (self.MaxValue - self.MinValue)
        ButtonXInBar =  int( Percent * self.Bar_width )
        self.ButtonX = self.Bar_height + ButtonXInBar
        self.ButtonY = int(self.Canvas_height/2)
        #左边的图片
        if self.BarImage1:
            self.BarImage1_Resize = self.BarImage1.resize((self.Bar_width, self.Bar_height),Image.LANCZOS)
            self.BarImage1Crop = self.BarImage1_Resize.crop((0, 0, ButtonXInBar, self.Bar_height))
            self.BarImage1_PT = ImageTk.PhotoImage(self.BarImage1Crop)
            self.Canvas.create_image(self.Bar_height,self.BarY,anchor=tkinter.NW,image=self.BarImage1_PT,tag="bar_1_img")
        else:
            #左边图形
            self.Canvas.create_oval(self.Canvas_radius, self.BarY, self.Bar_height+self.Canvas_radius, self.BarY + self.Bar_height-1,fill=self.BarBGColor2,width=0, tag='bar_1_oval')
            self.Canvas.create_rectangle(self.Bar_height,self.BarY,self.ButtonX,self.BarY + self.Bar_height,fill=self.BarBGColor2,width=0, tag='bar_1_bg')
        #右边的图片
        if self.BarImage2:
            self.BarImage2_Resize = self.BarImage2.resize((self.Bar_width, self.Bar_height),Image.LANCZOS)
            self.BarImage2Crop = self.BarImage2_Resize.crop((ButtonXInBar, 0, self.Bar_width, self.Bar_height))
            self.BarImage2_PT = ImageTk.PhotoImage(self.BarImage2Crop)
            self.Canvas.create_image(self.ButtonX,self.BarY,anchor=tkinter.NW,image=self.BarImage2_PT,tag="bar_2_img")
        else:
            #右边图形
            self.Canvas.create_rectangle(self.ButtonX,self.BarY,(self.Canvas_width-self.Bar_height),self.BarY + self.Bar_height,fill=self.BarBGColor1,width=0, tag='bar_2_bg')
            self.Canvas.create_oval((self.Canvas_width-self.Bar_height-self.Canvas_radius), self.BarY, (self.Canvas_width-self.Canvas_radius),self.BarY + self.Bar_height-1,fill=self.BarBGColor1,width=0, tag='bar_2_oval')
        #滑块
        if self.ButtonImage:
            self.ButtonImage_Resize = self.ButtonImage.resize((2 * self.ButtonRadius, 2 * self.ButtonRadius),Image.LANCZOS)
            self.ButtonImage_PT = ImageTk.PhotoImage(self.ButtonImage_Resize)
            if self.ButtonImage_Hover:
                self.ButtonImage_Resize_Hover = self.ButtonImage_Hover.resize((2 * self.ButtonRadius, 2 * self.ButtonRadius),Image.LANCZOS)
                self.ButtonImage_PT_Hover = ImageTk.PhotoImage(self.ButtonImage_Resize_Hover)
            if self.ButtonImage_Click:
                self.ButtonImage_Resize_Click = self.ButtonImage_Click.resize((2 * self.ButtonRadius, 2 * self.ButtonRadius),Image.LANCZOS)
                self.ButtonImage_PT_Click = ImageTk.PhotoImage(self.ButtonImage_Resize_Click)
            self.Canvas.create_image(self.ButtonX-self.ButtonRadius,self.ButtonY - self.ButtonRadius,anchor=tkinter.NW,image=self.ButtonImage_PT,tag="button")
        else:
            self.Canvas.create_oval(self.ButtonX-self.ButtonRadius,self.ButtonY - self.ButtonRadius, self.ButtonX+self.ButtonRadius, self.ButtonY + self.ButtonRadius,fill=self.BarButtonColor,width=0,tag='button')
        self.Canvas.tag_bind('button','<Button-1>',self.onBeginDraging)
        self.Canvas.tag_bind('button','<B1-Motion>',self.onDraging)
        self.Canvas.tag_bind('button','<ButtonRelease-1>',self.onEndDraging)
        self.Canvas.tag_bind('button','<Enter>',self.onEnter)
        self.Canvas.tag_bind('button','<Leave>',self.onLeave)
#进度转盘
class ProgressDial:
    def __init__(self, canvas):
        self.ParentWidget = canvas
        self.CurrValue = 50
        self.MaxValue  = 100
        self.Sections = 100
        self.Canvas_BGColor = '#FFFFFF'
        self.BGColor = '#43536f'
        self.BGImage = None
        self.BGColor_Shader = '#111111'
        self.BGColor_Center = '#182a4a'
        self.BGImage_Center = None
        self.BGColor_Center_Shader = '#111111'
        self.Progress_Fill = '#cd7d45'
        self.FillWidth = 20
        self.Persentage = True
        self.BeginAngle = 0
        self.EndAngle = 360
        self.showScale = False
        self.LastAngle = 0
        self.LastSectionCount = 0
        self.Font=tkinter.font.Font(family="Arial", size=26,weight='bold',slant='roman',underline=0,overstrike=0)
        self.TextColor = '#cd7d45'
        self.Canvas = tkinter.Canvas(self.ParentWidget,width=200,height=200,bg = self.Canvas_BGColor,highlightthickness=0,bd=0)
        self.Canvas.place(x=0, y=0,width=200,height=200)
        self.Canvas.bind('<Configure>',self.Configure)
    def Configure(self,event):
        self.Rebuild()
    def GetWidget(self):
        return self.Canvas
    #取得边框样式
    def Hide(self,layout="place"):
        if layout == "pack":
            self.Canvas.pack_forget()
        elif layout == "grid":
            self.Canvas.grid_forget()
        else:
            self.Canvas.place_forget()
    #传递pack_forget事件
    def pack_forget(self):
        if self.Canvas:
            self.Canvas.pack_forget()
    #传递grid_forget事件
    def grid_forget(self):
        if self.Canvas:
            self.Canvas.grid_forget()
    #传递place_forget事件
    def place_forget(self):
        if self.Canvas:
            self.Canvas.place_forget()
    #传递绑定事件
    def bind(self,EventName,callBack):
        if self.Canvas:
            self.Canvas.bind(EventName,callBack)
    def SetBGColor(self,bgColor,redraw=True):
        self.BGColor  = bgColor
        if redraw == True:
            self.Redraw()
    def GetBGColor(self):
        return self.BGColor
    def SetBGColor_Center(self,bgColor,redraw=True):
        self.BGColor_Center  = bgColor
        self.Canvas.configure(bg = bgColor)
        if redraw == True:
            self.Redraw()
    def GetBGColor_Center(self):
        return self.BGColor_Center
    def SetFillColor(self,bgColor,redraw=True):
        self.Progress_Fill  = bgColor
        if redraw == True:
            self.Redraw()
    def GetFillColor(self):
        return self.Progress_Fill 
    def SetFillWidth(self,width,redraw=True):
        self.FillWidth = width
        if redraw == True:
            self.Redraw()
    def GetFillWidth(self):
        return self.FillWidth
    def SetAngleRange(self,beginAngle,endAngle,redraw=True):
        self.BeginAngle  = beginAngle
        self.EndAngle  = endAngle
        if redraw == True:
            self.Redraw()
    def SetBeginAngle(self,beginAngle,redraw=True):
        self.BeginAngle = beginAngle
        if redraw == True:
            self.Redraw()
    def GetBeginAngle(self):
        return self.BeginAngle
    def SetEndAngle(self,endAngle,redraw=True):
        self.EndAngle = endAngle
        if redraw == True:
            self.Redraw()
    def GetEndAngle(self):
        return self.EndAngle
    def SetMaxValue(self,max,redraw=True):
        self.MaxValue  = max
        if redraw == True:
            self.Redraw()
    def GetMaxValue(self):
        return self.MaxValue
    def SetCurrValue(self,value,redraw=True):
        self.CurrValue = value
        if redraw == True:
            self.Redraw()
    def GetCurrValue(self):
        return self.CurrValue
    def SetFont(self,font,redraw=True):
        self.Font = font
        if redraw == True:
            self.Redraw()
    def GetFont(self):
        return self.Font
    def SetTextColor(self,fgColor,redraw=True):
        self.TextColor = fgColor
        if redraw == True:
            self.Redraw()
    def GetTextColor(self):
        return self.TextColor
    def SetSections(self,section,redraw=True):
        self.Sections = section
        if redraw == True:
            self.Redraw()
    def GetSections(self):
        return self.Sections
    def SetPersentage(self,isPersentage = True,redraw=True):
        self.Persentage = isPersentage
        if redraw == True:
            self.Redraw()
    def IsPersentage(self):
        return self.Persentage
    def Rebuild(self):
        width = self.Canvas.winfo_width()
        height = self.Canvas.winfo_height()
        radius = height
        HRGN = win32gui.CreateRoundRectRgn(0,0,width,height,radius,radius)
        win32gui.SetWindowRgn(self.Canvas.winfo_id(), HRGN,1)
        CanvasWidth = self.Canvas.winfo_width()
        if CanvasWidth == 1: 
            CanvasWidth = 200
        CanvasHeight = self.Canvas.winfo_height()
        if CanvasHeight == 1: 
            CanvasHeight = 200
        AngleRange = self.EndAngle - self.BeginAngle
        self.Canvas.delete("all")
        CenterX = int(CanvasHeight / 2)
        CenterY = int(CanvasHeight / 2)
        #背景绘制
        if AngleRange == 360:
            #如果角度范围是360度
            #背景圆
            self.Canvas.create_oval(0,0,CanvasWidth,CanvasHeight, fill=self.BGColor,width=0,tag='oval_bg')
        else:
            #背景弧
            self.Canvas.create_arc(0,0,CanvasWidth,CanvasHeight,start= 90 - self.BeginAngle , extent = -AngleRange ,fill=self.BGColor,width=0,tag='oval_bg')
        #进度值
        Persent = self.CurrValue / self.MaxValue
        #如果是分段式
        if self.Sections > 1:
            showSectionCount = int(Persent * self.Sections)
            if float(Persent * self.Sections) > int(Persent * self.Sections):
                showSectionCount = showSectionCount + 1
            sectionAngle = 1 / self.Sections * 360
            for i in range(0,showSectionCount):
                srcAngle = int( i * sectionAngle )
                dstAngle = int( (i+1)  * sectionAngle ) - 1
                extentAngle = dstAngle - srcAngle + 1
                self.Canvas.create_arc(0,0,CanvasWidth,CanvasHeight,start = 90 - self.BeginAngle - srcAngle , extent = -extentAngle ,fill = self.Progress_Fill , outline=self.Progress_Fill,width=0 , tag='fill')
        else:
            extentAngle = int(AngleRange * Persent)
            self.Canvas.create_arc(0,0,CanvasWidth,CanvasHeight,start = 90 - self.BeginAngle,extent = -extentAngle ,fill=self.Progress_Fill,width=0,tag='fill')
        #圆心填充
        if AngleRange == 360:
            self.Canvas.create_oval(self.FillWidth,self.FillWidth,CanvasWidth - self.FillWidth ,CanvasHeight - self.FillWidth, fill=self.BGColor_Center_Shader,width=0,tag='oval_center_shadow')
            self.Canvas.create_oval(self.FillWidth + 2,self.FillWidth + 2,CanvasWidth - self.FillWidth - 2 ,CanvasHeight - self.FillWidth - 2, fill=self.BGColor_Center,width=0,tag='oval_center')
        else:
            self.Canvas.create_arc(self.FillWidth,self.FillWidth,CanvasWidth - self.FillWidth ,CanvasHeight - self.FillWidth,start = 90 - self.BeginAngle,extent = -AngleRange ,fill= self.BGColor_Center_Shader ,width = 0 , tag='arc_center_shadow')
            self.Canvas.create_oval(self.FillWidth + 2,self.FillWidth + 2,CanvasWidth - self.FillWidth - 2 ,CanvasHeight - self.FillWidth - 2, fill=self.BGColor_Center,width=0,tag='oval_center')
        #如果是百分比显示
        if self.Persentage == True:
            self.Canvas.create_text(CenterX,CenterY, font=self.Font,anchor=tkinter.CENTER,fill=self.TextColor,text=str("%d%%"%self.CurrValue),tag='value')
        else:
            self.Canvas.create_text(CenterX,CenterY, font=self.Font,anchor=tkinter.CENTER,fill=self.TextColor,text=str(self.CurrValue),tag='value')
    def Redraw(self):
        self.Rebuild()
#原类出处：https://blog.csdn.net/qq_40597070/article/details/131565185
class CustomNoteBook(tkinter.ttk.Notebook):
    """定义一个名为CustomNoteBook的类，继承自ttk.Notebook"""
    __initialized = False  
    def __init__(self, *args, **kwargs):
        self.StyleName = kwargs["style"]
        if not self.__initialized:
            self.__initialize_custom_style()
            CustomNoteBook.__initialized = True 
        tkinter.ttk.Notebook.__init__(self, *args, **kwargs)
        self._active = None 
        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)
    def on_close_press(self, event):
        """当按钮被按下时触发，位于关闭按钮上方"""
        element = self.identify(event.x, event.y)
        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index
    def on_close_release(self, event):
        if not self.instate(['pressed']):
            return
        try:
            element =  self.identify(event.x, event.y)
            index = self.index("@%d,%d" % (event.x, event.y))
            if "close" in element and self._active == index:
                if FunLib.AskBox("提示","是否确定关闭"+self.tab(index,"text")) == True:
                    self.forget(index)
                    self.event_generate("<<NotebookTabClosed>>") 
        except: pass
        self.state(["!pressed"])
        self._active = None 
    def __initialize_custom_style(self):
        style = tkinter.ttk.Style()
        self.images = (
            tkinter.PhotoImage("img_closenormal", data='''
                R0lGODdhCwALAIMAAJKSkpeXl5ubm5+fn6CgoKampqqqqq2trbGxsba2tr29vcHBwdnZ2QAAAAAAAAAA
                ACwAAAAACwALAAAIXQAXJEBwwEDBAgUGHEigYOCBhwYMEBCAIAEDBgYQXhwg4ACCiwwKgOQIEeRGjgUK
                GgBJYABKgyYZuBRAQORFmwwEBBhgE6FNAQAEDCBAtCVHoAcC6AzANAAAAAYCAgA7
                '''),
            tkinter.PhotoImage("img_closeselected", data='''
                R0lGODdhCwALAIVUAJ9dcptfe6NfcpthfZ5hfJ9ifp5nfaNjda9lc6Rmea1nfqRpe6Fqfq9ofK1ofqxr
                frFndbJqeLJufZ9rgKpngaBqgKtpg6tphK5uhKxvia5xhq91iq1xjK1zj692jLFyg7N1hrJ3i7B2jbF4
                ja51ka94kq97l698mq9+m7B8mbB/nLCDn6aEoayMprCForGMq7KNq7KPrrOXt7WfwP///wAAAAAAAAAA
                AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACwAAAAACwALAAAIcgBnwFiBwoQJEh0yUGARQ8YLFwRPHLwQ
                wEUMGjQOcsB4YYAKFxhpbMRooYCJFSlCYlTgoAAJFSlMhHTgQEGBDilSqoyggACGEiFFhGxwAINQGiNC
                gMAIQcADDR48bAjxQUIEBABaGJgwoQKDBQkOCGAREAA7
                '''),
            )
        style.element_create("close", "image", "img_closenormal",
                            ("selected", "img_closeselected"), 
                            border=10, sticky='')
        style.layout(self.StyleName, [(self.StyleName+".client", {"sticky": "nswe"})])
        style.layout(self.StyleName+".Tab", [
            (self.StyleName+".tab", { 
                "sticky": "nswe", 
                "children": [
                    (self.StyleName+".padding", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                            (self.StyleName+".focus", {
                                "side": "top",
                                "sticky": "nswe",
                                "children": [
                                    (self.StyleName+".label", {"side": "left", "sticky": ''}),
                                    (self.StyleName+".close", {"side": "left", "sticky": ''}),
                                ]
                            })
                        ]
                    })
                ]
            })
        ])
#导航栏
class Navigation:
    def __init__(self, canvas):
        self.ParentCanvas = canvas
        self.ItemArray = []
        self.CanvasBGColor = '#EFEFEF'
        self.ItemBGColor = '#EFEFEF'
        self.ItemFGColor = '#000000'
        self.ItemFont = tkinter.font.Font(family="Arial", size=10,weight='normal',slant='roman',underline=0,overstrike=0)
        self.ItemImage = None
        self.ItemPhotoImage = None
        self.ItemImageFile = None
        self.ItemBGColor_Hover = '#FFFFFF'
        self.ItemFGColor_Hover = '#000000'
        self.ItemFont_Hover = tkinter.font.Font(family="Arial", size=10,weight='normal',slant='roman',underline=0,overstrike=0)
        self.ItemImage_Hover = None
        self.ItemPhotoImage_Hover = None
        self.ItemImageFile_Hover = None
        self.ItemBGColor_Click = '#FFFFFF'
        self.ItemFGColor_Click = '#0000FF'
        self.ItemFont_Click = tkinter.font.Font(family="Arial", size=10,weight='bold',slant='roman',underline=0,overstrike=0)
        self.ItemImage_Click = None
        self.ItemPhotoImage_Click = None
        self.ItemImageFile_Click = None
        self.Direction = tkinter.HORIZONTAL
        self.Anchor = 'center'
        self.Compound = 'left'
        self.ItemWidth = 100
        self.ItemHeight = 24
        self.BorderWidth = 20
        self.BorderHeight = 20
        self.ItemSpacingX = 10
        self.ItemSpacingY = 10
        self.ItemInnerSpacingX = 4
        self.ItemInnerSpacingY = 4
        self.CurrentIndex = -1
        self.Canvas_width = 500
        self.Canvas_height = 40
        self.Canvas = tkinter.Canvas(self.ParentCanvas,width=self.Canvas_width,height=self.Canvas_height,bg = self.CanvasBGColor,highlightthickness=0,bd=0)
        self.Canvas.pack(side=tkinter.TOP,fill=tkinter.BOTH,expand=True)
        self.Canvas.bind('<Configure>',self.Configure)
        self.NavigationCallBackFunction = None
        self.NavigationUIName = None
        self.NavigationName =  None
    def Configure(self,event):
        self.Redraw()
    #取得所属窗体
    def GetWidget(self):
        return self.Canvas
    #设置属性
    def configure(self,**kw):
        self.Canvas.configure(kw)
    #传递绑定事件
    def bind(self,EventName,callBack):
        if self.Canvas:
            self.Canvas.bind(EventName,callBack)
    #取得边框样式
    def Hide(self,layout="place"):
        if layout == "pack":
            self.Canvas.pack_forget()
        elif layout == "grid":
            self.Canvas.grid_forget()
        else:
            self.Canvas.place_forget()
    #传递pack_forget事件
    def pack_forget(self):
        if self.Canvas:
            self.Canvas.pack_forget()
    #传递grid_forget事件
    def grid_forget(self):
        if self.Canvas:
            self.Canvas.grid_forget()
    #传递place_forget事件
    def place_forget(self):
        if self.Canvas:
            self.Canvas.place_forget()
    #设置切换事件回调函数
    def SetNavigationCallBackFunction(self,callBack,uiName,widgetName):
        self.NavigationCallBackFunction = callBack 
        self.NavigationUIName = uiName
        self.NavigationName = widgetName
    #取得对应Item的文本宽度
    def GetItemTextWidth(self,itemText):
        return self.ItemFont.measure(itemText) + 2 * self.ItemInnerSpacingX
    #取得对应Item的文本高度
    def GetItemTextHeight(self):
        fontHeight = int(self.ItemFont.actual('size'))
        fontHeight = int(fontHeight*SCALE_FACTOR)  + int(5 * SCALE_FACTOR)  + 2 * self.ItemInnerSpacingY
        return fontHeight
    #设置方向
    def SetDirection(self,direction = tkinter.VERTICAL,redraw = True):
        self.Direction = direction
        if redraw:
            self.Redraw()
    #取得方向
    def GetDirection(self):
        return self.Direction
    #设置对齐锚点
    def SetAnchor(self,anchor,redraw = True):
        self.Anchor = anchor
        if redraw:
            self.Redraw()
    #取得对齐锚点
    def GetAnchor(self):
        return self.Anchor
    #设置图标的位置
    def SetCompound(self,compound,redraw = True):
        self.Compound = compound
        if redraw:
            self.Redraw()
    #取得设置图标的位置
    def GetCompound(self):
        return self.Compound
    #设置边界宽度
    def SetBorderWidth(self,spacing,redraw = True):
        self.BorderWidth = spacing
        if redraw:
            self.Redraw()
    #取得边界宽度
    def GetBorderWidth(self):
        return self.BorderWidth
    #设置边界高度
    def SetBorderHeight(self,spacing,redraw = True):
        self.BorderHeight = spacing
        if redraw:
            self.Redraw()
    #取得边界高度
    def GetBorderHeight(self):
        return self.BorderHeight
    #设置选项的间跑
    def SetItemSpacing(self,spacing,redraw = True):
        self.ItemSpacingX = spacing
        self.ItemSpacingY = spacing
        if redraw:
            self.Redraw()
    #取得选项的间隔
    def GetItemSpacing(self):
        if self.Direction ==  tkinter.HORIZONTAL:
            return self.ItemSpacingX
        return self.ItemSpacingY
    #设置选项的间跑
    def SetItemInnerSpacing(self,spacing,redraw = True):
        self.ItemInnerSpacingX = spacing
        self.ItemInnerSpacingY = spacing
        if redraw:
            self.Redraw()
    #取得选项的间隔
    def GetItemInnerSpacing(self):
        if self.Direction ==  tkinter.HORIZONTAL:
            return self.ItemInnerSpacingX
        return self.ItemInnerSpacingY
    #设置当前选中项
    def SetCurrentIndex(self,Index):
        ButtonIndex = 0
        for ButtonInfo in self.ItemArray:
            ButtonImageList = ButtonInfo[-1]
            if ButtonIndex == Index:
                self.RedrawItem(ButtonIndex,"Click")
                self.CurrentIndex = ButtonIndex
                if self.NavigationCallBackFunction:
                    ButtonText = ButtonInfo[0]
                    TargetPage = ButtonInfo[2]
                    self.NavigationCallBackFunction(self.NavigationUIName,self.NavigationName,ButtonText,TargetPage)
            else:
                self.RedrawItem(ButtonIndex,"Normal")
            ButtonIndex = ButtonIndex + 1
    #取得当前选中项
    def GetCurrentIndex(self):
        return self.CurrentIndex
    #取得当前选中项文本
    def GetCurrentItemText(self):
        if self.CurrentIndex >= 0 and self.CurrentIndex < len(self.ItemArray):
           ButtonInfo = self.ItemArray[self.CurrentIndex]
           return ButtonInfo[0]
        return ""
    #取得当前选中项的值
    def GetCurrentItemValue(self):
        if self.CurrentIndex >= 0 and self.CurrentIndex < len(self.ItemArray):
           ButtonInfo = self.ItemArray[self.CurrentIndex]
           return ButtonInfo[2]
        return ""
    #鼠标进入和离开时的处理
    def onItemEnter(self,event):
        event.widget.configure(cursor='hand2')
        ButtonIndex = 0
        for ButtonInfo in self.ItemArray:
            if ButtonIndex != self.CurrentIndex:
                if ButtonInfo[3] == event.widget:
                    self.RedrawItem(ButtonIndex,"Hover")
            ButtonIndex = ButtonIndex + 1
    def onItemLeave(self,event):
        try:
            event.widget.configure(cursor='arrow')
            ButtonIndex = 0
            for ButtonInfo in self.ItemArray:
                if ButtonIndex != self.CurrentIndex:
                    if ButtonInfo[3] == event.widget:
                        self.RedrawItem(ButtonIndex,"Normal")
                ButtonIndex = ButtonIndex + 1
        except:
            pass
    def onItemClick(self,event):
        ButtonIndex = 0
        for ButtonInfo in self.ItemArray:
            ButtonImageList = ButtonInfo[-1]
            if ButtonInfo[3] == event.widget:
                self.RedrawItem(ButtonIndex,"Click")
                self.CurrentIndex = ButtonIndex
                if self.NavigationCallBackFunction:
                    ButtonText = ButtonInfo[0]
                    TargetPage = ButtonInfo[2]
                    self.NavigationCallBackFunction(self.NavigationUIName,self.NavigationName,ButtonText,TargetPage)
            else:
                self.RedrawItem(ButtonIndex,"Normal")
            ButtonIndex = ButtonIndex + 1
    #取得菜单数据数组
    def GetItemArray(self):
        return self.ItemArray
    #取得菜单数据数组的复制
    def GetItemArray_Copy(self):
        ItemArray = []
        for ButtonInfo in self.ItemArray:
            ItemArray.append([ButtonInfo[0],ButtonInfo[1],ButtonInfo[2],ButtonInfo[3],ButtonInfo[4],ButtonInfo[5]])
        return ItemArray
    #清空所有
    def Clear(self):
        for ButtonInfo in self.ItemArray:
            LabelButton = ButtonInfo[3]
            if LabelButton:
                LabelButton.destroy()
        self.ItemArray.clear()
        self.CurrentIndex = -1
    #设置当前画布的背景色
    def SetBGColor(self,color):
        self.CanvasBGColor = color
        self.Canvas.configure(bg = color)
    #取得当前画布的背景色
    def GetBGColor(self):
        return self.CanvasBGColor
    #设置标题栏的背景色
    def SetItemBGColor(self,color):
        self.ItemBGColor = color
        for ItemInfo in self.ItemArray:
            ItemButton = ItemInfo[3]
            ItemButton.configure(bg = color)
    #取得标题栏的背景色
    def GetItemBGColor(self):
        return self.ItemBGColor
    #设置鼠标悬停在标题栏上的背景色
    def SetItemBGColor_Hover(self,color):
        self.ItemBGColor_Hover = color
    #取得鼠标悬停在标题栏上的背景色
    def GetItemBGColor_Hover(self):
        return self.ItemBGColor_Hover
    #设置鼠点击击标题栏时的背景色
    def SetItemBGColor_Click(self,color):
        self.ItemBGColor_Click = color
        if self.CurrentIndex >= 0 and self.CurrentIndex < len(self.ItemArray):
            ItemInfo = self.ItemArray[self.CurrentIndex]
            ItemButton = ItemInfo[3]
            ItemButton.configure(bg = color)
    #取得鼠点击击标题栏时的背景色
    def GetItemBGColor_Click(self):
        return self.ItemBGColor_Click
    #设置标题栏的文字色
    def SetItemFGColor(self,color,redraw = True):
        self.ItemFGColor = color
        if redraw:
            self.Redraw()
    #取得标题栏的文字色
    def GetItemFGColor(self):
        return self.ItemFGColor
    #设置鼠标悬停在标题栏上的背景色
    def SetItemFGColor_Hover(self,color):
        self.ItemFGColor_Hover = color
    #取得鼠标悬停在标题栏上的背景色
    def GetItemFGColor_Hover(self):
        return self.ItemFGColor_Hover
    #设置鼠点击击标题栏时的背景色
    def SetItemFGColor_Click(self,color):
        self.ItemFGColor_Click = color
        if self.CurrentIndex >= 0 and self.CurrentIndex < len(self.ItemArray):
            ItemInfo = self.ItemArray[self.CurrentIndex]
            ItemButton = ItemInfo[3]
            ItemButton.configure(fg = color)
    #取得鼠点击击标题栏时的背景色
    def GetItemFGColor_Click(self):
        return self.ItemFGColor_Click
    #设置标题栏的字体
    def SetItemFont(self,font,redraw = True):
        self.ItemFont = font
        fontHeight = int(self.ItemFont.actual('size'))
        fontHeight = int(fontHeight*SCALE_FACTOR)  + int(5 * SCALE_FACTOR) 
        if fontHeight > self.ItemHeight:
            self.ItemHeight = fontHeight 
        if redraw:
            self.Redraw()
    #取得标题栏的字体
    def GetItemFont(self):
        return self.ItemFont
    #设置鼠标悬停在标题栏上的字体
    def SetItemFont_Hover(self,font):
        self.ItemFont_Hover = font
        fontHeight = int(self.ItemFont_Hover.actual('size'))
        fontHeight = int(fontHeight*SCALE_FACTOR)  + int(5 * SCALE_FACTOR) 
        if fontHeight > self.ItemHeight:
            self.ItemHeight = fontHeight 
    #取得鼠标悬停在标题栏上的字体
    def GetItemFont_Hover(self):
        return self.ItemFont_Hover
    #设置鼠点击击标题栏时的字体
    def SetItemFont_Click(self,font):
        self.ItemFont_Click = font
        fontHeight = int(self.ItemFont_Click.actual('size'))
        fontHeight = int(fontHeight*SCALE_FACTOR)  + int(5 * SCALE_FACTOR) 
        if fontHeight > self.ItemHeight:
            self.ItemHeight = fontHeight 
    #取得鼠标悬停在标题栏上的字体
    def GetItemFont_Click(self):
        return self.ItemFont_Click
    #设置标题栏的字体
    def SetItemImage(self,fileName):
        global G_ExeDir
        global G_ResDir
        self.ItemImage = None
        self.ItemPhotoImage = None
        self.ItemImageFile = None
        filePath = fileName
        if fileName:
            if filePath and os.path.exists(filePath) == False:
                filePath = "Resources\\" + fileName
                if os.path.exists(filePath) == False:
                    filePath = os.path.join(G_ExeDir,fileName)
                    if os.path.exists(filePath) == False:
                        filePath = os.path.join(G_ResDir,fileName)
            if os.path.exists(filePath) == True:
                imagePath,imageFile = os.path.split(filePath)
                try:
                    self.ItemImage = Image.open(filePath).convert('RGBA')
                    ItemWidth = self.ItemWidth + 2 * self.ItemInnerSpacingX
                    ItemHeight = self.ItemHeight + 2 * self.ItemInnerSpacingY
                    Image_Resize = self.ItemImage.resize((ItemWidth, ItemHeight),Image.LANCZOS)
                    self.ItemPhotoImage = ImageTk.PhotoImage(Image_Resize)
                    self.ItemImageFile = imageFile
                    ItemIndex = 0
                    for ItemInfo in self.ItemArray:
                        ItemText = ItemInfo[0]
                        ItemButton = ItemInfo[3]
                        ItemImageList = ItemInfo[-1]
                        buttonW = self.GetItemWidth(ItemIndex)
                        buttonH = self.GetItemHeight(ItemIndex)
                        if buttonW != ItemWidth or buttonH != ItemHeight:
                            Image_Resize = self.ItemImage.resize((buttonW, buttonH),Image.LANCZOS)
                            ItemImageList[0] = ImageTk.PhotoImage(Image_Resize)
                            if self.CurrentIndex != ItemIndex:
                                self.RedrawItem(ItemIndex,"Normal")
                        else:
                            if self.CurrentIndex != ItemIndex:
                                self.RedrawItem(ItemIndex,"Normal")
                        ItemIndex = ItemIndex + 1
                except:
                    self.ItemImage = None
                    self.ItemPhotoImage = None
                    self.ItemImageFile = None
        else:
            for ItemInfo in self.ItemArray:
                ItemButton = ItemInfo[3]
                ItemImageList = ItemInfo[-1]
                ItemImageList[0] = None 
                ItemButton.delete('bgimg')
    #取得标题栏的图片
    def GetItemImage(self):
        return self.ItemImageFile
    #设置标题栏的字体
    def SetItemImage_Hover(self,fileName):
        global G_ExeDir
        global G_ResDir
        self.ItemImage_Hover = None
        self.ItemPhotoImage_Hover = None
        self.ItemImageFile_Hover = None
        filePath = fileName
        if fileName:
            if filePath and os.path.exists(filePath) == False:
                filePath = "Resources\\" + fileName
                if os.path.exists(filePath) == False:
                    filePath = os.path.join(G_ExeDir,fileName)
                    if os.path.exists(filePath) == False:
                        filePath = os.path.join(G_ResDir,fileName)
            if os.path.exists(filePath) == True:
                imagePath,imageFile = os.path.split(filePath)
                try:
                    self.ItemImage_Hover = Image.open(filePath).convert('RGBA')
                    ItemWidth = self.ItemWidth + 2 * self.ItemInnerSpacingX
                    ItemHeight = self.ItemHeight + 2 * self.ItemInnerSpacingY
                    Image_Resize = self.ItemImage_Hover.resize((ItemWidth, ItemHeight),Image.LANCZOS)
                    self.ItemPhotoImage_Hover = ImageTk.PhotoImage(Image_Resize)
                    self.ItemImageFile_Hover = imageFile
                    ItemIndex = 0
                    for ItemInfo in self.ItemArray:
                        ItemText = ItemInfo[0]
                        ItemButton = ItemInfo[3]
                        ItemImageList = ItemInfo[-1]
                        buttonW = self.GetItemWidth(ItemIndex)
                        buttonH = self.GetItemHeight(ItemIndex)
                        if buttonW != ItemWidth or buttonH != ItemHeight:
                            Image_Resize = self.ItemImage_Hover.resize((buttonW, buttonH),Image.LANCZOS)
                            ItemImageList[1] = ImageTk.PhotoImage(Image_Resize)
                        ItemIndex = ItemIndex + 1
                except:
                    self.ItemImage_Hover = None
                    self.ItemPhotoImage_Hover = None
                    self.ItemImageFile_Hover = None
        else:
            for ItemInfo in self.ItemArray:
                ItemImageList = ItemInfo[-1]
                ItemImageList[1] = None 
    #取得标题栏的图片
    def GetItemImage_Hover(self):
        return self.ItemImageFile_Hover
    #设置标题栏的字体
    def SetItemImage_Click(self,fileName):
        global G_ExeDir
        global G_ResDir
        self.ItemImage_Click = None
        self.ItemPhotoImage_Click = None
        self.ItemImageFile_Click = None
        filePath = fileName
        if fileName:
            if filePath and os.path.exists(filePath) == False:
                filePath = "Resources\\" + fileName
                if os.path.exists(filePath) == False:
                    filePath = os.path.join(G_ExeDir,fileName)
                    if os.path.exists(filePath) == False:
                        filePath = os.path.join(G_ResDir,fileName)
            if os.path.exists(filePath) == True:
                imagePath,imageFile = os.path.split(filePath)
                try:
                    self.ItemImage_Click = Image.open(filePath).convert('RGBA')
                    ItemWidth = self.ItemWidth + 2 * self.ItemInnerSpacingX
                    ItemHeight = self.ItemHeight + 2 * self.ItemInnerSpacingY
                    Image_Resize = self.ItemImage_Click.resize((ItemWidth, ItemHeight),Image.LANCZOS)
                    self.ItemPhotoImage_Click = ImageTk.PhotoImage(Image_Resize)
                    self.ItemImageFile_Click = imageFile
                    ItemIndex = 0
                    for ItemInfo in self.ItemArray:
                        ItemText = ItemInfo[0]
                        ItemButton = ItemInfo[3]
                        ItemImageList = ItemInfo[-1]
                        buttonW = self.GetItemWidth(ItemIndex)
                        buttonH = self.GetItemHeight(ItemIndex)
                        if buttonW != ItemWidth or buttonH != ItemHeight:
                            Image_Resize = self.ItemImage_Click.resize((buttonW, buttonH),Image.LANCZOS)
                            ItemImageList[2] = ImageTk.PhotoImage(Image_Resize)
                        ItemIndex = ItemIndex + 1
                    if self.CurrentIndex >= 0 and self.CurrentIndex < len(self.ItemArray):
                        self.RedrawItem(self.CurrentIndex,"Click")
                except:
                    self.ItemImage_Click = None
                    self.ItemPhotoImage_Click = None
                    self.ItemImageFile_Click = None
        else:
            for ItemInfo in self.ItemArray:
                ItemImageList = ItemInfo[-1]
                ItemImageList[2] = None 
    #取得标题栏的图片
    def GetItemImage_Click(self):
        return self.ItemImageFile_Click
    #设置标题的间隔
    def SetItemXSpacing(self,spacing):
        self.ItemSpacingX = spacing
    #取得标题的间隔
    def GetItemXSpacing(self):
        return self.ItemSpacingX
    #取得当前标题的宽度
    def GetItemWidth(self,ItemIndex):
        if ItemIndex < len(self.ItemArray):
            ButtonInfo = self.ItemArray[ItemIndex]
            ItemImageList = ButtonInfo[-1]
            ItemText = ButtonInfo[0]
            ItemWidth = self.ItemWidth + 2 * self.ItemInnerSpacingX
            ItemTextW = self.GetItemTextWidth(ItemText)
            RealButtonWidth = ItemTextW
            if ItemImageList[3]:
                ItemIconWidth = ItemImageList[3].width()
                if self.Compound == 'left' or self.Compound == 'right':
                    RealButtonWidth = ItemTextW + ItemIconWidth + self.ItemInnerSpacingX
                else:
                    if  RealButtonWidth < ItemIconWidth:
                        RealButtonWidth = ItemIconWidth
            if ItemWidth < RealButtonWidth:
                ItemWidth = RealButtonWidth
            return ItemWidth
        return self.ItemWidth
    #取得当前标题的高度
    def GetItemHeight(self,ItemIndex):
        if ItemIndex < len(self.ItemArray):
            ButtonInfo = self.ItemArray[ItemIndex]
            ItemImageList = ButtonInfo[-1]
            ItemText = ButtonInfo[0]
            ItemHeight = self.ItemHeight + 2 * self.ItemInnerSpacingY
            ItemTextH = self.GetItemTextHeight()
            RealButtonHeight = ItemTextH
            if ItemImageList[3]:
                ItemIconHeight = ItemImageList[3].height()
                if self.Compound == 'top' or self.Compound == 'bottom':
                    RealButtonHeight = ItemTextH + ItemIconHeight + self.ItemInnerSpacingY
                else:
                    if  RealButtonHeight < ItemIconHeight:
                        RealButtonHeight = ItemIconHeight
            if ItemHeight < RealButtonHeight:
                ItemHeight = RealButtonHeight
            return ItemHeight
        return self.ItemHeight
    #计算当前标题的长度
    def GetAllItemWidth(self):
        AllItemWidth = self.ItemSpacingX
        ButtonIndex = 0
        for ButtonInfo in self.ItemArray:
            ItemWidth = self.GetItemWidth(ButtonIndex)
            AllItemWidth = AllItemWidth + (self.ItemSpacingX + ItemWidth)
            ButtonIndex = ButtonIndex + 1
        return AllItemWidth
    #计算当前标题的高度
    def GetAllItemHeight(self):
        AllItemHeight = self.ItemSpacingY
        ButtonIndex = 0
        for ButtonInfo in self.ItemArray:
            ItemHeight = self.GetItemHeight(ButtonIndex)
            AllItemHeight = AllItemHeight + (self.ItemSpacingY + ItemHeight)
            ButtonIndex = ButtonIndex + 1
        return AllItemHeight
    #计算当前标题的X值
    def GetItemLeftX(self,ItemIndex):
        canvasW = self.Canvas.winfo_width()
        canvasH = self.Canvas.winfo_height()
        if canvasW == 1 and canvasH == 1:
            canvasW = 650
            canvasH = 40
        AllItemWidth = self.GetAllItemWidth()
        #先算出总的起点X
        ButtonLeftX = 0
        if self.Anchor == 'nw' or self.Anchor == 'w' or self.Anchor == 'sw':
            ButtonLeftX = self.BorderWidth
        elif self.Anchor == 'n' or self.Anchor == 'center' or self.Anchor == 's':
            if self.Direction == tkinter.HORIZONTAL:
                ButtonLeftX =  (canvasW - AllItemWidth)/2
            else:
                RealItemWidth = self.GetItemWidth(ItemIndex)
                ButtonLeftX = (canvasW - RealItemWidth)/2
        else:
            if self.Direction == tkinter.HORIZONTAL:
                ButtonLeftX = canvasW - AllItemWidth - self.BorderWidth
            else:
                RealItemWidth = self.GetItemWidth(ItemIndex)
                ButtonLeftX = canvasW - self.BorderWidth - self.ItemSpacingX - RealItemWidth
        #循环算出索引位置X
        if self.Direction == tkinter.HORIZONTAL:
            ButtonIndex = 0
            for ButtonInfo in self.ItemArray:
                if ItemIndex == ButtonIndex:
                    break
                RealItemWidth = self.GetItemWidth(ButtonIndex)
                ButtonLeftX = ButtonLeftX + (self.ItemSpacingX + RealItemWidth)
                ButtonIndex = ButtonIndex + 1
        return ButtonLeftX
    #计算当前标题的Y值
    def GetItemTopY(self,ItemIndex):
        canvasW = self.Canvas.winfo_width()
        canvasH = self.Canvas.winfo_height()
        if canvasW == 1 and canvasH == 1:
            canvasW = 650
            canvasH = 40
        AllItemHeight = self.GetAllItemHeight()
        #先算出总的起点y
        ButtonTopY = 0
        if self.Anchor == 'nw' or self.Anchor == 'n' or self.Anchor == 'ne':
            ButtonTopY = self.BorderHeight
        elif self.Anchor == 'w' or self.Anchor == 'center' or self.Anchor == 'e':
            if self.Direction == tkinter.HORIZONTAL:
                RealItemHeight = self.GetItemHeight(ItemIndex)
                ButtonTopY = (canvasH - RealItemHeight)/2
            else:
                ButtonTopY = (canvasH - AllItemHeight)/2
        else:
            if self.Direction == tkinter.HORIZONTAL:
                RealItemHeight = self.GetItemHeight(ItemIndex)
                ButtonTopY = canvasW - self.BorderHeight - self.ItemSpacingY - RealItemHeight
            else:
                ButtonTopY = canvasH - AllItemHeight - self.BorderHeight
        #循环算出索引位置X
        if self.Direction == tkinter.VERTICAL:
            ButtonIndex = 0
            for ButtonInfo in self.ItemArray:
                if ItemIndex == ButtonIndex:
                    break
                RealItemHeight = self.GetItemHeight(ButtonIndex)
                ButtonTopY = ButtonTopY + (self.ItemSpacingY + RealItemHeight)
                ButtonIndex = ButtonIndex + 1
        return ButtonTopY
    #增加标题
    def AddItem(self,ItemText='',ItemIcon='',ItemPage='',ItemIndex='end'):
        ButtonIndex = len(self.ItemArray)
        ItemPhotoImage = self.ItemPhotoImage
        ItemPhotoImage_Hover = self.ItemPhotoImage_Hover
        ItemPhotoImage_Click = self.ItemPhotoImage_Click
        ItemWidth = self.ItemWidth + 2 * self.ItemInnerSpacingX
        ItemHeight = self.ItemHeight + 2 * self.ItemInnerSpacingY
        ItemTextW = self.GetItemTextWidth(ItemText)
        ItemTextH = self.GetItemTextHeight()
        ItemIconWidth = 0
        ItemIconHeight = 0
        ItemPTIconImage = None
        if ItemIcon:
            filePath = ItemIcon
            if filePath and os.path.exists(filePath) == False:
                filePath = os.path.join(G_ExeDir,ItemIcon)
                if os.path.exists(filePath) == False:
                    filePath = os.path.join(G_ResDir,ItemIcon)
            if filePath and os.path.exists(filePath) == True:
                try:
                    Image_Temp = Image.open(filePath).convert('RGBA')
                    ItemPTIconImage = ImageTk.PhotoImage(Image_Temp)
                    ItemIconWidth = Image_Temp.width + self.ItemInnerSpacingX
                    ItemIconHeight = Image_Temp.height + self.ItemInnerSpacingY
                except:
                    ItemPTIconImage = None
        RealButtonWidth = ItemTextW 
        if self.Compound == 'left' or self.Compound == 'right':
            RealButtonWidth = ItemTextW + ItemIconWidth
        else:
            if  RealButtonWidth < ItemIconWidth:
                RealButtonWidth = ItemIconWidth
        RealButtonHeight = ItemTextH 
        if self.Compound == 'top' or self.Compound == 'bottom':
            RealButtonHeight = ItemTextH + ItemIconHeight
        else:
            if  RealButtonHeight < ItemIconHeight:
                RealButtonHeight = ItemIconHeight
        if ItemWidth < RealButtonWidth:
            ItemWidth = RealButtonWidth
        if ItemHeight < RealButtonHeight:
            ItemHeight = RealButtonHeight
        if self.ItemImage:
            Image_Resize = self.ItemImage.resize((ItemWidth, ItemHeight),Image.LANCZOS)
            ItemPhotoImage = ImageTk.PhotoImage(Image_Resize)
        if self.ItemImage_Hover:
            Image_Resize = self.ItemImage_Hover.resize((ItemWidth, ItemHeight),Image.LANCZOS)
            ItemPhotoImage_Hover = ImageTk.PhotoImage(Image_Resize)
        if self.ItemImage_Click:
            Image_Resize = self.ItemImage_Click.resize((ItemWidth, ItemHeight),Image.LANCZOS)
            ItemPhotoImage_Click = ImageTk.PhotoImage(Image_Resize)
        buttonX = self.GetItemLeftX(ButtonIndex)
        buttonY = self.GetItemTopY(ButtonIndex)
        newLabelButton = tkinter.Canvas(self.Canvas,relief=tkinter.FLAT,bg = self.ItemBGColor,highlightthickness=0,bd=0)
        newLabelButton.place(x = buttonX,y = buttonY,width = ItemWidth ,height = ItemHeight) 
        newLabelButton.bind('<Enter>',self.onItemEnter)
        newLabelButton.bind('<Leave>',self.onItemLeave)
        newLabelButton.bind('<Button-1>',self.onItemClick)
        newLabelButton.bind('<ButtonRelease-1>',self.onItemEnter)
        #背景图
        if ItemPhotoImage:
            newLabelButton.create_image(0,0,anchor=tkinter.NW,image=ItemPhotoImage,tag="bgimg")
        centerX = int(ItemWidth/2)
        centerY = int(ItemHeight/2)
        #图标
        if ItemPTIconImage:
            if self.Compound == 'left':
                x = self.ItemInnerSpacingX
                newLabelButton.create_image(self.ItemInnerSpacingX ,centerY,anchor=tkinter.W,image=ItemPTIconImage,tag="icon")
                x = x + ItemIconWidth
                newLabelButton.create_text(x,centerY, font=self.ItemFont,anchor=tkinter.W,fill=self.ItemFGColor,text=ItemText,tag='title') 
            elif self.Compound == 'right':
                x = ItemWidth - ItemIconWidth
                newLabelButton.create_image(x,centerY,anchor=tkinter.W,image=ItemPTIconImage,tag="icon")
                x = x - ItemTextW + self.ItemInnerSpacingX
                newLabelButton.create_text(x,centerY, font=self.ItemFont,anchor=tkinter.W,fill=self.ItemFGColor,text=ItemText,tag='title') 
            elif self.Compound == 'top':
                y = self.ItemInnerSpacingY
                newLabelButton.create_image(centerX,y,anchor=tkinter.N,image=ItemPTIconImage,tag="icon")
                y = y + ItemIconHeight
                newLabelButton.create_text(centerX,y, font=self.ItemFont,anchor=tkinter.N,fill=self.ItemFGColor,text=ItemText,tag='title') 
            elif self.Compound == 'bottom':
                y =  ItemHeight - ItemIconHeight
                newLabelButton.create_image(centerX,y ,anchor=tkinter.N,image=ItemPTIconImage,tag="icon")
                y = y - ItemTextH + self.ItemInnerSpacingY
                newLabelButton.create_text(centerX,y, font=self.ItemFont,anchor=tkinter.N,fill=self.ItemFGColor,text=ItemText,tag='title') 
            elif self.Compound == 'center':
                newLabelButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=ItemPTIconImage,tag="icon")
                newLabelButton.create_text(centerX,centerY, font=self.ItemFont,anchor=tkinter.CENTER,fill=self.ItemFGColor,text=ItemText,tag='title') 
            else:
                newLabelButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=ItemPTIconImage,tag="icon")
        #文字
        buttonHandle = self.Canvas.create_window(buttonX,buttonY, window=newLabelButton, anchor=tkinter.NW,tag="Item")
        self.Canvas.itemconfig(buttonHandle,width=ItemWidth,height=ItemHeight)
        if ItemIndex == "end" or  ItemIndex == -1:
            self.ItemArray.append([ItemText,ItemIcon,ItemPage,newLabelButton,buttonHandle,[ItemPhotoImage,ItemPhotoImage_Hover,ItemPhotoImage_Click,ItemPTIconImage]])
        else:
            if type(ItemIndex) == type(""):
                if ItemIndex.isdigit() == True:
                    ItemIndex = int(ItemIndex)
                else:
                    ItemIndex = len(self.ItemArray)
            self.ItemArray.insert(ItemIndex,[ItemText,ItemIcon,ItemPage,newLabelButton,buttonHandle,[ItemPhotoImage,ItemPhotoImage_Hover,ItemPhotoImage_Click,ItemPTIconImage]])
    #删除标题
    def DelItem(self,index):
        if index < len(self.ItemArray):
            ButtonInfo = self.ItemArray[index]
            LabelButton = ButtonInfo[3]
            if LabelButton:
                LabelButton.destroy()
            self.ItemArray.pop(index)
        self.Redraw()
    #重建
    def Rebuild(self):
        OldItemArray = self.GetItemArray_Copy()
        self.Clear()
        if self.ItemImageFile:
            self.SetItemImage(self.ItemImageFile)
        if self.ItemImageFile_Hover:
            self.SetItemImage_Hover(self.ItemImageFile_Hover)
        if self.ItemImageFile_Click:
            self.SetItemImage_Click(self.ItemImageFile_Click)
        for ItemInfo in OldItemArray:
            self.AddItem(ItemText=ItemInfo[0],ItemIcon=ItemInfo[1],ItemPage=ItemInfo[2])
        self.Redraw()
    #绘制一个按钮
    def RedrawItem(self,ItemIndex,ItemState='Normal'):
        if ItemIndex >= 0 and ItemIndex < len(self.ItemArray):
            ButtonInfo = self.ItemArray[ItemIndex]
            ItemText = ButtonInfo[0]
            ItemImageList = ButtonInfo[-1]
            ItemPTIconImage = ItemImageList[3]
            newLabelButton = ButtonInfo[3]
            ItemWidth = self.ItemWidth + 2 * self.ItemInnerSpacingX
            ItemHeight = self.ItemHeight + 2 * self.ItemInnerSpacingY
            ItemTextW = self.GetItemTextWidth(ItemText)
            ItemTextH = self.GetItemTextHeight()
            ItemIconWidth = 0
            ItemIconHeight = 0
            if ItemPTIconImage:                
                ItemIconWidth = ItemPTIconImage.width() + self.ItemInnerSpacingX
                ItemIconHeight = ItemPTIconImage.height() + self.ItemInnerSpacingY
            RealButtonWidth = ItemTextW 
            if self.Compound == 'left' or self.Compound == 'right':
                RealButtonWidth = ItemTextW + ItemIconWidth
            else:
                if  RealButtonWidth < ItemIconWidth:
                    RealButtonWidth = ItemIconWidth
            RealButtonHeight = ItemTextH 
            if self.Compound == 'top' or self.Compound == 'bottom':
                RealButtonHeight = ItemTextH + ItemIconHeight
            else:
                if  RealButtonHeight < ItemIconHeight:
                    RealButtonHeight = ItemIconHeight
            if ItemWidth < RealButtonWidth:
                ItemWidth = RealButtonWidth
            if ItemHeight < RealButtonHeight:
                ItemHeight = RealButtonHeight
            centerX = int(ItemWidth/2)
            centerY = int(ItemHeight/2)
            if ItemState == "Click":
                if self.ItemBGColor_Click:
                    newLabelButton.configure(bg = self.ItemBGColor_Click)
                newLabelButton.delete('all')
                if ItemImageList[2]:
                    newLabelButton.create_image(0,0,anchor=tkinter.NW,image=ItemImageList[2],tag="bgimg")
                elif self.ItemPhotoImage_Click:
                    newLabelButton.create_image(0,0,anchor=tkinter.NW,image=self.ItemPhotoImage_Click,tag="bgimg")
                #图标
                if ItemPTIconImage:
                    if self.Compound == 'left':
                        x = self.ItemInnerSpacingX
                        newLabelButton.create_image(self.ItemInnerSpacingX ,centerY,anchor=tkinter.W,image=ItemPTIconImage,tag="icon")
                        x = x + ItemIconWidth
                        newLabelButton.create_text(x,centerY, font=self.ItemFont_Click,anchor=tkinter.W,fill=self.ItemFGColor_Click,text=ItemText,tag='title') 
                    elif self.Compound == 'right':
                        x = ItemWidth - ItemIconWidth
                        newLabelButton.create_image(x,centerY,anchor=tkinter.W,image=ItemPTIconImage,tag="icon")
                        x = x - ItemTextW + self.ItemInnerSpacingX
                        newLabelButton.create_text(x,centerY, font=self.ItemFont_Click,anchor=tkinter.W,fill=self.ItemFGColor_Click,text=ItemText,tag='title') 
                    elif self.Compound == 'top':
                        y = self.ItemInnerSpacingY
                        newLabelButton.create_image(centerX,y,anchor=tkinter.N,image=ItemPTIconImage,tag="icon")
                        y = y + ItemIconHeight
                        newLabelButton.create_text(centerX,y, font=self.ItemFont_Click,anchor=tkinter.N,fill=self.ItemFGColor_Click,text=ItemText,tag='title') 
                    elif self.Compound == 'bottom':
                        y =  ItemHeight - ItemIconHeight
                        newLabelButton.create_image(centerX,y ,anchor=tkinter.N,image=ItemPTIconImage,tag="icon")
                        y = y - ItemTextH + self.ItemInnerSpacingY
                        newLabelButton.create_text(centerX,y, font=self.ItemFont_Click,anchor=tkinter.N,fill=self.ItemFGColor_Click,text=ItemText,tag='title') 
                    elif self.Compound == 'center':
                        newLabelButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=ItemPTIconImage,tag="icon")
                        newLabelButton.create_text(centerX,centerY, font=self.ItemFont_Click,anchor=tkinter.CENTER,fill=self.ItemFGColor_Click,text=ItemText,tag='title') 
                    else:
                        newLabelButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=ItemPTIconImage,tag="icon")
                else:
                    newLabelButton.create_text(centerX,centerY, font=self.ItemFont_Click,anchor=tkinter.CENTER,fill=self.ItemFGColor_Click,text=ItemText,tag='title') 
            elif ItemState == "Hover":
                if self.ItemBGColor_Hover:
                    newLabelButton.configure(bg = self.ItemBGColor_Hover)
                newLabelButton.delete('all')
                if ItemImageList[1]:
                    newLabelButton.create_image(0,0,anchor=tkinter.NW,image=ItemImageList[1],tag="bgimg")
                elif self.ItemPhotoImage_Hover:
                    newLabelButton.create_image(0,0,anchor=tkinter.NW,image=self.ItemPhotoImage_Hover,tag="bgimg")
                #图标
                if ItemPTIconImage:
                    if self.Compound == 'left':
                        x = self.ItemInnerSpacingX
                        newLabelButton.create_image(self.ItemInnerSpacingX ,centerY,anchor=tkinter.W,image=ItemPTIconImage,tag="icon")
                        x = x + ItemIconWidth
                        newLabelButton.create_text(x,centerY, font=self.ItemFont_Hover,anchor=tkinter.W,fill=self.ItemFGColor_Hover,text=ItemText,tag='title') 
                    elif self.Compound == 'right':
                        x = ItemWidth - ItemIconWidth
                        newLabelButton.create_image(x,centerY,anchor=tkinter.W,image=ItemPTIconImage,tag="icon")
                        x = x - ItemTextW + self.ItemInnerSpacingX
                        newLabelButton.create_text(x,centerY, font=self.ItemFont_Hover,anchor=tkinter.W,fill=self.ItemFGColor_Hover,text=ItemText,tag='title') 
                    elif self.Compound == 'top':
                        y = self.ItemInnerSpacingY
                        newLabelButton.create_image(centerX,y,anchor=tkinter.N,image=ItemPTIconImage,tag="icon")
                        y = y + ItemIconHeight
                        newLabelButton.create_text(centerX,y, font=self.ItemFont_Hover,anchor=tkinter.N,fill=self.ItemFGColor_Hover,text=ItemText,tag='title') 
                    elif self.Compound == 'bottom':
                        y =  ItemHeight - ItemIconHeight
                        newLabelButton.create_image(centerX,y ,anchor=tkinter.N,image=ItemPTIconImage,tag="icon")
                        y = y - ItemTextH + self.ItemInnerSpacingY
                        newLabelButton.create_text(centerX,y, font=self.ItemFont_Hover,anchor=tkinter.N,fill=self.ItemFGColor_Hover,text=ItemText,tag='title') 
                    elif self.Compound == 'center':
                        newLabelButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=ItemPTIconImage,tag="icon")
                        newLabelButton.create_text(centerX,centerY, font=self.ItemFont_Hover,anchor=tkinter.CENTER,fill=self.ItemFGColor_Hover,text=ItemText,tag='title') 
                    else:
                        newLabelButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=ItemPTIconImage,tag="icon")
                else:
                    newLabelButton.create_text(centerX,centerY, font=self.ItemFont_Hover,anchor=tkinter.CENTER,fill=self.ItemFGColor_Hover,text=ItemText,tag='title') 
            else:
                if self.ItemBGColor:
                    newLabelButton.configure(bg = self.ItemBGColor)
                newLabelButton.delete('all')
                if ItemImageList[0]:
                    newLabelButton.create_image(0,0,anchor=tkinter.NW,image=ItemImageList[0],tag="bgimg")
                elif self.ItemPhotoImage:
                    newLabelButton.create_image(0,0,anchor=tkinter.NW,image=self.ItemPhotoImage,tag="bgimg")
                #图标
                if ItemPTIconImage:
                    if self.Compound == 'left':
                        x = self.ItemInnerSpacingX
                        newLabelButton.create_image(self.ItemInnerSpacingX ,centerY,anchor=tkinter.W,image=ItemPTIconImage,tag="icon")
                        x = x + ItemIconWidth
                        newLabelButton.create_text(x,centerY, font=self.ItemFont,anchor=tkinter.W,fill=self.ItemFGColor,text=ItemText,tag='title') 
                    elif self.Compound == 'right':
                        x = ItemWidth - ItemIconWidth
                        newLabelButton.create_image(x,centerY,anchor=tkinter.W,image=ItemPTIconImage,tag="icon")
                        x = x - ItemTextW + self.ItemInnerSpacingX
                        newLabelButton.create_text(x,centerY, font=self.ItemFont,anchor=tkinter.W,fill=self.ItemFGColor,text=ItemText,tag='title') 
                    elif self.Compound == 'top':
                        y = self.ItemInnerSpacingY
                        newLabelButton.create_image(centerX,y,anchor=tkinter.N,image=ItemPTIconImage,tag="icon")
                        y = y + ItemIconHeight
                        newLabelButton.create_text(centerX,y, font=self.ItemFont,anchor=tkinter.N,fill=self.ItemFGColor,text=ItemText,tag='title') 
                    elif self.Compound == 'bottom':
                        y =  ItemHeight - ItemIconHeight
                        newLabelButton.create_image(centerX,y ,anchor=tkinter.N,image=ItemPTIconImage,tag="icon")
                        y = y - ItemTextH + self.ItemInnerSpacingY
                        newLabelButton.create_text(centerX,y, font=self.ItemFont,anchor=tkinter.N,fill=self.ItemFGColor,text=ItemText,tag='title') 
                    elif self.Compound == 'center':
                        newLabelButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=ItemPTIconImage,tag="icon")
                        newLabelButton.create_text(centerX,centerY, font=self.ItemFont,anchor=tkinter.CENTER,fill=self.ItemFGColor,text=ItemText,tag='title') 
                    else:
                        newLabelButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=ItemPTIconImage,tag="icon")
                else:
                    newLabelButton.create_text(centerX,centerY, font=self.ItemFont,anchor=tkinter.CENTER,fill=self.ItemFGColor,text=ItemText,tag='title')  
    #展开
    def Redraw(self):
        buttonX = 0
        ButtonIndex = 0
        for ButtonInfo in self.ItemArray:
            buttonX = self.GetItemLeftX(ButtonIndex) + self.ItemSpacingX
            buttonY = self.GetItemTopY(ButtonIndex) + self.ItemSpacingY
            ItemWidth = self.GetItemWidth(ButtonIndex)
            ItemHeight = self.GetItemHeight(ButtonIndex)
            ButtonHandle = ButtonInfo[4]
            if ButtonIndex == self.CurrentIndex:
                self.RedrawItem(ButtonIndex,'Click')
            else:
                self.RedrawItem(ButtonIndex,'Normal')
            self.Canvas.coords(ButtonHandle,buttonX,buttonY)
            self.Canvas.itemconfig(ButtonHandle,width=ItemWidth,height=ItemHeight)
            ButtonIndex = ButtonIndex + 1
#列表菜单
class ListMenu:
    def __init__(self, canvas):
        self.ParentCanvas = canvas
        self.MenuArray = []
        self.TitleHeight = 48
        self.TitleSpacingX = 0
        self.TitleSpacingY = 0
        self.TitleInnerSpacingX = 0
        self.TitleInnerSpacingY = 0
        self.TitleBGColor = '#FFFFFF'
        self.TitleFGColor = '#000000'
        self.TitleFont = tkinter.font.Font(family="Arial",size=12,weight='bold') 
        self.TitleBGColor_Hover = '#FFFFFF'
        self.TitleFGColor_Hover = '#000000'
        self.TitleFont_Hover = tkinter.font.Font(family="Arial",size=12,weight='bold')  
        self.TitleBGColor_Click = '#FFFFFF'
        self.TitleFGColor_Click = '#000000'
        self.TitleFont_Click = tkinter.font.Font(family="Arial",size=12,weight='bold')  
        self.TitleImage = None
        self.TitlePTImage = None
        self.TitleImageFile = None
        self.TitleCompound = 'left'
        self.TitleAnchor = 'left'
        self.ItemHeight = 40
        self.ItemSpacingX = 0
        self.ItemSpacingY = 0
        self.ItemInnerSpacingX = 0
        self.ItemInnerSpacingY = 0
        self.ItemBGColor = '#FFFFFF'
        self.ItemFGColor = '#000000'
        self.ItemFont = tkinter.font.Font(family="Arial",size=12,weight='normal')  
        self.ItemBGColor_Hover = '#FFFFFF'
        self.ItemFGColor_Hover = '#000000'
        self.ItemFont_Hover = tkinter.font.Font(family="Arial",size=12,weight='normal')   
        self.ItemBGColor_Click = '#FFFFFF'
        self.ItemFGColor_Click = '#000000'
        self.ItemFont_Click = tkinter.font.Font(family="Arial",size=12,weight='normal')   
        self.ItemImage = None
        self.ItemPTImage = None
        self.ItemImageFile = None
        self.ItemCompound = 'left'
        self.ItemAnchor = 'center'
        self.ExpandCharDict = {}
        self.ExpandCharDict['▼'] = ['▼','▲']
        self.ExpandCharDict['∨'] = ['∨','∧']
        self.ExpandCharDict['﹀'] = ['﹀','︿']
        self.ExpandCharDict['>'] = ['>','∨']
        self.ExpandChar = '﹀'
        self.SelectedItem = None
        self.Canvas_width = 140
        self.Canvas_height = 200
        self.Canvas_BGColor = '#FFFFFF'
        self.Canvas = tkinter.Canvas(self.ParentCanvas,width=self.Canvas_width,height=self.Canvas_height,bg = self.Canvas_BGColor ,highlightthickness=0,bd=0)
        self.Canvas.place(x=0, y=0,width=self.Canvas_width,height=self.Canvas_height)
        self.Canvas.bind('<Configure>',self.Configure)
        self.ListMenuCallBackFunction = None
        self.ListMenuUIName = None
        self.ListMenuName =  None
        self.SelectedItem = None
    #取得当前画布
    def GetWidget(self):
        return self.Canvas
    #传递绑定事件
    def bind(self,EventName,callBack):
        if self.Canvas:
            self.Canvas.bind(EventName,callBack)
    #窗口大小变化
    def Configure(self,event):
        self.Redraw()
    #取得边框样式
    def Hide(self,layout="place"):
        if layout == "pack":
            self.Canvas.pack_forget()
        elif layout == "grid":
            self.Canvas.grid_forget()
        else:
            self.Canvas.place_forget()
    #传递pack_forget事件
    def pack_forget(self):
        if self.Canvas:
            self.Canvas.pack_forget()
    #传递grid_forget事件
    def grid_forget(self):
        if self.Canvas:
            self.Canvas.grid_forget()
    #传递place_forget事件
    def place_forget(self):
        if self.Canvas:
            self.Canvas.place_forget()
    #取得菜单数据数组
    def GetMenuArray(self):
        return self.MenuArray
    #取得菜单数据数组的复制
    def GetMenuArray_Copy(self):
        MenuArray = []
        for subMenu in self.MenuArray:
            ChildArray = []
            if type(subMenu[2]) == type([]):
                for child in subMenu[2]:
                    ChildArray.append([child[0],child[1],child[2],child[3],child[4],child[5],child[6],child[7]])
            else:
                ChildArray = subMenu[2]
            MenuArray.append([subMenu[0],subMenu[1],ChildArray,subMenu[3],subMenu[4],subMenu[5],subMenu[6],subMenu[7]])
        return MenuArray
    #清空所有
    def Clear(self):
        for subMenu in self.MenuArray:
            subMenuButton = subMenu[4]
            if subMenuButton is None:
                continue
            subMenuHandle = subMenu[5]
            subMenuClickedImage = subMenu[6]
            subMenuClickedPhotoImage = subMenu[7]
            if type(subMenu[2]) == type([]):
                for item in subMenu[2]:
                    itemButton = item[4]
                    itemHandle = item[5]
                    itemClickedImage = item[6]
                    itemClickedPhotoImage = item[7]
                    if itemButton:
                        itemButton.destroy()
                    item[4] = None
                    item[5] = None
                    item[6] = None
                    item[7] = None
            if subMenuButton:
                subMenuButton.destroy()
            subMenu[4] = None
            subMenu[5] = None
            subMenu[6] = None
            subMenu[7] = None
            #self.Canvas.delete(subMenuHandle)
        self.MenuArray.clear()
    #设置当前画布的背景色
    def SetBGColor(self,color):
        self.Canvas_BGColor = color
        self.Canvas.configure(bg = self.Canvas_BGColor)
    #取得当前画布的背景色
    def GetBGColor(self):
        return self.Canvas_BGColor
    #设置标题横向间距
    def SetTitleSpacingX(self,spacingX,redraw = True):
        self.TitleSpacingX = spacingX
        if redraw:
            self.Redraw()
    #取得标题横向间距
    def GetTitleSpacingX(self):
        return self.TitleSpacingX
    #设置标题纵向间距
    def SetTitleSpacingY(self,spacingY,redraw = True):
        self.TitleSpacingY = spacingY
        if redraw:
            self.Redraw()
    #取得标题纵向间距
    def GetTitleSpacingY(self):
        return self.TitleSpacingY
    #设置标题的内部间距
    def SetTitleInnerSpacing(self,spacing,redraw = True):
        self.TitleInnerSpacingX = spacing
        self.TitleInnerSpacingY = spacing
        if redraw:
            self.Redraw()
    #取得标题的内部间距
    def GetTitleInnerSpacing(self):
        return self.TitleInnerSpacingY
    #设置标题栏的背景色
    def SetTitleBGColor(self,color):
        self.TitleBGColor = color
        for subMenu in self.MenuArray:
            titleButton = subMenu[4]
            titleButton.configure(bg = color)
    #取得标题栏的背景色
    def GetTitleBGColor(self):
        return self.TitleBGColor
    #设置标题栏的文字色
    def SetTitleFGColor(self,color,redraw = True):
        self.TitleFGColor = color
        if redraw:
            self.Redraw()
    def GetTitleFGColor(self):
        return self.TitleFGColor
    #设置标题栏的字体
    def SetTitleFont(self,font,redraw = True):
        self.TitleFont = font
        fontHeight = int(self.TitleFont.actual('size'))
        fontHeight = int((fontHeight + 8)*SCALE_FACTOR)
        if fontHeight > self.TitleHeight:
            self.TitleHeight = fontHeight
        if redraw:
            self.Redraw()
    #取得对应标题的文本宽度
    def GetTitleTextWidth(self,itemText):
        return self.TitleFont.measure(itemText) + 2 * self.TitleInnerSpacingY
    #取得对应标题的文本高度
    def GetTitleTextHeight(self):
        fontHeight = int(self.TitleFont.actual('size'))
        fontHeight = int(fontHeight*SCALE_FACTOR)  + int(5 * SCALE_FACTOR)  + 2 * self.TitleInnerSpacingY
        return fontHeight
    #取得当前标题的宽度
    def GetTitleWidth(self,TitleIndex):
        canvasW = self.Canvas.winfo_width()
        if canvasW == 1:
            canvasW = 140
        TitleWidth = canvasW-2*self.TitleSpacingX - 2 * self.TitleInnerSpacingX
        if TitleIndex < len(self.MenuArray):
            TitleInfo = self.MenuArray[TitleIndex]
            TitleIconImage = TitleInfo[-1]
            TitleText = TitleInfo[0]
            TitleTextW = self.GetItemTextWidth(TitleText)
            RealButtonWidth = TitleTextW
            if TitleIconImage:
                TitleIconWidth = TitleIconImage.width()
                if self.TitleCompound == 'left' or self.TitleCompound == 'right':
                    RealButtonWidth = TitleTextW + TitleIconWidth + self.ItemInnerSpacingX
                else:
                    if  RealButtonWidth < TitleIconWidth:
                        RealButtonWidth = TitleIconWidth
            if TitleWidth < RealButtonWidth:
                TitleWidth = RealButtonWidth
            return TitleWidth
        return TitleWidth
    #取得当前标题的高度
    def GetTitleHeight(self,TitleIndex):
        canvasH = self.Canvas.winfo_height()
        if canvasH == 1:
            canvasH = 200
        TitleHeight = self.TitleHeight
        if TitleIndex < len(self.MenuArray):
            TitleInfo = self.MenuArray[TitleIndex]
            TitleIconImage = TitleInfo[-1]
            TitleText = TitleInfo[0]
            TitleTextH = self.GetTitleTextHeight()
            RealButtonHeight = TitleTextH
            if TitleIconImage:
                TitleIconHeight = TitleIconImage.height()
                if self.TitleCompound == 'top' or self.TitleCompound == 'bottom':
                    RealButtonHeight = TitleTextH + TitleIconHeight + self.TitleInnerSpacingY
                else:
                    if  RealButtonHeight < TitleIconHeight:
                        RealButtonHeight = TitleIconHeight
            if TitleHeight < RealButtonHeight:
                TitleHeight = RealButtonHeight
            return TitleHeight
        return TitleHeight
    #设置图标的位置
    def SetTitleCompound(self,compound,redraw = True):
        self.TitleCompound = compound
        if redraw:
            self.Redraw()
    #取得设置图标的位置
    def GetTitleCompound(self):
        return self.TitleCompound
    #设置标题的锚点位置
    def SetTitleAnchor(self,anchor,redraw = True):
        self.TitleAnchor = anchor
        if redraw:
            self.Redraw()
    #取得标题的锚点位置
    def GetTitleAnchor(self):
        return self.TitleAnchor
    #取得标题栏的字体
    def GetTitleFont(self):
        return self.TitleFont
    #设置鼠标悬停在标题栏时的背景色
    def SetTitleBGColor_Hover(self,color):
        self.TitleBGColor_Hover = color
    #取得鼠标悬停在标题栏时背景色
    def GetTitleBGColor_Hover(self):
        return self.TitleBGColor_Hover
    #设置鼠标悬停在标题栏时的文字色
    def SetTitleFGColor_Hover(self,color):
        self.TitleFGColor_Hover = color
    #取得鼠标悬停在标题栏时文字色
    def GetTitleFGColor_Hover(self):
        return self.TitleFGColor_Hover
    #设置标题栏的字体
    def SetTitleFont_Hover(self,font):
        self.TitleFont_Hover = font
    #取得标题栏的字体
    def GetTitleFont_Hover(self):
        return self.TitleFont_Hover
    #设置鼠标按下标题栏时的背景色
    def SetTitleBGColor_Click(self,color):
        self.TitleBGColor_Click = color
    #取得鼠标按下标题栏时背景色
    def GetTitleBGColor_Click(self):
        return self.TitleBGColor_Click
    #设置鼠标按下标题栏时的文字色
    def SetTitleFGColor_Click(self,color):
        self.TitleFGColor_Click = color
    #取得鼠标按下标题栏时文字色
    def GetTitleFGColor_Click(self):
        return self.TitleFGColor_Click
    #设置鼠标按下标题栏时字体
    def SetTitleFont_Click(self,font):
        self.TitleFont_Click = font
    #取得鼠标按下标题栏时字体
    def GetTitleFont_Click(self):
        return self.TitleFont_Click
    #设置标题栏的背景图
    def SetTitleImage(self,fileName,redraw = True):
        global G_ExeDir
        global G_ResDir
        self.TitleImage = None
        self.TitlePTImage = None
        canvasW = self.Canvas.winfo_width()
        canvasH = self.Canvas.winfo_height()
        if canvasW == 1 and canvasH == 1:
            canvasW = 140
            canvasH = 200
        buttonW = canvasW-2*self.TitleSpacingX
        buttonH = self.TitleHeight 
        filePath = fileName
        if fileName:
            if filePath and os.path.exists(filePath) == False:
                filePath = "Resources\\" + fileName
                if os.path.exists(filePath) == False:
                    filePath = os.path.join(G_ExeDir,fileName)
                    if os.path.exists(filePath) == False:
                        filePath = os.path.join(G_ResDir,fileName)
            if filePath and os.path.exists(filePath) == True:
                try:
                    self.TitleImage = Image.open(filePath).convert('RGBA')
                    #Image_Resize = self.TitleImage.resize((buttonW, buttonH),Image.LANCZOS)
                    self.TitlePTImage = ImageTk.PhotoImage(self.TitleImage)
                    imagePath,imageFile = os.path.split(filePath)
                    self.TitleImageFile = imageFile
                except:
                    self.TitleImage = None
                    self.TitlePTImage = None
        if redraw:
            self.Redraw()
    #取得标题栏的字体
    def GetTitleImageFile(self):
        return self.TitleImageFile
    #设置选项横向间距
    def SetItemSpacingX(self,spacingX,redraw = True):
        self.ItemSpacingX = spacingX
        if redraw:
            self.Redraw()
    #取得选项横向间距
    def GetItemSpacingX(self):
        return self.ItemSpacingX
    #设置选项纵向间距
    def SetItemSpacingY(self,spacingY,redraw = True):
        self.ItemSpacingY = spacingY
        if redraw:
            self.Redraw()
    #取得选项纵向间距
    def GetItemSpacingY(self):
        return self.ItemSpacingY
    #设置选项的间跑
    def SetItemInnerSpacing(self,spacing,redraw = True):
        self.ItemInnerSpacingX = spacing
        self.ItemInnerSpacingY = spacing
        if redraw:
            self.Redraw()
    #取得选项的间隔
    def GetItemInnerSpacing(self):
        return self.ItemInnerSpacingY
    #取得对应选项的文本宽度
    def GetItemTextWidth(self,itemText):
        return self.ItemFont.measure(itemText) + 2 * self.ItemInnerSpacingX
    #取得对应选项的文本高度
    def GetItemTextHeight(self):
        fontHeight = int(self.ItemFont.actual('size'))
        fontHeight = int(fontHeight*SCALE_FACTOR)  + int(5 * SCALE_FACTOR)  + 2 * self.ItemInnerSpacingY
        return fontHeight
    #取得当前选项宽度
    def GetItemWidth(self,ItemList,ItemIndex):
        canvasW = self.Canvas.winfo_width()
        if canvasW == 1:
            canvasW = 140
        ItemWidth = canvasW-2*self.ItemSpacingX - 2 * self.ItemInnerSpacingX
        if ItemIndex < len(ItemList):
            ItemInfo = ItemList[ItemIndex]
            ItemIconImage = ItemInfo[-1]
            ItemText = ItemInfo[0]
            ItemTextW = self.GetItemTextWidth(ItemText)
            RealButtonWidth = ItemTextW
            if ItemIconImage:
                ItemIconWidth = ItemIconImage.width()
                if self.ItemCompound == 'left' or self.ItemCompound == 'right':
                    RealButtonWidth = ItemTextW + ItemIconWidth + self.ItemInnerSpacingX
                else:
                    if  RealButtonWidth < ItemIconWidth:
                        RealButtonWidth = ItemIconWidth
            if ItemWidth < RealButtonWidth:
                ItemWidth = RealButtonWidth
            return ItemWidth
        return ItemWidth
    #取得当前选项高度
    def GetItemHeight(self,ItemList,ItemIndex):
        canvasH = self.Canvas.winfo_height()
        if canvasH == 1:
            canvasH = 200
        ItemHeight = self.ItemHeight
        if ItemIndex < len(ItemList):
            ItemInfo = ItemList[ItemIndex]
            ItemIconImage = ItemInfo[-1]
            ItemText = ItemInfo[0]
            ItemTextH = self.GetItemTextHeight()
            RealButtonHeight = ItemTextH
            if ItemIconImage:
                ItemIconHeight = ItemIconImage.height()
                if self.ItemCompound == 'top' or self.ItemCompound == 'bottom':
                    RealButtonHeight = ItemTextH + ItemIconHeight + self.ItemInnerSpacingY
                else:
                    if  RealButtonHeight < ItemIconHeight:
                        RealButtonHeight = ItemIconHeight
            if ItemHeight < RealButtonHeight:
                ItemHeight = RealButtonHeight
            return ItemHeight
        return ItemHeight
    #设置子选项的背景色
    def SetItemBGColor(self,color):
        self.ItemBGColor = color
        for subMenu in self.MenuArray:
            itemList = subMenu[2]
            for item in itemList:
                itemButton = item[4]
                itemButton.configure(bg = color)
    #取得子选项背景色
    def GetItemBGColor(self):
        return self.ItemBGColor
    #设置子选项文字色
    def SetItemFGColor(self,color,redraw = True):
        self.ItemFGColor = color
        if redraw:
            self.Redraw()
    #取得子选项文字色
    def GetItemFGColor(self):
        return self.ItemFGColor
    #设置子选项字体
    def SetItemFont(self,font,redraw = True):
        self.ItemFont = font
        fontHeight = int(self.TitleFont.actual('size'))
        fontHeight = fontHeight + 8
        fontHeight = int((fontHeight + 8)*SCALE_FACTOR)
        if fontHeight > self.ItemHeight:
            self.ItemHeight = fontHeight
        if redraw:
            self.Redraw()
    #取得子选项的字体
    def GetItemFont(self):
        return self.ItemFont
    #设置鼠标悬停在选项的背景色
    def SetItemBGColor_Hover(self,color):
        self.ItemBGColor_Hover = color
    #取得鼠标悬停在标选项背景色
    def GetItemBGColor_Hover(self):
        return self.ItemBGColor_Hover
    #设置鼠标悬停在选项的文字色
    def SetItemFGColor_Hover(self,color):
        self.ItemFGColor_Hover = color
    #取得鼠标悬停在选项文字色
    def GetItemFGColor_Hover(self):
        return self.ItemFGColor_Hover
    #设置选项字体
    def SetItemFont_Hover(self,font):
        self.ItemFont_Hover = font
    #取得选项字体
    def GetItemFont_Hover(self):
        return self.ItemFont_Hover
    #设置鼠标按下选项背景色
    def SetItemBGColor_Click(self,color):
        self.ItemBGColor_Click = color
    #取得鼠标按下选项背景色
    def GetItemBGColor_Click(self):
        return self.ItemBGColor_Click
    #设置鼠标按下选项文字色
    def SetItemFGColor_Click(self,color):
        self.ItemFGColor_Click = color
    #取得鼠标按下选项文字色
    def GetItemFGColor_Click(self):
        return self.ItemFGColor_Click
    #设置鼠标按下选项时字体
    def SetItemFont_Click(self,font):
        self.ItemFont_Click = font
    #取得鼠标按下选项时字体
    def GetItemFont_Click(self):
        return self.ItemFont_Click
    #设置子选项的图片
    def SetItemImage(self,fileName,redraw = True):
        global G_ExeDir
        global G_ResDir
        self.ItemImage = None
        self.ItemPTImage = None
        canvasW = self.Canvas.winfo_width()
        canvasH = self.Canvas.winfo_height()
        if canvasW == 1 and canvasH == 1:
            canvasW = 140
            canvasH = 200
        itemW = canvasW-2*self.ItemSpacingX
        itemH = self.ItemHeight 
        filePath = fileName
        if fileName:
            if filePath and os.path.exists(filePath) == False:
                filePath = "Resources\\" + fileName
                if os.path.exists(filePath) == False:
                    filePath = os.path.join(G_ExeDir,fileName)
                    if os.path.exists(filePath) == False:
                        filePath = os.path.join(G_ResDir,fileName)
            if filePath and os.path.exists(filePath) == True:
                try:
                    self.ItemImage = Image.open(filePath).convert('RGBA')
                    #Image_Resize = Image_Temp.resize((110, 110),Image.LANCZOS)
                    self.ItemPTImage = ImageTk.PhotoImage(self.ItemImage)
                    imagePath,imageFile = os.path.split(filePath)
                    self.ItemImageFile = imageFile
                except:
                    self.ItemImage = None
                    self.ItemPTImage = None
        else:
            for subMenu in self.MenuArray:
                if type(subMenu[2]) == type([]):
                    for item in subMenu[2]:
                        itemButton = item[4]
                        itemButton.delete('bgimg')
        if redraw:
            self.Redraw()
    #取得选项的图片文件
    def GetItemImageFile(self):
        return self.ItemImageFile
    #设置选项的图标位置
    def SetItemCompound(self,compound,redraw = True):
        self.ItemCompound = compound
        if redraw:
            self.Redraw()
    #取得设置图标的位置
    def GetItemCompound(self):
        return self.ItemCompound
    #设置选项的锚点位置
    def SetItemAnchor(self,anchor,redraw = True):
        self.ItemAnchor = anchor
        if redraw:
            self.Redraw()
    #取得选项的锚点位置
    def GetItemAnchor(self):
        return self.ItemAnchor
    #设置标题全部展开
    def ExpandAllTitle(self,expand = True):
        for subMenu in self.MenuArray:
            subMenu[3] = expand
        self.Redraw()
    #取得标题是否展开
    def IsAllTitleExpand(self):
        for subMenu in self.MenuArray:
            if subMenu[3] == False:
                return False
        return True
    #设置标题展开
    def ExpandTitle(self,titleName,expand = True):
        for subMenu in self.MenuArray:
            if subMenu[0] == titleName:
                subMenu[3] = expand
        self.Redraw()
    #取得标题是否展开
    def IsTitleExpand(self,titleName):
        for subMenu in self.MenuArray:
            if subMenu[0] == titleName:
                return subMenu[3]
        return False
    #计算高度
    def GetTitleTop(self,index):
        Y = self.TitleSpacingY
        TitleIndex = 0
        for subMenu in self.MenuArray:
            if TitleIndex == index:
                return Y
            else:
                isExpand = subMenu[3] 
                TitleHeight = self.GetTitleHeight(TitleIndex)
                Y = Y + (TitleHeight+self.TitleSpacingY)
                if isExpand == True and type(subMenu[2]) == type([]):
                    itemCount = len(subMenu[2])    
                    Y = Y + itemCount * (self.ItemHeight+self.ItemSpacingY)
            TitleIndex = TitleIndex + 1
        return self.TitleSpacingY
    def Title_Button1(self,event):
        for subMenu in self.MenuArray:
            if subMenu[4] == event.widget:
                self.ResetSelectedItem()
                if self.TitleBGColor_Click:
                    event.widget.configure(bg=self.TitleBGColor_Click)
                if self.TitleFGColor_Click:
                    event.widget.itemconfig('title',fill=self.TitleFGColor_Click)
                    event.widget.itemconfig('expand',fill=self.TitleFGColor_Click)
                if self.TitleFont_Click:
                    event.widget.itemconfig('title',font = self.TitleFont_Click)
                self.SelectedItem = event.widget 
    def Title_ButtonRelease1(self,event):  
        for subMenu in self.MenuArray:
            if subMenu[4] == event.widget:
                #响应展开和收缩
                subMenuName = subMenu[0]
                if type(subMenu[2]) == type([]):
                    if subMenu[3] == False:
                        subMenu[3] = True
                        self.Redraw()
                    else:
                        subMenu[3] = False
                        self.Redraw()
                elif type(subMenu[2]) == type(""):
                    print("ClickItem:"+subMenuName)
                    self.ClickItem(subMenuName,subMenu[2])
    def Title_Enter(self,event):
        event.widget.configure(cursor='hand2')
        for subMenu in self.MenuArray:
            if subMenu[4] == event.widget and self.SelectedItem != subMenu[4]:
                if self.TitleBGColor_Hover:
                    event.widget.configure(bg = self.TitleBGColor_Hover)
                if self.TitleFGColor_Hover:
                    event.widget.itemconfig('title',fill=self.TitleFGColor_Hover)
                    event.widget.itemconfig('expand',fill=self.TitleFGColor_Hover)
                if self.TitleFont_Hover:
                    event.widget.itemconfig('title',font = self.TitleFont_Hover)
    def Title_Leave(self,event):    
        try:
            event.widget.configure(cursor='arrow')
            if self.SelectedItem != event.widget:
                if self.TitleBGColor:
                    event.widget.configure(bg = self.TitleBGColor)
                if self.TitleFGColor:
                    event.widget.itemconfig('title',fill=self.TitleFGColor)
                    event.widget.itemconfig('expand',fill=self.TitleFGColor)
                if self.TitleFont:
                    event.widget.itemconfig('title',font = self.TitleFont)
        except:
            pass
    #增加一级菜单
    def AddTitle(self,titleName='',titleIcon='',titlePage=''):
        TitleCount = len(self.MenuArray)
        canvasW = self.Canvas.winfo_width()
        canvasH = self.Canvas.winfo_height()
        if canvasW == 1 and canvasH == 1:
            canvasW = 140
            canvasH = 200
        self.MenuArray.append([titleName,titleIcon,titlePage,True,None,None,None,None])
        #subMenuTag = str("submenu_%d"%TitleIndex)
        buttonX = self.TitleSpacingX
        buttonY = self.GetTitleTop(TitleCount)
        buttonW = canvasW-2*self.TitleSpacingX
        buttonH = self.TitleHeight 
        newButton = tkinter.Canvas(self.Canvas,width = buttonW,height = 20,relief=tkinter.FLAT,bg=self.TitleBGColor,highlightthickness=0,bd=0)
        newButton.place(x = buttonX,y = buttonY,width = buttonW ,height = buttonH) 
        newButton.bind('<Button-1>',self.Title_Button1)
        newButton.bind('<ButtonRelease-1>',self.Title_ButtonRelease1)
        newButton.bind('<Enter>',self.Title_Enter)
        newButton.bind('<Leave>',self.Title_Leave)
        newButton.configure(bg = self.TitleBGColor)
        submeshIconImage = None
        submeshIconPTImage = None
        if titleIcon != "":
            filePath = titleIcon
            if filePath and os.path.exists(filePath) == False:
                filePath = os.path.join(G_ExeDir,titleIcon)
                if os.path.exists(filePath) == False:
                    filePath = os.path.join(G_ResDir,titleIcon)
            if filePath and os.path.exists(filePath) == True:
                try:
                    submeshIconImage = Image.open(filePath).convert('RGBA')
                    submeshIconPTImage = ImageTk.PhotoImage(submeshIconImage)
                except:
                    pass
        buttonHandle = self.Canvas.create_window(buttonX,buttonY, window=newButton, anchor=tkinter.NW,tag="title")
        self.Canvas.itemconfig(buttonHandle,width=buttonW,height=buttonH)
        self.MenuArray[TitleCount][4] = newButton
        self.MenuArray[TitleCount][5] = buttonHandle
        self.MenuArray[TitleCount][6] = submeshIconImage
        self.MenuArray[TitleCount][7] = submeshIconPTImage
        self.RedrawTitle(TitleCount)
    #增加一级菜单(废弃，改名为AddTitle)
    def AddSubMenu(self,submenName='',submenuIcon='',submenuPage=''):
        self.AddTitle(self,submenName,submenuIcon,submenuPage)
    #删除对应标题基
    def DelTitle(self,titleName):
        subMenuIndex = 0
        for subMenu in self.MenuArray:
            if subMenu[0] == titleName:
                self.MenuArray.pop(subMenuIndex)
                break
            subMenuIndex = subMenuIndex + 1
        self.Redraw()
    def Item_Button1(self,event):
        for subMenu in self.MenuArray:
            if type(subMenu[2]) == type([]):
                for items in subMenu[2]:
                    if items[4] == event.widget: 
                        self.ResetSelectedItem()
                        if self.ItemBGColor_Click:
                            event.widget.configure(bg = self.ItemBGColor_Click)
                        if self.ItemFGColor_Click:
                            event.widget.itemconfig('title',fill=self.ItemFGColor_Click)
                        if self.ItemFont_Click:
                            event.widget.itemconfig('title',font = self.ItemFont_Click)
                        self.SelectedItem = event.widget 
    def Item_ButtonRelease1(self,event):  
        for subMenu in self.MenuArray:
            if type(subMenu[2]) == type([]):
                for itemInfo in subMenu[2]:
                    if itemInfo[4] == event.widget:
                        subMenuName = subMenu[0]
                        itemName = itemInfo[0]
                        itemValue = itemInfo[2]
                        print("ClickItem:"+subMenuName+" "+itemName)
                        self.ClickItem(itemName,itemValue)
    def Item_Enter(self,event):
        event.widget.configure(cursor='hand2')
        for subMenu in self.MenuArray:
            if type(subMenu[2]) == type([]):
                for items in subMenu[2]:
                    if items[4] == event.widget and self.SelectedItem != items[4]:
                        if self.ItemBGColor_Hover:
                            event.widget.configure(bg = self.ItemBGColor_Hover)
                        if self.ItemFGColor_Hover:
                            event.widget.itemconfig('title',fill=self.ItemFGColor_Hover)
                        if self.ItemFont_Hover:
                             event.widget.itemconfig('title',font = self.ItemFont_Hover)
                        return 
    def Item_Leave(self,event):
        try:
            event.widget.configure(cursor='arrow')
            if self.SelectedItem != event.widget:
                if self.ItemBGColor:
                    event.widget.configure(bg = self.ItemBGColor)
                if self.ItemFGColor:
                    event.widget.itemconfig('title',fill=self.ItemFGColor)
                if self.ItemFont:
                    event.widget.itemconfig('title',font = self.ItemFont)
        except:
            pass
    #增加二级菜单（子菜单项）
    def AddItem(self,itemName='',titleName='',itemIcon='',itemPage=''):
        canvasW = self.Canvas.winfo_width()
        canvasH = self.Canvas.winfo_height()
        if canvasW == 1 and canvasH == 1:
            canvasW = 140
            canvasH = 200
        titleIndex = 0
        for subMenu in self.MenuArray:
            if subMenu[0] == titleName:
                if type(subMenu[2]) == type(""):
                    subMenu[2] = []
                itemCount = len(subMenu[2])
                itemTop = itemCount * (self.ItemHeight+self.ItemSpacingY)
                isExpand = subMenu[3] 
                subMeshTop = self.GetTitleTop(titleIndex)
                FirstItemTop = subMeshTop + (self.TitleHeight+self.TitleSpacingY)
                itemX = self.ItemSpacingX
                itemY = FirstItemTop + itemTop
                itemW = canvasW-2*self.ItemSpacingX
                itemH = self.ItemHeight 
                newItem = tkinter.Canvas(self.Canvas,width = itemW,height = itemH,relief=tkinter.FLAT,bg=self.ItemBGColor,highlightthickness=0,bd=0)
                newItem.place(x = itemX,y = itemY,width = itemW ,height = itemH ) 
                newItem.bind('<Button-1>',self.Item_Button1)
                newItem.bind('<ButtonRelease-1>',self.Item_ButtonRelease1)
                newItem.bind('<Enter>',self.Item_Enter)
                newItem.bind('<Leave>',self.Item_Leave)
                newItem.configure(bg = self.ItemBGColor)
                ItemImage = None
                ItemPhotoImage = None
                if itemIcon != "":
                    filePath = itemIcon
                    if filePath and os.path.exists(filePath) == False:
                        filePath = os.path.join(G_ExeDir,itemIcon)
                        if os.path.exists(filePath) == False:
                            filePath = os.path.join(G_ResDir,itemIcon)
                    if filePath and os.path.exists(filePath) == True:
                        try:
                            ItemImage = Image.open(filePath).convert('RGBA')
                            ItemPhotoImage = ImageTk.PhotoImage(ItemImage)
                        except:
                            pass
                itemHandle = self.Canvas.create_window(itemX,itemY, window=newItem, anchor=tkinter.NW,tag="item")
                if isExpand == True:
                    self.Canvas.itemconfig(itemHandle,width=itemW,height=itemH)
                else:
                    self.Canvas.itemconfig(itemHandle,width=0,height=0)
                subMenu[2].append([itemName,itemIcon,itemPage,itemTop,newItem,itemHandle,ItemImage,ItemPhotoImage])
                self.RedrawItem(subMenu[2],itemCount)
                return 
            titleIndex = titleIndex + 1
    #删除对应标题基
    def DelItem(self,titleName,itemName):
        subMenuIndex = 0
        for subMenu in self.MenuArray:
            if subMenu[0] == titleName:
                itemIndex = 0
                for Item in subMenu[2]:
                    if Item[0] == itemName:
                        subMenu[2].pop(itemIndex)
                        break
                    itemIndex = itemIndex + 1
                break
        self.Redraw()
    #点击标题按钮
    def ClickTitleButton(self,subMenuName):
        canvasW = self.Canvas.winfo_width()
        canvasH = self.Canvas.winfo_height()
        if canvasW == 1 and canvasH == 1:
            canvasW = 140
            canvasH = 200
        for subMenu in self.MenuArray:
            if subMenu[0] == subMenuName:
                subMeshTop = self.GetSubMenuY(subMenuName)
                if subMenu[3] == False:
                    subMenu[3] = True
                    self.Redraw()
                else:
                    subMenu[3] = False
                    self.Redraw()
    #绘制一个按钮
    def RedrawTitle(self,TitleIndex,TitleState='Normal'):
        canvasW = self.Canvas.winfo_width()
        if canvasW == 1:
            canvasW = 140
        InitTitleWidth = canvasW-2*self.TitleSpacingX - 2 * self.TitleInnerSpacingX
        if TitleIndex >= 0 and TitleIndex < len(self.MenuArray):
            ButtonInfo = self.MenuArray[TitleIndex]
            TitleText = ButtonInfo[0]
            TitlePTIconImage = ButtonInfo[-1]
            TitleButton = ButtonInfo[4]
            TitleWidth = InitTitleWidth
            TitleHeight = self.TitleHeight + 2 * self.TitleInnerSpacingY
            TitleTextW = self.GetTitleTextWidth(TitleText)
            TitleTextH = self.GetTitleTextHeight()
            TitleIconWidth = 0
            TitleIconHeight = 0
            if TitlePTIconImage:                
                TitleIconWidth = TitlePTIconImage.width() + self.TitleInnerSpacingX
                TitleIconHeight = TitlePTIconImage.height() + self.TitleInnerSpacingY
            RealButtonWidth = TitleTextW 
            if self.TitleCompound == 'left' or self.TitleCompound == 'right':
                RealButtonWidth = TitleTextW + TitleIconWidth
            else:
                if  RealButtonWidth < TitleIconWidth:
                    RealButtonWidth = TitleIconWidth
            RealButtonHeight = TitleTextH 
            if self.TitleCompound == 'top' or self.TitleCompound == 'bottom':
                RealButtonHeight = TitleTextH + TitleIconHeight
            else:
                if  RealButtonHeight < TitleIconHeight:
                    RealButtonHeight = TitleIconHeight
            if TitleWidth < RealButtonWidth:
                TitleWidth = RealButtonWidth
            if TitleHeight < RealButtonHeight:
                TitleHeight = RealButtonHeight
            centerX = int(TitleWidth/2)
            centerY = int(TitleHeight/2)
            if TitleState == "Click":
                if self.TitleBGColor_Click:
                    TitleButton.configure(bg = self.TitleBGColor_Click)
                TitleButton.delete('all')
                if self.TitlePTImage:
                    TitleButton.create_image(0,0,anchor=tkinter.NW,image=self.TitlePTImage,tag="bgimg")
                #图标
                if TitlePTIconImage:
                    if self.TitleCompound == 'left':
                        #跟据锚点位置计算X位置
                        leftX = self.TitleInnerSpacingX 
                        if self.TitleAnchor == "center":
                            leftX = int((TitleWidth - TitleIconWidth - TitleTextW)/2)
                        elif self.TitleAnchor == "right":
                            leftX = TitleWidth - self.TitleInnerSpacingX - TitleIconWidth - TitleTextW
                        TitleButton.create_image(leftX ,centerY,anchor=tkinter.W,image=TitlePTIconImage,tag="icon")
                        TitleButton.create_text(leftX + TitleIconWidth,centerY, font=self.TitleFont_Click,anchor=tkinter.W,fill=self.TitleFGColor_Click,text=TitleText,tag='title') 
                    elif self.TitleCompound == 'right':
                        #跟据锚点位置计算X位置
                        leftX = self.TitleInnerSpacingX 
                        if self.TitleAnchor == "center":
                            leftX = int((TitleWidth - TitleIconWidth - TitleTextW)/2)
                        elif self.TitleAnchor == "right":
                            leftX = TitleWidth - self.TitleInnerSpacingX - TitleIconWidth - TitleTextW
                        TitleButton.create_text(leftX,centerY, font=self.TitleFont_Click,anchor=tkinter.W,fill=self.TitleFGColor_Click,text=TitleText,tag='title') 
                        TitleButton.create_image(leftX + TitleIconWidth,centerY,anchor=tkinter.W,image=TitlePTIconImage,tag="icon")
                    elif self.TitleCompound == 'top':
                        ContentWidth = TitleTextW
                        if TitleTextW < TitleIconWidth:
                            ContentWidth = TitleIconWidth
                        #跟据锚点位置计算X位置
                        centerX = self.TitleInnerSpacingX + int(ContentWidth/2)
                        if self.TitleAnchor == "center":
                            centerX = int(TitleWidth/2)
                        elif self.TitleAnchor == "right":
                            centerX = TitleWidth - self.TitleInnerSpacingX - int(ContentWidth/2)
                        TitleButton.create_image(centerX,self.TitleInnerSpacingY,anchor=tkinter.N,image=TitlePTIconImage,tag="icon")
                        TitleButton.create_text(centerX,self.TitleInnerSpacingY + TitleIconHeight, font=self.TitleFont_Click,anchor=tkinter.N,fill=self.TitleFGColor_Click,text=TitleText,tag='title') 
                    elif self.TitleCompound == 'bottom':
                        ContentWidth = TitleTextW
                        if TitleTextW < TitleIconWidth:
                            ContentWidth = TitleIconWidth
                        #跟据锚点位置计算X位置
                        centerX = self.TitleInnerSpacingX + int(ContentWidth/2)
                        if self.TitleAnchor == "center":
                            centerX = int(TitleWidth/2)
                        elif self.TitleAnchor == "right":
                            centerX = TitleWidth - self.TitleInnerSpacingX - int(ContentWidth/2)
                        TitleButton.create_text(centerX,TitleHeight - self.TitleInnerSpacingY-TitleIconHeight - TitleTextH, font=self.TitleFont_Click,anchor=tkinter.N,fill=self.TitleFGColor_Click,text=TitleText,tag='title') 
                        TitleButton.create_image(centerX,TitleHeight - self.TitleInnerSpacingY-TitleIconHeight ,anchor=tkinter.N,image=TitlePTIconImage,tag="icon")
                    elif self.TitleCompound == 'center':
                        TitleButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=TitlePTIconImage,tag="icon")
                        TitleButton.create_text(centerX,centerY, font=self.TitleFont_Click,anchor=tkinter.CENTER,fill=self.TitleFGColor_Click,text=TitleText,tag='title') 
                    else:
                        TitleButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=TitlePTIconImage,tag="icon")
                else:
                    #跟据锚点位置计算X位置
                    leftX = self.TitleInnerSpacingX 
                    if self.TitleAnchor == "center":
                        leftX = int(TitleWidth - TitleTextW)/2
                    elif self.TitleAnchor == "right":
                        leftX = TitleWidth - self.TitleInnerSpacingX - TitleTextW
                    TitleButton.create_text(leftX,centerY, font=self.TitleFont_Click,anchor=tkinter.W,fill=self.TitleFGColor_Click,text=TitleText,tag='title')  
            elif TitleState == "Hover":
                if self.TitleBGColor_Hover:
                    TitleButton.configure(bg = self.TitleBGColor_Hover)
                TitleButton.delete('all')
                if self.TitlePTImage:
                    TitleButton.create_image(0,0,anchor=tkinter.NW,image=self.TitlePTImage,tag="bgimg")
                #图标
                if TitlePTIconImage:
                    if self.TitleCompound == 'left':
                        #跟据锚点位置计算X位置
                        leftX = self.TitleInnerSpacingX 
                        if self.TitleAnchor == "center":
                            leftX = int((TitleWidth - TitleIconWidth - TitleTextW)/2)
                        elif self.TitleAnchor == "right":
                            leftX = TitleWidth - self.TitleInnerSpacingX - TitleIconWidth - TitleTextW
                        TitleButton.create_image(leftX ,centerY,anchor=tkinter.W,image=TitlePTIconImage,tag="icon")
                        TitleButton.create_text(leftX + TitleIconWidth,centerY, font=self.TitleFont_Hover,anchor=tkinter.W,fill=self.TitleFGColor_Hover,text=TitleText,tag='title') 
                    elif self.TitleCompound == 'right':
                        #跟据锚点位置计算X位置
                        leftX = self.TitleInnerSpacingX 
                        if self.TitleAnchor == "center":
                            leftX = int((TitleWidth - TitleIconWidth - TitleTextW)/2)
                        elif self.TitleAnchor == "right":
                            leftX = TitleWidth - self.TitleInnerSpacingX - TitleIconWidth - TitleTextW
                        TitleButton.create_text(leftX,centerY, font=self.TitleFont_Hover,anchor=tkinter.W,fill=self.TitleFGColor_Hover,text=TitleText,tag='title') 
                        TitleButton.create_image(leftX + TitleIconWidth,centerY,anchor=tkinter.W,image=TitlePTIconImage,tag="icon")
                    elif self.TitleCompound == 'top':
                        ContentWidth = TitleTextW
                        if TitleTextW < TitleIconWidth:
                            ContentWidth = TitleIconWidth
                        #跟据锚点位置计算X位置
                        centerX = self.TitleInnerSpacingX + int(ContentWidth/2)
                        if self.TitleAnchor == "center":
                            centerX = int(TitleWidth/2)
                        elif self.TitleAnchor == "right":
                            centerX = TitleWidth - self.TitleInnerSpacingX - int(ContentWidth/2)
                        TitleButton.create_image(centerX,self.TitleInnerSpacingY,anchor=tkinter.N,image=TitlePTIconImage,tag="icon")
                        TitleButton.create_text(centerX,self.TitleInnerSpacingY + TitleIconHeight, font=self.TitleFont_Hover,anchor=tkinter.N,fill=self.TitleFGColor_Hover,text=TitleText,tag='title') 
                    elif self.TitleCompound == 'bottom':
                        ContentWidth = TitleTextW
                        if TitleTextW < TitleIconWidth:
                            ContentWidth = TitleIconWidth
                        #跟据锚点位置计算X位置
                        centerX = self.TitleInnerSpacingX + int(ContentWidth/2)
                        if self.TitleAnchor == "center":
                            centerX = int(TitleWidth/2)
                        elif self.TitleAnchor == "right":
                            centerX = TitleWidth - self.TitleInnerSpacingX - int(ContentWidth/2)
                        TitleButton.create_text(centerX,TitleHeight - self.TitleInnerSpacingY-TitleIconHeight - TitleTextH, font=self.TitleFont_Hover,anchor=tkinter.N,fill=self.TitleFGColor_Hover,text=TitleText,tag='title') 
                        TitleButton.create_image(centerX,TitleHeight - self.TitleInnerSpacingY-TitleIconHeight ,anchor=tkinter.N,image=TitlePTIconImage,tag="icon")
                    elif self.TitleCompound == 'center':
                        TitleButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=TitlePTIconImage,tag="icon")
                        TitleButton.create_text(centerX,centerY, font=self.TitleFont_Hover,anchor=tkinter.CENTER,fill=self.TitleFGColor_Hover,text=TitleText,tag='title') 
                    else:
                        TitleButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=TitlePTIconImage,tag="icon")
                else:
                    #跟据锚点位置计算X位置
                    leftX = self.TitleInnerSpacingX 
                    if self.TitleAnchor == "center":
                        leftX = int(TitleWidth - TitleTextW)/2
                    elif self.TitleAnchor == "right":
                        leftX = TitleWidth - self.TitleInnerSpacingX - TitleTextW
                    TitleButton.create_text(leftX,centerY, font=self.TitleFont_Hover,anchor=tkinter.W,fill=self.TitleFGColor_Hover,text=TitleText,tag='title')  
            else:
                if self.TitleBGColor:
                    TitleButton.configure(bg = self.TitleBGColor)
                TitleButton.delete('all')
                if self.TitlePTImage:
                    TitleButton.create_image(0,0,anchor=tkinter.NW,image=self.TitlePTImage,tag="bgimg")
                #图标
                if TitlePTIconImage:
                    if self.TitleCompound == 'left':
                        #跟据锚点位置计算X位置
                        leftX = self.TitleInnerSpacingX 
                        if self.TitleAnchor == "center":
                            leftX = int((TitleWidth - TitleIconWidth - TitleTextW)/2)
                        elif self.TitleAnchor == "right":
                            leftX = TitleWidth - self.TitleInnerSpacingX - TitleIconWidth - TitleTextW
                        TitleButton.create_image(leftX ,centerY,anchor=tkinter.W,image=TitlePTIconImage,tag="icon")
                        TitleButton.create_text(leftX + TitleIconWidth,centerY, font=self.TitleFont,anchor=tkinter.W,fill=self.TitleFGColor,text=TitleText,tag='title') 
                    elif self.TitleCompound == 'right':
                        #跟据锚点位置计算X位置
                        leftX = self.TitleInnerSpacingX 
                        if self.TitleAnchor == "center":
                            leftX = int((TitleWidth - TitleIconWidth - TitleTextW)/2)
                        elif self.TitleAnchor == "right":
                            leftX = TitleWidth - self.TitleInnerSpacingX - TitleIconWidth - TitleTextW
                        TitleButton.create_text(leftX,centerY, font=self.TitleFont,anchor=tkinter.W,fill=self.TitleFGColor,text=TitleText,tag='title') 
                        TitleButton.create_image(leftX + TitleIconWidth,centerY,anchor=tkinter.W,image=TitlePTIconImage,tag="icon")
                    elif self.TitleCompound == 'top':
                        ContentWidth = TitleTextW
                        if TitleTextW < TitleIconWidth:
                            ContentWidth = TitleIconWidth
                        #跟据锚点位置计算X位置
                        centerX = self.TitleInnerSpacingX + int(ContentWidth/2)
                        if self.TitleAnchor == "center":
                            centerX = int(TitleWidth/2)
                        elif self.TitleAnchor == "right":
                            centerX = TitleWidth - self.TitleInnerSpacingX - int(ContentWidth/2)
                        TitleButton.create_image(centerX,self.TitleInnerSpacingY,anchor=tkinter.N,image=TitlePTIconImage,tag="icon")
                        TitleButton.create_text(centerX,self.TitleInnerSpacingY + TitleIconHeight, font=self.TitleFont,anchor=tkinter.N,fill=self.TitleFGColor,text=TitleText,tag='title') 
                    elif self.TitleCompound == 'bottom':
                        ContentWidth = TitleTextW
                        if TitleTextW < TitleIconWidth:
                            ContentWidth = TitleIconWidth
                        #跟据锚点位置计算X位置
                        centerX = self.TitleInnerSpacingX + int(ContentWidth/2)
                        if self.TitleAnchor == "center":
                            centerX = int(TitleWidth/2)
                        elif self.TitleAnchor == "right":
                            centerX = TitleWidth - self.TitleInnerSpacingX - int(ContentWidth/2)
                        TitleButton.create_text(centerX,TitleHeight - self.TitleInnerSpacingY-TitleIconHeight-TitleTextH, font=self.TitleFont,anchor=tkinter.N,fill=self.TitleFGColor,text=TitleText,tag='title') 
                        TitleButton.create_image(centerX,TitleHeight - self.TitleInnerSpacingY-TitleIconHeight ,anchor=tkinter.N,image=TitlePTIconImage,tag="icon")
                    elif self.TitleCompound == 'center':
                        TitleButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=TitlePTIconImage,tag="icon")
                        TitleButton.create_text(centerX,centerY, font=self.TitleFont,anchor=tkinter.CENTER,fill=self.TitleFGColor,text=TitleText,tag='title') 
                    else:
                        TitleButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=TitlePTIconImage,tag="icon")
                else:
                    #跟据锚点位置计算X位置
                    leftX = self.TitleInnerSpacingX 
                    if self.TitleAnchor == "center":
                        leftX = int(TitleWidth - TitleTextW)/2
                    elif self.TitleAnchor == "right":
                        leftX = TitleWidth - self.TitleInnerSpacingX - TitleTextW
                    TitleButton.create_text(leftX,centerY, font=self.TitleFont,anchor=tkinter.W,fill=self.TitleFGColor,text=TitleText,tag='title')  
    #绘制一个按钮
    def RedrawItem(self,ItemList,ItemIndex,ItemState='Normal'):
        canvasW = self.Canvas.winfo_width()
        if canvasW == 1:
            canvasW = 140
        InitItemWidth = canvasW-2*self.ItemSpacingX - 2 * self.ItemInnerSpacingX
        if ItemIndex >= 0 and ItemIndex < len(ItemList):
            ButtonInfo = ItemList[ItemIndex]
            ItemText = ButtonInfo[0]
            ItemPTIconImage = ButtonInfo[-1]
            ItemButton = ButtonInfo[4]
            ItemWidth = InitItemWidth
            ItemHeight = self.ItemHeight + 2 * self.ItemInnerSpacingY
            ItemTextW = self.GetItemTextWidth(ItemText)
            ItemTextH = self.GetItemTextHeight()
            ItemIconWidth = 0
            ItemIconHeight = 0
            if ItemPTIconImage:                
                ItemIconWidth = ItemPTIconImage.width() + self.ItemInnerSpacingX
                ItemIconHeight = ItemPTIconImage.height() + self.ItemInnerSpacingY
            RealButtonWidth = ItemTextW 
            if self.ItemCompound == 'left' or self.ItemCompound == 'right':
                RealButtonWidth = ItemTextW + ItemIconWidth
            else:
                if  RealButtonWidth < ItemIconWidth:
                    RealButtonWidth = ItemIconWidth
            RealButtonHeight = ItemTextH 
            if self.ItemCompound == 'top' or self.ItemCompound == 'bottom':
                RealButtonHeight = ItemTextH + ItemIconHeight
            else:
                if  RealButtonHeight < ItemIconHeight:
                    RealButtonHeight = ItemIconHeight
            if ItemWidth < RealButtonWidth:
                ItemWidth = RealButtonWidth
            if ItemHeight < RealButtonHeight:
                ItemHeight = RealButtonHeight
            centerX = int(ItemWidth/2)
            centerY = int(ItemHeight/2)
            if ItemState == "Click":
                if self.ItemBGColor_Click:
                    ItemButton.configure(bg = self.ItemBGColor_Click)
                ItemButton.delete('all')
                if self.ItemPTImage:
                    ItemButton.create_image(0,0,anchor=tkinter.NW,image=self.ItemPTImage,tag="bgimg")
                #图标
                if ItemPTIconImage:
                    if self.ItemCompound == 'left':
                        #跟据锚点位置计算X位置
                        leftX = self.ItemInnerSpacingX 
                        if self.ItemAnchor == "center":
                            leftX = int((ItemWidth - ItemIconWidth - ItemTextW)/2)
                        elif self.ItemAnchor == "right":
                            leftX = ItemWidth - self.ItemInnerSpacingX - ItemIconWidth - ItemTextW
                        ItemButton.create_image(leftX ,centerY,anchor=tkinter.W,image=ItemPTIconImage,tag="icon")
                        ItemButton.create_text(leftX + ItemIconWidth,centerY, font=self.ItemFont_Click,anchor=tkinter.W,fill=self.ItemFGColor_Click,text=ItemText,tag='title') 
                    elif self.ItemCompound == 'right':
                        #跟据锚点位置计算X位置
                        leftX = self.ItemInnerSpacingX 
                        if self.ItemAnchor == "center":
                            leftX = int((ItemWidth - ItemIconWidth - ItemTextW)/2)
                        elif self.ItemAnchor == "right":
                            leftX = ItemWidth - self.ItemInnerSpacingX - ItemIconWidth - ItemTextW
                        ItemButton.create_text(leftX,centerY, font=self.ItemFont_Click,anchor=tkinter.W,fill=self.ItemFGColor_Click,text=ItemText,tag='title') 
                        ItemButton.create_image(leftX + ItemIconWidth,centerY,anchor=tkinter.W,image=ItemPTIconImage,tag="icon")
                    elif self.ItemCompound == 'top':
                        ContentWidth = ItemTextW
                        if ItemTextW < ItemIconWidth:
                            ContentWidth = ItemIconWidth
                        #跟据锚点位置计算X位置
                        centerX = self.ItemInnerSpacingX + int(ContentWidth/2)
                        if self.ItemAnchor == "center":
                            centerX = int(ItemWidth/2)
                        elif self.ItemAnchor == "right":
                            centerX = ItemWidth - self.ItemInnerSpacingX - int(ContentWidth/2)
                        ItemButton.create_image(centerX,self.ItemInnerSpacingY,anchor=tkinter.N,image=ItemPTIconImage,tag="icon")
                        ItemButton.create_text(centerX,self.ItemInnerSpacingY + ItemIconHeight, font=self.ItemFont_Click,anchor=tkinter.N,fill=self.ItemFGColor_Click,text=ItemText,tag='title') 
                    elif self.ItemCompound == 'bottom':
                        ContentWidth = ItemTextW
                        if ItemTextW < ItemIconWidth:
                            ContentWidth = ItemIconWidth
                        #跟据锚点位置计算X位置
                        centerX = self.ItemInnerSpacingX + int(ContentWidth/2)
                        if self.ItemAnchor == "center":
                            centerX = int(ItemWidth/2)
                        elif self.ItemAnchor == "right":
                            centerX = ItemWidth - self.ItemInnerSpacingX - int(ContentWidth/2)
                        ItemButton.create_text(centerX,ItemHeight - self.ItemInnerSpacingY-ItemIconHeight - ItemTextH, font=self.ItemFont_Click,anchor=tkinter.N,fill=self.ItemFGColor_Click,text=ItemText,tag='title') 
                        ItemButton.create_image(centerX,ItemHeight - self.ItemInnerSpacingY-ItemIconHeight ,anchor=tkinter.N,image=ItemPTIconImage,tag="icon")
                    elif self.ItemCompound == 'center':
                        ItemButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=ItemPTIconImage,tag="icon")
                        ItemButton.create_text(centerX,centerY, font=self.ItemFont_Click,anchor=tkinter.CENTER,fill=self.ItemFGColor_Click,text=ItemText,tag='title') 
                    else:
                        ItemButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=ItemPTIconImage,tag="icon")
                else:
                    #跟据锚点位置计算X位置
                    leftX = self.ItemInnerSpacingX 
                    if self.ItemAnchor == "center":
                        leftX = int((ItemWidth - ItemTextW)/2)
                    elif self.ItemAnchor == "right":
                        leftX = ItemWidth - self.ItemInnerSpacingX - ItemTextW
                    ItemButton.create_text(leftX,centerY, font=self.ItemFont_Click,anchor=tkinter.W,fill=self.ItemFGColor_Click,text=ItemText,tag='title')  
            elif ItemState == "Hover":
                if self.ItemBGColor_Hover:
                    ItemButton.configure(bg = self.ItemBGColor_Hover)
                ItemButton.delete('all')
                if self.ItemPTImage:
                    ItemButton.create_image(0,0,anchor=tkinter.NW,image=self.ItemPTImage,tag="bgimg")
                #图标
                if ItemPTIconImage:
                    if self.ItemCompound == 'left':
                        #跟据锚点位置计算X位置
                        leftX = self.ItemInnerSpacingX 
                        if self.ItemAnchor == "center":
                            leftX = int((ItemWidth - ItemIconWidth - ItemTextW)/2)
                        elif self.ItemAnchor == "right":
                            leftX = ItemWidth - self.ItemInnerSpacingX - ItemIconWidth - ItemTextW
                        ItemButton.create_image(leftX ,centerY,anchor=tkinter.W,image=ItemPTIconImage,tag="icon")
                        ItemButton.create_text(leftX + ItemIconWidth,centerY, font=self.ItemFont_Hover,anchor=tkinter.W,fill=self.ItemFGColor_Hover,text=ItemText,tag='title') 
                    elif self.ItemCompound == 'right':
                        #跟据锚点位置计算X位置
                        leftX = self.ItemInnerSpacingX 
                        if self.ItemAnchor == "center":
                            leftX = int((ItemWidth - ItemIconWidth - ItemTextW)/2)
                        elif self.ItemAnchor == "right":
                            leftX = ItemWidth - self.ItemInnerSpacingX - ItemIconWidth - ItemTextW
                        ItemButton.create_text(leftX,centerY, font=self.ItemFont_Hover,anchor=tkinter.W,fill=self.ItemFGColor_Hover,text=ItemText,tag='title') 
                        ItemButton.create_image(leftX + ItemIconWidth,centerY,anchor=tkinter.W,image=ItemPTIconImage,tag="icon")
                    elif self.ItemCompound == 'top':
                        ContentWidth = ItemTextW
                        if ItemTextW < ItemIconWidth:
                            ContentWidth = ItemIconWidth
                        #跟据锚点位置计算X位置
                        centerX = self.ItemInnerSpacingX + int(ContentWidth/2)
                        if self.ItemAnchor == "center":
                            centerX = int(ItemWidth/2)
                        elif self.ItemAnchor == "right":
                            centerX = ItemWidth - self.ItemInnerSpacingX - int(ContentWidth/2)
                        ItemButton.create_image(centerX,self.ItemInnerSpacingY,anchor=tkinter.N,image=ItemPTIconImage,tag="icon")
                        ItemButton.create_text(centerX,self.ItemInnerSpacingY + ItemIconHeight, font=self.ItemFont_Hover,anchor=tkinter.N,fill=self.ItemFGColor_Hover,text=ItemText,tag='title') 
                    elif self.ItemCompound == 'bottom':
                        ContentWidth = ItemTextW
                        if ItemTextW < ItemIconWidth:
                            ContentWidth = ItemIconWidth
                        #跟据锚点位置计算X位置
                        centerX = self.ItemInnerSpacingX + int(ContentWidth/2)
                        if self.ItemAnchor == "center":
                            centerX = int(ItemWidth/2)
                        elif self.ItemAnchor == "right":
                            centerX = ItemWidth - self.ItemInnerSpacingX - int(ContentWidth/2)
                        ItemButton.create_text(centerX,ItemHeight - self.ItemInnerSpacingY-ItemIconHeight - ItemTextH, font=self.ItemFont_Hover,anchor=tkinter.N,fill=self.ItemFGColor_Hover,text=ItemText,tag='title') 
                        ItemButton.create_image(centerX,ItemHeight - self.ItemInnerSpacingY-ItemIconHeight ,anchor=tkinter.N,image=ItemPTIconImage,tag="icon")
                    elif self.ItemCompound == 'center':
                        ItemButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=ItemPTIconImage,tag="icon")
                        ItemButton.create_text(centerX,centerY, font=self.ItemFont_Hover,anchor=tkinter.CENTER,fill=self.ItemFGColor_Hover,text=ItemText,tag='title') 
                    else:
                        ItemButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=ItemPTIconImage,tag="icon")
                else:
                    #跟据锚点位置计算X位置
                    leftX = self.ItemInnerSpacingX 
                    if self.ItemAnchor == "center":
                        leftX = int(ItemWidth - ItemTextW)/2
                    elif self.ItemAnchor == "right":
                        leftX = ItemWidth - self.ItemInnerSpacingX - ItemTextW
                    ItemButton.create_text(leftX,centerY, font=self.ItemFont_Hover,anchor=tkinter.W,fill=self.ItemFGColor_Hover,text=ItemText,tag='title')  
            else:
                if self.ItemBGColor:
                    ItemButton.configure(bg = self.ItemBGColor)
                ItemButton.delete('all')
                if self.ItemPTImage:
                    ItemButton.create_image(0,0,anchor=tkinter.NW,image=self.ItemPTImage,tag="bgimg")
                #图标
                if ItemPTIconImage:
                    if self.ItemCompound == 'left':
                        #跟据锚点位置计算X位置
                        leftX = self.ItemInnerSpacingX 
                        if self.ItemAnchor == "center":
                            leftX = int((ItemWidth - ItemIconWidth - ItemTextW)/2)
                        elif self.ItemAnchor == "right":
                            leftX = ItemWidth - self.ItemInnerSpacingX - ItemIconWidth - ItemTextW
                        ItemButton.create_image(leftX ,centerY,anchor=tkinter.W,image=ItemPTIconImage,tag="icon")
                        ItemButton.create_text(leftX + ItemIconWidth,centerY, font=self.ItemFont,anchor=tkinter.W,fill=self.ItemFGColor,text=ItemText,tag='title') 
                    elif self.ItemCompound == 'right':
                        #跟据锚点位置计算X位置
                        leftX = self.ItemInnerSpacingX 
                        if self.ItemAnchor == "center":
                            leftX = int((ItemWidth - ItemIconWidth - ItemTextW)/2)
                        elif self.ItemAnchor == "right":
                            leftX = ItemWidth - self.ItemInnerSpacingX - ItemIconWidth - ItemTextW
                        ItemButton.create_text(leftX,centerY, font=self.ItemFont,anchor=tkinter.W,fill=self.ItemFGColor,text=ItemText,tag='title') 
                        ItemButton.create_image(leftX + ItemIconWidth,centerY,anchor=tkinter.W,image=ItemPTIconImage,tag="icon")
                    elif self.ItemCompound == 'top':
                        ContentWidth = ItemTextW
                        if ItemTextW < ItemIconWidth:
                            ContentWidth = ItemIconWidth
                        #跟据锚点位置计算X位置
                        centerX = self.ItemInnerSpacingX + int(ContentWidth/2)
                        if self.ItemAnchor == "center":
                            centerX = int(ItemWidth/2)
                        elif self.ItemAnchor == "right":
                            centerX = ItemWidth - self.ItemInnerSpacingX - int(ContentWidth/2)
                        ItemButton.create_image(centerX,self.ItemInnerSpacingY,anchor=tkinter.N,image=ItemPTIconImage,tag="icon")
                        ItemButton.create_text(centerX,self.ItemInnerSpacingY + ItemIconHeight, font=self.ItemFont,anchor=tkinter.N,fill=self.ItemFGColor,text=ItemText,tag='title') 
                    elif self.ItemCompound == 'bottom':
                        ContentWidth = ItemTextW
                        if ItemTextW < ItemIconWidth:
                            ContentWidth = ItemIconWidth
                        #跟据锚点位置计算X位置
                        centerX = self.ItemInnerSpacingX + int(ContentWidth/2)
                        if self.ItemAnchor == "center":
                            centerX = int(ItemWidth/2)
                        elif self.ItemAnchor == "right":
                            centerX = ItemWidth - self.ItemInnerSpacingX - int(ContentWidth/2)
                        ItemButton.create_text(centerX,ItemHeight - self.ItemInnerSpacingY-ItemIconHeight - ItemTextH, font=self.ItemFont,anchor=tkinter.N,fill=self.ItemFGColor,text=ItemText,tag='title') 
                        ItemButton.create_image(centerX,ItemHeight - self.ItemInnerSpacingY-ItemIconHeight ,anchor=tkinter.N,image=ItemPTIconImage,tag="icon")
                    elif self.ItemCompound == 'center':
                        ItemButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=ItemPTIconImage,tag="icon")
                        ItemButton.create_text(centerX,centerY, font=self.ItemFont,anchor=tkinter.CENTER,fill=self.ItemFGColor,text=ItemText,tag='title') 
                    else:
                        ItemButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=ItemPTIconImage,tag="icon")
                else:
                    #跟据锚点位置计算X位置
                    leftX = self.ItemInnerSpacingX 
                    if self.ItemAnchor == "center":
                        leftX = int((ItemWidth - ItemTextW)/2)
                    elif self.ItemAnchor == "right":
                        leftX = ItemWidth - self.ItemInnerSpacingX - ItemTextW
                    ItemButton.create_text(leftX,centerY, font=self.ItemFont,anchor=tkinter.W,fill=self.ItemFGColor,text=ItemText,tag='title')  
    #展开
    def Redraw(self):
        canvasW = self.Canvas.winfo_width()
        canvasH = self.Canvas.winfo_height()
        if canvasW == 1 and canvasH == 1:
            canvasW = 140
            canvasH = 200
        TopY = self.TitleSpacingY
        TitleIndex = 0
        for subMenu in self.MenuArray:
            itemList = subMenu[2]
            isExpand = subMenu[3] 
            subMenuButton = subMenu[4]
            if subMenuButton is None:
                continue
            subMenuHandle = subMenu[5]
            TitleX = self.TitleSpacingX
            TitleY = TopY
            TitleWidth = self.GetTitleWidth(TitleIndex)
            TitleHeight = self.GetTitleHeight(TitleIndex)
            if self.SelectedItem == subMenuButton:
                self.RedrawTitle(TitleIndex,TitleState='Click')
            else:
                self.RedrawTitle(TitleIndex,TitleState='Normal')
            self.Canvas.coords(subMenuHandle,TitleX,TitleY)
            self.Canvas.itemconfig(subMenuHandle,width=TitleWidth,height=TitleHeight)
            TopY = TopY + self.GetTitleHeight(TitleIndex) + self.TitleSpacingY
            if type(subMenu[2]) == type([]):
                if isExpand == True:
                    # if self.ExpandChar != '' and itemList:
                    #     subMenuButton.delete('expand')
                    #     subMenuButton.create_text(TitleWidth - self.TitleSpacingX ,int(self.TitleHeight/2), font=self.TitleFont,anchor=tkinter.E,fill=self.TitleFGColor,text=self.ExpandCharDict[self.ExpandChar][0],tag='expand')  
                    ItemIndex = 0
                    for item in itemList:
                        itemButton = item[4]
                        itemHandle = item[5]
                        ItemX = self.ItemSpacingX
                        ItemY = TopY
                        ItemWidth = self.GetItemWidth(itemList,ItemIndex)
                        ItemHeight = self.GetItemHeight(itemList,ItemIndex)
                        if self.SelectedItem == itemButton:
                            self.RedrawItem(itemList,ItemIndex,ItemState='Click')
                        else:
                            self.RedrawItem(itemList,ItemIndex,ItemState='Normal')
                        itemButton.place(x=ItemX,y=ItemY,width=ItemWidth,height=ItemHeight)
                        self.Canvas.coords(itemHandle,ItemX,ItemY)
                        self.Canvas.itemconfig(itemHandle,width=ItemWidth,height=ItemHeight)
                        TopY = TopY + self.GetItemHeight(itemList,ItemIndex) + self.ItemSpacingY 
                        ItemIndex = ItemIndex + 1
                    TopY = TopY + self.TitleSpacingY 
                else:
                    # if self.ExpandChar != '' and itemList:
                    #     subMenuButton.delete('expand')
                    #     subMenuButton.create_text(buttonW - self.TitleSpacingX ,int(self.TitleHeight/2), font=self.TitleFont,anchor=tkinter.E,fill=self.TitleFGColor,text=self.ExpandCharDict[self.ExpandChar][1],tag='expand')  
                    for item in itemList:
                        itemButton = item[4]
                        itemHandle = item[5]
                        itemButton.place_forget()
                        self.Canvas.coords(itemHandle,-999,-999)
                        self.Canvas.itemconfig(itemHandle,width=0,height=0)
            TitleIndex = TitleIndex + 1 
    #点击展开或收缩
    def ClickItem(self,itemName,itemPage=''):
        print("ClickItem:"+itemName+" "+itemPage)
        if self.ListMenuCallBackFunction:
            self.ListMenuCallBackFunction(self.ListMenuUIName,self.ListMenuName,itemName,itemPage)
    #设置点击确定时的回调函数
    def SetListMenuCallBackFunction(self,callBackFun,uiName,widgetName):
        self.ListMenuCallBackFunction = callBackFun
        self.ListMenuUIName = uiName
        self.ListMenuName = widgetName
        self.Redraw()
    #重置
    def ResetSelectedItem(self):
        for subMenu in self.MenuArray:
            if subMenu[4] == self.SelectedItem:
                if self.TitleBGColor:
                    self.SelectedItem.configure(bg = self.TitleBGColor)
                if self.TitleFGColor:
                    self.SelectedItem.itemconfig('title',fill=self.TitleFGColor)
                    self.SelectedItem.itemconfig('expand',fill=self.TitleFGColor)
                if self.TitleFont:
                    self.SelectedItem.itemconfig('title',font = self.TitleFont)
                    return 
            if type(subMenu[2]) == type([]):
                for items in subMenu[2]:
                    if items[4] == self.SelectedItem:
                        if self.ItemBGColor:
                            self.SelectedItem.configure(bg = self.ItemBGColor)
                        if self.ItemFGColor:
                            self.SelectedItem.itemconfig('title',fill=self.ItemFGColor)
                        if self.ItemFont:
                            self.SelectedItem.itemconfig('title',font = self.ItemFont)
                        return 
#导航橱窗
class SwitchPage:
    def __init__(self, canvas):
        self.ParentCanvas = canvas
        self.ItemArray = []
        self.SwitchDelay = 4000
        self.CurrentIndex = -1
        self.BarButtonRadius = 6
        self.BarButtonSpacingX = 6
        self.BarButtonSpacingY = 2
        self.BarCurrButtonWidth = 15
        self.BarLeft = 200
        self.BarTop = -40
        self.TitleFont = tkinter.font.Font(family="Arial", size=12,weight='bold',slant='roman',underline=0,overstrike=0)
        self.TitleLeft = 0
        self.TitleTop = 0
        self.MouseEnter = False
        self.TitleColor = '#FFFFFF'
        self.PageClickCallBackFunction = None
        self.uiName = None
        self.widgetName = None
        self.Canvas_width = 350
        self.Canvas_height = 200
        self.Canvas_BGColor = '#FFFFFF'
        self.Canvas = tkinter.Canvas(self.ParentCanvas,width=self.Canvas_width,height=self.Canvas_height,bg = self.Canvas_BGColor ,highlightthickness=0,bd=0)
        self.Canvas.pack(expand=1, fill='both')
        self.Canvas.bind('<Configure>',self.Configure)
    #取得当前画布
    def GetWidget(self):
        return self.Canvas
    #传递绑定事件
    def bind(self,EventName,callBack):
        if self.Canvas:
            self.Canvas.bind(EventName,callBack)
    #窗口大小变化
    def Configure(self,event):
        self.Canvas_width = event.width
        self.Canvas_height = event.height
        self.Rebuild()
    #取得边框样式
    def Hide(self,layout="place"):
        if layout == "pack":
            self.Canvas.pack_forget()
        elif layout == "grid":
            self.Canvas.grid_forget()
        else:
            self.Canvas.place_forget()
    #传递pack_forget事件
    def pack_forget(self):
        if self.Canvas:
            self.Canvas.pack_forget()
    #传递grid_forget事件
    def grid_forget(self):
        if self.Canvas:
            self.Canvas.grid_forget()
    #传递place_forget事件
    def place_forget(self):
        if self.Canvas:
            self.Canvas.place_forget()
    #设置当前画布的背景色
    def SetBGColor(self,color):
        self.Canvas_BGColor = color
        self.Canvas.configure(bg = self.Canvas_BGColor)
    #取得当前画布的背景色
    def GetBGColor(self):
        return self.Canvas_BGColor
    #设置当前选中页
    def SetCurrentIndex(self,index):
        PageCount = len(self.ItemArray)
        if PageCount > index and index <= 0:
            self.CurrentIndex = index
        self.Redraw()
    #取得当前选中页
    def GetCurrentIndex(self):
        return self.CurrentIndex
    #鼠标进入和离开时的处理
    def onItemEnter(self,event):
        event.widget.configure(cursor='hand2')
        self.MouseEnter = True
    #鼠标离开时的处理
    def onItemLeave(self,event):
        try:
            event.widget.configure(cursor='arrow')
            self.MouseEnter = False
        except:
            pass
    #鼠标点击时的处理
    def onItemClick(self,event):
        ButtonInfo = self.ItemArray[self.CurrentIndex]
        if self.PageClickCallBackFunction:
            self.PageClickCallBackFunction(self.uiName,self.widgetName,self.CurrentIndex,ButtonInfo[0],ButtonInfo[2])
    #鼠标点击圆点时的处理
    def onPointClick(self,event,pageIndex):
        self.CurrentIndex = pageIndex
        self.Redraw()
    #上一页
    def goLast(self,event):
        PageCount = len(self.ItemArray)
        if PageCount > 0:
            self.CurrentIndex = self.CurrentIndex - 1 + PageCount
            self.CurrentIndex = self.CurrentIndex % PageCount
        self.Redraw()
    #下一页
    def goNext(self,event):
        PageCount = len(self.ItemArray)
        if PageCount > 0:
            self.CurrentIndex = self.CurrentIndex + 1
            self.CurrentIndex = self.CurrentIndex % PageCount
        self.Redraw()
    #取得菜单数据数组
    def GetItemArray(self):
        return self.ItemArray
    #取得菜单数据数组的复制
    def GetItemArray_Copy(self):
        ItemArray = []
        for ButtonInfo in self.ItemArray:
            ItemArray.append([ButtonInfo[0],ButtonInfo[1],ButtonInfo[2]])
        return ItemArray
    #清空所有
    def Clear(self):
        self.Canvas.delete("all")
        self.ItemArray.clear()
        self.CurrentIndex = -1
    #设置标题文字的左边位置
    def SetTitleLeft(self,left):
        self.TitleLeft = left
    #取得标题文字的左边位置
    def GetTitleLeft(self):
        return self.TitleLeft
    #设置标题文字的上部位置
    def SetTitleTop(self,top):
        self.TitleTop = top
    #取得标题文字的上部位置
    def GetTitleTop(self):
        return self.TitleTop
    #设置标题文字的颜色
    def SetTitleColor(self,color):
        self.TitleColor = color
    #取得标题文字的颜色
    def GetTitleColor(self):
        return self.TitleColor
    #设置当前进度条的X值
    def SetProgressBarLeft(self,left):
        self.BarLeft = int(left)
    #取得当前进度条的X值
    def GetProgressBarLeft(self):
        return self.BarLeft
    #设置当前进度条的Y值
    def SetProgressBarTop(self,top):
        self.BarTop = int(top)
    #取得当前进度条的Y值
    def GetProgressBarTop(self):
        return self.BarTop
    #设置当前进度栏里按钮圆点的半径
    def SetProgressBarButtonRadius(self,radius):
        self.BarButtonRadius = int(radius)
    #取得当前进度栏里按钮圆点的半径
    def GetProgressBarButtonRadius(self):
        return self.BarButtonRadius
    #设置当前进度栏里按钮之间的横向边距
    def SetProgressBarButtonSpacingX(self,spacingX):
        self.BarButtonSpacingX = int(spacingX)
    #取得当前进度栏里按钮之间的横向边距
    def GetProgressBarButtonSpacingX(self):
        return self.BarButtonSpacingX
    #设置当前进度栏里按钮之间的纵向边距
    def SetProgressBarButtonSpacingY(self,spacingY):
        self.BarButtonSpacingY = int(spacingY)
    #取得当前进度栏里按钮之间的纵向边距
    def GetProgressBarButtonSpacingY(self):
        return self.BarButtonSpacingY
    #设置当前进度栏里当前按钮的宽度
    def SetProgressBarCurrButtonWidth(self,width):
        self.BarCurrButtonWidth = int(width)
    #取得当前进度栏里当前按钮的宽度
    def GetProgressBarCurrButtonWidth(self):
        return self.BarCurrButtonWidth
    #设置点击确定时的回调函数
    def SetPageClickCallBackFunction(self,callBackFun,uiName,widgetName):
        self.PageClickCallBackFunction = callBackFun
        self.uiName = uiName
        self.widgetName = widgetName
    #增加一个页面项
    def AddPage(self,TitleText='',ImageFile='',ItemPage='',ItemIndex='end'):
        PageW = self.Canvas.winfo_width()
        if PageW == 1:
            PageW = 300
        PageH = self.Canvas.winfo_height()
        if PageH == 1:
            PageH = 240
        if ImageFile:
            filePath = ImageFile
            if filePath and os.path.exists(filePath) == False:
                filePath = os.path.join(G_ExeDir,ImageFile)
                if os.path.exists(filePath) == False:
                    filePath = os.path.join(G_ResDir,ImageFile)
            if os.path.exists(filePath) == True:
                try:
                    Image_Temp = Image.open(filePath).convert('RGBA')
                    Image_Resize = Image_Temp.resize((PageW, PageH),Image.LANCZOS)
                    Photo_Image = ImageTk.PhotoImage(Image_Resize)
                    if ItemIndex == "end" or  ItemIndex == -1:
                        self.CurrentIndex = len(self.ItemArray)
                        self.ItemArray.append([TitleText,ImageFile,ItemPage,Photo_Image])
                    else:
                        if type(ItemIndex) == type(""):
                            if ItemIndex.isdigit() == True:
                                ItemIndex = int(ItemIndex)
                            else:
                                ItemIndex = len(self.ItemArray)
                        self.CurrentIndex = ItemIndex
                        self.ItemArray.insert(ItemIndex,[TitleText,ImageFile,ItemPage,Photo_Image])
                except Exception as ex:
                    tkinter.messagebox.showwarning("error",ex)
    #删除指定页面项
    def DelPage(self,index):
        if index < len(self.ItemArray):
            self.ItemArray.pop(index)
        self.Redraw()
    #重建
    def Rebuild(self):
        OldItemArray = self.GetItemArray_Copy()
        self.Clear()
        for ItemInfo in OldItemArray:
            self.AddPage(TitleText=ItemInfo[0],ImageFile=ItemInfo[1],ItemPage=ItemInfo[2])
        self.Redraw()
    #页面播放
    def Play(self,switchDelay = 3000):
        if self.MouseEnter == False:
            PageCount = len(self.ItemArray)
            if PageCount > 0:
                self.CurrentIndex = self.CurrentIndex + 1
                self.CurrentIndex = self.CurrentIndex % PageCount
            self.Redraw()
        self.SwitchDelay = switchDelay
        if self.SwitchDelay > 0:
            self.Canvas.after(self.SwitchDelay,self.Play)
    #展开
    def Redraw(self):
        PageW = self.Canvas.winfo_width()
        if PageW == 1:
            PageW = 300
        PageH = self.Canvas.winfo_height()
        if PageH == 1:
            PageH = 240
        ButtonIndex = 0
        self.Canvas.delete("all")
        for ButtonInfo in self.ItemArray:
            if self.CurrentIndex == ButtonIndex:
                self.Canvas.create_image(0,0,anchor=tkinter.NW,image=ButtonInfo[3],tag='image')
                if ButtonInfo[0] !='':
                    Left = self.TitleLeft
                    if Left < 0 :
                        Left = PageW + Left
                    Top  = self.TitleTop
                    if Top < 0 :
                        Top = PageH + Top
                    self.Canvas.create_text(Left,Top,font=self.TitleFont,anchor=tkinter.NW,fill=self.TitleColor,text=ButtonInfo[0],tag='title')
            ButtonIndex = ButtonIndex + 1
        self.Canvas.tag_bind('image','<Enter>',self.onItemEnter)
        self.Canvas.tag_bind('image','<Leave>',self.onItemLeave)
        self.Canvas.tag_bind('image','<Button-1>',self.onItemClick)
        BarWidth = ButtonIndex * self.BarButtonSpacingX + ButtonIndex * 2 * self.BarButtonRadius + self.BarCurrButtonWidth
        BarHeight = (self.BarButtonRadius + self.BarButtonSpacingY) * 2
        BarLeft = self.BarLeft
        if BarLeft < 0:
            BarLeft = PageW + BarLeft
        BarTop = self.BarTop
        if BarTop < 0:
            BarTop = PageH + BarTop
        BarBGColor = '#333333'
        self.Canvas.create_rectangle(BarLeft,BarTop,BarLeft + BarWidth,BarTop + BarHeight+1,fill=BarBGColor,width=0,tag="bar") 
        self.Canvas.create_oval(BarLeft-self.BarButtonSpacingX,BarTop,BarLeft + self.BarButtonSpacingX,BarTop + BarHeight,fill=BarBGColor,width=0,tag="bar") 
        self.Canvas.create_oval(BarLeft + BarWidth - self.BarButtonSpacingX,BarTop,BarLeft  + BarWidth + self.BarButtonSpacingX,BarTop + BarHeight,fill=BarBGColor,width=0,tag="bar") 
        PointBGColor = '#FFFFFF'
        PointX = BarLeft
        PointY = BarTop + self.BarButtonSpacingY
        PointW = 2 * self.BarButtonRadius
        PointH = 2 * self.BarButtonRadius
        ButtonIndex = 0
        for ButtonInfo in self.ItemArray:
            TagName = str("point_%d"%ButtonIndex)
            self.Canvas.create_oval(PointX,PointY,PointX + PointW ,PointY + PointH,fill=PointBGColor,width=0,tag=TagName) 
            if self.CurrentIndex == ButtonIndex:
                self.Canvas.create_rectangle(PointX + self.BarButtonRadius,PointY,PointX + self.BarButtonRadius + self.BarCurrButtonWidth,PointY + PointH+1,fill=PointBGColor,width=0,tag=TagName) 
                PointX = PointX + self.BarButtonRadius + self.BarCurrButtonWidth
                self.Canvas.create_oval(PointX - self.BarButtonRadius,PointY,PointX + self.BarButtonRadius ,PointY + PointH,fill=PointBGColor,width=0,tag=TagName) 
                PointX = PointX + self.BarButtonRadius + self.BarButtonSpacingX
            else:
                PointX = PointX + PointW + self.BarButtonSpacingX
            #
            self.Canvas.tag_bind(TagName,'<Enter>',self.onItemEnter)
            self.Canvas.tag_bind(TagName,'<Leave>',self.onItemLeave)
            self.Canvas.tag_bind(TagName,'<Button-1>',partial(self.onPointClick,pageIndex=ButtonIndex))
            ButtonIndex = ButtonIndex + 1
        self.Canvas.create_text(30,PageH/2,font=("Arial",36),anchor=tkinter.CENTER,fill="#FFFFFF",text="〈",tag='last')
        self.Canvas.tag_bind('last','<Enter>',self.onItemEnter)
        self.Canvas.tag_bind('last','<Leave>',self.onItemLeave)
        self.Canvas.tag_bind('last','<Button-1>',self.goLast)
        self.Canvas.create_text(PageW-40,PageH/2,font=("Arial",36),anchor=tkinter.CENTER,fill="#FFFFFF",text="〉",tag='next')
        self.Canvas.tag_bind('next','<Enter>',self.onItemEnter)
        self.Canvas.tag_bind('next','<Leave>',self.onItemLeave)
        self.Canvas.tag_bind('next','<Button-1>',self.goNext)
#列表页
class ShowCase:
    def __init__(self, canvas):
        self.ParentCanvas = canvas
        self.ItemArray = []
        self.CanvasBGColor = '#EFEFEF'
        self.ItemBGColor = '#EFEFEF'
        self.ItemFGColor = '#000000'
        self.ItemFont = tkinter.font.Font(family="Arial", size=10,weight='normal',slant='roman',underline=0,overstrike=0)
        self.ItemBGColor_Hover = '#FFFFFF'
        self.ItemFGColor_Hover = '#000000'
        self.ItemFont_Hover = tkinter.font.Font(family="Arial", size=10,weight='normal',slant='roman',underline=0,overstrike=0)
        self.ItemBGColor_Click = '#FFFFFF'
        self.ItemFGColor_Click = '#0000FF'
        self.ItemFont_Click = tkinter.font.Font(family="Arial", size=10,weight='bold',slant='roman',underline=0,overstrike=0)
        self.ItemWidth = 220
        self.ItemHeight = 60
        self.ItemSpacing = 10
        self.ItemInnerSpacing = 0
        self.CurrentIndex = -1
        self.Canvas_width = 280
        self.Canvas_height = 400
        self.Canvas = tkinter.Canvas(self.ParentCanvas,width=self.Canvas_width,height=self.Canvas_height,bg = self.CanvasBGColor,highlightthickness=0,bd=0)
        self.Canvas.pack(side=tkinter.TOP,fill=tkinter.BOTH,expand=True)
        self.Canvas.bind('<Configure>',self.Configure)
        self.Canvas.bind('<MouseWheel>',self.OnMouseWheel)  
        self.CanvasScrollBar = tkinter.ttk.Scrollbar(self.Canvas,orient=tkinter.VERTICAL)
        self.CanvasScrollBar.pack(side=tkinter.RIGHT,fill=tkinter.Y)
        self.CanvasScrollBar.config(command=self.Canvas.yview)
        self.Canvas.config(yscrollcommand=self.CanvasScrollBar.set)
        self.NavigationCallBackFunction = None
        self.NavigationUIName = None
        self.NavigationName =  None
    def Configure(self,event):
        self.Canvas_width = event.width
        self.Canvas_height = event.height
        self.Redraw()
    #鼠标滚轮
    def OnMouseWheel(self,event):
        if event.delta > 0:
            self.Canvas.yview("scroll",-1,"units")
        else:
            self.Canvas.yview("scroll",1,"units")
        return "break"
    #取得所属窗体
    def GetWidget(self):
        return self.Canvas
    #设置属性
    def configure(self,**kw):
        self.Canvas.configure(kw)
    #传递绑定事件
    def bind(self,EventName,callBack):
        if self.Canvas:
            self.Canvas.bind(EventName,callBack)
    #取得边框样式
    def Hide(self,layout="place"):
        if layout == "pack":
            self.Canvas.pack_forget()
        elif layout == "grid":
            self.Canvas.grid_forget()
        else:
            self.Canvas.place_forget()
    #传递pack_forget事件
    def pack_forget(self):
        if self.Canvas:
            self.Canvas.pack_forget()
    #传递grid_forget事件
    def grid_forget(self):
        if self.Canvas:
            self.Canvas.grid_forget()
    #传递place_forget事件
    def place_forget(self):
        if self.Canvas:
            self.Canvas.place_forget()
    #设置切换事件回调函数
    def SetClickItemCallBackFunction(self,callBack,uiName,widgetName):
        self.NavigationCallBackFunction = callBack 
        self.NavigationUIName = uiName
        self.NavigationName = widgetName
    #设置选项宽度
    def SetItemWidth(self,width):
        self.ItemWidth = width
        self.Redraw()
    #取得选项宽度
    def GetItemWidth(self):
        return self.ItemWidth
    #设置选项高度
    def SetItemHeight(self,height):
        self.ItemHeight = height
        self.Redraw()
    #取得选项高度
    def GetItemHeight(self):
        return self.ItemHeight
    #设置图标的位置
    def SetCompound(self,compound):
        self.Compound = compound
        self.Redraw()
    #设置选项的间跑
    def SetItemSpacing(self,spacing):
        self.ItemSpacing = spacing
        self.Redraw()
    #取得选项的间隔
    def GetItemSpacing(self):
        return self.ItemSpacing
    #设置选项的间跑
    def SetItemInnerSpacing(self,spacing):
        self.ItemInnerSpacing = spacing
        self.Redraw()
    #取得选项的间隔
    def GetItemInnerSpacing(self):
        return self.ItemInnerSpacing
    #取得对应Item的文本宽度
    def GetItemTextWidth(self,itemText):
        return self.ItemFont.measure(itemText) + 2 * self.ItemInnerSpacing
    #取得对应Item的文本高度
    def GetItemTextHeight(self):
        fontHeight = int(self.ItemFont.actual('size'))
        fontHeight = int(fontHeight*SCALE_FACTOR)  + int(5 * SCALE_FACTOR)  + 2 * self.ItemInnerSpacing
        return fontHeight
    #设置当前选中项
    def SetCurrentIndex(self,Index):
        ButtonIndex = 0
        for ButtonInfo in self.ItemArray:
            ButtonImageList = ButtonInfo[-1]
            if ButtonIndex == Index:
                self.RedrawItem(ButtonIndex,"Click")
                self.CurrentIndex = ButtonIndex
                if self.NavigationCallBackFunction:
                    ButtonText = ButtonInfo[0]
                    TargetPage = ButtonInfo[2]
                    self.NavigationCallBackFunction(self.NavigationUIName,self.NavigationName,ButtonText,TargetPage)
            else:
                self.RedrawItem(ButtonIndex,"Normal")
            ButtonIndex = ButtonIndex + 1
    #取得当前选中项
    def GetCurrentIndex(self):
        return self.CurrentIndex
    #取得当前选中项文本
    def GetCurrentItemText(self):
        if self.CurrentIndex >= 0 and self.CurrentIndex < len(self.ItemArray):
           ButtonInfo = self.ItemArray[self.CurrentIndex]
           return ButtonInfo[0]
        return ""
    #取得当前选中项的值
    def GetCurrentItemValue(self):
        if self.CurrentIndex >= 0 and self.CurrentIndex < len(self.ItemArray):
           ButtonInfo = self.ItemArray[self.CurrentIndex]
           return ButtonInfo[2]
        return ""
    #鼠标进入和离开时的处理
    def onItemEnter(self,event):
        event.widget.configure(cursor='hand2')
        ButtonIndex = 0
        for ButtonInfo in self.ItemArray:
            if ButtonIndex != self.CurrentIndex:
                if ButtonInfo[3] == event.widget:
                    self.RedrawItem(ButtonIndex,"Hover")
            ButtonIndex = ButtonIndex + 1
    def onItemLeave(self,event):
        try:
            event.widget.configure(cursor='arrow')
            ButtonIndex = 0
            for ButtonInfo in self.ItemArray:
                if ButtonIndex != self.CurrentIndex:
                    if ButtonInfo[3] == event.widget:
                        self.RedrawItem(ButtonIndex,"Normal")
                ButtonIndex = ButtonIndex + 1
        except:
            pass
    def onItemClick(self,event):
        ButtonIndex = 0
        for ButtonInfo in self.ItemArray:
            ButtonImageList = ButtonInfo[-1]
            if ButtonInfo[3] == event.widget:
                self.RedrawItem(ButtonIndex,"Click")
                self.CurrentIndex = ButtonIndex
                if self.NavigationCallBackFunction:
                    ButtonText = ButtonInfo[0]
                    TargetPage = ButtonInfo[2]
                    self.NavigationCallBackFunction(self.NavigationUIName,self.NavigationName,ButtonText,TargetPage)
            else:
                self.RedrawItem(ButtonIndex,"Normal")
            ButtonIndex = ButtonIndex + 1
    #取得菜单数据数组
    def GetItemArray(self):
        return self.ItemArray
    #取得菜单数据数组的复制
    def GetItemArray_Copy(self):
        ItemArray = []
        for ButtonInfo in self.ItemArray:
            ItemArray.append([ButtonInfo[0],ButtonInfo[1],ButtonInfo[2],ButtonInfo[3],ButtonInfo[4],ButtonInfo[5]])
        return ItemArray
    #清空所有
    def Clear(self):
        for ButtonInfo in self.ItemArray:
            LabelButton = ButtonInfo[3]
            if LabelButton:
                LabelButton.destroy()
        self.ItemArray.clear()
        self.CurrentIndex = -1
    #设置当前画布的背景色
    def SetBGColor(self,color):
        self.CanvasBGColor = color
        self.Canvas.configure(bg = color)
    #取得当前画布的背景色
    def GetBGColor(self):
        return self.CanvasBGColor
    #设置标题栏的背景色
    def SetItemBGColor(self,color):
        self.ItemBGColor = color
        for ItemInfo in self.ItemArray:
            ItemButton = ItemInfo[3]
            ItemButton.configure(bg = color)
    #取得标题栏的背景色
    def GetItemBGColor(self):
        return self.ItemBGColor
    #设置鼠标悬停在标题栏上的背景色
    def SetItemBGColor_Hover(self,color):
        self.ItemBGColor_Hover = color
    #取得鼠标悬停在标题栏上的背景色
    def GetItemBGColor_Hover(self):
        return self.ItemBGColor_Hover
    #设置鼠点击击标题栏时的背景色
    def SetItemBGColor_Click(self,color):
        self.ItemBGColor_Click = color
        if self.CurrentIndex >= 0 and self.CurrentIndex < len(self.ItemArray):
            ItemInfo = self.ItemArray[self.CurrentIndex]
            ItemButton = ItemInfo[3]
            ItemButton.configure(bg = color)
    #取得鼠点击击标题栏时的背景色
    def GetItemBGColor_Click(self):
        return self.ItemBGColor_Click
    #设置标题栏的文字色
    def SetItemFGColor(self,color):
        self.ItemFGColor = color
        self.Redraw()
    #取得标题栏的文字色
    def GetItemFGColor(self):
        return self.ItemFGColor
    #设置鼠标悬停在标题栏上的背景色
    def SetItemFGColor_Hover(self,color):
        self.ItemFGColor_Hover = color
    #取得鼠标悬停在标题栏上的背景色
    def GetItemFGColor_Hover(self):
        return self.ItemFGColor_Hover
    #设置鼠点击击标题栏时的背景色
    def SetItemFGColor_Click(self,color):
        self.ItemFGColor_Click = color
        if self.CurrentIndex >= 0 and self.CurrentIndex < len(self.ItemArray):
            ItemInfo = self.ItemArray[self.CurrentIndex]
            ItemButton = ItemInfo[3]
            ItemButton.configure(fg = color)
    #取得鼠点击击标题栏时的背景色
    def GetItemFGColor_Click(self):
        return self.ItemFGColor_Click
    #设置标题栏的字体
    def SetItemFont(self,font,redraw = True):
        self.ItemFont = font
        fontHeight = int(self.ItemFont.actual('size'))
        fontHeight = int(fontHeight*SCALE_FACTOR)  + int(5 * SCALE_FACTOR) 
        if fontHeight > self.ItemHeight:
            self.ItemHeight = fontHeight 
        if redraw:
            self.Redraw()
    #取得标题栏的字体
    def GetItemFont(self):
        return self.ItemFont
    #设置鼠标悬停在标题栏上的字体
    def SetItemFont_Hover(self,font):
        self.ItemFont_Hover = font
        fontHeight = int(self.ItemFont_Hover.actual('size'))
        fontHeight = int(fontHeight*SCALE_FACTOR)  + int(5 * SCALE_FACTOR) 
        if fontHeight > self.ItemHeight:
            self.ItemHeight = fontHeight 
    #取得鼠标悬停在标题栏上的字体
    def GetItemFont_Hover(self):
        return self.ItemFont_Hover
    #设置鼠点击击标题栏时的字体
    def SetItemFont_Click(self,font):
        self.ItemFont_Click = font
        fontHeight = int(self.ItemFont_Click.actual('size'))
        fontHeight = int(fontHeight*SCALE_FACTOR)  + int(5 * SCALE_FACTOR) 
        if fontHeight > self.ItemHeight:
            self.ItemHeight = fontHeight 
    #取得鼠标悬停在标题栏上的字体
    def GetItemFont_Click(self):
        return self.ItemFont_Click
    #取得项的列数
    def GetItemColumns(self):
        return int(self.Canvas_width / (self.ItemWidth + self.ItemSpacing))
    #取得项的X位置
    def GetItemLeftX(self,ItemIndex):
        ItemColumns = self.GetItemColumns()
        if ItemColumns > 0:
            return self.ItemSpacing + (self.ItemWidth + self.ItemSpacing) * (ItemIndex % self.GetItemColumns())
        return self.ItemSpacing + (self.ItemWidth + self.ItemSpacing) * ItemIndex 
    #取得项的Y位置
    def GetItemTopY(self,ItemIndex):
        ItemColumns = self.GetItemColumns()
        if ItemColumns > 0:
            return self.ItemSpacing + (self.ItemHeight + self.ItemSpacing) * (ItemIndex // self.GetItemColumns())
        return self.ItemSpacing + (self.ItemHeight + self.ItemSpacing) * ItemIndex
    #增加一项
    def AddItem(self,ItemText='',ItemIcon='',ItemPage='',ItemIndex='end'):
        ButtonIndex = len(self.ItemArray)
        ItemX = self.GetItemLeftX(ButtonIndex)
        ItemY = self.GetItemTopY(ButtonIndex)
        ItemButton = tkinter.Canvas(self.Canvas,relief=tkinter.FLAT,bg = self.ItemBGColor,highlightthickness=0,bd=0)
        ItemButton.place(x = ItemX,y = ItemY,width = self.ItemWidth ,height = self.ItemHeight) 
        ItemButton.bind('<Enter>',self.onItemEnter)
        ItemButton.bind('<Leave>',self.onItemLeave)
        ItemButton.bind('<Button-1>',self.onItemClick)
        ItemButton.bind('<ButtonRelease-1>',self.onItemEnter)
        ItemButton.bind('<MouseWheel>',self.OnMouseWheel)
        buttonHandle = self.Canvas.create_window(ItemX,ItemY, window=ItemButton, anchor=tkinter.NW,tag="Item")
        self.Canvas.itemconfig(buttonHandle,width=self.ItemWidth,height=self.ItemHeight)
        ItemIconWidth = 0
        ItemIconHeight = 0
        ItemPTIconImage = None
        if ItemIcon:
            filePath = ItemIcon
            if filePath and os.path.exists(filePath) == False:
                filePath = os.path.join(G_ExeDir,ItemIcon)
                if os.path.exists(filePath) == False:
                    filePath = os.path.join(G_ResDir,ItemIcon)
            if filePath and os.path.exists(filePath) == True:
                try:
                    ItemImage = Image.open(filePath).convert('RGBA')
                    ItemPTIconImage = ImageTk.PhotoImage(ItemImage)
                except:
                    ItemPTIconImage = None
        if ItemIndex == "end" or  ItemIndex == -1:
            self.ItemArray.append([ItemText,ItemIcon,ItemPage,ItemButton,buttonHandle,ItemPTIconImage])
        else:
            if type(ItemIndex) == type(""):
                if ItemIndex.isdigit() == True:
                    ItemIndex = int(ItemIndex)
                else:
                    ItemIndex = len(self.ItemArray)
            self.ItemArray.insert(ItemIndex,[ItemText,ItemIcon,ItemPage,ItemButton,buttonHandle,ItemPTIconImage])
    #增加一项
    def AddItemUI(self,targetUIName='',params=None,ItemIndex='end'):
        ButtonIndex = len(self.ItemArray)
        ItemX = self.GetItemLeftX(ButtonIndex)
        ItemY = self.GetItemTopY(ButtonIndex)
        ItemButton = tkinter.Canvas(self.Canvas,relief=tkinter.FLAT,bg = self.ItemBGColor,highlightthickness=0,bd=0)
        ItemButton.place(x = ItemX,y = ItemY,width = self.ItemWidth ,height = self.ItemHeight) 
        ItemButton.bind('<Enter>',self.onItemEnter)
        ItemButton.bind('<Leave>',self.onItemLeave)
        ItemButton.bind('<Button-1>',self.onItemClick)
        ItemButton.bind('<ButtonRelease-1>',self.onItemEnter)
        ItemButton.bind('<MouseWheel>',self.OnMouseWheel)
        buttonHandle = self.Canvas.create_window(ItemX,ItemY, window=ItemButton, anchor=tkinter.NW,tag="Item")
        self.Canvas.itemconfig(buttonHandle,width=self.ItemWidth,height=self.ItemHeight)
        if ItemIndex == "end" or  ItemIndex == -1:
            self.ItemArray.append(['','','',ItemButton,buttonHandle,None])
        else:
            if type(ItemIndex) == type(""):
                if ItemIndex.isdigit() == True:
                    ItemIndex = int(ItemIndex)
                else:
                    ItemIndex = len(self.ItemArray)
            self.ItemArray.insert(ItemIndex,['','','',ItemButton,buttonHandle,None])
        self.LoadItemUI(ButtonIndex,targetUIName,params)
    #在对应项加载界面
    def LoadItemUI(self,ItemIndex=0,targetUIName='',params=None):
        if ItemIndex < len(self.ItemArray):
            ItemInfo = self.ItemArray[ItemIndex]
            ItemButton = ItemInfo[3]
            for child in ItemButton.winfo_children():
                child.destroy()
            import importlib
            from   importlib import import_module
            try:
                UIPath, UIFile = os.path.split(targetUIName)
                if UIPath.find(":") < 0:
                    UIPath = os.path.join(G_ExeDir,UIPath)
                UIName, extension = os.path.splitext(UIFile)
                import sys
                sys.path.append(UIPath)
                importModule = importlib.import_module(UIName)
                importModule = importlib.reload(importModule)
                if hasattr(importModule,"Fun") == True:
                    importModule.Fun.G_ExeDir = G_ExeDir
                    importModule.Fun.G_ResDir = G_ResDir
                    if hasattr(importModule,"EXUIControl") == True:
                        importModule.EXUIControl.G_ExeDir = G_ExeDir
                        importModule.EXUIControl.G_ResDir = G_ResDir
                if hasattr(importModule,UIName) == True:
                    uiClass = getattr(importModule,UIName)
                    uiDialog = uiClass(ItemButton,False,params)
                ItemInfo[0] = ''
                ItemInfo[1] = ''
                ItemInfo[2] = ''
                ItemInfo[5] = None
            except ModuleNotFoundError:
                FunLib.MessageBox("界面加载失败","提示")
    #删除标题
    def DelItem(self,index):
        if index < len(self.ItemArray):
            ButtonInfo = self.ItemArray[index]
            LabelButton = ButtonInfo[3]
            if LabelButton:
                LabelButton.destroy()
            self.ItemArray.pop(index)
        self.Redraw()
    #重建
    def Rebuild(self):
        OldItemArray = self.GetItemArray_Copy()
        self.Clear()
        for ItemInfo in OldItemArray:
            self.AddItem(ItemText=ItemInfo[0],ItemIcon=ItemInfo[1],ItemPage=ItemInfo[2])
        self.Redraw()
    #绘制一个按钮
    def RedrawItem(self,ItemIndex,ItemState='Normal'):
        if ItemIndex >= 0 and ItemIndex < len(self.ItemArray):
            ButtonInfo = self.ItemArray[ItemIndex]
            ItemText = ButtonInfo[0]
            ItemPTIconImage = ButtonInfo[5]
            ItemButton = ButtonInfo[3]
            ItemButtonHandle = ButtonInfo[4]
            self.Canvas.itemconfig(ItemButtonHandle,width=self.ItemWidth,height=self.ItemHeight)
            ItemWidth = self.ItemWidth + 2 * self.ItemInnerSpacing
            ItemHeight = self.ItemHeight + 2 * self.ItemInnerSpacing
            ItemTextW = self.GetItemTextWidth(ItemText)
            ItemTextH = self.GetItemTextHeight()
            ItemIconWidth = 0
            ItemIconHeight = 0
            if ItemPTIconImage:                
                ItemIconWidth = ItemPTIconImage.width() + self.ItemInnerSpacing
                ItemIconHeight = ItemPTIconImage.height() + self.ItemInnerSpacing
            centerX = int(ItemWidth/2)
            centerY = int(ItemHeight/2)
            if ItemState == "Click":
                if self.ItemBGColor_Click:
                    ItemButton.configure(bg = self.ItemBGColor_Click)
                ItemButton.delete('all')
                #图标
                if ItemPTIconImage:
                    if self.Compound == 'left':
                        x = self.ItemInnerSpacing
                        ItemButton.create_image(self.ItemInnerSpacing ,centerY,anchor=tkinter.W,image=ItemPTIconImage,tag="icon")
                        x = x + ItemIconWidth
                        ItemButton.create_text(x,centerY, font=self.ItemFont_Click,anchor=tkinter.W,fill=self.ItemFGColor_Click,text=ItemText,tag='title') 
                    elif self.Compound == 'right':
                        x = ItemWidth - ItemIconWidth
                        ItemButton.create_image(x,centerY,anchor=tkinter.W,image=ItemPTIconImage,tag="icon")
                        x = x - ItemTextW + self.ItemInnerSpacing
                        ItemButton.create_text(x,centerY, font=self.ItemFont_Click,anchor=tkinter.W,fill=self.ItemFGColor_Click,text=ItemText,tag='title') 
                    elif self.Compound == 'top':
                        y = self.ItemInnerSpacing
                        ItemButton.create_image(centerX,y,anchor=tkinter.N,image=ItemPTIconImage,tag="icon")
                        y = y + ItemIconHeight
                        ItemButton.create_text(centerX,y, font=self.ItemFont_Click,anchor=tkinter.N,fill=self.ItemFGColor_Click,text=ItemText,tag='title') 
                    elif self.Compound == 'bottom':
                        y =  ItemHeight - ItemIconHeight
                        ItemButton.create_image(centerX,y ,anchor=tkinter.N,image=ItemPTIconImage,tag="icon")
                        y = y - ItemTextH + self.ItemInnerSpacing
                        ItemButton.create_text(centerX,y, font=self.ItemFont_Click,anchor=tkinter.N,fill=self.ItemFGColor_Click,text=ItemText,tag='title') 
                    elif self.Compound == 'center':
                        ItemButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=ItemPTIconImage,tag="icon")
                        ItemButton.create_text(centerX,centerY, font=self.ItemFont_Click,anchor=tkinter.CENTER,fill=self.ItemFGColor_Click,text=ItemText,tag='title') 
                    else:
                        ItemButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=ItemPTIconImage,tag="icon")
                else:
                    ItemButton.create_text(centerX,centerY, font=self.ItemFont_Click,anchor=tkinter.CENTER,fill=self.ItemFGColor_Click,text=ItemText,tag='title') 
            elif ItemState == "Hover":
                if self.ItemBGColor_Hover:
                    ItemButton.configure(bg = self.ItemBGColor_Hover)
                ItemButton.delete('all')
                #图标
                if ItemPTIconImage:
                    if self.Compound == 'left':
                        x = self.ItemInnerSpacing
                        ItemButton.create_image(self.ItemInnerSpacing ,centerY,anchor=tkinter.W,image=ItemPTIconImage,tag="icon")
                        x = x + ItemIconWidth
                        ItemButton.create_text(x,centerY, font=self.ItemFont_Hover,anchor=tkinter.W,fill=self.ItemFGColor_Hover,text=ItemText,tag='title') 
                    elif self.Compound == 'right':
                        x = ItemWidth - ItemIconWidth
                        ItemButton.create_image(x,centerY,anchor=tkinter.W,image=ItemPTIconImage,tag="icon")
                        x = x - ItemTextW + self.ItemInnerSpacing
                        ItemButton.create_text(x,centerY, font=self.ItemFont_Hover,anchor=tkinter.W,fill=self.ItemFGColor_Hover,text=ItemText,tag='title') 
                    elif self.Compound == 'top':
                        y = self.ItemInnerSpacing
                        ItemButton.create_image(centerX,y,anchor=tkinter.N,image=ItemPTIconImage,tag="icon")
                        y = y + ItemIconHeight
                        ItemButton.create_text(centerX,y, font=self.ItemFont_Hover,anchor=tkinter.N,fill=self.ItemFGColor_Hover,text=ItemText,tag='title') 
                    elif self.Compound == 'bottom':
                        y =  ItemHeight - ItemIconHeight
                        ItemButton.create_image(centerX,y ,anchor=tkinter.N,image=ItemPTIconImage,tag="icon")
                        y = y - ItemTextH + self.ItemInnerSpacing
                        ItemButton.create_text(centerX,y, font=self.ItemFont_Hover,anchor=tkinter.N,fill=self.ItemFGColor_Hover,text=ItemText,tag='title') 
                    elif self.Compound == 'center':
                        ItemButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=ItemPTIconImage,tag="icon")
                        ItemButton.create_text(centerX,centerY, font=self.ItemFont_Hover,anchor=tkinter.CENTER,fill=self.ItemFGColor_Hover,text=ItemText,tag='title') 
                    else:
                        ItemButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=ItemPTIconImage,tag="icon")
                else:
                    ItemButton.create_text(centerX,centerY, font=self.ItemFont_Hover,anchor=tkinter.CENTER,fill=self.ItemFGColor_Hover,text=ItemText,tag='title') 
            else:
                if self.ItemBGColor:
                    ItemButton.configure(bg = self.ItemBGColor)
                ItemButton.delete('all')
                #图标
                if ItemPTIconImage:
                    if self.Compound == 'left':
                        x = self.ItemInnerSpacing
                        ItemButton.create_image(self.ItemInnerSpacing ,centerY,anchor=tkinter.W,image=ItemPTIconImage,tag="icon")
                        x = x + ItemIconWidth
                        ItemButton.create_text(x,centerY, font=self.ItemFont,anchor=tkinter.W,fill=self.ItemFGColor,text=ItemText,tag='title') 
                    elif self.Compound == 'right':
                        x = ItemWidth - ItemIconWidth
                        ItemButton.create_image(x,centerY,anchor=tkinter.W,image=ItemPTIconImage,tag="icon")
                        x = x - ItemTextW + self.ItemInnerSpacing
                        ItemButton.create_text(x,centerY, font=self.ItemFont,anchor=tkinter.W,fill=self.ItemFGColor,text=ItemText,tag='title') 
                    elif self.Compound == 'top':
                        y = self.ItemInnerSpacing
                        ItemButton.create_image(centerX,y,anchor=tkinter.N,image=ItemPTIconImage,tag="icon")
                        y = y + ItemIconHeight
                        ItemButton.create_text(centerX,y, font=self.ItemFont,anchor=tkinter.N,fill=self.ItemFGColor,text=ItemText,tag='title') 
                    elif self.Compound == 'bottom':
                        y =  ItemHeight - ItemIconHeight
                        ItemButton.create_image(centerX,y ,anchor=tkinter.N,image=ItemPTIconImage,tag="icon")
                        y = y - ItemTextH + self.ItemInnerSpacing
                        ItemButton.create_text(centerX,y, font=self.ItemFont,anchor=tkinter.N,fill=self.ItemFGColor,text=ItemText,tag='title') 
                    elif self.Compound == 'center':
                        ItemButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=ItemPTIconImage,tag="icon")
                        ItemButton.create_text(centerX,centerY, font=self.ItemFont,anchor=tkinter.CENTER,fill=self.ItemFGColor,text=ItemText,tag='title') 
                    else:
                        ItemButton.create_image(centerX,centerY,anchor=tkinter.CENTER,image=ItemPTIconImage,tag="icon")
                else:
                    ItemButton.create_text(centerX,centerY, font=self.ItemFont,anchor=tkinter.CENTER,fill=self.ItemFGColor,text=ItemText,tag='title')  
    #展开
    def Redraw(self):
        buttonX = 0
        buttonY = 0
        ButtonIndex = 0
        for ButtonInfo in self.ItemArray:
            buttonX = self.GetItemLeftX(ButtonIndex)
            buttonY = self.GetItemTopY(ButtonIndex)
            ButtonHandle = ButtonInfo[4]
            if ButtonIndex == self.CurrentIndex:
                self.RedrawItem(ButtonIndex,'Click')
            else:
                self.RedrawItem(ButtonIndex,'Normal')
            self.Canvas.coords(ButtonHandle,buttonX,buttonY)
            ButtonIndex = ButtonIndex + 1
        #取得项的列数
        XView = self.Canvas_width
        YView = buttonY + self.ItemHeight + self.ItemSpacing
        self.Canvas.config(scrollregion=(0,0,XView,YView))
