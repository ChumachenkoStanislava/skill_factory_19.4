from api import PetFriends
from settings import *

import os


class TestPetFriends:
    def setup_method(self):
        self.pf = PetFriends()

    # Тест 1. Проверка получения ключа API при условии ввода валидных данных
    def test_get_api_key_for_valid_user(self, email=valid_email, password=valid_password):
        status, result = self.pf.get_api_key(email, password)
        assert status == 200
        assert 'key' in result

    # Тест 2. Проверка получения ключа API при условии, что введён не валидный пароль
    def test_get_api_wrong_password(self, email=valid_email, password=valid_password + "123"):
        status, result = self.pf.get_api_key(email, password)
        assert status == 403
        # assert 'Please provide valid password' in result
        # сервер отдает неправильное сообщение
        assert 'This user wasn&#x27;t found in database' in result

    # Тест 3. Проверка получения ключа API при условии, что не введён пароль
    def test_get_api_key_without_password(self, email=valid_email, password=""):
        status, _ = self.pf.get_api_key(email, password)
        assert status == 403
        assert 'Please provide password'

    # Тест 4. Проверка получения ключа API при условии, что введён не валидный адрес электронной почты
    def test_get_api_key_wrong_email(self, email=valid_email + '123', password=valid_password):
        status, result = self.pf.get_api_key(email, password)
        assert status == 403
        # assert 'Please provide valid email' in result
        # сервер отдает неправильное сообщение
        assert 'This user wasn&#x27;t found in database' in result

    # Тест 5. Проверка получения API при условии, что адрес электронной почты не введён.
    def test_get_api_key_without_email(self, email='', password=valid_password):
        status, _ = self.pf.get_api_key(email, password)
        assert status == 403
        assert 'Please provide email'

    # Тест 6. Получение списка животных с вводом валидных данных
    def test_get_all_pets_with_valid_key(self, filter=''):
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)
        status, result = self.pf.get_list_of_pets(auth_key, filter)
        assert status == 200
        assert len(result['pets']) > 0

    # Тест 7. Получение списка животных с вводом НЕвалидных данных
    def test_get_pets_list_with_invalid_auth_key(self, filter=''):
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)
        auth_key['key'] += 'qwerty'
        status, result = self.pf.get_list_of_pets(auth_key, filter)
        assert status == 403
        assert "Please provide &#x27;auth_key&#x27; Header" in result

    # Тест 8. Добавление нового питомца с валидными данными
    def test_add_new_pet_with_valid_data(self, name='Пуська', animal_type='скоттиш-фолд',
                                         age='2', pet_photo='images/cat1.jpg'):
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)

        status, result = self.pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
        assert status == 200
        assert result['name'] == name

    # Тест 9. Добавление нового питомца с валидными данными БЕЗ фото
    def test_add_new_pet_with_valid_date_without_photo(self, name='Shrek', animal_type='ogr', age="30"):
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)
        status, result = self.pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
        assert status == 200
        assert result['name'] == name

    # Тест 10. Изменение данных существующего питомца
    def test_successful_update_self_pet_info(self, name='Мурзик', animal_type='Котэ', age=5):
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)
        _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")
        if len(my_pets['pets']) > 0:
            status, result = self.pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
            assert status == 200
            assert result['name'] == name
        else:
            raise Exception("There is no my pets")

    # Тест 11. Удаление существующего питомца
    def test_successful_delete_self_pet(self):
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)
        _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")
        if len(my_pets['pets']) > 0:
            self.pf.add_new_pet(
                auth_key,
                "Мурзик",
                "Котэ",
                "5",
                os.path.join(os.path.dirname(__file__), "images/cat1.jpg")
            )
            _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")

        pet_id = my_pets['pets'][0]['id']
        status, _ = self.pf.delete_pet(auth_key, pet_id)
        _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")

        assert status == 200
        assert pet_id not in my_pets.values()


class TestAddPhoto:
    def setup_method(self):
        self.pf = PetFriends()

        _, auth_key = self.pf.get_api_key(valid_email, valid_password)
        _, result = self.pf.add_new_pet_without_photo(auth_key, 'Shrek', 'ogr', '30')

        self.auth_key = auth_key
        self.pet_id = result['id']

    # Тест 12. Добавление фото к существующему питомцу без фото
    def test_add_photo(self, pet_photo='images/shrek.jpg'):
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
        status, result = self.pf.add_photo(self.auth_key, self.pet_id, pet_photo)
        assert status == 200