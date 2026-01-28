import flet as ft
from data_manager import DataManager

# 配置：数据文件路径
WEAPON_CSV = r"d:\code\pythonProject\tools\zmd_tool\数据\武器词条.CSV"
DUNGEON_CSV = r"d:\code\pythonProject\tools\zmd_tool\数据\副本.CSV"

def main(page: ft.Page):
    """
    Flet 应用主入口
    """
    page.title = "武器基质刷取工具箱"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 500
    page.window_height = 800

    # 加载数据
    try:
        dm = DataManager(WEAPON_CSV, DUNGEON_CSV)
        all_weapons = dm.get_weapon_names()
    except Exception as e:
        page.add(ft.Text(f"Error loading data: {e}", color="red"))
        return

    # UI 组件定义
    search_field = ft.TextField(
        label="搜索武器", 
        prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: filter_weapons(e.control.value)
    )
    
    # 武器列表容器
    weapon_list = ft.GridView(
        expand=True,
        max_extent=150,
        child_aspect_ratio=1.5,
        spacing=10,
        run_spacing=10,
        padding=10
    )
    
    def show_home():
        """显示主页（武器列表）"""
        page.clean()
        page.add(
            ft.Container(
                content=ft.Text("武器列表", size=30, weight="bold"),
                padding=ft.padding.only(top=20, left=10)
            ),
            ft.Container(
                content=search_field,
                padding=10
            ),
            weapon_list
        )
        filter_weapons("")
        page.update()

    def filter_weapons(query):
        """根据搜索关键词过滤并显示武器"""
        weapon_list.controls.clear()
        for name in all_weapons:
            if not query or query.lower() in name.lower():
                weapon_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Text(
                                f"{dm.get_weapon_details(name).rarity.replace('星', '')}★{name}",
                                weight="bold",
                                text_align=ft.TextAlign.CENTER,
                                size=16,
                                no_wrap=False,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            padding=10,
                            ink=True,
                            on_click=lambda e, n=name: show_detail(n),
                            alignment=ft.Alignment(0, 0)
                        ),
                        elevation=2,
                    )
                )
        page.update()

    def show_detail(weapon_name):
        """显示武器详情及刷取方案"""
        w = dm.get_weapon_details(weapon_name)
        if not w: return

        plan = dm.get_farming_plan(weapon_name)
        
        page.clean()
        
        # 头部：包含返回按钮
        header = ft.Row([
            ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_home()),
            ft.Text("返回列表", size=16, weight="bold")
        ])

        # 武器基本信息卡片
        info_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.SHIELD, size=30),
                        ft.Text(f"{w.name}", size=24, weight="bold"),
                    ]),
                    ft.Text(f"稀有度: {w.rarity} | 种类: {w.type}"),
                    ft.Divider(),
                    ft.Row([
                        ft.Column([ft.Text("主词条", weight="bold", color="blue"), ft.Text(w.main_stat)], horizontal_alignment="center"),
                        ft.Column([ft.Text("副词条", weight="bold", color="green"), ft.Text(w.sub_stat)], horizontal_alignment="center"),
                        ft.Column([ft.Text("技能", weight="bold", color="orange"), ft.Text(w.skill)], horizontal_alignment="center"),
                    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
                ]),
                padding=20
            ),
            elevation=4
        )

        plan_content = []
        if plan and "error" not in plan:
            # 方案详情
            main_stats_str = ", ".join(plan['selected_mains'])
            
            # 副产物展示
            by_products_controls = []
            if plan['by_products']:
                # 按受益武器数量排序
                sorted_items = sorted(plan['by_products'].items(), key=lambda x: len(x[1]), reverse=True)
                
                for (m, s, k), weapons in sorted_items:
                    by_products_controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.TOKEN, size=16),
                                    ft.Text(f" [{m} | {s} | {k}]", weight="bold", color=ft.Colors.BLUE_GREY),
                                ]),
                                ft.Text(f"适用: {', '.join(weapons)}", size=12, italic=True)
                            ]),
                            padding=5,
                            border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.GREY_300))
                        )
                    )
            else:
                by_products_controls.append(ft.Text("无其他适用武器产生的副产物", italic=True))

            plan_card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("推荐刷取方案", size=20, weight="bold", color=ft.Colors.TEAL),
                        ft.Text("此方案可最大化覆盖其他武器需求", size=12, color="grey"),
                        ft.Divider(),
                        ft.Text(f"副本: {plan['dungeon']}", size=16, weight="bold"),
                        ft.Row([
                            ft.Text("定向策略: ", weight="bold"),
                            ft.Text(f"{plan['strategy']} ({plan['fixed_val']})", color="blue")
                        ]),
                        ft.Column([
                            ft.Text("定向主词条 (3选1):", weight="bold"),
                            ft.Text(f"{main_stats_str}", color="blue")
                        ]),
                        ft.Divider(),
                        ft.Text(f"可能产出的有用副产物 (共帮助 {plan['score']} 把其他武器):", weight="bold"),
                        ft.Container(
                            content=ft.Column(by_products_controls, scroll=ft.ScrollMode.AUTO),
                            height=300, # 固定高度以便滚动
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            border_radius=5,
                            padding=5
                        )
                    ]),
                    padding=20
                ),
                elevation=4
            )
            plan_content.append(plan_card)
        elif plan and "error" in plan:
             plan_content.append(ft.Card(content=ft.Container(content=ft.Text(f"错误: {plan['error']}", color="red"), padding=20)))
        else:
            plan_content.append(ft.Text("无法生成方案", color="red"))

        page.add(
            header,
            info_card,
            *plan_content
        )
        page.update()

    show_home()

if __name__ == "__main__":
    ft.app(target=main)
