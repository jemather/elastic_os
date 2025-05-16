// need to install reghdfe if not already installed
// To do so:
// ssc install reghdfe


use all_sales_recalls.dta, clear

gen ln_q = ln(total_volume_sales)
gen avg_price = total_value_sales/total_volume_sales
gen ln_price = ln(avg_price)

// country is text, create indicators, and create year_month indicators
egen country_ind = group(country)
egen year_month = group(year month)


// indicators for any type of meat recall and the major meat categories 
gen anymeat_3day = (beef_3day+chicken_3day+pork_3day+pig_3day+lamb_3day+bison_3day+duck_3day+turkey_3day+goat_3day+rabbit_3day+venison_3day+goose_3day+veal_3day+fish_3day) > 0
gen anymeat_7day = (beef_7day+chicken_7day+pork_7day+pig_7day+lamb_7day+bison_7day+duck_7day+turkey_7day+goat_7day+rabbit_7day+venison_7day+goose_7day+veal_7day+fish_7day) > 0

// indicators for "major" meat categories - in US and europe, most places its beef/chicken/pork, and these are the products that meat substitutes typically imitate
gen majmeat_3day = (beef_3day+chicken_3day+pork_3day+pig_3day)>0
gen majmeat_7day = (beef_7day+chicken_7day+pork_7day+pig_7day)>0

// "pork" and "pig" recalls separated, combine them
gen pork_fix_3day = (pork_3day+pig_3day)>0
gen pork_fix_7day = (pork_7day+pig_7day)>0



// Conservatively cluster errors at country#year as this is the way treatments are applied
// base model, no brand specific effects
reghdfe ln_q c.ln_price i.majmeat_7day c.ln_price#i.majmeat_3day, absorb(panelist year_month day_of_month day_of_week brand retailer) cluster(country_ind#year_month)

// similar results with all meat and shorter time windows
reghdfe ln_q c.ln_price i.majmeat_3day c.ln_price#i.majmeat_7day, absorb(panelist year_month day_of_month day_of_week brand retailer) cluster(country_ind#year_month)
reghdfe ln_q c.ln_price i.anymeat_3day c.ln_price#i.anymeat_3day, absorb(panelist year_month day_of_month day_of_week brand retailer) cluster(country_ind#year_month)
reghdfe ln_q c.ln_price i.anymeat_7day c.ln_price#i.anymeat_7day, absorb(panelist year_month day_of_month day_of_week brand retailer) cluster(country_ind#year_month)

// estimate brand specific elasticities
// margins remains slow, estimation takes about 1.5 hours on M3 Max MBP
reghdfe ln_q c.ln_price#i.brand_num i.majmeat_7day c.ln_price#i.brand_num#i.majmeat_7day, absorb(panelist year_month day_of_month day_of_week brand retailer) cluster(country_ind#year_month)
margins, dydx(ln_price) at (brand_num = (1(1)68)) post

// write margins to the template
putexcel set "Template_Estimates.xlsx", modify sheet("Tabelle1")

matrix b = r(table)[1,1..68]
matrix ses = r(table)[2,1..68]
matrix ps = r(table)[4,1..68]
putexcel D3=matrix(b')
putexcel E3=matrix(ses')
putexcel F3=matrix(ps')

// and we're done!
