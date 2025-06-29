from django.shortcuts import render,redirect
from backoffice_engine.models import User, Plandetail, Subscription, Profile, Interview, Feedback, InterviewResult
from datetime import datetime, timedelta
from backoffice_engine.forms import userRegistrationForm, ProfileForm, FeedbackForm, User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .utils import text_to_text_structured_output, text_to_structured_questions, evaluate_response
from django.http import HttpResponse, JsonResponse
import time
from datetime import datetime, timedelta
import fitz,re
import google.generativeai as genai
from django import forms
import json
from datetime import date, timedelta
from django.utils.timezone import now
import random
from inquest import settings
from django.core.mail import send_mail
from django.template.loader import get_template
from xhtml2pdf import pisa


@csrf_exempt
def index(request):
    form = FeedbackForm()
    feedbacks = Feedback.objects.select_related('user').order_by('-created_at')[:10]

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user_id = request.session.get('id')
            feedback.save()
            return redirect('/feedback/')

    return render(request, 'index.html', {
        'form': form,
        'feedbacks': feedbacks
    })


def login(request):
    if request.method=="POST":
        uemail=request.POST["email"]
        pwd=request.POST["password"]
        u=User.objects.filter(email=uemail,password=pwd).count()
        if u== 1:
            user_object=User.objects.filter(email=uemail).first()
            request.session['id']=user_object.id
            request.session['name']=user_object.name
            request.session['email']=user_object.email
            user_subscription = Subscription.objects.filter(user=user_object, status="ACTIVE").first()
            if user_subscription:
                plan_object = user_subscription.plan
                request.session['plan']=plan_object.id
            
            return redirect("/index/")
        else:
            messages.error(request,"Invalid email or passsword")
    return render(request,"login.html")

def register(request):
    if request.method == 'POST':
        form = userRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            free_plan = Plandetail.objects.filter(price=0, is_active=True).first()
            if free_plan:
                start_time = datetime.now()
                end_time = start_time + timedelta(days=free_plan.duration_days)

                Subscription.objects.create(
                    user=user,
                    plan=free_plan,
                    start_date_time=start_time,
                    end_date_time=end_time,
                    status='ACTIVE',
                    pending_credits=free_plan.credits
                )
            return redirect("/login/")
    else:
        form = userRegistrationForm()
    return render(request, 'register.html', {'form': form})
    

def profile(request):
    user_id = request.session.get('id')
    if not user_id:
        return redirect('/login/')
    user = User.objects.get(id=user_id)
    subscription = Subscription.objects.filter(user=user, status='ACTIVE').first()
    if subscription:
        print(f"User Active Subscription Plan : {subscription.plan}")
    return render(request, 'profile.html', {'user': user,'subscription':subscription})

def about(request):
    return render(request,"about.html")

def pricing(request):
    plan_details = Plandetail.objects.filter(is_active=True)
    return render(request,"pricing.html", {"plan_details": plan_details})

def forgot(request):
    return render(request,"forgot-password.html")


def history(request):
    user_id = request.session.get("id")
    if not user_id:
        return redirect('/login/')

    user = User.objects.get(id=user_id)
    resumes = Profile.objects.filter(user=user).order_by("-created_at")

    history_data = []
    for resume in resumes:
        questions = Interview.objects.filter(user=user, resume=resume).order_by("created_at")
        result = InterviewResult.objects.filter(user=user, resume=resume).first()

        history_data.append({
            "resume": resume,
            "questions": questions,
            "result": result
        })

    return render(request, "history.html", {"history_data": history_data})

def download_history(request):
    user_id = request.session.get("id")
    if not user_id:
        return redirect("/login/")

    user = User.objects.get(id=user_id)
    resumes = Profile.objects.filter(user=user).order_by("-created_at")

    history_data = []
    for resume in resumes:
        questions = Interview.objects.filter(user=user, resume=resume).order_by("created_at")
        result = InterviewResult.objects.filter(user=user, resume=resume).first()

        history_data.append({
            "resume": resume,
            "questions": questions,
            "result": result
        })

    template_path = 'download_history.html'
    context = {'history_data': history_data}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="interview_history.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation error')
    return response


