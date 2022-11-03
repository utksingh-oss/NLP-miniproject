import mysql.connector as connector
from datetime import date

class DiaryEntryHelper:
	def __init__(self):
		self.con = connector.connect(host = 'localhost', port = '3306', user = 'root' , password = '858684Arsh123!', database = 'nlpproject')
		query = 'create table if not exists diary_entry(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,entry_date DATE,title TEXT, details MEDIUMTEXT)'
		cur = self.con.cursor()
		cur.execute(query)
		print("Created")
	
	def insert_entry(self, date , title , details):
		print("date : ", date)
		print("title : ", title)
		print("details: ",details)
		query = "insert into diary_entry(entry_date, title , details) values('{}','{}','{}')".format(date , title , details)
		cur = self.con.cursor()
		cur.execute(query)
		self.con.commit()
		print("Inserted Successfully")
	
	def get_entry(self , month):
		query = "select * from diary_entry where monthname(entry_date) = '{}'".format(month)
		cur = self.con.cursor(buffered = True)
		cur.execute(query)
		res = []
		for row in cur:
			res.append(row)
		return res