from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin

from dojo.models import (
    Answer,
    Answered_Survey,
    Choice,
    ChoiceAnswer,
    ChoiceQuestion,
    Engagement_Survey,
    Question,
    TextAnswer,
    TextQuestion,
)

# LogEntry is now defined in dojo.legacy_auditlog and should not be registered in admin
# (it's read-only for backward compatibility)

# ==============================
# Defect Dojo Engaegment Surveys
# ==============================


class QuestionChildAdmin(PolymorphicChildModelAdmin):

    """Base admin class for all child models of Question"""

    base_model = Question


class TextQuestionAdmin(QuestionChildAdmin):

    """ModelAdmin for a TextQuestion"""


class ChoiceQuestionAdmin(QuestionChildAdmin):

    """ModelAdmin for a ChoiceQuestion"""


class QuestionParentAdmin(PolymorphicParentModelAdmin):

    """Question parent model admin"""

    base_model = Question
    child_models = (
        TextQuestion,
        ChoiceQuestion,
    )


admin.site.register(TextQuestion, TextQuestionAdmin)
admin.site.register(ChoiceQuestion, ChoiceQuestionAdmin)
admin.site.register(Question, QuestionParentAdmin)
admin.site.register(Choice)


class AnswerChildAdmin(PolymorphicChildModelAdmin):

    """Base admin class for all child Answer models"""

    base_model = Answer


class TextAnswerAdmin(AnswerChildAdmin):

    """ModelAdmin for TextAnswer"""


class ChoiceAnswerAdmin(AnswerChildAdmin):

    """ModelAdmin for ChoiceAnswer"""


class AnswerParentAdmin(PolymorphicParentModelAdmin):

    """The parent model admin for answer"""

    list_display = (
        "answered_survey",
        "question",
    )

    base_model = Answer
    child_models = (
        TextAnswer,
        ChoiceAnswer,
    )


admin.site.register(TextAnswer, TextAnswerAdmin)
admin.site.register(ChoiceAnswer, ChoiceAnswerAdmin)
admin.site.register(Answer, AnswerParentAdmin)
admin.site.register(Engagement_Survey)
admin.site.register(Answered_Survey)
