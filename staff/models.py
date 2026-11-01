"""
Staff models for FixSoftRepair
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User


class StaffMember(models.Model):
    """Staff member model with detailed information"""
    
    class Department(models.TextChoices):
        TECHNICAL = 'TECHNICAL', _('Technical')
        SALES = 'SALES', _('Sales')
        ADMINISTRATION = 'ADMINISTRATION', _('Administration')
        MANAGEMENT = 'MANAGEMENT', _('Management')
    
    class EmploymentStatus(models.TextChoices):
        FULL_TIME = 'FULL_TIME', _('Full Time')
        PART_TIME = 'PART_TIME', _('Part Time')
        CONTRACTOR = 'CONTRACTOR', _('Contractor')
        INTERN = 'INTERN', _('Intern')
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff_member',
        verbose_name=_('User')
    )
    
    employee_id = models.CharField(
        _('Employee ID'),
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )
    
    telephone = models.CharField(
        _('Telephone'),
        max_length=20,
        blank=True,
        null=True
    )
    
    address = models.TextField(
        _('Address'),
        blank=True,
        null=True
    )
    
    city = models.CharField(
        _('City'),
        max_length=100,
        blank=True,
        null=True
    )
    
    postal_code = models.CharField(
        _('Postal Code'),
        max_length=20,
        blank=True,
        null=True
    )
    
    department = models.CharField(
        _('Department'),
        max_length=20,
        choices=Department.choices,
        default=Department.TECHNICAL
    )
    
    position = models.CharField(
        _('Position'),
        max_length=100,
        blank=True,
        null=True
    )
    
    employment_status = models.CharField(
        _('Employment Status'),
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.FULL_TIME
    )
    
    hire_date = models.DateField(
        _('Hire Date'),
        blank=True,
        null=True
    )
    
    termination_date = models.DateField(
        _('Termination Date'),
        blank=True,
        null=True
    )
    
    salary = models.DecimalField(
        _('Salary'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    
    commission_rate = models.DecimalField(
        _('Commission Rate'),
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    skills = models.TextField(
        _('Skills'),
        blank=True,
        null=True,
        help_text=_('Comma separated list of skills')
    )
    
    specialties = models.TextField(
        _('Specialties'),
        blank=True,
        null=True,
        help_text=_('Comma separated list of specialties')
    )
    
    work_schedule = models.TextField(
        _('Work Schedule'),
        blank=True,
        null=True,
        help_text=_('Description of work schedule')
    )
    
    performance_rating = models.PositiveSmallIntegerField(
        _('Performance Rating'),
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_('Rating from 1 to 5')
    )
    
    notes = models.TextField(
        _('Notes'),
        blank=True,
        null=True
    )
    
    is_active = models.BooleanField(
        _('Active'),
        default=True
    )
    
    date_created = models.DateTimeField(
        _('Date Created'),
        auto_now_add=True
    )
    
    date_updated = models.DateTimeField(
        _('Date Updated'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('Staff Member')
        verbose_name_plural = _('Staff Members')
        ordering = ['-date_created']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_department_display()})"
    
    def get_full_name(self):
        return self.user.get_full_name()
    
    def get_employee_info(self):
        return f"{self.employee_id} - {self.get_full_name()}"
    
    def get_skills_list(self):
        """Return skills as list"""
        if self.skills:
            return [skill.strip() for skill in self.skills.split(',') if skill.strip()]
        return []
    
    def get_specialties_list(self):
        """Return specialties as list"""
        if self.specialties:
            return [spec.strip() for spec in self.specialties.split(',') if spec.strip()]
        return []
