import matplotlib.pyplot as plt
import numpy as np
from numpy_financial import pmt
import plotly.graph_objects as go
import matplotlib.ticker as ticker
import streamlit as st

# Function to calculate the cost of renting
def calculate_renting_cost(rent, duration_months, monthly_house_payment, savings_interest_rate, rent_increase_rate, down_payment, inflation_rate, monthly_loan_payment):
    # Need original Price that lasted for sub loan term (loan + extras)
    savings, renting_cost = 0, 0
    # print("start: ", monthly_house_payment, monthly_loan_payment)
    for i in range(duration_months):
        if duration_months > loan_term * 12 and i <= loan_term * 12:
            payment = monthly_loan_payment + monthly_house_payment
            # print("Corrected Payment: ", payment)
        else:
            payment = monthly_house_payment
        # print(monthly_house_payment, rent)
        if i == 0:
            savings = down_payment
        if payment >= rent:
            savings = (payment - rent + savings) * ((1 + (savings_interest_rate - inflation_rate) / 12 / 100))
        else:
            savings = savings * ((1 + (savings_interest_rate - inflation_rate) / 12 / 100))
        renting_cost += rent
        rent *= (1 + rent_increase_rate / 12 / 100)
        # print(rent, renting_cost, savings, payment)
    return renting_cost, savings, rent

# Function to calculate the cost of buying
def calculate_buying_cost(purchase_price, down_payment, interest_rate, loan_term, property_tax, insurance, maintenance_cost, duration_months, inflation_rate, home_appreciation_rate, closing_costs, monthly_home_extras, tax_deduction_rate):
    loan_amount = purchase_price - down_payment - closing_costs
    monthly_interest_rate = interest_rate / 12 / 100
    num_of_payments = loan_term * 12

    monthly_property_tax_cost = property_tax * 1 / 12
    monthly_insurance_cost = insurance * 1 / 12
    monthly_maintenance_cost = maintenance_cost * 1 / 12
    monthly_extras_cost = monthly_home_extras
    
    original_loan_payment = pmt(monthly_interest_rate, num_of_payments, -loan_amount)
    monthly_loan_payment = pmt(monthly_interest_rate, num_of_payments, -loan_amount)

    loan_balance = loan_amount
    loan_cost = 0

    for i in range(duration_months):
        if int(loan_balance) <= 0:
            # print('Zero Loan', loan_balance, i)
            monthly_loan_payment = loan_balance = 0
            break
        interest_payment = loan_balance * monthly_interest_rate
        principal_payment = monthly_loan_payment - interest_payment
        if principal_payment > loan_balance:
            principal_payment = monthly_loan_payment = loan_balance
        loan_balance -= principal_payment
        loan_cost += interest_payment

    monthly_house_payment = monthly_loan_payment + monthly_property_tax_cost + monthly_insurance_cost + monthly_maintenance_cost + monthly_extras_cost
    monthly_non_loan = monthly_house_payment - monthly_loan_payment
    # print("Monthly House Payment: ${:,}".format(round(monthly_house_payment,2)))
    # print("Monthly Loan Payment: ${:,}".format(round(monthly_loan_payment,2)))

    property_tax_cost = property_tax * duration_months / 12
    insurance_cost = insurance * duration_months / 12
    maintenance_cost = maintenance_cost * duration_months / 12
    extras_cost = monthly_home_extras * duration_months

    buying_cost = loan_cost + purchase_price + property_tax_cost + insurance_cost + maintenance_cost + extras_cost + closing_costs
    # print("Inputs: ", int(loan_cost), purchase_price, property_tax_cost, insurance_cost, maintenance_cost, extras_cost, closing_costs)
    # print("Buying Cost: ", buying_cost)
    # Calculate future home value based on appreciation rate
    future_home_value = purchase_price * (1 + home_appreciation_rate / 12 / 100) ** (duration_months / 12) - closing_costs

    # Adjust costs for inflation rate
    inflation_factor = (1 + inflation_rate / 12 / 100) ** (duration_months / 12)
    buying_cost *= inflation_factor
    # print("Buying Cost Inflation: ", buying_cost)
    future_home_value *= inflation_factor

    # Calculate tax deductions
    if monthly_loan_payment == 0:
        interest_payment_total = pmt(monthly_interest_rate, num_of_payments, -loan_amount) * num_of_payments - loan_amount
    else:
        interest_payment_total = monthly_loan_payment * num_of_payments - loan_amount
    # print("interest payment total: ", interest_payment_total)
    # print("Loan balance", loan_balance)
    tax_savings = (property_tax + interest_payment_total) * (tax_deduction_rate / 100) * duration_months / 12
    buying_cost -= tax_savings
    # print("Buying Cost Tax: ", buying_cost)

    # Return the net cost of buying after factoring in future home value
    net_buying_cost = buying_cost - future_home_value
    # print("n ",net_buying_cost, buying_cost, future_home_value)
    return net_buying_cost, monthly_house_payment, future_home_value, original_loan_payment
