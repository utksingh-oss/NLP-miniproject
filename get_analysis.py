import spacy
from spacy.matcher import Matcher
from vaderSentiment.vaderSentiment import SentimentIntesityAnalyzer


# for obtaining data from DB
from add_diary_entry import DiaryEntryHelper

diary_entry_helper = DiaryEntryHelper()

nlp = spacy.load("en_core_web_sm")

expenditur_terms = ['buy','transfer','spend','expense','invest','loan','loss','charge','debit','decrement','use','give','lend']
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

# PART OF SPEECH TAGGING =======================================================================================================


## Utility Functions----------------------------
def get_children_text(txt):
	lst = {}
	lst[txt.text] = txt.idx
	for child in txt.children:
		rec_lst = get_children_text(child)
		lst.update(rec_lst)
	return lst

def sort_dict(myDict):
	marklist = list(myDict.items())
	l = len(myDict)
	#performing bubble sort on list 
	for i in range(l - 1):
		for j in range(i + 1 , l):
			if marklist[i][1] > marklist[i+1][1]:
				t = marklist[i]
				marklist[i] = marklist[j]
				marklist[j] = t
	sortdict = dict(marklist)
	return sortdict



#Extracting Expenditure for Sentence type : 1
#"I bought a house for seventy thousand dollars."
def get_moneyflow_table_1(text , flow , list_of_terms):
	doc = nlp(text)
	if flow == 'outwards':
		var_1 = "spent"
		var_2 = "spent-on"
	elif flow == 'inwards':
		var_1 = "received"
		var_2 = "received-from"
	
	total_flow = []
	for sent in doc.sents:
		for token in sent:
			if token.lemma_ in list_of_terms:
				curr_flow = {}
				for child in token.children:
					if child.pos_ == "NOUN" and child.dep_ =="dobj":
						curr_flow[var_2] = child
						list_of_string = get_children_text(child)
						list_of_string = sort_dict(list_of_string)

						temp = []
						for txt in list_of_string.keys():
							temp.append(txt)
						list_of_string = temp
						list_of_string = ' '.join(list_of_string)
						to_be_passed = nlp(list_of_string)
						result = matcher(to_be_passed , as_spans = True)
						if len(result) == 0:
							curr_flow = None
							continue
						else:
							max_string = ""
							for curr in result:
								if len(curr) > len(max_string):
									max_string = curr
							curr_flow[var_1] = max_string

						curr_flow.append(curr_flow)
	return total_flow

#Extracting Expenditure for Sentence type : 2
#"I spent fourty thousand dollars on a house."
def get_moneyflow_table_2(text, flow, list_of_terms):
	doc = nlp(text)
	if flow == 'outwards':
		var_1 = "spent"
		var_2 = "spent-on"
	elif flow == 'inwards':
		var_1 = "received"
		var_2 = "received-from"
	total_flow = []
	for sent in doc.sents:
		for token in sent:
			if token.lemma_ in list_of_terms:
				curr_flow = {}
				for child in token.children:
					for sub_child in child.children:
						if sub_child.pos_ == "NOUN" and sub_child == "pobj":
							curr_flow[var_2] = sub_child
							list_of_string = get_children_text(child)
							list_of_string = sort_dict(list_of_string)

							temp = []
							for txt in list_of_string.keys():
								temp.append(txt)
							list_of_string = temp
							list_of_string = ' '.join(list_of_string)
							to_be_passed = nlp(list_of_string)
							result = matcher(to_be_passed , as_spans = True)
							if len(result) == 0:
								curr_flow = None
								continue
							else:
								max_string = ""
								for curr in result:
									if len(curr) > len(max_string):
										max_string = curr
								curr_flow[var_1] = max_string
							total_flow.append(curr_flow)
	return total_flow

def get_moneyflow_table_3(text):
	doc = nlp(text)
	total_flow= []
	flow_term_found = False
	flow_term = ""
	for sent in doc.sents:
		for token in sent:
			if token.lemma_ in expenditure_terms:
				flow_term_found = True
				flow_term = 'outwards'

	for sent in doc.sents:
		for token in sent:
			if token.lemma_ in savings_terms:
				flow_terms_found = False
				flow_term = 'inwards'

	if not flow_term_found:
		return None

	if flow_term == 'outwards':
		var_1 = "spent"
		var_2 = "spent-on"
	elif flow_term == 'inwards':
		var_1 = "received"
		var_2 = "received-from"


	for sent in doc.sents:	 
		curr_flow = []
		matcher_result = matcher(sent , as_spans = True)
		max_string = ""
		for res in matcher_result :
			if len(res) > len(max_string):
				max_string = res
		curr_flow[var_1] = max_string
		curr_flow[var_2] = None
		total_flow.append(curr_flow)
	return curr_flow

def get_moneyFlow(txt):
	doc = nlp(txt)
	lst = []
	for sent in doc.sents:
		curr_lst = get_moneyflow_table_1(sent, 'inwards', savings_terms)
		if curr_lst == None:
			curr_lst = get_moneyflow_table_1(sent , 'outwards' , expenditure_terms)

		if curr_lst == None:
			curr_lst = get_moneyflow_table_2(sent , 'inwards', savings_terms)

		if curr_lst == None:
			curr_lst = get_moneyflow_table_2(sent , 'outwards', expenditure_terms)

		if curr_lst == None:
			curr_lst = get_moneyflow_table_3(sent)

		if curr_lst == None:
			continue
		else:
			lst.append(curr_lst)
	return lst


#FINAL CLASS ============================================================================

class GetAnalysis:
	def __init__(self):
		pass

	def get_money_flow(self, month):
		entries = diary_entry_helper.get_entry(month)
		res = []
		for curr in entries:
			temp = get_moneyFlow(curr)
			res.append(temp)
		return res

	def 

