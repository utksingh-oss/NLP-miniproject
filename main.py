import streamlit as st
from add_diary_entry import DiaryEntryHelper
from get_analysis import GetAnalysis

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
		# result_sentiment = get_analysis_object.get_sentiment_analysis(month)
		# st.write(result_money)
		# st.write(result_sentiment)
		result = diary_entry_helper.get_entry("November")
		st.write(result_money)