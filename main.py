import streamlit as st
from add_diary_entry import DiaryEntryHelper
from get_analysis import GetAnalysis
import pandas as pd

selection = st.sidebar.radio("Navigation", ["Add Diary Entry","Get Analysis"])
diary_entry_helper = DiaryEntryHelper()

if selection == "Add Diary Entry":
	st.title("My Diary")
	first , second = st.columns(2)
	first_val = first.text_input("Title of Entry")
	second_val = second.date_input("Date of Entry")
	
	entry = st.text_area("Entry")
	
	blank1, sub , blank2 = st.columns(3)
	sub_val = sub.button("Submit Entry")
	
	if sub_val:		
 		diary_entry_helper.insert_entry(second_val, first_val, entry)

elif selection == "Get Analysis":
	st.title("Get Analysis for Month")
	month = st.text_input("Enter the month: ")
	if st.button("Get Analysis"):
		# pass
		get_analysis_object = GetAnalysis()
		result_money = get_analysis_object.get_money_flow(month)
		income = result_money["income"]
		expense = result_money["expenses"]
		st.write("Income")
		inc_dates =[]
		inc_amount=[]
		inc_source=[]
		for curr in income:
			if curr and len(curr[0]) != 0:
				inc_dates.append(curr[0][0]["date"])
				inc_source.append(curr[0][0]["received from"])
				inc_amount.append(curr[0][0]["received"])

		inc_data = {
			"dates": inc_dates,
			"amount" : inc_amount,
			"source" : inc_source
		}
		df1 = pd.DataFrame(inc_data)

		st.write(df1)

		st.write("Expenses")
		exp_dates = []
		exp_amount = []
		exp_source = []
		for curr in expense:
			if curr and len(curr[0]) != 0 :
				exp_dates.append(curr[0][0]["date"])
				exp_amount.append(curr[0][0]["spent"])
				exp_source.append(curr[0][0]["spent on"])

		exp_data = {
			"dates" : exp_dates,
			"amount" : exp_amount,
			"source" : exp_source
		}
		df2 = pd.DataFrame(exp_data)
		st.write(df2)
		# st.write(income)
		# st.write(expense)
		# result_sentiment = get_analysis_object.get_sentiment_analysis(month)
		# st.write(result_money)
		# st.write(result_sentiment)