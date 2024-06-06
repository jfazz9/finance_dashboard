import dash
from dash import html, dcc
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from datetime import datetime
import os

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

script_dir = os.path.dirname(__file__)
csv_path = os.path.join(script_dir, 'person_finance.csv')

# load data or create new file
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
else:
    data = {
        'Date': ['2023-01-01', '2023-02-01', '2023-03-01'],
        'Income': [4000, 2000, 7000],
        'Expenses': [2000, 1000, 3000]
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)

years = [{'label':str(year), 'value': str(year)} for year in range(2020,datetime.today().year +1)]
#navbar
navbar = dbc.NavbarSimple(
    brand="Personal Finance Dashboard",
    brand_href="#",
    color="black",
    dark=True
)

input_card = dbc.Card(
    dbc.CardBody([
        dbc.Row([
            dbc.Col(dcc.Dropdown(
            id='year-dropdown',options=years, placeholder='Select Year', value=None, 
            style={'display': 'left'}),width=2),
        dbc.Col(dcc.DatePickerSingle(id='date-input', placeholder='Select Date', display_format='YYYY-MM-DD', min_date_allowed='2020-01-01', #Date
                                    date=None, max_date_allowed=datetime.today().strftime('%Y-%m-%d'),
                                    first_day_of_week=1,clearable=True, disabled=False, style={'border': '3px solid #ccc'},
                                    className='datepicker'), width=6),
        
        dbc.Col(dbc.Input(id='income-input', type='number', placeholder='Enter Income'), width=4),
        dbc.Col(dbc.Input(id='expenses-input', type='number', placeholder='Enter Expenses'), width=4),
        dbc.Col(dbc.Button('Add', id='submit-button', color='primary'), width=2),
        dbc.Col(dbc.Button('Remove', id='remove-button', color='danger'), width=3)
        ])
    ])
)

graph_card = dbc.Card(
    dbc.CardBody([
        dbc.Row([
            dbc.Col(dcc.Graph(id="income-expense-graph"), width=12)
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='expense-distribution-pie'), width=6),
            dbc.Col(dcc.Graph(id='income-expense-trend'), width=6)
        ])
    ])
)
message_card = dbc.Card(
    dbc.CardBody([
        dbc.Row([
            dbc.Col(html.Div(id='summary-text'), width=12)
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='error-message', style={'color':'red'}), width = 12)
        ])
    ])
)

app.layout = dbc.Container([
    navbar,
    dbc.Container([
        input_card,
        html.Br(),
        message_card,
        html.Br(),
        graph_card
    ], fluid=True)
], fluid=True)


@app.callback(
        Output('date-input', 'month'),
        Input('year-dropdown', 'value')
)
def update_year_selector(selected_year):
    if selected_year:
        return f"{selected_year}-01-01"
    return datetime.today().strftime('%Y-%m-%d')


