from selenium.webdriver import Safari
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json, requests, time

HEADERS = {
	'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
}

def search_page(objects, driver):
	base_url = 'https://sh.lianjia.com/ershoufang/'
	results = []
	counter = 0
	bad_counter = 0
	curr_title = ""
	for obj in objects:
		try:
			new_obj = obj.copy()
			print(counter)
			driver.get(base_url)
			# WebDriverWait(driver, 10).until_not(EC.title_is(curr_title))
			counter += 1
			searchbar = driver.find_element_by_id('searchInput')
			searchbar.send_keys(new_obj['name'])
			curr_title = driver.title
			searchbar.send_keys(Keys.ENTER)
			WebDriverWait(driver, 5).until_not(EC.title_is(curr_title))
			
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight/4);")
			time.sleep(0.5)
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
			time.sleep(0.5)
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight*3/4);")
			time.sleep(0.5)
			
			
			result_anchor = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//ul[@class="sellListContent LOGCLICKDATA"]/li/a')))
			new_url = result_anchor.get_attribute('href')
			print(new_url)
			driver.get(new_url)

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
	return results, bad_counter

def main():
	with open('parsed_building.json', 'r') as json_in:
		buildings = json.load(json_in)
	driver = Safari()
	detailed_buildings, bad_counter = search_page(buildings, driver)
	print(f"Total Skipped: {bad_counter}")
	# json_str = json.dumps(all_buildings).encode('utf-8')
	with open('detailed_buildings.json', 'w') as json_fl:
		json.dump(detailed_buildings, json_fl, ensure_ascii=False)



if __name__ == '__main__':
	main()