def service(request):
    return render(request,"services.html")

def service_details(request):
    return render(request,"service-details.html")

def team(request):
    return render(request,"team.html")

def testimonials(request):
    return render(request,"testimonials.html")

def assign_free_plan_if_expired(user):
    today = date.today()
    subscription = Subscription.objects.filter(user=user, status='ACTIVE').first()

    if subscription:
        credits_done = subscription.pending_credits <= 0
        expired = today >= subscription.end_date_time.date()

        if credits_done and expired:
            subscription.status = 'EXPIRED'
            subscription.save()

            free_plan = Plandetail.objects.filter(price=0, is_active=True).first()
            if free_plan:
                Subscription.objects.create(
                    user=user,
                    plan=free_plan,
                    start_date_time=today,
                    end_date_time=today + timedelta(days=free_plan.duration_days),
                    status='ACTIVE',
                    pending_credits=free_plan.credits
                )
                print("✅ Free plan assigned.")


def dashboard(request):
    total_users = User.objects.count()
    subscribed_users = Subscription.objects.filter(is_active=True).values('user').distinct().count()
    total_feedbacks = Feedback.objects.count()
    interviews = Interview.objects.count()
    seven_days_ago = now() - timedelta(days=7)
    new_users_this_week = User.objects.count()


    context = {
        'total_users': total_users,
        'subscribed_users': subscribed_users,
        'total_feedbacks': total_feedbacks,
        'interviews': interviews,
        'new_users_this_week': new_users_this_week,
    }

    return render(request, 'dashboard.html', context)

@csrf_exempt
def success(request):
    uid = request.POST.get("userid")
    pid = request.POST.get("planid")
    print("-----userid-----",uid,pid)

    p = Plandetail.objects.get(id=pid)

    sd= date.today()
    ed = sd + timedelta(days=p.duration_days)

    Subscription.objects.filter(user=uid).update(plan=pid,start_date_time=sd,end_date_time=ed,status='ACTIVE',pending_credits=p.credits)
    request.session["id"] = int(uid)
    request.session["plan"]=int(pid)

    return render (request,"success.html")


def edit_profile(request):
    user_id = request.session.get('id')
    if not user_id:
        return redirect('/login/')

    user = User.objects.get(id=user_id)
    if request.method == "POST":
        user.name = request.POST.get("name")
        user.email = request.POST.get("email")
        user.phone = request.POST.get("phone")
        user.address = request.POST.get("address")
        user.location = request.POST.get("location")
        user.dob = request.POST.get("dob")
        user.save()
        return redirect('/profile/')
    return render(request, 'edit-profile.html', {'user': user})

def logout(request):
    request.session.flush()
    return redirect('/login/')

def delete_account(request):
    user_id = request.session.get('id')
    if not user_id:
        return redirect('/register/')

    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            request.session.flush() 
            return redirect('/register/')
        except User.DoesNotExist:
            return redirect('/profile/')

    return redirect('/profile/')

def sendotp(request):
    if request.method == "POST":
        otp1 = random.randint(10000, 99999)
        e =  request.POST['email']

        request.session['temail']=e

        obj = User.objects.filter(email=e).count()

        if obj == 1:
            val = User.objects.filter(email=e).update(otp=otp1 , otp_used=0)
            subject = 'OTP Verification'
            message = str(otp1)
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [e, ]   

            send_mail(subject, message, email_from, recipient_list) 

            print("-----------------mail send---------------")
            return render(request,"reset-password.html")
        else:
            messages.error(request,"Invalid email Id")
            return render(request, "forgot-password.html")

    else:
        return render(request,"forgot-password.html")

        
