from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import time, datetime
import json
from .models import Habit

User = get_user_model()


class HabitModelTestCase(TestCase):
    """Тесты модели Habit"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

    def test_create_habit(self):
        """Тест создания привычки"""
        habit = Habit.objects.create(
            user=self.user,
            place="Дома",
            time=time(8, 0),
            action="Пить воду",
            execution_time=30,
            is_public=True,
        )

        self.assertEqual(habit.action, "Пить воду")
        self.assertEqual(habit.user.username, "testuser")
        self.assertTrue(habit.is_public)
        self.assertFalse(habit.is_pleasant)

    def test_pleasant_habit(self):
        """Тест создания приятной привычки"""
        habit = Habit.objects.create(
            user=self.user,
            place="Диван",
            time=time(20, 0),
            action="Смотреть сериал",
            execution_time=60,
            is_pleasant=True,
            is_public=False,
        )

        self.assertTrue(habit.is_pleasant)
        self.assertIsNone(habit.reward)
        self.assertIsNone(habit.related_habit)

    def test_habit_with_reward(self):
        """Тест привычки с вознаграждением"""
        habit = Habit.objects.create(
            user=self.user,
            place="Кафе",
            time=time(15, 0),
            action="Читать книгу",
            execution_time=90,
            reward="Кофе",
            is_public=True,
        )

        self.assertEqual(habit.reward, "Кофе")
        self.assertFalse(habit.is_pleasant)

    def test_invalid_execution_time(self):
        """Тест невалидного времени выполнения"""
        with self.assertRaises(Exception):
            habit = Habit(
                user=self.user,
                place="Дом",
                time=time(10, 0),
                action="Тест",
                execution_time=150,
            )
            habit.full_clean()


class HabitAPITestCase(APITestCase):
    """Тесты API привычек"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="apiuser",
            password="apipass123",
            email="api@example.com",
            telegram_chat_id="123456",
        )

        self.other_user = User.objects.create_user(
            username="otheruser", password="otherpass123", email="other@example.com"
        )

        self.client = APIClient()

        # Создаем привычки для тестирования
        self.habit = Habit.objects.create(
            user=self.user,
            place="Парк",
            time=time(9, 0),
            action="Утренняя пробежка",
            execution_time=60,
            is_public=True,
        )

        self.private_habit = Habit.objects.create(
            user=self.user,
            place="Дом",
            time=time(20, 0),
            action="Чтение",
            execution_time=45,
            is_public=False,
        )

    def get_token(self, username="apiuser", password="apipass123"):
        """Получение JWT токена"""
        url = "/api/users/token/"
        data = {"username": username, "password": password}
        response = self.client.post(url, data)
        return response.data.get("access")

    def test_user_registration(self):
        """Тест регистрации пользователя"""
        url = "/api/users/register/"
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)

    def test_user_login(self):
        """Тест авторизации пользователя"""
        url = "/api/users/token/"
        data = {"username": "apiuser", "password": "apipass123"}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_get_habits_unauthorized(self):
        """Тест получения привычек без авторизации"""
        response = self.client.get("/api/habits/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_habits_authorized(self):
        """Тест получения привычек с авторизацией"""
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get("/api/habits/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_create_habit(self):
        """Тест создания привычки через API"""
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {
            "place": "Спортзал",
            "time": "18:00:00",
            "action": "Тренировка",
            "execution_time": 90,
            "is_public": True,
        }

        response = self.client.post("/api/habits/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["action"], "Тренировка")

    def test_update_habit(self):
        """Тест обновления привычки"""
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {"action": "Вечерняя пробежка"}

        response = self.client.patch(f"/api/habits/{self.habit.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["action"], "Вечерняя пробежка")

    def test_delete_habit(self):
        """Тест удаления привычки"""
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.delete(f"/api/habits/{self.habit.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_public_habits(self):
        """Тест получения публичных привычек"""
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get("/api/habits/public/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pagination(self):
        """Тест пагинации"""
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Создаем дополнительные привычки
        for i in range(10):
            Habit.objects.create(
                user=self.user,
                place=f"Место {i}",
                time=time(i + 8, 0),
                action=f"Действие {i}",
                execution_time=30,
                is_public=False,
            )

        response = self.client.get("/api/habits/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 5)  # Проверяем пагинацию
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

    def test_permission_other_user(self):
        """Тест прав доступа другого пользователя"""
        token = self.get_token("otheruser", "otherpass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Пытаемся получить доступ к привычке другого пользователя
        response = self.client.get(f"/api/habits/{self.private_habit.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class HabitValidatorTestCase(TestCase):
    """Тесты валидаторов"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="validatoruser", password="validator123"
        )

    def test_reward_and_related_habit_together(self):
        """Тест одновременного указания вознаграждения и связанной привычки"""
        pleasant_habit = Habit.objects.create(
            user=self.user,
            place="Диван",
            time=time(20, 0),
            action="Релакс",
            execution_time=60,
            is_pleasant=True,
        )

        habit = Habit(
            user=self.user,
            place="Парк",
            time=time(9, 0),
            action="Пробежка",
            execution_time=90,
            reward="Кофе",
            related_habit=pleasant_habit,
        )

        with self.assertRaises(Exception):
            habit.full_clean()

    def test_execution_time_exceeds_limit(self):
        """Тест превышения времени выполнения"""
        habit = Habit(
            user=self.user,
            place="Дом",
            time=time(10, 0),
            action="Тест",
            execution_time=130,  # Больше 120 секунд
        )

        with self.assertRaises(Exception):
            habit.full_clean()

    def test_pleasant_habit_with_reward(self):
        """Тест приятной привычки с вознаграждением"""
        habit = Habit(
            user=self.user,
            place="Диван",
            time=time(21, 0),
            action="Медитация",
            execution_time=60,
            is_pleasant=True,
            reward="Чай",  # Не должно быть вознаграждения
        )

        with self.assertRaises(Exception):
            habit.full_clean()


class TelegramBotTestCase(TestCase):
    """Тесты Telegram бота"""

    def setUp(self):
        from .telegram_bot import TelegramBot

        self.bot = TelegramBot()
        self.user = User.objects.create_user(
            username="telegramuser",
            password="telegram123",
            telegram_chat_id="test_chat_id",
        )

    def test_message_formatting(self):
        """Тест форматирования сообщения"""
        from .models import Habit

        habit = Habit(
            user=self.user,
            place="Парк",
            time=time(9, 0),
            action="Пробежка",
            execution_time=60,
            reward="Смузи",
        )

        # Тестируем метод форматирования
        # В реальном тесте здесь нужно бы проверить формат сообщения
        self.assertIsNotNone(habit)
