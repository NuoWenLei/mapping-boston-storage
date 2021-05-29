from bs4 import BeautifulSoup
import requests, json

def parse_html(html):
	soup = BeautifulSoup(html, 'html.parser')
	body = soup.find('body')
	lis = []
	for ul in body.find_all('ul', recursive=False):
		lis.extend(ul.find_all('li', recursive=False))
	restaurants = []
	bad_counter = 0
	counter = 0
	for li in lis:
		counter += 1
		step = 0
		try:
			print(counter)
			obj = {}
			info_div = li.find_all('div', class_='info')[0]
			step = 1
			obj['restaurant_name'] = info_div.find_all('h4')[0].text
			step = 2
			point_txt = info_div.find_all('a')[0].find_all('p')[0].text
			step = 3
			obj['consumer_score'] = float(point_txt.split('分')[0].strip())
			step = 4
			obj['num_comments'] = int(point_txt.split('分')[1].strip()[:-3])
			step = 5
			desc_txt = info_div.find_all('a')[0].find_all('p', class_='desc')[0].text
			step = 6
			obj['website_address'] = desc_txt.split('人均')[0].strip()
			step = 7
			obj['avg_spending'] = float(desc_txt.split('人均')[1].strip()[1:].strip())
			step = 8
			url = f"http://api.map.baidu.com/place/v2/search?query={obj['restaurant_name']}&region= 上海&output=json&ak=Z7igo805MpAY3f06RyRgmEmDITzNZqsr"
			baidu_res = requests.get(url)
			res_obj = json.loads(baidu_res.text)
			restaurant_info = res_obj['results'][0]
			for k in restaurant_info.keys():
				obj[k] = restaurant_info[k]
			restaurants.append(obj)
		except Exception as e:
			bad_counter += 1
			print(step)
			print(bad_counter)
			print(e)
	return restaurants
	
def main():
	with open('restaurant_html.txt', 'r') as rest_txt:
		restaurant_html = rest_txt.read()
	detailed_restaurants = parse_html(restaurant_html)
	with open('detailed_restaurants.json', 'w') as rest_json:
		json.dump(detailed_restaurants, rest_json, ensure_ascii=False)


if __name__ == '__main__':
	main()
