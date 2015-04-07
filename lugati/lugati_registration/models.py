from django.db import models
from lugati.lugati_shop.models import Shop
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from lugati.lugati_shop.models import LugatiCompany
# from registration.models import RegistrationProfile
from lugati.lugati_shop.models import LugatiCurrency


class LugatiRole(models.Model):
    name = models.CharField(max_length=50)

class LugatiUserProfile(models.Model):
    user = models.ForeignKey(User)
    # shops = models.ManyToManyField(Shop)
    # main_shop = models.ForeignKey(Shop, blank=True, null=True, related_name="main_shop")
    roles = models.ManyToManyField(LugatiRole)
    company = models.ForeignKey(LugatiCompany, blank=True, null=True)
    license_accepted = models.BooleanField(default=False)

    def get_company(self):
        if not self.company:
            new_company = LugatiCompany()
            new_company.name = 'new company'
            new_company.default_currency = LugatiCurrency.objects.get(name="USD")
            new_company.save()
            self.company = new_company
            self.save()

        return self.company

def create_profile(sender, **kw):
    user = kw['instance']
    profs = LugatiUserProfile.objects.filter(user=user)
    if not profs.exists():
        prof = LugatiUserProfile()
        prof.user = kw['instance']
        prof.save()

        shop = Shop()
        shop.name = 'new shop'
        shop.company = prof.get_company()
        shop.save()

post_save.connect(create_profile, sender=User, dispatch_uid="users-profilecreation-signal")
