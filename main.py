import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
def credit_approval_percentage(data):
    # Параметры
    age = int(data['AGE'])
    a=1
    socstatus_work = int(data['SOCSTATUS_WORK_FL'])
    socstatus_pension = int(data['SOCSTATUS_PENS_FL'])
    gender = int(data['GENDER'])
    children = int(data['CHILD_TOTAL'])
    dependants = int(data['DEPENDANTS'])
    income = float(data['PERSONAL_INCOME'].replace(',', '.'))
    credit_amount = float(data['CREDIT'].replace(',', '.'))
    loan_dlq_num = int(data['LOAN_DLQ_NUM'])
    loan_avg_dlq_amt = float(data['LOAN_AVG_DLQ_AMT'].replace(',', '.'))

    # Логика для определения процента выдачи кредита
    approval_percentage = 0

    if age >= 18 and socstatus_work == 1 and gender == 1 and income > 0 and loan_dlq_num == 0:
        approval_percentage += 20

    if children == 0 and dependants == 0:
        approval_percentage += 10

    # Прочие условия и их влияние на процент выдачи кредита...

    # Вернуть процент выдачи кредита
    return min(approval_percentage, 100)  # Ограничение процента до максимального значения 100


data = pd.read_csv('Credit_OTP.csv')

# Добавление нового столбца 'Credit_Approval_Percentage' на основе вашей функции
data['Credit_Approval_Percentage'] = data.apply(credit_approval_percentage, axis=1)

# Отображение первых нескольких строк DataFrame для проверки
print(data)

