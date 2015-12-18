from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from datetime import datetime
import time, os, re, shutil, zipfile
import pandas as pd

to_check = [
	'Year',
	'Quarter',
	'Month',
	'DayofMonth',
	'DayofWeek',
	'DayOfWeek',
	'FlightDate',
	'UniqueCarrier',
	'TailNum',
	'FlightNum',
	'OriginAirportID',
	'DestAirportID',
	'CRSDepTime',
	'CRSElapsedTime',
	'DistanceGroup',
	'CarrierDelay',
	'WeatherDelay',
	'NASDelay',
	'SecurityDelay',
	'LateAircraftDelay',
	'Cancelled',
	'Diverted',
]

def check_checkboxes(driver):
	checkboxes = driver.find_elements_by_css_selector('.dataTD>input')
	checkboxes = filter(
		lambda c: c.get_attribute('title') in to_check, 
		driver.find_elements_by_css_selector('.dataTD>input')
	)
	for element in checkboxes:
		if element.is_selected():
			element.click()
		if element.get_attribute('title') in to_check:
			element.click()

def download_data_files(driver):
	driver.get('http://www.transtats.bts.gov/DL_SelectFields.asp?Table_ID=236&DB_Short_Name=On-Time')

	dl_folder_counter = 1
	current_year = datetime.now().year
	for year in xrange(current_year-2, current_year+1):
		for month in xrange(1,12):
			print 'downloading year: {0}, month:{1}'.format(year, month)
			check_checkboxes(driver)
			year_select = Select(driver.find_element_by_id('XYEAR'))
			year_select.select_by_value(str(year))
			month_select = Select(driver.find_element_by_id('FREQUENCY'))
			month_select.select_by_value(str(month))

			download_button = driver.find_element_by_css_selector('button.tsbutton[name=Download]')
			download_button.click()
			delay_download_until_folder_size(dl_folder_counter)
			dl_folder_counter+=1
	driver.close()

downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')

def list_files_in_downloads_folder(pattern='\d+_T_ONTIME.*\.zip(?!\.crdownload)'):
	pattern = re.compile(pattern)
	downloads_folder_contents = os.listdir(downloads_folder)
	return [f for f in downloads_folder_contents if re.search(pattern, f)]

def delay_download_until_folder_size(expected_n, minutes_wait=1):
	print 'waiting for download'
	for i in xrange(minutes_wait * 4):
		if len(list_files_in_downloads_folder())==expected_n:
			print 'proceeding'
			return
		elif len(list_files_in_downloads_folder())>expected_n:
			raise Exception('Too many matching files in Downloads Folder')
		else:
			time.sleep(15)
			print 'we\'ve waited {} seconds for file to download'.format((i+1)*15)
	raise Exception('Download Timout Exceeded')

def build_dataframe(sampling_size=1e5):
	print 'building dataframe...'
	df_list = []
	for f in list_files_in_downloads_folder():
		filepath = os.path.join(downloads_folder, f)
		zf = zipfile.ZipFile(filepath)
		df = pd.read_csv(zf.open(zf.filelist[0]))
		try:
			df = df.sample(sampling_size)
		except ValueError:
			print 'dataframe is small enough to keep all entries' 
		df_list.append(df)
	print 'concatenating dataframe'
	pd.concat(df_list).to_pickle(os.path.join('cache', 'raw_flights_data{}.pkl'.format(
		datetime.now().strftime('%Y%d%M-%H%M'))
	))

def clear_data_files_from_downloads_folder(pattern='\d+_T_ONTIME.*'):
	print 'clearing downloads folder...'
	for f in list_files_in_downloads_folder(pattern):
		print 'removing {}'.format(f)
		os.remove(os.path.join(downloads_folder, f))

def main():
	try:
		driver = webdriver.Chrome()
		download_data_files(driver)
		build_dataframe()
	finally:
		clear_data_files_from_downloads_folder()

if '__main__' in __name__:
	main()