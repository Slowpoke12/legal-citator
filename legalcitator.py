#won't detect errors in small caps

import mammoth #https://github.com/mwilliamson/python-mammoth
from bs4 import BeautifulSoup #https://www.crummy.com/software/BeautifulSoup/bs4/doc/
import re #https://docs.python.org/2/howto/regex.html
import requests
import urllib2 #from https://stackoverflow.com/questions/7395789/replacing-a-weird-single-quote-with-blank-string-in-python
thirteen_list = set() #gloabl variable that will be set of valid abbreviations for Table 13
import sys

def main():
	"""load Legal Citation guide table 13 abbreviations, convert document to html, run check on footnotes"""
	load_table() #see attribution for table 13 attribution
	with open("sample.docx", "rb") as docx_file: 
		result = mammoth.convert_to_html(docx_file)
		html = result.value # The generated HTML
		messages = result.messages # Any messages, such as warnings during conversion; this and the above two lines of code and comments come from https://github.com/mwilliamson/python-mammoth
		soup = BeautifulSoup(html, 'html.parser') 
		footnotes = soup.find_all('li') 
		print ("Your document contains the following errors:")
		for note in footnotes:
			check(note)

def load_table(table_13 ="table13.txt"):
	"""load table 13 for periocial abbreviations"""

	e = open(table_13, "r")
	for line in e:
		line = line.strip()
		thirteen_list.add(line)

def check(note):
	"""perform existing checks on each footnote"""

	#if note contains wrongly formatted single or double quotes, print footnote number and error type
	bad_apost(note)
	#If "see, e.g.," signal incorrectly formatted, print footnote number and error type
	see_eg(note)
	#if journal citations are incorrectly abbreviated, print footnote number and error type
	abbrevTable13(note)

def bad_apost(note):
	"""looks for instances in footnotes of either " or ' marks, which should be curved, and return error"""
	straight_apost = re.findall("'", str(note)) 
  	if straight_apost != []:
  		print note["id"], "straight apostraphe: {}" .format(straight_apost) 

def see_eg(note):
	"""for each footnote, check if an instance of "see, e.g.," exists; if so, check if correct formatting exists; if so return True.  This program contains a bug I attempted but ran out of time to solve"""
	seegs = re.search("(<em>)?(</em>)?[Ss](<em>)?(</em>)?e(<em>)?(</em>)?e(<em>)?(</em>)?,?(<em>)?(</em>)? e(<em>)?(</em>)?.?(<em>)?(</em>)?g.?(<em>)?(</em>)?.?(<em>)?(</em>)?", str(note))
	if seegs == None:
		return True
	elif re.search("<em>[Ss]ee, e\.g\.</em>,", seegs.group(0)):
		sys.stdout.write('')
	else:
		print note["id"], "see, e.g., formatting error"

def abbrevTable13(note):
	"""for each footnote, check each possible abbreviations for match in table 13.  If no match, check broader cite in an open-source case database.  If still no match, return error"""
	
	#find all matches for each footnote that take the format , <number> [...] <number>.  (This format is common in legal citations, for example: 52 Stan. L. Rev. 1373 or 717 F.Supp.2d 9651.)
	tabl13 = re.findall(", [0-9]+ .{1,30}? [0-9]+", str(note))
	for possible_cite in tabl13:
		#convert each match such that "&" is not encoded "&amp;"
		possible_cite = note_convert(possible_cite)
		courtListener_cite = re.split("^,\s", possible_cite) #courtListener_cite will be the whole citation, which can be fed into the to the open-source case database, CourtListener.
		
		#remove extra numbers and any outer commas from the citation to have only core citation (for example: 52 Stan. L. Rev. 1373 => Stan. L. Rev.). Process requires two steps.
		half_cut = re.split("^, [0-9]+ ", possible_cite)
		payload = re.split(",? ?[0-9]+,?$", half_cut[1])

		#check if core citation in lists; if not, check if larger citation generates a match in CourtListener.  Otherwise, return False and notify editor of mistake.
		if payload[0] not in thirteen_list:
			if check_page(courtListener_cite) is False:
				print note["id"], "table 13 abbreviation error for {}" .format(payload[0])

def note_convert(str):
	"""convert '&amp; to &'. Code from https://stackoverflow.com/questions/784586/convert-special-characters-to-html-in-javascript"""
  	str = str.replace("&amp;", "&")
  	str = str.replace("&gt;", "<")
  	str = str.replace("&lt;", ">")
  	str = convert_apostr(str)
  	return str

def check_page(courtListener_cite):
	r = requests.get('https://www.courtlistener.com/?q=&type=o&order_by=score+desc&stat_Precedential=on&citation={}+' .format(courtListener_cite))
	if "1 Opinion" in r.text:
		return True
	else:
		return False

def convert_apostr(str):
	#https://stackoverflow.com/questions/13093727/how-to-replace-unicode-characters-in-string-with-something-else-python
	a = str.decode("utf-8").replace(u"\u2019", "'").encode("utf-8")
	return a

if __name__ == "__main__":
	main()