# Main program
# Setting up Streamlit Data App
st.set_page_config(page_title="Rent vs Buy Simulator", layout="centered")
st.title("Rent vs Buy Simulator")
st.markdown("---")
with st.sidebar:
    st.title("Main Inputs")
    st.header("Duration")
    st.subheader("Months")
    duration_months = st.number_input("Enter the duration in months: ", min_value=1, format='%d', step=1, value=60)
    st.write("Years: " + str(round(duration_months / 12, 2)))
    st.subheader("Home Value")
    purchase_price = st.number_input("Enter your home value($): ", min_value=0, format='%d', step=100, value=650000)
    st.subheader("Down Payment Amount")
    down_payment = st.number_input("Enter your down payment amount($): ", min_value=0, format='%d', step=100, value=int(0.2*purchase_price))
    st.subheader("Loan Interest Rate")
    interest_rate = st.number_input("Enter your home loan interest rate(%): ", min_value=0.0, format='%f', step=0.1, value=4.5)
    st.subheader("Payment Period (Years)")
    loan_term = st.number_input("Enter your target payment period (years): ", min_value=3, format='%d', step=1, value=30)
    st.subheader("Monthly Rent")
    rent = st.number_input("Enter your monthly rent amount($): ", min_value=0, format='%d', step=100, value=2175)
st.header("Additional Details")
col1, col2 = st.columns(2)
with col1:
    st.header("Expenses")

    st.subheader("Property Tax (Yearly)")
    property_tax = st.number_input("Enter your yearly property tax($): ", min_value=0, format='%d', step=100, value=5000)

    st.subheader("Home Insurance (Yearly)")
    insurance = st.number_input("Enter your yearly home insurace($): ", min_value=0, format='%d', step=100)

    st.subheader("Maintenance (Yearly)")
    maintenance_cost = st.number_input("Enter your yearly home maintenance($): ", min_value=0, format='%d', step=100)

    st.subheader("Monthly Fees")
    monthly_home_extras = st.number_input("Enter your monthly HOA fees or extras($): ", min_value=0, format='%d', step=10)

    st.subheader("Closing Costs")
    closing_costs = st.number_input("Enter your closing costs($): (applied on buy & sell)", min_value=0, format='%d', step=100, value=5000)
with col2:
    st.header("Rates")

    st.subheader("Inflation Rate")
    inflation_rate = st.number_input("Enter the inflation rate(%): ", min_value=0.0, format='%f', step=0.1)

    st.subheader("Home Appreciation")
    home_appreciation_rate = st.number_input("Enter your home appreciation rate(%): ", min_value=0.0, format='%f', step=0.1, value=3.0)

    st.subheader("Tax Deduction Rate")
    tax_deduction_rate = st.number_input("Enter your tax deduction rate(%): ", min_value=0.0, format='%f', step=0.1, value=2.5)

    st.subheader("Savings Interest Rate")
    savings_interest_rate = st.number_input("Enter your savings interest rate(%): ", min_value=0.0, format='%f', step=0.1, value=3.0)

    st.subheader("Rent Increase Rate")
    rent_increase_rate = st.number_input("Enter your rent increase rate(%): ", min_value=0.0, format='%f', step=0.1, value=2.5)

