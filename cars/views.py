import profile
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.views import LoginView
from .models import Car, Enquiry, EnquiryReply, Wishlist, ContactMessage
from .models import DealerProfile
from django.contrib.auth.models import User
from threading import Thread
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile

from .models import (
    Car, CarImage, Enquiry, EnquiryReply,
    Wishlist
)
from .forms import (
    CarForm, EnquiryForm,
    RegisterForm, ContactForm
)

# ---------------- HOME ----------------

def home(request):
    featured_cars = Car.objects.filter(status='Available')[:3]
    return render(request, 'home.html', {'featured_cars': featured_cars})


# ---------------- CAR LIST ----------------

def car_list(request):
    cars = Car.objects.filter(status='Available')

    if request.GET.get('brand'):
        cars = cars.filter(brand__icontains=request.GET['brand'])

    if request.GET.get('fuel'):
        cars = cars.filter(fuel_type=request.GET['fuel'])

    if request.GET.get('transmission'):
        cars = cars.filter(transmission=request.GET['transmission'])

    paginator = Paginator(cars, 6)
    page = request.GET.get('page')
    cars = paginator.get_page(page)

    return render(request, 'car_list.html', {'cars': cars})


# ---------------- CAR DETAIL ----------------

def car_detail(request, id):
    car = get_object_or_404(Car, id=id)
    features = [f.strip() for f in car.features.split(',')] if car.features else []
    return render(request, 'car_detail.html', {'car': car, 'features': features})


# ---------------- ENQUIRIES ----------------

def send_enquiry(request, id):
    car = get_object_or_404(Car, id=id)

    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save(commit=False)
            enquiry.car = car
            if request.user.is_authenticated:
                enquiry.user = request.user
            enquiry.save()

            if car.dealer and car.dealer.email:
                send_mail(
                    'New Enquiry 🚗',
                    enquiry.message,
                    settings.DEFAULT_FROM_EMAIL,
                    [car.dealer.email],
                    fail_silently=True
                )
            if request.user.is_authenticated:
                return redirect('my_enquiries')
            else:
                return redirect('car_detail', id=car.id)


    return render(request, 'send_enquiry.html', {
        'car': car,
        'form': EnquiryForm()
    })


@login_required
def my_enquiries(request):
    enquiries = Enquiry.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_enquiries.html', {'enquiries': enquiries})


# ---------------- DEALER ----------------

@login_required
def dealer_dashboard(request):
    if request.user.profile.role != 'dealer':
        return redirect('home')
    if not request.user.dealer_profile.is_verified:
        messages.info(
            request,
            "Complete your dealer profile and wait for verification."
        )
    cars = Car.objects.filter(dealer=request.user)
    return render(request, 'dealer_dashboard.html', {
        'cars': cars,
        'total': cars.count(),
        'available': cars.filter(status='Available').count(),
        'sold': cars.filter(status='Sold').count(),
    })


@login_required
def dealer_enquiries(request):
    enquiries = Enquiry.objects.filter(car__dealer=request.user).order_by('-created_at')
    return render(request, 'dealer_enquiries.html', {'enquiries': enquiries})


@login_required
def reply_enquiry(request, id):
    enquiry = get_object_or_404(Enquiry, id=id, car__dealer=request.user)
    if request.method == 'POST':
        EnquiryReply.objects.create(
            enquiry=enquiry,
            dealer=request.user,
            message=request.POST.get('message')
        )
        enquiry.status = 'contacted'
        enquiry.save()
    return redirect('dealer_enquiries')


# ---------------- CARS CRUD ----------------

@login_required
def add_car(request):
    # 🔒 Dealer-only access
    if request.user.profile.role != 'dealer':
        return redirect('home')

    dealer_profile = getattr(request.user, 'dealer_profile', None)

    # 🔒 Dealer must exist & be verified
    if not dealer_profile.is_profile_complete:
        messages.info(
            request,
            "Please complete your dealer profile before adding cars."
        )
        return redirect('edit_dealer_profile')

    if not dealer_profile.is_verified:
        messages.warning(
        request,
        "Your account is under review. You’ll be able to add cars once verified."
        )
        return redirect('dealer_dashboard')

    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.dealer = request.user
            car.save()

            images = request.FILES.getlist('gallery_images')
            for img in images:
                CarImage.objects.create(car=car, image=img)

            return redirect('dealer_dashboard')
    else:
        form = CarForm()

    return render(request, 'add_car.html', {'form': form})


