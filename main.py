import helpers
from time import sleep
from time import time

if __name__ == '__main__':
    start = time()
    graz_apartment_links = helpers.get_all_urls()
    print(graz_apartment_links)
    for url in graz_apartment_links:
        params = helpers.get_apartment_details(url)
        helpers.write_to_db(params)
        sleep(1)
    print(f"{round(time()-start)} s")

