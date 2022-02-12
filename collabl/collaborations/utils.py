from collaborations.models import CollaborationTask, CollaborationMilestone
from itertools import chain

from django.db.models import F
from django.db.models import Value, CharField
from django.db.models.expressions import Window
from django.db.models.functions import Rank


def get_all_elements(collaboration):
    """
    This function works in three steps to produce a combined, ordered list of Tasks & Milestones
    """

    # 1. Get all Tasks, and annotate them with the type ('Task'), and their task number - which is determined by their
    # position in relation to the other tasks, rather than by their 'position' field, which orders them according to
    # position with milestones also (and is zero indexed.)
    tasks = CollaborationTask.objects.filter(collaboration=collaboration).annotate(
        type=Value('Task', output_field=CharField()), number=Window(
            expression=Rank(),
            order_by=F('position').asc()
        ))

    # 2. Get all Milestones, and annotate them with the type ('Milestone')
    milestones = CollaborationMilestone.objects.filter(collaboration=collaboration).annotate(
        type=Value('Milestone', output_field=CharField()))

    # 3. Chain the lists together, and sort them by their position field (in reverse)
    element_list = sorted(
        chain(tasks, milestones),
        key=lambda element: element.position)
    return element_list
