import requests
from vkinder_b import people_info,liked_photos, get_owner
from tokens import u_token
import time


links = {}


class Search:

  def __init__(self):
    self.url = 'http://api.vk.com/method/'
    self.user_token = u_token
    self.params = {'v': '5.89','country_id': '1'}

  @staticmethod
  def wrong_word():
    return 'Вас приветствует бот!' \
    'Для получения справки введите "инфо"\n Для начала работы напишите "Привет"'

  @staticmethod
  def status():
    return '1 - не женат (не замужем)\n2 - встречается\n3 - помолвлен(-а)\n4 - женат (замужем)\n5 - всё сложно\n' \
    '6 - в активном поиске\n7 - влюблен(-а)\n8 - в гражданском браке'

  @staticmethod
  def add_status(text):
    owner_status = {'1': 'женат (не замужем)','2': 'встречается','3': 'помолвлен(-а)','4': 'женат (замужем)','5': 'всё сложно','6': 'в активном поиске','7': 'влюблен(-а)','8': 'в гражданском браке'}
    return owner_status[text]

  @staticmethod
  def info():
    """
    Бот производит поиск людей по заданным параметрам в социальной сети "Вконтакте".
    Введите данные:
    - пол
    - возраст
    - город
    - семейное положение
    Далее бот находит кандидатов и возвращает для просмотра топ-3 фотографии профиля
    и ссылку на страницу пользователя.
    Можно внести кандидата в избранное или в черный список."""
    return True

  def get_search(self, candidate_info: dict):
    search_params = {
    'access_token': self.user_token,
    'sex': candidate_info['sex'],
    'status': candidate_info['status'],
    'age_from': candidate_info['age_from'],
    'age_to': candidate_info['age_to'],
    'city': candidate_info['city'],
    'sort': 0,
    'count': 500,
    'has_photo': 1}
    peoples = requests.get(self.url + 'users.search', params={**self.params, **search_params}).json()['response']['items']
    owner_id_list = get_owner()
    for person in peoples:
      if person['is_closed'] is False:
        if str(person['id']) not in owner_id_list:
          link = [person['first_name'] + ' ' + person['last_name'], person['id']]
          links[person['id']] = link
    return 'Запрос выполнен.'

  def city_search(self, city_title):
    search_params = {'access_token': self.user_token,'q': city_title.capitalize(),'count': '10'}
    try:
      city_id = requests.get(self.url + 'database.getCities', params={
      **self.params, **search_params}).json()['response']['items'][0]['id']
      return city_id
    except IndexError:
      return 'Ошибка!\nВведите название города'


class VkSaver(Search):
  def __init__(self, owner_id=None):
    super(VkSaver, self).__init__()
    self.owner_id = owner_id
    self.photo_stock = {}
    self.candidates_dict = {}

  def get_photo(self, owner_id, album_id=None):
    if album_id is None:
      album_id = 'profile'
    gp_params = {'access_token':self.user_token,'user_id': owner_id,'extended': 1,'photo_sizes': 1,'album_id': album_id}
    response = requests.get(self.url + 'photos.get', params={**self.params, **gp_params}).json()
    time.sleep(0.3)
    count_photos = response['response']['count']
    if count_photos >= 3:
      for items in response['response']['items']:
        self.photo_stock[items['sizes'][-1]['url']] = items['likes']['count']
    else:
      pass
    sorted_tuple = sorted(self.photo_stock.items(), key=lambda x: x[1])
    limit_tuple = sorted_tuple[-3:]
    return limit_tuple

  def photo_search(self):
    print(links)
    for owner_id in list(links.values()):
      result = self.get_photo(owner_id[-1])
      self.photo_stock = {}
      if result:
        people_info(owner_id)
        liked_photos(owner_id[-1], result)
        self.candidates_dict[owner_id[-1]] = result
    links.clear()
    return self.candidates_dict

if __name__ == '__main__':
    print('module')