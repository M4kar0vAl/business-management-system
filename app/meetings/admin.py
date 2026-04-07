from sqladmin import Admin, ModelView

from app.meetings.models import Meeting


class MeetingAdmin(ModelView, model=Meeting):
    column_list = (Meeting.id, Meeting.start_time, Meeting.end_time, Meeting.created_by)
    column_default_sort = (Meeting.start_time, True)


def register_admin_views(admin: Admin):
    admin.add_view(MeetingAdmin)
