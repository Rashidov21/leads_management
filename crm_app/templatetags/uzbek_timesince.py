from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def uzbek_timesince(value):
    """
    Vaqtni o'zbek tilida ko'rsatish
    Masalan: "1 soat 5 daqiqa oldin"
    """
    if not value:
        return ""
    
    now = timezone.now()
    
    # Agar value datetime bo'lmasa, uni datetime'ga o'girish
    if hasattr(value, 'tzinfo') and value.tzinfo is None:
        value = timezone.make_aware(value)
    
    # Vaqt farqi
    delta = now - value
    
    # Agar kelajakda bo'lsa
    if delta.total_seconds() < 0:
        return "hozir"
    
    # Sekundlar
    total_seconds = int(delta.total_seconds())
    
    # Bir necha soniya oldin
    if total_seconds < 60:
        return "hozirgina"
    
    # Daqiqalar
    total_minutes = total_seconds // 60
    if total_minutes < 60:
        if total_minutes == 1:
            return "1 daqiqa oldin"
        return f"{total_minutes} daqiqa oldin"
    
    # Soatlar
    total_hours = total_minutes // 60
    remaining_minutes = total_minutes % 60
    
    if total_hours < 24:
        if total_hours == 1:
            if remaining_minutes == 0:
                return "1 soat oldin"
            elif remaining_minutes == 1:
                return "1 soat 1 daqiqa oldin"
            else:
                return f"1 soat {remaining_minutes} daqiqa oldin"
        else:
            if remaining_minutes == 0:
                return f"{total_hours} soat oldin"
            elif remaining_minutes == 1:
                return f"{total_hours} soat 1 daqiqa oldin"
            else:
                return f"{total_hours} soat {remaining_minutes} daqiqa oldin"
    
    # Kunlar
    total_days = total_hours // 24
    remaining_hours = total_hours % 24
    
    if total_days < 30:
        if total_days == 1:
            if remaining_hours == 0:
                return "1 kun oldin"
            elif remaining_hours == 1:
                return "1 kun 1 soat oldin"
            else:
                return f"1 kun {remaining_hours} soat oldin"
        else:
            if remaining_hours == 0:
                return f"{total_days} kun oldin"
            elif remaining_hours == 1:
                return f"{total_days} kun 1 soat oldin"
            else:
                return f"{total_days} kun {remaining_hours} soat oldin"
    
    # Oylar
    total_months = total_days // 30
    remaining_days = total_days % 30
    
    if total_months < 12:
        if total_months == 1:
            if remaining_days == 0:
                return "1 oy oldin"
            elif remaining_days == 1:
                return "1 oy 1 kun oldin"
            else:
                return f"1 oy {remaining_days} kun oldin"
        else:
            if remaining_days == 0:
                return f"{total_months} oy oldin"
            elif remaining_days == 1:
                return f"{total_months} oy 1 kun oldin"
            else:
                return f"{total_months} oy {remaining_days} kun oldin"
    
    # Yillar
    total_years = total_months // 12
    remaining_months = total_months % 12
    
    if total_years == 1:
        if remaining_months == 0:
            return "1 yil oldin"
        elif remaining_months == 1:
            return "1 yil 1 oy oldin"
        else:
            return f"1 yil {remaining_months} oy oldin"
    else:
        if remaining_months == 0:
            return f"{total_years} yil oldin"
        elif remaining_months == 1:
            return f"{total_years} yil 1 oy oldin"
        else:
            return f"{total_years} yil {remaining_months} oy oldin"


@register.filter
def uzbek_timeuntil(value):
    """
    Kelajakdagi vaqtni o'zbek tilida ko'rsatish
    Masalan: "1 soat 5 daqiqadan keyin"
    """
    if not value:
        return ""
    
    now = timezone.now()
    
    # Agar value datetime bo'lmasa, uni datetime'ga o'girish
    if hasattr(value, 'tzinfo') and value.tzinfo is None:
        value = timezone.make_aware(value)
    
    # Vaqt farqi
    delta = value - now
    
    # Agar o'tgan bo'lsa
    if delta.total_seconds() < 0:
        return "vaqt o'tib ketgan"
    
    # Sekundlar
    total_seconds = int(delta.total_seconds())
    
    # Bir necha soniya
    if total_seconds < 60:
        return "hozir"
    
    # Daqiqalar
    total_minutes = total_seconds // 60
    if total_minutes < 60:
        if total_minutes == 1:
            return "1 daqiqadan keyin"
        return f"{total_minutes} daqiqadan keyin"
    
    # Soatlar
    total_hours = total_minutes // 60
    remaining_minutes = total_minutes % 60
    
    if total_hours < 24:
        if total_hours == 1:
            if remaining_minutes == 0:
                return "1 soatdan keyin"
            elif remaining_minutes == 1:
                return "1 soat 1 daqiqadan keyin"
            else:
                return f"1 soat {remaining_minutes} daqiqadan keyin"
        else:
            if remaining_minutes == 0:
                return f"{total_hours} soatdan keyin"
            elif remaining_minutes == 1:
                return f"{total_hours} soat 1 daqiqadan keyin"
            else:
                return f"{total_hours} soat {remaining_minutes} daqiqadan keyin"
    
    # Kunlar
    total_days = total_hours // 24
    remaining_hours = total_hours % 24
    
    if total_days < 30:
        if total_days == 1:
            if remaining_hours == 0:
                return "1 kundan keyin"
            elif remaining_hours == 1:
                return "1 kun 1 soatdan keyin"
            else:
                return f"1 kun {remaining_hours} soatdan keyin"
        else:
            if remaining_hours == 0:
                return f"{total_days} kundan keyin"
            elif remaining_hours == 1:
                return f"{total_days} kun 1 soatdan keyin"
            else:
                return f"{total_days} kun {remaining_hours} soatdan keyin"
    
    # Oylar
    total_months = total_days // 30
    remaining_days = total_days % 30
    
    if total_months < 12:
        if total_months == 1:
            if remaining_days == 0:
                return "1 oydan keyin"
            elif remaining_days == 1:
                return "1 oy 1 kundan keyin"
            else:
                return f"1 oy {remaining_days} kundan keyin"
        else:
            if remaining_days == 0:
                return f"{total_months} oydan keyin"
            elif remaining_days == 1:
                return f"{total_months} oy 1 kundan keyin"
            else:
                return f"{total_months} oy {remaining_days} kundan keyin"
    
    # Yillar
    total_years = total_months // 12
    remaining_months = total_months % 12
    
    if total_years == 1:
        if remaining_months == 0:
            return "1 yildan keyin"
        elif remaining_months == 1:
            return "1 yil 1 oydan keyin"
        else:
            return f"1 yil {remaining_months} oydan keyin"
    else:
        if remaining_months == 0:
            return f"{total_years} yildan keyin"
        elif remaining_months == 1:
            return f"{total_years} yil 1 oydan keyin"
        else:
            return f"{total_years} yil {remaining_months} oydan keyin"

