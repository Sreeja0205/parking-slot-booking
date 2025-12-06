# booking/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ParkingSlot, Booking
from datetime import datetime,date
from django.utils import timezone

# ================= HOME PAGE =================
def home(request):
    """Display available parking slots based on selected date and hour"""
    
    if request.method == "POST":
        date = request.POST.get('date')
        hour = request.POST.get('hour')
        
        try:
            hour = int(hour)
            
            # Find all bookings for that date and hour
            booked_slots = Booking.objects.filter(
                booking_date=date,
                start_hour__lte=hour,
                end_hour__gt=hour
            )
            
            # Get booked slot IDs
            booked_ids = booked_slots.values_list('slot_id', flat=True)
            
            # Get available slots (not booked + active)
            slots = ParkingSlot.objects.filter(is_active=True).exclude(id__in=booked_ids)
            
            return render(request, 'booking/home.html', {
                'slots': slots,
                'date': date,
                'hour': hour,
            })
        except (ValueError, TypeError):
            messages.error(request, "Invalid date or hour format!")
            return render(request, 'booking/home.html')
    else:
        # GET request - show all active slots
        slots = ParkingSlot.objects.filter(is_active=True)
        return render(request, 'booking/home.html', {'slots': slots})


# ================= AUTHENTICATION =================
def register(request):
    """User registration page"""
    
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "✅ Account created successfully! Please login.")
            return redirect('login')
        else:
            # Form errors will be displayed in template
            return render(request, 'booking/register.html', {'form': form})
    else:
        form = UserCreationForm()
        return render(request, 'booking/register.html', {'form': form})


def login_view(request):
    """User login page"""
    
    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"✅ Welcome {username}! You are logged in.")
            return redirect('home')
        else:
            messages.error(request, "❌ Invalid username or password. Please try again.")
            return render(request, 'booking/login.html')
    else:
        return render(request, 'booking/login.html')


def logout_view(request):
    """User logout"""
    
    logout(request)
    messages.success(request, "✅ You have been logged out successfully!")
    return redirect('home')


# ================= BOOKING =================
@login_required(login_url='login')
def book_slot(request, slot_id):
    """Book a parking slot"""
    
    slot = get_object_or_404(ParkingSlot, id=slot_id)
    
    if request.method == "POST":
        date_str = request.POST.get('date')
        start_hour = request.POST.get('start_hour')
        end_hour = request.POST.get('end_hour')
        
        try:
            start_hour = int(start_hour)
            end_hour = int(end_hour)
            booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Get current date and time
            today = date.today()
            current_hour = datetime.now().hour
            
            # ===== VALIDATION: Check if date is in past =====
            if booking_date < today:
                messages.error(request, "❌ Cannot book slots for past dates!")
                return redirect('home')
            
            # ===== VALIDATION: Check if hour is in past (for today) =====
            if booking_date == today and start_hour <= current_hour:
                messages.error(request, "❌ Cannot book past hours! Please select a future time.")
                return redirect('book_slot', slot_id=slot_id)
            
            # ===== VALIDATION: end_hour must be greater than start_hour =====
            if end_hour <= start_hour:
                messages.error(request, "❌ End hour must be later than start hour!")
                return redirect('book_slot', slot_id=slot_id)
            
            # ===== VALIDATION: hours must be between 0 and 23 =====
            if not (0 <= start_hour < 24 and 0 < end_hour <= 24):
                messages.error(request, "❌ Hours must be between 0 and 23!")
                return redirect('book_slot', slot_id=slot_id)
            
            # ===== CHECK FOR CONFLICTS (overlapping bookings) =====
            conflicts = Booking.objects.filter(
                slot=slot,
                booking_date=booking_date,
                start_hour__lt=end_hour,
                end_hour__gt=start_hour
            )
            
            if conflicts.exists():
                messages.error(request, "❌ This slot is already booked for this time period!")
                return redirect('home')
            
            # ===== CREATE THE BOOKING =====
            booking = Booking.objects.create(
                slot=slot,
                user=request.user,
                booking_date=booking_date,
                start_hour=start_hour,
                end_hour=end_hour
            )
            
            messages.success(
                request,
                f"✅ Slot {slot.slot_number} booked successfully for {booking_date} ({start_hour:02d}:00 - {end_hour:02d}:00)!"
            )
            return redirect('my_bookings')
            
        except ValueError as e:
            messages.error(request, "❌ Invalid input data! Please try again.")
            return redirect('book_slot', slot_id=slot_id)
        except Exception as e:
            messages.error(request, f"❌ An error occurred: {str(e)}")
            return redirect('book_slot', slot_id=slot_id)
    
    else:
        # GET request - show booking form
        date_param = request.GET.get('date', '')
        start_hour = request.GET.get('start_hour', '')
        
        return render(request, 'booking/book_slot.html', {
            'slot': slot,
            'date': date_param,
            'start_hour': start_hour,
        })

# ================= USER BOOKINGS =================
@login_required(login_url='login')
def my_bookings(request):
    """Display all bookings made by the current user"""
    
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date', '-start_hour')
    
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})
