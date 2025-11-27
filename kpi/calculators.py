"""
KPI calculation logic.
"""
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Count, Avg, Q, Sum
from leads.models import Lead, Seller
from .models import KPIRule, KPICalculation, SellerKPISummary


class KPICalculator:
    """Handles automatic KPI calculation with bonuses and penalties."""
    
    @staticmethod
    def calculate_rule_value(seller: Seller, rule: KPIRule, period_start, period_end) -> Decimal:
        """Calculate the actual value for a rule based on seller's performance."""
        leads = Lead.objects.filter(
            seller=seller,
            created_at__gte=period_start,
            created_at__lte=period_end
        )
        
        if rule.rule_type == 'conversion_rate':
            total = leads.count()
            converted = leads.filter(status='converted').count()
            if total > 0:
                return Decimal(converted) / Decimal(total) * Decimal('100')
            return Decimal('0.00')
        
        elif rule.rule_type == 'leads_contacted':
            return Decimal(leads.filter(status__in=['contacted', 'qualified', 'converted']).count())
        
        elif rule.rule_type == 'leads_converted':
            return Decimal(leads.filter(status='converted').count())
        
        elif rule.rule_type == 'response_time':
            # Average response time in hours (simplified - would need actual response tracking)
            contacted_leads = leads.filter(
                status__in=['contacted', 'qualified', 'converted'],
                contacted_at__isnull=False
            )
            if contacted_leads.exists():
                # Calculate average time from creation to contact
                total_hours = Decimal('0')
                count = 0
                for lead in contacted_leads:
                    if lead.contacted_at:
                        delta = lead.contacted_at - lead.created_at
                        total_hours += Decimal(str(delta.total_seconds() / 3600))
                        count += 1
                if count > 0:
                    return total_hours / Decimal(str(count))
            return Decimal('999.99')  # High value if no contacts
        
        elif rule.rule_type == 'revenue':
            # Placeholder - would need revenue tracking
            return Decimal('0.00')
        
        return Decimal('0.00')
    
    @staticmethod
    def evaluate_rule(actual_value: Decimal, rule: KPIRule) -> bool:
        """Check if a rule is met based on actual value and threshold."""
        if rule.comparison == 'gte':
            return actual_value >= rule.threshold_value
        elif rule.comparison == 'lte':
            return actual_value <= rule.threshold_value
        elif rule.comparison == 'eq':
            return actual_value == rule.threshold_value
        elif rule.comparison == 'between':
            return rule.threshold_min <= actual_value <= rule.threshold_max
        
        return False
    
    @staticmethod
    def calculate_for_seller_rule(seller: Seller, rule: KPIRule, period_start=None, period_end=None):
        """Calculate KPI for a specific seller and rule."""
        if not period_end:
            period_end = timezone.now()
        if not period_start:
            period_start = period_end - timedelta(days=rule.evaluation_period_days)
        
        # Calculate actual value
        actual_value = KPICalculator.calculate_rule_value(seller, rule, period_start, period_end)
        
        # Get threshold value
        if rule.comparison == 'between':
            threshold_value = rule.threshold_max  # Use max for display
        else:
            threshold_value = rule.threshold_value
        
        # Evaluate rule
        rule_met = KPICalculator.evaluate_rule(actual_value, rule)
        
        # Calculate financial impact
        bonus_amount = rule.bonus_amount if rule_met else Decimal('0.00')
        penalty_amount = rule.penalty_amount if not rule_met else Decimal('0.00')
        net_amount = bonus_amount - penalty_amount
        
        # Create or update calculation record
        calculation, created = KPICalculation.objects.update_or_create(
            seller=seller,
            rule=rule,
            period_start=period_start,
            period_end=period_end,
            defaults={
                'actual_value': actual_value,
                'threshold_value': threshold_value,
                'rule_met': rule_met,
                'bonus_amount': bonus_amount,
                'penalty_amount': penalty_amount,
                'net_amount': net_amount,
            }
        )
        
        return calculation
    
    @staticmethod
    def calculate_all_active_rules(seller: Seller = None, period_start=None, period_end=None):
        """Calculate all active KPI rules for sellers."""
        sellers = [seller] if seller else Seller.objects.filter(is_active=True)
        rules = KPIRule.objects.filter(is_active=True)
        
        if not period_end:
            period_end = timezone.now()
        
        calculations = []
        for seller_obj in sellers:
            for rule in rules:
                if not period_start:
                    period_start = period_end - timedelta(days=rule.evaluation_period_days)
                
                calculation = KPICalculator.calculate_for_seller_rule(
                    seller_obj, rule, period_start, period_end
                )
                calculations.append(calculation)
        
        return calculations
    
    @staticmethod
    def calculate_monthly_summary(seller: Seller, month_date=None):
        """Calculate monthly KPI summary for a seller."""
        if not month_date:
            month_date = timezone.now().date().replace(day=1)
        else:
            month_date = month_date.replace(day=1)
        
        period_start = timezone.make_aware(datetime.combine(month_date, datetime.min.time()))
        if month_date.month == 12:
            next_month = month_date.replace(year=month_date.year + 1, month=1)
        else:
            next_month = month_date.replace(month=month_date.month + 1)
        period_end = timezone.make_aware(datetime.combine(next_month, datetime.min.time()))
        
        # Get all calculations for this period
        calculations = KPICalculation.objects.filter(
            seller=seller,
            period_start__gte=period_start,
            period_start__lt=period_end
        )
        
        # Aggregate financials
        total_bonus = calculations.aggregate(Sum('bonus_amount'))['bonus_amount__sum'] or Decimal('0.00')
        total_penalty = calculations.aggregate(Sum('penalty_amount'))['penalty_amount__sum'] or Decimal('0.00')
        net_amount = total_bonus - total_penalty
        
        # Calculate lead statistics
        leads = Lead.objects.filter(
            seller=seller,
            created_at__gte=period_start,
            created_at__lt=period_end
        )
        total_leads = leads.count()
        converted_leads = leads.filter(status='converted').count()
        conversion_rate = (Decimal(converted_leads) / Decimal(total_leads) * Decimal('100')) if total_leads > 0 else Decimal('0.00')
        
        # Create or update summary
        summary, created = SellerKPISummary.objects.update_or_create(
            seller=seller,
            month=month_date,
            defaults={
                'total_bonus': total_bonus,
                'total_penalty': total_penalty,
                'net_amount': net_amount,
                'total_leads': total_leads,
                'converted_leads': converted_leads,
                'conversion_rate': conversion_rate,
            }
        )
        
        return summary

