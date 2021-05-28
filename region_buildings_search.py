from selenium.webdriver import Safari
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json, requests, time, copy, numpy as np, sys


"""
Args: link_of_site, file_version
Returns: detailed_compounds_v?.json, detailed_buildings_v?.json

Steps:
- parse all building links from site
- search building page
- search compound page
- add more detailed compounds data
"""

HEADERS = {
	'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
}

def parse_lianjia_website(link, driver):
	"""
	Args: link_of_site, webdriver
	Returns: all_buildings (list of dict)
	"""
	results = []
	driver.get(link)
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight*3/4);")
	next_page_anchor = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//a[text()="下一页"]')))
	total_pages = int(next_page_anchor.parent.find_elements_by_xpath('//a[@data-page]')[-2].get_attribute('data-page'))
	print(total_pages)
	for p in range(total_pages+1):
		if p == 0:
			continue
		driver.get(f"{link}pg{p}")
		time.sleep(0.5)
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
		time.sleep(0.5)
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight*3/4);")
		li_items = driver.find_elements_by_xpath('//ul[@class="sellListContent"]/li')
		bad_counter = 0
		for li in li_items:
			try:
				obj = {}
				obj['name'] = li.find_element_by_xpath('./div/div[@class="title"]/a').text
				obj['link'] = li.find_element_by_xpath('./a').get_attribute('href')
				price_info = li.find_element_by_xpath('./div/div[@class="priceInfo"]')
				obj['total_price'] = int(price_info.find_element_by_xpath('./div[@class="totalPrice"]/span').text)*10000.0
				obj['unit_price'] = int(price_info.find_element_by_xpath('./div[@class="unitPrice"]/span').text[2:-4])
				results.append(obj)
			except Exception as e:
				bad_counter += 1
		print(f'got page {p} with {bad_counter} fails')
	return results





def search_building_page(objects, driver):
	"""
	Args: buildings, webdriver
	Returns: detailed_buildings
	"""

	results = []
	counter = 0
	bad_counter = 0
	for obj in objects:
		try:
			new_obj = obj.copy()
			print(counter)
			driver.get(obj['link'])
			# WebDriverWait(driver, 10).until_not(EC.title_is(curr_title))
			counter += 1

			space_tag = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@class="content"]/div[@class="houseInfo"]/div[@class="area"]/div[1]')))
			new_obj['area(sq_meters)'] = float(space_tag.text[:-2])

			year_tag = driver.find_element_by_xpath('//div[@class="houseInfo"]/div[@class="area"]/div[2]')
			new_obj['year_of_construction'] = int(year_tag.text[:4])

			floor_tag = driver.find_element_by_xpath('//div[@class="houseInfo"]/div[@class="room"]/div[2]')
			new_obj['floors_of_building'] = int(floor_tag.text.split('/')[1][1:-1])

			compound_tag = driver.find_element_by_xpath('//div[@class="aroundInfo"]/div[@class="communityName"]/a[1]')
			new_obj['compound_name'] = compound_tag.text
			new_obj['compound_link'] = compound_tag.get_attribute('href')

			floor_plan_tag = driver.find_element_by_xpath('//div[@class="houseInfo"]/div[@class="room"]/div[1]')
			new_obj['floor_plan'] = floor_plan_tag.text

			type_tag = driver.find_element_by_xpath('//div[@class="transaction"]/div[@class="content"]/ul/li[4]/span[2]')
			new_obj['room_type'] = type_tag.text

			results.append(new_obj)
		except Exception as e:
			print(type(e))
			print(e)
			bad_counter += 1
	driver.quit()
	return results, bad_counter

def search_compound_page(buildings):
	"""
	Args: detailed_buildings
	Returns: detailed_compounds
	"""
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
	
	return compounds

def get_detailed_compounds(compounds, detailed_buildings):
	"""
	Args: compounds_data, detailed_buildings
	Returns: detailed_compounds_data
	"""
	updated_compounds_v1 = []

	for compound in compounds:
		updated_compound = compound.copy()
		updated_compound['sum_of_prices($/space)'] = 0
		updated_compound['sum_of_prices(total)'] = 0
		updated_compound['sum_of_area(sq_meters)'] = 0
		updated_compound['sum_of_floors'] = 0
		updated_compound['units_on_sale'] = 0
		for building in detailed_buildings:
			if compound['compound_name'] == building['compound_name']:
				updated_compound['sum_of_prices($/space)'] += building['unit_price']
				updated_compound['sum_of_prices(total)'] += building['total_price']
				updated_compound['sum_of_area(sq_meters)'] += building['area(sq_meters)']
				updated_compound['sum_of_floors'] += building['floors_of_building']
				updated_compound['units_on_sale'] += 1
		updated_compounds_v1.append(updated_compound)

	for updated_compound in updated_compounds_v1:
		updated_compound['avg_prices($/space)'] = updated_compound['sum_of_prices($/space)'] / updated_compound['units_on_sale']
		updated_compound['avg_prices(total)'] = updated_compound['sum_of_prices(total)'] / updated_compound['units_on_sale']
		updated_compound['avg_area(sq_meters)'] = updated_compound['sum_of_area(sq_meters)'] / updated_compound['units_on_sale']
		updated_compound['avg_floors'] = updated_compound['sum_of_floors'] / updated_compound['units_on_sale']
	return full_rank_attr(updated_compounds_v1)


