import json
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import FormView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from redactor.forms import ImageForm
from redactor.utils import import_class


class RedactorUploadView(FormView):
    form_class = ImageForm
    http_method_names = ('post',)
    upload_to = getattr(settings, 'REDACTOR_UPLOAD', 'redactor/')
    upload_handler = getattr(
        settings,
        'REDACTOR_UPLOAD_HANDLER',
        'redactor.handlers.SimpleUploader'
    )
    response = lambda name, url: url

    @method_decorator(csrf_exempt)
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(RedactorUploadView, self).dispatch(
            request,
            *args,
            **kwargs
        )

    def form_valid(self, form):
        handler_class = import_class(self.upload_handler)
        uploader = handler_class(form.cleaned_data['file'])
        uploader.save_file()
        return HttpResponse(
            json.dumps({
                "filename": uploader.get_filename().encode('utf-8'),
                "filelink": uploader.get_url(),
            }),
            content_type='application/json'
        )
