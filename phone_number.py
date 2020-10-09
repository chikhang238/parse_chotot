from selenium import webdriver
from selenium.webdriver.firefox.options import Options
   
options = Options()
options.add_argument("--headless")

driver = webdriver.Firefox(executable_path='/home/chikhang/Downloads/geckodriver', options=options)
driver.get('https://www.chotot.com/tp-ho-chi-minh/quan-tan-phu/mua-ban-laptop/77695278.htm#px=SR-stickyad-[PO-1][PL-top]')
xpath = '/html'
print(driver.find_element_by_xpath(xpath))

xpath_click = "//span[contains(text(), 'BẤM ĐỂ HIỆN SỐ')]"
button = driver.find_element_by_xpath(xpath_click)
print(driver.execute_script("arguments[0].click();", button))

phone = "/html/body/div[1]/div/div[1]/div/div[4]/div/div[2]/div[2]/div[1]/div"
print(driver.find_element_by_xpath(phone).text)


driver.get('https://www.chotot.com/tp-ho-chi-minh/quan-9/mua-ban-do-an-thuc-pham/78109199.htm')
xpath = '/html'
print(driver.find_element_by_xpath(xpath))

xpath_click = "//span[contains(text(), 'BẤM ĐỂ HIỆN SỐ')]"
button = driver.find_element_by_xpath(xpath_click)
print(driver.execute_script("arguments[0].click();", button))

phone = "/html/body/div[1]/div/div[1]/div/div[4]/div/div[2]/div[2]/div[1]/div"
print(driver.find_element_by_xpath(phone).text)



