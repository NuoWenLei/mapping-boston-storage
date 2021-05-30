from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
import requests, datetime, json, numpy as np

HEADERS = {
	'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
}

def find_records(link):
	try:
		r = requests.get(link, headers=HEADERS)
		r.raise_for_status()
		soup = BeautifulSoup(r.text, 'html.parser')
		href = soup.find_all('div', class_='frameDealList')[0].find_next_sibling('a')['href']
		records = []
		r = requests.get(href, headers=HEADERS)
		soup = BeautifulSoup(r.text, 'html.parser')
		ul = soup.find_all('ul', class_='listContent')[0]
		for li in ul.find_all('li', recursive=False):
			obj = {}
			year, month, day = li.find_all('div', class_='dealDate')[0].text.strip().split('.')
			obj['transaction_date'] = datetime.date(int(year), int(month), int(day))
			obj['unit_price'] = float(li.find_all('div', class_='unitPrice')[0].find('span').text.strip())
			records.append(obj)
		
		num_pages = int(json.loads(soup.find_all('div', class_='page-box house-lst-page-box')[0]['page-data'])['totalPage'])

		if len(records) < 10:
			return "too little records"
		
		if num_pages > 1:
			r = requests.get(f"{href.split('chengjiao/')[0]}chengjiao/pg{num_pages}{href.split('chengjiao/')[1]}", headers=HEADERS)
			soup = BeautifulSoup(r.text, 'html.parser')
			ul = soup.find_all('ul', class_='listContent')[0]
			for li in ul.find_all('li', recursive=False):
				obj = {}
				year, month, day = li.find_all('div', class_='dealDate')[0].text.strip().split('.')
				obj['transaction_date'] = datetime.date(int(year), int(month), int(day))
				obj['unit_price'] = float(li.find_all('div', class_='unitPrice')[0].find('span').text.strip())
				records.append(obj)
		
	
		difference = relativedelta(records[-2]['transaction_date'], records[1]['transaction_date'])
		year_diff = difference.years
		if difference.months >= 10:
			year_diff += 1
		early_sum = (sum(records[i]['unit_price'] for i in [0,1,2])/3.0)
		late_sum = (sum(records[i]['unit_price'] for i in [-1, -2, -3])/3.0)
		avg_percent_increase_per_year = ((late_sum - early_sum)/early_sum)/float(year_diff)
		return avg_percent_increase_per_year * 100.0

	except Exception as e:
		print('error:')
		print(e)
		return 'ended with error'

def main():
	with open('detailed_compounds_changning.json', 'r') as changning_json:
		compounds = json.load(changning_json)
	
	for i,c in enumerate(compounds):
		c['avg_price_increase_per_year'] = find_records(c['link'])
		if i % 10 == 0:
			print(i)

	with open('detailed_compounds_changning_v2.json', 'w') as chang_v2_json:
		json.dump(compounds, chang_v2_json, ensure_ascii=False)
	print('success!')

if __name__ == '__main__':
	main()

		
		
