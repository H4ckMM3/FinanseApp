import flet as ft
import datetime
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
                "rent_paid_until": None
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
                ft.NavigationBarDestination(icon=ft.Icons.TRENDING_UP, label="Цели"),
                ft.NavigationBarDestination(icon=ft.Icons.ANALYTICS, label="Аналитика"),
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
        
        self.page.update()
    
    def create_home_page(self):
        current_date = datetime.datetime.now()
        salary = self.finance_app.data["salary"]
        current_money = self.finance_app.data["current_money"]
        
        next_salary_date = self.get_next_salary_date()
        days_until_salary = (next_salary_date - current_date).days
        
        daily_budget = self.calculate_daily_budget()
        
        return ft.Column([
            ft.Text("Добро пожаловать в ваше финансовое приложение!", 
                   size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Текущее состояние", size=18, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Column([
                                ft.Text("Текущие деньги:", size=14),
                                ft.Text(f"{current_money:,.0f} ₽", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN)
                            ], expand=True),
                            ft.Column([
                                ft.Text("Оклад:", size=14),
                                ft.Text(f"{salary:,.0f} ₽", size=20, weight=ft.FontWeight.BOLD)
                            ], expand=True)
                        ])
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("До следующей зарплаты", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{days_until_salary} дней", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                        ft.Text(f"Рекомендуемый дневной бюджет: {daily_budget:,.0f} ₽", size=16)
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("🧠 Умный калькулятор покупок", size=18, weight=ft.FontWeight.BOLD),
                        ft.TextField(
                            label="Название товара",
                            on_change=self.update_purchase_name
                        ),
                        ft.TextField(
                            label="Цена (₽)",
                            keyboard_type=ft.KeyboardType.NUMBER,
                            on_change=self.update_purchase_price
                        ),
                        ft.ElevatedButton(
                            "Могу ли я это купить?",
                            on_click=self.check_purchase_affordability,
                            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_400)
                        ),
                        ft.Container(
                            content=self.create_purchase_analysis(),
                            padding=10
                        )
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Быстрые действия", size=18, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.ElevatedButton("Добавить доход", on_click=self.show_add_income_dialog),
                            ft.ElevatedButton("Добавить расход", on_click=self.show_add_expense_dialog)
                        ], spacing=10)
                    ], spacing=10),
                    padding=20
                )
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
    
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
                        ft.Text("Введите числа от 1 до 31", size=12, color=ft.Colors.GREY_600)
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
                        ft.Text("Квартплата", size=18, weight=ft.FontWeight.BOLD),
                        ft.TextField(
                            label="Сумма квартплаты (₽)",
                            value=str(self.finance_app.data["rent"]),
                            on_change=self.update_rent
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
            ft.Text("Аналитика и прогнозы", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Умный прогноз", size=18, weight=ft.FontWeight.BOLD),
                        self.create_smart_forecast()
                    ], spacing=10),
                    padding=20
                )
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Статистика расходов", size=18, weight=ft.FontWeight.BOLD),
                        self.create_expense_statistics()
                    ], spacing=10),
                    padding=20
                )
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
    
    def get_next_salary_date(self):
        today = datetime.datetime.now()
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
        current_money = self.finance_app.data["current_money"]
        days_until_salary = (self.get_next_salary_date() - datetime.datetime.now()).days
        
        if days_until_salary > 0:
            return current_money / days_until_salary
        return 0
    
    def update_salary(self, e):
        try:
            self.finance_app.data["salary"] = float(e.control.value)
            self.finance_app.save_data()
        except ValueError:
            pass
    
    def update_current_money(self, e):
        try:
            self.finance_app.data["current_money"] = float(e.control.value)
            self.finance_app.save_data()
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
    
    def update_rent_paid_until(self, e):
        self.finance_app.data["rent_paid_until"] = e.control.value
        self.finance_app.save_data()
    
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
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        self.finance_app.data["transactions"].append(transaction)
        self.finance_app.save_data()
        self.page.update()
    
    def reset_rent(self, e):
        def confirm_reset(confirm_e):
            if confirm_e.control.text == "Да, сбросить":
                self.finance_app.data["rent"] = 0
                self.finance_app.data["rent_paid_until"] = None
                self.finance_app.save_data()
                self.page.update()
            self.close_dialog(confirm_e)
        
        def cancel_reset(cancel_e):
            self.close_dialog(cancel_e)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Сброс квартплаты"),
            content=ft.Text("Вы уверены, что хотите сбросить все настройки квартплаты? Это действие нельзя отменить."),
            actions=[
                ft.TextButton("Отмена", on_click=cancel_reset),
                ft.TextButton("Да, сбросить", on_click=confirm_reset, style=ft.ButtonStyle(color=ft.Colors.RED))
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
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
            paid_until_date = datetime.datetime.strptime(rent_paid_until, "%Y-%m-%d").date()
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
            paid_until_date = datetime.datetime.strptime(rent_paid_until, "%Y-%m-%d").date()
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
                goal_date = datetime.datetime.strptime(goal["date"], "%Y-%m-%d").date()
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
                                ft.ElevatedButton(
                                    "Добавить в цель",
                                    on_click=lambda e, goal_name=goal["name"]: self.show_add_to_goal_dialog(goal_name),
                                    style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_400)
                                )
                            ]),
                            ft.ProgressBar(value=progress, width=300),
                            ft.Text(progress_text, size=12)
                        ], spacing=5),
                        padding=15
                    )
                )
            )
        
        return ft.Column(goal_widgets)
    
    def calculate_goal_progress(self, goal):
        try:
            goal_name = goal["name"]
            invested_amount = self.finance_app.data["goal_investments"].get(goal_name, 0)
            
            goal_date = datetime.datetime.strptime(goal["date"], "%Y-%m-%d").date()
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
                goal_date = datetime.datetime.strptime(goal["date"], "%Y-%m-%d").date()
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
        current_month = datetime.datetime.now().strftime("%Y-%m")
        
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
        
        def add_transaction(e):
            try:
                amount = float(amount_field.value)
                description = description_field.value
                
                if amount > 0 and description:
                    transaction = {
                        "type": transaction_type,
                        "amount": amount,
                        "description": description,
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    
                    self.finance_app.data["transactions"].append(transaction)
                    
                    if transaction_type == "income":
                        self.finance_app.data["current_money"] += amount
                    else:
                        self.finance_app.data["current_money"] -= amount
                    
                    self.finance_app.save_data()
                    self.page.update()
                    self.page.dialog.open = False
                    self.page.update()
            except ValueError:
                pass
        
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Column([amount_field, description_field], tight=True),
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
                    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                    if date_obj.date() <= datetime.datetime.now().date():
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
                    
                    self.page.update()
                    
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
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
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
        
        # Проверяем нужно ли платить квартплату
        rent_due = self.check_rent_due()
        rent_to_pay = rent if rent_due else 0
        
        # Свободные деньги (не вложенные в цели, с учетом квартплаты)
        free_money = current_money - sum(goal_investments.values()) - rent_to_pay
        
        # Ежемесячный доход
        monthly_income = salary
        
        # Дневной бюджет
        days_until_salary = (self.get_next_salary_date() - datetime.datetime.now()).days
        daily_budget = free_money / max(days_until_salary, 1)
        
        if price <= free_money:
            # Можем купить прямо сейчас
            remaining_after_purchase = free_money - price
            days_remaining = remaining_after_purchase / daily_budget if daily_budget > 0 else 0
            
            return ft.Column([
                ft.Text("✅ Можете купить прямо сейчас!", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                ft.Text(f"Останется: {remaining_after_purchase:,.0f} ₽"),
                ft.Text(f"Этого хватит на: {days_remaining:.0f} дней"),
                ft.Text(f"Товар: {self.purchase_name}", size=12, color=ft.Colors.GREY_600)
            ], spacing=5)
        
        elif price <= current_money:
            # Можем купить, но придется снять с целей
            needed_from_goals = price - free_money
            
            return ft.Column([
                ft.Text("⚠️ Можете купить, но сняв с целей", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE),
                ft.Text(f"Нужно снять с целей: {needed_from_goals:,.0f} ₽"),
                ft.Text(f"Товар: {self.purchase_name}", size=12, color=ft.Colors.GREY_600),
                ft.Text("Рекомендуем подождать", size=12, color=ft.Colors.RED)
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
    
    def close_dialog(self, e=None):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

def main(page: ft.Page):
    app = MainApp(page)

if __name__ == "__main__":
    ft.app(target=main)
