import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QScrollArea, QLabel, QPushButton, QStackedWidget,
    QFrame, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QAction

from data_manager import DataManager

# 配置：数据文件路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEAPON_CSV = os.path.join(BASE_DIR, "数据", "武器词条.CSV")
DUNGEON_CSV = os.path.join(BASE_DIR, "数据", "副本.CSV")

class WeaponCard(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, name, rarity, dm, parent=None):
        super().__init__(parent)
        self.name = name
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            WeaponCard {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            WeaponCard:hover {
                background-color: #f0f0f0;
                border: 1px solid #bbb;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # 显示类似于 Flet 的文本："{rarity}★{name}"
        # CSV 中的稀有度通常包含 "星"，如果存在则将其移除以保持一致性
        rarity_clean = rarity.replace('星', '')
        display_text = f"{rarity_clean}★{name}"
        
        label = QLabel(display_text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        layout.addWidget(label)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.name)
        super().mousePressEvent(event)

class DetailView(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, dm: DataManager, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        # 带有返回按钮的头部
        header_layout = QHBoxLayout()
        self.back_btn = QPushButton("← 返回列表")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.setStyleSheet("QPushButton { border: none; font-weight: bold; color: #333; text-align: left; } QPushButton:hover { color: #000; }")
        self.back_btn.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(self.back_btn)
        header_layout.addStretch()
        self.layout.addLayout(header_layout)

        # 内容滚动区域
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.scroll.setWidget(self.content_widget)
        self.layout.addWidget(self.scroll)

    def show_weapon(self, weapon_name):
        # 清除旧内容
        for i in reversed(range(self.content_layout.count())): 
            widget = self.content_layout.itemAt(i).widget()
            if widget: widget.deleteLater()

        w = self.dm.get_weapon_details(weapon_name)
        if not w:
            self.content_layout.addWidget(QLabel("Weapon not found"))
            return

        # --- 信息卡片 ---
        info_card = QFrame()
        info_card.setStyleSheet(".QFrame { background-color: white; border: 1px solid #ccc; border-radius: 8px; }")
        info_layout = QVBoxLayout(info_card)
        
        # 标题
        title_label = QLabel(w.name)
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        info_layout.addWidget(title_label)
        
        subtitle = QLabel(f"稀有度: {w.rarity} | 种类: {w.type}")
        subtitle.setStyleSheet("color: #666;")
        info_layout.addWidget(subtitle)
        
        # 属性
        stats_layout = QHBoxLayout()
        
        def create_stat_col(title, value, color):
            container = QWidget()
            l = QVBoxLayout(container)
            t = QLabel(title)
            t.setStyleSheet(f"font-weight: bold; color: {color};")
            t.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v = QLabel(value)
            v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l.addWidget(t)
            l.addWidget(v)
            return container

        stats_layout.addWidget(create_stat_col("主词条", w.main_stat, "blue"))
        stats_layout.addWidget(create_stat_col("副词条", w.sub_stat, "green"))
        stats_layout.addWidget(create_stat_col("技能", w.skill, "orange"))
        
        info_layout.addLayout(stats_layout)
        self.content_layout.addWidget(info_card)

        # --- 刷取方案 ---
        plan = self.dm.get_farming_plan(weapon_name)
        
        if plan and "error" not in plan:
            plan_card = QFrame()
            plan_card.setStyleSheet(".QFrame { background-color: white; border: 1px solid #ccc; border-radius: 8px; }")
            plan_layout = QVBoxLayout(plan_card)
            
            plan_title = QLabel("推荐刷取方案")
            plan_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            plan_title.setStyleSheet("color: teal;")
            plan_layout.addWidget(plan_title)
            
            plan_layout.addWidget(QLabel("此方案可最大化覆盖其他武器需求"))
            
            # 方案详情
            detail_grid = QGridLayout()
            detail_grid.addWidget(QLabel("副本:"), 0, 0)
            detail_grid.addWidget(QLabel(f"<b>{plan['dungeon']}</b>"), 0, 1)
            
            detail_grid.addWidget(QLabel("定向策略:"), 1, 0)
            detail_grid.addWidget(QLabel(f"<font color='blue'>{plan['strategy']} ({plan['fixed_val']})</font>"), 1, 1)
            
            main_stats_str = ", ".join(plan['selected_mains'])
            detail_grid.addWidget(QLabel("定向主词条 (3选1):"), 2, 0)
            detail_grid.addWidget(QLabel(f"<font color='blue'>{main_stats_str}</font>"), 2, 1)
            
            plan_layout.addLayout(detail_grid)
            
            # 副产物
            plan_layout.addWidget(QLabel(f"<b>可能产出的有用副产物 (共帮助 {plan['score']} 把其他武器):</b>"))
            
            by_prod_scroll = QScrollArea()
            by_prod_scroll.setFixedHeight(300)
            by_prod_scroll.setWidgetResizable(True)
            by_prod_content = QWidget()
            by_prod_layout = QVBoxLayout(by_prod_content)
            
            if plan['by_products']:
                sorted_items = sorted(plan['by_products'].items(), key=lambda x: len(x[1]), reverse=True)
                for (m, s, k), weapons in sorted_items:
                    item_frame = QFrame()
                    item_frame.setStyleSheet("border-bottom: 1px solid #eee;")
                    item_l = QVBoxLayout(item_frame)
                    
                    header = QLabel(f"[{m} | {s} | {k}]")
                    header.setStyleSheet("font-weight: bold; color: #555;")
                    item_l.addWidget(header)
                    
                    w_list = QLabel(f"适用: {', '.join(weapons)}")
                    w_list.setWordWrap(True)
                    w_list.setStyleSheet("font-size: 11px; font-style: italic;")
                    item_l.addWidget(w_list)
                    
                    by_prod_layout.addWidget(item_frame)
            else:
                by_prod_layout.addWidget(QLabel("无其他适用武器产生的副产物"))
            
            by_prod_layout.addStretch()
            by_prod_scroll.setWidget(by_prod_content)
            plan_layout.addWidget(by_prod_scroll)
            
            self.content_layout.addWidget(plan_card)
            
        elif plan and "error" in plan:
             err_label = QLabel(f"错误: {plan['error']}")
             err_label.setStyleSheet("color: red;")
             self.content_layout.addWidget(err_label)
        else:
            self.content_layout.addWidget(QLabel("无法生成方案", styleSheet="color: red;"))

        self.content_layout.addStretch()

class HomeView(QWidget):
    weapon_selected = pyqtSignal(str)

    def __init__(self, dm: DataManager, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.all_weapons = dm.get_weapon_names()
        
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("武器列表")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 搜索
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索武器...")
        self.search_input.textChanged.connect(self.filter_weapons)
        layout.addWidget(self.search_input)
        
        # 网格区域
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.grid_widget)
        layout.addWidget(self.scroll)
        
        self.filter_weapons("")

    def filter_weapons(self, text):
        # 清除网格
        # 注意：在 Qt 中正确地从网格布局中移除项目有点繁琐
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        row = 0
        col = 0
        max_cols = 3 
        
        for name in self.all_weapons:
            if not text or text.lower() in name.lower():
                w_details = self.dm.get_weapon_details(name)
                card = WeaponCard(name, w_details.rarity, self.dm)
                card.clicked.connect(self.weapon_selected.emit)
                card.setFixedHeight(100) # 类似于 Flet 中的宽高比
                
                self.grid_layout.addWidget(card, row, col)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("武器基质刷取工具箱")
        self.resize(500, 800)
        
        # 加载数据
        try:
            self.dm = DataManager(WEAPON_CSV, DUNGEON_CSV)
        except Exception as e:
            error_widget = QLabel(f"Error loading data: {e}")
            error_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setCentralWidget(error_widget)
            return

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self.home_view = HomeView(self.dm)
        self.detail_view = DetailView(self.dm)
        
        self.stack.addWidget(self.home_view)
        self.stack.addWidget(self.detail_view)
        
        # 连接信号
        self.home_view.weapon_selected.connect(self.go_to_detail)
        self.detail_view.back_requested.connect(self.go_to_home)

    def go_to_detail(self, weapon_name):
        self.detail_view.show_weapon(weapon_name)
        self.stack.setCurrentWidget(self.detail_view)

    def go_to_home(self):
        self.stack.setCurrentWidget(self.home_view)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
