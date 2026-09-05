# -*- coding: utf-8 -*-
"""
健身记录应用 - Fitness Tracker
使用 Kivy 框架开发，可打包成 APK
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.widget import Widget
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.metrics import dp
from datetime import datetime, timedelta
import json
import os

# 注册中文字体（避免在 Android 上中文字符显示为白色方块乱码）
base_dir = os.path.dirname(os.path.abspath(__file__))
font_candidates = [
    os.path.join(base_dir, 'app_font.ttf'),
    os.path.join(base_dir, 'app_font.ttc'),
    'C:\\Windows\\Fonts\\msyh.ttc',
    'C:\\Windows\\Fonts\\simhei.ttf',
    '/system/fonts/NotoSansCJK-Regular.ttc',
    '/system/fonts/DroidSansFallback.ttf',
]
for font in font_candidates:
    if os.path.exists(font):
        try:
            LabelBase.register(name='Roboto', fn_regular=font)
            break
        except Exception:
            pass

# 设置窗口大小（开发时使用，打包后自动适应屏幕）
Window.size = (360, 640)

# ==================== 数据管理类 ====================
class DataManager:
    """管理应用数据的持久化"""
    def __init__(self):
        data_dir = '.'
        try:
            from kivy.app import App
            app = App.get_running_app()
            if app and hasattr(app, 'user_data_dir') and app.user_data_dir:
                data_dir = app.user_data_dir
        except Exception:
            data_dir = '.'
        self.data_file = os.path.join(data_dir, 'fitness_data.json')
        self.data = self.load_data()

    def load_data(self):
        """加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {'start_year': None, 'records': {}}
        return {'start_year': None, 'records': {}}

    def save_data(self):
        """保存数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def set_start_year(self, year):
        """设置起始年份"""
        self.data['start_year'] = year
        self.save_data()

    def get_start_year(self):
        """获取起始年份"""
        return self.data.get('start_year')

    def save_record(self, date_str, record):
        """保存某天的记录"""
        self.data['records'][date_str] = record
        self.save_data()

    def get_record(self, date_str):
        """获取某天的记录"""
        return self.data['records'].get(date_str)

    def get_all_records(self):
        """获取所有记录"""
        return self.data['records']

    def get_exercise_history(self, exercise_name):
        """获取某个动作的历史记录"""
        history = []
        for date_str, record in sorted(self.data['records'].items()):
            if record.get('type') == 'training':
                for group in record.get('groups', []):
                    if group.get('exercise') == exercise_name:
                        history.append({
                            'date': date_str,
                            'max_weight': max([s['weight'] for s in group.get('sets', [])], default=0),
                            'total_weight': sum([s['weight'] * s['reps'] for s in group.get('sets', [])]),
                            'total_sets': len(group.get('sets', [])),
                            'total_reps': sum([s['reps'] for s in group.get('sets', [])])
                        })
        return history

# ==================== 工具函数 ====================
def get_week_dates(date):
    """获取某个日期所在周的所有日期（周一到周日）"""
    # 获取周一
    monday = date - timedelta(days=date.weekday())
    return [monday + timedelta(days=i) for i in range(7)]

def get_month_dates(year, month):
    """获取某月的所有日期"""
    from calendar import monthrange
    days_in_month = monthrange(year, month)[1]
    return [datetime(year, month, day) for day in range(1, days_in_month + 1)]

def get_weekday_name(date):
    """获取星期几的中文名称"""
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    return weekdays[date.weekday()]

# ==================== 日历视图组件 ====================
class CalendarScreen(Screen):
    """日历主界面"""
    def __init__(self, data_manager, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = data_manager
        self.current_date = datetime.now()
        self.view_mode = 'week'  # week, month, year

        # 检查是否需要设置起始年份
        if not self.data_manager.get_start_year():
            self.show_year_input_popup()
        else:
            self.build_ui()

    def show_year_input_popup(self):
        """显示年份输入弹窗"""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text='请输入起始年份', size_hint_y=0.3))

        year_input = TextInput(
            text=str(datetime.now().year),
            multiline=False,
            input_filter='int',
            size_hint_y=0.3
        )
        content.add_widget(year_input)

        btn = Button(text='确定', size_hint_y=0.4)
        content.add_widget(btn)

        popup = Popup(
            title='首次使用设置',
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        def on_confirm(instance):
            try:
                year = int(year_input.text)
                if 2000 <= year <= 2100:
                    self.data_manager.set_start_year(year)
                    popup.dismiss()
                    self.build_ui()
            except:
                pass

        btn.bind(on_press=on_confirm)
        popup.open()

    def build_ui(self):
        """构建日历界面"""
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical')

        # 顶部导航栏
        nav_bar = BoxLayout(size_hint_y=0.1, spacing=dp(5), padding=dp(5))

        prev_btn = Button(text='◀', size_hint_x=0.2)
        prev_btn.bind(on_press=self.go_previous)
        nav_bar.add_widget(prev_btn)

        self.title_label = Label(text='', size_hint_x=0.6)
        nav_bar.add_widget(self.title_label)

        next_btn = Button(text='▶', size_hint_x=0.2)
        next_btn.bind(on_press=self.go_next)
        nav_bar.add_widget(next_btn)

        layout.add_widget(nav_bar)

        # 视图切换按钮
        view_switch = BoxLayout(size_hint_y=0.08, spacing=dp(5), padding=dp(5))

        week_btn = Button(text='周视图', background_color=(0.3, 0.8, 0.3, 1) if self.view_mode == 'week' else (0.5, 0.5, 0.5, 1))
        week_btn.bind(on_press=lambda x: self.switch_view('week'))
        view_switch.add_widget(week_btn)

        month_btn = Button(text='月视图', background_color=(0.3, 0.8, 0.3, 1) if self.view_mode == 'month' else (0.5, 0.5, 0.5, 1))
        month_btn.bind(on_press=lambda x: self.switch_view('month'))
        view_switch.add_widget(month_btn)

        year_btn = Button(text='年视图', background_color=(0.3, 0.8, 0.3, 1) if self.view_mode == 'year' else (0.5, 0.5, 0.5, 1))
        year_btn.bind(on_press=lambda x: self.switch_view('year'))
        view_switch.add_widget(year_btn)

        layout.add_widget(view_switch)

        # 日历内容区域
        self.calendar_container = BoxLayout(orientation='vertical', size_hint_y=0.82)
        layout.add_widget(self.calendar_container)

        self.add_widget(layout)
        self.update_calendar_view()

    def switch_view(self, mode):
        """切换视图模式"""
        self.view_mode = mode
        self.build_ui()

    def go_previous(self, instance):
        """上一个周期"""
        if self.view_mode == 'week':
            self.current_date -= timedelta(days=7)
        elif self.view_mode == 'month':
            # 上一个月
            if self.current_date.month == 1:
                self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        else:  # year
            self.current_date = self.current_date.replace(year=self.current_date.year - 1)
        self.update_calendar_view()

    def go_next(self, instance):
        """下一个周期"""
        if self.view_mode == 'week':
            self.current_date += timedelta(days=7)
        elif self.view_mode == 'month':
            # 下一个月
            if self.current_date.month == 12:
                self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        else:  # year
            self.current_date = self.current_date.replace(year=self.current_date.year + 1)
        self.update_calendar_view()

    def update_calendar_view(self):
        """更新日历显示"""
        self.calendar_container.clear_widgets()

        if self.view_mode == 'week':
            self.show_week_view()
        elif self.view_mode == 'month':
            self.show_month_view()
        else:
            self.show_year_view()

    def show_week_view(self):
        """显示周视图"""
        week_dates = get_week_dates(self.current_date)
        self.title_label.text = f"{week_dates[0].strftime('%Y年%m月%d日')} - {week_dates[-1].strftime('%m月%d日')}"

        grid = GridLayout(cols=1, spacing=dp(5), padding=dp(5), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        for date in week_dates:
            self.add_date_button(grid, date)

        scroll = ScrollView()
        scroll.add_widget(grid)
        self.calendar_container.add_widget(scroll)

    def show_month_view(self):
        """显示月视图"""
        self.title_label.text = f"{self.current_date.strftime('%Y年%m月')}"

        month_dates = get_month_dates(self.current_date.year, self.current_date.month)

        # 创建网格（7列，显示周一到周日）
        grid = GridLayout(cols=7, spacing=dp(2), padding=dp(5), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        # 添加星期标题
        for day in ['一', '二', '三', '四', '五', '六', '日']:
            grid.add_widget(Label(text=day, size_hint_y=None, height=dp(30)))

        # 填充月初空白
        first_day_weekday = month_dates[0].weekday()
        for _ in range(first_day_weekday):
            grid.add_widget(Label(text='', size_hint_y=None, height=dp(60)))

        # 添加日期
        for date in month_dates:
            self.add_date_button(grid, date, compact=True)

        scroll = ScrollView()
        scroll.add_widget(grid)
        self.calendar_container.add_widget(scroll)

    def show_year_view(self):
        """显示年视图"""
        self.title_label.text = f"{self.current_date.year}年"

        grid = GridLayout(cols=3, spacing=dp(10), padding=dp(10))

        for month in range(1, 13):
            month_widget = self.create_mini_month(self.current_date.year, month)
            grid.add_widget(month_widget)

        scroll = ScrollView()
        scroll.add_widget(grid)
        self.calendar_container.add_widget(scroll)

    def create_mini_month(self, year, month):
        """创建迷你月份视图"""
        layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120))

        # 月份标题
        layout.add_widget(Label(text=f'{month}月', size_hint_y=0.2, bold=True))

        # 简化的月历
        month_dates = get_month_dates(year, month)
        has_training = any(self.data_manager.get_record(d.strftime('%Y-%m-%d')) for d in month_dates)

        info_label = Label(
            text=f'共{len(month_dates)}天',
            size_hint_y=0.3
        )
        layout.add_widget(info_label)

        # 点击跳转到该月
        btn = Button(
            text='查看详情' if has_training else '暂无记录',
            size_hint_y=0.5,
            background_color=(0.3, 0.8, 0.3, 1) if has_training else (0.5, 0.5, 0.5, 1)
        )
        btn.bind(on_press=lambda x: self.jump_to_month(year, month))
        layout.add_widget(btn)

        return layout

    def jump_to_month(self, year, month):
        """跳转到指定月份"""
        self.current_date = datetime(year, month, 1)
        self.view_mode = 'month'
        self.build_ui()

    def add_date_button(self, container, date, compact=False):
        """添加日期按钮"""
        date_str = date.strftime('%Y-%m-%d')
        record = self.data_manager.get_record(date_str)
        today = datetime.now().date()

        # 确定背景色
        if record:
            if record.get('type') == 'training':
                bg_color = (0.2, 0.8, 0.2, 1)  # 绿色 - 训练日
                status = '✓'
            else:
                bg_color = (1, 0.6, 0.2, 1)  # 橙色 - 休息日
                status = '休'
        else:
            bg_color = (0.3, 0.3, 0.3, 1)  # 灰色 - 无记录
            status = ''

        if compact:
            # 月视图的紧凑样式
            btn = Button(
                text=f"{date.day}\n{status}",
                size_hint_y=None,
                height=dp(60),
                background_color=bg_color
            )
            # 今天用蓝色边框（通过颜色变化模拟）
            if date.date() == today:
                btn.background_color = (0.2, 0.4, 1, 1)
        else:
            # 周视图的详细样式
            weekday = get_weekday_name(date)
            text = f"{date.strftime('%m月%d日')} {weekday}\n{status}"
            btn = Button(
                text=text,
                size_hint_y=None,
                height=dp(80),
                background_color=bg_color,
                font_size='16sp'
            )
            if date.date() == today:
                btn.background_color = (0.2, 0.4, 1, 1)

        btn.bind(on_press=lambda x: self.open_record_screen(date))
        container.add_widget(btn)

    def open_record_screen(self, date):
        """打开记录界面"""
        app = App.get_running_app()
        record_screen = app.sm.get_screen('record')
        record_screen.set_date(date)
        app.sm.current = 'record'

# ==================== 训练记录界面 ====================
class RecordScreen(Screen):
    """训练记录界面"""
    def __init__(self, data_manager, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = data_manager
        self.current_date = None
        self.current_record = None

    def set_date(self, date):
        """设置当前日期并加载数据"""
        self.current_date = date
        date_str = date.strftime('%Y-%m-%d')
        self.current_record = self.data_manager.get_record(date_str) or {
            'type': None,
            'groups': [],
            'note': ''
        }
        self.build_ui()

    def build_ui(self):
        """构建记录界面"""
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical')

        # 顶部标题栏
        header = BoxLayout(size_hint_y=0.08, padding=dp(5))
        back_btn = Button(text='← 返回', size_hint_x=0.3)
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)

        weekday = get_weekday_name(self.current_date)
        title = Label(text=f"{self.current_date.strftime('%Y年%m月%d日')} {weekday}", size_hint_x=0.7, bold=True)
        header.add_widget(title)

        layout.add_widget(header)

        # 类型选择
        type_box = BoxLayout(size_hint_y=0.08, spacing=dp(5), padding=dp(5))
        type_box.add_widget(Label(text='类型:', size_hint_x=0.3))

        training_btn = Button(
            text='训练日',
            size_hint_x=0.35,
            background_color=(0.2, 0.8, 0.2, 1) if self.current_record.get('type') == 'training' else (0.5, 0.5, 0.5, 1)
        )
        training_btn.bind(on_press=lambda x: self.set_type('training'))
        type_box.add_widget(training_btn)

        rest_btn = Button(
            text='休息日',
            size_hint_x=0.35,
            background_color=(1, 0.6, 0.2, 1) if self.current_record.get('type') == 'rest' else (0.5, 0.5, 0.5, 1)
        )
        rest_btn.bind(on_press=lambda x: self.set_type('rest'))
        type_box.add_widget(rest_btn)

        layout.add_widget(type_box)

        # 内容区域（滚动）
        self.content_container = ScrollView(size_hint_y=0.74)
        layout.add_widget(self.content_container)

        # 底部按钮
        bottom_box = BoxLayout(size_hint_y=0.1, spacing=dp(5), padding=dp(5))

        if self.current_record.get('type') == 'training':
            add_group_btn = Button(text='+ 添加动作组', background_color=(0.2, 0.6, 0.8, 1))
            add_group_btn.bind(on_press=self.add_exercise_group)
            bottom_box.add_widget(add_group_btn)

        save_btn = Button(text='保存', background_color=(0.2, 0.8, 0.2, 1))
        save_btn.bind(on_press=self.save_record)
        bottom_box.add_widget(save_btn)

        layout.add_widget(bottom_box)
        self.add_widget(layout)
        self.update_content()

    def set_type(self, record_type):
        """设置记录类型"""
        self.current_record['type'] = record_type
        if record_type == 'rest':
            self.current_record['groups'] = []
        self.build_ui()

    def update_content(self):
        """更新内容显示"""
        self.content_container.clear_widgets()

        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10), padding=dp(10))
        content.bind(minimum_height=content.setter('height'))

        if self.current_record.get('type') == 'training':
            # 显示训练内容
            for idx, group in enumerate(self.current_record.get('groups', [])):
                group_widget = self.create_exercise_group_widget(idx, group)
                content.add_widget(group_widget)

            # 图表区域
            if self.current_record.get('groups'):
                content.add_widget(Label(text='历史趋势', size_hint_y=None, height=dp(40), bold=True))
                chart = ChartWidget(self.data_manager, size_hint_y=None, height=dp(200))
                # 默认显示第一个动作的图表
                first_exercise = self.current_record['groups'][0]['exercise']
                chart.set_exercise(first_exercise)
                content.add_widget(chart)

        elif self.current_record.get('type') == 'rest':
            # 显示休息日备注
            content.add_widget(Label(text='休息日备注:', size_hint_y=None, height=dp(30)))
            note_input = TextInput(
                text=self.current_record.get('note', ''),
                multiline=True,
                size_hint_y=None,
                height=dp(150)
            )
            note_input.bind(text=lambda instance, value: self.current_record.update({'note': value}))
            content.add_widget(note_input)

        else:
            content.add_widget(Label(text='请先选择训练日或休息日', size_hint_y=None, height=dp(100)))

        self.content_container.add_widget(content)

    def create_exercise_group_widget(self, group_idx, group):
        """创建动作组件"""
        group_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5), padding=dp(5))
        group_layout.bind(minimum_height=group_layout.setter('height'))

        # 设置背景色
        with group_layout.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            group_layout.bg_rect = Rectangle(pos=group_layout.pos, size=group_layout.size)
        group_layout.bind(pos=lambda instance, value: setattr(instance.bg_rect, 'pos', value))
        group_layout.bind(size=lambda instance, value: setattr(instance.bg_rect, 'size', value))

        # 动作选择和删除按钮
        header_box = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        header_box.add_widget(Label(text=f'动作 {group_idx + 1}:', size_hint_x=0.3))

        exercise_spinner = Spinner(
            text=group.get('exercise', '选择动作'),
            values=['全蹲', '高翻', '引体', '划船', '卧推', '自定义...'],
            size_hint_x=0.5
        )
        exercise_spinner.bind(text=lambda spinner, text: self.on_exercise_selected(group_idx, text))
        header_box.add_widget(exercise_spinner)

        del_btn = Button(text='删除', size_hint_x=0.2, background_color=(0.8, 0.2, 0.2, 1))
        del_btn.bind(on_press=lambda x: self.delete_group(group_idx))
        header_box.add_widget(del_btn)

        group_layout.add_widget(header_box)

        # 组数显示
        sets_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(3))
        sets_layout.bind(minimum_height=sets_layout.setter('height'))

        for set_idx, set_data in enumerate(group.get('sets', [])):
            set_box = BoxLayout(size_hint_y=None, height=dp(35), spacing=dp(3))
            set_box.add_widget(Label(text=f'第{set_idx + 1}组', size_hint_x=0.25))

            weight_input = TextInput(
                text=str(set_data.get('weight', '')),
                multiline=False,
                input_filter='float',
                size_hint_x=0.3
            )
            weight_input.bind(text=lambda instance, value, gi=group_idx, si=set_idx: self.update_set(gi, si, 'weight', value))
            set_box.add_widget(weight_input)

            set_box.add_widget(Label(text='kg', size_hint_x=0.1))

            reps_input = TextInput(
                text=str(set_data.get('reps', '')),
                multiline=False,
                input_filter='int',
                size_hint_x=0.2
            )
            reps_input.bind(text=lambda instance, value, gi=group_idx, si=set_idx: self.update_set(gi, si, 'reps', value))
            set_box.add_widget(reps_input)

            set_box.add_widget(Label(text='次', size_hint_x=0.1))

            del_set_btn = Button(text='×', size_hint_x=0.05)
            del_set_btn.bind(on_press=lambda x, gi=group_idx, si=set_idx: self.delete_set(gi, si))
            set_box.add_widget(del_set_btn)

            sets_layout.add_widget(set_box)

        group_layout.add_widget(sets_layout)

        # 添加组按钮
        add_set_btn = Button(text='+ 添加组', size_hint_y=None, height=dp(35))
        add_set_btn.bind(on_press=lambda x: self.add_set(group_idx))
        group_layout.add_widget(add_set_btn)

        # 统计信息
        stats = self.calculate_group_stats(group)
        stats_text = f"总组数: {stats['total_sets']} | 总次数: {stats['total_reps']} | 总重量: {stats['total_weight']}kg | 最大重量: {stats['max_weight']}kg"
        group_layout.add_widget(Label(text=stats_text, size_hint_y=None, height=dp(30), color=(0.8, 0.8, 0.2, 1)))

        # 进步对比
        comparison = self.get_exercise_comparison(group.get('exercise', ''))
        if comparison:
            comp_text = f"上次: 最大{comparison['prev_max']}kg | 总重{comparison['prev_total']}kg\n"
            comp_text += f"本次: 最大{comparison['curr_max']}kg | 总重{comparison['curr_total']}kg\n"
            if comparison['max_diff'] > 0:
                comp_text += f"进步: 最大重量+{comparison['max_diff']}kg, 总重量+{comparison['total_diff']}kg"
            elif comparison['max_diff'] < 0:
                comp_text += f"变化: 最大重量{comparison['max_diff']}kg, 总重量{comparison['total_diff']}kg"
            else:
                comp_text += "保持稳定"
            group_layout.add_widget(Label(text=comp_text, size_hint_y=None, height=dp(60), color=(0.2, 0.8, 0.8, 1)))

        # 备注
        note_input = TextInput(
            text=group.get('note', ''),
            hint_text='备注...',
            multiline=True,
            size_hint_y=None,
            height=dp(60)
        )
        note_input.bind(text=lambda instance, value, gi=group_idx: self.update_group_note(gi, value))
        group_layout.add_widget(note_input)

        return group_layout

    def on_exercise_selected(self, group_idx, exercise_name):
        """选择动作时的回调"""
        if exercise_name == '自定义...':
            self.show_custom_exercise_input(group_idx)
        else:
            self.current_record['groups'][group_idx]['exercise'] = exercise_name
            self.update_content()

    def show_custom_exercise_input(self, group_idx):
        """显示自定义动作输入框"""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text='输入动作名称:', size_hint_y=0.3))

        exercise_input = TextInput(multiline=False, size_hint_y=0.3)
        content.add_widget(exercise_input)

        btn_box = BoxLayout(size_hint_y=0.4, spacing=dp(5))
        cancel_btn = Button(text='取消')
        confirm_btn = Button(text='确定')
        btn_box.add_widget(cancel_btn)
        btn_box.add_widget(confirm_btn)
        content.add_widget(btn_box)

        popup = Popup(title='自定义动作', content=content, size_hint=(0.8, 0.4))

        def on_confirm(instance):
            if exercise_input.text.strip():
                self.current_record['groups'][group_idx]['exercise'] = exercise_input.text.strip()
                self.update_content()
            popup.dismiss()

        cancel_btn.bind(on_press=popup.dismiss)
        confirm_btn.bind(on_press=on_confirm)
        popup.open()

    def calculate_group_stats(self, group):
        """计算动作组统计"""
        sets = group.get('sets', [])
        total_sets = len(sets)
        total_reps = sum(s.get('reps', 0) for s in sets)
        total_weight = sum(s.get('weight', 0) * s.get('reps', 0) for s in sets)
        max_weight = max([s.get('weight', 0) for s in sets], default=0)

        return {
            'total_sets': total_sets,
            'total_reps': total_reps,
            'total_weight': total_weight,
            'max_weight': max_weight
        }

    def get_exercise_comparison(self, exercise_name):
        """获取动作对比数据"""
        if not exercise_name:
            return None

        history = self.data_manager.get_exercise_history(exercise_name)
        if len(history) < 1:
            return None

        # 排除今天的记录
        today_str = self.current_date.strftime('%Y-%m-%d')
        history = [h for h in history if h['date'] != today_str]

        if not history:
            return None

        prev_record = history[-1]  # 最近一次

        # 计算当前数据
        current_group = next((g for g in self.current_record.get('groups', []) if g.get('exercise') == exercise_name), None)
        if not current_group:
            return None

        curr_stats = self.calculate_group_stats(current_group)

        return {
            'prev_max': prev_record['max_weight'],
            'prev_total': prev_record['total_weight'],
            'curr_max': curr_stats['max_weight'],
            'curr_total': curr_stats['total_weight'],
            'max_diff': curr_stats['max_weight'] - prev_record['max_weight'],
            'total_diff': curr_stats['total_weight'] - prev_record['total_weight']
        }

    def add_exercise_group(self, instance):
        """添加动作组"""
        self.current_record['groups'].append({
            'exercise': '',
            'sets': [],
            'note': ''
        })
        self.update_content()

    def delete_group(self, group_idx):
        """删除动作组"""
        if 0 <= group_idx < len(self.current_record['groups']):
            self.current_record['groups'].pop(group_idx)
            self.update_content()

    def add_set(self, group_idx):
        """添加组"""
        if 0 <= group_idx < len(self.current_record['groups']):
            self.current_record['groups'][group_idx]['sets'].append({
                'weight': 0,
                'reps': 0
            })
            self.update_content()

    def delete_set(self, group_idx, set_idx):
        """删除组"""
        if 0 <= group_idx < len(self.current_record['groups']):
            sets = self.current_record['groups'][group_idx]['sets']
            if 0 <= set_idx < len(sets):
                sets.pop(set_idx)
                self.update_content()

    def update_set(self, group_idx, set_idx, field, value):
        """更新组数据"""
        try:
            if 0 <= group_idx < len(self.current_record['groups']):
                sets = self.current_record['groups'][group_idx]['sets']
                if 0 <= set_idx < len(sets):
                    if field == 'weight':
                        sets[set_idx]['weight'] = float(value) if value else 0
                    elif field == 'reps':
                        sets[set_idx]['reps'] = int(value) if value else 0
        except:
            pass

    def update_group_note(self, group_idx, note):
        """更新组备注"""
        if 0 <= group_idx < len(self.current_record['groups']):
            self.current_record['groups'][group_idx]['note'] = note

    def save_record(self, instance):
        """保存记录"""
        if self.current_record.get('type'):
            date_str = self.current_date.strftime('%Y-%m-%d')
            self.data_manager.save_record(date_str, self.current_record)

            # 显示保存成功提示
            popup = Popup(
                title='提示',
                content=Label(text='保存成功！'),
                size_hint=(0.6, 0.3)
            )
            popup.open()

            # 1秒后自动关闭并返回
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: popup.dismiss(), 1)
            Clock.schedule_once(lambda dt: self.go_back(None), 1.2)
        else:
            popup = Popup(
                title='提示',
                content=Label(text='请先选择训练日或休息日'),
                size_hint=(0.6, 0.3)
            )
            popup.open()

    def go_back(self, instance):
        """返回日历界面"""
        app = App.get_running_app()
        calendar_screen = app.sm.get_screen('calendar')
        calendar_screen.build_ui()  # 刷新日历
        app.sm.current = 'calendar'

# ==================== 图表组件 ====================
class ChartWidget(Widget):
    """绘制训练趋势图表"""
    def __init__(self, data_manager, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = data_manager
        self.exercise_name = None
        self.bind(pos=self.update_chart, size=self.update_chart)

    def set_exercise(self, exercise_name):
        """设置要显示的动作"""
        self.exercise_name = exercise_name
        self.update_chart()

    def update_chart(self, *args):
        """绘制图表"""
        self.canvas.clear()

        if not self.exercise_name:
            return

        history = self.data_manager.get_exercise_history(self.exercise_name)
        if len(history) < 2:
            with self.canvas:
                Color(1, 1, 1, 1)
                from kivy.graphics import Line as KivyLine, Rectangle
                # 绘制提示文本（简化处理）
            return

        # 只显示最近10次记录
        history = history[-10:]

        # 提取数据
        dates = [h['date'] for h in history]
        max_weights = [h['max_weight'] for h in history]
        total_weights = [h['total_weight'] for h in history]

        # 计算坐标
        padding = dp(40)
        width = self.width - 2 * padding
        height = self.height - 2 * padding

        if width <= 0 or height <= 0:
            return

        # 归一化数据
        max_max_weight = max(max_weights) if max_weights else 1
        max_total_weight = max(total_weights) if total_weights else 1

        with self.canvas:
            # 背景
            Color(0.15, 0.15, 0.15, 1)
            Rectangle(pos=self.pos, size=self.size)

            # 绘制网格线
            Color(0.3, 0.3, 0.3, 1)
            for i in range(5):
                y = self.y + padding + (height / 4) * i
                Line(points=[self.x + padding, y, self.x + self.width - padding, y], width=1)

            # 绘制最大重量折线（绿色）
            Color(0.2, 0.8, 0.2, 1)
            points = []
            for i, weight in enumerate(max_weights):
                x = self.x + padding + (width / (len(max_weights) - 1)) * i if len(max_weights) > 1 else self.x + padding + width / 2
                y = self.y + padding + (weight / max_max_weight) * height * 0.8
                points.extend([x, y])
            if len(points) >= 4:
                Line(points=points, width=2)

            # 绘制总重量折线（蓝色）
            Color(0.2, 0.4, 0.8, 1)
            points = []
            for i, weight in enumerate(total_weights):
                x = self.x + padding + (width / (len(total_weights) - 1)) * i if len(total_weights) > 1 else self.x + padding + width / 2
                y = self.y + padding + (weight / max_total_weight) * height * 0.4  # 缩放到下半部分
                points.extend([x, y])
            if len(points) >= 4:
                Line(points=points, width=2)

            # 绘制图例
            Color(1, 1, 1, 1)
            # 这里简化了文本绘制，Kivy中文本需要用Label widget
            # 在实际应用中会在外部添加Label来显示图例

# ==================== 主应用 ====================
class FitnessTrackerApp(App):
    """健身记录应用主类"""
    def build(self):
        self.title = '健身记录'
        self.data_manager = DataManager()

        # 创建屏幕管理器
        self.sm = ScreenManager()

        # 添加日历屏幕
        calendar_screen = CalendarScreen(self.data_manager, name='calendar')
        self.sm.add_widget(calendar_screen)

        # 添加记录屏幕
        record_screen = RecordScreen(self.data_manager, name='record')
        self.sm.add_widget(record_screen)

        return self.sm

if __name__ == '__main__':
    FitnessTrackerApp().run()

