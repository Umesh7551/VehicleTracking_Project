from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


# @receiver(post_save, sender=User)
# def deactivate_related_users(sender, instance, **kwargs):
#     # Check if the user was deactivated
#     if not instance.is_active:
#         # Check if the user belongs to the 'fleetowner' group
#         if instance.groups.filter(name='fleetowner').exists():
#             # Find all users in the 'fleetowner support' group
#             fleetowner_support_group = Group.objects.get(name='fleetowner_support_person')
#             fleetowner_support_users = User.objects.filter(groups=fleetowner_support_group)
#
#             # Deactivate all users in the 'fleetowner_support_person' group
#             for support_user in fleetowner_support_users:
#                 support_user.is_active = False
#                 support_user.save()


@receiver(post_save, sender=User)
def toggle_related_users_activation(sender, instance, **kwargs):
    # Check if the user belongs to the 'fleetowner' group
    if instance.groups.filter(name='fleetowner').exists():
        # Find all users in the 'fleetowner support' group
        fleetowner_support_group = Group.objects.get(name='fleetowner_support_person')
        fleetowner_support_users = User.objects.filter(groups=fleetowner_support_group)

        if instance.is_active:
            # If fleetowner is reactivated, reactivate fleetowner support users
            for support_user in fleetowner_support_users:
                support_user.is_active = True
                support_user.save()
        else:
            # If fleetowner is deactivated, deactivate fleetowner support users
            for support_user in fleetowner_support_users:
                support_user.is_active = False
                support_user.save()
