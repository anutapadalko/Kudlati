from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

class UserProfile(models.Model):
    B2C = "B2C"
    B2B = "B2B"
    PROFILE_TYPE = {
        B2B: "Business user",
        B2C: "Regular user"
    }

    WWW = "WWW"
    INS = "INS"
    MRK = "MRK"
    TKT = "TKT"
    OTH = "OTH"
    SOURCE_OF_ATTRACTION = {
        WWW: "Web site",
        INS: "Instagram",
        MRK: "Marketplace",
        TKT: "TikTok",
        OTH: "Other"
    }

    NEW = "NEW"
    REP = "REP"
    OLD = "OLD"
    PROFILE_STATUS = {
        NEW: "New", # перша покупка за останні 30 діб або відсутність покупок за останні 30 діб
        REP: "Repeat", # 2+ покупки
        OLD: "Old" # відсутні покупки > 90 діб
    }

    created_at = models.DateTimeField(auto_now_add=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_type = models.CharField(max_length=3, choices=PROFILE_TYPE)
    source_of_attraction = models.CharField(max_length=3, choices=SOURCE_OF_ATTRACTION, null=True, blank=True)
    profile_status = models.CharField(max_length=3, choices=PROFILE_STATUS, default=NEW)
    phone = PhoneNumberField(blank=True)
    delivery_address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}" or self.user.email
