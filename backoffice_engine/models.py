from django.db import models

# Create your models here.
class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class User(BaseModel):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=10)
    phone = models.CharField(max_length=10, blank=True)
    address = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    dob = models.DateField(null=True, blank=True)
    otp = models.CharField(null=True, blank=True)
    otp_used = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'user'

    def __str__(self):
        return f"{self.id} - {self.name} - {self.email}"


class Plandetail(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True,blank=True)
    price = models.IntegerField(null=False,blank=False)
    credits = models.IntegerField(default=10)
    duration_days = models.IntegerField(null=False,blank=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table ="plan_detail"
        verbose_name = "Plan Detail"
        verbose_name_plural = "Plan Details"
    
    def __str__(self):
        return f"{self.id} - {self.name}"


class Subscription(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plandetail, on_delete=models.CASCADE)
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()
    status = models.CharField(max_length=20, default='ACTIVE') 
    is_active = models.BooleanField(default=True)
    pending_credits = models.IntegerField(default=0)

    class Meta:
        db_table ="subscription"

    def __str__(self):
        return f"{self.plan}"


class Feedback(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()

    class Meta:
        db_table ="feedback"
    
    def __str__(self):
        return f"User: {self.user.name} | Feedback: {self.comment}"


class Profile(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to="backoffice_engine/user_file",null=True,blank=True)
    resume_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table ="profile"

    def __str__(self):
        return f"{self.id} - {self.name} - {self.email}"

class Interview(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    completed = models.BooleanField(default=False)

    class Meta:
        db_table ="interview"

    def __str__(self):
        return f"{self.id} - User: {self.user.name} - Resume ID: {self.resume.id}"

class InterviewResult(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.ForeignKey(Profile, on_delete=models.CASCADE)
    total_questions = models.CharField(max_length=255,null=True,blank=True)
    confidence_level = models.CharField(max_length=255,null=True,blank=True)
    time_taken = models.CharField(max_length=255,null=True,blank=True)
    overall_rating = models.CharField(max_length=255,null=True,blank=True)
    submitted_at = models.CharField(max_length=255,null=True,blank=True)
    final_result = models.TextField()

    class Meta:
        db_table = "interview_result"
        ordering = ['-submitted_at']

    def __str__(self):
        return f"\{self.id} - User: {self.user.username} - Resume ID: {self.resume.id} - Rating: {self.overall_rating}"
    

    