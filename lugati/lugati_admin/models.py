from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic

class PasswordRestoreRequest(models.Model):
    user = models.ForeignKey(User)
    code = models.CharField(max_length=100)
    dt_add = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ['-dt_add']

class LugatiEvent(models.Model):
    cart_id = models.CharField(max_length=60,  blank=True, null=True)
    update_iteration = models.IntegerField(default=1)

    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    # test_field = models.CharField(max_length=50, blank=True, null=True)

    dt_modify = models.DateTimeField(auto_now=True)
    dt_add = models.DateTimeField(auto_now_add=True, editable=False)

    def save(self, *args, **kwargs):
        if self.update_iteration:
            self.update_iteration += 1
        else:
            self.update_iteration = 1
        super(LugatiEvent, self).save(*args, **kwargs)

class Tooltip(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    text = models.TextField()

    def get_list_item_info(self, request=None):
        node = {
            'id': self.name,
            'content_type_id': ContentType.objects.get_for_model(Tooltip).id,
            'name': self.name,
            'styled_name': self.text,
            'show': True
        }

        if request:
            if request.user.is_authenticated():
                try:
                    tooltip_show = TooltipShow.objects.get(tooltip=self, user=request.user)
                except:
                    tooltip_show = TooltipShow()
                    tooltip_show.user = request.user
                    tooltip_show.tooltip = self
                    tooltip_show.save()

                # if tooltip_show.show:
                node['show'] = tooltip_show.show
                # else:
                #     node['show'] = True

                if tooltip_show.csrftoken:
                    node['csrftoken'] = str(tooltip_show.csrftoken)
                else:
                    node['csrftoken'] = ''

                # if tooltip_show.show_in_session:
                node['show_in_session'] = tooltip_show.show_in_session
                # else:
                #     node['show_in_session'] = True

        return node

class TooltipShow(models.Model):

    tooltip = models.ForeignKey(Tooltip)
    user = models.ForeignKey(User)
    show_in_session = models.BooleanField(default=True)
    csrftoken = models.CharField(max_length=100, blank=True, null=True)
    show = models.BooleanField(default=True)

    def get_list_item_info(self, request=None):

        node = {
            'id': self.id,
            'content_type_id': ContentType.objects.get_for_model(TooltipShow).id,
            'show': self.show,
            'tooltip': self.tooltip.get_list_item_info(request)
        }

        return node