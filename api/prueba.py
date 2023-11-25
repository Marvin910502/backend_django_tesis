import requests


wrf_urls = [
    '/home/marvin/PycharmProject/projects/backend_django_tesis/wrfout_files/wrfout_d01_2005-08-28_00_00_00',
    '/home/marvin/PycharmProject/projects/backend_django_tesis/wrfout_files/wrfout_d01_2005-08-28_12_00_00',

]

url = 'http://127.0.0.1:8000/api/prueba-error/'

post_data = {
    'urls': wrf_urls,
    'diagnostic': 'slp',
    'units': 'Pa',
    'index': 0,
}



for i in range(1000):

    response = requests.post(url, json=post_data, headers={'Content-Type': 'application/json'})

    if response.status_code == 200:
        print('success')
    else:
        print('error')



