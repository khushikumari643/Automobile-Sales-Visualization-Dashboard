# ============================================================
#  Automobile Sales Statistics Dashboard  —  Dash + Plotly
#  Run : python automobile_dashboard.py
#  Open: http://127.0.0.1:8050
# ============================================================

import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Output, Input



# ── Load data ────────────────────────────────────────────────────────────────

URL = "Enter the file URL"
data = pd.read_csv(URL)
data['Year'] = pd.to_numeric(data['Year'], errors='coerce')
recession_data = data[data['Recession'] == 1]
year_list = sorted(data['Year'].dropna().astype(int).unique().tolist())



# ── App layout ────────────────────────────────────────────────────────────────
app = Dash(__name__)
app.title = "Automobile Sales Dashboard"
app.layout = html.Div([
    html.H1(
        "Automobile Sales Statistics Dashboard",
        style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 24}
    ),
  
    # ── Dropdowns ─────────────────────────────────────────────────────────────
    html.Div([
        dcc.Dropdown(
            id='dropdown-statistics',
            options=[
                {'label': 'Yearly Statistics',            'value': 'Yearly Statistics'},
                {'label': 'Recession Period Statistics',  'value': 'Recession Period Statistics'},
            ],
            placeholder='Select a report type',
            style={'width': '80%', 'padding': '3px', 'fontSize': '20px', 'textAlignLast': 'center'}
        ),

        dcc.Dropdown(
            id='select-year',
            options=[{'label': i, 'value': i} for i in year_list],
            placeholder='Select year',
            style={'width': '80%', 'padding': '3px', 'fontSize': '20px', 'textAlignLast': 'center'}
        ),
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'}),

    # ── Output container ──────────────────────────────────────────────────────
    html.Div(
        id='output-container',
        className='chart-grid',
    )
])



# ── Callback 1 : enable / disable year dropdown ───────────────────────────────

@app.callback(
    Output('select-year', 'disabled'),
    Input('dropdown-statistics', 'value')
)
def update_input_container(selected_statistics):
    return selected_statistics != 'Yearly Statistics'


# ── Callback 2 : render charts ────────────────────────────────────────────────
@app.callback(
    Output('output-container', 'children'),
    [
        Input('dropdown-statistics', 'value'),
        Input('select-year',         'value'),
    ]
)


def update_output_container(selected_statistics, input_year):
    if selected_statistics == 'Recession Period Statistics':

        # Chart R1 : Average automobile sales per year during recessions
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(figure=px.line(
            yearly_rec, x='Year', y='Automobile_Sales',
            title="Average Automobile Sales during Recession (Year-wise)"
        ))

        # Chart R2 : Average sales by vehicle type during recessions
        avg_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(figure=px.bar(
            avg_sales, x='Vehicle_Type', y='Automobile_Sales',
            title="Average Vehicle Sales by Type during Recession"
        ))

        # Chart R3 : Advertising expenditure share by vehicle type
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(figure=px.pie(
            exp_rec, values='Advertising_Expenditure', names='Vehicle_Type',
            title="Advertising Expenditure Share by Vehicle Type during Recession"
        ))

        # Chart R4 : Effect of unemployment rate on sales by vehicle type
        unemp_data = (recession_data
                      .groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales']
                      .mean().reset_index())
        R_chart4 = dcc.Graph(figure=px.bar(
            unemp_data, x='unemployment_rate', y='Automobile_Sales', color='Vehicle_Type',
            labels={'unemployment_rate': 'Unemployment Rate',
                    'Automobile_Sales':  'Average Automobile Sales'},
            title='Effect of Unemployment Rate on Vehicle Type and Sales'
        ))

        return [
            html.Div(className='chart-item',
                     children=[html.Div(R_chart1), html.Div(R_chart2)],
                     style={'display': 'flex'}),
            html.Div(className='chart-item',
                     children=[html.Div(R_chart3), html.Div(R_chart4)],
                     style={'display': 'flex'}),
        ]

    # ── Yearly Statistics ─────────────────────────────────────────────────────
    elif selected_statistics == 'Yearly Statistics' and input_year:

        yearly_data = data[data['Year'] == int(input_year)]

        # Chart Y1 : Yearly average automobile sales — whole period
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(figure=px.line(
            yas, x='Year', y='Automobile_Sales',
            title="Average Automobile Sales (Year-wise)"
        ))

        # Chart Y2 : Total monthly automobile sales
        mas = data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        Y_chart2 = dcc.Graph(figure=px.line(
            mas, x='Month', y='Automobile_Sales',
            title="Total Monthly Automobile Sales"
        ))

        # Chart Y3 : Average sales by vehicle type for selected year
        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(figure=px.bar(
            avr_vdata, x='Vehicle_Type', y='Automobile_Sales',
            title=f"Average Vehicles Sold by Vehicle Type in {input_year}"
        ))

        # Chart Y4 : Total advertising expenditure by vehicle type for selected year
        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(figure=px.pie(
            exp_data, values='Advertising_Expenditure', names='Vehicle_Type',
            title=f"Total Advertisement Expenditure by Vehicle Type in {input_year}"
        ))

        return [
            html.Div(className='chart-item',
                     children=[html.Div(Y_chart1), html.Div(Y_chart2)],
                     style={'display': 'flex'}),
            html.Div(className='chart-item',
                     children=[html.Div(Y_chart3), html.Div(Y_chart4)],
                     style={'display': 'flex'}),
        ]

    # ── Nothing selected yet ──────────────────────────────────────────────────
    return html.P("Please select a report type above.",
                  style={'textAlign': 'center', 'color': '#888', 'marginTop': '40px'})


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)
