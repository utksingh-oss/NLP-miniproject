import spacy
from spacy.matcher import Matcher
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer



# for obtaining data from DB
from add_diary_entry import DiaryEntryHelper

diary_entry_helper = DiaryEntryHelper()

nlp = spacy.load("en_core_web_sm")

expenditure_terms = ['buy','transfer','spend','expense','invest','loan','loss','charge','debit','decrement','use','give','lend']
savings_terms = ['receive','gain','acquire','credit','borrowed']

# MATCHER FUNCTIONS ============================================================================================================

matcher = Matcher(nlp.vocab)
money_pattern = []

#making pattern of the form NUM .. NUM POBJ

for i in range(1,8):
	curr_pattern = []
	for j in range(i):
		curr_pattern.append({"POS":"NUM"})
	curr_pattern.append({"DEP":"pobj"})
	money_pattern.append(curr_pattern)

for i in range(1,8):
	curr_pattern = []
	curr_pattern.append({"DEP": "pobj"})
	for i in range(i):
		curr_pattern.append({"POS":"NUM"})
	money_pattern.append(curr_pattern)

money_pattern.append([{"DEP":"nmod"},{"POS":"NUM"}])
money_pattern.append([{"POS" : "NUM"},{"DEP":"nmod"}])

matcher.add("money", patterns = money_pattern)


#UTIL FUNCTIONS ===============================================================================================================
			
def get_children_text(txt):
  lst = {}
  
  lst[txt.text] = txt.idx
  
  for child in txt.children:
    rec_lst = get_children_text(child)
    lst.update(rec_lst)
  return lst

def sort_dict(mydict):
  marklist=list(mydict.items())
  l=len(mydict)
  for i in range(l-1):
      for j in range(i+1,l):
          if marklist[i][1]>marklist[j][1]:
              t=marklist[i]
              marklist[i]=marklist[j]
              marklist[j]=t
  sortdict=dict(marklist)
  return sortdict

# PART OF SPEECH TAGGING =======================================================================================================


## Utility Functions----------------------------

#GET EXPENDITURE 
def get_expenditure_table_1(text , date):
  doc = nlp(text)
  expenses = []
  for sent in doc.sents:
    # matcher_result = matcher(sent , as_spans = True)
    for token in sent:
      if token.lemma_ in expenditure_terms:
        #check if their is negation in sentence if so break current loop
        
        for child in token.children:
           curr_expense = {}
           if (child.pos_ == "NOUN" or child.pos_ == "PROPN") and child.dep_ == "dobj":

             curr_expense["spent on"] = child.text
             curr_expense["date"] = date
             list_of_string = get_children_text(token)
             list_of_string = sort_dict(list_of_string)
           
             temp = []
             for txt in list_of_string.keys():
               temp.append(txt)
             list_of_string = temp
             list_of_string = ' '.join(list_of_string)
             to_be_passed = nlp(list_of_string)
             result = matcher(to_be_passed, as_spans = True)
             if len(result) == 0:
               curr_expense = None
             else:
               max_string = ""
               for curr in result:
                 if len(curr) > len(max_string):
                   max_string = curr
               curr_expense["spent"] = max_string.text

             if(curr_expense == None): 
               continue
             else:
               expenses.append(curr_expense)
  print(expenses)
  return expenses

def get_expenditure_table_2(text , date):
  doc = nlp(text)
  expenses = []
  for sent in doc.sents:
    # matcher_result = matcher(sent, as_spans = True)
    for token in sent:
      if token.lemma_ in expenditure_terms:
        for child in token.children:
          for sub_child in child.children:
            if (sub_child.pos_ == "NOUN" or sub_child.pos_=="PROPN") and sub_child.dep_ == "pobj":
              
              curr_expense = {}
              curr_expense["spent on"] = sub_child.text
              curr_expense["date"] = date
              
         
              list_of_string = get_children_text(token)
              
              list_of_string = sort_dict(list_of_string)
              

              temp = []
              for txt in list_of_string.keys():
                temp.append(txt)
              list_of_string = temp
              list_of_string = ' '.join(list_of_string)
              to_be_passed = nlp(list_of_string)
              result = matcher(to_be_passed , as_spans = True)
              if len(result) == 0:
                curr_expense = None
              else:
                max_string = ""
                for curr in result:		
                  if len(curr) > len(max_string):
                    max_string = curr
                curr_expense["spent"] = max_string.text
                if(curr_expense == None):
                  continue
                else:
                  expenses.append(curr_expense)
  return expenses

def get_expenditure_table_3(text , date):
  doc = nlp(text)
  expenses = []
  spending_term = False
  for sent in doc.sents:
    for token in sent:
      if token.lemma_ in expenditure_terms:
        spending_term = True
    if not spending_term:
      continue
    curr_expense = {}
    matcher_result = matcher(sent , as_spans = True)
    max_string = ""
    for res in matcher_result:
      if len(res) > len(max_string):
        max_string = res
    curr_expense["spent"] = max_string.text
    curr_expense["spent on"] = "NA"
    curr_expense["date"] = date
    expenses.append(curr_expense)
  return expenses
      

