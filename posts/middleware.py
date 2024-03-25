import datetime

from django.http import HttpRequest

class UserActivityLog:


    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        response = self.get_response(request)
        date = datetime.datetime.now().strftime("%m.%d.%Y %H:%M")
        username = request.user
        url = request.get_full_path()
        strings = f'{date} | {username} | {url}\n'

        with open('usersActivity.log', mode='a', encoding='utf-8') as file:
            file.write(strings)

        return response

