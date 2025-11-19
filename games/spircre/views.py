import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import PlayerProgress, HighScore, Inventory
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

def calculate_level(xp):
    if xp < 0:
        return 1
    level = 1
    required_xp = 0
    while xp >= required_xp:
        if level == 1:
            required_xp = 100
        else:
            required_xp += 100 * (2 ** (level - 2))
        if xp < required_xp:
            break
        level += 1
    return level

def xp_for_next_level(current_level):
    if current_level == 1:
        return 100
    return 100 * (2 ** (current_level - 1))

def calculate_progress(xp, level):
    xp_needed = xp_for_next_level(level)
    previous_xp = sum(100 * (2 ** (i - 1)) for i in range(1, level)) if level > 1 else 0
    progress_percent = ((xp - previous_xp) / xp_needed) * 100
    return min(progress_percent, 100)

@login_required
def spircre_game(request):
    progress, created = PlayerProgress.objects.using('game_scores').get_or_create(user_id=request.user.id)
    skills = ['woodcutting', 'mining', 'fishing', 'cooking', 'smithing', 'attack', 'strength', 'defence', 'hitpoints']

    time_diff = (timezone.now() - progress.last_active).total_seconds() / 60
    offline_minutes = min(time_diff, 1440)
    offline_xp = int(offline_minutes)

    if request.method == 'POST':
        action = request.POST.get('action')
        skill = request.POST.get('skill')
        xp = int(request.POST.get('xp', 0))
        reward = json.loads(request.POST.get('reward', '{}'))
        logger.info(f"POST request: action={action}, skill={skill}, xp={xp}, reward={reward}")

        if action == 'train' and skill in skills:
            # Update XP
            field = f"{skill}_xp"
            current_xp = getattr(progress, field)
            new_xp = current_xp + xp
            setattr(progress, field, new_xp)
            progress.save(using='game_scores')

            # Update inventory
            for item, qty in reward.items():
                inv, _ = Inventory.objects.using('game_scores').get_or_create(user_id=request.user.id, item_name=item)
                inv.quantity += qty
                inv.save(using='game_scores')

            # Update high score
            total_level = sum(calculate_level(getattr(progress, f"{s}_xp")) for s in skills)
            try:
                HighScore.objects.using('game_scores').update_or_create(
                    user_id=request.user.id, defaults={'score': total_level}
                )
            except Exception as e:
                logger.error(f"Error updating HighScore: {e}")

            level = calculate_level(new_xp)
            progress_percent = calculate_progress(new_xp, level)
            return JsonResponse({
                'status': 'success',
                'xp': new_xp,
                'level': level,
                'progress': progress_percent
            })

    progress.woodcutting_xp += offline_xp
    progress.save(using='game_scores')

    levels = {skill: calculate_level(getattr(progress, f"{skill}_xp")) for skill in skills}
    progress_data = {skill: calculate_progress(getattr(progress, f"{skill}_xp"), levels[skill]) for skill in skills}
    progress_xp = {skill: getattr(progress, f"{skill}_xp") for skill in skills}

    context = {
        'progress': progress,
        'progress_xp': progress_xp,
        'levels': levels,
        'progress_data': progress_data
    }
    return render(request, 'spircre/game.html', context)

@login_required
def get_high_scores(request):
    high_scores = HighScore.objects.using('game_scores').all()[:10]
    from django.contrib.auth.models import User
    user_ids = [score.user_id for score in high_scores]
    users = User.objects.using('default').filter(id__in=user_ids)
    user_dict = {user.id: user.username for user in users}
    data = [{'username': user_dict.get(score.user_id, 'Unknown'), 'score': score.score} for score in high_scores]
    return JsonResponse({'high_scores': data})

@login_required
def get_inventory(request):
    inventory = Inventory.objects.using('game_scores').filter(user_id=request.user.id)
    data = [{'item_name': item.item_name, 'quantity': item.quantity} for item in inventory]
    return JsonResponse({'inventory': data})