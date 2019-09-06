from collections import Counter
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


SCHEDULED = "S"
RUNNING = "R"
MULTI_RUNS = "MR"  # only parents
IDLE = "I"  # only parents
COMPLETE = "C"

TASK_STATUS_MAPPER = {
    SCHEDULED: "Scheduled",
    RUNNING: "Running",
    MULTI_RUNS: "Multi-Runs",  # only parents
    IDLE: "Idle",  # only parents
    COMPLETE: "Complete",
}

PRIORITY_CHOICES = (
    ('L', 'Low'),
    ('N', 'Normal'),
    ('U', 'Urgent'),
)


class Owner(models.Model):
    name = models.CharField(
        max_length=32,
        null=False,
        blank=False
    )
    surname = models.CharField(
        max_length=64,
        null=False,
        blank=False
    )

    def __str__(self):
        return "{} {}".format(
            self.name,
            self.surname
        )


class Task(models.Model):
    owner = models.ForeignKey(
        Owner,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    priority = models.CharField(
        choices=PRIORITY_CHOICES,
        default='N',
        null=True,
        max_length=1,
    )
    name = models.CharField(
        max_length=120,
        help_text="Name of the task in maximum 120 signs.",
    )
    start_date = models.DateTimeField(
        null=True,
        blank=False,
        help_text="Scheduled start time of the task.",
    )
    end_date = models.DateTimeField(
        null=True,
        blank=False,
        help_text="Scheduled end time of the task.",
    )

    parent = models.ForeignKey(
        'self',
        related_name="subtasks",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Parent task."
    )
    created = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )
    modified = models.DateTimeField(
        auto_now=True,
        editable=False,
    )

    def __str__(self):
        return "{} ({})".format(self.name,
                                self.id)

    class Meta:
        order_with_respect_to = 'parent'

    @property
    def has_children(self):
        """Returns number of children node_task objects. """
        return self.subtasks.all().count()

    @property
    def status(self):
        """Returns human-friendly name of the task status. Calculated property."""
        return TASK_STATUS_MAPPER[self.__status()]

    def __status(self):
        """Returns the flag of the task's status.

        Single node_task can have following flags,
        depending on the start_date and end_date values:
        - S, for Scheduled
        - R, for Running
        - C, for Complete

        Parent task can have following flags:
        - S, R or C - the same flags like node_task
        - M, for Multi-run (at least 2 tasks are running now)
        - I, for Idle (no tasks are running, at least one is scheduled)

        Returns:
            status(str): str flag of the status
        """
        if not self.has_children:
            return self.__node_task_status()
        return self.__parent_task_status()

    def __node_task_status(self):
        """Returns status of node_task. Private method."""
        current = timezone.now()
        if current < self.start_date:
            return SCHEDULED
        elif current > self.end_date:
            return COMPLETE
        return RUNNING

    def __parent_task_status(self):
        """Returns status of parent node. Private method."""
        statuses_counter = self.__parent_task_status_counter()

        # if all sub-tasks has status complete:
        if statuses_counter[COMPLETE] and not (
            statuses_counter[RUNNING] or
            statuses_counter[SCHEDULED]
        ):
            return COMPLETE

        # if all sub-tasks has status scheduled
        elif statuses_counter[SCHEDULED] and not (
            statuses_counter[RUNNING] or
            statuses_counter[COMPLETE]
        ):
            return SCHEDULED

        # if exactly one sub-task is running
        elif statuses_counter[RUNNING] == 1:
            return RUNNING

        # if more then one sub-task is running
        elif statuses_counter[RUNNING] > 1:
            return MULTI_RUNS

        else:
            return IDLE

    def __parent_task_status_counter(self):
        """Returns information about how many sub tasks we have got of a given status.

        Returns:
            status_counter(container.Counter): returns data structure with status's flags and number of sub tasks.
        """

        status_counter = Counter()

        for subtask in self.subtasks.all():
            if not subtask.has_children:
                status_counter.update(subtask.__status())
            else:
                status_counter = status_counter + subtask.__parent_task_status_counter()
        return status_counter

    @property
    def duration(self):
        """Returns simple difference between end_date and start_date of any task."""
        return self.end_date - self.start_date

    @property
    def net_duration(self):
        """Returns real value of task time.
        This function is taking care of tasks that are running at the same moment.

        Two sub-tasks of following structure:
        -- [......] --------
        -------[......]-----

        are recalculated as one following scope of the timetable:
        -- [..........]-----


        Returns:
            net_duration(datetime.deltatime()): the sum of time of every task/time scope in the timetable
        """
        if not self.has_children:
            return self.duration
        return self.__net_duration()

    def __net_duration(self):
        return self.__total_time_of_scopes()

    def __total_time_of_scopes(self):
        total = timezone.timedelta(0)
        all_scopes = self.get_merged_timetable()
        for dt_scope in all_scopes:
            total += dt_scope[1] - dt_scope[0]
        return total

    def __net_duration(self):
        """
        Main logic of calculating net_duration value.

        1. Get the flat list of all node_tasks of this particular parent
            (children and any grandchildren).
        2. Sort by 'start_date'
        3. Merge of tasks that run together,
            we can eliminate repeated time calculations.
        4. Count total net time

        Returns:
            total(datetime.timedelta): net duration value
        """
        merged_subtasks = Task.merge_subtasks_by_scope(
            Task.sort_flat_children_by_start_date(
                self.get_flat_subtasks_list()
            )
        )

        total = timezone.timedelta(0)
        for subtask in merged_subtasks:
            print(subtask)
            total += subtask[1] - subtask[0]
        return total

    def get_flat_subtasks_list(self):
            all = []
            for sub_task in self.subtasks.all():
                if not sub_task.subtasks.all():
                    all.append(sub_task)
                else:
                    all.extend(sub_task.get_flat_subtasks_list())
            return all

    @staticmethod
    def sort_flat_children_by_start_date(subtasks_flat_list):
        subtasks_flat_list = sorted(subtasks_flat_list,
                                    key=lambda x: x.start_date)
        return subtasks_flat_list

    @staticmethod
    def merge_subtasks_by_scope(sorted_list):
        merged_scopes = []
        for subtask_scope in sorted_list:
            Task.__merge_scopes(merged_scopes, subtask_scope)
        return merged_scopes

    def __merge_scopes(datetime_scopes: list, new_scope):
            if not datetime_scopes or \
                    (new_scope.start_date > datetime_scopes[-1][1]):
                datetime_scopes.append([new_scope.start_date, new_scope.end_date])
            elif new_scope.start_date <= datetime_scopes[-1][1] and \
                (new_scope.end_date > datetime_scopes[-1][1]):
                datetime_scopes[-1][1] = new_scope.end_date

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError('End date should be after start date.')


@receiver(post_save, sender=Task)
def update_parent_timetable(sender, instance, **kwargs):
    """Update start_date and end_date
    values of parent nodes in the tree of tasks."""
    if instance.parent:
        instance.parent.start_date = instance.parent.subtasks.order_by('start_date').first().start_date
        instance.parent.end_date = instance.parent.subtasks.order_by('-end_date').first().end_date

        instance.parent.save()


