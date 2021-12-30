import re, argparse, datetime
import pandas as pd
import chromedriver_binary
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

def main(args):
    options = ChromeOptions()
    options.headless = True
    driver = Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    driver.get('http://utanohi.everyday.jp/')
    assert 'うたの日' in driver.title

    wait.until(expected_conditions.visibility_of_element_located((By.ID, "sc4")))
    driver.find_element(by=By.ID, value='sc4').click() # 「サーチ」
    driver.find_elements(by=By.NAME, value='key')[0].click() # 検索範囲指定   

    form = driver.find_element(by=By.NAME, value='search')
    form.send_keys(args.name)
    driver.find_element(by=By.NAME, value='number').click() # 「OK」

    wait.until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, "fs12.lime")))

    result = pd.DataFrame({
        'date': [],
        'theme': [],
        'tanka': [],
        'love': [],
        'like': [],
        'loved': [],
        'liked': []
    })

    infostr = driver.find_element(by=By.CLASS_NAME, value='fs12.lime').text
    assert '該当件数' in infostr
    total = int(re.findall(r'[0-9０-９]+', infostr)[0]) # 件数

    pages = total // 100
    remain = total % 100
    if remain != 0:
        pages = pages + 1

    for page in range(1, pages+1):
        wait.until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, "per.mrz")))

        print(f'page{page}/{pages}')
        datalist = driver.find_elements(by=By.CLASS_NAME, value='per.mrz')
        date = [data.find_element(by=By.CLASS_NAME, value='green').text for data in datalist]
        theme = [data.find_element(by=By.CLASS_NAME, value='the.fs12').text for data in datalist]
        tanka = [data.find_element(by=By.CLASS_NAME, value='verse').text for data in datalist]
        love = [data.find_element(by=By.CLASS_NAME, value='love').text for data in datalist]
        like = [data.find_element(by=By.CLASS_NAME, value='like').text for data in datalist]

        loved_lists = [data.find_elements(by=By.CLASS_NAME, value='name.love') for data in datalist]
        loved = [[name.text for name in _list] for _list in loved_lists]

        liked_lists = [data.find_elements(by=By.CLASS_NAME, value='name.like') for data in datalist]
        liked = [[name.text for name in _list] for _list in liked_lists]

        result_page = pd.DataFrame({
            'date': date,
            'theme': theme,
            'tanka': tanka,
            'love': love,
            'like': like,
            'loved': loved,
            'liked': liked
        })
        result = pd.concat([result, result_page])
        if page != pages:
            buttons = driver.find_elements(By.LINK_TEXT, str(page+1))
            buttons[0].click()
    
    #assert len(result) == total
    result.to_csv(f'utanohi-{str(datetime.date.today())}.csv', index=False, encoding='utf_8_sig')
    driver.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name', help='筆名')
    args = parser.parse_args()

    main(args)