### Input parameters
##Duration in Months
# duration_months = 360
#Home Centered
# purchase_price = 508000
# down_payment = 120000
# interest_rate = 5.5             #Mortage Loan Rate
# loan_term = 30                 
# property_tax = 11000             #Yearly
# insurance = 1000                #Yearly
# maintenance_cost = 2000         #Yearly
# inflation_rate = 3.5
# home_appreciation_rate = 4.0
# closing_costs = 5000
# monthly_home_extras = 100
# tax_deduction_rate = 2.0
#Rent Centered
# rent = 2100
# savings_interest_rate = 4.5
# rent_increase_rate = 2.5

# Calculate the costs
buying_cost, monthly_payment, future_home_value, original_loan_payment = calculate_buying_cost(purchase_price, down_payment, interest_rate, loan_term, property_tax, insurance, maintenance_cost, 
                                                                        duration_months, inflation_rate, home_appreciation_rate, closing_costs, monthly_home_extras, tax_deduction_rate)
renting_cost, savings, current_rent = calculate_renting_cost(rent, duration_months, monthly_payment, savings_interest_rate, rent_increase_rate, down_payment, inflation_rate, original_loan_payment)
# Calculate the savings difference and final result
savings_difference = abs(renting_cost - (savings - down_payment) - buying_cost)
print("end:",buying_cost, renting_cost-(savings-down_payment))
if buying_cost > (renting_cost - (savings - down_payment)):
    final_result = "Renting is better!"
else:
    final_result = "Buying is better!"

# Print the results to cmd
print("Cost of Renting: ${:,}".format(round(renting_cost, 2)))
print("Cost of Renting with Savings offset: ${:,}".format(round(renting_cost-(savings-down_payment), 2)))
print("Cost of Buying: ${:,}".format(round(buying_cost, 2)))
print("Savings Difference: ${:,}".format(round(savings_difference, 2)))
print("Assumes House Sale: ${:,}".format(round(future_home_value, 2)))
print("Assumes Net Rent Savings Acct: ${:,}".format(round(savings, 2)))
print(final_result)
#Show results on streamlit
st.markdown("---")
st.title("Results")
st.markdown("---")
st.header(final_result)
st.subheader("_Cost of Renting:_ ${:,}".format(round(renting_cost, 2)))
st.subheader("_Cost of Renting with Savings offset:_  ${:,}".format(round(renting_cost-(savings-down_payment), 2)))
st.subheader("_Cost of Buying:_  ${:,}".format(round(buying_cost, 2)))
st.subheader("_Savings Difference:_  ${:,}".format(round(savings_difference, 2)))
st.subheader("_House Sale:_  ${:,}".format(round(future_home_value, 2)))
st.subheader("_Rent Savings Acct:_  ${:,}".format(round(savings, 2)))



## Calculate Arrays & Plot the results
rent_costs, total_current_rent, rentdiff_costs = [], [], []
buying_costs, total_monthly_payment = [], []
savings, savings_differences = [], []
durations = np.arange(1, duration_months + 1)
for duration_months in (durations):
    current_buy_cost, current_monthly_payment, current_home_value, monthly_loan_payment = calculate_buying_cost(purchase_price, down_payment, interest_rate, loan_term, property_tax, insurance, maintenance_cost, duration_months, inflation_rate, home_appreciation_rate, closing_costs, monthly_home_extras, tax_deduction_rate)
    current_rent_cost, current_savings, current_rent = calculate_renting_cost(rent, duration_months, current_monthly_payment, savings_interest_rate, rent_increase_rate, down_payment, inflation_rate, monthly_loan_payment)
    rent_costs.append(current_rent_cost)
    rentdiff_costs.append(current_rent_cost-(current_savings-down_payment))
    savings.append(current_savings)
    buying_costs.append(current_buy_cost)
    total_current_rent.append(current_rent)
    total_monthly_payment.append(current_monthly_payment)
    savings_differences.append(current_rent_cost - (current_savings - down_payment) - current_buy_cost)