def full_rank_attr(updated_compounds_v1):
	for k in ['year_of_construction', 'number_of_buildings', 'number_of_rooms', 'avg_prices($/space)', 'avg_prices(total)', 'avg_area(sq_meters)', 'avg_floors']:
		updated_compounds_v1 = add_rank_attr(updated_compounds_v1, k)
		updated_compounds_v1 = label_outliers(updated_compounds_v1, k)
		updated_compounds_v1 = adjust_rank_attr_by_outliers(updated_compounds_v1, k)

	return updated_compounds_v1
	

def add_rank_attr(compounds, key):
	"""
	Args: detailed_compounds, keys
	Returns: ranked_compounds
	"""
	new_compounds = copy.deepcopy(compounds)
	selected_attr = np.array([i[key] for i in compounds])
	attr_max = selected_attr.max()
	attr_min = selected_attr.min()
	lin_range = np.linspace(attr_min, attr_max, 50)
	print(len(lin_range))
	for j,a in enumerate(selected_attr):
		for i,r in enumerate(lin_range):
			if a < r:
				new_compounds[j][f'{key}_ranking'] = i - 1
				break
		else:
			new_compounds[j][f'{key}_ranking'] = len(lin_range) - 1
	return new_compounds

def label_outliers(data, k, m=2):
	new_data = []
	selected_data = np.array([i[k] for i in data])
	mask_arr = (abs(selected_data - np.mean(selected_data)) < (m * np.std(selected_data)))
	for mask, c in zip(mask_arr, data):
		new_obj = c.copy()
		new_obj[f'not_{k}_outlier'] = 1 if mask else 0
		new_data.append(new_obj)
	return new_data

def adjust_rank_attr_by_outliers(compounds, key):
	new_compounds = copy.deepcopy(compounds)
	index_arr = np.array([i for i,obj in enumerate(compounds) if obj[f'not_{key}_outlier'] == 1])
	selected_attr = np.array([i[key] for i in compounds if i[f'not_{key}_outlier'] == 1])
	attr_max = selected_attr.max()
	attr_min = selected_attr.min()
	lin_range = np.linspace(attr_min, attr_max, 50)
	for j,a in zip(index_arr, selected_attr):
		for i,r in enumerate(lin_range):
			if a < r:
				new_compounds[j][f'{key}_ranking_adjusted'] = i - 1
				break
		else:
			new_compounds[j][f'{key}_ranking_adjusted'] = len(lin_range) - 1
	return new_compounds

def main(region_link, version_name):

	print('at stage 1')

	driver = Safari()

	all_buildings = parse_lianjia_website(region_link, driver)

	print('at stage 2')

	# Create driver and pass buildings data to stage 2
	

	detailed_buildings, bad_counter = search_building_page(all_buildings, driver)

	print(f"Total Skipped: {bad_counter}")

	print('at stage 3')

	# Store stage 2 data and pass detailed buildings data to stage 3
	with open(f'detailed_buildings_{version_name}.json', 'w') as buildings_json:
		json.dump(detailed_buildings, buildings_json, ensure_ascii=False)
	
	all_compounds = search_compound_page(detailed_buildings)

	print('at stage 4')

	# Store stage 3 data and pass compounds data to stage 4
	with open(f'all_compounds_{version_name}.json', 'w') as compounds_json:
		json.dump(all_compounds, compounds_json, ensure_ascii=False)

	detailed_compounds = get_detailed_compounds(all_compounds, detailed_buildings)

	print('FINISHED')

	# Store final result data
	with open(f'detailed_compounds_{version_name}.json', 'w') as detailed_compounds_json:
		json.dump(detailed_compounds, detailed_compounds_json, ensure_ascii=False)
	
if __name__=='__main__':
	link_of_region = sys.argv[1]
	version_name = sys.argv[2]
	print(link_of_region)
	print(version_name)
	main(link_of_region, version_name)