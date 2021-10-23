import bs4
import requests
from vkinder_b import user_info, output_search_result, add_favorite, ban_list, clear_database
from bot import *
from words import start_word, stop_word

candidate_values = {
  'sex': 0,
  'age_from': 0,
  'age_to': 0,
  'city': 0,
  'status': 0
  }

candidate = {
  'sex': '',
  'age_from': 0,
  'age_to': 0,
  'city': '',
  'status': ''
  }

params = {
  'start_dialog': False,
  'input_age': False,
  'input_status': False,
  'input_city': False,
  'ready': False,
  'search_completed': False,
  'output': False,
  'count': 0,
  'iter': 0,
  'limit': 0
  }
cut_candidates = {}
output_info = []


class VkBot:
  def __init__(self, user_id):
    self.username = self._get_user_name(user_id)
    self.response = []

  def _get_user_name(self, user_id):
    request = requests.get("https://vk.com/id" + str(user_id))
    bs = bs4.BeautifulSoup(request.text, "html.parser")

    user_name = self._clean_all_tag(bs.findAll("title")[0])
    user_info(user_id, user_name)
    return user_name.split()[0]

  @staticmethod
  def _clean_all_tag(string_line):
    result = ""
    not_skip = True
    for i in list(string_line):
      if not_skip:
        if i == "<":
          not_skip = False
        else:
            result += i
      else:
        if i == ">":
          not_skip = True
    return result

  def new_message(self, message):
    if message.lower() in start_word:
      params['start_dialog'] = True
      return f'Приветствую, {self.username}! \nКого искать? (М / Ж):'

    elif params['start_dialog'] and (message.lower() not in 'мж'):
      return 'Введите букву "м"  или  "ж"'

    elif message.lower() == 'инфо':
      return f'Привет {self.username}\n{Search.info.__doc__}'

    elif params['start_dialog'] and message.lower() == 'м':
      params['input_age'] = True
      params['start_dialog'] = False
      candidate_values['sex'] = 2
      candidate['sex'] = 'Мужчина'
      return 'Введите возраст  От - До  (через пробел)'

    elif params['start_dialog'] and message.lower() == 'ж':
      params['input_age'] = True
      params['start_dialog'] = False
      candidate_values['sex'] = 1
      candidate['sex'] = 'Женщина'
      return 'Введите возраст  От - До  (через пробел)'

    elif params['input_age'] and message.isalpha():
      return 'Можно вводить только цифры!'

    elif params['input_age'] and message.isdigit():
      return 'Можно ввести только две цифры!'

    elif params['input_age'] and len(message.split()) == 2:
      result = message.split()
      if result[0].isdigit() and result[-1].isdigit():
        candidate_values['age_from'] = int(result[0])
        candidate['age_from'] = result[0]
        candidate_values['age_to'] = int(result[-1])
        candidate['age_to'] = result[-1]
        params['input_status'] = True
        params['input_age'] = False
        return f'Введите семейное положение.\n{Search.status()}'
      else:
        return 'Ошибка'

    elif params['input_status'] and message not in '12345678':
      return 'Допустимы только цифры от 1 до 8'

    elif params['input_status'] and message in '12345678':
      candidate_values['status'] = int(message)
      candidate['status'] = Search.add_status(message)
      params['input_city'] = True
      params['input_status'] = False
      return 'Введите название города'

    elif params['input_city'] and message.isalpha():
      city_title = Search().city_search(message.lower())
      if type(city_title) == int:
        candidate_values['city'] = city_title
        candidate['city'] = message
        params['ready'] = True
        params['input_city'] = False
        return f'Данные:\n{candidate["sex"]}от {candidate["age_from"]} до {candidate["age_to"]} '\
               f'{candidate["status"]}\nИз города {candidate["city"].capitalize()}'\
               f'\nДля запуска поиска введите "старт"\nДля отмены введите "стоп"\n'\
               f'Для изменения параметров введите "сброс"\n\nДождитесь окончания проверки'
      else:
        return city_title

    elif params['input_city'] and message.isdigit():
      return 'В названии не должно быть цифры!'

    elif params['ready'] and message.lower() == 'старт':
      params['ready'] = False
      params['search_completed'] = True
      Search().get_search(candidate_values)
      cut_candidate = VkSaver().photo_search()
      params['limit'] = len(cut_candidate)
      for key, item in cut_candidate.items():
        cut_candidates[key] = item
        return f'Нашел {len(cut_candidate)} кандидатов).\n Введите количество кандидатов:'

    elif params['ready'] and message.lower() == 'сброс':
      params['start_dialog'] = True
      return 'Повторите ввод:\nВыберите пол (М / Ж):'

    elif params['search_completed'] and message.isdigit():
      if int(message) > 0:
        message = params['limit']
        response = output_search_result(int(message))
        output_info.append(response)
        clear_database()
        params['output'] = True
        params['count'] = int(message)
        return f'Будет показано {message} варианта(ов)\nПросмотрите фото по ссылкам, затем введите "+" или "-"\n'\
               f'+  добавить в избранное\n- добавить в черный список\n\nДля запуска нажмите "+"'
      else:
        return 'Ошибка'
      
    elif params['output'] and message == '+' and params['count'] != 0:
      params['count'] -= 1
      params['iter'] += 1
      result = output_info[0].pop()
      owner_id = output_info[0].pop()
      add_favorite(owner_id, result)
      return f"Кандидат {params['iter']} из {params['count'] + params['iter']}\n{result}"

    elif params['output'] and message == '-' and params['count'] != 0:
      params['count'] -= 1
      params['iter'] += 1
      result = output_info[0].pop()
      owner_id = output_info[0].pop()
      ban_list(owner_id)
      return f"Кандидат {params['iter']} из {params['count'] + params['iter']}\n{result}"

    elif params['output'] and message in '+-' and params['count'] == 0:
      params['count'] = params['iter'] = 0
      params['output'] = False
      return 'Поиск завершен'

    elif message.lower() in stop_word:
      return f"До встречи, {self.username}!"

    else:
      return Search.wrong_word()


if __name__ == '__main__':
    print('Вас приветствует Бот!')
