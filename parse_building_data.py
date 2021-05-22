from bs4 import BeautifulSoup
import json

def parse_page(html):
	soup = BeautifulSoup(html, 'html.parser')
	ul = soup.find_all('ul')[0]
	results = []
	for li in ul.find_all('li'):
		step = 0
		try:
			obj = {}
			obj['name'] = li.find_all('span', class_='name')[0].text
			step = 1
			total_price_str = li.find_all('span', class_='total-price')[0].text.replace(',', '')
			total_price = 0
			if '万' in total_price_str:
				total_price = int(total_price_str.strip('万'))*10000
			else:
				total_price = int(total_price)
			obj['total_price'] = total_price

			step = 2
			unit_price_str = li.find_all('span', class_='unit-price')[0].text.replace(',', '')[:-3]
			obj['unit_price'] = int(unit_price_str)
			results.append(obj)
		except Exception as e:
			print(f'failed at step {step} with error {str(e)}')
		
	return results

def main():
	with open('building_html.txt', 'r') as txt:
		txt_decoded = txt.read()
	all_buildings = parse_page(txt_decoded)
	# json_str = json.dumps(all_buildings).encode('utf-8')
	with open('parsed_building.json', 'w') as json_fl:
		json.dump(all_buildings, json_fl, ensure_ascii=False)



if __name__ == '__main__':
	main()