def ScrapeHDentalAssistanttData():
    
    import pandas as pd
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import TimeoutException,NoSuchElementException
    import time
    import psycopg2
    
    #creating connection to db
    address='127.0.0.1'
    port='5432'
    database_name='DENTALASSISTANT'
    username='postgres'
    user_password='deveid'
    
    conn = psycopg2.connect(host=address, dbname=database_name,
                            port=port,
                            user=username,
                            password=user_password)
    cur = conn.cursor()
    

    
    #Using ChromeDriver establish connection with url
    url='http://ls.tsbde.texas.gov/ast-grid.php?_searchform=true&lic_nbr=&first_nme=&last_nme=&city=-1&st=-1&zip=&county=-1&disc_action=-1'
    driver = webdriver.Chrome(executable_path='C:/Users/Byteworks/Downloads/chromedriver_win32/chromedriver.exe')
    driver.get(url)
    
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-widget-content jqgrow ui-row-ltr')))
    except TimeoutException:
        print('Page timed out after 10 secs.')
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    #Get last page Number
    for number in soup.find("div", attrs={"id":"pager"}):
        last_page=number.find("span", attrs={"id": "sp_1_pager"})
    last_page=int(last_page.text.replace(' ',''))

    
    for  i in range(1,last_page):
        p1=[]
        p2=[]
        p3=[]
        p4=[]

        try:
            next_link = driver.find_element_by_xpath('//*[@id="next_pager"]')
            next_link.click()
            index = 0
            # update html and soup
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            for data in soup.find("tbody"):

                license_number=data.find('a')
                name=data.find("td", attrs={"aria-describedby": "list_fullname"})
                status=data.find("td", attrs={"aria-describedby": "list_lic_sta_desc"})
                city=data.find("td",attrs={"aria-describedby" : "list_citystate"})

                if license_number is None:
                    license='N/A'
                else:
                    license=license_number.text
                p1.append(license)
                if name is None:
                    full_name='N/A'
                else:
                    full_name=name.text
                p2.append(full_name)
                if status is None:
                    statuses='N/A'
                else:
                    statuses=status.text
                p3.append(statuses)
                if city is None:
                    state_city='N/A'
                else:
                    state_city=city.text
                p4.append(state_city)

            
            
            #Inserting only Active License into into database
            for i in range(0,len(p1)):
                if p1[i] =='N/A' and p2[i]=='N/A' and p3[i]=='N/A' and p4[i]=='N/A':
                    continue
                elif p3[i]=='Active':
                    postgres_insert_query = """ INSERT INTO data (license, name, status,city) VALUES (%s,%s,%s,%s)"""
                    data_to_insert=(p1[i],p2[i],p3[i],p4[i])
            
                    cur.execute(postgres_insert_query,data_to_insert)
                    conn.commit()
                    print (p1[i], "Record inserted successfully")

            time.sleep(3)
            
            
            
        except NoSuchElementException:
            rows_remaining = False
            print("Could not find Element in the html source")
            
    driver.quit()
ScrapeHDentalAssistanttData()
