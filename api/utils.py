import uuid
import json
import string

from datetime import timedelta

from timeloop import Timeloop
timeloop = Timeloop()

from django.utils.crypto import get_random_string

from .models import Error, User, ForgotPasswordToken, StripeCustomer

import stripe

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from decouple import config


stripe.api_key = config('STRIPE_TEST_KEY')
sendgrid_api_key = config('SENDGRID_KEY')

def create_stripe_payment(amount):    
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency='usd',
        metadata={'integration_check': 'accept_a_payment'},
    )
    return intent


def create_error(user, details):
    obj = Error.objects.create(
        user = user,
        details = details
    )
    return obj

def send_forgot_password_email(email_address):
    sg = SendGridAPIClient(sendgrid_api_key)

    no_account_template_id = "d-5be42725530348c4a9b58b7d524347ef"

    account_found_template_id = "d-5f07fd7b5b644daaad40484acebf7055"


    data = {
        "personalizations" : [
            {
                "to" : [
                    { 
                    "email" : email_address
                    }
                ]
            },
        ],
        "from" : {
            "email" : 'LebaronGaleanaOfficial@gmail.com'
        }
    }

def send_message(email_address, username, message):
    
    sg = SendGridAPIClient(sendgrid_api_key)

    account_found_template_id = "d-5f07fd7b5b644daaad40484acebf7055"

    data = {
        "personalizations" : [
            {
                "to" : [
                    { 
                    "email" : 'LebaronGaleanaOfficial@gmail.com'
                    }
                ]
            },
        ],
        "from" : {
            "email" : email_address
        }
    }


    # find user 
    try:
        user = User.objects.get( email=email_address )

        name = user.get_full_name()

        token = generate_forgot_password_token(user)

        template_id = account_found_template_id

        data["personalizations"][0]["dynamic_template_data"] = {
            "name" : name,
            "link" : "http://localhost:3000/app/forgot-password/{}".format(token)
        }

    except User.DoesNotExist:
        template_id = no_account_template_id

        data["personalizations"][0]["dynamic_template_data"] = {
            "email" : email_address
        }

    data["template_id"] = template_id

    # send email
    try:
        response = sg.client.mail.send.post(request_body=data)
    except Exception as e:
        return

def generate_forgot_password_token(user):
    
    token = ForgotPasswordToken(user=user, token=get_random_string(42, allowed_chars=string.ascii_lowercase + string.digits))

    token.save()
    
    return token.get_token()

def reset_password(token, password):
    try:
        token = ForgotPasswordToken.objects.get(token=token)
        if token.is_expired():
            token.delete()
            return 'token not found'
        
        user = token.get_user()
        token.delete()
        user.set_password(password)
        user.save()
        return 'success'
    except ForgotPasswordToken.DoesNotExist:
        return 'token not found'

@timeloop.job(interval=timedelta(minutes=60))
def check_for_expired_tokens():
    queryset = ForgotPasswordToken.objects.all()
    for item in queryset:
        if item.is_expired():
            item.delete()





# not really sure where to put this, but this is necessary to start the timeloop
timeloop.start()
# There was some other boiler plate code for killing the process,
# but it kept causing problems.
# This by itself works. 


def get_subscription(user):
    if user.profile.subscriptionActive == True:
        try:
            stripe_customer = StripeCustomer.objects.get(user=user)
            subscription = stripe.Subscription.retrieve(stripe_customer.stripeSubscriptionId)
            if subscription.status == "active":
                return {'active': True, 'type': 'paid', 'plan': subscription.plan, 'end': subscription.current_period_end}
            elif subscription.status == "trialing":
                return {'active': True, 'type': 'trial', 'plan': subscription.plan, 'end': subscription.current_period_end}
            else:
                return {'active': False}
        except:
            return {'active': False}
    else:
        if user.profile.role == 3:
            return {'active': True, 'type': 'admin'}
        elif user.profile.freeAccount == True:
            return {'active': True, 'type': 'free'}
        else:
            return {'active': False}
