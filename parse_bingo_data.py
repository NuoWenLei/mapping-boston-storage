from bs4 import BeautifulSoup
import json

def parse_page(html):
	soup = BeautifulSoup(html, 'html.parser')
	r_batch = []
	for li in soup.find_all('li'):
		obj = {}
		obj['name'] = li.find_all('h6')[0].find_all('a')[0].text
		score_div = li.find_all('div', class_="scr-remark")[0]
		score_span = score_div.find_all('span')[0]['title']
		obj['score_class'] = score_span
		loc_div, tag_div = li.find_all('div', class_="scr-tag")
		obj['location'] = loc_div.find_all('a')[0].text
		obj['tag'] = tag_div.find_all('a')[0].text
		r_batch.append(obj)
	return r_batch

def main():
	# txt = ""
	with open('restaurants.txt', 'r') as restaurant_txt:
		txt_decoded = restaurant_txt.read()
	# txt_decoded = txt.encode('utf-8').decode('utf-8')
	pages = txt_decoded.split('ifrickenlovechickenwings')
	all_restaurants = []
	for p in pages:
		res = parse_page(p)
		all_restaurants.extend(res)
	json_str = json.dumps(all_restaurants).encode('utf-8')
	with open('parsed_restaurants.json', 'w') as restaurant_json:
		# restaurant_json.write(json_str)
		json.dump(all_restaurants, restaurant_json, ensure_ascii=False)



if __name__ == '__main__':
	main()