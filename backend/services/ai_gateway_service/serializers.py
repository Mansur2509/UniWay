from rest_framework import serializers


class MentorRequestSerializer(serializers.Serializer):
    class Purpose:
        ADMISSIONS = "admissions"
        ROADMAP = "roadmap"
        ESSAY_FEEDBACK = "essay_feedback"
        EVENTS = "events"
        RESEARCH = "research"
        ACTIVITIES = "activities"
        FINANCE_EDUCATION = "finance_education"
        CAREERS = "careers"

    purpose = serializers.ChoiceField(
        choices=(
            Purpose.ADMISSIONS,
            Purpose.ROADMAP,
            Purpose.ESSAY_FEEDBACK,
            Purpose.EVENTS,
            Purpose.RESEARCH,
            Purpose.ACTIVITIES,
            Purpose.FINANCE_EDUCATION,
            Purpose.CAREERS,
        )
    )
    message = serializers.CharField(min_length=1, max_length=6000, trim_whitespace=True)

    def validate_message(self, value):
        if "\x00" in value:
            raise serializers.ValidationError("Message contains unsupported characters.")
        return value

