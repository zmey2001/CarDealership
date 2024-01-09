import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Загрузка данных
data = pd.read_csv('Credit_OTP.csv')

# Создание Dash-приложения
app = dash.Dash(__name__)
server = app.server

# Создание выпадающего списка с уникальными значениями из 'POSTAL_ADDRESS_PROVINCE'
provinces = data['POSTAL_ADDRESS_PROVINCE'].unique()
dropdown_options = [{'label': province, 'value': province} for province in provinces]

app.layout = html.Div(
    [
        dcc.Dropdown(
            id='province-dropdown',
            options=dropdown_options,
            multi=True,
            value=[],  # Начально нет выбранных значений
            style={'color': 'blue'}  # Синий цвет текста
        ),
        html.Br(),
        dcc.Graph(id='credit-histogram'),  # Отображение гистограммы
        html.Div(id='output-data'),  # Отображение отфильтрованных данных
        dcc.Graph(id='loan-scatter-plot'),  # Отображение точечной диаграммы
        html.Br(),
    ],
    style={'background-color': 'navy', 'color': 'white', 'font-family': 'Arial, sans-serif'}
)

# Callback для обновления гистограммы на основе выбранных областей
@app.callback(
    Output('credit-histogram', 'figure'),
    Output('output-data', 'children'),  # Вывод таблицы данных
    [Input('province-dropdown', 'value')]
)
def update_histogram(selected_provinces):
    if not selected_provinces:  # Если области не выбраны, выводим сообщение
        return {}, []

    filtered_data = data[data['POSTAL_ADDRESS_PROVINCE'].isin(selected_provinces)]
    fig = px.histogram(filtered_data, x='CREDIT', title='Распределение последней суммы кредита', hover_data=['AGREEMENT_RK'])
    fig.update_layout(
        xaxis_title='Сумма последнего кредита (рубли)',
        yaxis_title='Количество',
        xaxis=dict(title='Сумма последнего кредита (рубли)'),
        yaxis=dict(title='Количество')
    )

    # Вывод основных и нужных столбцов для анализа
    output_table = filtered_data[['AGREEMENT_RK', 'TARGET', 'AGE', 'SOCSTATUS_WORK_FL', 'SOCSTATUS_PENS_FL', 'GENDER', 'CHILD_TOTAL', 'DEPENDANTS', 'EDUCATION', 'MARITAL_STATUS', 'FAMILY_INCOME', 'PERSONAL_INCOME']]
    output_table = output_table.head(10)  # Выводим только первые 10 строк для примера

    return fig, html.Table(
        [
            html.Thead(html.Tr([html.Th(col) for col in output_table.columns])),
            html.Tbody(
                [
                    html.Tr([html.Td(output_table.iloc[i][col]) for col in output_table.columns]) for i in range(len(output_table))
                ]
            ),
        ],
        style={'border': '1px solid white', 'padding': '5px'}
    )

# Callback для обновления точечной диаграммы на основе выбранных областей
@app.callback(
    Output('loan-scatter-plot', 'figure'),
    [Input('province-dropdown', 'value')]
)
def update_scatter_plot(selected_provinces):
    if not selected_provinces:  # Если области не выбраны, выводим сообщение
        return {}

    filtered_data = data[data['POSTAL_ADDRESS_PROVINCE'].isin(selected_provinces)]
    fig = px.scatter(filtered_data, x='AGE', y='LOAN_DLQ_NUM', title='Точечная диаграмма LOAN_DLQ_NUM (количество просрочек)по возрасту', hover_data=['AGREEMENT_RK'])
    fig.update_layout(
        xaxis_title='Возраст',
        yaxis_title='LOAN_DLQ_NUM (количество просрочек)',
        xaxis=dict(title='Возраст'),
        yaxis=dict(title='LOAN_DLQ_NUM')
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
