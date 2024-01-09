import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Загрузка данных
data = pd.read_csv('Credit_OTP.csv')

# Создание Dash-приложения
app = dash.Dash(__name__)

# Создание выпадающего списка с уникальными значениями из 'POSTAL_ADDRESS_PROVINCE'
provinces = data['POSTAL_ADDRESS_PROVINCE'].unique()
dropdown_options = [{'label': province, 'value': province} for province in provinces]

app.layout = html.Div([
    dcc.Dropdown(
        id='province-dropdown',
        options=dropdown_options,
        multi=True,
        value=[]  # Начально нет выбранных значений
    ),
    html.Br(),
    dcc.Graph(id='credit-histogram'),  # Отображение гистограммы
    dcc.Graph(id='loan-scatter-plot'),  # Отображение точечной диаграммы
    html.Br(),
    html.Div(id='output-data')  # Отображение отфильтрованных данных
])

# Callback для обновления гистограммы на основе выбранных областей
@app.callback(
    Output('credit-histogram', 'figure'),
    [Input('province-dropdown', 'value')]
)
def update_histogram(selected_provinces):
    if not selected_provinces:  # Если области не выбраны, выводим сообщение
        return {}

    filtered_data = data[data['POSTAL_ADDRESS_PROVINCE'].isin(selected_provinces)]
    fig = px.histogram(filtered_data, x='CREDIT', title='Распределение последней суммы кредита')
    fig.update_layout(xaxis_title='Сумма последнего кредита (рубли)', yaxis_title='Количество')
    
    return fig

# Callback для обновления точечной диаграммы на основе выбранных областей
@app.callback(
    Output('loan-scatter-plot', 'figure'),
    [Input('province-dropdown', 'value')]
)
def update_scatter_plot(selected_provinces):
    if not selected_provinces:  # Если области не выбраны, выводим сообщение
        return {}

    filtered_data = data[data['POSTAL_ADDRESS_PROVINCE'].isin(selected_provinces)]
    fig = px.scatter(filtered_data, x='AGE', y='LOAN_DLQ_NUM', title='Точечная диаграмма LOAN_DLQ_NUM по возрасту')
    fig.update_layout(xaxis_title='Возраст', yaxis_title='LOAN_DLQ_NUM')
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