# Callback to update the graph
@app.callback(
    [Output('income-expense-graph', 'figure'),
    Output('expense-distribution-pie', 'figure'),
    Output('income-expense-trend', 'figure')],
    [Input('submit-button', 'n_clicks'),
     Input('remove-button', 'n_clicks')],
    [State('date-input', 'date'),
     State('income-input', 'value'),
     State('expenses-input', 'value')]
)
def update_graphs(add_clicks, remove_clicks, date, income, expenses):
    '''function to update the graphs'''
    global df
    ctx = dash.callback_context

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')

    if not ctx.triggered:
        income_expense_fig = {
        'data': [
            {'x': df['Date'], 'y': df['Income'], 'type': 'bar', 'name': 'Income'},
            {'x': df['Date'], 'y': df['Expenses'], 'type': 'bar', 'name': 'Expenses'}
        ],
        'layout': {
            'title': 'Monthly Income vs Expenses'
        }}
        expense_distribution_fig = {
            'data': [
                {'values': df['Expenses'], 'labels': df['Date'].dt.strftime('%Y-%m-%d'), 'type': 'pie', 'name': 'Expenses'}
            ],
            'layout': {
                'title': 'Expense Distribution'
            }
        }
        income_expense_trend_fig = {
            'data': [
                {'x': df['Date'], 'y': df['Income'], 'type': 'scatter', 'name':'Income'},
                {'x': df['Date'], 'y': df['Expenses'], 'type': 'scatter', 'name': 'Expenses'}
            ],
            'layout': {
                'title': 'Income and Expenses Over Time'
            }
        }
        return income_expense_fig, expense_distribution_fig, income_expense_trend_fig
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'submit-button':
        if date and income is not None and expenses is not None:
            try:
                datetime.strptime(date, '%Y-%m-%d')
                income = float(income)
                expenses = float(expenses)
                if income < 0 or expenses < 0:
                    raise ValueError("Income must be greater than zero")
            except (ValueError, TypeError):
                return {
                        'data': [
                            {'x': df['Date'], 'y': df['Income'], 'type': 'bar', 'name': 'Income'},
                            {'x': df['Date'], 'y': df['Expenses'], 'type': 'bar', 'name': 'Expenses'}
                        ],
                        'layout': {
                            'title': 'Monthly Income vs Expenses'
                        }
                    }, {
                        'data': [
                            {'values': df['Expenses'], 'labels': df['Date'].dt.strftime('%Y-%m-%d'), 'type': 'pie', 'name': 'Expenses'}
                        ],
                        'layout': {
                            'title': 'Expense Distribution'
                        }
                    }, {
                        'data': [
                            {'x': df['Date'], 'y': df['Income'], 'type': 'line', 'name': 'Income'},
                            {'x': df['Date'], 'y': df['Expenses'], 'type': 'line', 'name': 'Expenses'}
                        ],
                        'layout': {
                            'title': 'Income and Expenses Over Time'
                        }
                    }
            
            new_data = {'Date': [date], 'Income': [income], 'Expenses': [expenses]}
            new_df = pd.DataFrame(new_data)
            df = pd.concat([df, new_df], ignore_index=True)
            df['Date'] = pd.to_datetime(df['Date'])
            df.sort_values('Date', inplace=True)
            df.to_csv(csv_path, index=False)
    elif button_id == 'remove-button' and not df.empty:
        if date:
            date_to_remove = pd.to_datetime(date)
            df= df[df['Date'] != date_to_remove]
            df.to_csv(csv_path, index=False)
    income_expense_fig = {
        'data': [
            {'x': df['Date'], 'y': df['Income'], 'type': 'bar', 'name': 'Income'},
            {'x': df['Date'], 'y': df['Expenses'], 'type': 'bar', 'name': 'Expenses'}
        ],
        'layout': {
            'title': 'Monthly Income vs Expenses'
        }
    }
    expense_distribution_fig = {
            'data': [
                {'values': df['Expenses'], 'labels': df['Date'].dt.strftime('%Y-%m-%d'), 'type': 'pie', 'name': 'Expenses'}
            ],
            'layout': {
                'title': 'Expense Distribution'
            }
        }
    income_expense_trend_fig = {
                'data': [
                    {'x': df['Date'], 'y': df['Income'], 'type': 'line', 'name': 'Income'},
                    {'x': df['Date'], 'y': df['Expenses'], 'type': 'line', 'name': 'Expenses'}
                ],
                'layout': {
                    'title': 'Income and Expenses Over Time'
                }
            }
    return income_expense_fig, expense_distribution_fig, income_expense_trend_fig

@app.callback(
    Output('summary-text', 'children'),
    [Input('submit-button', 'n_clicks'),
    Input('remove-button', 'n_clicks')],
    [State('income-input', 'value'),
    State('expenses-input', 'value'),
    State('date-input', 'date')]
)
def update_summary(add_clicks, remove_clicks, income, expenses, date):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "Enter data to see the summary"
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id =='submit-button' and income > 0 and expenses > 0 and date is not None:
        summary = f"Latest Entry - Date: {date}, Income: ${income}, Expenses: ${expenses}"
    elif button_id == 'remove-button':
        summary =f"Removed the latest entry."
    else:
        summary = "Enter data to see the summary."
    
    return summary

# Callback to update the error message
@app.callback(
        Output('error-message', 'children'),
        [Input('submit-button', 'n_clicks')],
        [State('date-input', 'date'),
         State('income-input', 'value'),
         State('expenses-input', 'value')]
)
def update_error_message(n_clicks, date, income, expenses):
    if n_clicks is None:
        return ""
    if date:
        try:
            datetime.strptime(date, "%Y-%m-%d")
            income = float(income)
            expenses = float(expenses)
            if income < 0 or expenses < 0:
                return "Income and Expenses must be non-negative numbers."
        except(ValueError, TypeError):
            return "Invalid date format or non-numeric values for Income/Expenses"
    else:
        return "Please select a date."
    return ""


def print_data():
    print(df)
          

if __name__ == '__main__':
    app.run_server(debug=True)
    print_data()