def reset(request):
    if request.method == "POST":
        otp = request.POST["otp"]
        pwd = request.POST["new_password"]
        cpwd = request.POST["confirm_password"]
        e = request.session['temail']  

        val = User.objects.filter(email=e, otp=otp, otp_used=0).count()

        if val == 1:
            if pwd == cpwd:
                User.objects.filter(email=e).update(password=pwd, otp_used=1)
                return redirect("/login/")
            else:
                messages.error(request, "Password and confirm password do not match")
                return render(request, "reset-password.html")
        else:
            messages.error(request, "Invalid OTP")
            return render(request, "reset-password.html")
    return render(request, "reset-password.html")

genai.configure(api_key="AIzaSyBco8g2AIY68pqrOlqKb4qf9vXN5BCARmE")

def count_words(text):
    return len(re.findall(r"\b\w+\b", text))

def validate_questions_length(questions, min_words=10, max_words=15):
    valid = []
    invalid_indices = []
    for idx, q in enumerate(questions):
        wc = count_words(q)
        if min_words <= wc <= max_words:
            valid.append(q)
        else:
            invalid_indices.append(idx)
    return valid, invalid_indices

def upload_resume(request):
    if not request.session.get('id'):
        messages.warning(request, "Please log in to upload your resume and start the interview.")
        return redirect('/login/')
    user = User.objects.get(id=request.session.get("id"))
    assign_free_plan_if_expired(user)
    subscription = Subscription.objects.filter(user=user, status='ACTIVE').first()
    pending_credits = subscription.pending_credits if subscription else 0
    if request.method == 'POST':
        if subscription and pending_credits <= 0:
            messages.error(request, "You have no credits left. Please purchase a plan to continue.")
            return redirect('/pricing/')
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = form.cleaned_data['resume']
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            resume_text = "".join([page.get_text() for page in doc])

            prompt = (
                "Based on the following resume, generate 5 interview questions. "
                "Each question must be between 10 and 15 words (inclusive). "
                "Return the questions as a JSON array of strings, with no numbering or extra commentary.\n\n"
                + resume_text
            )
            all_questions = text_to_structured_questions(prompt)

            valid, invalid_idxs = validate_questions_length(all_questions, 10, 15)
            if invalid_idxs:
                for idx in invalid_idxs:
                    bad_q = all_questions[idx]
                    sub_prompt = (
                        f"The following interview question is not between 10 and 15 words: \"{bad_q}\".\n"
                        "Please rewrite this question so that it remains semantically similar but uses between 10 and 15 words.\n"
                        "Return only the rewritten question string."
                    )
                    rewritten = text_to_structured_questions(sub_prompt)
                    if isinstance(rewritten, list) and len(rewritten) > 0:
                        all_questions[idx] = rewritten[0]
            
            request.session['questions'] = all_questions
            request.session['current_index'] = 0
            request.session['start_time'] = time.time()

            data = form.save()
            data.resume_text = resume_text
            data.save()
            request.session['current_profile_id'] = data.id
            return redirect('/gemini-interview/')
    else:
        form = ProfileForm()

    return render(request, 'upload.html', {'form': form,'pending_credits': pending_credits})

def gemini_interview(request):
    questions = request.session.get('questions', [])
    return render(request, 'gemini-questions.html', {
        'questions_json': json.dumps(questions)
    })

