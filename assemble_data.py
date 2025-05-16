
import pandas as pd
import polars as pl 
import numpy as np


meat_types = ['beef', 'chicken', 'pork', 'pig', 'lamb', 'bison', 'duck', 'turkey',
	 'goat', 'rabbit', 'venison', 'goose', 'veal', 'fish']
	
	
rasff_recalls = pd.read_csv("rasff_notification_table.csv")
rasff_recalls.columns = [
	'case_date', 'reference', 'notif_country', 'origin_country',
       'product', 'product_category', 'hazard_substance', 'hazard_category']
rasff_recalls['case_date'] = pd.to_datetime(rasff_recalls['case_date'], unit='ms')

usda_recalls = pd.read_parquet("usda_recalls.parquet")
usda_recalls['recall_date'] = pd.to_datetime(usda_recalls['recall_date'])

usda_recalls = usda_recalls.groupby('recall_number').first().reset_index()
usda_recalls['recall_date'] = pd.to_datetime(usda_recalls['recall_date'])


for type in meat_types:
	rasff_recalls[type] = (rasff_recalls['product'].str.contains(type, case=False) | rasff_recalls['product_category'].str.contains(type, case=False)) * 1
	usda_recalls[type] = (usda_recalls['title'].str.contains(type, case=False) | usda_recalls['product_items'].str.contains(type, case=False) | usda_recalls['summary'].str.contains(type, case=False)) *1

rasff_recalls['meat'] = (rasff_recalls['product'].str.contains('meat', case=False) | rasff_recalls['product_category'].str.contains('meat', case=False)) * 1
usda_recalls['meat'] = (usda_recalls['title'].str.contains('meat', case=False) | usda_recalls['product_items'].str.contains('meat', case=False) | usda_recalls['summary'].str.contains('meat', case=False)) *1

rasff_recalls['notif_country_fixed'] = rasff_recalls['notif_country'].str.replace(r'\s*\(.*?\)', '', regex=True)



purchases = pd.read_csv("purchases.csv")
purchases['date'] = pd.to_datetime(purchases['date'])

purchases['year'] = purchases['date'].dt.year
purchases['month'] = purchases['date'].dt.month
purchases['quarter'] = purchases['date'].dt.quarter

targets = pd.read_excel("Template_Results_250303.xlsx")	
targets['target'] = 1	
targets['Brand Name'] = targets['Brand Name'].str.strip()
targets['Country'] = targets['Country'].str.strip()


	
purchases = purchases.merge(
	targets[['Brand Name', 'Country', 'Brand Number', 'target']].rename(
		{'Brand Name': 'brand', 'Country': 'country', 'Brand Number': 'brand_num'}, axis=1).dropna(),
	how = 'left', on = ['country', 'brand'])

purchases['target'] = purchases['target'].fillna(0)
purchases['brand_num'] = purchases['brand_num'].fillna(0)

purchases['brand_gr'] = purchases['brand'] * (purchases['target']==1)
purchases.loc[purchases['target']==0, 'brand_gr'] = 'ALL_OTHER'



agged = purchases.groupby(['country', 'brand_gr', 'brand_num', 'year', 'month']).agg(
	total_unit_sales = ('total_unit_sales','sum'),
	total_value_sales = ('total_value_sales','sum'),
	total_volume_sales = ('total_volume_sales','sum')).reset_index()


usda_recalls['year'] = usda_recalls['recall_date'].dt.year
usda_recalls['month'] = usda_recalls['recall_date'].dt.month
usda_recalls['quarter'] = usda_recalls['recall_date'].dt.quarter

rasff_recalls['year'] = rasff_recalls['case_date'].dt.year
rasff_recalls['month'] = rasff_recalls['case_date'].dt.month
rasff_recalls['quarter'] = rasff_recalls['case_date'].dt.quarter



