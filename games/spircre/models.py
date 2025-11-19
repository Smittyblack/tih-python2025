from django.db import models

class PlayerProgress(models.Model):
    user_id = models.IntegerField()
    woodcutting_xp = models.BigIntegerField(default=0)
    mining_xp = models.BigIntegerField(default=0)
    fishing_xp = models.BigIntegerField(default=0)
    cooking_xp = models.BigIntegerField(default=0)
    smithing_xp = models.BigIntegerField(default=0)
    attack_xp = models.BigIntegerField(default=0)
    strength_xp = models.BigIntegerField(default=0)
    defence_xp = models.BigIntegerField(default=0)
    hitpoints_xp = models.BigIntegerField(default=10000)
    last_active = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'spircre'

    def __str__(self):
        return f"Progress for user ID {self.user_id}"

class HighScore(models.Model):
    user_id = models.IntegerField(unique=True)  # Ensure uniqueness
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'spircre'
        ordering = ['-score']

    def __str__(self):
        return f"Score {self.score} for user ID {self.user_id}"

class Inventory(models.Model):
    user_id = models.IntegerField()
    item_name = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)

    class Meta:
        app_label = 'spircre'
        unique_together = ('user_id', 'item_name')

    def __str__(self):
        return f"{self.quantity} {self.item_name} for user ID {self.user_id}"