@csrf_exempt
def save_interview_answer(request):
    if request.method == "POST":
        user = User.objects.get(id=request.session.get("id"))
        resume = Profile.objects.get(id=request.session.get("current_profile_id"))
        question = request.POST.get('question')
        answer = request.POST.get('answer')
        Interview.objects.create(user=user, resume=resume, question=question, answer=answer)
        print(f"Answer received:\nQ: {question}\nA: {answer}")
        return JsonResponse({'status': 'saved'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def gemini_audio_question(request):
    from gtts import gTTS
    from io import BytesIO
    q = request.GET.get("q", "")
    tts = gTTS(q)
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)
    return HttpResponse(audio_file.read(), content_type="audio/mpeg")

    
def feedback(request):
    user_id = request.session.get('id')
    if not user_id:
        return redirect('/login/') 

    if request.method == 'POST':

        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user_id = user_id  
            feedback.save()
            return redirect('/index/') 
    else:
        form = FeedbackForm()

    return render(request, 'feedback.html', {'form': form})


def result(request):
    user = User.objects.get(id=request.session.get("id"))
    resume = Profile.objects.get(id=request.session.get("current_profile_id"))
    questions = Interview.objects.filter(user=user, resume=resume)
    
    question_answer_list = []
    for qa in questions:
        question_answer_list.append(f"Question : {qa.question} \nUser Answer : {qa.answer}\n")

    question_answer = "\n".join(question_answer_list)

    full_user_prompt = f"""
    User Resume
    {resume.resume_text}
    
    \n\n

    Question & Answer
    {question_answer}
    """
    gemini_response = evaluate_response(full_user_prompt)

    total_questions = gemini_response.get("total_questions")
    answered = gemini_response.get("answered")
    confidence = gemini_response.get("confidence")
    performance = gemini_response.get("performance")


    start_time = request.session.get("start_time")
    end_time = time.time()
    time_taken = round(end_time - start_time) if start_time else 0

    
    minutes = time_taken // 60
    seconds = time_taken % 60
    formatted_time = f"{minutes} min {seconds} sec"

    InterviewResult.objects.create(
        user=user,
        resume=resume,
        total_questions=total_questions,
        confidence_level=confidence,
        time_taken=time_taken,
        overall_rating=performance,
    )
    subscription = Subscription.objects.filter(user=user, status='ACTIVE').first()
    if subscription and subscription.pending_credits > 0:
        subscription.pending_credits -= 1
        subscription.save()
    assign_free_plan_if_expired(user)

    return render(request, 'result.html', {
        'total_questions': total_questions,
        'answered': answered,
        'confidence': confidence,
        'performance': performance,
        'time_taken': formatted_time
    })


def check(request):
    uid = request.session["id"]
    s = Subscription.objects.get(user=uid)
    print("----------subscription--------", s)
    end = s.end_date_time.date()
    print("date----", end, date.today())

    if date.today() >= end:
        request.session.flush()
        # TODO :  Subscription expired
        print("Expired------------")
        return HttpResponse("Your subscription has expired. Please renew to continue.")

    return HttpResponse("")


def download(request):
    user_id = request.session.get("id")
    if not user_id:
        return redirect("/login/")

    user = User.objects.get(id=user_id)
    resume_id = request.session.get("current_profile_id")

    if not resume_id:
        return HttpResponse("❌ No recent interview found to generate report.")

    try:
        resume = Profile.objects.get(id=resume_id)
    except Profile.DoesNotExist:
        return HttpResponse("❌ Resume not found.")

    questions = Interview.objects.filter(user=user, resume=resume)

    total = questions.count()
    answered = sum(1 for q in questions if q.answer.strip())

    
    result = InterviewResult.objects.filter(user=user, resume=resume).first()
    confidence = result.confidence_level if result else 0
    performance = result.overall_rating if result else 0

    
    time_taken_seconds = int(request.session.get('interview_time', 0))
    minutes, seconds = divmod(time_taken_seconds, 60)
    formatted_time = f"{minutes} minutes {seconds} seconds" if minutes else f"{seconds} seconds"

    context = {
        'user': user,
        'resume': resume,
        'questions': questions,
        'total': total,
        'answered': answered,
        'confidence': confidence,
        'performance': performance,
        'time_taken': formatted_time,
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Interview_Report.pdf"'

    template = get_template('download.html')
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('❌ PDF generation failed.')
    return response