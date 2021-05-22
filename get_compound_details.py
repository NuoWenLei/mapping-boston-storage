import requests, json
from bs4 import BeautifulSoup

HEADERS = {
	'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
}

def main():
	with open('detailed_buildings.json', 'r') as buildings_json:
		buildings = json.load(buildings_json)
	compound_link_set = set([(i['compound_name'], i['compound_link']) for i in buildings])
	print(compound_link_set)
	print(len(compound_link_set))
	compounds = []
	counter = 0
	for compound_name, link in compound_link_set:
		print(counter)
		print(link)
		counter += 1
		compound = {}
		try:
			compound['compound_name'] = compound_name
			compound['link'] = link
			r = requests.get(link, headers=HEADERS)
			soup = BeautifulSoup(r.text, 'html.parser')
			q = soup.find_all('div',class_="xiaoquDetailHeader")[0].find_all('div', class_="detailHeader fl")[0].find_all('div', class_='detailDesc')[0].text.split(')')[1].strip()
			info_divs = soup.find_all('div', class_='xiaoquDescribe fr')[0].find_all('div', class_='xiaoquInfoItem')

			compound['available_address'] = q

			compound['year_of_construction'] = int(info_divs[0].find_all('span', recursive=False)[1].text[:4])
			compound['building_type'] = (info_divs[1].find_all('span', recursive=False)[1].text)
			compound['management_company'] = (info_divs[3].find_all('span', recursive=False)[1].text)
			compound['developer_company'] = (info_divs[4].find_all('span', recursive=False)[1].text)
			compound['number_of_buildings'] = int(info_divs[5].find_all('span', recursive=False)[1].text[:-1])
			compound['number_of_rooms'] = int(info_divs[6].find_all('span', recursive=False)[1].text[:-1])
			url = f"http://api.map.baidu.com/place/v2/search?query={q}&region= 上海&output=json&ak=Z7igo805MpAY3f06RyRgmEmDITzNZqsr"
			baidu_res = requests.get(url)
			res_obj = json.loads(baidu_res.text)
			compound_info = res_obj['results'][0]
			for k in compound_info.keys():
				compound[k] = compound_info[k]
			compounds.append(compound)
		except Exception as e:
			print(e)
	with open('detailed_compounds.json', 'w') as compounds_json:
		json.dump(compounds, compounds_json, ensure_ascii=False)

if __name__ == '__main__':
	main()