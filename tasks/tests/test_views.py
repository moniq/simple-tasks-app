from django.test import TestCase


class TaskTest(TestCase):

    def test_index_status_code(self):
        response = self.client.get("/")
        self.assertEquals(response.status_code, 200)
