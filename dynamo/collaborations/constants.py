"""COLLABORATION STATUS"""

COLLABORATION_STATUS_PLANNING: str = "Planning"
COLLABORATION_STATUS_ONGOING: str = "Ongoing"
COLLABORATION_STATUS_COMPLETED: str = "Completed"
COLLABORATION_STATUS_ALL: str = "All"  # Used for filtering

COLLABORATION_STATUS_CHOICES: tuple = (
    (COLLABORATION_STATUS_PLANNING, "Planning"),
    (COLLABORATION_STATUS_ONGOING, "Ongoing"),
    (COLLABORATION_STATUS_COMPLETED, "Completed"),
)

"""COLLABORATION ELEMENT TYPES"""

COLLABORATION_ELEMENT_TYPE_TASK: str = "Task"
COLLABORATION_ELEMENT_TYPE_MILESTONE: str = "Milestone"

COLLABORATION_ELEMENT_TYPE_CHOICES: tuple = (
    (COLLABORATION_ELEMENT_TYPE_TASK, "Task"),
    (COLLABORATION_ELEMENT_TYPE_MILESTONE, "Milestone"),
)

"""COLLABORATION FILE FORMATS"""

FILE_FORMAT_PDF: str = ".pdf"
FILE_FORMAT_PPT: str = ".ppt"
FILE_FORMAT_DOCX: str = ".doc/doc"
FILE_FORMAT_TXT: str = ".txt"

FILE_FORMAT_CHOICES: tuple = (
    (FILE_FORMAT_PDF, ".pdf"),
    (FILE_FORMAT_PPT, ".ppt"),
    (FILE_FORMAT_DOCX, ".doc/doc"),
    (FILE_FORMAT_TXT, ".txt"),
)

"""MILESTONE STATUS"""

MILESTONE_STATUS_ON_TARGET: str = "On Target"
MILESTONE_STATUS_BEHIND_TARGET: str = "Behind Target"
MILESTONE_STATUS_REACHED: str = "Reached"
