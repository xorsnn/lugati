from django.shortcuts import render
from registration.backends.default.views import RegistrationView
from lugati.lugati_registration.forms import LugatiRegistrationForm
from django.conf import settings
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site

from registration import signals
from registration.models import RegistrationProfile
from registration.views import ActivationView as BaseActivationView
from registration.views import RegistrationView as BaseRegistrationView
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
import logging

logger = logging.getLogger(__name__)

class LugatiRegistrationView(RegistrationView):
    form_class = LugatiRegistrationForm

    def register(self, request, **cleaned_data):
        """
        Given a username, email address and password, register a new
        user account, which will initially be inactive.

        Along with the new ``User`` object, a new
        ``registration.models.RegistrationProfile`` will be created,
        tied to that ``User``, containing the activation key which
        will be used for this account.

        An email will be sent to the supplied email address; this
        email should contain an activation link. The email will be
        rendered using two templates. See the documentation for
        ``RegistrationProfile.send_activation_email()`` for
        information about these templates and the contexts provided to
        them.

        After the ``User`` and ``RegistrationProfile`` are created and
        the activation email is sent, the signal
        ``registration.signals.user_registered`` will be sent, with
        the new ``User`` as the keyword argument ``user`` and the
        class of this backend as the sender.

        """
        username, email, password = cleaned_data['username'], cleaned_data['email'], cleaned_data['password1']
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)

        new_user = RegistrationProfile.objects.create_inactive_user(username, email,
                                                                    password, site, False)

        #mail
        reg_prof = RegistrationProfile.objects.get(user=new_user)
        ctx_dict = {'activation_key': reg_prof.activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'site': site,
                    'cur_domain': settings.POS_SERVER,
                    'user': new_user}
        subject = render_to_string('registration/activation_email_subject.txt',
                                   ctx_dict)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        message = render_to_string('registration/activation_email.html',
                                   ctx_dict)

        # new_user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)

        emails = [new_user.email]
        message_html = message
        try:
            msg = EmailMultiAlternatives(subject, message_html, settings.DEFAULT_FROM_EMAIL, emails)
            #msg = EmailMultiAlternatives(subject, message_text, settings.DEFAULT_FROM_EMAIL, emails)
            msg.attach_alternative(message_html, "text/html")
            msg.send()
        except Exception, e:
            logger.error(str(e))
        #~mail

        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        return new_user