crossings = []
# renting_cost - (savings - down_payment) - buying_cost 
for i in range(1, len(savings_differences)):
    if savings_differences[i-1] < 0 and savings_differences[i] >= 0:
        crossings.append(durations[i])
    elif savings_differences[i-1] >= 0 and savings_differences[i] < 0:
        crossings.append(durations[i])
if len(crossings) == 0:
    break_even = "Never"
else:
    break_even = str(crossings[0])
st.subheader("Breakeven Month: " + break_even)

# print("Buying Cost: ", buying_costs)
# print("Buying Cost: ", buying_costs[-2])
# print("Savings Account: ", savings)
# Create a figure with multiple subplots
# fig, axs = plt.subplots(4, 1, figsize=(10, 15))
# # Plot 1: Renting vs. Buying Cost Comparison
# axs[0].plot(durations, rent_costs, label='Renting Cost')
# axs[0].plot(durations, buying_costs, label='Buying Cost')
# axs[0].set_xlabel('Duration (months)')
# axs[0].set_ylabel('Cost')
# axs[0].yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
# y_max = max(max(rent_costs), max(buying_costs))
# axs[0].set_ylim(0, y_max * 1.1)
# axs[0].set_title('Renting vs. Buying Cost Comparison')
# axs[0].legend(loc='upper left')

# # Plot 2: Monthly Payment Comparison
# axs[1].plot(durations, total_current_rent, label='Rent')
# axs[1].plot(durations, total_monthly_payment, label='Monthly Payment')
# axs[1].set_xlabel('Duration (months)')
# axs[1].set_ylabel('Cost')
# axs[1].yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
# y_max = max(max(total_current_rent), max(total_monthly_payment))
# y_min = min(min(total_current_rent), min(total_monthly_payment))
# axs[1].set_ylim(y_min * 0.7, y_max * 1.2)
# axs[1].set_title('Monthly Payment Comparison')
# axs[1].legend(loc='upper left')

# # Plot 3: Savings Account Balance
# axs[2].plot(durations, savings)
# axs[2].set_xlabel('Duration (months)')
# axs[2].set_ylabel('Savings Account Balance')
# axs[2].yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
# y_max = max(savings)
# axs[2].set_ylim(0, y_max * 1.3)
# axs[2].set_title('Savings Account Balance While Renting')

# # Plot 4: Renting Offset vs. Buying Cost Comparison
# axs[3].plot(durations, rentdiff_costs, label='Renting Offset Savings')
# axs[3].plot(durations, buying_costs, label='Buying Cost')
# axs[3].set_xlabel('Duration (months)')
# axs[3].set_ylabel('Cost')
# axs[3].yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
# y_max = max(max(rentdiff_costs), max(buying_costs))
# axs[3].set_ylim(min(rentdiff_costs)*1.1, y_max * 1.1)
# axs[3].set_title('Renting with Savings vs. Buying Cost Comparison')
# axs[3].legend(loc='upper left')
# # Adjust spacing between subplots
# plt.tight_layout()
# # Show all plots
# st.pyplot(fig)

st.markdown("---")
st.header("Charts!")
st.markdown("---")
Compare = go.Figure()
Compare.add_trace(go.Scatter(x=durations, y=rent_costs, mode='lines', 
                         marker=dict(line=dict(width=4), color='red', size=3), name="Rent",
                         hovertemplate="<b>%{y:$,d}</b>" 
                        ))
Compare.add_trace(go.Scatter(x=durations, y=buying_costs, mode='lines', 
                         marker=dict(line=dict(width=4), color='green'), name="Buy",
                         hovertemplate="<b>%{y:$,d}</b>" 
                         ))
