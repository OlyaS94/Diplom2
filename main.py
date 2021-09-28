from random import randrange
from tokens import b_token
from vk_bot import VkBot
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


required_param = 10 ** 7


class SearchPeople:
  
  def __init__(self):
    self.vk = vk_api.VkApi(token=b_token)
    self.longpoll = VkLongPoll(self.vk)
    self.vk_button = self.vk.get_api()

  def write_msg(self, user_id, message):
    self.vk.method('messages.send', {'user_id': user_id,'message': message,'random_id': randrange(required_param)})

  def bot_talk(self):
    for event in self.longpoll.listen():
      if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
          print('New message:')
          print(f'For me by: {event.user_id}',end='')

          bot = VkBot(event.user_id)
          self.write_msg(event.user_id, bot.new_message(event.text))
          print(' Text: ', event.text)

  print("Start")


if __name__ == '__main__':
  search = SearchPeople()
  search.bot_talk()