def get_expenditure(text  , date):
  doc = nlp(text)
  total_expenses = []
  for sent in doc.sents:
    
    expenses = get_expenditure_table_1(sent.text , date)
    if len(expenses) == 0:
      expenses = get_expenditure_table_2(sent.text, date)
    if len(expenses) == 0:
      expenses = get_expenditure_table_3(sent.text, date)
      print(expenses)
    
    total_expenses.append(expenses)
  return total_expenses


# GET INCOME
def get_income_table_1(text , date):
  doc = nlp(text)
  income = []
  for sent in doc.sents:
    matcher_result = matcher(sent , as_spans = True)
    for token in sent:
      if token.lemma_ in savings_terms:
        #check if their is negation in sentence if so break current loop
        curr_income = {}
        for child in token.children:
           if (child.pos_ == "NOUN" or child.pos_ == "PROPN") and child.dep_ == "dobj":
             curr_income["received from"] = child.text
             curr_income["date"] = date
             list_of_string = get_children_text(token)
             list_of_string = sort_dict(list_of_string)
           
             temp = []
             for txt in list_of_string.keys():
               temp.append(txt)
             list_of_string = temp
             list_of_string = ' '.join(list_of_string)
             to_be_passed = nlp(list_of_string)
             result = matcher(to_be_passed, as_spans = True)
             if len(result) == 0:
               curr_income = None
             else:
               max_string = ""
               for curr in result:
                 if len(curr) > len(max_string):
                   max_string = curr
               curr_income["received"] = max_string.text

             if(curr_income == None): 
               continue
             else:
               income.append(curr_income)
  return income

def get_income_table_2(text , date):
  doc = nlp(text)
  income = []
  for sent in doc.sents:
    matcher_result = matcher(sent, as_spans = True)
    for token in sent:
      if token.lemma_ in savings_terms:
        curr_income = {}
        for child in token.children:
          for sub_child in child.children:
            if (sub_child.pos_ == "NOUN" or sub_child.pos_=="PROPN") and sub_child.dep_ == "pobj":
              curr_income["received from"] = sub_child.text
              curr_income["date"] = date
              list_of_string = get_children_text(token)
              list_of_string = sort_dict(list_of_string)

              temp = []
              for txt in list_of_string.keys():
                temp.append(txt)
              list_of_string = temp
              list_of_string = ' '.join(list_of_string)
              to_be_passed = nlp(list_of_string)
              result = matcher(to_be_passed , as_spans = True)
              if len(result) == 0:
                curr_income = None
              else:
                max_string = ""
                for curr in result:		
                  if len(curr) > len(max_string):
                    max_string = curr
                curr_income["received"] = max_string.text
                if(curr_income == None):
                  continue
                else:
                  income.append(curr_income)
  return income

def get_income_table_3(text , date):
  doc = nlp(text)
  income = []
  income_term = False
  for sent in doc.sents:
    for token in sent:
      if token.lemma_ in savings_terms:
        income_term = True
    if not income_term:
      continue
    curr_income = {}
    matcher_result = matcher(sent , as_spans = True)
    max_string = ""
    for res in matcher_result:
      if len(res) > len(max_string):
        max_string = res
    curr_income["received"] = max_string.text
    curr_income["date"] = date
    curr_income["received from"] = "NA"
    income.append(curr_income)
  return income
      
		

def get_income(text , date):
  doc = nlp(text)
  total_income = []
  for sent in doc.sents:
    print(sent)
    income = get_income_table_1(sent.text , date)
    if len(income) == 0 :
      income = get_income_table_2(sent.text , date)
      print("inside first if")
    if len(income) == 0:
      income = get_income_table_3(sent.text , date)
      print("inside second if")
    total_income.append(income)
  return total_income


#FINAL CLASS ============================================================================

class GetAnalysis:
	def __init__(self):
		pass

	def get_money_flow(self, month):
		entries = diary_entry_helper.get_entry(month)
		exp = []
		print("The entries for the month are : ",entries)
		for curr in entries:
			print("this is to be passed : ", curr[3])
			doc = nlp(curr[3])
			for sent in doc.sents:
				temp = get_expenditure(sent.text , curr[1])
				if len(temp)!=0:
					exp.append(temp)
		
		inc = []
		for curr in entries:
			print("this is to be passed : ", curr[3])
			doc = nlp(curr[3])
			for sent in doc.sents:
				temp = get_income(sent.text , curr[1])
				if len(temp)!= 0 :
					inc.append(temp)
		res = {}
		res["expenses"] = exp
		res["income"] = inc
		print(res)
		return res