@login_required
def edit_car(request, id):
    car = get_object_or_404(Car, id=id, dealer=request.user)
    form = CarForm(request.POST or None, request.FILES or None, instance=car)
    if form.is_valid():
        form.save()
        return redirect('dealer_dashboard')
    return render(request, 'edit_car.html', {'form': form})


@login_required
def delete_car(request, id):
    car = get_object_or_404(Car, id=id, dealer=request.user)
    if request.method == 'POST':
        car.delete()
        return redirect('dealer_dashboard')
    return render(request, 'delete_car.html', {'car': car})


# ---------------- AUTH ----------------
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.email:
                Thread(
                target=send_welcome_email,
                args=(user.email, user.username)
                ).start()
            role = form.cleaned_data['role']

            # ✅ PROFILE (SAFE)
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={'role': role}
            )
            if not created and profile.role != role:
                profile.role = role
                profile.save()

            # ✅ DEALER PROFILE (SAFE)
            if role == 'dealer':
                DealerProfile.objects.get_or_create(
                    user=user,
                    defaults={'company_name': user.username}
                )

            # ✅ EMAIL
            # ✅ EMAIL (NON-BLOCKING)
            if user.email:
                Thread(
                    target=send_welcome_email,
                    args=(user.email, user.username)
                ).start()


            login(request, user)

            # ✅ CORRECT REDIRECT
            if role == 'dealer':
                messages.info(
                    request,
                    "Please complete your dealer profile and upload documents for verification."
                )
                return redirect('edit_dealer_profile')

            return redirect('home')

    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.role == 'dealer':
            return reverse_lazy('dealer_dashboard')
        return reverse_lazy('home')


# ---------------- WISHLIST ----------------

@login_required
def add_to_wishlist(request, id):
    Wishlist.objects.get_or_create(user=request.user, car_id=id)
    return redirect(request.META.get('HTTP_REFERER', 'car_list'))


@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user).select_related('car')
    return render(request, 'wishlist.html', {'items': items})


@login_required
def remove_from_wishlist(request, id):
    Wishlist.objects.filter(user=request.user, car_id=id).delete()
    return redirect('wishlist')


# ---------------- COMPARE ----------------

def add_to_compare(request, id):
    compare = request.session.get('compare', [])
    if id not in compare and len(compare) < 2:
        compare.append(id)
    request.session['compare'] = compare
    return redirect(request.META.get('HTTP_REFERER', 'car_list'))


def compare_cars(request):
    ids = request.session.get('compare', [])
    if len(ids) < 2:
        return redirect('car_list')
    cars = Car.objects.filter(id__in=ids)
    return render(request, 'compare.html', {'cars': cars})


def clear_compare(request):
    request.session['compare'] = []
    return redirect('car_list')


# ---------------- CONTACT ----------------

def contact(request):
    if request.method == 'POST':
        contact = ContactMessage.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            subject=request.POST['subject'],
            message=request.POST['message'],
            type=request.POST['type'],
            user=request.user if request.user.is_authenticated else None
        )



        messages.success(request, "Thanks! Our team will contact you shortly.")
        return redirect('contact')

    return render(request, 'contact.html')
from threading import Thread
from django.core.mail import send_mail
from django.conf import settings

