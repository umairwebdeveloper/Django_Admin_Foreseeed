from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_forget_password_mail(email, token, request):
    subject = 'Reset Your Password'

    # Render the HTML template for the email
    html_message = render_to_string('auth/reset-password-email.html', {'token': token, 'request':request})

    # Extract the text content from HTML for the plain text version of the email
    text_content = strip_tags(html_message)

    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]

    # Create an EmailMultiAlternatives object to include both HTML and plain text versions of the email
    msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
    msg.attach_alternative(html_message, "text/html")

    # Send the email
    msg.send()
    return True

# def send_mail_test(email, token='abc'):
#     subject = 'Your forget password link'
#     message = f'Hi , click on the link to reset your password http://127.0.0.1:8000/change-password/{token}/'
#     email_from = settings.EMAIL_HOST_USER
#     recipient_list = [email]
#     print(444,email_from,email,token)
#     send_mail(subject, message, email_from, recipient_list)
#     return True