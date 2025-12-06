from django.db import models
from django.contrib.auth.models import User

class ParkingSlot(models.Model):
    slot_number = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Slot {self.slot_number}"

class Booking(models.Model):
    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking_date = models.DateField()
    start_hour = models.IntegerField()  # E.g., 8 for 8 AM
    end_hour = models.IntegerField()    # E.g., 11 for 11 AM

    def __str__(self):
        return f"{self.user.username} - {self.slot} [{self.booking_date}] ({self.start_hour}-{self.end_hour})"