def send_welcome_email(email, username):
    try:
        send_mail(
            subject="Welcome to DriveSurely 🚗",
            message=(
                f"Hi {username},\n\n"
                "Welcome to DriveSurely!\n\n"
                "Please complete your profile.\n\n"
                "— DriveSurely Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as e:
        print("Email error:", e)

@login_required
@require_POST
def update_enquiry_status(request, id):
    enquiry = get_object_or_404(
        Enquiry,
        id=id,
        car__dealer=request.user
    )

    status = request.POST.get('status')
    if status in ['new', 'contacted', 'closed']:
        enquiry.status = status
        enquiry.save()

    return redirect('dealer_enquiries')
from django.db.models import Avg
from django.contrib.auth.models import User
from django.db.models import Avg
from .models import Car, DealerProfile, DealerReview

from django.contrib.auth.models import User
from django.db.models import Avg
from .models import Car, DealerProfile, DealerReview
from django.db.models import Avg
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .models import Car, Enquiry, DealerProfile, DealerReview

def dealer_public_profile(request, username):
    dealer = get_object_or_404(User, username=username)

    if not hasattr(dealer, 'profile') or dealer.profile.role != 'dealer':
        return redirect('home')

    # 🔒 Block unverified dealers
    if not dealer.dealer_profile.is_verified:
        return redirect('home')

    dealer_profile, _ = DealerProfile.objects.get_or_create(
        user=dealer,
        defaults={
            'company_name': dealer.get_full_name() or dealer.username,
            'about': 'This dealer has not added a description yet.'
        }
    )

    cars = Car.objects.filter(dealer=dealer, status='Available')
    reviews = DealerReview.objects.filter(dealer=dealer)
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']

    total_cars = Car.objects.filter(dealer=dealer).count()
    available_cars = cars.count()
    total_enquiries = Enquiry.objects.filter(car__dealer=dealer).count()

    # ✅ SAFE DEFAULTS
    can_review = False
    review_form = None

    # ✅ REVIEW ELIGIBILITY CHECK
    if (
        request.user.is_authenticated
        and hasattr(request.user, 'profile')
        and request.user.profile.role == 'customer'
        and request.user != dealer
    ):
        has_enquired = Enquiry.objects.filter(
            user=request.user,
            car__dealer=dealer
        ).exists()

        already_reviewed = DealerReview.objects.filter(
            dealer=dealer,
            user=request.user
        ).exists()

        if has_enquired and not already_reviewed:
            can_review = True
            review_form = DealerReviewForm()

    context = {
        'dealer': dealer,
        'profile': dealer_profile,
        'cars': cars,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'can_review': can_review,
        'review_form': review_form,
        'stats': {
            'total_cars': total_cars,
            'available': available_cars,
            'enquiries': total_enquiries,
        },
    }

    return render(request, 'dealer_public_profile.html', context)

@login_required
def add_dealer_review(request, username):
    dealer = get_object_or_404(User, username=username)

    if request.user.profile.role != 'customer':
        return redirect('home')

    # Must have enquired
    has_enquired = Enquiry.objects.filter(
        user=request.user,
        car__dealer=dealer
    ).exists()

    if not has_enquired:
        messages.error(request, "You can only review dealers you contacted.")
        return redirect('dealer_public_profile', username=username)

    form = DealerReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.dealer = dealer
        review.user = request.user
        review.save()

        messages.success(request, "Thanks for your review!")
    
    return redirect('dealer_public_profile', username=username)

from .forms import DealerReviewForm
from django.contrib.auth.decorators import login_required

@login_required
def add_dealer_review(request, username):
    dealer = get_object_or_404(User, username=username)

    if dealer.profile.role != 'dealer':
        return redirect('home')

    form = DealerReviewForm(request.POST or None)

    if form.is_valid():
        review = form.save(commit=False)
        review.dealer = dealer
        review.user = request.user
        review.save()

    return redirect('dealer_public_profile', username=username)
# forms.py
from django import forms
from .models import DealerProfile

class DealerProfileForm(forms.ModelForm):
    class Meta:
        model = DealerProfile
        exclude = ('user', 'verification_status', 'created_at')
# views.py
from django.contrib.auth.decorators import login_required
from .models import DealerProfile
from .forms import DealerProfileForm

@login_required
def edit_dealer_profile(request):
    if request.user.profile.role != 'dealer':
        return redirect('home')

    profile, _ = DealerProfile.objects.get_or_create(
        user=request.user,
        defaults={'company_name': request.user.username}
    )

    if request.method == 'POST':
        form = DealerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Profile submitted successfully. Awaiting admin verification."
            )
            return redirect('dealer_dashboard')
    else:
        form = DealerProfileForm(instance=profile)

    return render(request, 'edit_dealer_profile.html', {'form': form})
@login_required
@require_POST
def reply_to_review(request, review_id):
    review = get_object_or_404(DealerReview, id=review_id)

    # 🔒 Only dealer who owns this profile can reply
    if request.user != review.dealer:
        return redirect('home')

    reply = request.POST.get('reply')
    if reply:
        review.dealer_reply = reply
        review.save()

    return redirect('dealer_public_profile', username=review.dealer.username)

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(DealerReview, id=review_id, user=request.user)

    if request.method == 'POST':
        review.rating = request.POST.get('rating')
        review.comment = request.POST.get('comment')
        review.save()
        return redirect('dealer_public_profile', username=review.dealer.username)

    return render(request, 'edit_review.html', {'review': review})


@login_required
@require_POST
def delete_review(request, review_id):
    review = get_object_or_404(DealerReview, id=review_id, user=request.user)
    dealer_username = review.dealer.username
    review.delete()
    return redirect('dealer_public_profile', username=dealer_username)
@login_required
def dealer_status(request):
    if request.user.profile.role != 'dealer':
        return redirect('home')

    profile = get_object_or_404(DealerProfile, user=request.user)

    return render(request, 'dealer_status.html', {
        'profile': profile
    })
