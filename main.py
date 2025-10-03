import flet as ft
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional

class FinanceApp:
    def __init__(self):
        self.data_file = "finance_data.json"
        self.load_data()
        
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
                if "goal_investments" not in self.data:
                    self.data["goal_investments"] = {}
                if "salary_dates" not in self.data:
                    self.data["salary_dates"] = [8, 22]
                if "rent" not in self.data:
                    self.data["rent"] = 0
                if "rent_paid_until" not in self.data:
                    self.data["rent_paid_until"] = None
                if "safety_reserve" not in self.data:
                    self.data["safety_reserve"] = 20000
                if "chatgpt_enabled" not in self.data:
                    self.data["chatgpt_enabled"] = True
                if "birthdays" not in self.data:
                    self.data["birthdays"] = []
                if "notes" not in self.data:
                    self.data["notes"] = []
        else:
            self.data = {
                "salary": 0,
                "current_money": 0,
                "transactions": [],
                "goals": [],
                "monthly_budget": {},
                "goal_investments": {},
                "salary_dates": [8, 22],
                "rent": 0,
                "rent_paid_until": None,
                "safety_reserve": 20000,
                "chatgpt_enabled": True,
                "birthdays": [],
                "notes": []
            }
    
    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

class MainApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.finance_app = FinanceApp()
        self.purchase_name = ""
        self.purchase_price = 0
        self.purchase_analysis = ft.Text("Введите название товара и цену", size=14, color=ft.Colors.GREY_600)
        self.setup_page()
        self.create_main_interface()
    
    def setup_page(self):
        self.page.title = "Умное Финансовое Приложение"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 1000
        self.page.window_height = 700
        self.page.padding = 20
    
    def create_main_interface(self):
        self.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Главная"),
                ft.NavigationBarDestination(icon=ft.Icons.ACCOUNT_BALANCE_WALLET, label="Деньги"),
                ft.NavigationBarDestination(icon=ft.Icons.STAR, label="Цели"),
                ft.NavigationBarDestination(icon=ft.Icons.ANALYTICS, label="Аналитика"),
                ft.NavigationBarDestination(icon=ft.Icons.TRENDING_UP, label="Прогноз"),
                ft.NavigationBarDestination(icon=ft.Icons.CALCULATE, label="Калькулятор"),
                ft.NavigationBarDestination(icon=ft.Icons.NOTE, label="Заметки"),
            ],
            on_change=self.on_navigation_change
        )
        
        self.main_content = ft.Container(
            content=self.create_home_page(),
            expand=True
        )
        
        self.page.add(
            ft.Column([
                self.main_content,
                self.navigation_bar
            ], expand=True)
        )
    
    def on_navigation_change(self, e):
        selected_index = e.control.selected_index
        
        if selected_index == 0:
            self.main_content.content = self.create_home_page()
        elif selected_index == 1:
            self.main_content.content = self.create_money_page()
        elif selected_index == 2:
            self.main_content.content = self.create_goals_page()
        elif selected_index == 3:
            self.main_content.content = self.create_analytics_page()
        elif selected_index == 4:
            self.main_content.content = self.create_forecast_page()
        elif selected_index == 5:
            self.main_content.content = self.create_calculator_page()
        elif selected_index == 6:
            self.main_content.content = self.create_notes_page()
        
        self.page.update()
    
    def create_home_page(self):
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        free_money = current_money - safety_reserve
        daily_budget = self.calculate_daily_budget()
        days_until_salary = self.calculate_days_until_salary(self.finance_app.data["salary_dates"][0])
        
        # Получаем данные для текущего месяца
        current_month_income = self.get_current_month_income()
        current_month_expenses = self.get_current_month_expenses()
        month_balance = current_month_income - current_month_expenses
        
        # Получаем информацию о целях
        goals = self.finance_app.data["goals"]
        goal_investments = self.finance_app.data["goal_investments"]
        total_goals = sum(goal["amount"] for goal in goals)
        total_invested = sum(goal_investments.values())
        remaining_goals = total_goals - total_invested
        
        # Получаем дни рождения на текущий месяц
        current_month = datetime.now().month
        current_birthdays = self.get_birthdays_for_month(current_month)
        
        # Создаем предупреждения и рекомендации
        warnings = []
        recommendations = []
        
        if free_money < 5000:
            warnings.append("⚠️ Критически мало свободных денег")
        elif free_money < 10000:
            warnings.append("⚠️ Мало свободных денег")
        
        if daily_budget < 500:
            warnings.append("⚠️ Очень маленький дневной бюджет")
        elif daily_budget < 1000:
            warnings.append("⚠️ Маленький дневной бюджет")
        
        if month_balance < 0:
            warnings.append("⚠️ Отрицательный баланс месяца")
        elif month_balance < 5000:
            warnings.append("⚠️ Низкий баланс месяца")
        
        if days_until_salary > 20:
            recommendations.append("💡 До зарплаты еще долго - экономьте")
        elif days_until_salary < 3:
            recommendations.append("💡 Скоро зарплата - можно немного потратить")
        
        return ft.Column([
            # Заголовок с датой и днем недели
            ft.Container(
                content=ft.Row([
                    ft.Text(f"📅 {datetime.now().strftime('%d %B %Y')}", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.Text(f"📅 {datetime.now().strftime('%A')}", size=18, color=ft.Colors.GREY_600)
                ]),
                padding=20,
                bgcolor=ft.Colors.BLUE_50,
                border_radius=10
            ),
            
            # Основная статистика - два столбца
            ft.Row([
                # Финансы
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("💰 Финансы", size=20, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Text(f"Всего денег: {current_money:,.0f} ₽", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Свободно: {free_money:,.0f} ₽", size=14, color=ft.Colors.GREEN),
                            ft.Text(f"Резерв безопасности: {safety_reserve:,.0f} ₽", size=14, color=ft.Colors.BLUE)
                        ], spacing=10),
                        padding=20
                    ),
                    expand=1
                ),
                
                # Текущий месяц
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("📊 Текущий месяц", size=20, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Text(f"Доходы: {current_month_income:,.0f} ₽", size=16, color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Расходы: {current_month_expenses:,.0f} ₽", size=16, color=ft.Colors.RED, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Баланс: {month_balance:,.0f} ₽", size=16, color=ft.Colors.BLUE if month_balance >= 0 else ft.Colors.RED, weight=ft.FontWeight.BOLD)
                        ], spacing=10),
                        padding=20
                    ),
                    expand=1
                )
            ], spacing=20),
            
            # Цели и дни рождения - два столбца
            ft.Row([
                # Цели
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("🎯 Цели", size=20, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Text(f"Активных целей: {len(goals)}", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Нужно накопить: {remaining_goals:,.0f} ₽" if goals else "Нет целей", size=14, color=ft.Colors.ORANGE),
                            ft.Text(f"Уже накоплено: {total_invested:,.0f} ₽" if goals else "", size=14, color=ft.Colors.GREEN)
                        ], spacing=10),
                        padding=20
                    ),
                    expand=1
                ),
                
                # Дни рождения
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("🎂 Дни рождения", size=20, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Text(f"В этом месяце: {len(current_birthdays)}", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(", ".join([bday["name"] for bday in current_birthdays]) if current_birthdays else "Нет дней рождения", size=14, color=ft.Colors.PINK)
                        ], spacing=10),
                        padding=20
                    ),
                    expand=1
                )
            ], spacing=20),
            
            # Календарь
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("📅 Календарь", size=20, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        self.create_mini_calendar()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            # До зарплаты
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("📅 До зарплаты", size=20, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Text(f"Осталось дней: {days_until_salary}", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Дневной бюджет: {daily_budget:,.0f} ₽", size=16, color=ft.Colors.GREEN),
                        ft.Text(f"Следующая зарплата: {self.get_next_salary_date_formatted()}", size=14, color=ft.Colors.GREY_600),
                        ft.Divider(),
                        ft.Text("📊 Детали:", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(f"• Всего денег: {current_money:,.0f} ₽", size=12),
                        ft.Text(f"• Резерв: {safety_reserve:,.0f} ₽", size=12),
                        ft.Text(f"• Доступно: {free_money:,.0f} ₽", size=12),
                        ft.Text(f"• На день: {daily_budget:,.0f} ₽", size=12)
                    ]),
                    padding=20,
                    border_radius=10
                )
            ),
            
            # Улучшенный умный калькулятор покупок
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("🧮 Умный калькулятор покупок", size=20, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Row([
                            ft.TextField(
                                label="Название товара",
                                value=self.purchase_name,
                                on_change=self.update_purchase_name,
                                expand=1,
                                border_radius=8
                            ),
                            ft.TextField(
                                label="Цена (₽)",
                                value=str(self.purchase_price) if self.purchase_price > 0 else "",
                                on_change=self.update_purchase_price,
                                keyboard_type=ft.KeyboardType.NUMBER,
                                expand=1,
                                border_radius=8
                            )
                        ], spacing=10),
                        ft.ElevatedButton(
                            "🔍 Анализировать покупку",
                            on_click=self.check_purchase_affordability,
                            bgcolor=ft.Colors.BLUE,
                            color=ft.Colors.WHITE,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8)
                            )
                        ),
                        self.purchase_analysis
                    ], spacing=15),
                    padding=20
                )
            ),
            
            # Быстрые действия
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("⚡ Быстрые действия", size=20, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Row([
                            ft.ElevatedButton(
                                "➕ Добавить доход",
                                on_click=self.go_to_money_page,
                                bgcolor=ft.Colors.GREEN,
                                color=ft.Colors.WHITE,
                                expand=1,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8)
                                )
                            ),
                            ft.ElevatedButton(
                                "➖ Добавить расход",
                                on_click=self.go_to_money_page,
                                bgcolor=ft.Colors.RED,
                                color=ft.Colors.WHITE,
                                expand=1,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8)
                                )
                            ),
                            ft.ElevatedButton(
                                "📊 Аналитика",
                                on_click=self.go_to_analytics_page,
                                bgcolor=ft.Colors.BLUE,
                                color=ft.Colors.WHITE,
                                expand=1,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8)
                                )
                            )
                        ], spacing=10)
                    ], spacing=15),
                    padding=20
                )
            ),
            
            # Предупреждения и рекомендации
            self.create_smart_alerts(warnings, recommendations)
            
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
    
    def go_to_money_page(self, e):
        """Переход на страницу денег"""
        self.main_content.content = self.create_money_page()
        self.page.update()
    
    def go_to_analytics_page(self, e):
        """Переход на страницу аналитики"""
        self.main_content.content = self.create_analytics_page()
        self.page.update()
    
    def create_mini_calendar(self):
        """Создает аккуратный мини-календарь текущего месяца"""
        import calendar
        now = datetime.now()
        year = now.year
        month = now.month
        
        # Получаем календарь месяца
        cal = calendar.monthcalendar(year, month)
        month_name = calendar.month_name[month]
        
        # Создаем заголовок
        header = ft.Container(
            content=ft.Column([
                ft.Text("📅 Календарь", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(f"📅 {month_name} {year}", size=12, color=ft.Colors.BLUE)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=8
        )
        
        # Создаем дни недели с фиксированной шириной
        weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        weekday_row = ft.Row([
            ft.Container(
                content=ft.Text(day, size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                width=28,
                height=24,
                alignment=ft.alignment.center
            )
            for day in weekdays
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
        
        # Создаем дни месяца с фиксированными размерами
        day_rows = []
        for week in cal:
            week_row = ft.Row([], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
            for day in week:
                if day == 0:
                    # Пустая ячейка для дней предыдущего/следующего месяца
                    week_row.controls.append(
                        ft.Container(
                            content=ft.Text("", size=11),
                            width=28,
                            height=28,
                            alignment=ft.alignment.center
                        )
                    )
                else:
                    is_today = day == now.day
                    is_weekend = week.index(day) >= 5
                    
                    # Определяем цвета
                    if is_today:
                        color = ft.Colors.WHITE
                        bgcolor = ft.Colors.BLUE_400
                        border_color = ft.Colors.BLUE_600
                    elif is_weekend:
                        color = ft.Colors.RED_600
                        bgcolor = ft.Colors.RED_50
                        border_color = ft.Colors.RED_200
                    else:
                        color = ft.Colors.BLACK
                        bgcolor = ft.Colors.WHITE
                        border_color = ft.Colors.GREY_200
                    
                    week_row.controls.append(
                        ft.Container(
                            content=ft.Text(str(day), size=11, color=color, weight=ft.FontWeight.BOLD if is_today else ft.FontWeight.NORMAL),
                            width=28,
                            height=28,
                            bgcolor=bgcolor,
                            border=ft.border.all(1, border_color),
                            border_radius=4,
                            alignment=ft.alignment.center
                        )
                    )
            day_rows.append(week_row)
        
        # Создаем основной контейнер календаря
        calendar_container = ft.Container(
            content=ft.Column([
                weekday_row,
                *day_rows
            ], spacing=2),
            padding=8,
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300)
        )
        
        return ft.Column([
            header,
            calendar_container
        ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    def create_smart_alerts(self, warnings, recommendations):
        """Создает умные предупреждения и рекомендации"""
        alerts = []
        
        for warning in warnings:
            alerts.append(ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.WARNING, color=ft.Colors.ORANGE, size=16),
                    ft.Text(warning, size=12, color=ft.Colors.ORANGE)
                ]),
                padding=8,
                bgcolor=ft.Colors.ORANGE_50,
            ))
        
        for recommendation in recommendations:
            alerts.append(ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.THUMB_UP, color=ft.Colors.GREEN, size=16),
                    ft.Text(recommendation, size=12, color=ft.Colors.GREEN)
                ]),
                padding=8,
                bgcolor=ft.Colors.GREEN_50,
            ))
        
        return ft.Column(alerts, spacing=5) if alerts else ft.Container()
    
    def get_current_month_birthdays(self):
        """Получает дни рождения текущего месяца"""
        now = datetime.now()
        current_month = now.month
        
        birthdays = []
        for birthday in self.finance_app.data["birthdays"]:
            if self.convert_month_to_int(birthday["month"]) == current_month:
                birthdays.append(birthday["name"])
        
        return birthdays
    
    def convert_month_to_int(self, month_name):
        """Конвертирует название месяца в число"""
        months = {
            "Январь": 1, "Февраль": 2, "Март": 3, "Апрель": 4,
            "Май": 5, "Июнь": 6, "Июль": 7, "Август": 8,
            "Сентябрь": 9, "Октябрь": 10, "Ноябрь": 11, "Декабрь": 12
        }
        return months.get(month_name, 1)
    
    def calculate_days_until_salary(self, salary_date):
        """Рассчитывает дни до следующей зарплаты"""
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        
        # Следующая зарплата
        if now.day <= salary_date:
            next_salary = datetime(current_year, current_month, salary_date)
        else:
            if current_month == 12:
                next_salary = datetime(current_year + 1, 1, salary_date)
            else:
                next_salary = datetime(current_year, current_month + 1, salary_date)
        
        # Используем только даты без времени для точного расчета
        today = now.date()
        salary_day = next_salary.date()
        delta = salary_day - today
        return max(0, delta.days)
    
    def get_next_salary_date_formatted(self):
        """Получает дату следующей зарплаты в формате строки"""
        salary_date = self.finance_app.data["salary_dates"][0]
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        
        if now.day <= salary_date:
            next_salary = datetime(current_year, current_month, salary_date)
        else:
            if current_month == 12:
                next_salary = datetime(current_year + 1, 1, salary_date)
            else:
                next_salary = datetime(current_year, current_month + 1, salary_date)
        
        return next_salary.strftime("%d.%m.%Y")
    
    def calculate_current_month_expenses(self):
        """Рассчитывает расходы текущего месяца"""
        # Простой расчет - можно улучшить
        return 30000
    
    def analyze_purchase_new(self, e):
        """Новый анализ покупки"""
        if not hasattr(self, 'purchase_price') or self.purchase_price <= 0:
            self.purchase_result = ft.Text("Введите цену товара", size=14, color=ft.Colors.GREY_600)
        else:
            self.purchase_result = self.create_simple_purchase_analysis()
        
        self.page.update()
    
    def create_new_purchase_result(self):
        """Создает контейнер для результата анализа"""
        if not hasattr(self, 'purchase_result'):
            self.purchase_result = ft.Text("Введите название товара и цену", size=14, color=ft.Colors.GREY_600)
        
        return ft.Container(
            content=self.purchase_result,
            padding=10
        )
    
    def create_simple_purchase_analysis(self):
        """Создает максимально подробный анализ покупки с детальной информацией"""
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        free_money = current_money - safety_reserve
        price = getattr(self, 'purchase_price', 0)
        product_name = getattr(self, 'purchase_name', 'Товар')
        
        # Получаем дополнительную информацию
        goals = self.finance_app.data["goals"]
        goal_investments = self.finance_app.data["goal_investments"]
        total_goals = sum(goal["amount"] for goal in goals)
        total_invested = sum(goal_investments.values())
        remaining_goals = total_goals - total_invested
        
        # Рассчитываем месячные накопления
        rent_cost = self.finance_app.data.get("rent_cost", 25000)
        monthly_savings = self.finance_app.data["salary"] - self.calculate_average_monthly_expenses() - (3000 if self.finance_app.data["chatgpt_enabled"] else 0) - rent_cost
        
        # Анализ возможности покупки
        can_buy_now = free_money >= price
        after_purchase_free = free_money - price
        reserve_impact = max(0, safety_reserve - after_purchase_free)
        
        analysis = []
        
        # Заголовок
        analysis.append(ft.Text(f"🛒 {product_name} - {price:,.0f} ₽", size=18, weight=ft.FontWeight.BOLD))
        analysis.append(ft.Divider())
        
        # Финансовая ситуация
        analysis.append(ft.Container(
            content=ft.Column([
                ft.Text("💰 Ваша финансовая ситуация:", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(f"• Всего денег: {current_money:,.0f} ₽", size=14),
                ft.Text(f"• Резерв безопасности: {safety_reserve:,.0f} ₽", size=14),
                ft.Text(f"• Свободно для трат: {free_money:,.0f} ₽", size=14),
                ft.Text(f"• После покупки останется: {after_purchase_free:,.0f} ₽", size=14)
            ], spacing=5),
            padding=15,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=8
        ))
        
        # Анализ покупки
        if can_buy_now:
            if after_purchase_free >= safety_reserve:
                # Резерв не затронут
                analysis.append(ft.Container(
                    content=ft.Column([
                        ft.Text("✅ МОЖНО КУПИТЬ", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                        ft.Text("Резерв не затронут", size=16, color=ft.Colors.GREEN),
                        ft.Text(f"Останется резерва: {after_purchase_free:,.0f} ₽", size=14, color=ft.Colors.GREEN)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=15,
                    bgcolor=ft.Colors.GREEN_50,
                    border_radius=8
                ))
            elif after_purchase_free > 0:
                # Затронет резерв, но не критично
                analysis.append(ft.Container(
                    content=ft.Column([
                        ft.Text("⚠️ МОЖЕТЕ КУПИТЬ, НО ЗАТРОНЕТЕ РЕЗЕРВ", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE),
                        ft.Text(f"Затронете резерв на: {reserve_impact:,.0f} ₽", size=16),
                        ft.Text(f"Останется резерва: {after_purchase_free:,.0f} ₽", size=16),
                        ft.Text("⚠️ Не рекомендуется - нарушает финансовую безопасность", size=14, color=ft.Colors.RED)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=15,
                    bgcolor=ft.Colors.ORANGE_50,
                    border_radius=8
                ))
            else:
                # Критическая ситуация
                analysis.append(ft.Container(
                    content=ft.Column([
                        ft.Text("❌ НЕЛЬЗЯ КУПИТЬ", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
                        ft.Text(f"Недостаточно свободных денег", size=16, color=ft.Colors.RED),
                        ft.Text(f"Нужно еще: {abs(after_purchase_free):,.0f} ₽", size=16, color=ft.Colors.RED)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=15,
                    bgcolor=ft.Colors.RED_50,
                ))
        else:
            # Не может купить
            needed = price - free_money
            analysis.append(ft.Container(
                content=ft.Column([
                    ft.Text("❌ НЕЛЬЗЯ КУПИТЬ", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
                    ft.Text(f"Недостаточно свободных денег", size=14, color=ft.Colors.RED),
                    ft.Text(f"Нужно еще: {needed:,.0f} ₽", size=14, color=ft.Colors.RED)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=15,
                bgcolor=ft.Colors.RED_50,
            ))
        
        # Детали
        analysis.append(ft.Text("📊 Детали:", size=14, weight=ft.FontWeight.BOLD))
        analysis.append(ft.Text(f"• Всего денег: {current_money:,.0f} ₽", size=12))
        analysis.append(ft.Text(f"• Резерв безопасности: {safety_reserve:,.0f} ₽", size=12))
        analysis.append(ft.Text(f"• Свободно для трат: {free_money:,.0f} ₽", size=12))
        analysis.append(ft.Text(f"• После покупки: {after_purchase_free:,.0f} ₽", size=12, 
                               color=ft.Colors.GREEN if after_purchase_free >= 0 else ft.Colors.RED))
        
        # Анализ по месяцам
        analysis.append(ft.Text("📅 Анализ по месяцам:", size=14, weight=ft.FontWeight.BOLD))
        
        # Получаем лучшие месяцы для покупки
        best_months = self.get_best_months_for_purchase(price)
        worst_months = self.get_worst_months_for_purchase(price)
        
        # Лучшие месяцы
        if best_months:
            analysis.append(ft.Text("🟢 Лучшие месяцы для покупки:", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN))
            for month_info in best_months[:3]:  # Показываем топ-3
                month_name = month_info['month']
                reason = month_info['reason']
                analysis.append(ft.Text(f"  • {month_name}: {reason}", size=11, color=ft.Colors.GREEN))
        
        # Худшие месяцы
        if worst_months:
            analysis.append(ft.Text("🔴 Избегайте покупки в:", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.RED))
            for month_info in worst_months[:2]:  # Показываем топ-2 худших
                month_name = month_info['month']
                reason = month_info['reason']
                analysis.append(ft.Text(f"  • {month_name}: {reason}", size=11, color=ft.Colors.RED))
        
        # План накоплений
        if not can_buy_now:
            analysis.append(ft.Text("💰 План накоплений:", size=14, weight=ft.FontWeight.BOLD))
            needed = price - free_money
            monthly_savings = self.calculate_monthly_savings()
            
            if monthly_savings > 0:
                months_to_save = max(1, round(needed / monthly_savings))
                analysis.append(ft.Text(f"• Нужно накопить: {needed:,.0f} ₽", size=12))
                analysis.append(ft.Text(f"• При накоплении {monthly_savings:,.0f} ₽/мес: {months_to_save} мес", size=12))
                
                # Лучшие месяцы для накоплений
                best_saving_months = self.get_best_months_for_saving()
                if best_saving_months:
                    analysis.append(ft.Text("• Лучше начать копить в:", size=12, weight=ft.FontWeight.BOLD))
                    for month_info in best_saving_months[:2]:
                        month_name = month_info['month']
                        reason = month_info['reason']
                        analysis.append(ft.Text(f"  - {month_name}: {reason}", size=11, color=ft.Colors.BLUE))
            else:
                analysis.append(ft.Text("• Увеличьте доходы или уменьшите расходы", size=12, color=ft.Colors.ORANGE))
        
        # Умные советы
        analysis.append(ft.Text("💡 Умные советы:", size=14, weight=ft.FontWeight.BOLD))
        
        if can_buy_now and after_purchase_free >= safety_reserve:
            analysis.append(ft.Text("• Покупка безопасна - можете покупать сейчас", size=12, color=ft.Colors.GREEN))
            analysis.append(ft.Text("• Рассмотрите скидки в конце месяца", size=12, color=ft.Colors.BLUE))
        elif can_buy_now and after_purchase_free > 0:
            analysis.append(ft.Text("• Лучше подождать - затронете резерв", size=12, color=ft.Colors.ORANGE))
            analysis.append(ft.Text("• Накопите еще {:.0f} ₽ перед покупкой".format(safety_reserve - after_purchase_free), size=12, color=ft.Colors.ORANGE))
        else:
            analysis.append(ft.Text("• Накопите деньги перед покупкой", size=12, color=ft.Colors.RED))
            analysis.append(ft.Text("• Поищите скидки и акции", size=12, color=ft.Colors.BLUE))
            analysis.append(ft.Text("• Рассмотрите покупку в рассрочку", size=12, color=ft.Colors.BLUE))
            analysis.append(ft.Text("• Подождите лучшего месяца для покупки", size=12, color=ft.Colors.BLUE))
        
        # Влияние на цели
        if goals and remaining_goals > 0:
            analysis.append(ft.Text("🎯 Влияние на ваши цели:", size=14, weight=ft.FontWeight.BOLD))
            analysis.append(ft.Text(f"• Осталось накопить: {remaining_goals:,.0f} ₽", size=12))
            
            if can_buy_now:
                new_remaining = remaining_goals + price
                analysis.append(ft.Text(f"• После покупки нужно будет накопить: {new_remaining:,.0f} ₽", size=12, color=ft.Colors.ORANGE))
                
                if monthly_savings > 0:
                    months_delay = price / monthly_savings
                    analysis.append(ft.Text(f"• Цели отложатся на: {months_delay:.1f} месяцев", size=12, color=ft.Colors.ORANGE))
            else:
                analysis.append(ft.Text("• Покупка не повлияет на цели (недостаточно денег)", size=12, color=ft.Colors.GREY_600))
        
        # Риск-анализ
        analysis.append(ft.Text("⚠️ Риск-анализ:", size=14, weight=ft.FontWeight.BOLD))
        
        if after_purchase_free >= safety_reserve * 1.5:
            risk_level = "Низкий"
            risk_color = ft.Colors.GREEN
        elif after_purchase_free >= safety_reserve:
            risk_level = "Средний"
            risk_color = ft.Colors.ORANGE
        else:
            risk_level = "Высокий"
            risk_color = ft.Colors.RED
        
        analysis.append(ft.Text(f"• Уровень риска: {risk_level}", size=12, color=risk_color))
        analysis.append(ft.Text(f"• Останется резерва: {after_purchase_free:,.0f} ₽", size=12))
        analysis.append(ft.Text(f"• Рекомендуемый резерв: {safety_reserve:,.0f} ₽", size=12))
        
        # Альтернативы
        analysis.append(ft.Text("🔄 Альтернативы:", size=14, weight=ft.FontWeight.BOLD))
        
        if not can_buy_now:
            analysis.append(ft.Text("• Накопите деньги перед покупкой", size=12, color=ft.Colors.BLUE))
            analysis.append(ft.Text("• Рассмотрите покупку в рассрочку", size=12, color=ft.Colors.BLUE))
            analysis.append(ft.Text("• Поищите более дешевые аналоги", size=12, color=ft.Colors.BLUE))
        else:
            analysis.append(ft.Text("• Можете купить сейчас", size=12, color=ft.Colors.GREEN))
            analysis.append(ft.Text("• Подождите скидок", size=12, color=ft.Colors.BLUE))
            analysis.append(ft.Text("• Сравните с другими магазинами", size=12, color=ft.Colors.BLUE))
        
        # Дополнительные советы
        analysis.append(ft.Text("🎯 Дополнительные советы:", size=12, weight=ft.FontWeight.BOLD))
        analysis.append(ft.Text("• Следите за сезонными скидками", size=11, color=ft.Colors.GREY_600))
        analysis.append(ft.Text("• Сравните цены в разных магазинах", size=11, color=ft.Colors.GREY_600))
        analysis.append(ft.Text("• Рассмотрите б/у варианты", size=11, color=ft.Colors.GREY_600))
        analysis.append(ft.Text("• Используйте кэшбэк и бонусы", size=11, color=ft.Colors.GREY_600))
        analysis.append(ft.Text("• Проверьте гарантию и возврат", size=11, color=ft.Colors.GREY_600))
        analysis.append(ft.Text("• Учитывайте стоимость доставки", size=11, color=ft.Colors.GREY_600))
        
        return ft.Column(analysis, spacing=10)
    
    def get_best_months_for_purchase(self, price=None):
        """Возвращает лучшие месяцы для покупки с причинами"""
        months_analysis = {
            1: {"name": "Январь", "good": True, "reason": "Нет праздников, стабильные расходы"},
            2: {"name": "Февраль", "good": True, "reason": "День Святого Валентина, но небольшие траты"},
            3: {"name": "Март", "good": True, "reason": "8 Марта, но умеренные расходы"},
            4: {"name": "Апрель", "good": True, "reason": "Нет крупных праздников"},
            5: {"name": "Май", "good": True, "reason": "Майские праздники, но много выходных"},
            6: {"name": "Июнь", "good": True, "reason": "Начало лета, стабильные расходы"},
            7: {"name": "Июль", "good": True, "reason": "Середина лета, отпуска"},
            8: {"name": "Август", "good": True, "reason": "Конец лета, подготовка к осени"},
            9: {"name": "Сентябрь", "good": True, "reason": "Начало учебного года, стабильность"},
            10: {"name": "Октябрь", "good": True, "reason": "Осень, умеренные расходы"},
            11: {"name": "Ноябрь", "good": True, "reason": "Подготовка к зиме, стабильность"},
            12: {"name": "Декабрь", "good": False, "reason": "Новый год - много трат"}
        }
        
        # Добавляем дни рождения
        birthdays = self.finance_app.data["birthdays"]
        for birthday in birthdays:
            month = self.convert_month_to_int(birthday["month"])
            if month in months_analysis:
                months_analysis[month]["good"] = False
                months_analysis[month]["reason"] = f"День рождения {birthday['name']} - дополнительные траты"
        
        # Фильтруем и сортируем по приоритету
        good_months = []
        for month_num, data in months_analysis.items():
            if data["good"]:
                good_months.append({
                    "month": data["name"],
                    "reason": data["reason"],
                    "priority": self.get_month_priority(month_num)
                })
        
        # Сортируем по приоритету (чем выше, тем лучше)
        good_months.sort(key=lambda x: x["priority"], reverse=True)
        return good_months
    
    def get_worst_months_for_purchase(self, price=None):
        """Возвращает худшие месяцы для покупки с причинами"""
        months_analysis = {
            1: {"name": "Январь", "bad": False, "reason": ""},
            2: {"name": "Февраль", "bad": False, "reason": ""},
            3: {"name": "Март", "bad": False, "reason": ""},
            4: {"name": "Апрель", "bad": False, "reason": ""},
            5: {"name": "Май", "bad": False, "reason": ""},
            6: {"name": "Июнь", "bad": False, "reason": ""},
            7: {"name": "Июль", "bad": False, "reason": ""},
            8: {"name": "Август", "bad": False, "reason": ""},
            9: {"name": "Сентябрь", "bad": False, "reason": ""},
            10: {"name": "Октябрь", "bad": False, "reason": ""},
            11: {"name": "Ноябрь", "bad": False, "reason": ""},
            12: {"name": "Декабрь", "bad": True, "reason": "Новый год - много трат на подарки"}
        }
        
        # Добавляем дни рождения
        birthdays = self.finance_app.data["birthdays"]
        for birthday in birthdays:
            month = self.convert_month_to_int(birthday["month"])
            if month in months_analysis:
                months_analysis[month]["bad"] = True
                months_analysis[month]["reason"] = f"День рождения {birthday['name']} - дополнительные траты"
        
        # Фильтруем плохие месяцы
        bad_months = []
        for month_num, data in months_analysis.items():
            if data["bad"]:
                bad_months.append({
                    "month": data["name"],
                    "reason": data["reason"],
                    "priority": self.get_month_bad_priority(month_num)
                })
        
        # Сортируем по приоритету (чем выше, тем хуже)
        bad_months.sort(key=lambda x: x["priority"], reverse=True)
        return bad_months
    
    def get_best_months_for_saving(self):
        """Возвращает лучшие месяцы для накопления с причинами"""
        best_purchase = self.get_best_months_for_purchase()
        # Для накоплений приоритет немного другой
        saving_months = []
        for month_info in best_purchase:
            month_name = month_info["month"]
            if month_name in ["Апрель", "Октябрь", "Сентябрь"]:
                reason = f"Отличное время для накоплений - {month_info['reason']}"
            else:
                reason = f"Хорошее время для накоплений - {month_info['reason']}"
            
            saving_months.append({
                "month": month_name,
                "reason": reason
            })
        
        return saving_months
    
    def get_month_priority(self, month):
        """Возвращает приоритет месяца для покупок (1-10)"""
        priorities = {
            1: 8,   # Январь - после праздников, хорошие скидки
            2: 6,   # Февраль - стабильно
            3: 7,   # Март - весна, активность
            4: 9,   # Апрель - отличный месяц
            5: 8,   # Май - праздники, но много выходных
            6: 7,   # Июнь - лето
            7: 6,   # Июль - отпуска
            8: 7,   # Август - конец лета
            9: 8,   # Сентябрь - начало года
            10: 9,  # Октябрь - отличный месяц
            11: 8,  # Ноябрь - стабильно
            12: 2   # Декабрь - много трат
        }
        return priorities.get(month, 5)
    
    def get_month_bad_priority(self, month):
        """Возвращает приоритет месяца для избегания покупок (1-10)"""
        priorities = {
            1: 3,   # Январь - после праздников, но может быть усталость
            2: 2,   # Февраль - стабильно
            3: 2,   # Март - стабильно
            4: 1,   # Апрель - хороший месяц
            5: 2,   # Май - праздники, но не критично
            6: 1,   # Июнь - хороший месяц
            7: 2,   # Июль - отпуска, но не критично
            8: 1,   # Август - хороший месяц
            9: 1,   # Сентябрь - хороший месяц
            10: 1,  # Октябрь - отличный месяц
            11: 1,  # Ноябрь - хороший месяц
            12: 10  # Декабрь - худший месяц
        }
        return priorities.get(month, 1)
    
    def calculate_monthly_savings(self):
        """Рассчитывает ежемесячные накопления"""
        salary = self.finance_app.data["salary"]
        monthly_expenses = self.calculate_current_month_expenses()
        chatgpt_cost = 3000 if self.finance_app.data["chatgpt_enabled"] else 0
        rent_cost = self.finance_app.data.get("rent", 25000)
        return salary - monthly_expenses - chatgpt_cost - rent_cost
    
    def update_purchase_name(self, e):
        """Обновляет название товара"""
        self.purchase_name = e.control.value
    
    def update_purchase_price(self, e):
        """Обновляет цену товара"""
        try:
            self.purchase_price = float(e.control.value) if e.control.value else 0
        except ValueError:
            self.purchase_price = 0
    
    def go_to_analytics_page(self, e):
        """Переход на страницу аналитики"""
        self.main_content.content = self.create_analytics_page()
        self.page.update()
    
    def create_money_page(self):
        return ft.Column([
            ft.Text("Управление деньгами", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Настройка оклада", size=18, weight=ft.FontWeight.BOLD),
                        ft.TextField(
                            label="Оклад (₽)",
                            value=str(self.finance_app.data["salary"]),
                            on_change=self.update_salary
                        ),
                        ft.Text("Даты получения зарплаты:", size=14, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.TextField(
                                label="Первая дата",
                                value=str(self.finance_app.data["salary_dates"][0]),
                                width=100,
                                keyboard_type=ft.KeyboardType.NUMBER,
                                on_change=self.update_salary_date_1
                            ),
                            ft.TextField(
                                label="Вторая дата",
                                value=str(self.finance_app.data["salary_dates"][1]),
                                width=100,
                                keyboard_type=ft.KeyboardType.NUMBER,
                                on_change=self.update_salary_date_2
                            )
                        ], spacing=10),
                        ft.Text("Введите числа от 1 до 31", size=12, color=ft.Colors.GREY_600),
                        ft.ElevatedButton("Обновить", on_click=self.update_money_values)
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Текущие деньги", size=18, weight=ft.FontWeight.BOLD),
                        ft.TextField(
                            label="Сумма (₽)",
                            value=str(self.finance_app.data["current_money"]),
                            on_change=self.update_current_money
                        ),
                        ft.ElevatedButton("Обновить", on_click=self.update_money_values)
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("🛡️ Резерв безопасности", size=18, weight=ft.FontWeight.BOLD),
                        ft.TextField(
                            label="Размер резерва (₽)",
                            value=str(self.finance_app.data["safety_reserve"]),
                            on_change=self.update_safety_reserve
                        ),
                        ft.Text("Минимальная сумма, которая всегда должна оставаться на счету", size=12, color=ft.Colors.GREY_600),
                        self.create_reserve_status()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("🤖 ChatGPT Plus", size=18, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Text("3,000 ₽/месяц", size=16),
                            ft.Switch(
                                value=self.finance_app.data["chatgpt_enabled"],
                                on_change=self.toggle_chatgpt
                            )
                        ]),
                        ft.Text("Включить/выключить учет подписки ChatGPT", size=12, color=ft.Colors.GREY_600)
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("🎂 Дни рождения", size=18, weight=ft.FontWeight.BOLD),
                        self.create_birthdays_management()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Квартплата", size=18, weight=ft.FontWeight.BOLD),
                        ft.TextField(
                            label="Сумма квартплаты (₽)",
                            value=str(self.finance_app.data.get("rent_cost", 25000)),
                            on_change=self.update_rent_cost
                        ),
                        ft.TextField(
                            label="Оплачено до (YYYY-MM-DD)",
                            value=self.finance_app.data["rent_paid_until"] or "",
                            on_change=self.update_rent_paid_until
                        ),
                        ft.Row([
                            ft.ElevatedButton(
                                "Оплатить квартплату",
                                on_click=self.pay_rent,
                                style=ft.ButtonStyle(bgcolor=ft.Colors.ORANGE_400)
                            ),
                            ft.ElevatedButton(
                                "Сбросить квартплату",
                                on_click=self.reset_rent,
                                style=ft.ButtonStyle(bgcolor=ft.Colors.RED_400)
                            )
                        ], spacing=10),
                        ft.ElevatedButton("Обновить", on_click=self.update_money_values),
                        self.create_rent_status()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Транзакции", size=18, weight=ft.FontWeight.BOLD),
                        self.create_transactions_list()
                    ], spacing=10),
                    padding=20
                )
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
    
    def create_goals_page(self):
        self.goal_name_field = ft.TextField(label="Название цели")
        self.goal_amount_field = ft.TextField(label="Сумма (₽)", keyboard_type=ft.KeyboardType.NUMBER)
        self.goal_date_field = ft.TextField(
            label="Дата достижения (YYYY-MM-DD)", 
            hint_text="Например: 2024-12-25",
            helper_text="Введите дату в формате ГГГГ-ММ-ДД"
        )
        
        return ft.Column([
            ft.Text("Финансовые цели", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Добавить цель", size=18, weight=ft.FontWeight.BOLD),
                        self.goal_name_field,
                        self.goal_amount_field,
                        self.goal_date_field,
                        ft.ElevatedButton("Добавить цель", on_click=self.add_goal)
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Мои цели", size=18, weight=ft.FontWeight.BOLD),
                        self.create_goals_list()
                    ], spacing=10),
                    padding=20
                )
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
    
    def create_analytics_page(self):
        return ft.Column([
            ft.Text("🤖 Умный финансовый помощник", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Анализирую ваши финансы и даю конкретные советы", size=14, color=ft.Colors.GREY_600),
            ft.Divider(),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("🎯 Мой финансовый план", size=18, weight=ft.FontWeight.BOLD),
                        self.create_financial_plan()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("💰 Когда и сколько копить", size=18, weight=ft.FontWeight.BOLD),
                        self.create_savings_strategy()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("⚠️ Критические предупреждения", size=18, weight=ft.FontWeight.BOLD),
                        self.create_critical_warnings()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("🎯 Мои цели и сроки", size=18, weight=ft.FontWeight.BOLD),
                        self.create_goals_analysis()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("📊 Детальный анализ по месяцам", size=18, weight=ft.FontWeight.BOLD),
                        self.create_detailed_monthly_analysis()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("💡 Конкретные действия", size=18, weight=ft.FontWeight.BOLD),
                        self.create_action_plan()
                    ], spacing=10),
                    padding=20
                )
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
    
    def update_purchase_name(self, e):
        self.purchase_name = e.control.value
        # Обновляем анализ сразу при изменении названия
        self.refresh_purchase_analysis()
    
    def update_purchase_price(self, e):
        try:
            self.purchase_price = float(e.control.value) if e.control.value else 0
        except ValueError:
            self.purchase_price = 0
        # Обновляем анализ сразу при изменении цены
        self.refresh_purchase_analysis()
    
    def create_purchase_analysis_container(self):
        # Создаем контейнер для анализа покупки
        self.purchase_analysis_container = ft.Container(
            content=self.create_purchase_analysis(),
            padding=10
        )
        return self.purchase_analysis_container
    
    def refresh_purchase_analysis(self):
        # Обновляем контейнер с анализом покупки
        if hasattr(self, 'purchase_analysis_container'):
            self.purchase_analysis_container.content = self.create_purchase_analysis()
            self.page.update()
    
    def refresh_all_pages(self):
        """Обновляет все страницы с актуальными данными"""
        # Обновляем текущую страницу
        if hasattr(self, 'main_content') and self.main_content.content:
            # Получаем текущий индекс из навигационной панели
            current_page = self.navigation_bar.selected_index if hasattr(self, 'navigation_bar') else 0
            
            if current_page == 0:  # Главная
                self.main_content.content = self.create_home_page()
            elif current_page == 1:  # Деньги
                self.main_content.content = self.create_money_page()
            elif current_page == 2:  # Цели
                self.main_content.content = self.create_goals_page()
            elif current_page == 3:  # Аналитика
                self.main_content.content = self.create_analytics_page()
            elif current_page == 4:  # Прогноз
                self.main_content.content = self.create_forecast_page()
            elif current_page == 5:  # Калькулятор
                self.main_content.content = self.create_calculator_page()
            elif current_page == 6:  # Заметки
                self.main_content.content = self.create_notes_page()
        
        self.page.update()
    
    def check_purchase_affordability(self, e):
        self.refresh_purchase_analysis()
    
    def create_purchase_analysis(self):
        if not hasattr(self, 'purchase_price') or self.purchase_price <= 0:
            return ft.Text("Введите цену товара", size=14, color=ft.Colors.GREY_600)
        
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        free_money = current_money - safety_reserve
        
        # Получаем информацию о квартплате
        rent_paid_until = self.finance_app.data.get("rent_paid_until", "")
        current_date = datetime(2025, datetime.now().month, datetime.now().day)
        
        # Определяем, нужно ли платить квартплату в текущем месяце
        def should_pay_rent_current():
            if not rent_paid_until:
                return True
            try:
                paid_until = datetime.strptime(rent_paid_until, "%Y-%m-%d")
                return current_date > paid_until
            except:
                return True
        
        rent_cost = self.finance_app.data.get("rent_cost", 25000)
        rent_for_current_month = rent_cost if should_pay_rent_current() else 0
        monthly_savings = self.finance_app.data["salary"] - self.calculate_average_monthly_expenses() - (3000 if self.finance_app.data["chatgpt_enabled"] else 0) - rent_for_current_month
        
        # Получаем текущий месяц и анализируем праздники
        current_month = datetime.now().month
        current_year = datetime.now().year
        current_day = datetime.now().day
        
        # Анализируем праздники и ДР в текущем месяце
        holidays = self.get_holidays_for_month(current_month)
        birthdays = self.get_birthdays_for_month(current_month)
        
        # Анализ возможности покупки
        can_buy_now = free_money >= self.purchase_price
        
        analysis = []
        
        # Заголовок с названием товара
        product_name = getattr(self, 'purchase_name', 'Товар')
        analysis.append(ft.Text(f"🛒 {product_name} - {self.purchase_price:,.0f} ₽", size=18, weight=ft.FontWeight.BOLD))
        analysis.append(ft.Divider())
        
        # Текущая финансовая ситуация
        analysis.append(ft.Text("💰 Ваша финансовая ситуация:", size=16, weight=ft.FontWeight.BOLD))
        analysis.append(ft.Text(f"• Всего денег: {current_money:,.0f} ₽", size=14))
        analysis.append(ft.Text(f"• Резерв безопасности: {safety_reserve:,.0f} ₽", size=14))
        analysis.append(ft.Text(f"• Свободно для трат: {free_money:,.0f} ₽", size=14, color=ft.Colors.BLUE if free_money >= 0 else ft.Colors.RED))
        analysis.append(ft.Text(f"• Можете копить: {monthly_savings:,.0f} ₽/мес", size=14, color=ft.Colors.GREEN if monthly_savings > 0 else ft.Colors.RED))
        
        analysis.append(ft.Divider())
        
        # Анализ текущего месяца
        analysis.append(ft.Text(f"📅 Анализ текущего месяца ({self.get_month_name(current_month)}):", size=16, weight=ft.FontWeight.BOLD))
        
        if holidays:
            analysis.append(ft.Text(f"• Праздники: {', '.join(holidays)}", size=14, color=ft.Colors.ORANGE))
        else:
            analysis.append(ft.Text("• Праздников нет", size=14, color=ft.Colors.GREEN))
        
        if birthdays:
            analysis.append(ft.Text(f"• Дни рождения: {', '.join(birthdays)}", size=14, color=ft.Colors.PURPLE))
        else:
            analysis.append(ft.Text("• Дней рождения нет", size=14, color=ft.Colors.GREEN))
        
        # Остаток месяца
        import calendar
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        remaining_days = days_in_month - current_day + 1
        analysis.append(ft.Text(f"• Осталось дней в месяце: {remaining_days}", size=14))
        
        analysis.append(ft.Divider())
        
        if can_buy_now:
            # Может купить сейчас
            remaining_after_purchase = free_money - self.purchase_price
            
            analysis.append(ft.Text("✅ МОЖЕТЕ КУПИТЬ СЕЙЧАС!", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN))
            analysis.append(ft.Text("Почему ДА:", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN))
            analysis.append(ft.Text(f"• У вас есть {free_money:,.0f} ₽ свободных денег", size=14))
            analysis.append(ft.Text(f"• Товар стоит {self.purchase_price:,.0f} ₽", size=14))
            analysis.append(ft.Text(f"• После покупки останется {remaining_after_purchase:,.0f} ₽", size=14))
            analysis.append(ft.Text("• Резерв безопасности сохранен", size=14, color=ft.Colors.GREEN))
            
            if remaining_after_purchase < 5000:
                analysis.append(ft.Text("⚠️ ВНИМАНИЕ: После покупки останется мало денег", size=14, color=ft.Colors.ORANGE))
            
            # Рекомендации по времени покупки
            if holidays or birthdays:
                analysis.append(ft.Text("⚠️ В этом месяце есть праздники/ДР - будьте осторожны с тратами", size=14, color=ft.Colors.ORANGE))
            else:
                analysis.append(ft.Text("✅ Отличный месяц для покупки - нет дополнительных трат", size=14, color=ft.Colors.GREEN))
                
        else:
            # Нужно копить
            need_to_save = self.purchase_price - free_money
            
            analysis.append(ft.Text("❌ НЕ МОЖЕТЕ КУПИТЬ СЕЙЧАС", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.RED))
            analysis.append(ft.Text("Почему НЕТ:", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.RED))
            analysis.append(ft.Text(f"• У вас только {free_money:,.0f} ₽ свободных денег", size=14))
            analysis.append(ft.Text(f"• Товар стоит {self.purchase_price:,.0f} ₽", size=14))
            analysis.append(ft.Text(f"• Не хватает: {need_to_save:,.0f} ₽", size=14, color=ft.Colors.RED))
            
            if monthly_savings > 0:
                months_to_save = need_to_save / monthly_savings
                best_month = self.find_best_month_for_purchase()
                
                analysis.append(ft.Divider())
                analysis.append(ft.Text("💡 План накопления:", size=16, weight=ft.FontWeight.BOLD))
                analysis.append(ft.Text(f"• Нужно накопить: {need_to_save:,.0f} ₽", size=14, color=ft.Colors.ORANGE))
                analysis.append(ft.Text(f"• Время накопления: {months_to_save:.1f} месяцев", size=14, color=ft.Colors.BLUE))
                analysis.append(ft.Text(f"• Откладывайте: {monthly_savings:,.0f} ₽/мес", size=14, color=ft.Colors.BLUE))
                analysis.append(ft.Text(f"• Лучший месяц для покупки: {best_month}", size=14, color=ft.Colors.GREEN))
                
                # Детальный план по месяцам
                analysis.append(ft.Divider())
                analysis.append(ft.Text("📅 Детальный план накопления по месяцам:", size=16, weight=ft.FontWeight.BOLD))
                self.add_monthly_savings_plan(analysis, need_to_save, monthly_savings, current_month)
                
                # Рекомендации по лучшим месяцам
                analysis.append(ft.Divider())
                analysis.append(ft.Text("🎯 Рекомендации по времени покупки:", size=16, weight=ft.FontWeight.BOLD))
                self.add_purchase_recommendations(analysis, need_to_save, monthly_savings, current_month)
                
            else:
                analysis.append(ft.Divider())
                analysis.append(ft.Text("🚨 КРИТИЧЕСКАЯ СИТУАЦИЯ:", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.RED))
                analysis.append(ft.Text("• СРОЧНО: Сократите расходы!", size=14, color=ft.Colors.RED))
                analysis.append(ft.Text("• Накопления отрицательные", size=14, color=ft.Colors.RED))
                analysis.append(ft.Text("• Нужно увеличить доходы или уменьшить траты", size=14, color=ft.Colors.RED))
        
        return ft.Column(analysis, spacing=8)
    
    def get_holidays_for_month(self, month):
        holidays = []
        if month == 1:
            holidays.append("Новый год")
        elif month == 2:
            holidays.append("День Святого Валентина")
        elif month == 3:
            holidays.append("8 Марта")
        return holidays
    
    def get_birthdays_for_month(self, month):
        birthdays = []
        for birthday in self.finance_app.data["birthdays"]:
            if self.convert_month_to_int(birthday["month"]) == month:
                birthdays.append({
                    "name": birthday["name"],
                    "relationship": birthday["relationship"],
                    "gift_cost": birthday.get("gift_cost", 2000)
                })
        return birthdays
    
    def get_months_analysis(self):
        """Анализ месяцев с учетом праздников и дней рождения"""
        months_analysis = {
            1: {"name": "Январь", "good": True, "cost": 0, "reason": ""},
            2: {"name": "Февраль", "good": True, "cost": 0, "reason": ""},
            3: {"name": "Март", "good": True, "cost": 0, "reason": ""},
            4: {"name": "Апрель", "good": True, "cost": 0, "reason": ""},
            5: {"name": "Май", "good": True, "cost": 0, "reason": ""},
            6: {"name": "Июнь", "good": True, "cost": 0, "reason": ""},
            7: {"name": "Июль", "good": True, "cost": 0, "reason": ""},
            8: {"name": "Август", "good": True, "cost": 0, "reason": ""},
            9: {"name": "Сентябрь", "good": True, "cost": 0, "reason": ""},
            10: {"name": "Октябрь", "good": True, "cost": 0, "reason": ""},
            11: {"name": "Ноябрь", "good": True, "cost": 0, "reason": ""},
            12: {"name": "Декабрь", "good": True, "cost": 0, "reason": ""}
        }
        
        # Добавляем праздники
        holiday_months = {
            2: 3000,  # День святого Валентина
            3: 5000,  # 8 Марта
            5: 2000,  # День Победы
            6: 2000,  # День России
            11: 2000, # День народного единства
            12: 15000 # Новый год
        }
        
        for month, cost in holiday_months.items():
            months_analysis[month]["cost"] = cost
            months_analysis[month]["good"] = False
            months_analysis[month]["reason"] = "Праздник"
        
        # Добавляем дни рождения
        for birthday in self.finance_app.data["birthdays"]:
            month = self.convert_month_to_int(birthday["month"])
            if month in months_analysis:
                months_analysis[month]["cost"] += birthday.get("gift_cost", 2000)
                months_analysis[month]["good"] = months_analysis[month]["cost"] < 5000
                if months_analysis[month]["reason"]:
                    months_analysis[month]["reason"] += f" + ДР {birthday['name']}"
                else:
                    months_analysis[month]["reason"] = f"ДР {birthday['name']}"
        
        return months_analysis
    
    def get_month_name(self, month):
        months = ["", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                 "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
        return months[month]
    
    def add_monthly_savings_plan(self, analysis, need_to_save, monthly_savings, current_month):
        saved_amount = 0
        month = current_month
        
        for i in range(12):  # Показываем максимум 12 месяцев
            if saved_amount >= need_to_save:
                break
                
            month_name = self.get_month_name(month)
            holidays = self.get_holidays_for_month(month)
            birthdays = self.get_birthdays_for_month(month)
            
            # Определяем, сколько можно отложить в этом месяце
            if holidays or birthdays:
                # В месяце с праздниками/ДР откладываем меньше
                monthly_save = monthly_savings * 0.5
            else:
                monthly_save = monthly_savings
            
            saved_amount += monthly_save
            remaining = max(0, need_to_save - saved_amount)
            
            status = "✅ ГОТОВО" if remaining == 0 else f"Осталось: {remaining:,.0f} ₽"
            color = ft.Colors.GREEN if remaining == 0 else ft.Colors.BLUE
            
            month_info = f"• {month_name}: +{monthly_save:,.0f} ₽ (накоплено: {min(saved_amount, need_to_save):,.0f} ₽) - {status}"
            
            if holidays:
                month_info += f" [Праздники: {', '.join(holidays)}]"
            if birthdays:
                month_info += f" [ДР: {', '.join(birthdays)}]"
            
            analysis.append(ft.Text(month_info, size=12, color=color))
            
            month = (month % 12) + 1
    
    def add_purchase_recommendations(self, analysis, need_to_save, monthly_savings, current_month):
        # Анализируем лучшие месяцы для покупки
        months_analysis = {
            1: {"name": "Январь", "holiday": "", "cost": 0, "good": True, "reason": "Спокойный месяц"},
            2: {"name": "Февраль", "holiday": "День Святого Валентина", "cost": 5000, "good": True, "reason": "Хороший месяц - мало трат"},
            3: {"name": "Март", "holiday": "8 Марта", "cost": 3000, "good": True, "reason": "Хороший месяц - мало трат"},
            4: {"name": "Апрель", "holiday": "Нет", "cost": 0, "good": True, "reason": "Отличный месяц - нет праздников"},
            5: {"name": "Май", "holiday": "Нет", "cost": 0, "good": True, "reason": "Отличный месяц - нет праздников"},
            6: {"name": "Июнь", "holiday": "Нет", "cost": 0, "good": True, "reason": "Отличный месяц - нет праздников"},
            7: {"name": "Июль", "holiday": "Нет", "cost": 0, "good": True, "reason": "Отличный месяц - нет праздников"},
            8: {"name": "Август", "holiday": "Нет", "cost": 0, "good": True, "reason": "Отличный месяц - нет праздников"},
            9: {"name": "Сентябрь", "holiday": "Нет", "cost": 0, "good": True, "reason": "Отличный месяц - нет праздников"},
            10: {"name": "Октябрь", "holiday": "Нет", "cost": 0, "good": True, "reason": "Отличный месяц - нет праздников"},
            11: {"name": "Ноябрь", "holiday": "Нет", "cost": 0, "good": True, "reason": "Отличный месяц - нет праздников"},
            12: {"name": "Декабрь", "holiday": "Новый год", "cost": 20000, "good": False, "reason": "Дорогой месяц - много трат на праздники"}
        }
        
        # Добавляем дни рождения
        birthdays = self.finance_app.data["birthdays"]
        for birthday in birthdays:
            month = self.convert_month_to_int(birthday["month"])
            if month in months_analysis:
                months_analysis[month]["cost"] += birthday["cost"]
                months_analysis[month]["good"] = months_analysis[month]["cost"] < 5000
                if birthday["cost"] > 0:
                    months_analysis[month]["reason"] += f" + ДР {birthday['name']}"
        
        # Находим лучшие месяцы
        good_months = [data for data in months_analysis.values() if data["good"]]
        bad_months = [data for data in months_analysis.values() if not data["good"]]
        
        # Рекомендуем лучшие месяцы
        if good_months:
            analysis.append(ft.Text("✅ Лучшие месяцы для покупки:", size=14, color=ft.Colors.GREEN))
            for month_data in good_months[:3]:  # Показываем топ-3
                analysis.append(ft.Text(f"• {month_data['name']}: {month_data['reason']}", size=12, color=ft.Colors.GREEN))
        
        # Предупреждаем о плохих месяцах
        if bad_months:
            analysis.append(ft.Text("❌ Избегайте покупок в:", size=14, color=ft.Colors.RED))
            for month_data in bad_months:
                analysis.append(ft.Text(f"• {month_data['name']}: {month_data['reason']}", size=12, color=ft.Colors.RED))
        
        # Конкретная рекомендация
        if monthly_savings > 0:
            months_needed = need_to_save / monthly_savings
            recommended_month = good_months[0]["name"] if good_months else "Любой месяц"
            analysis.append(ft.Text(f"💡 Рекомендация: Начните копить сейчас, покупайте в {recommended_month}", size=14, color=ft.Colors.BLUE))
        else:
            analysis.append(ft.Text("💡 Рекомендация: Сначала исправьте финансовую ситуацию", size=14, color=ft.Colors.ORANGE))
    
    def update_new_category(self, e):
        self.new_category_field = e.control
        self.page.update()
    
    def add_custom_category(self, e):
        if hasattr(self, 'new_category_field') and self.new_category_field.value:
            category_name = self.new_category_field.value.strip()
            category_key = category_name.lower().replace(" ", "_")
            
            # Добавляем в список категорий
            if "custom_categories" not in self.finance_app.data:
                self.finance_app.data["custom_categories"] = []
            
            if category_key not in [cat["key"] for cat in self.finance_app.data["custom_categories"]]:
                self.finance_app.data["custom_categories"].append({
                    "key": category_key,
                    "name": category_name,
                    "icon": "📦"
                })
                self.finance_app.save_data()
                self.refresh_all_pages()
                
                # Очищаем поле
                self.new_category_field.value = ""
                self.page.update()
    
    def find_best_month_for_purchase(self):
        # Анализируем месяцы для покупки
        months_analysis = {
            1: {"name": "Январь", "holiday": "", "cost": 0, "good": True},
            2: {"name": "Февраль", "holiday": "День Святого Валентина", "cost": 5000, "good": True},
            3: {"name": "Март", "holiday": "8 Марта", "cost": 3000, "good": True},
            4: {"name": "Апрель", "holiday": "Нет", "cost": 0, "good": True},
            5: {"name": "Май", "holiday": "Нет", "cost": 0, "good": True},
            6: {"name": "Июнь", "holiday": "Нет", "cost": 0, "good": True},
            7: {"name": "Июль", "holiday": "Нет", "cost": 0, "good": True},
            8: {"name": "Август", "holiday": "Нет", "cost": 0, "good": True},
            9: {"name": "Сентябрь", "holiday": "Нет", "cost": 0, "good": True},
            10: {"name": "Октябрь", "holiday": "Нет", "cost": 0, "good": True},
            11: {"name": "Ноябрь", "holiday": "Нет", "cost": 0, "good": True},
            12: {"name": "Декабрь", "holiday": "Новый год", "cost": 20000, "good": False}
        }
        
        # Добавляем дни рождения
        birthdays = self.finance_app.data["birthdays"]
        for birthday in birthdays:
            month = self.convert_month_to_int(birthday["month"])
            if month in months_analysis:
                months_analysis[month]["cost"] += birthday["cost"]
                months_analysis[month]["good"] = months_analysis[month]["cost"] < 5000
        
        # Находим лучший месяц
        good_months = [data["name"] for data in months_analysis.values() if data["good"]]
        return good_months[0] if good_months else "Любой месяц"
    
    def create_financial_plan(self):
        current_money = self.finance_app.data["current_money"]
        salary = self.finance_app.data["salary"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        current_month_expenses = self.get_current_month_expenses()
        current_month_income = self.get_current_month_income()
        
        # Анализ текущей ситуации
        free_money = current_money - safety_reserve
        rent_cost = self.finance_app.data.get("rent_cost", 25000)
        monthly_savings = salary - self.calculate_average_monthly_expenses() - (3000 if self.finance_app.data["chatgpt_enabled"] else 0) - rent_cost
        
        # Определяем статус
        if free_money < 0:
            status = "🔴 КРИТИЧНО"
            status_color = ft.Colors.RED
            advice = "Срочно нужно пополнить счет!"
        elif free_money < safety_reserve * 0.5:
            status = "🟡 ВНИМАНИЕ"
            status_color = ft.Colors.ORANGE
            advice = "Мало свободных денег, будьте осторожны"
        elif free_money < safety_reserve:
            status = "🟠 ОСТОРОЖНО"
            status_color = ft.Colors.ORANGE
            advice = "Приближаетесь к минимальному резерву"
        else:
            status = "🟢 ОТЛИЧНО"
            status_color = ft.Colors.GREEN
            advice = "Финансовая ситуация стабильная"
        
        return ft.Column([
            ft.Row([
                ft.Text(f"Статус: {status}", size=16, weight=ft.FontWeight.BOLD, color=status_color),
                ft.Text(f"Свободно: {free_money:,.0f} ₽", size=16, color=ft.Colors.BLUE)
            ]),
            ft.Text(advice, size=14, color=status_color),
            ft.Divider(),
            
            ft.Text("📊 Ваша финансовая картина:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"• Всего денег: {current_money:,.0f} ₽", size=14),
            ft.Text(f"• Резерв безопасности: {safety_reserve:,.0f} ₽", size=14),
            ft.Text(f"• Свободно для трат: {free_money:,.0f} ₽", size=14, color=ft.Colors.GREEN if free_money >= 0 else ft.Colors.RED),
            ft.Text(f"• Зарплата в месяц: {salary:,.0f} ₽", size=14),
            ft.Text(f"• Можете копить: {monthly_savings:,.0f} ₽/мес", size=14, color=ft.Colors.BLUE if monthly_savings > 0 else ft.Colors.RED),
            
            ft.Divider(),
            
            ft.Text("🎯 Мой план для вас:", size=16, weight=ft.FontWeight.BOLD),
            self.get_personalized_plan(free_money, monthly_savings, safety_reserve)
        ], spacing=10)
    
    def get_personalized_plan(self, free_money, monthly_savings, safety_reserve):
        plans = []
        
        if free_money < 0:
            plans.append("1. СРОЧНО: Пополните счет на 20,000+ ₽")
            plans.append("2. НЕ ТРАТЬТЕ ничего до пополнения")
            plans.append("3. Используйте кредитку только в крайнем случае")
        elif free_money < safety_reserve * 0.5:
            plans.append("1. Сократите траты до минимума")
            plans.append("2. Копите до 20,000 ₽ резерва")
            plans.append("3. Не покупайте ничего дорогого")
        elif free_money < safety_reserve:
            plans.append("1. Осторожно с тратами")
            plans.append("2. Копите до полного резерва")
            plans.append("3. Отложите крупные покупки")
        else:
            plans.append("1. Можете тратить свободно")
            plans.append("2. Копите на цели")
            plans.append("3. Планируйте крупные покупки")
        
        if monthly_savings > 0:
            plans.append(f"4. Откладывайте {monthly_savings:,.0f} ₽ каждый месяц")
        else:
            plans.append("4. СРОЧНО: Сократите расходы!")
        
        return ft.Column([
            ft.Text(plan, size=12, color=ft.Colors.BLUE) for plan in plans
        ], spacing=5)
    
    def create_savings_strategy(self):
        current_money = self.finance_app.data["current_money"]
        salary = self.finance_app.data["salary"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        monthly_expenses = self.calculate_average_monthly_expenses()
        chatgpt_cost = 3000 if self.finance_app.data["chatgpt_enabled"] else 0
        goals = self.finance_app.data["goals"]
        
        # Получаем информацию о квартплате
        rent_paid_until = self.finance_app.data.get("rent_paid_until", "")
        current_date = datetime(2025, datetime.now().month, datetime.now().day)
        
        # Определяем, нужно ли платить квартплату в текущем месяце
        def should_pay_rent_current():
            if not rent_paid_until:
                return True
            try:
                paid_until = datetime.strptime(rent_paid_until, "%Y-%m-%d")
                return current_date > paid_until
            except:
                return True
        
        rent_cost = self.finance_app.data.get("rent_cost", 25000)
        rent_for_current_month = rent_cost if should_pay_rent_current() else 0
        
        # Расчеты с учетом квартплаты и реальной даты
        # Если сегодня конец месяца (последние 2 дня), то накопления не актуальны
        current_day = datetime.now().day
        current_month = datetime.now().month
        current_year = 2025
        current_year = 2025  # Устанавливаем 2025 год
        days_in_month = 30  # Сентябрь
        if current_day >= days_in_month - 1:  # 29-30 сентября
            monthly_savings = 0  # В конце месяца копить не нужно
        else:
            # Для текущего месяца используем rent_for_current_month, для будущих - всегда rent_cost
            monthly_savings = salary - monthly_expenses - chatgpt_cost - rent_cost
        free_money = current_money - safety_reserve
        
        # Анализируем месяцы с учетом праздников и ДР
        months_analysis = {
            1: {"name": "Январь", "holiday": "", "cost": 0, "good": True},
            2: {"name": "Февраль", "holiday": "День Святого Валентина", "cost": 5000, "good": True},
            3: {"name": "Март", "holiday": "8 Марта", "cost": 3000, "good": True},
            4: {"name": "Апрель", "holiday": "Нет", "cost": 0, "good": True},
            5: {"name": "Май", "holiday": "Нет", "cost": 0, "good": True},
            6: {"name": "Июнь", "holiday": "Нет", "cost": 0, "good": True},
            7: {"name": "Июль", "holiday": "Нет", "cost": 0, "good": True},
            8: {"name": "Август", "holiday": "Нет", "cost": 0, "good": True},
            9: {"name": "Сентябрь", "holiday": "Нет", "cost": 0, "good": True},
            10: {"name": "Октябрь", "holiday": "Нет", "cost": 0, "good": True},
            11: {"name": "Ноябрь", "holiday": "Нет", "cost": 0, "good": True},
            12: {"name": "Декабрь", "holiday": "Новый год", "cost": 20000, "good": False}
        }
        
        # Добавляем дни рождения
        birthdays = self.finance_app.data["birthdays"]
        for birthday in birthdays:
            month = self.convert_month_to_int(birthday["month"])
            if month in months_analysis:
                months_analysis[month]["cost"] += birthday["cost"]
                months_analysis[month]["good"] = months_analysis[month]["cost"] < 5000
        
        good_months = [data["name"] for data in months_analysis.values() if data["good"]]
        bad_months = [data["name"] for data in months_analysis.values() if not data["good"]]
        
        # Анализ целей и лучших дней для накоплений
        salary_dates = self.finance_app.data["salary_dates"]
        current_day = datetime.now().day
        current_month = datetime.now().month
        current_year = 2025
        
        def analyze_goals():
            """Анализирует цели и дает рекомендации"""
            if not goals:
                return ft.Column([
                    ft.Text("🎯 У вас нет целей!", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE),
                    ft.Text("Без целей копить не имеет смысла - деньги просто лежат без цели", size=12, color=ft.Colors.GREY_600),
                    ft.Divider(),
                    ft.Text("💡 Зачем нужны цели:", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text("• Понять, сколько нужно копить каждый месяц", size=12),
                    ft.Text("• Выбрать лучший месяц для начала накоплений", size=12),
                    ft.Text("• Рассчитать точные сроки достижения цели", size=12),
                    ft.Text("• Получить мотивацию и контроль над финансами", size=12),
                    ft.Divider(),
                    ft.Text("🎯 Рекомендация:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                    ft.Text("1. Добавьте цель во вкладке 'Цели'", size=12),
                    ft.Text("2. Тогда получите персональный план накоплений", size=12),
                    ft.Text("3. Пока что просто тратьте разумно", size=12)
                ], spacing=5)
            
            goal_analysis = []
            for goal in goals:
                goal_name = goal["name"]
                goal_amount = goal["amount"]
                goal_saved = goal.get("saved", 0)
                remaining = goal_amount - goal_saved
                
                if remaining <= 0:
                    goal_analysis.append(ft.Text(f"✅ {goal_name} - ВЫПОЛНЕНА!", size=12, color=ft.Colors.GREEN))
                    continue
                
                # Рассчитываем, сколько нужно копить в месяц
                months_needed = remaining / max(monthly_savings, 1)
                
                # Находим лучший месяц для начала
                best_month = self.find_best_month_for_goal(months_analysis, current_month)
                best_day = self.find_best_day_for_goal(salary_dates, current_day)
                
                goal_analysis.extend([
                    ft.Text(f"🎯 {goal_name}: {remaining:,.0f} ₽", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"• Нужно копить: {remaining/months_needed:,.0f} ₽/мес", size=12, color=ft.Colors.BLUE),
                    ft.Text(f"• Время накопления: {months_needed:.1f} месяцев", size=12),
                    ft.Text(f"• Лучший месяц: {best_month}", size=12, color=ft.Colors.GREEN),
                    ft.Text(f"• Лучший день: {best_day}", size=12, color=ft.Colors.GREEN),
                    ft.Divider()
                ])
            
            return ft.Column(goal_analysis, spacing=5)
        
        
        def get_best_days_for_saving():
            """Определяет лучшие дни для начала накоплений на основе прогноза и аналитики"""
            best_days = []
            
            # Если конец месяца, то копить не нужно
            if current_day >= days_in_month - 1:
                return ["Копить не нужно - конец месяца"]
            
            # Если нет целей, то копить не нужно
            if not goals:
                return ["Добавьте цель во вкладке 'Цели'"]
            
            # Анализируем текущий месяц
            current_month_data = months_analysis.get(current_month, {"good": True, "cost": 0})
            
            # Если текущий месяц хороший для накоплений
            if current_month_data["good"]:
                # Можно копить с любой зарплаты
                for salary_day in salary_dates:
                    if current_day <= salary_day:
                        best_days.append(f"{salary_day} число (хороший месяц для накоплений)")
            else:
                # Плохой месяц - лучше копить с первой зарплаты
                if current_day <= salary_dates[0]:
                    best_days.append(f"{salary_dates[0]} число (до праздников)")
                elif current_day <= salary_dates[1]:
                    best_days.append(f"{salary_dates[1]} число (после первой ЗП)")
            
            # Если сегодня после второй зарплаты, то следующий месяц
            if current_day > salary_dates[1]:
                next_month = current_month + 1 if current_month < 12 else 1
                next_month_data = months_analysis.get(next_month, {"good": True, "cost": 0})
                if next_month_data["good"]:
                    best_days.append("1 число следующего месяца (хороший месяц)")
                else:
                    best_days.append("1 число следующего месяца (плохой месяц)")
            
            # Дни в конце месяца (если есть свободные деньги)
            if free_money > 5000:
                best_days.append("Сегодня (есть свободные деньги)")
            
            return best_days if best_days else ["В любой день после зарплаты"]
        
        best_days = get_best_days_for_saving()
        
        # Рекомендации по накоплениям
        if monthly_savings > 0:
            time_to_reserve = (safety_reserve - free_money) / monthly_savings if free_money < safety_reserve else 0
            recommendation = f"Можете копить {monthly_savings:,.0f} ₽/мес"
        else:
            time_to_reserve = 999
            recommendation = "СРОЧНО сократите расходы!"
        
        return ft.Column([
            ft.Text("🎯 Анализ ваших целей:", size=16, weight=ft.FontWeight.BOLD),
            analyze_goals(),
            
            ft.Text("📊 Ваши финансовые возможности:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"• Зарплата: {salary:,.0f} ₽/мес", size=14, color=ft.Colors.GREEN),
            ft.Text(f"• Средние расходы: {monthly_expenses:,.0f} ₽/мес", size=14, color=ft.Colors.RED),
            ft.Text(f"• ChatGPT Plus: {chatgpt_cost:,.0f} ₽/мес", size=14, color=ft.Colors.ORANGE),
            ft.Text(f"• Квартплата: {rent_cost:,.0f} ₽/мес", size=14, color=ft.Colors.ORANGE),
            ft.Text(f"• Сегодня: {datetime.now().strftime('%d %B %Y')}", size=14, color=ft.Colors.BLUE),
            ft.Text(f"• Можете копить: {monthly_savings:,.0f} ₽/мес", size=14, color=ft.Colors.BLUE, weight=ft.FontWeight.BOLD) if monthly_savings > 0 else ft.Text("• Копить не нужно - конец месяца", size=14, color=ft.Colors.ORANGE),
            ft.Text(f"• Свободно для трат: {free_money:,.0f} ₽", size=14, color=ft.Colors.GREEN),
            
            ft.Divider(),
            
            ft.Text("🎯 Лучшие дни для начала накоплений:", size=16, weight=ft.FontWeight.BOLD),
            *[ft.Text(f"• {day}", size=12, color=ft.Colors.GREEN) for day in best_days],
            
            ft.Divider(),
            
            ft.Text("📋 Конкретный план:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("1. Добавьте цель во вкладке 'Цели'", size=12),
            ft.Text("2. Начинайте копить в лучший день", size=12),
            ft.Text("3. Откладывайте сразу после зарплаты", size=12),
            ft.Text("4. Не трогайте накопления", size=12),
            ft.Text("5. Покупайте крупное в хорошие месяцы", size=12)
        ], spacing=10)
    
    def find_best_month_for_goal(self, months_analysis, current_month):
        """Находит лучший месяц для начала накоплений на цель"""
        good_months = [data["name"] for data in months_analysis.values() if data["good"]]
        
        # Если есть хорошие месяцы, выбираем ближайший
        if good_months:
            month_names = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", 
                          "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
            current_month_name = month_names[current_month - 1]
            
            # Ищем ближайший хороший месяц
            for i in range(12):
                check_month = (current_month + i - 1) % 12
                month_name = month_names[check_month]
                if month_name in good_months:
                    return month_name
        
        return "Любой месяц"
    
    def find_best_day_for_goal(self, salary_dates, current_day):
        """Находит лучший день для начала накоплений на цель"""
        # Дни после зарплаты - лучшие для начала накоплений
        for salary_day in salary_dates:
            if current_day <= salary_day:
                return f"{salary_day} число (после зарплаты)"
        
        # Если сегодня после второй зарплаты, то следующий месяц
        if current_day > salary_dates[1]:
            return "1 число следующего месяца"
        
        return "В любой день после зарплаты"
    
    def create_critical_warnings(self):
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        rent_cost = self.finance_app.data.get("rent_cost", 25000)
        monthly_savings = self.finance_app.data["salary"] - self.calculate_average_monthly_expenses() - (3000 if self.finance_app.data["chatgpt_enabled"] else 0) - rent_cost
        
        warnings = []
        
        # Проверяем критические ситуации
        if current_money < safety_reserve:
            warnings.append({
                "level": "🔴 КРИТИЧНО",
                "message": f"Денег меньше резерва! {current_money:,.0f} ₽ < {safety_reserve:,.0f} ₽",
                "action": "СРОЧНО пополните счет!",
                "color": ft.Colors.RED
            })
        
        if monthly_savings < 0:
            warnings.append({
                "level": "🔴 КРИТИЧНО", 
                "message": f"Тратите больше чем зарабатываете!",
                "action": "СРОЧНО сократите расходы!",
                "color": ft.Colors.RED
            })
        
        if current_money < safety_reserve * 1.5:
            warnings.append({
                "level": "🟡 ВНИМАНИЕ",
                "message": f"Мало свободных денег",
                "action": "Будьте осторожны с тратами",
                "color": ft.Colors.ORANGE
            })
        
        if not warnings:
            warnings.append({
                "level": "🟢 ВСЕ ОТЛИЧНО",
                "message": "Финансовая ситуация стабильная",
                "action": "Продолжайте в том же духе!",
                "color": ft.Colors.GREEN
            })
        
        return ft.Column([
            ft.Text(warning["level"], size=16, weight=ft.FontWeight.BOLD, color=warning["color"]) for warning in warnings
        ] + [
            ft.Text(warning["message"], size=14) for warning in warnings
        ] + [
            ft.Text(f"Действие: {warning['action']}", size=12, color=warning["color"]) for warning in warnings
        ], spacing=10)
    
    def create_expense_analysis(self):
        current_month_expenses = self.get_current_month_expenses()
        avg_monthly_expenses = self.calculate_average_monthly_expenses()
        
        # Анализ категорий трат
        transactions = self.finance_app.data["transactions"]
        current_month = datetime.now().strftime("%Y-%m")
        
        categories = {}
        for transaction in transactions:
            if transaction["type"] == "expense" and transaction["date"].startswith(current_month):
                category = transaction.get("category", "other")
                amount = transaction["amount"]
                categories[category] = categories.get(category, 0) + amount
        
        # Сортируем по убыванию
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        
        return ft.Column([
            ft.Text("📊 Ваши траты в этом месяце:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"• Всего потрачено: {current_month_expenses:,.0f} ₽", size=14, color=ft.Colors.RED),
            ft.Text(f"• Средние траты: {avg_monthly_expenses:,.0f} ₽/мес", size=14),
            
            ft.Divider(),
            
            ft.Text("📈 По категориям:", size=16, weight=ft.FontWeight.BOLD),
            *[ft.Text(f"• {self.get_category_name(cat)}: {amount:,.0f} ₽", size=12, color=ft.Colors.BLUE) for cat, amount in sorted_categories[:5]],
            
            ft.Divider(),
            
            ft.Text("💡 Рекомендации:", size=16, weight=ft.FontWeight.BOLD),
            self.get_expense_recommendations(categories, current_month_expenses, avg_monthly_expenses),
            
            ft.Divider(),
            
            ft.Text("➕ Добавить категорию:", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.TextField(
                    label="Название категории",
                    on_change=self.update_new_category,
                    expand=True
                ),
                ft.ElevatedButton(
                    "Добавить",
                    on_click=self.add_custom_category,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_400)
                )
            ])
        ], spacing=10)
    
    def get_category_name(self, category):
        names = {
            "food": "🍎 Еда",
            "restaurants": "🍽️ Рестораны",
            "games": "🎮 Игры", 
            "transport": "🚗 Транспорт",
            "clothing": "👕 Одежда",
            "electronics": "📱 Электроника",
            "entertainment": "🎬 Развлечения",
            "other": "📦 Прочее"
        }
        
        # Проверяем кастомные категории
        if "custom_categories" in self.finance_app.data:
            for cat in self.finance_app.data["custom_categories"]:
                if cat["key"] == category:
                    return f"{cat['icon']} {cat['name']}"
        
        return names.get(category, "📦 Прочее")
    
    def get_expense_recommendations(self, categories, current_expenses, avg_expenses):
        recommendations = []
        
        if current_expenses > avg_expenses * 1.2:
            recommendations.append("⚠️ Тратите больше обычного!")
        
        if categories.get("games", 0) > 5000:
            recommendations.append("🎮 Много тратите на игры - установите лимит")
        
        if categories.get("restaurants", 0) > 10000:
            recommendations.append("🍽️ Много тратите в ресторанах - готовьте дома")
        
        if categories.get("electronics", 0) > 20000:
            recommendations.append("📱 Крупная покупка электроники - планируйте заранее")
        
        if not recommendations:
            recommendations.append("✅ Траты в норме")
        
        return ft.Column([
            ft.Text(rec, size=12, color=ft.Colors.BLUE) for rec in recommendations
        ], spacing=5)
    
    def create_goals_analysis(self):
        goals = self.finance_app.data["goals"]
        goal_investments = self.finance_app.data["goal_investments"]
        rent_cost = self.finance_app.data.get("rent_cost", 25000)
        monthly_savings = self.finance_app.data["salary"] - self.calculate_average_monthly_expenses() - (3000 if self.finance_app.data["chatgpt_enabled"] else 0) - rent_cost
        
        if not goals:
            return ft.Column([
                ft.Text("🎯 У вас нет целей", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("Добавьте цели на вкладке 'Цели'", size=14, color=ft.Colors.GREY_600)
            ])
        
        goal_analysis = []
        for goal in goals:
            goal_name = goal["name"]
            goal_amount = goal["amount"]
            invested = goal_investments.get(goal_name, 0)
            remaining = goal_amount - invested
            progress = (invested / goal_amount * 100) if goal_amount > 0 else 0
            
            if monthly_savings > 0:
                months_to_goal = remaining / monthly_savings
            else:
                months_to_goal = 999
            
            goal_analysis.append({
                "name": goal_name,
                "amount": goal_amount,
                "invested": invested,
                "remaining": remaining,
                "progress": progress,
                "months": months_to_goal
            })
        
        return ft.Column([
            ft.Text("🎯 Анализ ваших целей:", size=16, weight=ft.FontWeight.BOLD),
            *[ft.Column([
                ft.Text(f"• {goal['name']}: {goal['invested']:,.0f} ₽ из {goal['amount']:,.0f} ₽", size=14),
                ft.Text(f"  Прогресс: {goal['progress']:.1f}%", size=12, color=ft.Colors.BLUE),
                ft.Text(f"  Осталось: {goal['remaining']:,.0f} ₽", size=12, color=ft.Colors.ORANGE),
                ft.Text(f"  Время до цели: {goal['months']:.1f} месяцев", size=12, color=ft.Colors.GREEN if goal['months'] < 12 else ft.Colors.RED),
                ft.Divider()
            ]) for goal in goal_analysis]
        ], spacing=10)
    
    def create_detailed_monthly_analysis(self):
        """Создает детальный анализ по месяцам с максимальной информацией"""
        current_month = datetime.now().month
        months_analysis = self.get_months_analysis()
        goals = self.finance_app.data["goals"]
        goal_investments = self.finance_app.data["goal_investments"]
        rent_cost = self.finance_app.data.get("rent_cost", 25000)
        monthly_savings = self.finance_app.data["salary"] - self.calculate_average_monthly_expenses() - (3000 if self.finance_app.data["chatgpt_enabled"] else 0) - rent_cost
        
        # Рассчитываем общую сумму целей
        total_goals = sum(goal["amount"] for goal in goals)
        total_invested = sum(goal_investments.values())
        remaining_goals = total_goals - total_invested
        
        # Создаем заголовок таблицы
        header = ft.Container(
            content=ft.Row([
                ft.Text("Месяц", size=14, weight=ft.FontWeight.BOLD, expand=1),
                ft.Text("Статус", size=14, weight=ft.FontWeight.BOLD, expand=1, text_align=ft.TextAlign.CENTER),
                ft.Text("Праздники", size=14, weight=ft.FontWeight.BOLD, expand=1, text_align=ft.TextAlign.CENTER),
                ft.Text("Дни рождения", size=14, weight=ft.FontWeight.BOLD, expand=1, text_align=ft.TextAlign.CENTER),
                ft.Text("Доп. расходы", size=14, weight=ft.FontWeight.BOLD, expand=1, text_align=ft.TextAlign.CENTER),
                ft.Text("Накопления", size=14, weight=ft.FontWeight.BOLD, expand=1, text_align=ft.TextAlign.CENTER),
                ft.Text("Лучший для накоплений", size=14, weight=ft.FontWeight.BOLD, expand=1, text_align=ft.TextAlign.CENTER),
                ft.Text("Детали", size=14, weight=ft.FontWeight.BOLD, expand=2, text_align=ft.TextAlign.CENTER)
            ]),
            bgcolor=ft.Colors.BLUE_50,
            padding=12,
            border=ft.border.all(1, ft.Colors.BLUE_200)
        )
        
        # Создаем строки таблицы
        table_rows = []
        for month_num, data in months_analysis.items():
            month_name = data["name"]
            holiday_cost = data["cost"]
            
            # Получаем информацию о днях рождения
            birthdays = self.get_birthdays_for_month(month_num)
            birthday_names = [bday["name"] for bday in birthdays]
            birthday_cost = sum(bday["gift_cost"] for bday in birthdays)
            
            # Рассчитываем общие дополнительные расходы
            total_extra_costs = holiday_cost + birthday_cost
            
            # Рассчитываем доступную сумму для накоплений
            available_for_savings = max(0, monthly_savings - total_extra_costs)
            
            # Умная логика определения статуса месяца
            if total_extra_costs == 0:
                status = "Отличный"
                status_color = ft.Colors.GREEN
                status_icon = "✅"
                status_reason = "Никаких дополнительных трат"
            elif total_extra_costs < monthly_savings * 0.2:
                status = "Хороший"
                status_color = ft.Colors.LIGHT_GREEN
                status_icon = "👍"
                status_reason = f"Доп. траты: {total_extra_costs:,.0f} ₽"
            elif total_extra_costs < monthly_savings * 0.5:
                status = "Осторожно"
                status_color = ft.Colors.ORANGE
                status_icon = "⚠️"
                status_reason = f"Много доп. трат: {total_extra_costs:,.0f} ₽"
            else:
                status = "Опасно"
                status_color = ft.Colors.RED
                status_icon = "🚨"
                status_reason = f"Критично много трат: {total_extra_costs:,.0f} ₽"
            
            # Формируем информацию о праздниках
            holiday_info = "Нет праздников"
            if holiday_cost > 0:
                holiday_names = []
                if month_num == 2:
                    holiday_names.append("День святого Валентина")
                if month_num == 3:
                    holiday_names.append("8 Марта")
                if month_num == 5:
                    holiday_names.append("День Победы")
                if month_num == 6:
                    holiday_names.append("День России")
                if month_num == 11:
                    holiday_names.append("День народного единства")
                if month_num == 12:
                    holiday_names.append("Новый год")
                holiday_info = f"{', '.join(holiday_names)}\n({holiday_cost:,.0f} ₽)"
            
            # Формируем информацию о днях рождения
            birthday_info = "Нет ДР"
            if birthday_names:
                birthday_info = f"{', '.join(birthday_names)}\n({birthday_cost:,.0f} ₽)"
            
            # Определяем, является ли месяц лучшим для накоплений
            if total_extra_costs == 0:
                best_for_saving = "✅ Отличный"
                best_color = ft.Colors.GREEN
            elif total_extra_costs < monthly_savings * 0.2:
                best_for_saving = "👍 Хороший"
                best_color = ft.Colors.LIGHT_GREEN
            elif total_extra_costs < monthly_savings * 0.5:
                best_for_saving = "⚠️ Осторожно"
                best_color = ft.Colors.ORANGE
            else:
                best_for_saving = "❌ Избегайте"
                best_color = ft.Colors.RED
            
            # Формируем детальную информацию
            if goals:
                if available_for_savings > 0:
                    months_to_goal = remaining_goals / available_for_savings if available_for_savings > 0 else 999
                    details = f"Нужно накопить: {available_for_savings:,.0f} ₽\nДо цели: {months_to_goal:.1f} мес\nСвободно: {monthly_savings - total_extra_costs:,.0f} ₽"
                else:
                    details = f"Не копите в этом месяце\nСлишком много трат\nДефицит: {total_extra_costs - monthly_savings:,.0f} ₽"
            else:
                details = f"Нет цели\nДобавьте цель для планирования\nСвободно: {monthly_savings - total_extra_costs:,.0f} ₽"
            
            # Создаем строку таблицы
            row = ft.Container(
                content=ft.Row([
                    ft.Text(month_name, size=12, weight=ft.FontWeight.BOLD, expand=1),
                    ft.Column([
                        ft.Text(f"{status_icon} {status}", size=12, color=status_color, text_align=ft.TextAlign.CENTER),
                        ft.Text(status_reason, size=10, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)
                    ], expand=1, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Text(holiday_info, size=11, color=ft.Colors.PURPLE, expand=1, text_align=ft.TextAlign.CENTER),
                    ft.Text(birthday_info, size=11, color=ft.Colors.PINK, expand=1, text_align=ft.TextAlign.CENTER),
                    ft.Text(f"{total_extra_costs:,.0f} ₽", size=12, color=ft.Colors.RED if total_extra_costs > 0 else ft.Colors.GREY, expand=1, text_align=ft.TextAlign.CENTER),
                    ft.Text(f"{available_for_savings:,.0f} ₽" if goals and available_for_savings > 0 else "Нет цели", 
                           size=12, color=ft.Colors.GREEN if goals and available_for_savings > 0 else ft.Colors.GREY, 
                           expand=1, text_align=ft.TextAlign.CENTER),
                    ft.Text(best_for_saving, size=12, color=best_color, expand=1, text_align=ft.TextAlign.CENTER),
                    ft.Text(details, size=10, color=ft.Colors.BLUE, expand=2, text_align=ft.TextAlign.CENTER)
                ]),
                bgcolor=ft.Colors.WHITE if month_num % 2 == 0 else ft.Colors.GREY_50,
                padding=10,
                border=ft.border.all(0.5, ft.Colors.GREY_300)
            )
            table_rows.append(row)
        
        # Создаем итоговую информацию
        summary = ft.Container(
            content=ft.Column([
                ft.Text("📊 Итоговая информация:", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(f"• Общая сумма целей: {total_goals:,.0f} ₽" if goals else "• Нет целей", size=14),
                ft.Text(f"• Уже накоплено: {total_invested:,.0f} ₽" if goals else "", size=14),
                ft.Text(f"• Осталось накопить: {remaining_goals:,.0f} ₽" if goals else "", size=14),
                ft.Text(f"• Средние накопления: {monthly_savings:,.0f} ₽/месяц", size=14),
                ft.Text(f"• Время до всех целей: {remaining_goals / monthly_savings:.1f} месяцев" if goals and monthly_savings > 0 else "", size=14)
            ], spacing=5),
            bgcolor=ft.Colors.LIGHT_BLUE_50,
            padding=15,
            border=ft.border.all(1, ft.Colors.BLUE_200)
        )
        
        # Добавляем объяснение оценок
        explanation = ft.Container(
            content=ft.Column([
                ft.Text("📊 Объяснение оценок для накоплений:", size=14, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Text("✅ Отличный", size=12, color=ft.Colors.GREEN),
                    ft.Text("- нет дополнительных трат", size=11, color=ft.Colors.GREY_600)
                ], spacing=5),
                ft.Row([
                    ft.Text("👍 Хороший", size=12, color=ft.Colors.LIGHT_GREEN),
                    ft.Text("- мало дополнительных трат (<20%)", size=11, color=ft.Colors.GREY_600)
                ], spacing=5),
                ft.Row([
                    ft.Text("⚠️ Осторожно", size=12, color=ft.Colors.ORANGE),
                    ft.Text("- умеренные дополнительные траты (20-50%)", size=11, color=ft.Colors.GREY_600)
                ], spacing=5),
                ft.Row([
                    ft.Text("❌ Избегайте", size=12, color=ft.Colors.RED),
                    ft.Text("- много дополнительных трат (>50%)", size=11, color=ft.Colors.GREY_600)
                ], spacing=5)
            ], spacing=3),
            padding=15,
            bgcolor=ft.Colors.BLUE_50,
            border=ft.border.all(1, ft.Colors.BLUE_200)
        )
        
        return ft.Column([
            header,
            *table_rows,
            ft.Divider(),
            summary,
            ft.Divider(),
            explanation
        ], spacing=0)
    
    def create_action_plan(self):
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        rent_cost = self.finance_app.data.get("rent_cost", 25000)
        monthly_savings = self.finance_app.data["salary"] - self.calculate_average_monthly_expenses() - (3000 if self.finance_app.data["chatgpt_enabled"] else 0) - rent_cost
        
        actions = []
        
        # Приоритетные действия
        if current_money < safety_reserve:
            actions.append("🔴 СРОЧНО: Пополните счет до 20,000 ₽")
        elif current_money < safety_reserve * 1.5:
            actions.append("🟡 ВАЖНО: Копите до полного резерва")
        else:
            actions.append("🟢 ОТЛИЧНО: Резерв в порядке")
        
        if monthly_savings < 0:
            actions.append("🔴 КРИТИЧНО: Сократите расходы!")
        elif monthly_savings < 5000:
            actions.append("🟡 ВНИМАНИЕ: Мало накоплений")
        else:
            actions.append("🟢 ХОРОШО: Можете копить")
        
        # Еженедельные действия
        actions.append("📅 ЕЖЕНЕДЕЛЬНО: Проверяйте баланс")
        actions.append("💰 ЕЖЕНЕДЕЛЬНО: Откладывайте накопления")
        actions.append("📊 ЕЖЕНЕДЕЛЬНО: Анализируйте траты")
        
        # Ежемесячные действия
        actions.append("🎯 ЕЖЕМЕСЯЧНО: Обновляйте цели")
        actions.append("📈 ЕЖЕМЕСЯЧНО: Планируйте крупные покупки")
        
        return ft.Column([
            ft.Text("📋 Ваш план действий:", size=16, weight=ft.FontWeight.BOLD),
            *[ft.Text(action, size=12, color=ft.Colors.BLUE) for action in actions]
        ], spacing=8)
    
    def get_next_salary_date(self):
        today = datetime.now()
        current_day = today.day
        salary_dates = self.finance_app.data["salary_dates"]
        
        # Находим следующую дату зарплаты
        for salary_day in sorted(salary_dates):
            if current_day <= salary_day:
                return today.replace(day=salary_day)
        
        # Если все даты прошли, берем первую дату следующего месяца
        next_month = today.replace(month=today.month + 1, day=1) if today.month < 12 else today.replace(year=today.year + 1, month=1, day=1)
        return next_month.replace(day=min(salary_dates))
    
    def calculate_daily_budget(self):
        """Рассчитывает правильный дневной бюджет с учетом резерва"""
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        free_money = current_money - safety_reserve
        
        salary_date = self.finance_app.data["salary_dates"][0]
        days_until_salary = self.calculate_days_until_salary(salary_date)
        
        if days_until_salary <= 0 or free_money <= 0:
            return 0
        
        if free_money < 1000:
            return free_money / days_until_salary
        
        available_for_daily = max(0, free_money - 2000)
        return available_for_daily / days_until_salary
    
    def update_salary(self, e):
        try:
            self.finance_app.data["salary"] = float(e.control.value)
            self.finance_app.save_data()
            # Не обновляем страницу сразу, чтобы не сбрасывать фокус
        except ValueError:
            pass
    
    def update_current_money(self, e):
        try:
            self.finance_app.data["current_money"] = float(e.control.value)
            self.finance_app.save_data()
            # Не обновляем страницу сразу, чтобы не сбрасывать фокус
        except ValueError:
            pass
    
    def update_salary_date_1(self, e):
        try:
            date = int(e.control.value)
            if 1 <= date <= 31:
                self.finance_app.data["salary_dates"][0] = date
                self.finance_app.save_data()
        except ValueError:
            pass
    
    def update_salary_date_2(self, e):
        try:
            date = int(e.control.value)
            if 1 <= date <= 31:
                self.finance_app.data["salary_dates"][1] = date
                self.finance_app.save_data()
        except ValueError:
            pass
    
    def update_money_values(self, e):
        self.finance_app.save_data()
        self.page.update()
    
    def update_rent(self, e):
        try:
            self.finance_app.data["rent"] = float(e.control.value)
            self.finance_app.save_data()
        except ValueError:
            pass
    
    def update_rent_cost(self, e):
        try:
            self.finance_app.data["rent_cost"] = float(e.control.value)
            self.finance_app.save_data()
            # Не обновляем страницу сразу, чтобы не сбрасывать фокус
        except ValueError:
            pass
    
    def update_rent_paid_until(self, e):
        self.finance_app.data["rent_paid_until"] = e.control.value
        self.finance_app.save_data()
        # Не обновляем страницу сразу, чтобы не сбрасывать фокус
    
    def update_safety_reserve(self, e):
        try:
            self.finance_app.data["safety_reserve"] = float(e.control.value)
            self.finance_app.save_data()
            self.refresh_all_pages()
        except ValueError:
            pass
    
    def toggle_chatgpt(self, e):
        self.finance_app.data["chatgpt_enabled"] = e.control.value
        self.finance_app.save_data()
        self.refresh_all_pages()
    
    def create_birthdays_management(self):
        birthdays = self.finance_app.data["birthdays"]
        salary = self.finance_app.data["salary"]
        
        # Поля для добавления нового ДР
        self.birthday_name = ft.TextField(label="Имя", width=150)
        self.birthday_month = ft.Dropdown(
            label="Месяц",
            width=100,
            options=[
                ft.dropdown.Option("Январь", "1"), ft.dropdown.Option("Февраль", "2"),
                ft.dropdown.Option("Март", "3"), ft.dropdown.Option("Апрель", "4"),
                ft.dropdown.Option("Май", "5"), ft.dropdown.Option("Июнь", "6"),
                ft.dropdown.Option("Июль", "7"), ft.dropdown.Option("Август", "8"),
                ft.dropdown.Option("Сентябрь", "9"), ft.dropdown.Option("Октябрь", "10"),
                ft.dropdown.Option("Ноябрь", "11"), ft.dropdown.Option("Декабрь", "12")
            ]
        )
        self.birthday_relationship = ft.Dropdown(
            label="Кто это",
            width=120,
            options=[
                ft.dropdown.Option("Девушка", "Девушка"),
                ft.dropdown.Option("Мама", "Мама"),
                ft.dropdown.Option("Папа", "Папа"),
                ft.dropdown.Option("Бабушка", "Бабушка"),
                ft.dropdown.Option("Брат/Сестра", "Брат/Сестра"),
                ft.dropdown.Option("Друг", "Друг"),
                ft.dropdown.Option("Коллега", "Коллега"),
                ft.dropdown.Option("Другое", "Другое")
            ]
        )
        
        # Умный расчет стоимости подарка с учетом месяца и финансов
        def calculate_gift_cost(relationship, month):
            # Базовые проценты от дохода
            base_percentages = {
                "Девушка": 0.12,  # 12% - самый важный человек
                "Мама": 0.08,     # 8% - родители важны
                "Папа": 0.08,     # 8% - родители важны
                "Бабушка": 0.07,  # 7% - бабушка очень важна
                "Брат/Сестра": 0.06,  # 6% - семья
                "Друг": 0.04,     # 4% - друзья
                "Коллега": 0.02,  # 2% - коллеги
                "Другое": 0.03    # 3% - по умолчанию
            }
            
            # Коэффициенты по месяцам (сезонные скидки и важность)
            month_multipliers = {
                1: 1.2,   # Январь - после Нового года, дорого
                2: 1.1,   # Февраль - День влюбленных, дорого
                3: 1.0,   # Март - 8 марта, нормально
                4: 0.9,   # Апрель - весна, дешевле
                5: 0.9,   # Май - весна, дешевле
                6: 0.8,   # Июнь - лето, дешевле
                7: 0.8,   # Июль - лето, дешевле
                8: 0.8,   # Август - лето, дешевле
                9: 0.9,   # Сентябрь - осень, нормально
                10: 1.0,  # Октябрь - осень, нормально
                11: 1.1,  # Ноябрь - перед Новым годом, дороже
                12: 1.3   # Декабрь - Новый год, самый дорогой
            }
            
            # Учитываем финансовое состояние
            current_money = self.finance_app.data["current_money"]
            monthly_expenses = self.calculate_average_monthly_expenses()
            safety_reserve = self.finance_app.data["safety_reserve"]
            
            # Финансовый коэффициент (чем лучше дела, тем дороже подарок)
            if current_money > safety_reserve * 2:
                financial_multiplier = 1.2  # Отличное состояние
            elif current_money > safety_reserve * 1.5:
                financial_multiplier = 1.1  # Хорошее состояние
            elif current_money > safety_reserve:
                financial_multiplier = 1.0  # Нормальное состояние
            else:
                financial_multiplier = 0.8  # Плохое состояние
            
            # Рассчитываем стоимость
            base_percent = base_percentages.get(relationship, 0.03)
            month_mult = month_multipliers.get(month, 1.0)
            
            # Минимальная стоимость подарка (чтобы не было слишком дешево)
            min_costs = {
                "Девушка": 2000,
                "Мама": 1500,
                "Папа": 1500,
                "Бабушка": 1200,
                "Брат/Сестра": 1000,
                "Друг": 500,
                "Коллега": 300,
                "Другое": 500
            }
            
            calculated_cost = int(salary * base_percent * month_mult * financial_multiplier)
            min_cost = min_costs.get(relationship, 500)
            
            return max(calculated_cost, min_cost)
        
        self.birthday_cost_display = ft.Text("", size=14, color=ft.Colors.BLUE)
        
        def update_cost_display(e):
            relationship = self.birthday_relationship.value
            month = self.birthday_month.value
            if relationship and month:
                month_int = self.convert_month_to_int(month)  # Используем универсальную функцию
                cost = calculate_gift_cost(relationship, month_int)
                month_name = ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 
                             'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'][month_int]
                
                # Определяем качество подарка
                if cost >= 5000:
                    quality = "💎 Премиум подарок"
                elif cost >= 3000:
                    quality = "⭐ Качественный подарок"
                elif cost >= 1500:
                    quality = "🎁 Хороший подарок"
                else:
                    quality = "🎀 Простой подарок"
                
                self.birthday_cost_display.value = f"💰 {month_name}: {cost:,.0f} ₽ ({quality})"
                self.page.update()
        
        self.birthday_relationship.on_change = update_cost_display
        self.birthday_month.on_change = update_cost_display
        
        return ft.Column([
            ft.Text("Добавить день рождения:", size=14, weight=ft.FontWeight.BOLD),
            ft.Row([
                self.birthday_name,
                self.birthday_month,
                self.birthday_relationship,
                ft.ElevatedButton("Добавить", on_click=self.add_birthday)
            ], spacing=10),
            
            self.birthday_cost_display,
            
            ft.Divider(),
            
            ft.Text("Список дней рождения:", size=14, weight=ft.FontWeight.BOLD),
                *[ft.Row([
                    ft.Text(f"🎂 {birthday['name']} - {['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'][self.convert_month_to_int(birthday['month'])]} - {birthday['cost']:,.0f} ₽", size=12),
                    ft.IconButton(ft.Icons.DELETE, on_click=lambda e, idx=i: self.delete_birthday(idx))
                ]) for i, birthday in enumerate(birthdays)],
            
            ft.Divider(),
            
                ft.Text("💡 Умный расчет подарков:", size=14, weight=ft.FontWeight.BOLD),
                ft.Text("• Учитывает месяц (зима дороже, лето дешевле)", size=12),
                ft.Text("• Учитывает ваше финансовое состояние", size=12),
                ft.Text("• Минимальные суммы для качественных подарков", size=12),
                ft.Text("• Девушка: от 2,000 ₽ (12% от дохода)", size=12),
                ft.Text("• Родители: от 1,500 ₽ (8% от дохода)", size=12),
                ft.Text("• Бабушка: от 1,200 ₽ (7% от дохода)", size=12),
                ft.Text("• Семья: от 1,000 ₽ (6% от дохода)", size=12),
                ft.Text("• Друзья: от 500 ₽ (4% от дохода)", size=12),
                ft.Text("• Коллеги: от 300 ₽ (2% от дохода)", size=12),
            
                ft.Text("💡 Совет: Система автоматически рассчитывает разумную стоимость подарка", size=10, color=ft.Colors.GREY_600),
                
                ft.Divider(),
                
                ft.Text("📊 Как работает умный расчет:", size=14, weight=ft.FontWeight.BOLD),
                ft.Text("• Базовый % от зарплаты (зависит от отношения)", size=11),
                ft.Text("• × Коэффициент месяца (зима +30%, лето -20%)", size=11),
                ft.Text("• × Финансовый коэффициент (от 0.8 до 1.2)", size=11),
                ft.Text("• = Итоговая стоимость (но не меньше минимума)", size=11),
                
                ft.Text("🎯 Примеры для зарплаты 50,000 ₽:", size=12, weight=ft.FontWeight.BOLD),
                ft.Text("• Девушка в декабре: 7,800 ₽ (премиум)", size=11),
                ft.Text("• Девушка в июле: 4,800 ₽ (качественный)", size=11),
                ft.Text("• Бабушка в декабре: 4,550 ₽ (качественный)", size=11),
                ft.Text("• Бабушка в июле: 2,800 ₽ (хороший)", size=11),
                ft.Text("• Друг в декабре: 2,600 ₽ (хороший)", size=11),
                ft.Text("• Друг в июле: 1,600 ₽ (хороший)", size=11)
        ], spacing=10)
    
    def add_birthday(self, e):
        name = self.birthday_name.value
        month = self.birthday_month.value
        relationship = self.birthday_relationship.value
        
        if name and month and relationship:
            # Умный расчет стоимости подарка с учетом месяца и финансов
            salary = self.finance_app.data["salary"]
            month = self.convert_month_to_int(month)  # Используем универсальную функцию
            
            # Базовые проценты от дохода
            base_percentages = {
                "Девушка": 0.12,  # 12% - самый важный человек
                "Мама": 0.08,     # 8% - родители важны
                "Папа": 0.08,     # 8% - родители важны
                "Бабушка": 0.07,  # 7% - бабушка очень важна
                "Брат/Сестра": 0.06,  # 6% - семья
                "Друг": 0.04,     # 4% - друзья
                "Коллега": 0.02,  # 2% - коллеги
                "Другое": 0.03    # 3% - по умолчанию
            }
            
            # Коэффициенты по месяцам
            month_multipliers = {
                1: 1.2,   # Январь - после Нового года, дорого
                2: 1.1,   # Февраль - День влюбленных, дорого
                3: 1.0,   # Март - 8 марта, нормально
                4: 0.9,   # Апрель - весна, дешевле
                5: 0.9,   # Май - весна, дешевле
                6: 0.8,   # Июнь - лето, дешевле
                7: 0.8,   # Июль - лето, дешевле
                8: 0.8,   # Август - лето, дешевле
                9: 0.9,   # Сентябрь - осень, нормально
                10: 1.0,  # Октябрь - осень, нормально
                11: 1.1,  # Ноябрь - перед Новым годом, дороже
                12: 1.3   # Декабрь - Новый год, самый дорогой
            }
            
            # Учитываем финансовое состояние
            current_money = self.finance_app.data["current_money"]
            safety_reserve = self.finance_app.data["safety_reserve"]
            
            if current_money > safety_reserve * 2:
                financial_multiplier = 1.2  # Отличное состояние
            elif current_money > safety_reserve * 1.5:
                financial_multiplier = 1.1  # Хорошее состояние
            elif current_money > safety_reserve:
                financial_multiplier = 1.0  # Нормальное состояние
            else:
                financial_multiplier = 0.8  # Плохое состояние
            
            # Минимальная стоимость подарка
            min_costs = {
                "Девушка": 2000,
                "Мама": 1500,
                "Папа": 1500,
                "Бабушка": 1200,
                "Брат/Сестра": 1000,
                "Друг": 500,
                "Коллега": 300,
                "Другое": 500
            }
            
            base_percent = base_percentages.get(relationship, 0.03)
            month_mult = month_multipliers.get(month, 1.0)
            calculated_cost = int(salary * base_percent * month_mult * financial_multiplier)
            min_cost = min_costs.get(relationship, 500)
            
            cost = max(calculated_cost, min_cost)
            
            birthday = {
                "name": name,
                "month": month,
                "relationship": relationship,
                "cost": cost
            }
            self.finance_app.data["birthdays"].append(birthday)
            self.finance_app.save_data()
            
            # Очищаем поля
            self.birthday_name.value = ""
            self.birthday_month.value = None
            self.birthday_relationship.value = None
            self.birthday_cost_display.value = ""
            
            self.refresh_all_pages()
    
    def delete_birthday(self, idx):
        if 0 <= idx < len(self.finance_app.data["birthdays"]):
            del self.finance_app.data["birthdays"][idx]
            self.finance_app.save_data()
            self.refresh_all_pages()
    
    def create_reserve_status(self):
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        
        if current_money >= safety_reserve:
            status_text = f"✅ Резерв обеспечен: {current_money:,.0f} ₽ из {safety_reserve:,.0f} ₽"
            status_color = ft.Colors.GREEN
        else:
            deficit = safety_reserve - current_money
            status_text = f"⚠️ Недостаток: {deficit:,.0f} ₽ (нужно {safety_reserve:,.0f} ₽)"
            status_color = ft.Colors.RED
        
        return ft.Text(status_text, size=14, color=status_color, weight=ft.FontWeight.BOLD)
    
    def pay_rent(self, e):
        rent_amount = self.finance_app.data["rent"]
        current_money = self.finance_app.data["current_money"]
        
        if rent_amount <= 0:
            return
        
        if rent_amount > current_money:
            self.show_rent_error_dialog("Недостаточно средств для оплаты квартплаты")
            return
        
        # Оплачиваем квартплату
        self.finance_app.data["current_money"] -= rent_amount
        
        # Обновляем дату оплаты до следующего месяца
        today = datetime.date.today()
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)
        
        self.finance_app.data["rent_paid_until"] = next_month.strftime("%Y-%m-%d")
        
        # Добавляем транзакцию
        transaction = {
            "type": "expense",
            "amount": rent_amount,
            "description": "Оплата квартплаты",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        self.finance_app.data["transactions"].append(transaction)
        self.finance_app.save_data()
        self.page.update()
    
    def reset_rent(self, e):
        print("Кнопка сброса квартплаты нажата")
        self.finance_app.data["rent"] = 0
        self.finance_app.data["rent_paid_until"] = None
        
        # Удаляем все транзакции связанные с квартплатой
        self.finance_app.data["transactions"] = [
            transaction for transaction in self.finance_app.data["transactions"]
            if "квартплат" not in transaction["description"].lower()
        ]
        
        self.finance_app.save_data()
        self.page.update()
        print("Квартплата сброшена, транзакции очищены")
    
    def show_rent_error_dialog(self, message):
        dialog = ft.AlertDialog(
            title=ft.Text("Ошибка оплаты"),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=self.close_dialog)]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def create_rent_status(self):
        rent = self.finance_app.data["rent"]
        rent_paid_until = self.finance_app.data["rent_paid_until"]
        
        if not rent_paid_until or rent <= 0:
            return ft.Text("Квартплата не настроена", size=12, color=ft.Colors.GREY_600)
        
        try:
            paid_until_date = datetime.strptime(rent_paid_until, "%Y-%m-%d").date()
            today = datetime.date.today()
            
            if paid_until_date > today:
                days_remaining = (paid_until_date - today).days
                return ft.Column([
                    ft.Text(f"✅ Оплачено до: {rent_paid_until}", size=12, color=ft.Colors.GREEN),
                    ft.Text(f"Осталось дней: {days_remaining}", size=12, color=ft.Colors.GREEN)
                ])
            else:
                days_overdue = (today - paid_until_date).days
                return ft.Column([
                    ft.Text(f"⚠️ Просрочено с: {rent_paid_until}", size=12, color=ft.Colors.ORANGE),
                    ft.Text(f"Дней просрочки: {days_overdue}", size=12, color=ft.Colors.RED)
                ])
        except:
            return ft.Text("Неверный формат даты", size=12, color=ft.Colors.RED)
    
    def check_rent_due(self):
        rent_paid_until = self.finance_app.data["rent_paid_until"]
        if not rent_paid_until:
            return False
        
        try:
            paid_until_date = datetime.strptime(rent_paid_until, "%Y-%m-%d").date()
            today = datetime.date.today()
            return today >= paid_until_date
        except:
            return False
    
    def create_transactions_list(self):
        transactions = self.finance_app.data["transactions"]
        
        if not transactions:
            return ft.Text("Нет транзакций")
        
        transaction_widgets = []
        for transaction in reversed(transactions[-10:]):
            if transaction["type"] == "income":
                color = ft.Colors.GREEN
                icon = ft.Icons.ADD
            elif transaction["type"] == "goal_investment":
                color = ft.Colors.BLUE
                icon = ft.Icons.SAVINGS
            else:
                color = ft.Colors.RED
                icon = ft.Icons.REMOVE
            
            transaction_widgets.append(
                ft.ListTile(
                    leading=ft.Icon(icon, color=color),
                    title=ft.Text(transaction["description"]),
                    subtitle=ft.Text(transaction["date"]),
                    trailing=ft.Text(f"{transaction['amount']:,.0f} ₽", color=color, weight=ft.FontWeight.BOLD)
                )
            )
        
        return ft.Column(transaction_widgets)
    
    def create_goals_list(self):
        goals = self.finance_app.data["goals"]
        
        if not goals:
            return ft.Text("Нет целей")
        
        goal_widgets = []
        for goal in goals:
            progress = self.calculate_goal_progress(goal)
            goal_name = goal["name"]
            invested_amount = self.finance_app.data["goal_investments"].get(goal_name, 0)
            
            try:
                goal_date = datetime.strptime(goal["date"], "%Y-%m-%d").date()
                today = datetime.date.today()
                days_left = (goal_date - today).days
                
                salary = self.finance_app.data["salary"]
                monthly_income = salary
                
                remaining_amount = goal["amount"] - invested_amount
                monthly_savings_needed = remaining_amount / max(days_left / 30, 1)
                
                progress_text = f"Вложено: {invested_amount:,.0f} ₽ из {goal['amount']:,.0f} ₽ ({progress*100:.1f}%)"
                if days_left > 0:
                    progress_text += f" | Осталось: {days_left} дней"
                    if monthly_savings_needed > 0:
                        progress_text += f" | Нужно откладывать: {monthly_savings_needed:,.0f} ₽/мес"
                
            except:
                progress_text = f"Вложено: {invested_amount:,.0f} ₽ из {goal['amount']:,.0f} ₽ ({progress*100:.1f}%)"
            
            goal_widgets.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Column([
                                    ft.Text(goal["name"], size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Цель: {goal['amount']:,.0f} ₽"),
                                    ft.Text(f"До {goal['date']}"),
                                ], expand=True),
                                ft.Row([
                                    ft.ElevatedButton(
                                        "Добавить в цель",
                                        on_click=lambda e, goal_name=goal["name"]: self.show_add_to_goal_dialog(goal_name),
                                        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_400)
                                    ),
                                    ft.ElevatedButton(
                                        "🗑️",
                                        on_click=lambda e, goal_name=goal["name"]: self.delete_goal(goal_name),
                                        tooltip="Удалить цель",
                                        style=ft.ButtonStyle(bgcolor=ft.Colors.RED_400, color=ft.Colors.WHITE)
                                    )
                                ], spacing=5)
                            ]),
                            ft.ProgressBar(value=progress, width=300),
                            ft.Text(progress_text, size=12)
                        ], spacing=5),
                        padding=15
                    )
                )
            )
        
        return ft.Column(goal_widgets)
    
    def delete_goal(self, goal_name):
        """Удаляет цель по имени"""
        print(f"DEBUG: Удаляем цель '{goal_name}'")
        
        # Показываем уведомление об удалении
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Цель '{goal_name}' удалена"),
            bgcolor=ft.Colors.RED_400
        )
        self.page.snack_bar.open = True
        
        goals = self.finance_app.data["goals"]
        self.finance_app.data["goals"] = [goal for goal in goals if goal["name"] != goal_name]
        
        # Также удаляем инвестиции в эту цель
        if goal_name in self.finance_app.data["goal_investments"]:
            del self.finance_app.data["goal_investments"][goal_name]
        
        self.finance_app.save_data()
        self.refresh_all_pages()
        self.page.update()
        print(f"DEBUG: Цель '{goal_name}' удалена")
    
    def show_delete_goal_dialog(self, goal_name):
        """Показывает диалог подтверждения удаления цели"""
        print(f"DEBUG: Показываем диалог удаления для цели '{goal_name}'")
        def confirm_delete(e):
            print(f"DEBUG: Подтверждено удаление цели '{goal_name}'")
            self.delete_goal(goal_name)
            self.page.dialog.open = False
            self.page.update()
        
        def cancel_delete(e):
            print(f"DEBUG: Отменено удаление цели '{goal_name}'")
            self.page.dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Удалить цель?"),
            content=ft.Text(f"Вы уверены, что хотите удалить цель '{goal_name}'? Это действие нельзя отменить."),
            actions=[
                ft.TextButton("Отмена", on_click=cancel_delete),
                ft.TextButton("Удалить", on_click=confirm_delete, style=ft.ButtonStyle(color=ft.Colors.RED))
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def calculate_goal_progress(self, goal):
        try:
            goal_name = goal["name"]
            invested_amount = self.finance_app.data["goal_investments"].get(goal_name, 0)
            
            goal_date = datetime.strptime(goal["date"], "%Y-%m-%d").date()
            today = datetime.date.today()
            
            if goal_date <= today:
                return 1.0 if invested_amount >= goal["amount"] else invested_amount / goal["amount"]
            
            days_total = (goal_date - today).days
            
            salary = self.finance_app.data["salary"]
            monthly_income = salary
            
            remaining_amount = goal["amount"] - invested_amount
            monthly_savings_needed = remaining_amount / max(days_total / 30, 1)
            
            if monthly_savings_needed <= monthly_income * 0.3:
                total_available = invested_amount + (monthly_income * 0.3 * (days_total / 30))
            else:
                total_available = invested_amount + (monthly_income * (days_total / 30))
            
            progress = min(total_available / goal["amount"], 1.0)
            return max(0.0, progress)
        except:
            return 0.0
    
    def create_smart_forecast(self):
        salary = self.finance_app.data["salary"]
        current_money = self.finance_app.data["current_money"]
        goals = self.finance_app.data["goals"]
        goal_investments = self.finance_app.data["goal_investments"]
        rent = self.finance_app.data["rent"]
        
        monthly_income = salary
        
        # Проверяем квартплату
        rent_due = self.check_rent_due()
        rent_to_pay = rent if rent_due else 0
        
        # Расчет резерва (с учетом квартплаты)
        emergency_fund = (monthly_income - rent) * 6
        current_emergency = current_money - sum(goal_investments.values()) - rent_to_pay
        
        # Анализ целей
        total_goal_amount = sum(goal["amount"] for goal in goals)
        total_invested = sum(goal_investments.values())
        remaining_goals = total_goal_amount - total_invested
        
        # Умные рекомендации
        recommendations = self.calculate_smart_recommendations(
            monthly_income, current_money, goals, goal_investments, emergency_fund
        )
        
        forecast_widgets = [
            ft.Text("🧠 Умный финансовый прогноз", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("💰 Текущее состояние", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"• Доход в месяц: {monthly_income:,.0f} ₽"),
                        ft.Text(f"• Квартплата: {rent:,.0f} ₽/мес"),
                        ft.Text(f"• Всего денег: {current_money:,.0f} ₽"),
                        ft.Text(f"• В резерве: {current_emergency:,.0f} ₽"),
                        ft.Text(f"• В целях: {total_invested:,.0f} ₽"),
                        ft.Text(f"• Свободно: {current_money - total_invested - rent_to_pay:,.0f} ₽"),
                        ft.Text(f"• Квартплата к оплате: {'Да' if rent_due else 'Нет'}", color=ft.Colors.RED if rent_due else ft.Colors.GREEN)
                    ], spacing=5),
                    padding=15
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("🎯 Анализ целей", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"• Всего целей: {len(goals)}"),
                        ft.Text(f"• Общая сумма: {total_goal_amount:,.0f} ₽"),
                        ft.Text(f"• Уже накоплено: {total_invested:,.0f} ₽"),
                        ft.Text(f"• Осталось накопить: {remaining_goals:,.0f} ₽")
                    ], spacing=5),
                    padding=15
                )
            )
        ]
        
        # Добавляем рекомендации
        for rec in recommendations:
            forecast_widgets.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(rec["title"], size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(rec["description"], size=14),
                            ft.Text(rec["action"], size=12, color=ft.Colors.BLUE_600)
                        ], spacing=5),
                        padding=15
                    )
                )
            )
        
        return ft.Column(forecast_widgets, spacing=10)
    
    def calculate_smart_recommendations(self, monthly_income, current_money, goals, goal_investments, emergency_fund):
        recommendations = []
        current_emergency = current_money - sum(goal_investments.values())
        
        # Рекомендация по резерву
        if current_emergency < emergency_fund * 0.5:
            # Рассчитываем реалистичную сумму для накопления резерва
            monthly_savings_for_reserve = min(monthly_income * 0.2, (emergency_fund - current_emergency) / 12)
            months_to_reserve = (emergency_fund - current_emergency) / monthly_savings_for_reserve
            
            recommendations.append({
                "title": "🚨 Критично: Увеличьте резерв",
                "description": f"Ваш резерв составляет {current_emergency:,.0f} ₽, но рекомендуется {emergency_fund:,.0f} ₽",
                "action": f"Откладывайте {monthly_savings_for_reserve:,.0f} ₽ в месяц ({months_to_reserve:.0f} месяцев до цели)"
            })
        elif current_emergency < emergency_fund:
            monthly_savings_for_reserve = min(monthly_income * 0.15, (emergency_fund - current_emergency) / 6)
            months_to_reserve = (emergency_fund - current_emergency) / monthly_savings_for_reserve
            
            recommendations.append({
                "title": "⚠️ Увеличьте резерв",
                "description": f"Резерв {current_emergency:,.0f} ₽ из рекомендуемых {emergency_fund:,.0f} ₽",
                "action": f"Откладывайте {monthly_savings_for_reserve:,.0f} ₽ в месяц ({months_to_reserve:.0f} месяцев до цели)"
            })
        else:
            recommendations.append({
                "title": "✅ Резерв в порядке",
                "description": f"Отличный резерв: {current_emergency:,.0f} ₽",
                "action": "Можете сосредоточиться на целях и инвестициях"
            })
        
        # Анализ целей
        if goals:
            total_goal_amount = sum(goal["amount"] for goal in goals)
            total_invested = sum(goal_investments.values())
            remaining_goals = total_goal_amount - total_invested
            
            if remaining_goals > 0:
                # Расчет приоритетов целей
                goal_priorities = self.calculate_goal_priorities(goals, goal_investments)
                
                recommendations.append({
                    "title": "🎯 Стратегия по целям",
                    "description": f"Осталось накопить {remaining_goals:,.0f} ₽ на {len(goals)} целей",
                    "action": f"Приоритет: {goal_priorities[0]['name']} - {goal_priorities[0]['monthly_needed']:,.0f} ₽/мес"
                })
                
                # Рекомендация по распределению дохода
                total_monthly_needed = sum(g["monthly_needed"] for g in goal_priorities)
                max_affordable = monthly_income * 0.25  # Максимум 25% от дохода на цели
                
                if total_monthly_needed > max_affordable:
                    recommendations.append({
                        "title": "💡 Оптимизация целей",
                        "description": f"Нужно {total_monthly_needed:,.0f} ₽/мес, но это {total_monthly_needed/monthly_income*100:.0f}% дохода",
                        "action": f"Реально откладывать только {max_affordable:,.0f} ₽/мес. Рассмотрите увеличение сроков целей"
                    })
                else:
                    recommendations.append({
                        "title": "✅ Цели достижимы",
                        "description": f"Нужно {total_monthly_needed:,.0f} ₽/мес ({total_monthly_needed/monthly_income*100:.0f}% дохода)",
                        "action": "Продолжайте следовать плану!"
                    })
        
        # Общие рекомендации по распределению
        rent = self.finance_app.data["rent"]
        disposable_income = monthly_income - rent
        
        recommendations.append({
            "title": "📊 Реалистичное распределение",
            "description": f"При доходе {monthly_income:,.0f} ₽ и квартплате {rent:,.0f} ₽ рекомендуем:",
            "action": f"• Квартплата: {rent:,.0f} ₽ • Расходы: {disposable_income * 0.80:,.0f} ₽ • Резерв/цели: {disposable_income * 0.15:,.0f} ₽ • Инвестиции: {disposable_income * 0.05:,.0f} ₽"
        })
        
        return recommendations
    
    def calculate_goal_priorities(self, goals, goal_investments):
        priorities = []
        today = datetime.date.today()
        
        for goal in goals:
            try:
                goal_date = datetime.strptime(goal["date"], "%Y-%m-%d").date()
                days_left = (goal_date - today).days
                invested = goal_investments.get(goal["name"], 0)
                remaining = goal["amount"] - invested
                
                if remaining > 0 and days_left > 0:
                    monthly_needed = remaining / (days_left / 30)
                    priority_score = remaining / max(days_left, 1)
                    
                    priorities.append({
                        "name": goal["name"],
                        "amount": goal["amount"],
                        "invested": invested,
                        "remaining": remaining,
                        "days_left": days_left,
                        "monthly_needed": monthly_needed,
                        "priority_score": priority_score
                    })
            except:
                continue
        
        return sorted(priorities, key=lambda x: x["priority_score"], reverse=True)
    
    def create_expense_statistics(self):
        transactions = self.finance_app.data["transactions"]
        current_month = datetime.now().strftime("%Y-%m")
        
        monthly_expenses = sum(
            t["amount"] for t in transactions 
            if t["type"] == "expense" and t["date"].startswith(current_month)
        )
        
        monthly_income = sum(
            t["amount"] for t in transactions 
            if t["type"] == "income" and t["date"].startswith(current_month)
        )
        
        goal_investments = sum(
            t["amount"] for t in transactions 
            if t["type"] == "goal_investment" and t["date"].startswith(current_month)
        )
        
        salary = self.finance_app.data["salary"]
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📈 Статистика за месяц", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(f"• Доходы: {monthly_income:,.0f} ₽", color=ft.Colors.GREEN),
                    ft.Text(f"• Расходы: {monthly_expenses:,.0f} ₽", color=ft.Colors.RED),
                    ft.Text(f"• В цели: {goal_investments:,.0f} ₽", color=ft.Colors.BLUE),
                    ft.Text(f"• Баланс: {monthly_income - monthly_expenses - goal_investments:,.0f} ₽"),
                    ft.Divider(),
                    ft.Text("🎯 Эффективность", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"• Доля на цели: {goal_investments/max(salary,1)*100:.1f}%"),
                    ft.Text(f"• Доля расходов: {monthly_expenses/max(salary,1)*100:.1f}%"),
                    ft.Text(f"• Накопления: {(monthly_income - monthly_expenses - goal_investments)/max(salary,1)*100:.1f}%")
                ], spacing=5),
                padding=15
            )
        )
    
    def show_add_income_dialog(self, e):
        self.show_transaction_dialog("income", "Добавить доход")
    
    def show_add_expense_dialog(self, e):
        self.show_transaction_dialog("expense", "Добавить расход")
    
    def show_transaction_dialog(self, transaction_type, title):
        amount_field = ft.TextField(label="Сумма (₽)", keyboard_type=ft.KeyboardType.NUMBER)
        description_field = ft.TextField(label="Описание")
        
        # Добавляем категорию для расходов
        category_field = None
        if transaction_type == "expense":
            # Базовые категории
            category_options = [
                ft.dropdown.Option("🍎 Еда", "food"),
                ft.dropdown.Option("🍽️ Рестораны", "restaurants"),
                ft.dropdown.Option("🎮 Игры", "games"),
                ft.dropdown.Option("🚗 Транспорт", "transport"),
                ft.dropdown.Option("👕 Одежда", "clothing"),
                ft.dropdown.Option("📱 Электроника", "electronics"),
                ft.dropdown.Option("🎬 Развлечения", "entertainment"),
                ft.dropdown.Option("📦 Прочее", "other")
            ]
            
            # Добавляем кастомные категории
            if "custom_categories" in self.finance_app.data:
                for cat in self.finance_app.data["custom_categories"]:
                    category_options.append(ft.dropdown.Option(f"{cat['icon']} {cat['name']}", cat['key']))
            
            category_field = ft.Dropdown(
                label="Категория",
                options=category_options
            )
        
        def add_transaction(e):
            try:
                amount = float(amount_field.value)
                description = description_field.value
                category = category_field.value if category_field else None
                
                if amount > 0 and description:
                    # Проверяем безопасность для расходов
                    if transaction_type == "expense":
                        safety_reserve = self.finance_app.data["safety_reserve"]
                        current_money = self.finance_app.data["current_money"]
                        
                        # Свободные деньги с учетом резерва
                        available_for_spending = current_money - safety_reserve
                        
                        if amount > available_for_spending:
                            if available_for_spending <= 0:
                                amount_field.error_text = f"❌ Недостаточно средств! Нужно сохранить {safety_reserve:,.0f} ₽ резерва"
                            else:
                                amount_field.error_text = f"⚠️ Можно потратить только {available_for_spending:,.0f} ₽ (резерв: {safety_reserve:,.0f} ₽)"
                            self.page.update()
                            return
                    
                    transaction = {
                        "type": transaction_type,
                        "amount": amount,
                        "description": description,
                        "category": category,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    
                    self.finance_app.data["transactions"].append(transaction)
                    
                    if transaction_type == "income":
                        self.finance_app.data["current_money"] += amount
                    else:
                        self.finance_app.data["current_money"] -= amount
                    
                    self.finance_app.save_data()
                    self.refresh_all_pages()
                    self.page.dialog.open = False
                    self.page.update()
            except ValueError:
                pass
        
        content_fields = [amount_field, description_field]
        if category_field:
            content_fields.append(category_field)
        
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Column(content_fields, tight=True),
            actions=[
                ft.TextButton("Отмена", on_click=self.close_dialog),
                ft.TextButton("Добавить", on_click=add_transaction)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def add_goal(self, e):
        try:
            name = self.goal_name_field.value
            amount = float(self.goal_amount_field.value)
            date_str = self.goal_date_field.value
            
            if name and amount > 0 and date_str:
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    if date_obj.date() <= datetime.now().date():
                        self.goal_date_field.error_text = "Дата должна быть в будущем"
                        self.page.update()
                        return
                    
                    goal = {
                        "name": name,
                        "amount": amount,
                        "date": date_str
                    }
                    
                    self.finance_app.data["goals"].append(goal)
                    self.finance_app.save_data()
                    
                    self.goal_name_field.value = ""
                    self.goal_amount_field.value = ""
                    self.goal_date_field.value = ""
                    self.goal_date_field.error_text = ""
                    
                    self.refresh_all_pages()
                    
                except ValueError:
                    self.goal_date_field.error_text = "Неверный формат даты (используйте YYYY-MM-DD)"
                    self.page.update()
        except ValueError:
            pass
    
    def show_add_to_goal_dialog(self, goal_name):
        amount_field = ft.TextField(label="Сумма для перевода (₽)", keyboard_type=ft.KeyboardType.NUMBER)
        
        def add_to_goal(e):
            try:
                amount = float(amount_field.value)
                current_money = self.finance_app.data["current_money"]
                
                if amount > 0 and amount <= current_money:
                    if goal_name not in self.finance_app.data["goal_investments"]:
                        self.finance_app.data["goal_investments"][goal_name] = 0
                    
                    self.finance_app.data["goal_investments"][goal_name] += amount
                    self.finance_app.data["current_money"] -= amount
                    
                    transaction = {
                        "type": "goal_investment",
                        "amount": amount,
                        "description": f"Перевод в цель: {goal_name}",
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    
                    self.finance_app.data["transactions"].append(transaction)
                    self.finance_app.save_data()
                    
                    self.page.update()
                    self.page.dialog.open = False
                    self.page.update()
                elif amount > current_money:
                    amount_field.error_text = f"Недостаточно средств. Доступно: {current_money:,.0f} ₽"
                    self.page.update()
            except ValueError:
                amount_field.error_text = "Введите корректную сумму"
                self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"Добавить в цель: {goal_name}"),
            content=ft.Column([
                ft.Text(f"Доступно для перевода: {self.finance_app.data['current_money']:,.0f} ₽"),
                amount_field
            ], tight=True),
            actions=[
                ft.TextButton("Отмена", on_click=self.close_dialog),
                ft.TextButton("Перевести", on_click=add_to_goal)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def update_purchase_name(self, e):
        self.purchase_name = e.control.value
    
    def update_purchase_price(self, e):
        try:
            self.purchase_price = float(e.control.value) if e.control.value else 0
        except ValueError:
            self.purchase_price = 0
    
    def check_purchase_affordability(self, e):
        if not self.purchase_name or self.purchase_price <= 0:
            self.purchase_analysis = ft.Text("Введите корректное название и цену", size=14, color=ft.Colors.RED)
            self.page.update()
            return
        
        analysis = self.calculate_purchase_analysis(self.purchase_price)
        self.purchase_analysis = analysis
        self.page.update()
    
    def calculate_purchase_analysis(self, price):
        current_money = self.finance_app.data["current_money"]
        salary = self.finance_app.data["salary"]
        goal_investments = self.finance_app.data["goal_investments"]
        rent = self.finance_app.data["rent"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        
        # Проверяем нужно ли платить квартплату
        rent_due = self.check_rent_due()
        rent_to_pay = rent if rent_due else 0
        
        # Свободные деньги (не вложенные в цели, с учетом квартплаты и резерва)
        free_money = current_money - sum(goal_investments.values()) - rent_to_pay
        available_for_spending = free_money - safety_reserve
        
        # Ежемесячный доход
        monthly_income = salary
        
        # Дневной бюджет с учетом резерва
        days_until_salary = self.calculate_days_until_salary(self.finance_app.data["salary_dates"][0])
        daily_budget = available_for_spending / max(days_until_salary, 1)
        
        if price <= available_for_spending:
            # Можем купить прямо сейчас с учетом резерва
            remaining_after_purchase = available_for_spending - price
            days_remaining = remaining_after_purchase / daily_budget if daily_budget > 0 else 0
            
            return ft.Column([
                ft.Text("✅ Можете купить прямо сейчас!", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                ft.Text(f"Останется для трат: {remaining_after_purchase:,.0f} ₽"),
                ft.Text(f"Резерв сохранен: {safety_reserve:,.0f} ₽"),
                ft.Text(f"Этого хватит на: {days_remaining:.0f} дней"),
                ft.Text(f"Товар: {self.purchase_name}", size=12, color=ft.Colors.GREY_600)
            ], spacing=5)
        
        elif price <= free_money:
            # Можем купить, но затронем резерв
            reserve_impact = price - available_for_spending
            
            return ft.Column([
                ft.Text("⚠️ Можете купить, но затронете резерв", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE),
                ft.Text(f"Затронете резерв на: {reserve_impact:,.0f} ₽"),
                ft.Text(f"Останется резерва: {safety_reserve - reserve_impact:,.0f} ₽"),
                ft.Text(f"Товар: {self.purchase_name}", size=12, color=ft.Colors.GREY_600),
                ft.Text("⚠️ Не рекомендуется - нарушает финансовую безопасность", size=12, color=ft.Colors.RED)
            ], spacing=5)
        
        else:
            # Нужно копить
            needed_amount = price - current_money
            months_to_save = needed_amount / monthly_income
            monthly_savings_needed = needed_amount / max(months_to_save, 1)
            
            return ft.Column([
                ft.Text("❌ Нужно копить", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
                ft.Text(f"Не хватает: {needed_amount:,.0f} ₽"),
                ft.Text(f"Время накопления: {months_to_save:.1f} месяцев"),
                ft.Text(f"Нужно откладывать: {monthly_savings_needed:,.0f} ₽/мес"),
                ft.Text(f"Товар: {self.purchase_name}", size=12, color=ft.Colors.GREY_600)
            ], spacing=5)
    
    def create_purchase_analysis(self):
        return self.purchase_analysis
    
    def create_smart_money_analysis(self):
        current_money = self.finance_app.data["current_money"]
        salary = self.finance_app.data["salary"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        goal_investments = sum(self.finance_app.data["goal_investments"].values())
        rent = self.finance_app.data["rent"]
        
        # Проверяем квартплату
        rent_due = self.check_rent_due()
        rent_to_pay = rent if rent_due else 0
        
        # Свободные деньги (с учетом резерва и квартплаты)
        free_money = current_money - goal_investments - rent_to_pay
        available_for_spending = free_money - safety_reserve
        
        # Анализ безопасности
        if current_money < safety_reserve:
            safety_status = "🚨 КРИТИЧНО"
            safety_color = ft.Colors.RED
            safety_message = f"У вас {current_money:,.0f} ₽, но нужно {safety_reserve:,.0f} ₽"
        elif current_money < safety_reserve * 1.5:
            safety_status = "⚠️ ВНИМАНИЕ"
            safety_color = ft.Colors.ORANGE
            safety_message = f"Резерв: {current_money:,.0f} ₽ (рекомендуется {safety_reserve:,.0f} ₽)"
        else:
            safety_status = "✅ БЕЗОПАСНО"
            safety_color = ft.Colors.GREEN
            safety_message = f"Отличный резерв: {current_money:,.0f} ₽"
        
        # Прогноз на следующие 3 месяца
        monthly_income = salary
        monthly_expenses = self.calculate_average_monthly_expenses()
        monthly_savings = monthly_income - monthly_expenses - rent
        
        # Прогноз баланса
        months_forecast = []
        current_balance = current_money
        for month in range(1, 4):
            current_balance += monthly_savings
            months_forecast.append({
                "month": f"Через {month} мес",
                "balance": current_balance,
                "safe": current_balance >= safety_reserve
            })
        
        return ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("Текущие деньги:", size=14),
                    ft.Text(f"{current_money:,.0f} ₽", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN)
                ], expand=True),
                ft.Column([
                    ft.Text("Оклад:", size=14),
                    ft.Text(f"{salary:,.0f} ₽", size=20, weight=ft.FontWeight.BOLD)
                ], expand=True),
                ft.Column([
                    ft.Text("В целях:", size=14),
                    ft.Text(f"{goal_investments:,.0f} ₽", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE)
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            ft.Row([
                ft.Column([
                    ft.Text("🛡️ Статус безопасности", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(safety_status, size=18, weight=ft.FontWeight.BOLD, color=safety_color),
                    ft.Text(safety_message, size=12)
                ], expand=True),
                ft.Column([
                    ft.Text("💰 Доступно для трат", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{max(0, available_for_spending):,.0f} ₽", 
                           size=18, weight=ft.FontWeight.BOLD, 
                           color=ft.Colors.GREEN if available_for_spending > 0 else ft.Colors.RED),
                    ft.Text(f"Резерв: {safety_reserve:,.0f} ₽", size=12)
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            ft.Text("📈 Прогноз на 3 месяца", size=16, weight=ft.FontWeight.BOLD),
            ft.Column([
                ft.Row([
                    ft.Text(forecast["month"], size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{forecast['balance']:,.0f} ₽", 
                           size=14, 
                           color=ft.Colors.GREEN if forecast["safe"] else ft.Colors.RED),
                    ft.Text("✅" if forecast["safe"] else "⚠️", size=16)
                ]) for forecast in months_forecast
            ], spacing=5),
            
            ft.Divider(),
            
            ft.Text("🎯 Рекомендации", size=16, weight=ft.FontWeight.BOLD),
            self.create_smart_recommendations()
        ], spacing=10)
    
    def calculate_average_monthly_expenses(self):
        transactions = self.finance_app.data["transactions"]
        
        # Базовые расходы 10,000 ₽/месяц
        base_expenses = 10000
        
        # Временно возвращаем базовые расходы 10,000 ₽
        # Позже можно будет включить динамический расчет
        return base_expenses
        
        # Закомментированный код для будущего динамического расчета:
        # if not transactions:
        #     return base_expenses
        # 
        # months_with_data = {}
        # for transaction in transactions:
        #     if transaction["type"] == "expense":
        #         month_str = transaction["date"][:7]  # YYYY-MM
        #         if month_str not in months_with_data:
        #             months_with_data[month_str] = 0
        #         months_with_data[month_str] += transaction["amount"]
        # 
        # if not months_with_data:
        #     return base_expenses
        # 
        # sorted_months = sorted(months_with_data.keys(), reverse=True)
        # months_to_use = sorted_months[:3] if len(sorted_months) >= 3 else sorted_months
        # 
        # total_expenses = sum(months_with_data[month] for month in months_to_use)
        # average_expenses = total_expenses / len(months_to_use)
        # 
        # return average_expenses
    
    def get_current_month_expenses(self):
        """Получает расходы за текущий месяц"""
        transactions = self.finance_app.data["transactions"]
        current_month = datetime.now().strftime("%Y-%m")
        
        current_expenses = sum(
            t["amount"] for t in transactions 
            if t["type"] == "expense" and t["date"].startswith(current_month)
        )
        return current_expenses
    
    def get_current_month_income(self):
        """Получает доходы за текущий месяц"""
        transactions = self.finance_app.data["transactions"]
        current_month = datetime.now().strftime("%Y-%m")
        
        current_income = sum(
            t["amount"] for t in transactions 
            if t["type"] == "income" and t["date"].startswith(current_month)
        )
        return current_income
    
    def create_smart_recommendations(self):
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        salary = self.finance_app.data["salary"]
        monthly_expenses = self.calculate_average_monthly_expenses()
        rent = self.finance_app.data["rent"]
        
        recommendations = []
        
        # Анализ резерва
        if current_money < safety_reserve:
            needed = safety_reserve - current_money
            months_to_save = needed / max(salary - monthly_expenses - rent, 1)
            recommendations.append(
                ft.Text(f"🚨 СРОЧНО: Нужно накопить {needed:,.0f} ₽ за {months_to_save:.1f} мес", 
                       color=ft.Colors.RED, size=12)
            )
        elif current_money < safety_reserve * 1.5:
            recommendations.append(
                ft.Text("⚠️ Увеличьте резерв до 30,000 ₽ для полной безопасности", 
                       color=ft.Colors.ORANGE, size=12)
            )
        else:
            recommendations.append(
                ft.Text("✅ Резерв в порядке! Можете инвестировать в цели", 
                       color=ft.Colors.GREEN, size=12)
            )
        
        # Анализ трат
        if monthly_expenses > salary * 0.7:
            recommendations.append(
                ft.Text(f"💡 Сократите расходы: {monthly_expenses:,.0f} ₽/мес ({monthly_expenses/salary*100:.0f}% дохода)", 
                       color=ft.Colors.ORANGE, size=12)
            )
        
        # Анализ целей
        goals = self.finance_app.data["goals"]
        if goals:
            total_goal_amount = sum(goal["amount"] for goal in goals)
            total_invested = sum(self.finance_app.data["goal_investments"].values())
            remaining = total_goal_amount - total_invested
            
            if remaining > 0:
                monthly_savings = salary - monthly_expenses - rent
                months_for_goals = remaining / max(monthly_savings * 0.3, 1)  # 30% от сбережений на цели
                recommendations.append(
                    ft.Text(f"🎯 На цели осталось {remaining:,.0f} ₽ (~{months_for_goals:.0f} мес)", 
                           color=ft.Colors.BLUE, size=12)
                )
        
        return ft.Column(recommendations, spacing=5)
    
    def create_critical_alerts(self):
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        goal_investments = sum(self.finance_app.data["goal_investments"].values())
        rent = self.finance_app.data["rent"]
        rent_due = self.check_rent_due()
        rent_to_pay = rent if rent_due else 0
        
        alerts = []
        
        # Критический уровень денег
        if current_money < safety_reserve:
            deficit = safety_reserve - current_money
            alerts.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("🚨 КРИТИЧЕСКАЯ СИТУАЦИЯ", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
                            ft.Text(f"У вас {current_money:,.0f} ₽, но нужно {safety_reserve:,.0f} ₽", size=16),
                            ft.Text(f"Недостаток: {deficit:,.0f} ₽", size=14, color=ft.Colors.RED),
                            ft.Text("СРОЧНО пополните счет!", size=14, color=ft.Colors.RED, weight=ft.FontWeight.BOLD)
                        ], spacing=5),
                        padding=15,
                        bgcolor=ft.Colors.RED_50
                    )
                )
            )
        elif current_money < safety_reserve * 1.2:
            alerts.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("⚠️ НИЗКИЙ РЕЗЕРВ", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE),
                            ft.Text(f"У вас {current_money:,.0f} ₽, резерв {safety_reserve:,.0f} ₽", size=16),
                            ft.Text("Рекомендуется пополнить счет", size=14, color=ft.Colors.ORANGE)
                        ], spacing=5),
                        padding=15,
                        bgcolor=ft.Colors.ORANGE_50
                    )
                )
            )
        else:
            alerts.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("✅ РЕЗЕРВ В ПОРЯДКЕ", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                            ft.Text(f"У вас {current_money:,.0f} ₽, резерв {safety_reserve:,.0f} ₽", size=16),
                            ft.Text("Финансовая безопасность обеспечена", size=14, color=ft.Colors.GREEN)
                        ], spacing=5),
                        padding=15,
                        bgcolor=ft.Colors.GREEN_50
                    )
                )
            )
        
        # Предупреждение о квартплате
        if rent_due and rent > 0:
            alerts.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("⚠️ КВАРТПЛАТА К ОПЛАТЕ", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE),
                            ft.Text(f"Сумма: {rent:,.0f} ₽", size=14),
                            ft.Text("Оплатите квартплату", size=14, color=ft.Colors.ORANGE)
                        ], spacing=5),
                        padding=15,
                        bgcolor=ft.Colors.ORANGE_50
                    )
                )
            )
        
        # Предупреждение о низком резерве
        if current_money < safety_reserve * 1.5:
            alerts.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("⚠️ НИЗКИЙ РЕЗЕРВ", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE),
                            ft.Text(f"Резерв: {current_money:,.0f} ₽ (рекомендуется {safety_reserve:,.0f} ₽)", size=14),
                            ft.Text("Рекомендуем увеличить резерв", size=14, color=ft.Colors.ORANGE)
                        ], spacing=5),
                        padding=15,
                        bgcolor=ft.Colors.ORANGE_50
                    )
                )
            )
        
        # Все в порядке
        else:
            alerts.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("✅ ВСЕ В ПОРЯДКЕ", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                            ft.Text(f"Резерв: {current_money:,.0f} ₽", size=14),
                            ft.Text("Финансовая безопасность обеспечена", size=14, color=ft.Colors.GREEN)
                        ], spacing=5),
                        padding=15,
                        bgcolor=ft.Colors.GREEN_50
                    )
                )
            )
        
        return ft.Column(alerts, spacing=10) if alerts else ft.Container()
    
    def create_ai_assistant_card(self):
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        salary = self.finance_app.data["salary"]
        monthly_expenses = self.calculate_average_monthly_expenses()
        rent = self.finance_app.data["rent"]
        
        # Анализ финансового здоровья
        financial_health = self.calculate_financial_health()
        
        # Умные рекомендации от ИИ
        ai_recommendations = self.get_ai_recommendations()
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.SMART_TOY, size=40, color=ft.Colors.BLUE),
                        ft.Column([
                            ft.Text("Ваш финансовый помощник", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Финансовое здоровье: {financial_health['score']}/100", 
                                   size=16, color=financial_health['color'])
                        ], expand=True)
                    ], spacing=10),
                    
                    ft.Divider(),
                    
                    ft.Text("🎯 Главные рекомендации:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Column(ai_recommendations[:3], spacing=5),
                    
                    ft.Divider(),
                    
                    ft.Text("📊 Быстрая статистика:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.Column([
                            ft.Text("Доход/мес", size=12, color=ft.Colors.GREY_600),
                            ft.Text(f"{salary:,.0f} ₽", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN)
                        ], expand=True),
                        ft.Column([
                            ft.Text("Расходы/мес", size=12, color=ft.Colors.GREY_600),
                            ft.Text(f"{monthly_expenses:,.0f} ₽", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.RED)
                        ], expand=True),
                        ft.Column([
                            ft.Text("Сбережения", size=12, color=ft.Colors.GREY_600),
                            ft.Text(f"{salary - monthly_expenses - rent:,.0f} ₽", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE)
                        ], expand=True)
                    ])
                ], spacing=10),
                padding=20
            )
        )
    
    def calculate_financial_health(self):
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        salary = self.finance_app.data["salary"]
        monthly_expenses = self.calculate_average_monthly_expenses()
        goals = self.finance_app.data["goals"]
        goal_investments = sum(self.finance_app.data["goal_investments"].values())
        
        score = 0
        
        # Резерв (40 баллов)
        if current_money >= safety_reserve * 2:
            score += 40
        elif current_money >= safety_reserve:
            score += 30
        elif current_money >= safety_reserve * 0.5:
            score += 15
        
        # Соотношение доход/расходы (30 баллов)
        if monthly_expenses > 0:
            expense_ratio = monthly_expenses / salary
            if expense_ratio <= 0.5:
                score += 30
            elif expense_ratio <= 0.7:
                score += 20
            elif expense_ratio <= 0.9:
                score += 10
        
        # Цели (20 баллов)
        if goals:
            total_goal_amount = sum(goal["amount"] for goal in goals)
            if total_goal_amount > 0:
                goal_progress = goal_investments / total_goal_amount
                score += int(20 * goal_progress)
        
        # Стабильность (10 баллов)
        if salary > 0 and monthly_expenses > 0:
            savings_rate = (salary - monthly_expenses) / salary
            if savings_rate >= 0.3:
                score += 10
            elif savings_rate >= 0.2:
                score += 7
            elif savings_rate >= 0.1:
                score += 5
        
        if score >= 80:
            return {"score": score, "color": ft.Colors.GREEN, "status": "Отлично"}
        elif score >= 60:
            return {"score": score, "color": ft.Colors.ORANGE, "status": "Хорошо"}
        else:
            return {"score": score, "color": ft.Colors.RED, "status": "Требует внимания"}
    
    def get_ai_recommendations(self):
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        salary = self.finance_app.data["salary"]
        monthly_expenses = self.calculate_average_monthly_expenses()
        rent = self.finance_app.data["rent"]
        goals = self.finance_app.data["goals"]
        
        recommendations = []
        
        # Анализ резерва
        if current_money < safety_reserve:
            deficit = safety_reserve - current_money
            recommendations.append(
                ft.Text(f"🚨 СРОЧНО: Накопите {deficit:,.0f} ₽ для резерва", 
                       color=ft.Colors.RED, size=14, weight=ft.FontWeight.BOLD)
            )
        
        # Анализ расходов
        if monthly_expenses > salary * 0.8:
            recommendations.append(
                ft.Text(f"💡 Сократите расходы на {monthly_expenses - salary * 0.7:,.0f} ₽/мес", 
                       color=ft.Colors.ORANGE, size=14)
            )
        
        # Анализ целей
        if goals:
            total_goal_amount = sum(goal["amount"] for goal in goals)
            total_invested = sum(self.finance_app.data["goal_investments"].values())
            if total_invested < total_goal_amount * 0.1:
                recommendations.append(
                    ft.Text(f"🎯 Начните инвестировать в цели (осталось {total_goal_amount - total_invested:,.0f} ₽)", 
                           color=ft.Colors.BLUE, size=14)
                )
        
        # Праздничные рекомендации
        current_month = datetime.now().month
        if current_month == 12:
            recommendations.append(
                ft.Text("🎄 Новый год: отложите 15,000-30,000 ₽ на подарки", 
                       color=ft.Colors.PURPLE, size=14)
            )
        
        return recommendations
    
    def create_detailed_analytics(self):
        current_money = self.finance_app.data["current_money"]
        salary = self.finance_app.data["salary"]
        transactions = self.finance_app.data["transactions"]
        monthly_expenses = self.calculate_average_monthly_expenses()
        
        # Анализ по категориям расходов
        expense_categories = self.analyze_expense_categories()
        
        # Тренды
        trends = self.calculate_trends()
        
        return ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("📈 Тренды", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Расходы: {trends['expense_trend']}", 
                           color=ft.Colors.RED if trends['expense_trend'] == "↗️ Растут" else ft.Colors.GREEN),
                    ft.Text(f"Доходы: {trends['income_trend']}", 
                           color=ft.Colors.GREEN if trends['income_trend'] == "↗️ Растут" else ft.Colors.RED),
                    ft.Text(f"Сбережения: {trends['savings_trend']}", 
                           color=ft.Colors.BLUE if trends['savings_trend'] == "↗️ Растут" else ft.Colors.ORANGE)
                ], expand=True),
                ft.Column([
                    ft.Text("💰 Категории расходов", size=16, weight=ft.FontWeight.BOLD),
                    ft.Column([
                        ft.Text(f"{cat}: {amount:,.0f} ₽", size=12) 
                        for cat, amount in expense_categories.items()
                    ], spacing=2)
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            ft.Text("📊 Месячная статистика", size=16, weight=ft.FontWeight.BOLD),
            self.create_monthly_chart()
        ], spacing=10)
    
    def analyze_expense_categories(self):
        transactions = self.finance_app.data["transactions"]
        current_month = datetime.now().strftime("%Y-%m")
        
        categories = {}
        category_names = {
            "food": "🍎 Еда",
            "restaurants": "🍽️ Рестораны", 
            "games": "🎮 Игры",
            "transport": "🚗 Транспорт",
            "clothing": "👕 Одежда",
            "electronics": "📱 Электроника",
            "entertainment": "🎬 Развлечения",
            "other": "📦 Прочее"
        }
        
        for transaction in transactions:
            if transaction["type"] == "expense" and transaction["date"].startswith(current_month):
                amount = transaction["amount"]
                category = transaction.get("category", "other")
                category_name = category_names.get(category, "📦 Прочее")
                categories[category_name] = categories.get(category_name, 0) + amount
        
        return dict(sorted(categories.items(), key=lambda x: x[1], reverse=True))
    
    def calculate_trends(self):
        transactions = self.finance_app.data["transactions"]
        
        # Сравниваем последние 2 месяца
        current_month = datetime.now().strftime("%Y-%m")
        last_month = (datetime.now() - timedelta(days=30)).strftime("%Y-%m")
        
        current_expenses = sum(t["amount"] for t in transactions 
                             if t["type"] == "expense" and t["date"].startswith(current_month))
        last_expenses = sum(t["amount"] for t in transactions 
                          if t["type"] == "expense" and t["date"].startswith(last_month))
        
        current_income = sum(t["amount"] for t in transactions 
                           if t["type"] == "income" and t["date"].startswith(current_month))
        last_income = sum(t["amount"] for t in transactions 
                        if t["type"] == "income" and t["date"].startswith(last_month))
        
        return {
            "expense_trend": "↗️ Растут" if current_expenses > last_expenses else "↘️ Снижаются",
            "income_trend": "↗️ Растут" if current_income > last_income else "↘️ Снижаются",
            "savings_trend": "↗️ Растут" if (current_income - current_expenses) > (last_income - last_expenses) else "↘️ Снижаются"
        }
    
    def create_monthly_chart(self):
        transactions = self.finance_app.data["transactions"]
        
        # Создаем данные за последние 6 месяцев
        months_data = []
        for i in range(6):
            month_date = datetime.now() - timedelta(days=30*i)
            month_str = month_date.strftime("%Y-%m")
            month_name = month_date.strftime("%b")
            
            month_income = sum(t["amount"] for t in transactions 
                             if t["type"] == "income" and t["date"].startswith(month_str))
            month_expenses = sum(t["amount"] for t in transactions 
                               if t["type"] == "expense" and t["date"].startswith(month_str))
            
            months_data.append({
                "month": month_name,
                "income": month_income,
                "expenses": month_expenses,
                "savings": month_income - month_expenses
            })
        
        months_data.reverse()  # От старых к новым
        
        return ft.Column([
            ft.Row([
                ft.Text(month["month"], size=12, weight=ft.FontWeight.BOLD),
                ft.Text(f"Доход: {month['income']:,.0f} ₽", size=10, color=ft.Colors.GREEN),
                ft.Text(f"Расход: {month['expenses']:,.0f} ₽", size=10, color=ft.Colors.RED),
                ft.Text(f"Сбережения: {month['savings']:,.0f} ₽", size=10, color=ft.Colors.BLUE)
            ]) for month in months_data
        ], spacing=5)
    
    def create_holiday_planning(self):
        current_month = datetime.now().month
        current_money = self.finance_app.data["current_money"]
        salary = self.finance_app.data["salary"]
        
        holiday_planning = []
        
        # Новый год
        if current_month == 12:
            new_year_budget = min(salary * 0.2, 30000)  # 20% от зарплаты или 30,000 ₽
            holiday_planning.append(
                ft.Column([
                    ft.Text("🎄 Новый год 2024", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Рекомендуемый бюджет: {new_year_budget:,.0f} ₽", size=14),
                    ft.Text("• Подарки: 15,000-20,000 ₽", size=12),
                    ft.Text("• Праздничный стол: 8,000-12,000 ₽", size=12),
                    ft.Text("• Развлечения: 5,000-8,000 ₽", size=12),
                    ft.Text(f"Доступно: {current_money:,.0f} ₽", 
                           color=ft.Colors.GREEN if current_money >= new_year_budget else ft.Colors.RED, size=12)
                ], spacing=5)
            )
        elif current_month == 11:
            holiday_planning.append(
                ft.Column([
                    ft.Text("🎄 Подготовка к Новому году", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("Начните откладывать 5,000-8,000 ₽/мес", size=14),
                    ft.Text("• Создайте список подарков", size=12),
                    ft.Text("• Ищите скидки заранее", size=12),
                    ft.Text("• Планируйте меню", size=12)
                ], spacing=5)
            )
        
        # Другие праздники
        holidays = [
            {"month": 2, "name": "День Святого Валентина", "budget": 5000, "icon": "💕"},
            {"month": 3, "name": "8 Марта", "budget": 8000, "icon": "🌸"},
            {"month": 5, "name": "День Победы", "budget": 3000, "icon": "🎖️"},
            {"month": 6, "name": "День России", "budget": 2000, "icon": "🇷🇺"},
            {"month": 9, "name": "День знаний", "budget": 10000, "icon": "📚"},
            {"month": 11, "name": "День народного единства", "budget": 2000, "icon": "🤝"}
        ]
        
        for holiday in holidays:
            if holiday["month"] == current_month:
                holiday_planning.append(
                    ft.Column([
                        ft.Text(f"{holiday['icon']} {holiday['name']}", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Рекомендуемый бюджет: {holiday['budget']:,.0f} ₽", size=14),
                        ft.Text(f"Доступно: {current_money:,.0f} ₽", 
                               color=ft.Colors.GREEN if current_money >= holiday['budget'] else ft.Colors.RED, size=12)
                    ], spacing=5)
                )
        
        if not holiday_planning:
            holiday_planning.append(
                ft.Text("📅 В этом месяце нет крупных праздников", size=14, color=ft.Colors.GREY_600)
            )
        
        return ft.Column(holiday_planning, spacing=10)
    
    def create_yearly_forecast(self):
        current_money = self.finance_app.data["current_money"]
        salary = self.finance_app.data["salary"]
        monthly_expenses = self.calculate_average_monthly_expenses()
        rent = self.finance_app.data["rent"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        goals = self.finance_app.data["goals"]
        
        # Прогноз на 12 месяцев
        monthly_savings = salary - monthly_expenses - rent
        forecast_months = []
        
        current_balance = current_money
        for month in range(1, 13):
            month_date = datetime.now() + timedelta(days=30*month)
            month_name = month_date.strftime("%B %Y")
            
            # Учитываем праздники
            holiday_adjustment = 0
            if month_date.month == 12:  # Новый год
                holiday_adjustment = -min(salary * 0.2, 30000)
            elif month_date.month in [2, 3, 5, 6, 9, 11]:  # Другие праздники
                holiday_adjustment = -5000
            
            current_balance += monthly_savings + holiday_adjustment
            
            forecast_months.append({
                "month": month_name,
                "balance": current_balance,
                "safe": current_balance >= safety_reserve,
                "holiday": holiday_adjustment != 0
            })
        
        return ft.Column([
            ft.Text("Прогноз баланса на год:", size=16, weight=ft.FontWeight.BOLD),
            ft.Column([
                ft.Row([
                    ft.Text(forecast["month"], size=12, weight=ft.FontWeight.BOLD, expand=2),
                    ft.Text(f"{forecast['balance']:,.0f} ₽", size=12, 
                           color=ft.Colors.GREEN if forecast["safe"] else ft.Colors.RED, expand=1),
                    ft.Text("🎄" if forecast["holiday"] else "✅" if forecast["safe"] else "⚠️", size=12, expand=0)
                ]) for forecast in forecast_months
            ], spacing=3),
            
            ft.Divider(),
            
            ft.Text("📊 Ключевые показатели года:", size=14, weight=ft.FontWeight.BOLD),
            ft.Text(f"• Ожидаемые сбережения: {monthly_savings * 12:,.0f} ₽", size=12),
            ft.Text(f"• Праздничные расходы: ~{min(salary * 0.2, 30000) + 5000 * 5:,.0f} ₽", size=12),
            ft.Text(f"• Итоговый баланс: {forecast_months[-1]['balance']:,.0f} ₽", size=12),
            ft.Text(f"• Безопасность: {'✅ Обеспечена' if forecast_months[-1]['safe'] else '⚠️ Под угрозой'}", 
                   size=12, color=ft.Colors.GREEN if forecast_months[-1]['safe'] else ft.Colors.RED)
        ], spacing=10)
    
    def create_smart_tips(self):
        current_money = self.finance_app.data["current_money"]
        salary = self.finance_app.data["salary"]
        monthly_expenses = self.calculate_average_monthly_expenses()
        safety_reserve = self.finance_app.data["safety_reserve"]
        
        tips = []
        
        # Советы по резерву
        if current_money < safety_reserve:
            tips.append(
                ft.Text("💡 СОВЕТ: Создайте автоматический перевод на отдельный счет для резерва", 
                       size=12, color=ft.Colors.BLUE)
            )
        
        # Советы по расходам
        if monthly_expenses > salary * 0.7:
            tips.append(
                ft.Text("💡 СОВЕТ: Ведите учет всех трат - это поможет найти скрытые расходы", 
                       size=12, color=ft.Colors.ORANGE)
            )
        
        # Советы по инвестициям
        if current_money > safety_reserve * 2:
            tips.append(
                ft.Text("💡 СОВЕТ: Рассмотрите инвестиции - избыточные деньги могут работать на вас", 
                       size=12, color=ft.Colors.GREEN)
            )
        
        # Сезонные советы
        current_month = datetime.now().month
        if current_month == 12:
            tips.append(
                ft.Text("🎄 СОВЕТ: Покупайте подарки заранее - в декабре цены выше", 
                       size=12, color=ft.Colors.PURPLE)
            )
        elif current_month in [1, 2]:
            tips.append(
                ft.Text("❄️ СОВЕТ: Зима - время экономии. Отложите деньги на летний отпуск", 
                       size=12, color=ft.Colors.BLUE)
            )
        
        # Общие советы
        tips.extend([
            ft.Text("💡 СОВЕТ: Правило 50/30/20: 50% на нужды, 30% на желания, 20% на сбережения", 
                   size=12, color=ft.Colors.GREY_700),
            ft.Text("💡 СОВЕТ: Регулярно пересматривайте свои финансовые цели", 
                   size=12, color=ft.Colors.GREY_700),
            ft.Text("💡 СОВЕТ: Используйте кэшбэк и скидки - это может сэкономить 5-10%", 
                   size=12, color=ft.Colors.GREY_700)
        ])
        
        return ft.Column(tips, spacing=5)
    
    def create_wants_calculator(self):
        self.want_item = ft.TextField(label="Что хотите купить?", width=200)
        self.want_price = ft.TextField(label="Цена (₽)", keyboard_type=ft.KeyboardType.NUMBER, width=150)
        self.want_category = ft.Dropdown(
            label="Категория",
            width=150,
            options=[
                ft.dropdown.Option("Игры", "games"),
                ft.dropdown.Option("Рестораны", "restaurants"),
                ft.dropdown.Option("Видеокарта", "electronics"),
                ft.dropdown.Option("Телефон", "electronics"),
                ft.dropdown.Option("Одежда", "clothing"),
                ft.dropdown.Option("Развлечения", "entertainment"),
                ft.dropdown.Option("Прочее", "other")
            ]
        )
        self.want_result = ft.Text("Введите данные для анализа", size=14, color=ft.Colors.GREY_600)
        
        return ft.Column([
            ft.Row([
                self.want_item,
                self.want_price,
                self.want_category,
                ft.ElevatedButton("Анализировать", on_click=self.analyze_want)
            ], spacing=10),
            ft.Container(content=self.want_result, padding=10)
        ], spacing=10)
    
    def analyze_want(self, e):
        try:
            item = self.want_item.value
            price = float(self.want_price.value) if self.want_price.value else 0
            category = self.want_category.value
            
            if not item or price <= 0 or not category:
                self.want_result = ft.Text("Введите корректные данные", size=14, color=ft.Colors.RED)
                self.page.update()
                return
            
            current_money = self.finance_app.data["current_money"]
            safety_reserve = self.finance_app.data["safety_reserve"]
            salary = self.finance_app.data["salary"]
            monthly_expenses = self.calculate_average_monthly_expenses()
            
            # Анализ по категориям
            category_analysis = self.get_category_analysis(category, price, salary)
            
            # Общий анализ доступности
            available_money = current_money - safety_reserve
            months_to_save = (price - available_money) / max(salary - monthly_expenses, 1) if price > available_money else 0
            
            # Рекомендации
            if price <= available_money:
                recommendation = "✅ Можете купить сейчас"
                color = ft.Colors.GREEN
                priority = "Высокий"
            elif months_to_save <= 3:
                recommendation = f"⏰ Нужно копить {months_to_save:.1f} месяцев"
                color = ft.Colors.ORANGE
                priority = "Средний"
            else:
                recommendation = f"❌ Слишком дорого - {months_to_save:.1f} месяцев"
                color = ft.Colors.RED
                priority = "Низкий"
            
            self.want_result = ft.Column([
                ft.Text(f"🎯 {item}", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(f"💰 Цена: {price:,.0f} ₽", size=14),
                ft.Text(f"📂 Категория: {category_analysis['name']}", size=14),
                ft.Text(f"🎯 Приоритет: {priority}", size=14, color=color),
                ft.Text(f"💳 Доступно: {available_money:,.0f} ₽", size=14),
                ft.Text(f"⏰ Время накопления: {months_to_save:.1f} мес", size=14),
                ft.Text(recommendation, size=14, color=color, weight=ft.FontWeight.BOLD),
                
                ft.Divider(),
                
                ft.Text("💡 Рекомендации:", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(category_analysis['advice'], size=12),
                ft.Text(f"• Бюджет на категорию: {category_analysis['budget']:,.0f} ₽/мес", size=12),
                ft.Text(f"• Доля от дохода: {category_analysis['percentage']:.1f}%", size=12)
            ], spacing=5)
            
            self.page.update()
        except ValueError:
            self.want_result = ft.Text("Ошибка в данных", size=14, color=ft.Colors.RED)
            self.page.update()
    
    def get_category_analysis(self, category, price, salary):
        category_data = {
            "games": {
                "name": "Игры",
                "budget": salary * 0.05,  # 5% от дохода
                "percentage": 5,
                "advice": "• Покупайте игры со скидками (Steam Sale)\n• Установите лимит: 3,000 ₽/мес\n• Рассмотрите Game Pass"
            },
            "restaurants": {
                "name": "Рестораны",
                "budget": salary * 0.1,  # 10% от дохода
                "percentage": 10,
                "advice": "• Выбирайте бизнес-ланчи\n• Готовьте дома с девушкой\n• Используйте скидки"
            },
            "clothing": {
                "name": "Одежда",
                "budget": salary * 0.03,  # 3% от дохода
                "percentage": 3,
                "advice": "• Покупайте в сезон скидок\n• Выбирайте качественные вещи\n• Продавайте старую одежду"
            },
            "electronics": {
                "name": "Электроника",
                "budget": salary * 0.15,   # 15% от дохода
                "percentage": 15,
                "advice": "• Покупайте в период скидок (Черная пятница)\n• Рассмотрите б/у видеокарты\n• Используйте кэшбэк карты"
            },
            "entertainment": {
                "name": "Развлечения",
                "budget": salary * 0.05,  # 5% от дохода
                "percentage": 5,
                "advice": "• Кино, кафе с девушкой\n• Ищите бесплатные мероприятия\n• Планируйте бюджет заранее"
            },
            "other": {
                "name": "Прочее",
                "budget": salary * 0.02,  # 2% от дохода
                "percentage": 2,
                "advice": "• Подумайте о необходимости\n• Ищите альтернативы\n• Отложите на потом"
            }
        }
        
        return category_data.get(category, category_data["other"])
    
    def create_my_budget_analysis(self):
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        salary = self.finance_app.data["salary"]
        
        # Реальные данные текущего месяца
        current_month_expenses = self.get_current_month_expenses()
        current_month_income = self.get_current_month_income()
        
        # Оставшиеся дни в месяце
        current_day = datetime.now().day
        import calendar
        current_year = datetime.now().year
        current_month = datetime.now().month
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        remaining_days = days_in_month - current_day + 1
        
        # ChatGPT подписка
        chatgpt_cost = 3000 if self.finance_app.data["chatgpt_enabled"] else 0
        
        # Ожидаемые расходы до конца месяца (средние)
        avg_monthly_expenses = self.calculate_average_monthly_expenses()
        expected_remaining_expenses = (avg_monthly_expenses / days_in_month) * remaining_days
        
        # Доступные деньги с учетом уже потраченного
        # Если месяц заканчивается, не вычитаем текущие траты дважды
        if remaining_days <= 2:  # Последние дни месяца
            available_money = current_money - safety_reserve
        else:
            available_money = current_money - safety_reserve - current_month_expenses
        
        daily_budget = available_money / remaining_days if remaining_days > 0 else 0
        weekly_budget = available_money / (remaining_days / 7) if remaining_days > 0 else 0
        monthly_budget = available_money
        
        # ChatGPT подписка
        chatgpt_cost = 3000 if self.finance_app.data["chatgpt_enabled"] else 0
        
        return ft.Column([
            ft.Text("💳 Мои деньги (реальные данные):", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"📅 Сегодня: {datetime.now().strftime('%d %B %Y')}", size=12, color=ft.Colors.GREY_600),
            ft.Text(f"⏰ Осталось дней в месяце: {remaining_days}", size=12, color=ft.Colors.GREY_600),
            ft.Divider(),
            ft.Row([
                ft.Column([
                    ft.Text("💰 В день", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{daily_budget:,.0f} ₽", size=18, color=ft.Colors.GREEN),
                    ft.Text("свободно", size=12, color=ft.Colors.GREY_600)
                ], expand=True),
                ft.Column([
                    ft.Text("📅 В неделю", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{weekly_budget:,.0f} ₽", size=18, color=ft.Colors.BLUE),
                    ft.Text("свободно", size=12, color=ft.Colors.GREY_600)
                ], expand=True),
                ft.Column([
                    ft.Text("📆 В месяц", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{monthly_budget:,.0f} ₽", size=18, color=ft.Colors.ORANGE),
                    ft.Text("свободно", size=12, color=ft.Colors.GREY_600)
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            ft.Text("📊 Мои расходы в этом месяце:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"• Доходы: {current_month_income:,.0f} ₽", size=14, color=ft.Colors.GREEN),
            ft.Text(f"• Траты: {current_month_expenses:,.0f} ₽", size=14, color=ft.Colors.RED),
            ft.Text(f"• Ожидаемые траты до конца месяца: {expected_remaining_expenses:,.0f} ₽", size=14, color=ft.Colors.ORANGE),
            ft.Text(f"• Квартплата: 25,000 ₽", size=14, color=ft.Colors.ORANGE),
            ft.Text(f"• ChatGPT: {chatgpt_cost:,.0f} ₽", size=14, color=ft.Colors.PURPLE),
            ft.Text(f"• Доступно для трат: {available_money:,.0f} ₽", size=14, color=ft.Colors.GREEN if available_money >= 0 else ft.Colors.RED),
            
            ft.Divider(),
            
            ft.Text("💡 Рекомендации:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"• На еду в день: {max(0, daily_budget * 0.4):,.0f} ₽", size=12, color=ft.Colors.GREEN if daily_budget >= 0 else ft.Colors.RED),
            ft.Text(f"• На игры в день: {max(0, daily_budget * 0.2):,.0f} ₽", size=12, color=ft.Colors.BLUE if daily_budget >= 0 else ft.Colors.RED),
            ft.Text(f"• На развлечения в день: {max(0, daily_budget * 0.2):,.0f} ₽", size=12, color=ft.Colors.ORANGE if daily_budget >= 0 else ft.Colors.RED),
            ft.Text(f"• На накопления в день: {max(0, daily_budget * 0.2):,.0f} ₽", size=12, color=ft.Colors.BLUE if daily_budget >= 0 else ft.Colors.RED)
        ], spacing=10)
    
    def create_my_games_analysis(self):
        # Анализ игровых трат
        game_transactions = [t for t in self.finance_app.data["transactions"] 
                           if t.get("category") == "games"]
        monthly_game_spending = sum(t["amount"] for t in game_transactions 
                                  if t["type"] == "expense" and t["date"].startswith(datetime.now().strftime("%Y-%m")))
        
        salary = self.finance_app.data["salary"]
        recommended_game_budget = salary * 0.05  # 5% от дохода на игры
        
        return ft.Column([
            ft.Text("🎮 Мои игровые траты:", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    ft.Text("💸 Потрачено", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{monthly_game_spending:,.0f} ₽", size=16, color=ft.Colors.RED),
                    ft.Text("в этом месяце", size=12)
                ], expand=True),
                ft.Column([
                    ft.Text("🎯 Лимит", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{recommended_game_budget:,.0f} ₽", size=16, color=ft.Colors.GREEN),
                    ft.Text("рекомендуется", size=12)
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            ft.Text("🎮 Мои игры:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("• Покупаю игры со скидками (Steam Sale)", size=12),
            ft.Text("• Лимит на донаты: 1,000-2,000 ₽/мес", size=12),
            ft.Text("• Иногда покупаю игру за 3,000 ₽", size=12),
            ft.Text("• Рассматриваю Game Pass", size=12),
            
            ft.Divider(),
            
            ft.Text("💡 Советы по играм:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("• Жди скидок - экономия до 70%", size=12),
            ft.Text("• Используй кэшбэк от банка", size=12),
            ft.Text("• Продавай старые игры", size=12),
            ft.Text("• Не трать больше 5% от зарплаты", size=12)
        ], spacing=10)
    
    def create_my_food_analysis(self):
        # Анализ трат на еду
        food_transactions = [t for t in self.finance_app.data["transactions"] 
                           if t.get("category") in ["food", "restaurants"]]
        monthly_food_spending = sum(t["amount"] for t in food_transactions 
                                  if t["type"] == "expense" and t["date"].startswith(datetime.now().strftime("%Y-%m")))
        
        salary = self.finance_app.data["salary"]
        recommended_food_budget = salary * 0.15  # 15% от дохода на еду
        
        return ft.Column([
            ft.Text("🍽️ Мои траты на еду:", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    ft.Text("💸 Потрачено", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{monthly_food_spending:,.0f} ₽", size=16, color=ft.Colors.RED),
                    ft.Text("в этом месяце", size=12)
                ], expand=True),
                ft.Column([
                    ft.Text("🎯 Лимит", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{recommended_food_budget:,.0f} ₽", size=16, color=ft.Colors.GREEN),
                    ft.Text("рекомендуется", size=12)
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            ft.Text("🍽️ Моя еда с девушкой:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("• Готовим дома - экономим деньги", size=12),
            ft.Text("• Ходим в рестораны 1-2 раза в неделю", size=12),
            ft.Text("• Выбираем бизнес-ланчи", size=12),
            ft.Text("• Заказываем доставку иногда", size=12),
            
            ft.Divider(),
            
            ft.Text("💡 Советы по еде:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("• Планируй меню на неделю", size=12),
            ft.Text("• Покупай продукты по акциям", size=12),
            ft.Text("• Готовь дома чаще - дешевле", size=12),
            ft.Text("• Используй скидки в ресторанах", size=12)
        ], spacing=10)
    
    def create_my_purchases_analysis(self):
        # Анализ покупок электроники
        electronics_transactions = [t for t in self.finance_app.data["transactions"] 
                                  if t.get("category") == "electronics"]
        monthly_electronics_spending = sum(t["amount"] for t in electronics_transactions 
                                         if t["type"] == "expense" and t["date"].startswith(datetime.now().strftime("%Y-%m")))
        
        salary = self.finance_app.data["salary"]
        recommended_electronics_budget = salary * 0.15  # 15% от дохода на электронику
        
        return ft.Column([
            ft.Text("💻 Мои покупки электроники:", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    ft.Text("💸 Потрачено", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{monthly_electronics_spending:,.0f} ₽", size=16, color=ft.Colors.RED),
                    ft.Text("в этом месяце", size=12)
                ], expand=True),
                ft.Column([
                    ft.Text("🎯 Лимит", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{recommended_electronics_budget:,.0f} ₽", size=16, color=ft.Colors.GREEN),
                    ft.Text("рекомендуется", size=12)
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            ft.Text("💻 Мои планы покупок:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("• Новая видеокарта - приоритет", size=12),
            ft.Text("• Новый телефон - когда старый сломается", size=12),
            ft.Text("• Игровая периферия - по необходимости", size=12),
            ft.Text("• Обновление ПК - раз в 2-3 года", size=12),
            
            ft.Divider(),
            
            ft.Text("💡 Советы по покупкам:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("• Покупай в период скидок (Черная пятница)", size=12),
            ft.Text("• Рассмотри б/у видеокарты", size=12),
            ft.Text("• Используй кэшбэк карты", size=12),
            ft.Text("• Копи деньги заранее", size=12)
        ], spacing=10)
    
    def create_my_monthly_analysis(self):
        # Анализ по месяцам
        transactions = self.finance_app.data["transactions"]
        current_year = datetime.now().year
        
        monthly_data = {}
        for month in range(1, 13):
            month_str = f"{current_year}-{month:02d}"
            month_transactions = [t for t in transactions if t["date"].startswith(month_str)]
            
            income = sum(t["amount"] for t in month_transactions if t["type"] == "income")
            expenses = sum(t["amount"] for t in month_transactions if t["type"] == "expense")
            
            monthly_data[month] = {
                "income": income,
                "expenses": expenses,
                "balance": income - expenses
            }
        
        # Находим месяц с наибольшими тратами
        max_expenses_month = max(monthly_data.keys(), key=lambda m: monthly_data[m]["expenses"])
        min_expenses_month = min(monthly_data.keys(), key=lambda m: monthly_data[m]["expenses"])
        
        return ft.Column([
            ft.Text("📈 Мои траты по месяцам:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"• Больше всего тратил в {max_expenses_month} месяце: {monthly_data[max_expenses_month]['expenses']:,.0f} ₽", size=12),
            ft.Text(f"• Меньше всего тратил в {min_expenses_month} месяце: {monthly_data[min_expenses_month]['expenses']:,.0f} ₽", size=12),
            
            ft.Divider(),
            
            ft.Text("📊 Последние 3 месяца:", size=16, weight=ft.FontWeight.BOLD),
            *[ft.Text(f"• {month} месяц: Доходы {monthly_data[month]['income']:,.0f} ₽, Расходы {monthly_data[month]['expenses']:,.0f} ₽", size=12) 
              for month in range(10, 13) if month in monthly_data],
            
            ft.Divider(),
            
            ft.Text("💡 Выводы:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("• Следи за тратами каждый месяц", size=12),
            ft.Text("• Планируй большие покупки заранее", size=12),
            ft.Text("• Откладывай деньги на видеокарту", size=12),
            ft.Text("• Не трать больше чем зарабатываешь", size=12)
        ], spacing=10)
    
    def create_student_tips(self):
        return ft.Column([
            ft.Text("👨‍🎓 Советы для студента:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("• Учись и работай - это твое будущее", size=12),
            ft.Text("• Не трать все деньги сразу", size=12),
            ft.Text("• Копи на важные покупки", size=12),
            ft.Text("• Используй студенческие скидки", size=12),
            ft.Text("• Планируй бюджет на месяц", size=12),
            ft.Text("• Не бери кредиты без необходимости", size=12),
            ft.Text("• Инвестируй в себя (курсы, навыки)", size=12),
            ft.Text("• Наслаждайся студенческой жизнью", size=12)
        ], spacing=5)
    
    def create_gift_analysis(self):
        birthdays = self.finance_app.data["birthdays"]
        salary = self.finance_app.data["salary"]
        monthly_expenses = self.calculate_average_monthly_expenses()
        chatgpt_cost = 3000 if self.finance_app.data["chatgpt_enabled"] else 0
        
        # Анализ подарков по месяцам
        monthly_gifts = {}
        total_gift_cost = 0
        
        for birthday in birthdays:
            month = self.convert_month_to_int(birthday["month"])
            
            cost = birthday["cost"]
            if month not in monthly_gifts:
                monthly_gifts[month] = []
            monthly_gifts[month].append(birthday)
            total_gift_cost += cost
        
        # Анализ по типам отношений
        relationship_costs = {}
        for birthday in birthdays:
            rel = birthday.get("relationship", "other")
            if rel not in relationship_costs:
                relationship_costs[rel] = {"count": 0, "total": 0}
            relationship_costs[rel]["count"] += 1
            relationship_costs[rel]["total"] += birthday["cost"]
        
        # Рекомендации
        monthly_savings = salary - monthly_expenses - chatgpt_cost
        gift_budget_ratio = total_gift_cost / salary if salary > 0 else 0
        
        return ft.Column([
            ft.Text("🎁 Мой анализ подарков:", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    ft.Text("💰 Общая стоимость", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{total_gift_cost:,.0f} ₽", size=18, color=ft.Colors.RED),
                    ft.Text("в год", size=12)
                ], expand=True),
                ft.Column([
                    ft.Text("📊 Доля от дохода", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{gift_budget_ratio*100:.1f}%", size=18, color=ft.Colors.BLUE),
                    ft.Text("от зарплаты", size=12)
                ], expand=True),
                ft.Column([
                    ft.Text("👥 Количество ДР", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{len(birthdays)}", size=18, color=ft.Colors.GREEN),
                    ft.Text("человек", size=12)
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            ft.Text("📅 Подарки по месяцам:", size=16, weight=ft.FontWeight.BOLD),
            *[ft.Text(f"• {['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'][month]}: {sum(b['cost'] for b in gifts):,.0f} ₽", size=12) 
              for month, gifts in sorted(monthly_gifts.items())],
            
            ft.Divider(),
            
            ft.Text("👥 Анализ по отношениям:", size=16, weight=ft.FontWeight.BOLD),
            *[ft.Text(f"• {self.get_relationship_name(rel)}: {data['total']:,.0f} ₽ ({data['count']} чел.)", size=12) 
              for rel, data in relationship_costs.items()],
            
            ft.Divider(),
            
            ft.Text("💡 Рекомендации по подаркам:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"• Бюджет на подарки: {int(salary * 0.15):,.0f} ₽/год (15% от дохода)", size=12),
            ft.Text(f"• Текущие траты: {total_gift_cost:,.0f} ₽/год", size=12, 
                   color=ft.Colors.GREEN if total_gift_cost <= salary * 0.15 else ft.Colors.RED),
            ft.Text(f"• Можно потратить: {int(salary * 0.15) - total_gift_cost:,.0f} ₽ еще", size=12),
            ft.Text("• Покупай подарки заранее со скидками", size=12),
            ft.Text("• Делай подарки своими руками - дешевле", size=12),
            ft.Text("• Планируй бюджет на каждый ДР", size=12)
        ], spacing=10)
    
    def get_relationship_name(self, relationship):
        names = {
            "Девушка": "Девушка",
            "Мама": "Мама", 
            "Папа": "Папа",
            "Бабушка": "Бабушка",
            "Брат/Сестра": "Брат/Сестра",
            "Друг": "Друзья",
            "Коллега": "Коллеги",
            "Другое": "Другое"
        }
        return names.get(relationship, "Неизвестно")
    
    def convert_month_to_int(self, month_value):
        """Преобразует месяц в число (может быть строкой или числом)"""
        month_str = str(month_value)
        if month_str.isdigit():
            return int(month_str)
        else:
            # Если это название месяца, преобразуем в число
            month_names = ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 
                          'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
            try:
                return month_names.index(month_str)
            except ValueError:
                return 1  # По умолчанию январь
    
    def create_smart_savings_helper(self):
        current_money = self.finance_app.data["current_money"]
        salary = self.finance_app.data["salary"]
        monthly_expenses = self.calculate_average_monthly_expenses()
        chatgpt_cost = 3000 if self.finance_app.data["chatgpt_enabled"] else 0
        safety_reserve = self.finance_app.data["safety_reserve"]
        
        # Расчеты
        monthly_savings = salary - monthly_expenses - chatgpt_cost
        available_for_savings = current_money - safety_reserve
        
        # Анализ лучших месяцев для накоплений
        current_month = datetime.now().month
        
        # Основные праздники и их влияние на накопления
        holiday_months = {
            1: {"name": "Январь", "holiday": "", "cost": 0, "risk": "Низкий", "advice": "Отличный месяц для накоплений"},
            2: {"name": "Февраль", "holiday": "День Святого Валентина", "cost": 5000, "risk": "Средний", "advice": "Осторожно с накоплениями"},
            3: {"name": "Март", "holiday": "8 Марта", "cost": 3000, "risk": "Низкий", "advice": "Можно начинать"},
            4: {"name": "Апрель", "holiday": "Нет", "cost": 0, "risk": "Низкий", "advice": "Отличный месяц для накоплений"},
            5: {"name": "Май", "holiday": "Нет", "cost": 0, "risk": "Низкий", "advice": "Отличный месяц для накоплений"},
            6: {"name": "Июнь", "holiday": "Нет", "cost": 0, "risk": "Низкий", "advice": "Отличный месяц для накоплений"},
            7: {"name": "Июль", "holiday": "Нет", "cost": 0, "risk": "Низкий", "advice": "Лучший месяц для накоплений"},
            8: {"name": "Август", "holiday": "Нет", "cost": 0, "risk": "Низкий", "advice": "Лучший месяц для накоплений"},
            9: {"name": "Сентябрь", "holiday": "Нет", "cost": 0, "risk": "Низкий", "advice": "Отличный месяц для накоплений"},
            10: {"name": "Октябрь", "holiday": "Нет", "cost": 0, "risk": "Низкий", "advice": "Хороший месяц для накоплений"},
            11: {"name": "Ноябрь", "holiday": "Нет", "cost": 0, "risk": "Низкий", "advice": "Отличный месяц для накоплений"},
            12: {"name": "Декабрь", "holiday": "Новый год", "cost": 20000, "risk": "Высокий", "advice": "Не начинай накопления"}
        }
        
        # Добавляем дни рождения
        birthdays = self.finance_app.data["birthdays"]
        for birthday in birthdays:
            month = self.convert_month_to_int(birthday["month"])
            
            if month in holiday_months:
                holiday_months[month]["holiday"] = f"ДР {birthday['name']}"
                holiday_months[month]["cost"] += birthday["cost"]
                holiday_months[month]["risk"] = "Средний" if holiday_months[month]["cost"] > 5000 else "Низкий"
        
        # Рекомендации по месяцам
        best_months = [month for month, data in holiday_months.items() if data["risk"] == "Низкий" and data["cost"] == 0]
        good_months = [month for month, data in holiday_months.items() if data["risk"] == "Низкий" and data["cost"] > 0]
        
        # Стратегия накоплений
        if monthly_savings > 0:
            strategy = "Агрессивная" if monthly_savings > 10000 else "Умеренная" if monthly_savings > 5000 else "Консервативная"
        else:
            strategy = "Критическая - нужно сократить расходы"
        
        return ft.Column([
            ft.Text("🎯 Мой план накоплений:", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    ft.Text("💰 Могу накапливать", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{monthly_savings:,.0f} ₽/мес", size=18, color=ft.Colors.GREEN if monthly_savings > 0 else ft.Colors.RED),
                    ft.Text("в месяц", size=12)
                ], expand=True),
                ft.Column([
                    ft.Text("🎯 Стратегия", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(strategy, size=16, color=ft.Colors.BLUE),
                    ft.Text("накоплений", size=12)
                ], expand=True),
                ft.Column([
                    ft.Text("💎 Доступно", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{available_for_savings:,.0f} ₽", size=18, color=ft.Colors.ORANGE),
                    ft.Text("сейчас", size=12)
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            ft.Text("📅 Лучшие месяцы для накоплений:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("🟢 Отличные месяцы (без праздников):", size=14, color=ft.Colors.GREEN),
            ft.Text(f"• {', '.join([holiday_months[m]['name'] for m in best_months])}", size=12),
            
            ft.Text("🟡 Хорошие месяцы (малые праздники):", size=14, color=ft.Colors.ORANGE),
            ft.Text(f"• {', '.join([holiday_months[m]['name'] for m in good_months])}", size=12),
            
            ft.Text("🔴 Избегай (большие праздники):", size=14, color=ft.Colors.RED),
            ft.Text("• Декабрь (Новый год)", size=12),
            
            ft.Divider(),
            
            ft.Text("💡 Мои рекомендации:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"• Начни накопления в {holiday_months[current_month]['name']} - {holiday_months[current_month]['advice']}", size=12),
            ft.Text(f"• Лучший месяц для старта: {holiday_months[best_months[0]]['name'] if best_months else 'Любой'}", size=12),
            ft.Text(f"• Откладывай {monthly_savings * 0.7:,.0f} ₽ каждый месяц (70% от возможного)", size=12),
            ft.Text(f"• Оставь {monthly_savings * 0.3:,.0f} ₽ на непредвиденные расходы", size=12),
            
            ft.Divider(),
            
            ft.Text("🎯 Конкретный план:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("1. Начни с 1,000-2,000 ₽ в месяц", size=12),
            ft.Text("2. Увеличивай сумму каждые 3 месяца", size=12),
            ft.Text("3. Используй автопереводы в накопительный счет", size=12),
            ft.Text("4. Не трогай накопления без крайней необходимости", size=12),
            ft.Text("5. Покупай видеокарту в период скидок (Черная пятница)", size=12)
        ], spacing=10)
    
    def create_forecast_page(self):
        return ft.Column([
            ft.Text("📅 Прогноз на весь год", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("📊 Детальный прогноз по месяцам", size=18, weight=ft.FontWeight.BOLD),
                        self.create_monthly_forecast()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("🎄 Праздники и подарки", size=18, weight=ft.FontWeight.BOLD),
                        self.create_holidays_forecast()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("🎯 Мои цели на год", size=18, weight=ft.FontWeight.BOLD),
                        self.create_goals_forecast()
                    ], spacing=10),
                    padding=20
                )
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
    
    def create_calculator_page(self):
        # Инициализируем переменные калькулятора
        self.calculator_display = ft.TextField(
            value="0",
            text_align=ft.TextAlign.RIGHT,
            read_only=True,
            width=300,
            height=60,
            text_size=24
        )
        self.calculator_expression = ""
        self.calculator_result = None
        
        return ft.Column([
            ft.Text("🧮 Калькулятор", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("🔢 Обычный калькулятор", size=18, weight=ft.FontWeight.BOLD),
                        self.create_basic_calculator()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("💰 Финансовые функции", size=18, weight=ft.FontWeight.BOLD),
                        self.create_financial_calculator()
                    ], spacing=10),
                    padding=20
                )
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
    
    def create_notes_page(self):
        return ft.Column([
            ft.Text("📝 Финансовые заметки", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("➕ Добавить заметку", size=18, weight=ft.FontWeight.BOLD),
                        self.create_note_input()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("📋 Мои заметки", size=18, weight=ft.FontWeight.BOLD),
                        self.create_notes_list()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("💡 Шаблоны заметок", size=18, weight=ft.FontWeight.BOLD),
                        self.create_note_templates()
                    ], spacing=10),
                    padding=20
                )
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
    
    def get_salary_status(self):
        current_day = datetime.now().day
        current_month = datetime.now().month
        current_year = 2025
        current_year = datetime.now().year
        salary_dates = self.finance_app.data["salary_dates"]
        salary = self.finance_app.data["salary"]
        
        # Получаем количество дней в текущем месяце
        import calendar
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        
        # Если сегодня последние дни месяца
        if current_day >= days_in_month - 2:
            return ft.Text(f"• Статус зарплаты: ✅ Месяц заканчивается - все получено ({salary:,.0f} ₽)", 
                          size=12, color=ft.Colors.GREEN)
        elif current_day >= salary_dates[1]:  # После 22 числа
            return ft.Text(f"• Статус зарплаты: ✅ Обе зарплаты получены ({salary:,.0f} ₽)", 
                          size=12, color=ft.Colors.GREEN)
        elif current_day >= salary_dates[0]:  # Между 8 и 22 числом
            return ft.Text(f"• Статус зарплаты: ⚠️ Получена 1/2 зарплаты ({salary/2:,.0f} ₽ из {salary:,.0f} ₽)", 
                          size=12, color=ft.Colors.ORANGE)
        else:  # До 8 числа
            return ft.Text(f"• Статус зарплаты: ❌ Зарплата еще не получена", 
                          size=12, color=ft.Colors.RED)
    
    def create_monthly_forecast(self):
        current_money = self.finance_app.data["current_money"]
        salary = self.finance_app.data["salary"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        monthly_expenses = self.calculate_average_monthly_expenses()
        chatgpt_cost = 3000 if self.finance_app.data["chatgpt_enabled"] else 0
        # Получаем информацию о квартплате из данных
        rent_paid_until = self.finance_app.data.get("rent_paid_until", "")
        rent_cost = self.finance_app.data.get("rent_cost", 25000)  # Квартплата из настроек или 25,000 по умолчанию
        
        # Получаем текущий месяц
        current_month = datetime.now().month
        current_year = 2025  # Устанавливаем 2025 год
        
        def should_pay_rent(month, year):
            """Определяет, нужно ли платить квартплату в указанном месяце"""
            if not rent_paid_until:
                return True  # Если не указано, платим всегда
            
            try:
                # Парсим дату "до которой уплачена квартплата"
                paid_until = datetime.strptime(rent_paid_until, "%Y-%m-%d")
                # Квартплата платится 10 числа каждого месяца
                target_date = datetime(year, month, 10)
                
                # Если целевой месяц раньше даты уплаты, НЕ нужно платить
                # Например: если квартплата уплачена до 2025-10-10,
                # то в октябре 2025 (2025-10-10) платить НЕ нужно
                should_pay = target_date >= paid_until
                return should_pay
            except:
                return True  # Если ошибка парсинга, платим всегда
        
        # Основные праздники и их стоимость
        holidays = {
            1: {"name": "", "cost": 0, "description": ""},
            2: {"name": "День Святого Валентина", "cost": 5000, "description": "Подарок девушке, ужин"},
            3: {"name": "8 Марта", "cost": 3000, "description": "Подарок маме и девушке"},
            12: {"name": "Новый год", "cost": 20000, "description": "Подарки, еда, празднование"}
        }
        
        # Добавляем дни рождения
        birthdays = self.finance_app.data["birthdays"]
        for birthday in birthdays:
            month = self.convert_month_to_int(birthday["month"])
            
            if month not in holidays:
                holidays[month] = {"name": f"ДР {birthday['name']}", "cost": birthday["cost"], "description": f"Подарок на день рождения {birthday['name']}"}
            else:
                holidays[month]["cost"] += birthday["cost"]
                holidays[month]["name"] += f" + ДР {birthday['name']}"
        
        monthly_forecast = []
        balance = current_money
        
        # Начинаем с текущего месяца и идем 12 месяцев вперед
        for i in range(12):
            month = ((current_month - 1 + i) % 12) + 1
            forecast_year = current_year + ((current_month - 1 + i) // 12)
            month_name = ["", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                         "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"][month]
            month_name_with_year = f"{month_name} {forecast_year}"
            
            # Доходы - 2 раза в месяц (8 и 22 числа)
            salary_dates = self.finance_app.data["salary_dates"]
            half_salary = salary / 2
            
            # Если это текущий месяц, проверяем, сколько зарплат уже получено
            if i == 0:  # Текущий месяц
                current_day = datetime.now().day
                current_month = datetime.now().month
                current_year = datetime.now().year
                
                # Проверяем, какой сейчас месяц в прогнозе
                forecast_month = ((current_month - 1 + i) % 12) + 1
                forecast_year = current_year + ((current_month - 1 + i) // 12)
                
                # Если это действительно текущий месяц
                if forecast_month == current_month and forecast_year == current_year:
                    # Получаем количество дней в текущем месяце
                    import calendar
                    days_in_month = calendar.monthrange(current_year, current_month)[1]
                    
                    # Если сегодня последний день месяца или близко к концу
                    if current_day >= days_in_month - 2:  # Последние 2 дня месяца
                        income = 0  # Зарплата уже получена
                        # Расходы тоже минимальные, так как месяц заканчивается
                        holiday_cost = holidays.get(month, {}).get("cost", 0)
                        # Определяем, нужно ли платить квартплату в этом месяце
                        forecast_year = current_year + ((current_month - 1 + i) // 12)
                        rent_for_month = rent_cost if should_pay_rent(month, forecast_year) else 0
                        expenses = chatgpt_cost + holiday_cost + rent_for_month
                    elif current_day >= salary_dates[1]:  # Уже получены обе зарплаты (после 22 числа)
                        income = 0
                    elif current_day >= salary_dates[0]:  # Получена только первая зарплата (8-21 число)
                        income = half_salary
                    else:  # Не получена ни одна зарплата (до 8 числа)
                        income = salary
                else:
                    income = salary
            else:  # Будущие месяцы
                income = salary
            
            # Расходы
            expenses = 0  # Инициализируем переменную
            holiday_cost = 0  # Инициализируем переменную
            if i == 0:  # Текущий месяц
                current_day = datetime.now().day
                current_month = datetime.now().month
                current_year = datetime.now().year
                forecast_month = ((current_month - 1 + i) % 12) + 1
                forecast_year = current_year + ((current_month - 1 + i) // 12)
                
                if forecast_month == current_month and forecast_year == current_year:
                    import calendar
                    days_in_month = calendar.monthrange(current_year, current_month)[1]
                    
                    # Если сегодня последние дни месяца
                    if current_day >= days_in_month - 2:
                        # Минимальные расходы - только обязательные
                        holiday_cost = holidays.get(month, {}).get("cost", 0)
                        # Определяем, нужно ли платить квартплату в этом месяце
                        forecast_year = current_year + ((current_month - 1 + i) // 12)
                        rent_for_month = rent_cost if should_pay_rent(month, forecast_year) else 0
                        expenses = chatgpt_cost + holiday_cost + rent_for_month
                        total_expenses = expenses
                    else:
                        # Обычные расходы с учетом оставшихся дней
                        remaining_days = days_in_month - current_day + 1
                        daily_expenses = monthly_expenses / days_in_month
                        expected_remaining_expenses = daily_expenses * remaining_days
                        
                        # Добавляем уже потраченные деньги в текущем месяце
                        current_month_expenses = self.get_current_month_expenses()
                        # Определяем, нужно ли платить квартплату в этом месяце
                        forecast_year = current_year + ((current_month - 1 + i) // 12)
                        rent_for_month = rent_cost if should_pay_rent(month, forecast_year) else 0
                        expenses = current_month_expenses + expected_remaining_expenses + chatgpt_cost + rent_for_month
                        holiday_cost = holidays.get(month, {}).get("cost", 0)
                        total_expenses = expenses + holiday_cost
                else:
                    # Определяем, нужно ли платить квартплату в этом месяце
                    forecast_year = current_year + ((current_month - 1 + i) // 12)
                    rent_for_month = rent_cost if should_pay_rent(month, forecast_year) else 0
                    expenses = monthly_expenses + chatgpt_cost + rent_for_month
                    holiday_cost = holidays.get(month, {}).get("cost", 0)
                    total_expenses = expenses + holiday_cost
            else:  # Будущие месяцы
                # Определяем, нужно ли платить квартплату в этом месяце
                forecast_year = current_year + ((current_month - 1 + i) // 12)
                rent_for_month = rent_cost if should_pay_rent(month, forecast_year) else 0
                holiday_cost = holidays.get(month, {}).get("cost", 0)
                expenses = monthly_expenses + chatgpt_cost + rent_for_month
                total_expenses = expenses + holiday_cost
            
            # Баланс
            balance += income - total_expenses
            
            monthly_forecast.append({
                "month": month_name_with_year,
                "income": income,
                "expenses": total_expenses,
                "holiday_cost": holiday_cost,
                "balance": balance,
                "holiday": holidays.get(month, {}).get("name", "")
            })
        
        return ft.Column([
            ft.Text("📅 Прогноз по месяцам:", size=16, weight=ft.FontWeight.BOLD),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("💰 Исходные данные (обновляются в реальном времени):", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(f"• Текущий баланс: {current_money:,.0f} ₽", size=12),
                        ft.Text(f"• Оклад: {salary:,.0f} ₽/месяц (2 раза: {salary/2:,.0f} ₽)", size=12),
                        ft.Text(f"• Даты зарплаты: {self.finance_app.data['salary_dates'][0]} и {self.finance_app.data['salary_dates'][1]} число", size=12),
                        ft.Text(f"• Траты в этом месяце: {self.get_current_month_expenses():,.0f} ₽", size=12, color=ft.Colors.RED),
                        ft.Text(f"• Доходы в этом месяце: {self.get_current_month_income():,.0f} ₽", size=12, color=ft.Colors.GREEN),
                        ft.Text(f"• Средние расходы: {monthly_expenses:,.0f} ₽/месяц", size=12),
                        ft.Text(f"• Квартплата: {rent_cost:,.0f} ₽/месяц", size=12, color=ft.Colors.ORANGE),
                        ft.Text(f"• Уплачена до: {rent_paid_until if rent_paid_until else 'Не указано'}", size=12, color=ft.Colors.BLUE),
                        ft.Text(f"• ChatGPT Plus: {chatgpt_cost:,.0f} ₽/месяц", size=12),
                        ft.Text(f"• Резерв безопасности: {safety_reserve:,.0f} ₽", size=12),
                        ft.Text(f"• Сегодня: {datetime.now().strftime('%d %B %Y')}", size=12, weight=ft.FontWeight.BOLD),
                        self.get_salary_status(),
                        ft.Text(f"• Начинаем с: {['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'][current_month]}", size=12, weight=ft.FontWeight.BOLD)
                    ], spacing=5),
                    padding=15
                )
            ),
            
            # Детальный заголовок таблицы
            ft.Container(
                content=ft.Row([
                    ft.Text("Месяц", size=14, weight=ft.FontWeight.BOLD, expand=2),
                    ft.Text("Доходы", size=14, weight=ft.FontWeight.BOLD, expand=1, text_align=ft.TextAlign.CENTER),
                    ft.Text("Расходы", size=14, weight=ft.FontWeight.BOLD, expand=1, text_align=ft.TextAlign.CENTER),
                    ft.Text("Праздники", size=14, weight=ft.FontWeight.BOLD, expand=1, text_align=ft.TextAlign.CENTER),
                    ft.Text("Баланс", size=14, weight=ft.FontWeight.BOLD, expand=1, text_align=ft.TextAlign.CENTER),
                    ft.Text("Статус", size=14, weight=ft.FontWeight.BOLD, expand=1, text_align=ft.TextAlign.CENTER),
                    ft.Text("Детали", size=14, weight=ft.FontWeight.BOLD, expand=2, text_align=ft.TextAlign.CENTER)
                ]),
                bgcolor=ft.Colors.BLUE_50,
                padding=12,
                border=ft.border.all(1, ft.Colors.BLUE_200)
            ),
            
            # Детальные строки таблицы
            ft.Column([
                ft.Container(
                    content=ft.Row([
                        # Месяц и праздники
                        ft.Column([
                            ft.Text(f"{forecast['month']}", size=13, weight=ft.FontWeight.BOLD),
                            ft.Text(f"{forecast['holiday']}", size=10, color=ft.Colors.PURPLE) if forecast['holiday'] else ft.Text("Нет праздников", size=10, color=ft.Colors.GREY_600)
                        ], expand=2),
                        
                        # Доходы
                        ft.Column([
                            ft.Text(f"{forecast['income']:,.0f} ₽", size=12, color=ft.Colors.GREEN, text_align=ft.TextAlign.CENTER),
                            ft.Text("2 зарплаты", size=9, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER) if forecast['income'] > 0 else ft.Text("Нет", size=9, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)
                        ], expand=1, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        
                        # Расходы
                        ft.Column([
                            ft.Text(f"{forecast['expenses']:,.0f} ₽", size=12, color=ft.Colors.RED, text_align=ft.TextAlign.CENTER),
                            ft.Text("Все расходы", size=9, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)
                        ], expand=1, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        
                        # Праздники
                        ft.Column([
                            ft.Text(f"{forecast['holiday_cost']:,.0f} ₽" if forecast['holiday_cost'] > 0 else "—", 
                                   size=12, color=ft.Colors.PURPLE, text_align=ft.TextAlign.CENTER),
                            ft.Text("Подарки", size=9, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER) if forecast['holiday_cost'] > 0 else ft.Text("", size=9, text_align=ft.TextAlign.CENTER)
                        ], expand=1, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        
                        # Баланс
                        ft.Column([
                            ft.Text(f"{forecast['balance']:,.0f} ₽", size=12, 
                                   color=ft.Colors.GREEN if forecast['balance'] > safety_reserve else ft.Colors.RED, 
                                   text_align=ft.TextAlign.CENTER),
                            ft.Text(f"Резерв: {safety_reserve:,.0f}", size=9, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)
                        ], expand=1, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        
                        # Статус
                        ft.Column([
                            ft.Text("✅ Отлично" if forecast['balance'] > safety_reserve * 1.5 else 
                                   "👍 Хорошо" if forecast['balance'] > safety_reserve else 
                                   "⚠️ Осторожно" if forecast['balance'] > 0 else "❌ Критично", 
                                   size=11, 
                                   color=ft.Colors.GREEN if forecast['balance'] > safety_reserve else 
                                         ft.Colors.ORANGE if forecast['balance'] > 0 else ft.Colors.RED,
                                   text_align=ft.TextAlign.CENTER),
                            ft.Text(f"Свободно: {forecast['balance'] - safety_reserve:,.0f}" if forecast['balance'] > safety_reserve else 
                                   f"Дефицит: {safety_reserve - forecast['balance']:,.0f}", 
                                   size=9, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)
                        ], expand=1, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        
                        # Детали
                        ft.Column([
                            ft.Text(f"Доход: {forecast['income']:,.0f}", size=10, color=ft.Colors.GREEN, text_align=ft.TextAlign.CENTER),
                            ft.Text(f"Расход: {forecast['expenses']:,.0f}", size=10, color=ft.Colors.RED, text_align=ft.TextAlign.CENTER),
                            ft.Text(f"Праздник: {forecast['holiday_cost']:,.0f}", size=10, color=ft.Colors.PURPLE, text_align=ft.TextAlign.CENTER) if forecast['holiday_cost'] > 0 else ft.Text("", size=10, text_align=ft.TextAlign.CENTER),
                            ft.Text(f"Итого: {forecast['income'] - forecast['expenses']:,.0f}", size=10, 
                                   color=ft.Colors.GREEN if forecast['income'] - forecast['expenses'] > 0 else ft.Colors.RED, text_align=ft.TextAlign.CENTER)
                        ], expand=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                    ]),
                    bgcolor=ft.Colors.WHITE if i % 2 == 0 else ft.Colors.GREY_50,
                    padding=12,
                    border=ft.border.all(0.5, ft.Colors.GREY_300)
                ) for i, forecast in enumerate(monthly_forecast)
            ], spacing=1),
            
            ft.Divider(),
            
            # Детальная статистика
            ft.Container(
                content=ft.Column([
                    ft.Text("📊 Детальная статистика прогноза:", size=16, weight=ft.FontWeight.BOLD),
                    
                    # Находим лучший и худший месяцы
                    ft.Row([
                        ft.Column([
                            ft.Text("🏆 Лучший месяц:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                            ft.Text(f"{max(monthly_forecast, key=lambda x: x['balance'])['month']}", size=12, color=ft.Colors.GREEN),
                            ft.Text(f"Баланс: {max(monthly_forecast, key=lambda x: x['balance'])['balance']:,.0f} ₽", size=11, color=ft.Colors.GREEN)
                        ], expand=1),
                        
                        ft.Column([
                            ft.Text("⚠️ Сложный месяц:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
                            ft.Text(f"{min(monthly_forecast, key=lambda x: x['balance'])['month']}", size=12, color=ft.Colors.RED),
                            ft.Text(f"Баланс: {min(monthly_forecast, key=lambda x: x['balance'])['balance']:,.0f} ₽", size=11, color=ft.Colors.RED)
                        ], expand=1)
                    ], spacing=20),
                    
                    ft.Divider(),
                    
                    # Общая статистика
                    ft.Text("💰 Общая статистика за год:", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"• Общий доход: {sum(f['income'] for f in monthly_forecast):,.0f} ₽", size=12, color=ft.Colors.GREEN),
                    ft.Text(f"• Общие расходы: {sum(f['expenses'] for f in monthly_forecast):,.0f} ₽", size=12, color=ft.Colors.RED),
                    ft.Text(f"• На праздники: {sum(f['holiday_cost'] for f in monthly_forecast):,.0f} ₽", size=12, color=ft.Colors.PURPLE),
                    ft.Text(f"• Итоговый баланс: {monthly_forecast[-1]['balance']:,.0f} ₽", size=12, 
                           color=ft.Colors.GREEN if monthly_forecast[-1]['balance'] > safety_reserve else ft.Colors.RED),
                    ft.Text(f"• Свободных денег: {monthly_forecast[-1]['balance'] - safety_reserve:,.0f} ₽", size=12, 
                           color=ft.Colors.BLUE if monthly_forecast[-1]['balance'] > safety_reserve else ft.Colors.ORANGE),
                    
                    ft.Divider(),
                    
                    # Рекомендации
                    ft.Text("💡 Умные рекомендации:", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text("• Самый дорогой месяц: декабрь (Новый год)", size=12),
                    ft.Text("• Самые дешевые месяцы: летние", size=12),
                    ft.Text("• Планируй подарки заранее", size=12),
                    ft.Text("• Откладывай деньги на праздники", size=12),
                    ft.Text("• Следи за резервом безопасности", size=12),
                    ft.Text("• Используй скидки и акции", size=12)
                ], spacing=8),
                padding=15,
                bgcolor=ft.Colors.LIGHT_BLUE_50,
                border_radius=8,
                border=ft.border.all(1, ft.Colors.BLUE_200)
            )
        ], spacing=5)
    
    def create_holidays_forecast(self):
        holidays = {
            "Новый год": {"cost": 20000, "description": "Подарки семье и друзьям, еда, алкоголь, украшения"},
            "День Святого Валентина": {"cost": 5000, "description": "Подарок девушке, ужин в ресторане, цветы"},
            "8 Марта": {"cost": 3000, "description": "Подарки маме и девушке, цветы"}
        }
        
        # Добавляем дни рождения
        birthdays = self.finance_app.data["birthdays"]
        for birthday in birthdays:
            holidays[f"ДР {birthday['name']}"] = {
                "cost": birthday["cost"], 
                "description": f"Подарок на день рождения {birthday['name']}"
            }
        
        total_holiday_cost = sum(holiday["cost"] for holiday in holidays.values())
        
        return ft.Column([
            ft.Text("🎄 Праздники и подарки:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"• Общая стоимость праздников: {total_holiday_cost:,.0f} ₽", size=14, color=ft.Colors.RED),
            
            ft.Divider(),
            
            *[ft.Column([
                ft.Text(f"🎉 {holiday_name}", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(f"Стоимость: {holiday_data['cost']:,.0f} ₽", size=12, color=ft.Colors.RED),
                ft.Text(f"На что: {holiday_data['description']}", size=10, color=ft.Colors.GREY_600)
            ], spacing=5) for holiday_name, holiday_data in holidays.items()],
            
            ft.Divider(),
            
            ft.Text("💡 Советы по праздникам:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("• Покупай подарки заранее со скидками", size=12),
            ft.Text("• Делай подарки своими руками", size=12),
            ft.Text("• Планируй бюджет на каждый праздник", size=12),
            ft.Text("• Не трать больше чем можешь", size=12),
            ft.Text("• Используй скидки и акции", size=12)
        ], spacing=10)
    
    def create_goals_forecast(self):
        goals = self.finance_app.data["goals"]
        current_money = self.finance_app.data["current_money"]
        salary = self.finance_app.data["salary"]
        monthly_expenses = self.calculate_average_monthly_expenses()
        chatgpt_cost = 3000 if self.finance_app.data["chatgpt_enabled"] else 0
        
        monthly_savings = salary - monthly_expenses - chatgpt_cost
        
        # Вычисляем примеры балансов заранее
        sept_balance = current_money - chatgpt_cost
        oct_balance = sept_balance + salary - monthly_expenses - chatgpt_cost
        nov_balance = oct_balance + salary - monthly_expenses - chatgpt_cost - 25000
        
        return ft.Column([
            ft.Text("📊 Как считаются доходы, расходы и баланс:", size=16, weight=ft.FontWeight.BOLD),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("💰 ДОХОДЫ", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                        ft.Text(f"• Оклад: {salary:,.0f} ₽/месяц", size=12),
                        ft.Text("• Зарплата приходит 2 раза в месяц:", size=12),
                        ft.Text(f"  - {self.finance_app.data['salary_dates'][0]} число: {salary/2:,.0f} ₽", size=11, color=ft.Colors.GREEN),
                        ft.Text(f"  - {self.finance_app.data['salary_dates'][1]} число: {salary/2:,.0f} ₽", size=11, color=ft.Colors.GREEN),
                        ft.Text("• В текущем месяце учитывается реальная дата", size=11, color=ft.Colors.BLUE),
                        ft.Text("• В будущих месяцах - полная зарплата", size=11, color=ft.Colors.BLUE),
                    ], spacing=3),
                    padding=15
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("💸 РАСХОДЫ", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
                        ft.Text(f"• Средние расходы: {monthly_expenses:,.0f} ₽/месяц", size=12),
                        ft.Text("  (фиксированные 10,000 ₽ для планирования)", size=10, color=ft.Colors.GREY_600),
                        ft.Text(f"• ChatGPT Plus: {chatgpt_cost:,.0f} ₽/месяц", size=12, color=ft.Colors.ORANGE),
                        ft.Text("• Квартплата: 25,000 ₽/месяц (платится 10 числа)", size=12, color=ft.Colors.ORANGE),
                        ft.Text("• Праздники и ДР: по календарю", size=12, color=ft.Colors.PURPLE),
                        ft.Text("", size=8),
                        ft.Text("📅 Логика по месяцам:", size=11, weight=ft.FontWeight.BOLD),
                        ft.Text("• Текущий месяц: реальные + прогнозируемые расходы", size=10, color=ft.Colors.BLUE),
                        ft.Text("• Будущие месяцы: средние + фиксированные расходы", size=10, color=ft.Colors.BLUE),
                    ], spacing=3),
                    padding=15
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("💳 БАЛАНС", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                        ft.Text("• Начальный баланс: текущие деньги", size=12),
                        ft.Text("• Каждый месяц: Баланс + Доходы - Расходы", size=12),
                        ft.Text("• Формула: Новый_баланс = Старый_баланс + Зарплата - Все_расходы", size=11, color=ft.Colors.GREY_600),
                        ft.Text("", size=8),
                        ft.Text("🎯 Пример расчета:", size=11, weight=ft.FontWeight.BOLD),
                        ft.Text(f"• Начальный баланс: {current_money:,.0f} ₽", size=10, color=ft.Colors.GREEN),
                        ft.Text("", size=5),
                        ft.Text("📅 Сентябрь 2025 (текущий месяц):", size=10, weight=ft.FontWeight.BOLD),
                        ft.Text(f"  Доходы: 0 ₽ (конец месяца)", size=9, color=ft.Colors.GREEN),
                        ft.Text(f"  Расходы: {chatgpt_cost:,.0f} ₽ (ChatGPT)", size=9, color=ft.Colors.RED),
                        ft.Text(f"  Баланс: {current_money:,.0f} - {chatgpt_cost:,.0f} = {sept_balance:,.0f} ₽", size=9),
                        ft.Text("", size=5),
                        ft.Text("📅 Октябрь 2025:", size=10, weight=ft.FontWeight.BOLD),
                        ft.Text(f"  Доходы: {salary:,.0f} ₽ (зарплата)", size=9, color=ft.Colors.GREEN),
                        ft.Text(f"  Расходы: {monthly_expenses:,.0f} + {chatgpt_cost:,.0f} = {monthly_expenses + chatgpt_cost:,.0f} ₽", size=9, color=ft.Colors.RED),
                        ft.Text(f"  Баланс: {sept_balance:,.0f} + {salary:,.0f} - {monthly_expenses + chatgpt_cost:,.0f} = {oct_balance:,.0f} ₽", size=9),
                        ft.Text("", size=5),
                        ft.Text("📅 Ноябрь 2025:", size=10, weight=ft.FontWeight.BOLD),
                        ft.Text(f"  Доходы: {salary:,.0f} ₽ (зарплата)", size=9, color=ft.Colors.GREEN),
                        ft.Text(f"  Расходы: {monthly_expenses:,.0f} + {chatgpt_cost:,.0f} + 25,000 = {monthly_expenses + chatgpt_cost + 25000:,.0f} ₽", size=9, color=ft.Colors.RED),
                        ft.Text(f"  Баланс: {oct_balance:,.0f} + {salary:,.0f} - {monthly_expenses + chatgpt_cost + 25000:,.0f} = {nov_balance:,.0f} ₽", size=9),
                    ], spacing=3),
                    padding=15
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("🔄 ДИНАМИЧЕСКОЕ ОБНОВЛЕНИЕ", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE),
                        ft.Text("• Добавляете транзакцию → текущие расходы пересчитываются", size=11, color=ft.Colors.BLUE),
                        ft.Text("• Меняете оклад → все доходы пересчитываются", size=11, color=ft.Colors.BLUE),
                        ft.Text("• Меняете квартплату → все расходы пересчитываются", size=11, color=ft.Colors.BLUE),
                        ft.Text("• Добавляете ДР → праздники пересчитываются", size=11, color=ft.Colors.BLUE),
                        ft.Text("• Все изменения мгновенно отражаются в прогнозе", size=11, color=ft.Colors.GREEN),
                        ft.Text("", size=5),
                        ft.Text("📊 Логика средних расходов:", size=11, weight=ft.FontWeight.BOLD),
                        ft.Text("• Фиксированные расходы: 10,000 ₽/месяц", size=10, color=ft.Colors.ORANGE),
                        ft.Text("• Стабильная основа для планирования", size=10, color=ft.Colors.GREEN),
                        ft.Text("• Не зависит от ваших транзакций", size=10, color=ft.Colors.BLUE),
                    ], spacing=3),
                    padding=15
                )
            )
        ], spacing=10)
    
    def create_daily_budget_analysis(self):
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        salary = self.finance_app.data["salary"]
        monthly_expenses = self.calculate_average_monthly_expenses()
        rent = self.finance_app.data["rent"]
        goal_investments = sum(self.finance_app.data["goal_investments"].values())
        
        # Расчеты бюджета
        available_money = current_money - safety_reserve - goal_investments
        monthly_income = salary
        monthly_savings = monthly_income - monthly_expenses - rent
        
        # Бюджеты на разные периоды
        daily_budget = available_money / 30
        weekly_budget = available_money / 4.3
        monthly_budget = available_money
        
        # Рекомендуемые бюджеты (правило 50/30/20)
        needs_budget = monthly_income * 0.5  # 50% на нужды
        wants_budget = monthly_income * 0.3  # 30% на желания
        savings_budget = monthly_income * 0.2  # 20% на сбережения
        
        # Анализ текущего распределения
        current_needs = monthly_expenses + rent
        current_wants = monthly_income - current_needs - (monthly_income - monthly_expenses - rent)
        current_savings = monthly_income - monthly_expenses - rent
        
        return ft.Column([
            ft.Text("📊 Ваш текущий бюджет:", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    ft.Text("💰 В день", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{daily_budget:,.0f} ₽", size=18, color=ft.Colors.GREEN),
                    ft.Text("доступно", size=12, color=ft.Colors.GREY_600)
                ], expand=True),
                ft.Column([
                    ft.Text("📅 В неделю", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{weekly_budget:,.0f} ₽", size=18, color=ft.Colors.BLUE),
                    ft.Text("доступно", size=12, color=ft.Colors.GREY_600)
                ], expand=True),
                ft.Column([
                    ft.Text("📆 В месяц", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{monthly_budget:,.0f} ₽", size=18, color=ft.Colors.ORANGE),
                    ft.Text("доступно", size=12, color=ft.Colors.GREY_600)
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            ft.Text("🎯 Рекомендуемое распределение (правило 50/30/20):", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    ft.Text("🏠 Нужды (50%)", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{needs_budget:,.0f} ₽", size=16, color=ft.Colors.RED),
                    ft.Text(f"Текущие: {current_needs:,.0f} ₽", size=12, 
                           color=ft.Colors.GREEN if current_needs <= needs_budget else ft.Colors.RED)
                ], expand=True),
                ft.Column([
                    ft.Text("🎮 Желания (30%)", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{wants_budget:,.0f} ₽", size=16, color=ft.Colors.PURPLE),
                    ft.Text(f"Текущие: {current_wants:,.0f} ₽", size=12, 
                           color=ft.Colors.GREEN if current_wants <= wants_budget else ft.Colors.RED)
                ], expand=True),
                ft.Column([
                    ft.Text("💎 Сбережения (20%)", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{savings_budget:,.0f} ₽", size=16, color=ft.Colors.BLUE),
                    ft.Text(f"Текущие: {current_savings:,.0f} ₽", size=12, 
                           color=ft.Colors.GREEN if current_savings >= savings_budget else ft.Colors.RED)
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            ft.Text("💡 Рекомендации по тратам:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"• На еду в день: {daily_budget * 0.3:,.0f} ₽", size=12),
            ft.Text(f"• На развлечения в день: {daily_budget * 0.2:,.0f} ₽", size=12),
            ft.Text(f"• На транспорт в день: {daily_budget * 0.1:,.0f} ₽", size=12),
            ft.Text(f"• На непредвиденные расходы: {daily_budget * 0.1:,.0f} ₽", size=12),
            ft.Text(f"• Остаток на накопления: {daily_budget * 0.3:,.0f} ₽", size=12, color=ft.Colors.BLUE)
        ], spacing=10)
    
    def create_wants_analysis(self):
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        salary = self.finance_app.data["salary"]
        monthly_expenses = self.calculate_average_monthly_expenses()
        
        # Бюджет на желания
        wants_budget = salary * 0.3  # 30% от дохода
        available_for_wants = current_money - safety_reserve
        
        # Анализ игровых трат
        game_transactions = [t for t in self.finance_app.data["transactions"] 
                           if t.get("category") == "games"]
        monthly_game_spending = sum(t["amount"] for t in game_transactions 
                                  if t["type"] == "expense" and t["date"].startswith(datetime.now().strftime("%Y-%m")))
        
        # Рекомендации по играм
        recommended_game_budget = wants_budget * 0.2  # 20% от бюджета желаний на игры
        
        return ft.Column([
            ft.Text("🎮 Анализ игровых трат:", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    ft.Text("💸 Потрачено на игры", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"В этом месяце: {monthly_game_spending:,.0f} ₽", size=16, color=ft.Colors.RED),
                    ft.Text(f"Рекомендуется: {recommended_game_budget:,.0f} ₽", size=14, color=ft.Colors.GREEN)
                ], expand=True),
                ft.Column([
                    ft.Text("📊 Статус", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text("✅ В норме" if monthly_game_spending <= recommended_game_budget else "⚠️ Превышение", 
                           size=16, color=ft.Colors.GREEN if monthly_game_spending <= recommended_game_budget else ft.Colors.RED),
                    ft.Text(f"Остаток: {recommended_game_budget - monthly_game_spending:,.0f} ₽", size=14)
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            ft.Text("🎯 Рекомендации по играм:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("• Покупайте игры со скидками (Steam Sale, PlayStation Store)", size=12),
            ft.Text("• Установите лимит на донаты: 2,000-3,000 ₽/мес", size=12),
            ft.Text("• Рассмотрите Game Pass вместо покупки отдельных игр", size=12),
            ft.Text("• Продавайте старые игры для покупки новых", size=12),
            
            ft.Divider(),
            
            ft.Text("💡 Умные советы по экономии на играх:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("• Ждите скидок - экономия до 70%", size=12),
            ft.Text("• Используйте кэшбэк от банков (до 10%)", size=12),
            ft.Text("• Покупайте игры в регионах с низкими ценами", size=12),
            ft.Text("• Рассмотрите подписки вместо покупок", size=12),
            
            ft.Divider(),
            
            ft.Text("🎮 Бюджет на развлечения:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"• Игры: {recommended_game_budget:,.0f} ₽/мес", size=12),
            ft.Text(f"• Кино/сериалы: {wants_budget * 0.15:,.0f} ₽/мес", size=12),
            ft.Text(f"• Кафе/рестораны: {wants_budget * 0.25:,.0f} ₽/мес", size=12),
            ft.Text(f"• Хобби: {wants_budget * 0.2:,.0f} ₽/мес", size=12),
            ft.Text(f"• Прочее: {wants_budget * 0.2:,.0f} ₽/мес", size=12)
        ], spacing=10)
    
    def create_food_budget_analysis(self):
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        salary = self.finance_app.data["salary"]
        
        # Анализ трат на еду
        food_transactions = [t for t in self.finance_app.data["transactions"] 
                           if t.get("category") in ["food", "restaurants"]]
        monthly_food_spending = sum(t["amount"] for t in food_transactions 
                                  if t["type"] == "expense" and t["date"].startswith(datetime.now().strftime("%Y-%m")))
        
        # Рекомендации по еде
        recommended_food_budget = salary * 0.15  # 15% от дохода на еду
        daily_food_budget = recommended_food_budget / 30
        
        # Разбивка по типам еды
        restaurant_budget = recommended_food_budget * 0.3  # 30% на рестораны
        groceries_budget = recommended_food_budget * 0.7   # 70% на продукты
        
        return ft.Column([
            ft.Text("🍽️ Анализ трат на еду:", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    ft.Text("💸 Потрачено на еду", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"В этом месяце: {monthly_food_spending:,.0f} ₽", size=16, color=ft.Colors.RED),
                    ft.Text(f"Рекомендуется: {recommended_food_budget:,.0f} ₽", size=14, color=ft.Colors.GREEN)
                ], expand=True),
                ft.Column([
                    ft.Text("📊 Статус", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text("✅ В норме" if monthly_food_spending <= recommended_food_budget else "⚠️ Превышение", 
                           size=16, color=ft.Colors.GREEN if monthly_food_spending <= recommended_food_budget else ft.Colors.RED),
                    ft.Text(f"Остаток: {recommended_food_budget - monthly_food_spending:,.0f} ₽", size=14)
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            ft.Text("💰 Рекомендуемый бюджет на еду:", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    ft.Text("🛒 Продукты (70%)", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{groceries_budget:,.0f} ₽/мес", size=16, color=ft.Colors.BLUE),
                    ft.Text(f"{groceries_budget/30:,.0f} ₽/день", size=12)
                ], expand=True),
                ft.Column([
                    ft.Text("🍕 Рестораны (30%)", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{restaurant_budget:,.0f} ₽/мес", size=16, color=ft.Colors.ORANGE),
                    ft.Text(f"{restaurant_budget/30:,.0f} ₽/день", size=12)
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            ft.Text("💡 Советы по экономии на еде:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("• Планируйте меню на неделю заранее", size=12),
            ft.Text("• Покупайте продукты по акциям", size=12),
            ft.Text("• Готовьте дома вместо заказов", size=12),
            ft.Text("• Используйте купоны и скидки", size=12),
            ft.Text("• Покупайте сезонные продукты", size=12),
            
            ft.Divider(),
            
            ft.Text("🍽️ Бюджет на рестораны:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"• В день: {restaurant_budget/30:,.0f} ₽", size=12),
            ft.Text(f"• В неделю: {restaurant_budget/4.3:,.0f} ₽", size=12),
            ft.Text(f"• Обеды в ресторанах: {restaurant_budget * 0.6:,.0f} ₽/мес", size=12),
            ft.Text(f"• Доставка еды: {restaurant_budget * 0.4:,.0f} ₽/мес", size=12),
            
            ft.Divider(),
            
            ft.Text("🎯 Рекомендации по ресторанам:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("• Выбирайте рестораны с бизнес-ланчами", size=12),
            ft.Text("• Используйте программы лояльности", size=12),
            ft.Text("• Заказывайте на двоих для экономии", size=12),
            ft.Text("• Избегайте алкоголя в ресторанах", size=12)
        ], spacing=10)
    
    def create_subscriptions_analysis(self):
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        salary = self.finance_app.data["salary"]
        
        # Анализ подписок
        subscriptions = [
            {"name": "ChatGPT Plus", "price": 3000, "period": "месяц", "enabled": self.finance_app.data["chatgpt_enabled"]},
            {"name": "Netflix", "price": 500, "period": "месяц", "enabled": False},
            {"name": "Spotify", "price": 300, "period": "месяц", "enabled": False},
            {"name": "YouTube Premium", "price": 200, "period": "месяц", "enabled": False}
        ]
        
        # Текущие подписки (из транзакций)
        subscription_transactions = [t for t in self.finance_app.data["transactions"] 
                                   if any(word in t["description"].lower() for word in ["подписка", "subscription", "netflix", "spotify", "youtube", "microsoft", "adobe", "playstation", "xbox"])]
        monthly_subscription_spending = sum(t["amount"] for t in subscription_transactions 
                                          if t["type"] == "expense" and t["date"].startswith(datetime.now().strftime("%Y-%m")))
        
        # Добавляем ChatGPT если включен
        if self.finance_app.data["chatgpt_enabled"]:
            monthly_subscription_spending += 3000
        
        # Рекомендации
        recommended_subscription_budget = salary * 0.05  # 5% от дохода на подписки
        
        return ft.Column([
            ft.Text("💳 Анализ подписок:", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    ft.Text("💸 Текущие подписки", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"В этом месяце: {monthly_subscription_spending:,.0f} ₽", size=16, color=ft.Colors.RED),
                    ft.Text(f"Рекомендуется: {recommended_subscription_budget:,.0f} ₽", size=14, color=ft.Colors.GREEN)
                ], expand=True),
                ft.Column([
                    ft.Text("📊 Статус", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text("✅ В норме" if monthly_subscription_spending <= recommended_subscription_budget else "⚠️ Превышение", 
                           size=16, color=ft.Colors.GREEN if monthly_subscription_spending <= recommended_subscription_budget else ft.Colors.RED),
                    ft.Text(f"Остаток: {recommended_subscription_budget - monthly_subscription_spending:,.0f} ₽", size=14)
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            ft.Text("📋 Популярные подписки и их стоимость:", size=16, weight=ft.FontWeight.BOLD),
            ft.Column([
                ft.Row([
                    ft.Text(f"• {sub['name']}: {sub['price']:,.0f} ₽/{sub['period']}", size=12),
                    ft.Text("✅ Включено" if sub['enabled'] else "❌ Выключено", 
                           size=10, color=ft.Colors.GREEN if sub['enabled'] else ft.Colors.GREY)
                ]) for sub in subscriptions
            ], spacing=5),
            
            ft.Divider(),
            
            ft.Text("💡 Советы по подпискам:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("• Отменяйте неиспользуемые подписки", size=12),
            ft.Text("• Покупайте годовые подписки со скидкой", size=12),
            ft.Text("• Используйте семейные планы", size=12),
            ft.Text("• Рассмотрите альтернативы (бесплатные версии)", size=12),
            ft.Text("• Отслеживайте автопродления", size=12),
            
            ft.Divider(),
            
            ft.Text("🎯 Рекомендации по ChatGPT Plus:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"• Стоимость: 3,000 ₽/мес", size=12),
            ft.Text(f"• Доля от дохода: {(3000/salary*100):.1f}%" if salary > 0 else "• Доля от дохода: 0%", size=12),
            ft.Text("• Рекомендуется, если доход > 60,000 ₽/мес", size=12),
            ft.Text("• Рассмотрите альтернативы: Claude, Gemini", size=12),
            ft.Text("• Используйте промокоды и скидки", size=12)
        ], spacing=10)
    
    def create_calculators_page(self):
        return ft.Column([
            ft.Text("🧮 Финансовые калькуляторы", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("💰 Калькулятор покупок", size=18, weight=ft.FontWeight.BOLD),
                        self.create_purchase_calculator()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("🏠 Калькулятор недвижимости", size=18, weight=ft.FontWeight.BOLD),
                        self.create_real_estate_calculator()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("🚗 Калькулятор автомобиля", size=18, weight=ft.FontWeight.BOLD),
                        self.create_car_calculator()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("✈️ Калькулятор отпуска", size=18, weight=ft.FontWeight.BOLD),
                        self.create_vacation_calculator()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("💳 Калькулятор кредитов", size=18, weight=ft.FontWeight.BOLD),
                        self.create_loan_calculator()
                    ], spacing=10),
                    padding=20
                )
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
    
    def create_purchase_calculator(self):
        self.purchase_item = ft.TextField(label="Что покупаете?", width=200)
        self.purchase_price = ft.TextField(label="Цена (₽)", keyboard_type=ft.KeyboardType.NUMBER, width=150)
        self.purchase_result = ft.Text("Введите данные для расчета", size=14, color=ft.Colors.GREY_600)
        
        return ft.Column([
            ft.Row([
                self.purchase_item,
                self.purchase_price,
                ft.ElevatedButton("Рассчитать", on_click=self.calculate_purchase)
            ], spacing=10),
            ft.Container(content=self.purchase_result, padding=10)
        ], spacing=10)
    
    def calculate_purchase(self, e):
        try:
            item = self.purchase_item.value
            price = float(self.purchase_price.value) if self.purchase_price.value else 0
            
            if not item or price <= 0:
                self.purchase_result = ft.Text("Введите корректные данные", size=14, color=ft.Colors.RED)
                self.page.update()
                return
            
            current_money = self.finance_app.data["current_money"]
            safety_reserve = self.finance_app.data["safety_reserve"]
            salary = self.finance_app.data["salary"]
            monthly_expenses = self.calculate_average_monthly_expenses()
            
            # Расчеты
            available_money = current_money - safety_reserve
            months_to_save = (price - available_money) / max(salary - monthly_expenses, 1) if price > available_money else 0
            daily_budget_impact = price / 30 if months_to_save <= 1 else 0
            
            # Рекомендации
            if price <= available_money:
                recommendation = "✅ Можете купить сейчас"
                color = ft.Colors.GREEN
            elif months_to_save <= 3:
                recommendation = f"⏰ Нужно копить {months_to_save:.1f} месяцев"
                color = ft.Colors.ORANGE
            else:
                recommendation = f"❌ Слишком дорого - {months_to_save:.1f} месяцев"
                color = ft.Colors.RED
            
            self.purchase_result = ft.Column([
                ft.Text(f"📱 {item}", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(f"💰 Цена: {price:,.0f} ₽", size=14),
                ft.Text(f"💳 Доступно: {available_money:,.0f} ₽", size=14),
                ft.Text(f"⏰ Время накопления: {months_to_save:.1f} мес", size=14),
                ft.Text(f"📅 Ежедневно нужно: {daily_budget_impact:,.0f} ₽", size=14),
                ft.Text(recommendation, size=14, color=color, weight=ft.FontWeight.BOLD)
            ], spacing=5)
            
            self.page.update()
        except ValueError:
            self.purchase_result = ft.Text("Ошибка в данных", size=14, color=ft.Colors.RED)
            self.page.update()
    
    def create_real_estate_calculator(self):
        self.property_price = ft.TextField(label="Стоимость недвижимости (₽)", keyboard_type=ft.KeyboardType.NUMBER, width=200)
        self.down_payment = ft.TextField(label="Первый взнос (₽)", keyboard_type=ft.KeyboardType.NUMBER, width=150)
        self.interest_rate = ft.TextField(label="Процентная ставка (%)", keyboard_type=ft.KeyboardType.NUMBER, width=150)
        self.property_result = ft.Text("Введите данные для расчета", size=14, color=ft.Colors.GREY_600)
        
        return ft.Column([
            ft.Row([
                self.property_price,
                self.down_payment,
                self.interest_rate,
                ft.ElevatedButton("Рассчитать", on_click=self.calculate_property)
            ], spacing=10),
            ft.Container(content=self.property_result, padding=10)
        ], spacing=10)
    
    def calculate_property(self, e):
        try:
            price = float(self.property_price.value) if self.property_price.value else 0
            down_payment = float(self.down_payment.value) if self.down_payment.value else 0
            interest_rate = float(self.interest_rate.value) if self.interest_rate.value else 0
            
            if price <= 0 or down_payment < 0 or interest_rate < 0:
                self.property_result = ft.Text("Введите корректные данные", size=14, color=ft.Colors.RED)
                self.page.update()
                return
            
            # Расчеты
            loan_amount = price - down_payment
            monthly_rate = interest_rate / 100 / 12
            months = 20 * 12  # 20 лет
            
            if monthly_rate > 0:
                monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
            else:
                monthly_payment = loan_amount / months
            
            total_payment = monthly_payment * months
            total_interest = total_payment - loan_amount
            
            # Анализ доступности
            current_money = self.finance_app.data["current_money"]
            salary = self.finance_app.data["salary"]
            monthly_expenses = self.calculate_average_monthly_expenses()
            
            available_for_mortgage = salary - monthly_expenses
            affordability = "✅ Доступно" if monthly_payment <= available_for_mortgage * 0.4 else "⚠️ Дорого" if monthly_payment <= available_for_mortgage * 0.6 else "❌ Недоступно"
            
            self.property_result = ft.Column([
                ft.Text("🏠 Расчет ипотеки", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(f"💰 Стоимость: {price:,.0f} ₽", size=14),
                ft.Text(f"💳 Первый взнос: {down_payment:,.0f} ₽", size=14),
                ft.Text(f"📊 Сумма кредита: {loan_amount:,.0f} ₽", size=14),
                ft.Text(f"💸 Ежемесячный платеж: {monthly_payment:,.0f} ₽", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(f"📈 Общая переплата: {total_interest:,.0f} ₽", size=14),
                ft.Text(f"🎯 Доступность: {affordability}", size=14, 
                       color=ft.Colors.GREEN if "Доступно" in affordability else ft.Colors.ORANGE if "Дорого" in affordability else ft.Colors.RED)
            ], spacing=5)
            
            self.page.update()
        except ValueError:
            self.property_result = ft.Text("Ошибка в данных", size=14, color=ft.Colors.RED)
            self.page.update()
    
    def create_car_calculator(self):
        self.car_price = ft.TextField(label="Стоимость авто (₽)", keyboard_type=ft.KeyboardType.NUMBER, width=200)
        self.car_down_payment = ft.TextField(label="Первый взнос (₽)", keyboard_type=ft.KeyboardType.NUMBER, width=150)
        self.car_loan_term = ft.TextField(label="Срок кредита (мес)", keyboard_type=ft.KeyboardType.NUMBER, width=150)
        self.car_result = ft.Text("Введите данные для расчета", size=14, color=ft.Colors.GREY_600)
        
        return ft.Column([
            ft.Row([
                self.car_price,
                self.car_down_payment,
                self.car_loan_term,
                ft.ElevatedButton("Рассчитать", on_click=self.calculate_car)
            ], spacing=10),
            ft.Container(content=self.car_result, padding=10)
        ], spacing=10)
    
    def calculate_car(self, e):
        try:
            price = float(self.car_price.value) if self.car_price.value else 0
            down_payment = float(self.car_down_payment.value) if self.car_down_payment.value else 0
            term_months = int(self.car_loan_term.value) if self.car_loan_term.value else 0
            
            if price <= 0 or down_payment < 0 or term_months <= 0:
                self.car_result = ft.Text("Введите корректные данные", size=14, color=ft.Colors.RED)
                self.page.update()
                return
            
            # Расчеты
            loan_amount = price - down_payment
            interest_rate = 0.15  # 15% годовых для авто
            monthly_rate = interest_rate / 12
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**term_months) / ((1 + monthly_rate)**term_months - 1)
            
            total_payment = monthly_payment * term_months
            total_interest = total_payment - loan_amount
            
            # Дополнительные расходы
            insurance_monthly = price * 0.01 / 12  # 1% в год
            maintenance_monthly = price * 0.02 / 12  # 2% в год
            fuel_monthly = 8000  # Примерно
            total_monthly_cost = monthly_payment + insurance_monthly + maintenance_monthly + fuel_monthly
            
            # Анализ доступности
            salary = self.finance_app.data["salary"]
            monthly_expenses = self.calculate_average_monthly_expenses()
            available_income = salary - monthly_expenses
            
            affordability = "✅ Доступно" if total_monthly_cost <= available_income * 0.3 else "⚠️ Дорого" if total_monthly_cost <= available_income * 0.5 else "❌ Недоступно"
            
            self.car_result = ft.Column([
                ft.Text("🚗 Расчет автомобиля", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(f"💰 Стоимость: {price:,.0f} ₽", size=14),
                ft.Text(f"💳 Первый взнос: {down_payment:,.0f} ₽", size=14),
                ft.Text(f"📊 Кредит: {loan_amount:,.0f} ₽", size=14),
                ft.Text(f"💸 Платеж по кредиту: {monthly_payment:,.0f} ₽", size=14),
                ft.Text(f"🛡️ Страховка: {insurance_monthly:,.0f} ₽/мес", size=14),
                ft.Text(f"🔧 Обслуживание: {maintenance_monthly:,.0f} ₽/мес", size=14),
                ft.Text(f"⛽ Топливо: {fuel_monthly:,.0f} ₽/мес", size=14),
                ft.Text(f"📈 Общие расходы: {total_monthly_cost:,.0f} ₽/мес", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(f"🎯 Доступность: {affordability}", size=14, 
                       color=ft.Colors.GREEN if "Доступно" in affordability else ft.Colors.ORANGE if "Дорого" in affordability else ft.Colors.RED)
            ], spacing=5)
            
            self.page.update()
        except ValueError:
            self.car_result = ft.Text("Ошибка в данных", size=14, color=ft.Colors.RED)
            self.page.update()
    
    def create_vacation_calculator(self):
        self.vacation_destination = ft.TextField(label="Куда едете?", width=200)
        self.vacation_days = ft.TextField(label="Количество дней", keyboard_type=ft.KeyboardType.NUMBER, width=150)
        self.vacation_people = ft.TextField(label="Количество человек", keyboard_type=ft.KeyboardType.NUMBER, width=150)
        self.vacation_result = ft.Text("Введите данные для расчета", size=14, color=ft.Colors.GREY_600)
        
        return ft.Column([
            ft.Row([
                self.vacation_destination,
                self.vacation_days,
                self.vacation_people,
                ft.ElevatedButton("Рассчитать", on_click=self.calculate_vacation)
            ], spacing=10),
            ft.Container(content=self.vacation_result, padding=10)
        ], spacing=10)
    
    def calculate_vacation(self, e):
        try:
            destination = self.vacation_destination.value
            days = int(self.vacation_days.value) if self.vacation_days.value else 0
            people = int(self.vacation_people.value) if self.vacation_people.value else 0
            
            if not destination or days <= 0 or people <= 0:
                self.vacation_result = ft.Text("Введите корректные данные", size=14, color=ft.Colors.RED)
                self.page.update()
                return
            
            # Базовые расчеты (примерные цены)
            flight_per_person = 15000 if "заграниц" in destination.lower() or "европ" in destination.lower() else 8000
            hotel_per_night = 3000 if "заграниц" in destination.lower() or "европ" in destination.lower() else 2000
            food_per_day = 2000 if "заграниц" in destination.lower() or "европ" in destination.lower() else 1500
            activities_per_day = 1500 if "заграниц" in destination.lower() or "европ" in destination.lower() else 1000
            
            # Расчеты
            total_flight = flight_per_person * people
            total_hotel = hotel_per_night * days * people
            total_food = food_per_day * days * people
            total_activities = activities_per_day * days * people
            total_cost = total_flight + total_hotel + total_food + total_activities
            
            # Анализ доступности
            current_money = self.finance_app.data["current_money"]
            safety_reserve = self.finance_app.data["safety_reserve"]
            available_money = current_money - safety_reserve
            
            months_to_save = (total_cost - available_money) / max(self.finance_app.data["salary"] - self.calculate_average_monthly_expenses(), 1) if total_cost > available_money else 0
            
            affordability = "✅ Доступно" if total_cost <= available_money else f"⏰ Нужно копить {months_to_save:.1f} мес" if months_to_save <= 12 else "❌ Слишком дорого"
            
            self.vacation_result = ft.Column([
                ft.Text(f"✈️ {destination}", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(f"📅 {days} дней, {people} чел.", size=14),
                ft.Text(f"✈️ Авиабилеты: {total_flight:,.0f} ₽", size=14),
                ft.Text(f"🏨 Отель: {total_hotel:,.0f} ₽", size=14),
                ft.Text(f"🍽️ Питание: {total_food:,.0f} ₽", size=14),
                ft.Text(f"🎯 Развлечения: {total_activities:,.0f} ₽", size=14),
                ft.Text(f"💰 Общая стоимость: {total_cost:,.0f} ₽", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(f"💳 Доступно: {available_money:,.0f} ₽", size=14),
                ft.Text(f"🎯 {affordability}", size=14, 
                       color=ft.Colors.GREEN if "Доступно" in affordability else ft.Colors.ORANGE if "копить" in affordability else ft.Colors.RED)
            ], spacing=5)
            
            self.page.update()
        except ValueError:
            self.vacation_result = ft.Text("Ошибка в данных", size=14, color=ft.Colors.RED)
            self.page.update()
    
    def create_loan_calculator(self):
        self.loan_amount = ft.TextField(label="Сумма кредита (₽)", keyboard_type=ft.KeyboardType.NUMBER, width=200)
        self.loan_rate = ft.TextField(label="Процентная ставка (%)", keyboard_type=ft.KeyboardType.NUMBER, width=150)
        self.loan_term = ft.TextField(label="Срок (мес)", keyboard_type=ft.KeyboardType.NUMBER, width=150)
        self.loan_result = ft.Text("Введите данные для расчета", size=14, color=ft.Colors.GREY_600)
        
        return ft.Column([
            ft.Row([
                self.loan_amount,
                self.loan_rate,
                self.loan_term,
                ft.ElevatedButton("Рассчитать", on_click=self.calculate_loan)
            ], spacing=10),
            ft.Container(content=self.loan_result, padding=10)
        ], spacing=10)
    
    def calculate_loan(self, e):
        try:
            amount = float(self.loan_amount.value) if self.loan_amount.value else 0
            rate = float(self.loan_rate.value) if self.loan_rate.value else 0
            term = int(self.loan_term.value) if self.loan_term.value else 0
            
            if amount <= 0 or rate < 0 or term <= 0:
                self.loan_result = ft.Text("Введите корректные данные", size=14, color=ft.Colors.RED)
                self.page.update()
                return
            
            # Расчеты
            monthly_rate = rate / 100 / 12
            monthly_payment = amount * (monthly_rate * (1 + monthly_rate)**term) / ((1 + monthly_rate)**term - 1)
            total_payment = monthly_payment * term
            total_interest = total_payment - amount
            
            # Анализ доступности
            salary = self.finance_app.data["salary"]
            monthly_expenses = self.calculate_average_monthly_expenses()
            available_income = salary - monthly_expenses
            
            debt_ratio = monthly_payment / salary
            affordability = "✅ Доступно" if debt_ratio <= 0.3 else "⚠️ Осторожно" if debt_ratio <= 0.5 else "❌ Опасно"
            
            self.loan_result = ft.Column([
                ft.Text("💳 Расчет кредита", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(f"💰 Сумма: {amount:,.0f} ₽", size=14),
                ft.Text(f"📊 Ставка: {rate:.1f}%", size=14),
                ft.Text(f"⏰ Срок: {term} мес", size=14),
                ft.Text(f"💸 Ежемесячный платеж: {monthly_payment:,.0f} ₽", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(f"📈 Общая переплата: {total_interest:,.0f} ₽", size=14),
                ft.Text(f"📊 Доля от дохода: {debt_ratio*100:.1f}%", size=14),
                ft.Text(f"🎯 {affordability}", size=14, 
                       color=ft.Colors.GREEN if "Доступно" in affordability else ft.Colors.ORANGE if "Осторожно" in affordability else ft.Colors.RED)
            ], spacing=5)
            
            self.page.update()
        except ValueError:
            self.loan_result = ft.Text("Ошибка в данных", size=14, color=ft.Colors.RED)
            self.page.update()
    
    def create_investments_page(self):
        return ft.Column([
            ft.Text("💎 Инвестиции и накопления", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("📊 Портфель инвестиций", size=18, weight=ft.FontWeight.BOLD),
                        self.create_investment_portfolio()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("💰 Калькулятор накоплений", size=18, weight=ft.FontWeight.BOLD),
                        self.create_savings_calculator()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("📈 Инвестиционные стратегии", size=18, weight=ft.FontWeight.BOLD),
                        self.create_investment_strategies()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("🎯 Рекомендации по инвестициям", size=18, weight=ft.FontWeight.BOLD),
                        self.create_investment_recommendations()
                    ], spacing=10),
                    padding=20
                )
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
    
    def create_investment_portfolio(self):
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        goal_investments = self.finance_app.data["goal_investments"]
        salary = self.finance_app.data["salary"]
        
        # Расчеты
        total_invested = sum(goal_investments.values())
        available_for_investment = current_money - safety_reserve - total_invested
        investment_ratio = total_invested / current_money if current_money > 0 else 0
        
        # Рекомендуемое распределение
        recommended_emergency = safety_reserve
        recommended_investments = (current_money - safety_reserve) * 0.7
        recommended_cash = (current_money - safety_reserve) * 0.3
        
        return ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("💎 Общий портфель", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Всего денег: {current_money:,.0f} ₽", size=14),
                    ft.Text(f"В инвестициях: {total_invested:,.0f} ₽", size=14, color=ft.Colors.BLUE),
                    ft.Text(f"В резерве: {safety_reserve:,.0f} ₽", size=14, color=ft.Colors.GREEN),
                    ft.Text(f"Свободно: {available_for_investment:,.0f} ₽", size=14, color=ft.Colors.ORANGE)
                ], expand=True),
                ft.Column([
                    ft.Text("📊 Распределение", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Инвестиции: {investment_ratio*100:.1f}%", size=14),
                    ft.Text(f"Резерв: {(safety_reserve/current_money*100):.1f}%" if current_money > 0 else "Резерв: 0%", size=14),
                    ft.Text(f"Наличные: {((current_money-safety_reserve-total_invested)/current_money*100):.1f}%" if current_money > 0 else "Наличные: 0%", size=14)
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            ft.Text("🎯 Рекомендуемое распределение:", size=14, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Text(f"Резерв: {recommended_emergency:,.0f} ₽", size=12, color=ft.Colors.GREEN),
                ft.Text(f"Инвестиции: {recommended_investments:,.0f} ₽", size=12, color=ft.Colors.BLUE),
                ft.Text(f"Наличные: {recommended_cash:,.0f} ₽", size=12, color=ft.Colors.ORANGE)
            ], spacing=20)
        ], spacing=10)
    
    def create_savings_calculator(self):
        self.savings_goal = ft.TextField(label="Цель накоплений (₽)", keyboard_type=ft.KeyboardType.NUMBER, width=200)
        self.savings_time = ft.TextField(label="Срок (мес)", keyboard_type=ft.KeyboardType.NUMBER, width=150)
        self.savings_rate = ft.TextField(label="Процентная ставка (%)", keyboard_type=ft.KeyboardType.NUMBER, width=150)
        self.savings_result = ft.Text("Введите данные для расчета", size=14, color=ft.Colors.GREY_600)
        
        return ft.Column([
            ft.Row([
                self.savings_goal,
                self.savings_time,
                self.savings_rate,
                ft.ElevatedButton("Рассчитать", on_click=self.calculate_savings)
            ], spacing=10),
            ft.Container(content=self.savings_result, padding=10)
        ], spacing=10)
    
    def calculate_savings(self, e):
        try:
            goal = float(self.savings_goal.value) if self.savings_goal.value else 0
            months = int(self.savings_time.value) if self.savings_time.value else 0
            rate = float(self.savings_rate.value) if self.savings_rate.value else 0
            
            if goal <= 0 or months <= 0 or rate < 0:
                self.savings_result = ft.Text("Введите корректные данные", size=14, color=ft.Colors.RED)
                self.page.update()
                return
            
            # Расчеты
            monthly_rate = rate / 100 / 12
            if monthly_rate > 0:
                monthly_payment = goal * monthly_rate / ((1 + monthly_rate)**months - 1)
            else:
                monthly_payment = goal / months
            
            total_invested = monthly_payment * months
            total_earnings = goal - total_invested
            
            # Анализ доступности
            salary = self.finance_app.data["salary"]
            monthly_expenses = self.calculate_average_monthly_expenses()
            available_income = salary - monthly_expenses
            
            affordability = "✅ Доступно" if monthly_payment <= available_income * 0.3 else "⚠️ Дорого" if monthly_payment <= available_income * 0.5 else "❌ Недоступно"
            
            self.savings_result = ft.Column([
                ft.Text("💰 Расчет накоплений", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(f"🎯 Цель: {goal:,.0f} ₽", size=14),
                ft.Text(f"⏰ Срок: {months} мес", size=14),
                ft.Text(f"📊 Ставка: {rate:.1f}%", size=14),
                ft.Text(f"💸 Ежемесячно: {monthly_payment:,.0f} ₽", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(f"📈 Всего вложено: {total_invested:,.0f} ₽", size=14),
                ft.Text(f"💎 Доход: {total_earnings:,.0f} ₽", size=14, color=ft.Colors.GREEN),
                ft.Text(f"🎯 {affordability}", size=14, 
                       color=ft.Colors.GREEN if "Доступно" in affordability else ft.Colors.ORANGE if "Дорого" in affordability else ft.Colors.RED)
            ], spacing=5)
            
            self.page.update()
        except ValueError:
            self.savings_result = ft.Text("Ошибка в данных", size=14, color=ft.Colors.RED)
            self.page.update()
    
    def create_investment_strategies(self):
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        salary = self.finance_app.data["salary"]
        age = 30  # Предполагаемый возраст
        
        # Рекомендации по возрасту
        if age < 30:
            risk_profile = "Агрессивный"
            stock_ratio = 0.8
            bond_ratio = 0.2
        elif age < 50:
            risk_profile = "Умеренный"
            stock_ratio = 0.6
            bond_ratio = 0.4
        else:
            risk_profile = "Консервативный"
            stock_ratio = 0.4
            bond_ratio = 0.6
        
        available_for_investment = current_money - safety_reserve
        recommended_stocks = available_for_investment * stock_ratio
        recommended_bonds = available_for_investment * bond_ratio
        
        return ft.Column([
            ft.Text(f"👤 Ваш профиль: {risk_profile}", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"Возраст: {age} лет", size=14),
            
            ft.Divider(),
            
            ft.Text("📊 Рекомендуемое распределение:", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    ft.Text("📈 Акции", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{stock_ratio*100:.0f}%", size=16, color=ft.Colors.BLUE),
                    ft.Text(f"{recommended_stocks:,.0f} ₽", size=12)
                ], expand=True),
                ft.Column([
                    ft.Text("🏛️ Облигации", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{bond_ratio*100:.0f}%", size=16, color=ft.Colors.GREEN),
                    ft.Text(f"{recommended_bonds:,.0f} ₽", size=12)
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            ft.Text("💡 Стратегии:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("• ETF на S&P 500 - 40%", size=12),
            ft.Text("• Российские акции - 20%", size=12),
            ft.Text("• ОФЗ - 30%", size=12),
            ft.Text("• Золото - 10%", size=12),
            
            ft.Divider(),
            
            ft.Text("⚠️ Важные правила:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("• Не инвестируйте последние деньги", size=12),
            ft.Text("• Диверсифицируйте портфель", size=12),
            ft.Text("• Инвестируйте регулярно", size=12),
            ft.Text("• Не паникуйте при падениях", size=12)
        ], spacing=10)
    
    def create_investment_recommendations(self):
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        salary = self.finance_app.data["salary"]
        monthly_expenses = self.calculate_average_monthly_expenses()
        
        recommendations = []
        
        # Анализ текущей ситуации
        if current_money < safety_reserve * 2:
            recommendations.append(
                ft.Text("🚨 Сначала накопите резерв в 2-3 раза больше текущего", 
                       size=14, color=ft.Colors.RED, weight=ft.FontWeight.BOLD)
            )
        elif current_money > safety_reserve * 3:
            excess = current_money - safety_reserve * 3
            recommendations.append(
                ft.Text(f"💎 Можете инвестировать {excess:,.0f} ₽", 
                       size=14, color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD)
            )
        
        # Рекомендации по суммам
        monthly_savings = salary - monthly_expenses
        if monthly_savings > 0:
            recommended_monthly_investment = monthly_savings * 0.3
            recommendations.append(
                ft.Text(f"📅 Рекомендуется инвестировать {recommended_monthly_investment:,.0f} ₽/мес", 
                       size=14, color=ft.Colors.BLUE)
            )
        
        # Инструменты
        recommendations.extend([
            ft.Text("🏦 Инструменты для начинающих:", size=14, weight=ft.FontWeight.BOLD),
            ft.Text("• Банковские вклады - 5-7% годовых", size=12),
            ft.Text("• ОФЗ - 6-8% годовых", size=12),
            ft.Text("• ETF - 8-12% годовых", size=12),
            ft.Text("• Акции - 10-15% годовых (риск)", size=12),
            
            ft.Text("📚 Где изучать:", size=14, weight=ft.FontWeight.BOLD),
            ft.Text("• Тинькофф Инвестиции", size=12),
            ft.Text("• Сбер Инвестор", size=12),
            ft.Text("• ВТБ Мои Инвестиции", size=12),
            ft.Text("• YouTube каналы по инвестициям", size=12)
        ])
        
        return ft.Column(recommendations, spacing=5)
    
    def create_loans_page(self):
        return ft.Column([
            ft.Text("💳 Кредиты и долги", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("📊 Анализ кредитной нагрузки", size=18, weight=ft.FontWeight.BOLD),
                        self.create_debt_analysis()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("💡 Стратегии погашения долгов", size=18, weight=ft.FontWeight.BOLD),
                        self.create_debt_strategies()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("🆘 Кризисное планирование", size=18, weight=ft.FontWeight.BOLD),
                        self.create_crisis_planning()
                    ], spacing=10),
                    padding=20
                )
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
    
    def create_debt_analysis(self):
        salary = self.finance_app.data["salary"]
        monthly_expenses = self.calculate_average_monthly_expenses()
        current_money = self.finance_app.data["current_money"]
        
        # Анализ кредитоспособности
        available_income = salary - monthly_expenses
        max_loan_payment = available_income * 0.4  # Максимум 40% от дохода
        recommended_loan_payment = available_income * 0.2  # Рекомендуется 20%
        
        # Оценка кредитоспособности
        if available_income > 50000:
            credit_score = "Отличная"
            score_color = ft.Colors.GREEN
        elif available_income > 30000:
            credit_score = "Хорошая"
            score_color = ft.Colors.ORANGE
        else:
            credit_score = "Ограниченная"
            score_color = ft.Colors.RED
        
        return ft.Column([
            ft.Text(f"🏦 Кредитоспособность: {credit_score}", size=16, weight=ft.FontWeight.BOLD, color=score_color),
            
            ft.Divider(),
            
            ft.Row([
                ft.Column([
                    ft.Text("💰 Доходы", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Зарплата: {salary:,.0f} ₽", size=12),
                    ft.Text(f"Расходы: {monthly_expenses:,.0f} ₽", size=12),
                    ft.Text(f"Свободно: {available_income:,.0f} ₽", size=12, color=ft.Colors.GREEN)
                ], expand=True),
                ft.Column([
                    ft.Text("💳 Кредиты", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Макс. платеж: {max_loan_payment:,.0f} ₽", size=12),
                    ft.Text(f"Рекомендуется: {recommended_loan_payment:,.0f} ₽", size=12),
                    ft.Text(f"Резерв: {current_money:,.0f} ₽", size=12, color=ft.Colors.BLUE)
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            ft.Text("⚠️ Правила безопасного кредитования:", size=14, weight=ft.FontWeight.BOLD),
            ft.Text("• Платеж не должен превышать 40% дохода", size=12),
            ft.Text("• Оставьте 20% дохода на сбережения", size=12),
            ft.Text("• Имейте резерв на 3-6 месяцев", size=12),
            ft.Text("• Сравнивайте предложения банков", size=12)
        ], spacing=10)
    
    def create_debt_strategies(self):
        return ft.Column([
            ft.Text("🎯 Методы погашения долгов:", size=16, weight=ft.FontWeight.BOLD),
            
            ft.Text("1️⃣ Метод снежного кома", size=14, weight=ft.FontWeight.BOLD),
            ft.Text("• Погашайте сначала самые маленькие долги", size=12),
            ft.Text("• Психологически легче", size=12),
            ft.Text("• Подходит для мотивации", size=12),
            
            ft.Text("2️⃣ Метод лавины", size=14, weight=ft.FontWeight.BOLD),
            ft.Text("• Погашайте сначала самые дорогие долги", size=12),
            ft.Text("• Экономически выгоднее", size=12),
            ft.Text("• Быстрее снижает общую переплату", size=12),
            
            ft.Text("3️⃣ Рефинансирование", size=14, weight=ft.FontWeight.BOLD),
            ft.Text("• Объедините несколько кредитов в один", size=12),
            ft.Text("• Снизьте процентную ставку", size=12),
            ft.Text("• Упростите управление долгами", size=12),
            
            ft.Divider(),
            
            ft.Text("💡 Дополнительные советы:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("• Создайте бюджет и следуйте ему", size=12),
            ft.Text("• Найдите дополнительные источники дохода", size=12),
            ft.Text("• Избегайте новых долгов", size=12),
            ft.Text("• Рассмотрите консолидацию долгов", size=12)
        ], spacing=10)
    
    def create_crisis_planning(self):
        current_money = self.finance_app.data["current_money"]
        safety_reserve = self.finance_app.data["safety_reserve"]
        salary = self.finance_app.data["salary"]
        monthly_expenses = self.calculate_average_monthly_expenses()
        
        # Расчет времени выживания
        months_survival = current_money / monthly_expenses if monthly_expenses > 0 else 0
        
        # Рекомендации по кризису
        if months_survival < 3:
            crisis_status = "🚨 КРИТИЧНО"
            crisis_color = ft.Colors.RED
            crisis_advice = "СРОЧНО найдите дополнительные источники дохода"
        elif months_survival < 6:
            crisis_status = "⚠️ ОПАСНО"
            crisis_color = ft.Colors.ORANGE
            crisis_advice = "Нужно увеличить резерв"
        else:
            crisis_status = "✅ БЕЗОПАСНО"
            crisis_color = ft.Colors.GREEN
            crisis_advice = "У вас хороший резерв"
        
        return ft.Column([
            ft.Text(f"🆘 Статус: {crisis_status}", size=16, weight=ft.FontWeight.BOLD, color=crisis_color),
            ft.Text(f"Время выживания: {months_survival:.1f} месяцев", size=14),
            ft.Text(crisis_advice, size=14, color=crisis_color),
            
            ft.Divider(),
            
            ft.Text("📋 План действий в кризисе:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("1. Сократите все необязательные расходы", size=12),
            ft.Text("2. Найдите дополнительные источники дохода", size=12),
            ft.Text("3. Обратитесь за помощью к близким", size=12),
            ft.Text("4. Рассмотрите рефинансирование долгов", size=12),
            ft.Text("5. Обратитесь в службы поддержки", size=12),
            
            ft.Divider(),
            
            ft.Text("🆘 Экстренные контакты:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("• Служба психологической помощи: 8-800-2000-122", size=12),
            ft.Text("• Центр занятости населения", size=12),
            ft.Text("• Социальные службы", size=12),
            ft.Text("• Банк - реструктуризация кредитов", size=12)
        ], spacing=10)
    
    def create_reports_page(self):
        return ft.Column([
            ft.Text("📊 Отчеты и документы", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("📈 Финансовый отчет", size=18, weight=ft.FontWeight.BOLD),
                        self.create_financial_report()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("📋 Налоговый отчет", size=18, weight=ft.FontWeight.BOLD),
                        self.create_tax_report()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("📄 Экспорт данных", size=18, weight=ft.FontWeight.BOLD),
                        self.create_export_section()
                    ], spacing=10),
                    padding=20
                )
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
    
    def create_financial_report(self):
        current_money = self.finance_app.data["current_money"]
        salary = self.finance_app.data["salary"]
        transactions = self.finance_app.data["transactions"]
        monthly_expenses = self.calculate_average_monthly_expenses()
        
        # Статистика за год
        current_year = datetime.now().year
        year_income = sum(t["amount"] for t in transactions 
                         if t["type"] == "income" and str(current_year) in t["date"])
        year_expenses = sum(t["amount"] for t in transactions 
                           if t["type"] == "expense" and str(current_year) in t["date"])
        year_savings = year_income - year_expenses
        
        return ft.Column([
            ft.Text(f"📊 Отчет за {current_year} год", size=16, weight=ft.FontWeight.BOLD),
            
            ft.Row([
                ft.Column([
                    ft.Text("💰 Доходы", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{year_income:,.0f} ₽", size=16, color=ft.Colors.GREEN)
                ], expand=True),
                ft.Column([
                    ft.Text("💸 Расходы", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{year_expenses:,.0f} ₽", size=16, color=ft.Colors.RED)
                ], expand=True),
                ft.Column([
                    ft.Text("💎 Сбережения", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{year_savings:,.0f} ₽", size=16, color=ft.Colors.BLUE)
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            ft.Text("📈 Ключевые показатели:", size=14, weight=ft.FontWeight.BOLD),
            ft.Text(f"• Норма сбережений: {(year_savings/year_income*100):.1f}%" if year_income > 0 else "• Норма сбережений: 0%", size=12),
            ft.Text(f"• Средний доход в месяц: {year_income/12:,.0f} ₽", size=12),
            ft.Text(f"• Средние расходы в месяц: {year_expenses/12:,.0f} ₽", size=12),
            ft.Text(f"• Текущий баланс: {current_money:,.0f} ₽", size=12)
        ], spacing=10)
    
    def create_tax_report(self):
        salary = self.finance_app.data["salary"]
        transactions = self.finance_app.data["transactions"]
        
        # Расчет налогов
        annual_salary = salary * 12
        income_tax = annual_salary * 0.13  # 13% НДФЛ
        social_contributions = annual_salary * 0.3  # 30% страховые взносы
        
        # Доходы от инвестиций (если есть)
        investment_income = sum(t["amount"] for t in transactions 
                               if t["type"] == "income" and "инвест" in t["description"].lower())
        investment_tax = investment_income * 0.13
        
        return ft.Column([
            ft.Text("📋 Налоговый отчет", size=16, weight=ft.FontWeight.BOLD),
            
            ft.Text("💰 Зарплатные налоги:", size=14, weight=ft.FontWeight.BOLD),
            ft.Text(f"• Годовая зарплата: {annual_salary:,.0f} ₽", size=12),
            ft.Text(f"• НДФЛ (13%): {income_tax:,.0f} ₽", size=12),
            ft.Text(f"• Страховые взносы (30%): {social_contributions:,.0f} ₽", size=12),
            ft.Text(f"• Чистая зарплата: {annual_salary - income_tax:,.0f} ₽", size=12),
            
            ft.Divider(),
            
            ft.Text("💎 Инвестиционные доходы:", size=14, weight=ft.FontWeight.BOLD),
            ft.Text(f"• Доходы от инвестиций: {investment_income:,.0f} ₽", size=12),
            ft.Text(f"• Налог с инвестиций: {investment_tax:,.0f} ₽", size=12),
            
            ft.Divider(),
            
            ft.Text("📄 Документы для налоговой:", size=14, weight=ft.FontWeight.BOLD),
            ft.Text("• Справка 2-НДФЛ (от работодателя)", size=12),
            ft.Text("• Декларация 3-НДФЛ (если нужно)", size=12),
            ft.Text("• Справки о доходах от инвестиций", size=12),
            ft.Text("• Документы на налоговые вычеты", size=12)
        ], spacing=10)
    
    def create_export_section(self):
        return ft.Column([
            ft.Text("📤 Экспорт данных", size=16, weight=ft.FontWeight.BOLD),
            
            ft.Row([
                ft.ElevatedButton("📊 Excel отчет", on_click=self.export_to_excel),
                ft.ElevatedButton("📄 PDF отчет", on_click=self.export_to_pdf),
                ft.ElevatedButton("📱 Резервная копия", on_click=self.create_backup)
            ], spacing=10),
            
            ft.Divider(),
            
            ft.Text("💾 Что экспортируется:", size=14, weight=ft.FontWeight.BOLD),
            ft.Text("• Все транзакции", size=12),
            ft.Text("• Финансовые цели", size=12),
            ft.Text("• Настройки приложения", size=12),
            ft.Text("• Аналитика и отчеты", size=12),
            
            ft.Divider(),
            
            ft.Text("🔒 Безопасность:", size=14, weight=ft.FontWeight.BOLD),
            ft.Text("• Данные хранятся локально", size=12),
            ft.Text("• Никто не имеет доступа к вашей информации", size=12),
            ft.Text("• Резервные копии можно восстановить", size=12)
        ], spacing=10)
    
    def export_to_excel(self, e):
        # Заглушка для экспорта в Excel
        self.show_export_dialog("Excel отчет создан!")
    
    def export_to_pdf(self, e):
        # Заглушка для экспорта в PDF
        self.show_export_dialog("PDF отчет создан!")
    
    def create_backup(self, e):
        # Заглушка для создания резервной копии
        self.show_export_dialog("Резервная копия создана!")
    
    def show_export_dialog(self, message):
        dialog = ft.AlertDialog(
            title=ft.Text("Экспорт"),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=self.close_dialog)]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def close_dialog(self, e=None):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
        if self.page.overlay:
            for overlay_item in self.page.overlay:
                if hasattr(overlay_item, 'open') and overlay_item.open:
                    overlay_item.open = False
            self.page.update()
    
    def create_basic_calculator(self):
        def button_click(button_text):
            if button_text == "C":
                self.calculator_expression = ""
                self.calculator_display.value = "0"
            elif button_text == "=":
                try:
                    self.calculator_result = eval(self.calculator_expression)
                    self.calculator_display.value = str(self.calculator_result)
                    self.calculator_expression = str(self.calculator_result)
                except:
                    self.calculator_display.value = "Ошибка"
                    self.calculator_expression = ""
            elif button_text == "⌫":
                if len(self.calculator_expression) > 0:
                    self.calculator_expression = self.calculator_expression[:-1]
                    self.calculator_display.value = self.calculator_expression if self.calculator_expression else "0"
            else:
                if self.calculator_expression == "0" and button_text.isdigit():
                    self.calculator_expression = button_text
                else:
                    self.calculator_expression += button_text
                self.calculator_display.value = self.calculator_expression
            self.page.update()
        
        # Создаем кнопки калькулятора
        buttons = [
            ["C", "⌫", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["0", ".", "=", ""]
        ]
        
        button_grid = []
        for row in buttons:
            row_buttons = []
            for button_text in row:
                if button_text == "":  # Пропускаем пустые кнопки
                    continue
                elif button_text == "=":  # Кнопка = занимает 2 места
                    row_buttons.append(ft.ElevatedButton(
                        button_text,
                        on_click=lambda e, text=button_text: button_click(text),
                        width=150,
                        height=50,
                        bgcolor=ft.Colors.ORANGE,
                        color=ft.Colors.WHITE
                    ))
                elif button_text == "0":  # Кнопка 0 занимает 2 места
                    row_buttons.append(ft.ElevatedButton(
                        button_text,
                        on_click=lambda e, text=button_text: button_click(text),
                        width=150,
                        height=50
                    ))
                else:
                    row_buttons.append(ft.ElevatedButton(
                        button_text,
                        on_click=lambda e, text=button_text: button_click(text),
                        width=70,
                        height=50,
                        bgcolor=ft.Colors.BLUE_100 if button_text in ["+", "-", "×", "÷", "%"] else None
                    ))
            button_grid.append(ft.Row(row_buttons, spacing=5))
        
        return ft.Column([
            self.calculator_display,
            ft.Divider(),
            *button_grid
        ], spacing=10)
    
    def create_financial_calculator(self):
        self.financial_result = ft.Container()
        
        def calculate_percentage(e):
            try:
                value = float(self.calculator_display.value)
                percentage = value / 100
                self.calculator_display.value = str(percentage)
                self.calculator_expression = str(percentage)
                self.page.update()
            except:
                pass
        
        def calculate_tax(e):
            try:
                value = float(self.calculator_display.value)
                # НДФЛ 13%
                tax = value * 0.13
                net_amount = value - tax
                self.financial_result.content = ft.Column([
                    ft.Text("💰 Налоговый расчет:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Сумма: {value:,.0f} ₽", size=14),
                    ft.Text(f"НДФЛ (13%): {tax:,.0f} ₽", size=14, color=ft.Colors.RED),
                    ft.Text(f"К получению: {net_amount:,.0f} ₽", size=14, color=ft.Colors.GREEN)
                ], spacing=5)
                self.page.update()
            except:
                pass
        
        def calculate_tip(e):
            try:
                bill = float(self.calculator_display.value)
                tip_15 = bill * 0.15
                tip_20 = bill * 0.20
                self.financial_result.content = ft.Column([
                    ft.Text("🍽️ Чаевые:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Счет: {bill:,.0f} ₽", size=14),
                    ft.Text(f"15% чаевых: {tip_15:,.0f} ₽", size=14),
                    ft.Text(f"20% чаевых: {tip_20:,.0f} ₽", size=14),
                    ft.Text(f"Итого с 15%: {bill + tip_15:,.0f} ₽", size=14, color=ft.Colors.GREEN),
                    ft.Text(f"Итого с 20%: {bill + tip_20:,.0f} ₽", size=14, color=ft.Colors.GREEN)
                ], spacing=5)
                self.page.update()
            except:
                pass
        
        def calculate_discount(e):
            try:
                original_price = float(self.calculator_display.value)
                discount_10 = original_price * 0.9
                discount_20 = original_price * 0.8
                discount_30 = original_price * 0.7
                self.financial_result.content = ft.Column([
                    ft.Text("🏷️ Скидки:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Оригинальная цена: {original_price:,.0f} ₽", size=14),
                    ft.Text(f"Скидка 10%: {discount_10:,.0f} ₽", size=14, color=ft.Colors.GREEN),
                    ft.Text(f"Скидка 20%: {discount_20:,.0f} ₽", size=14, color=ft.Colors.GREEN),
                    ft.Text(f"Скидка 30%: {discount_30:,.0f} ₽", size=14, color=ft.Colors.GREEN)
                ], spacing=5)
                self.page.update()
            except:
                pass
        
        def calculate_compound_interest(e):
            try:
                principal = float(self.calculator_display.value)
                rate = 0.10  # 10% годовых
                years = 1
                amount = principal * (1 + rate) ** years
                interest = amount - principal
                self.financial_result.content = ft.Column([
                    ft.Text("📈 Сложный процент:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Начальная сумма: {principal:,.0f} ₽", size=14),
                    ft.Text(f"Ставка: 10% годовых", size=14),
                    ft.Text(f"Через 1 год: {amount:,.0f} ₽", size=14, color=ft.Colors.GREEN),
                    ft.Text(f"Доход: {interest:,.0f} ₽", size=14, color=ft.Colors.BLUE)
                ], spacing=5)
                self.page.update()
            except:
                pass
        
        def calculate_currency(e):
            try:
                rubles = float(self.calculator_display.value)
                usd = rubles / 95  # Примерный курс
                eur = rubles / 105
                self.financial_result.content = ft.Column([
                    ft.Text("💱 Валютный калькулятор:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Рубли: {rubles:,.0f} ₽", size=14),
                    ft.Text(f"Доллары: ${usd:.2f}", size=14, color=ft.Colors.GREEN),
                    ft.Text(f"Евро: €{eur:.2f}", size=14, color=ft.Colors.BLUE)
                ], spacing=5)
                self.page.update()
            except:
                pass
        
        return ft.Column([
            ft.Text("Финансовые функции (введите число в калькуляторе выше):", size=14, color=ft.Colors.GREY_600),
            ft.Row([
                ft.ElevatedButton("НДФЛ 13%", on_click=calculate_tax, width=100, height=40),
                ft.ElevatedButton("Чаевые", on_click=calculate_tip, width=100, height=40),
                ft.ElevatedButton("Скидки", on_click=calculate_discount, width=100, height=40)
            ], spacing=10),
            ft.Row([
                ft.ElevatedButton("Сложный %", on_click=calculate_compound_interest, width=100, height=40),
                ft.ElevatedButton("Валюты", on_click=calculate_currency, width=100, height=40),
                ft.ElevatedButton("Процент", on_click=calculate_percentage, width=100, height=40)
            ], spacing=10),
            self.financial_result
        ], spacing=10)
    
    def create_note_input(self):
        self.note_title = ft.TextField(label="Заголовок заметки", width=300)
        self.note_content = ft.TextField(label="Содержание", multiline=True, min_lines=3, max_lines=6, width=400)
        self.note_category = ft.Dropdown(
            label="Категория",
            width=150,
            options=[
                ft.dropdown.Option("💰 Покупки", "purchases"),
                ft.dropdown.Option("🎯 Цели", "goals"),
                ft.dropdown.Option("📊 Анализ", "analysis"),
                ft.dropdown.Option("💡 Идеи", "ideas"),
                ft.dropdown.Option("📝 Общее", "general")
            ]
        )
        
        def add_note(e):
            title = self.note_title.value
            content = self.note_content.value
            category = self.note_category.value
            
            if title and content:
                note = {
                    "title": title,
                    "content": content,
                    "category": category,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "id": len(self.finance_app.data["notes"]) + 1
                }
                self.finance_app.data["notes"].append(note)
                self.finance_app.save_data()
                
                self.note_title.value = ""
                self.note_content.value = ""
                self.note_category.value = None
                self.page.update()
        
        return ft.Column([
            ft.Row([
                self.note_title,
                self.note_category
            ], spacing=10),
            self.note_content,
            ft.ElevatedButton("Добавить заметку", on_click=add_note)
        ], spacing=10)
    
    def create_notes_list(self):
        notes = self.finance_app.data["notes"]
        
        if not notes:
            return ft.Text("Нет заметок")
        
        note_widgets = []
        for note in reversed(notes):  # Показываем новые заметки сверху
            category_icons = {
                "purchases": "💰",
                "goals": "🎯", 
                "analysis": "📊",
                "ideas": "💡",
                "general": "📝"
            }
            
            note_widgets.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"{category_icons.get(note['category'], '📝')} {note['title']}", 
                                       size=16, weight=ft.FontWeight.BOLD),
                                ft.Text(note['date'], size=12, color=ft.Colors.GREY_600),
                                ft.IconButton(ft.Icons.DELETE, on_click=lambda e, note_id=note['id']: self.delete_note(note_id))
                            ]),
                            ft.Text(note['content'], size=14),
                        ], spacing=5),
                        padding=15
                    )
                )
            )
        
        return ft.Column(note_widgets, spacing=10)
    
    def create_note_templates(self):
        templates = [
            {
                "title": "Планирую купить",
                "content": "Что: \nЦена: \nКогда: \nЗачем: ",
                "category": "purchases"
            },
            {
                "title": "Финансовая цель",
                "content": "Цель: \nСумма: \nСрок: \nПлан накопления: ",
                "category": "goals"
            },
            {
                "title": "Анализ трат",
                "content": "Месяц: \nОсновные траты: \nВыводы: \nРекомендации: ",
                "category": "analysis"
            },
            {
                "title": "Идея для экономии",
                "content": "Идея: \nЭкономия в месяц: \nСложность: \nПлан внедрения: ",
                "category": "ideas"
            }
        ]
        
        def use_template(template):
            self.note_title.value = template["title"]
            self.note_content.value = template["content"]
            self.note_category.value = template["category"]
            self.page.update()
        
        template_widgets = []
        for template in templates:
            template_widgets.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(template["title"], size=14, weight=ft.FontWeight.BOLD),
                            ft.Text(template["content"][:100] + "...", size=12, color=ft.Colors.GREY_600),
                            ft.ElevatedButton("Использовать", on_click=lambda e, t=template: use_template(t), width=120)
                        ], spacing=5),
                        padding=10
                    )
                )
            )
        
        return ft.Column(template_widgets, spacing=10)
    
    def delete_note(self, note_id):
        self.finance_app.data["notes"] = [note for note in self.finance_app.data["notes"] if note["id"] != note_id]
        self.finance_app.save_data()
        self.refresh_all_pages()

def main(page: ft.Page):
    app = MainApp(page)

if __name__ == "__main__":
    ft.app(target=main)
