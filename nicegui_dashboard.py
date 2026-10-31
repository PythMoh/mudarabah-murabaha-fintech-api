from nicegui import ui
import requests

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# Enable dark mode theme
ui.dark_mode().enable()

# --- Header ---
with ui.header().classes('bg-slate-900 text-white p-4 elevation-2 flex justify-between items-center'):
    ui.label('🏦 SHARIA FINTECH PORTAL').classes('text-xl font-bold tracking-wide text-emerald-400')
    ui.label('Sharia-Compliant Non-Interest Banking Portal').classes('text-sm text-slate-400')

# --- Main Page Layout ---
with ui.column().classes('w-full max-w-7xl mx-auto my-6 gap-6 p-4'):

    # Navigation Tabs
    with ui.tabs().classes('w-full text-emerald-400') as tabs:
        tab_mudarabah = ui.tab('Mudarabah (Profit Sharing)')
        tab_murabaha = ui.tab('Murabaha (Cost-Plus)')

    with ui.tab_panels(tabs, value=tab_mudarabah).classes('w-full bg-transparent'):
        
        # ==========================================
        # TAB 1: MUDARABAH PORTAL
        # ==========================================
        with ui.tab_panel(tab_mudarabah):
            ui.label('Mudarabah Profit-Sharing Calculator').classes('text-2xl font-bold text-slate-100 mb-4')

            with ui.grid(columns=12).classes('w-full gap-6'):
                
                # Input Panel
                with ui.card().classes('col-span-12 lg:col-span-4 bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg'):
                    ui.label('Business Execution Parameters').classes('text-lg font-semibold text-emerald-400 mb-4')

                    mud_account_id = ui.number('Financing Account ID', value=1, format='%d').classes('w-full mb-3')
                    gross_revenue = ui.number('Gross Revenue (₦)', value=500000.0, step=10000, precision=2).classes('w-full mb-3')
                    operating_expenses = ui.number('Operating Expenses (₦)', value=200000.0, step=10000, precision=2).classes('w-full mb-3')

                    ui.label('Bank Profit-Sharing Ratio (PSR)').classes('text-sm text-slate-300 mt-2')
                    bank_psr_slider = ui.slider(min=0.05, max=0.95, value=0.30, step=0.05).props('label-always color=emerald')

                    async def calculate_mudarabah():
                        payload = {
                            "account_id": int(mud_account_id.value),
                            "gross_revenue": float(gross_revenue.value),
                            "operating_expenses": float(operating_expenses.value),
                            "bank_psr_ratio": float(bank_psr_slider.value)
                        }
                        try:
                            res = requests.post(f"{API_BASE_URL}/calculate-mudarabah", json=payload)
                            if res.status_code == 200:
                                data = res.json()
                                mud_badge.set_text(f"✓ Mudarabah Calculation #{data['calculation_id']} Saved to MySQL")
                                mud_badge.classes(replace='bg-emerald-900/50 text-emerald-300 border-emerald-500')
                                
                                rev = float(gross_revenue.value)
                                exp = float(operating_expenses.value)
                                net = rev - exp
                                b_psr = float(bank_psr_slider.value)
                                c_psr = 1.0 - b_psr
                                
                                bank_share = max(0.0, net * b_psr) if net > 0 else 0.0
                                cust_share = max(0.0, net * c_psr) if net > 0 else net
                                
                                m_net_prof.set_text(f"₦{net:,.2f}")
                                m_bank_share.set_text(f"₦{bank_share:,.2f}")
                                m_cust_share.set_text(f"₦{cust_share:,.2f}")

                                # Update Pie Chart Dynamic Options
                                mud_chart.options['series'][0]['data'] = [
                                    {'value': round(bank_share, 2), 'name': 'Bank Share (Mudarib)'},
                                    {'value': round(cust_share, 2), 'name': 'Customer Share (Rab-ul-Mal)'}
                                ]
                                mud_chart.update()

                            else:
                                ui.notify(f"API Error: {res.json().get('detail')}", type='negative')
                        except Exception as e:
                            ui.notify(f"Connection Failed: {e}", type='negative')

                    ui.button('Calculate & Persist Share', on_click=calculate_mudarabah)\
                        .classes('w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-lg shadow-md mt-4')

                # Metrics & Interactive Pie Chart Display
                with ui.column().classes('col-span-12 lg:col-span-8 gap-6'):
                    mud_badge = ui.label('Awaiting Mudarabah Input...')\
                        .classes('w-full p-3 rounded-lg text-sm text-center border border-slate-700 bg-slate-800 text-slate-400')

                    with ui.grid(columns=3).classes('w-full gap-4'):
                        with ui.card().classes('bg-slate-800 p-4 rounded-xl border border-slate-700'):
                            ui.label('Net Profit / Loss').classes('text-xs text-slate-400')
                            m_net_prof = ui.label('₦0.00').classes('text-lg font-bold text-slate-100 mt-1')

                        with ui.card().classes('bg-slate-800 p-4 rounded-xl border border-slate-700'):
                            ui.label('Bank Share (Mudarib)').classes('text-xs text-slate-400')
                            m_bank_share = ui.label('₦0.00').classes('text-lg font-bold text-emerald-400 mt-1')

                        with ui.card().classes('bg-slate-800 p-4 rounded-xl border border-slate-700'):
                            ui.label('Customer Share (Rab-ul-Mal)').classes('text-xs text-slate-400')
                            m_cust_share = ui.label('₦0.00').classes('text-lg font-bold text-indigo-400 mt-1')

                    # EChart Pie Chart Visualizer
                    with ui.card().classes('w-full bg-slate-800 p-4 rounded-xl border border-slate-700 h-80'):
                        mud_chart = ui.echart({
                            'title': {'text': 'Profit Distribution Split', 'left': 'center', 'textStyle': {'color': '#f8fafc'}},
                            'tooltip': {'trigger': 'item', 'formatter': '{b}: ₦{c} ({d}%)'},
                            'legend': {'bottom': '0%', 'textStyle': {'color': '#94a3b8'}},
                            'series': [{
                                'type': 'pie',
                                'radius': ['40%', '70%'],
                                'color': ['#10b981', '#6366f1'],
                                'data': [
                                    {'value': 0, 'name': 'Bank Share (Mudarib)'},
                                    {'value': 0, 'name': 'Customer Share (Rab-ul-Mal)'}
                                ],
                                'label': {'color': '#f8fafc'}
                            }]
                        }).classes('w-full h-full')

        # ==========================================
        # TAB 2: MURABAHA PORTAL
        # ==========================================
        with ui.tab_panel(tab_murabaha):
            ui.label('Murabaha Contract Generator').classes('text-2xl font-bold text-slate-100 mb-4')

            with ui.grid(columns=12).classes('w-full gap-6'):
                
                # Left Input Card
                with ui.card().classes('col-span-12 lg:col-span-4 bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg'):
                    ui.label('Contract Parameters').classes('text-lg font-semibold text-emerald-400 mb-4')

                    account_id = ui.number('Account ID', value=1, format='%d').classes('w-full mb-3')
                    asset_cost = ui.number('Asset Acquisition Cost (₦)', value=5000000, precision=2).classes('w-full mb-3')
                    
                    ui.label('Annual Profit Rate (%)').classes('text-sm text-slate-300 mt-2')
                    profit_rate = ui.slider(min=1, max=50, value=20, step=0.5).props('label-always color=emerald')

                    tenure_months = ui.select(
                        label='Tenure (Months)', 
                        options=[6, 12, 18, 24, 36, 48], 
                        value=12
                    ).classes('w-full mt-2 mb-6')

                    async def generate_murabaha_contract():
                        payload = {
                            "account_id": int(account_id.value),
                            "asset_cost": float(asset_cost.value),
                            "profit_rate_annual": float(profit_rate.value / 100.0),
                            "tenure_months": int(tenure_months.value)
                        }
                        try:
                            res = requests.post(f"{API_BASE_URL}/calculate-murabaha", json=payload)
                            if res.status_code == 200:
                                data = res.json()
                                s = data["summary"]
                                
                                m_asset.set_text(f"₦{s['asset_cost']:,.2f}")
                                m_profit.set_text(f"₦{s['total_profit']:,.2f}")
                                m_total.set_text(f"₦{s['total_selling_price']:,.2f}")
                                m_installment.set_text(f"₦{s['monthly_installment']:,.2f}")
                                
                                # Process Schedule for NiceGUI Table
                                schedule_data = data["amortization_schedule"]
                                formatted_rows = []
                                for item in schedule_data:
                                    formatted_rows.append({
                                        'month': item['month'],
                                        'installment': f"₦{item['installment']:,.2f}",
                                        'cost_repaid': f"₦{item['cost_repaid']:,.2f}",
                                        'profit_repaid': f"₦{item['profit_repaid']:,.2f}",
                                        'remaining_balance': f"₦{item['remaining_balance']:,.2f}"
                                    })

                                table.rows = formatted_rows
                                table.update()

                                status_badge.set_text(f"✓ Murabaha Contract #{data['contract_id']} Persisted to MySQL")
                                status_badge.classes(replace='bg-emerald-900/50 text-emerald-300 border-emerald-500')
                            else:
                                ui.notify(f"API Error: {res.json().get('detail')}", type='negative')
                        except Exception as e:
                            ui.notify(f"Connection Failed: {e}", type='negative')

                    ui.button('Generate & Persist Contract', on_click=generate_murabaha_contract)\
                        .classes('w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-lg shadow-md')

                # Right Summary & Amortization Table
                with ui.column().classes('col-span-12 lg:col-span-8 gap-6'):
                    status_badge = ui.label('Awaiting Murabaha Input...')\
                        .classes('w-full p-3 rounded-lg text-sm text-center border border-slate-700 bg-slate-800 text-slate-400')

                    with ui.grid(columns=4).classes('w-full gap-4'):
                        with ui.card().classes('bg-slate-800 p-4 rounded-xl border border-slate-700'):
                            ui.label('Asset Cost').classes('text-xs text-slate-400')
                            m_asset = ui.label('₦0.00').classes('text-lg font-bold text-slate-100 mt-1')

                        with ui.card().classes('bg-slate-800 p-4 rounded-xl border border-slate-700'):
                            ui.label('Total Profit Markup').classes('text-xs text-slate-400')
                            m_profit = ui.label('₦0.00').classes('text-lg font-bold text-emerald-400 mt-1')

                        with ui.card().classes('bg-slate-800 p-4 rounded-xl border border-slate-700'):
                            ui.label('Selling Price').classes('text-xs text-slate-400')
                            m_total = ui.label('₦0.00').classes('text-lg font-bold text-slate-100 mt-1')

                        with ui.card().classes('bg-slate-800 p-4 rounded-xl border border-slate-700'):
                            ui.label('Monthly Installment').classes('text-xs text-slate-400')
                            m_installment = ui.label('₦0.00').classes('text-lg font-bold text-indigo-400 mt-1')

                    ui.label('Repayment Schedule Breakdown').classes('text-lg font-semibold text-slate-100 mt-2')
                    
                    columns = [
                        {'name': 'month', 'label': 'Month', 'field': 'month', 'align': 'left', 'sortable': True},
                        {'name': 'installment', 'label': 'Installment', 'field': 'installment', 'align': 'right'},
                        {'name': 'cost_repaid', 'label': 'Cost Repaid', 'field': 'cost_repaid', 'align': 'right'},
                        {'name': 'profit_repaid', 'label': 'Profit Repaid', 'field': 'profit_repaid', 'align': 'right'},
                        {'name': 'remaining_balance', 'label': 'Remaining Balance', 'field': 'remaining_balance', 'align': 'right'},
                    ]
                    
                    table = ui.table(columns=columns, rows=[], row_key='month')\
                        .classes('w-full bg-slate-800 rounded-xl border border-slate-700 text-slate-200')

ui.run(title='Sharia Fintech Portal', host='0.0.0.0', port=8501, dark=True)