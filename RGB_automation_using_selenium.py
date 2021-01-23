from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

browser = webdriver.Chrome(executable_path=r"chromedriver.exe")
browser.get("https://skyview.gsfc.nasa.gov/current/cgi/query.pl")
search_field = browser.find_element_by_id("object")
s=input("Coordinates : ")
search_field.send_keys(s)
search_field = browser.find_element_by_id("size_pix")
search_field.send_keys("600")
search_field = browser.find_element_by_id("size_deg")
search_field.send_keys("0.1")
browser.find_element_by_id("buttonOP").click()
#Other option
dropdown = browser.find_element_by_id('bscale')
select = Select(dropdown)
select.select_by_visible_text('Sqrt')

dropdown = browser.find_element_by_id('sampler')
select = Select(dropdown)
select.select_by_visible_text('Lanczos3')

#Overlays

browser.find_element_by_id("buttonCO").click()
dropdown = browser.find_element_by_id('overlay_red')
select = Select(dropdown)
select.select_by_visible_text('TGSS ADR1')
dropdown = browser.find_element_by_id('overlay_green')
select = Select(dropdown)
select.select_by_visible_text('DSS2 Red')
dropdown = browser.find_element_by_id('overlay_blue')
select = Select(dropdown)
select.select_by_visible_text('NVSS')
search_field.submit()

# Contours
dropdown = browser.find_element_by_id('contours')
select = Select(dropdown)
select.select_by_visible_text('TGSS ADR1')

dropdown = browser.find_element_by_id('cont_scaling')
select = Select(dropdown)
select.select_by_visible_text('Sqrt')

search_field = browser.find_element_by_id("cont_min")
search_field.send_keys("0.015")

##search_field = browser.find_element_by_id("cont_num")
##search_field.send_keys('8')







#str(len(lists))
##
##for x in range(0,25):
##    o_red = browser.find_element_by_name("overlay_red")
##    for option in o_red.find_elements_by_tag_name('UI_IMREDD'):
##        if option.test == 'TGSS ADR1':
##            option.click()
##            break
