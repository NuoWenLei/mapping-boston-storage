import json, numpy as np, sys, copy

def combine_compounds(fn_1, fn_2):
	with open(f'{fn_1}.json', 'r') as comp_json_1:
		compounds_1 = json.load(comp_json_1)
	
	with open(f'{fn_2}.json', 'r') as comp_json_2:
		compounds_2 = json.load(comp_json_2)

	compounds_joined = compounds_1 + compounds_2

	detailed_compounds_joined = full_rank_attr(compounds_joined)

	with open(f'joined_{fn_1}_{fn_2}.json', 'w') as comp_json_joined:
		json.dump(detailed_compounds_joined, comp_json_joined)
	
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

def main():
	fn_1 = sys.argv[1]
	fn_2 = sys.argv[2]
	combine_compounds(fn_1, fn_2)


if __name__ == '__main__':
	main()