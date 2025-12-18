from django.db import models
from django.contrib.auth.models import User
class Car(models.Model):
    dealer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cars',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    price = models.IntegerField()
    year = models.IntegerField()
    fuel_type = models.CharField(max_length=20)
    engine_capacity = models.CharField(
        max_length=50,
        help_text="Eg: 2.0L Turbo, 3.2 V8, Electric",
        blank=True
    )
    # ✅ Transmission
    TRANSMISSION_CHOICES = (
        ('Manual', 'Manual'),
        ('Automatic', 'Automatic'),
    )
    transmission = models.CharField(
        max_length=20,
        choices=TRANSMISSION_CHOICES,
        blank=True
    )

    # ✅ Mileage / Range
    mileage = models.CharField(
        max_length=50,
        blank=True,
        help_text="Eg: 18 km/l or 450 km"
    )

    # ✅ Features
    features = models.TextField(
        blank=True,
        help_text="Comma separated: ABS, Airbags, Sunroof"
    )
    description = models.TextField()

    main_image = models.ImageField(
        upload_to='cars/main/',
        null=True,
        blank=True
        )  # ✅ MAIN IMAGE

    status = models.CharField(
        max_length=20,
        choices=[
            ('Available', 'Available'),
            ('Sold', 'Sold'),
            ('Reserved', 'Reserved'),
        ],
        default='Available'
    )

    def __str__(self):
        return self.title


class CarImage(models.Model):
    car = models.ForeignKey(
        Car,
        related_name='images',
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='cars/gallery/')
class Enquiry(models.Model):
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    STATUS_CHOICES = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('closed', 'Closed'),
    )

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='enquiries')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.car.title} - {self.name} ({self.status})"

class Profile(models.Model):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('dealer', 'Dealer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'car')
from django.db import models
from django.contrib.auth.models import User

class ContactMessage(models.Model):
    CONTACT_TYPE_CHOICES = (
        ('sales', 'Sales'),
        ('support', 'Support'),
        ('general', 'General'),
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()

    # ✅ THIS IS THE FIX
    type = models.CharField(
        max_length=20,
        choices=CONTACT_TYPE_CHOICES,
        default='general'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.type}"

class EnquiryReply(models.Model):
    enquiry = models.ForeignKey(
        Enquiry, related_name='replies', on_delete=models.CASCADE
    )
    dealer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
class DealerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dealer_profile')

    company_name = models.CharField(max_length=150)
    about = models.TextField(blank=True)

    # 🔐 Verification
    is_verified = models.BooleanField(default=False)
    admin_message = models.TextField(
        blank=True,
        help_text="Message shown to dealer regarding verification"
    )
    # 📄 Documents
    gst_number = models.CharField(max_length=20, blank=True,null=True)
    gst_document = models.FileField(upload_to='dealer_docs/gst/', blank=True, null=True)
    id_document = models.FileField(upload_to='dealer_docs/id/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def is_profile_complete(self):
        return bool(self.gst_number and self.gst_document and self.id_document)
    def __str__(self):
        return self.company_name

class DealerReview(models.Model):
    dealer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dealer_reviews'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='given_reviews'
    )

    rating = models.PositiveIntegerField(choices=[
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ])

    comment = models.TextField(blank=True)
    dealer_reply = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('dealer', 'user')

    def __str__(self):
        return f"{self.dealer.username} - {self.rating}★"
# cars/models.py
from django.db import models
from django.contrib.auth.models import User