all_recalls = pd.concat([
	usda_recalls[(usda_recalls['recall_type'] == 'Closed Recall') & 
		(usda_recalls['recall_reason'].str.contains("Product Contamination"))][[
		'recall_date', 'beef', 'chicken', 'pork', 'pig',
		   'lamb', 'bison', 'duck', 'turkey', 'goat', 'rabbit', 'venison', 'goose',
		   'veal', 'fish']].assign(notif_country_fixed = 'United States'),		
	rasff_recalls[
		((rasff_recalls['hazard_category'].str.lower().str.contains("micro-organisms")) |
		(rasff_recalls['hazard_category'].str.lower().str.contains("contaminants")) |
		(rasff_recalls['hazard_category'].str.lower().str.contains("mycotoxins")) |
		(rasff_recalls['hazard_category'].str.lower().str.contains("residues")) |
		(rasff_recalls['hazard_category'].str.lower().str.contains("composition")) |
		(rasff_recalls['hazard_category'].str.lower().str.contains("toxins")) |
		(rasff_recalls['hazard_category'].str.lower().str.contains("pollutants")) |
		(rasff_recalls['hazard_category'].str.lower().str.contains("foreign bodies")) |
		(rasff_recalls['hazard_category'].str.lower().str.contains("metals"))) &
		(rasff_recalls['meat'] == 1) &
		(rasff_recalls['product_category'] != 'Pet food')][[
		'case_date', 'beef',
		   'chicken', 'pork', 'pig', 'lamb', 'bison', 'duck', 'turkey', 'goat',
		   'rabbit', 'venison', 'goose', 'veal', 'fish', 'notif_country_fixed']].rename({
		   	'case_date': 'recall_date'}, axis=1)])
		

purchases['age'] = purchases['age'].astype(str)

# switching to polars to do the non-equi join since the cross join is huge
purchases_pl = pl.DataFrame(purchases.reset_index())
all_recalls = pl.DataFrame(all_recalls)
	
purchases_merged = purchases_pl.join_where(all_recalls,
	(pl.col('country') == pl.col('notif_country_fixed')) & (
		(pl.col("date") > pl.col('recall_date')) & 
			(pl.col("date") <= pl.col('recall_date') + pd.Timedelta(days=7))))

treatments_7days = purchases_merged.group_by(['index']).agg(
	pl.col("beef").max(),
	pl.col("chicken").max(),
	pl.col("pork").max(),
	pl.col("pig").max(),
	pl.col("lamb").max(),
	pl.col("bison").max(),
	pl.col("duck").max(),
	pl.col("turkey").max(),
	pl.col("goat").max(),
	pl.col("rabbit").max(),
	pl.col("venison").max(),
	pl.col("goose").max(),
	pl.col("veal").max(),
	pl.col("fish").max())
	
purchases_merged = purchases_pl.join_where(all_recalls,
	(pl.col('country') == pl.col('notif_country_fixed')) & (
		(pl.col("date") > pl.col('recall_date')) & 
			(pl.col("date") <= pl.col('recall_date') + pd.Timedelta(days=3))))

treatments_3days = purchases_merged.group_by(['index']).agg(
	pl.col("beef").max(),
	pl.col("chicken").max(),
	pl.col("pork").max(),
	pl.col("pig").max(),
	pl.col("lamb").max(),
	pl.col("bison").max(),
	pl.col("duck").max(),
	pl.col("turkey").max(),
	pl.col("goat").max(),
	pl.col("rabbit").max(),
	pl.col("venison").max(),
	pl.col("goose").max(),
	pl.col("veal").max(),
	pl.col("fish").max())	


# and we're back to pandas

purchases_treated = purchases.reset_index().merge(treatments_3days.to_pandas(), how = 'left', on = 'index')
purchases_treated = purchases_treated.merge(treatments_7days.to_pandas(),
	how = 'left', on = 'index', suffixes = ('_3day','_7day'))

# fill in the NAs
purchases_treated[purchases_treated.columns[20:]] = purchases_treated[purchases_treated.columns[20:]].fillna(0)

# off to stata to model
purchases_treated.to_stata("/Users/math0231/Desktop/elastic/all_sales_recalls.dta")