Compare.update_layout(title="Renting vs. Buying Cost Comparison", xaxis_title='Duration (months)', yaxis_title='Cost ($)',
                  hovermode='x unified',
                  height=500, width=1200,
                  xaxis=dict(nticks=20),
                  yaxis=dict(nticks=20),
                  xaxis_range = [0, max(durations)+10],
                  yaxis_range = [0, 1.2 * max(max(rent_costs), max(buying_costs))],
                  legend=dict(orientation="h", yanchor='top', y=1.14, xanchor='left', x=0.01, font=dict(size=16))
                )

MonthlyPayment = go.Figure()
MonthlyPayment.add_trace(go.Scatter(x=durations, y=total_current_rent, mode='lines', 
                         marker=dict(line=dict(width=4), color='red'), name="Rent",
                         hovertemplate="<b>%{y:$,d}</b>" ))
MonthlyPayment.add_trace(go.Scatter(x=durations, y=total_monthly_payment, mode='lines', 
                         marker=dict(line=dict(width=4), color='green'), name="Monthly Payment",
                         hovertemplate="<b>%{y:$,d}</b>" ))
MonthlyPayment.update_layout(title="Monthly Payment Comparison", xaxis_title='Duration (months)', yaxis_title='Cost ($)',
                  hovermode='x unified',
                  height=500, width=1200,
                  xaxis=dict(nticks=20),
                  yaxis=dict(nticks=20),
                  xaxis_range = [0, max(durations)+10],
                  yaxis_range = [0.7 * min(min(total_current_rent), min(total_monthly_payment)), 
                                 1.2 * max(max(total_current_rent), max(total_monthly_payment))],
                  legend=dict(orientation="h", yanchor='top', y=1.14, xanchor='left', x=0.01, font=dict(size=16))
                )

SavingsAcct = go.Figure()
SavingsAcct.add_trace(go.Scatter(x=durations, y=savings, mode='lines', 
                         marker=dict(line=dict(width=4), color='red'), name="Balance",
                         hovertemplate="<b>%{y:$,d}</b>" ))
SavingsAcct.update_layout(title="Savings Account Balance While Renting", xaxis_title='Duration (months)', yaxis_title='Savings Account Balance',
                  hovermode='x unified',
                  height=500, width=1200,
                  xaxis=dict(nticks=20),
                  yaxis=dict(nticks=20),
                  xaxis_range = [0, max(durations)+10],
                  yaxis_range = [0, 
                                 1.2 * max(savings)],
                  legend=dict(orientation="h", yanchor='top', y=1.14, xanchor='left', x=0.01, font=dict(size=16)),
                  showlegend=True
                )

Compare_wSavings = go.Figure()
Compare_wSavings.add_trace(go.Scatter(x=durations, y=rentdiff_costs, mode='lines', 
                         marker=dict(line=dict(width=4), color='red'), name="Renting Offset Savings",
                         hovertemplate="<b>%{y:$,d}</b>" ))
Compare_wSavings.add_trace(go.Scatter(x=durations, y=buying_costs, mode='lines', 
                         marker=dict(line=dict(width=4), color='green'), name="Buying Cost",
                         hovertemplate="<b>%{y:$,d}</b>" ))
Compare_wSavings.update_layout(title="Renting with Savings vs. Buying Cost Comparison", xaxis_title='Duration (months)', yaxis_title='Cost ($)',
                  hovermode='x unified',
                  height=500, width=1200,
                  xaxis=dict(nticks=20),
                  yaxis=dict(nticks=20),
                  xaxis_range = [0, max(durations)+10],
                  yaxis_range = [0.7 * min(rentdiff_costs), 
                                 1.2 * max(max(rentdiff_costs), max(buying_costs))],
                  legend=dict(orientation="h", yanchor='top', y=1.14, xanchor='left', x=0.01, font=dict(size=16))
                )
st.plotly_chart(Compare, use_container_width=True)
st.plotly_chart(Compare_wSavings, use_container_width=True)
st.plotly_chart(SavingsAcct, use_container_width=True)
st.plotly_chart(MonthlyPayment, use_container_width=True)