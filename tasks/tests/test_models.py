from django.test import TestCase
from datetime import datetime
from django.utils.timezone import make_aware
from unittest import mock
from django.core.exceptions import ValidationError
from ..models import Task


class TaskModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        Task.objects.create(
            name="Task A",
            start_date=make_aware(datetime.strptime('20-01-2019', '%d-%m-%Y')),
            end_date=make_aware(datetime.strptime('22-01-2019', '%d-%m-%Y')),
        )

        task_b = Task.objects.create(
            name="Task B",
        )

        Task.objects.create(
            name="Task B 1",
            parent=task_b,
            start_date=make_aware(datetime.strptime('01-01-2019', '%d-%m-%Y')),
            end_date=make_aware(datetime.strptime('10-01-2019', '%d-%m-%Y')),
        )

        task_b2 = Task.objects.create(
            name="Task B 2",
            parent=task_b,
        )

        Task.objects.create(
            name="Task B 2a",
            start_date=make_aware(datetime.strptime('01-03-2019', '%d-%m-%Y')),
            end_date=make_aware(datetime.strptime('10-03-2019', '%d-%m-%Y')),
            parent=task_b2
        )

        Task.objects.create(
            name="Task B 2b",
            start_date=make_aware(datetime.strptime('05-03-2019', '%d-%m-%Y')),
            end_date=make_aware(datetime.strptime('15-03-2019', '%d-%m-%Y')),
            parent=task_b2,
        )

    def test_name_max_length(self):
        task = Task.objects.get(id=1)
        max_length = task._meta.get_field('name').max_length
        self.assertEquals(max_length, 120)

    @mock.patch('django.utils.timezone.now')
    def test_node_task_scheduled_status(self, now_mock):
        now_mock.return_value = make_aware(datetime.strptime('01-01-2019', '%d-%m-%Y'))
        node_task = Task.objects.get(id=1)
        self.assertEqual(node_task.status, 'Scheduled')

    @mock.patch('django.utils.timezone.now')
    def test_node_task_running_status(self, now_mock):
        now_mock.return_value = make_aware(datetime.strptime('21-01-2019', '%d-%m-%Y'))
        node_task = Task.objects.get(id=1)
        self.assertEqual(node_task.status, 'Running')

    @mock.patch('django.utils.timezone.now')
    def test_node_task_complete_status(self, now_mock):
        now_mock.return_value = make_aware(datetime.strptime('25-01-2019', '%d-%m-%Y'))
        node_task = Task.objects.get(id=1)
        self.assertEqual(node_task.status, 'Complete')

    @mock.patch('django.utils.timezone.now')
    def test_parent_task_scheduled_status(self, now_mock):
        now_mock.return_value = make_aware(datetime.strptime('30-12-2018', '%d-%m-%Y'))
        task = Task.objects.get(id=2)
        self.assertEqual(task.status, 'Scheduled')

    @mock.patch('django.utils.timezone.now')
    def test_parent_task_running_status(self, now_mock):
        now_mock.return_value = make_aware(datetime.strptime('05-01-2019', '%d-%m-%Y'))
        task = Task.objects.get(id=2)
        self.assertEqual(task.status, 'Running')

    @mock.patch('django.utils.timezone.now')
    def test_parent_task_multiruns_status(self, now_mock):
        now_mock.return_value = make_aware(datetime.strptime('07-03-2019', '%d-%m-%Y'))
        task = Task.objects.get(id=2)
        self.assertEqual(task.status, 'Multi-Runs')

    @mock.patch('django.utils.timezone.now')
    def test_parent_task_idle_status(self, now_mock):
        now_mock.return_value = make_aware(datetime.strptime('07-02-2019', '%d-%m-%Y'))
        task = Task.objects.get(id=2)
        self.assertEqual(task.status, 'Idle')

    @mock.patch('django.utils.timezone.now')
    def test_parent_task_multiruns_status(self, now_mock):
        now_mock.return_value = make_aware(datetime.strptime('07-10-2019', '%d-%m-%Y'))
        task = Task.objects.get(id=2)
        self.assertEqual(task.status, 'Complete')

    @mock.patch('django.utils.timezone.now')
    def test_multilevel_task_idle_scheduled_status(self, now_mock):
        now_mock.return_value = make_aware(datetime.strptime('07-02-2019', '%d-%m-%Y'))
        task_top = Task.objects.get(id=2)
        task_mid = Task.objects.get(id=4)
        self.assertEqual(task_top.status, 'Idle')
        self.assertEqual(task_mid.status, 'Scheduled')

    @mock.patch('django.utils.timezone.now')
    def test_multilevel_task_multiruns_status(self, now_mock):
        now_mock.return_value = make_aware(datetime.strptime('07-03-2019', '%d-%m-%Y'))
        task_top = Task.objects.get(id=2)
        task_mid = Task.objects.get(id=4)
        self.assertEqual(task_top.status, 'Multi-Runs')
        self.assertEqual(task_mid.status, 'Multi-Runs')

    def test_cannot_save_start_date_grtr_end_date(self):
        task = Task(
            name="Task C",
            start_date=make_aware(datetime.strptime('17-03-2019', '%d-%m-%Y')),
            end_date=make_aware(datetime.strptime('07-03-2019', '%d-%m-%Y'))
        )
        with self.assertRaises(ValidationError):
            task.save()
            task.full_clean()

    def test_cannot_save_start_date_equal_end_date(self):
        task = Task(
            name="Task C",
            start_date=make_aware(datetime.strptime('17-03-2019', '%d-%m-%Y')),
            end_date=make_aware(datetime.strptime('17-03-2019', '%d-%m-%Y'))
        )

        with self.assertRaises(ValidationError):
            task.save()
            task.full_clean()

    def test_min_very_early_start_date_propagation(self):
        parent_task = Task.objects.get(id=5)
        min_task = Task.objects.create(
            name="very old task",
            start_date=make_aware(datetime.strptime('07-03-2009', '%d-%m-%Y')),
            end_date=make_aware(datetime.strptime('17-03-2009', '%d-%m-%Y')),
            parent=parent_task
        )
        self.assertEqual(min_task.start_date, parent_task.start_date)
        self.assertEqual(min_task.start_date, parent_task.parent.start_date)
        self.assertEqual(min_task.start_date, parent_task.parent.parent.start_date)

    def test_max_very_late_end_date_propagation(self):
        parent_task = Task.objects.get(id=5)
        task = Task.objects.create(
            name="future task",
            start_date=make_aware(datetime.strptime('07-03-2109', '%d-%m-%Y')),
            end_date=make_aware(datetime.strptime('17-03-2109', '%d-%m-%Y')),
            parent=parent_task
        )
        self.assertEqual(task.end_date, parent_task.end_date)
        self.assertEqual(task.end_date, parent_task.parent.end_date)
        self.assertEqual(task.end_date, parent_task.parent.parent.end_date)

    def test_end_date_no_propagation(self):
        parent_task = Task.objects.get(id=5)
        tmp_parent_end_datetime = parent_task.parent.end_date


        task = Task.objects.create(
            name="task B2a.1",
            start_date=make_aware(datetime.strptime('07-03-2009', '%d-%m-%Y')),
            end_date=make_aware(datetime.strptime('11-03-2009', '%d-%m-%Y')),
            parent=parent_task
        )
        self.assertEqual(task.end_date, parent_task.end_date)
        self.assertNotEqual(task.end_date, parent_task.parent.end_date)
        self.assertEqual(tmp_parent_end_datetime, parent_task.parent.end_date)

    def test_start_date_no_propagation(self):
        parent_task = Task.objects.get(id=6)
        tmp_parent_start_datetime = parent_task.parent.start_date

        task = Task.objects.create(
            name="Task B2b.1",
            start_date=make_aware(datetime.strptime('02-03-2019', '%d-%m-%Y')),
            end_date=make_aware(datetime.strptime('25-03-2019', '%d-%m-%Y')),
            parent=parent_task
        )
        self.assertEqual(
            task.start_date,
            parent_task.start_date
        )
        self.assertNotEqual(
            task.start_date,
            parent_task.parent.start_date
        )
        self.assertEqual(
            tmp_parent_start_datetime,
            parent_task.parent.start_date
        )

    def test_subtasks_duration(self):
        parent_task = Task.objects.get(id=2)
        first_subtask = Task.objects.get(id=3)
        last_subtask = Task.objects.get(id=6)

        self.assertEqual(
            parent_task.duration,
            last_subtask.end_date-first_subtask.start_date
        )

    def test_get_flat_subtasks_list(self):
        parent_task = Task.objects.get(id=2)
        self.assertEqual(
            parent_task.get_flat_subtasks_list(),
            [Task.objects.get(id=3),
             Task.objects.get(id=5),
             Task.objects.get(id=6)]
        )

    def test_sort_flat_children_by_start_date(self):

        parent_task = Task.objects.get(id=2)
        t = Task.objects.create(
            name="Task B 3",
            start_date=make_aware(datetime.strptime('02-03-2007', '%d-%m-%Y')),
            end_date=make_aware(datetime.strptime('22-03-2007', '%d-%m-%Y')),
            parent=parent_task
        )
        self.assertEqual(
            Task.sort_flat_children_by_start_date(parent_task.get_flat_subtasks_list()),
            [t,
             Task.objects.get(id=3),
             Task.objects.get(id=5),
             Task.objects.get(id=6),
             ]
        )

    def test_merge_subtasks_by_scope(self):
        parent_task = Task.objects.get(id=2)
        t = Task.objects.create(
            name="Task B 3",
            start_date=make_aware(datetime.strptime('02-03-2007', '%d-%m-%Y')),
            end_date=make_aware(datetime.strptime('22-03-2007', '%d-%m-%Y')),
            parent=parent_task
        )
        self.assertEqual(
            Task.merge_subtasks_by_scope(
                Task.sort_flat_children_by_start_date(parent_task.get_flat_subtasks_list())
            ),
            [[t.start_date, t.end_date],
             [Task.objects.get(id=3).start_date, Task.objects.get(id=3).end_date],
             [Task.objects.get(id=5).start_date, Task.objects.get(id=6).end_date],
             ]
        )

    def test_net_duration(self):
        parent_task = Task.objects.get(id=2)
        t = Task.objects.create(
            name="Task B 3",
            start_date=make_aware(datetime.strptime('02-03-2007', '%d-%m-%Y')),
            end_date=make_aware(datetime.strptime('22-03-2007', '%d-%m-%Y')),
            parent=parent_task
        )
        self.assertEqual(str(parent_task.net_duration), '43 days, 0:00:00')