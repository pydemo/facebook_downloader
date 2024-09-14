#https://medium.com/python-script/using-python-to-monitor-my-medium-views-4fbe24d0c78
# import requests
import re

cookies = {'sid': '# INSERT YOUR SID COOKIE HERE #',
           'uid': '# INSERT YOUR UID COOKIE HERE #'}

source_code = requests.get(url='https://medium.com/@gabrielbonfim1/stats', 
                           cookies=cookies).text

views_counts = re.findall('"views":([0-9]+)',source_code)
views = sum([int(num) for num in views_counts])

print(f"Your view count is {views}")