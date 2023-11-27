import os
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import shutil
import pandas as pd
from prophet import Prophet
import tempfile
from django.core.mail import send_mail
from django.urls import reverse
from accounts.models import Profile


import numpy as np
import pandas as pd
import pulp as p


def index(request):
    return render(request, 'landing_page.html')


#Old code for page submission needs rewrite
def demo(request):
    if request.method == 'POST':
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        phone = request.POST["phone"]
        email = request.POST["email"]
        company_name = request.POST["company_name"]
        company_size = request.POST["company_size"]

        
        message_txt = f"First name: {first_name} \nLast Name: {last_name}\nPhone: {phone} \nCompany Email: {email} \nCompany Name: {company_name} \nCompany size: {company_size}"
        
        print(message_txt)
        send_mail(
            'Request a demo',
            message_txt,
            'info@foreseeed.app',
            ['info@foreseeed.app'],
            fail_silently=False,
        )
        return HttpResponseRedirect(reverse('demo'))

    return render(request, 'demo.html')


def features(request):
    return render(request, 'features.html')


def pricing(request):
    return render(request, 'pricing.html')


def about_us(request):
    return render(request, 'about_us.html')

def faqs(request):
    return render(request, 'faq.html')


def login_fn(request):
    if request.user.is_authenticated:
        # If the user is already authenticated, redirect to the dashboard
        return redirect('/dashboard')

    if request.method == 'GET':
        # Render the login form for GET requests
        return render(request, 'auth/new_login.html')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if a user with the given email exists
        user = User.objects.filter(email=email).first()

        if user is not None:
            # If the user exists, attempt to authenticate
            authenticated_user = authenticate(username=user.username, password=password)

            if authenticated_user is not None:
                # If authentication is successful, log in the user and redirect to dashboard
                login(request, authenticated_user)
                return redirect('/dashboard')
            else:
                # If authentication fails, display an error message
                return render(request, 'auth/new_login.html', {'msg': "Incorrect password. Please try again.", 's': "error", "d": "danger"})
        else:
            # If the user does not exist, display an error message
            return render(request, 'auth/new_login.html', {'msg': "User does not exist. Please sign up.", 's': "error", "d": "danger"})

    # Redirect to logout if the request doesn't fall into any of the above cases
    return redirect('logout')


def register(request):
    if request.user.is_authenticated and request.method == 'GET':
        return redirect('dashboard')
    elif request.method == 'GET':
        return render(request, 'auth/new_register.html')
    if request.method == "POST":
        data = request.POST
        email = data.get("email")
        first_name = data.get("full_name")
        password = data.get("password")
        if not User.objects.filter(username=email):
            user = User.objects.create_user(first_name=first_name,
                                            username=email,
                                            email=email,
                                            password=password)
            profile_obj = Profile.objects.create(user = user )
            profile_obj.save()
            return render(request, "auth/new_login.html", context={"msg": "Registered Successfully! ", "s": "success", "d": "success"})
        else:
            return render(request, "auth/new_register.html", context={"msg": "Email Already Exists!", "s": "error", "d": "danger"})
    return redirect('logout')


@login_required(login_url='/login')
def dashboard(request):
    if request.method == 'GET':
        if request.session.get('data_file_temp_path', False):
            data_file_path = request.session["data_file_temp_path"]
            print("File: ", data_file_path)
        else:
            print("No File Uploaded!")
        return render(request, 'dashboard/dashboard.html')
    if request.method == "POST":
        excel_file = request.FILES.get("excel_file")
        if excel_file:
            if excel_file.content_type == "text/csv":
                mb_size = excel_file.size / (1024 * 1024)
                if mb_size < 200:

                    temp_file = tempfile.NamedTemporaryFile(
                        suffix=".csv", delete=False)

                    temp_path = temp_file.name

                    with open(temp_path, 'wb+') as destination:
                        for chunk in excel_file.chunks():
                            destination.write(chunk)

                    # print(temp_path)
                    request.session['data_file_temp_path'] = temp_path
                    return render(request, 'dashboard/dashboard.html', context={"msg": "Saved Successfully"})
                else:
                    return render(request, 'dashboard/dashboard.html',
                                  context={"error": "File size should be less then 200MB."})
            else:
                return render(request, 'dashboard/dashboard.html',
                              context={"error": "Only text/csv file supported. Please Select text/CSV File"})
        else:
            return render(request, 'dashboard/dashboard.html',
                          context={"error": "No File Selected. Please Select Text/CSV File"})


@login_required(login_url='login')
def dashboards(request):
    if request.method == "GET":
        if request.session.get('data_file_temp_path', False):
            data_file_path = request.session["data_file_temp_path"]
            try:
                df = pd.read_csv(open(data_file_path)).dropna()
                context_df = pd.read_csv(open(data_file_path)).dropna()
                data = request.GET
                if data:
                    df = apply_filters(df=df, data=data)

                context = get_context_dic(df, context_df)
                context.update({"query_params": data})
                
                return render(request, 'dashboard/upload_file.html', context=context)
            except Exception as e:
                print(e)
                try:
                    del request.session['data_file_temp_path']
                except KeyError:
                    pass

        print("No File Uploaded!")
        return render(request, 'dashboard/upload_file.html', context={"msg": "No Cvs Uploaded Yet!",
                                                                     "csv": False})


@login_required(login_url='login')
def forecastings(request):
    if request.method == "GET":
        if request.session.get('data_file_temp_path', False):
            data_file_path = request.session["data_file_temp_path"]
            try:
                df = pd.read_csv(open(data_file_path)).dropna()
                context_df = pd.read_csv(open(data_file_path)).dropna()
                data = request.GET
                if data:
                    try:
                        df = apply_filters_forecasting(df=df, data=data)
                        context = get_context_dic_forecast(df, context_df)
                        if data.get("download"):
                            response = HttpResponse(content_type='text/csv')
                            response['Content-Disposition'] = 'attachment; filename=forecastings.csv'
                            df.to_csv(path_or_buf=response,
                                      index=False, decimal=".")
                            return response
                    except Exception as e:
                        context = get_context_dic_forecast(
                            df, context_df, True)
                        context.update(
                            {"msg": str(e) + " OR Make sure you have upload the accurate data format"})
                        return render(request, 'dashboard/forecastings.html', context=context)

                else:
                    context = get_context_dic_forecast(df, context_df, True)

                context.update({"query_params": data})
                return render(request, 'dashboard/forecastings.html', context=context)
            except Exception as e:
                e = str(e)
                exc = e + " OR make sure that data source is according to guidelines"
                # try:
                #     del request.session['data_file_temp_path']
                # except KeyError:
                #     pass
                return render(request, 'dashboard/forecastings.html', context={"msg": exc,
                                                                               "csv": False})
        else:
            print("No File Uploaded!")
            return render(request, 'dashboard/forecastings.html', context={"msg": "No Cvs Uploaded Yet!",
                                                                           "csv": False})



@login_required(login_url='login')
def budgetallocator(request):

    if request.method == 'POST':
        budget_limit = request.POST["budget_limit"]
        print(request.POST)
        
        channels = []
        if "channels" in request.POST:
            channels = request.POST["channels"]
        


        min_budget_array = []
        monthly_conversions = []
        roi = []
        conversion_rates = []

        
        for i in range(1, 5):
            
            min_budget_array.append(convert_to_number(request.POST[f"min_budget_opt{i}"]))
            
            monthly_conversions.append(convert_to_number(request.POST[f"number_of_conversions_opt{i}"]))
            roi.append(convert_to_number(request.POST[f"roi_opt{i}"]))
            conversion_rates.append(convert_to_number(request.POST[f"conversion_rate_opt{i}"]))
            
        print(min_budget_array, monthly_conversions, roi, budget_limit, conversion_rates)
        results = budget_allocation(channels, monthly_conversions, conversion_rates, min_budget_array, int(budget_limit) )
        request.session["results"] = results
        return HttpResponseRedirect(reverse('budget_allocator_results'))
    return render(request, 'dashboard/budget_allocator.html')

@login_required
def budgetallocatorresults(request):

    results = request.session["results"]
    if 'results' in request.session:
        del request.session['results']
    return render(request, 'dashboard/budget_allocator_results.html', context={"results": results})



def convert_to_number(input):
    if input == '':
        return 0
    return int(input)

@ login_required(login_url='login')
def logout_user(request):
    username = request.user.username.split('@')[0]
    try:
        shutil.rmtree('media/' + username)
    except:
        pass
    logout(request)
    return redirect("index")


def apply_filters(df, data):
    #
    brand = data.get("brand")
    try:
        if brand != "All":
            df = df[df["brand_type"] == brand]
    except:
        pass
    #
    engine = data.get("engine")
    try:
        if engine != "All":
            df = df[df["engine"] == engine]
    except:
        pass
    #
    device = data.get("device")
    try:
        if device != "All":
            df = df[df["device_name"] == device]
    except:
        pass
    #
    campaign = data.get("campaign")
    try:
        if campaign != "All":
            df = df[df["campaign"] == campaign]
    except:
        pass
    #
    date_from = data.get("date_from")
    try:
        if date_from != "All":
            df = df[df["date"] >= date_from]
    except:
        pass
    #
    date_to = data.get("date_to")
    try:
        if date_to != "All":
            df = df[df["date"] <= date_to]
    except:
        pass

    return df


def get_context_dic(dataframe, context_df):
    brand_types = context_df.get("brand_type", [])
    engines = context_df.get("engine", [])
    device_names = context_df.get("device_name", [])
    campaigns = context_df.get("campaign", [])
    dates = context_df.get("date", [])

    try:
        dates = dates.unique()
    except:
        pass
    try:
        campaigns = campaigns.unique()
    except:
        pass
    # print(campaigns)
    try:
        device_names = device_names.unique()
    except:
        pass

    try:
        engines = engines.unique()
    except:
        pass

    try:
        brand_types = brand_types.unique()
    except:
        pass

    try:
        imps = dataframe.get("imps", []).values.tolist()
    except:
        imps = []
        pass

    try:
        clicks = dataframe["clicks"].values.tolist()
    except:
        clicks = []
        pass
    try:
        cpc = dataframe["cpc"].values.tolist()
        dataframe["cpc"] = dataframe["cpc"].str.replace(
            '$', '', regex=True)
        dataframe["cpc"] = dataframe["cpc"].astype(float)
        sum_cpc = dataframe["cpc"].values.tolist()
    except:
        cpc = []
        pass
    try:
        conversions = dataframe["conversions"].values.tolist()
    except:
        conversions = []
        pass
    try:
        ctr = dataframe["ctr"].values.tolist()
    except:
        ctr = []
        pass

    try:
        engine = dataframe["engine"].unique().tolist()
    except:
        engine = []
        pass

    try:
        dataframe["media_spend"] = dataframe["media_spend"].str.replace(
            ',', '', regex=True)
        dataframe["media_spend"] = dataframe["media_spend"].str.replace(
            '$', '', regex=True)
        media_spend = dataframe["media_spend"].values.tolist()
        dataframe["media_spend"] = dataframe["media_spend"].astype(float)
        total_cost =  dataframe["media_spend"].values.tolist()
    except:
        media_spend = []
        total_cost = 0
        pass
    try:
        date = dataframe["date"].values.tolist()
    except:
        date = []
        pass
    
    try:
        dataframe["cvr"] = dataframe["cvr"].str.replace('%', '', regex=True)
        dataframe["cvr"] = dataframe["cvr"].astype(float)
        cvr = dataframe["cvr"].values.tolist()
    except:
        cvr = []
        pass
    try:
        
        dataframe["cpo"] = dataframe["cpo"].str.replace('$', '', regex=True)
        dataframe["cpo"] = dataframe["cpo"].str.replace(',', '', regex=True)
        dataframe["cpo"] = dataframe["cpo"].astype(float)
        print(dataframe["cpo"])
        cpo = dataframe["cpo"].values.tolist()
        print(cpo)
    except Exception as e:
        print(str(e))
        cpo = []
        pass
    

    print(sum(sum_cpc))
    total_cpc = round(sum(sum_cpc))
    total_cvr = round(sum(cvr))
    total_cpo = round(sum(cpo))

    print(total_cpo)
    

    context = {
        "brand_types": brand_types,
        "engines": engines,
        "device_names": device_names,
        "campaigns": campaigns,
        "dates": dates,
        "imps": imps,
        "clicks": clicks,
        "cpc": cpc,
        "conversions": conversions,
        "ctr": ctr,
        "engine": engine,
        "media_spend": media_spend,
        "date": date,
        "total_cost": f"{round(sum(total_cost)):,}",
        "total_conversions": f"{sum(conversions):,}",
        "total_cvr": f"{total_cvr:,}",
        "total_cpc": f"{total_cpc:,}",
        "total_cpo": f"{total_cpo:,}"
    }
    return context


def apply_filters_forecasting(df, data):

    #
    brand = data.get("brand")
    try:
        if brand != "All":
            df = df[df["brand_type"] == brand]
    except:
        pass

    campaign = data.get("campaign")
    try:
        if campaign != "All":
            df = df[df["campaign"] == campaign]
    except:
        pass
    period = data.get("period")
    x_matric = "date"
    y_matric = data.get("y_matric")

    if y_matric == "media_spend":
        df["media_spend"] = df["media_spend"].str.replace(',', '', regex=True)
        df["media_spend"] = df["media_spend"].str.replace('$', '', regex=True)

    brand_data = df.rename(columns={x_matric: 'ds', y_matric: 'y'})

    model = Prophet()

    model.fit(brand_data)
    future_thirty = model.make_future_dataframe(periods=int(period), freq='D')
    forecast = model.predict(future_thirty)
    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(30)

    return forecast


def get_context_dic_forecast(df, context_df, data=False):
    brand_types = context_df.get("brand_type", [])
    campaigns = context_df.get("campaign", [])

    df_matrics = context_df.select_dtypes(include=['int', 'float'])
    matrics = df_matrics.columns.tolist()

    if 'media_spend' in context_df.columns:
        matrics.append("media_spend")

    try:
        brand_types = brand_types.unique()
    except:
        pass

    try:
        campaigns = campaigns.unique()
    except:
        pass

    if data:
        context = {
            "brand_types": brand_types,
            "campaigns": campaigns,
            "matrics": matrics
        }
    else:
        ds = df['ds'].astype(str).tolist()
        trend = df["trend"].values.tolist()
        yhat = df["yhat"].values.tolist()
        context = {
            "brand_types": brand_types,
            "campaigns": campaigns,
            "matrics": matrics,
            "yhat": yhat,
            "ds": ds,
            "trend": trend,
        }

    return context


def budget_allocation(channels,number_of_conversions, conversion_rates, min_budgets, budget):
    # directory_path = os.getcwd()
    # print(directory_path)
    # digi_data = pd.read_excel(os.path.join(directory_path, "budget_alloc_testdata.xlsx"), sheet_name='PT')
    # digi_data.head(20)    
    print(channels)
    print(number_of_conversions)
    print(min_budgets)
    print(budget)

    lp_model = p.LpProblem("Budget_Allocation", p.LpMaximize)

    paidsearch_x1 = p.LpVariable("PaidSearch", lowBound=0)
    paidsearchbrand_x2 = p.LpVariable("PaidSearchBrand", lowBound=0)
    paidsearchnondisplaybrand_x3 = p.LpVariable("PaidSearchOnDisplayBrand", lowBound=0)
    paidsocialorTV_x4 = p.LpVariable("PaidSocialOrTV", lowBound=0)


    

    
    lp_model += number_of_conversions[0] * paidsearch_x1 + number_of_conversions[1] * paidsearchbrand_x2 + number_of_conversions[2]* paidsearchnondisplaybrand_x3 + number_of_conversions[3] * paidsocialorTV_x4
    print(lp_model)
    lp_model += paidsearch_x1 + paidsearchbrand_x2 + paidsearchnondisplaybrand_x3 + paidsocialorTV_x4 <= budget
    lp_model += paidsearch_x1 >= min_budgets[0]
    lp_model += paidsearchbrand_x2 >= min_budgets[1]
    lp_model += paidsearchnondisplaybrand_x3 >= min_budgets[2]
    lp_model += paidsocialorTV_x4 >= min_budgets[3]

    print(lp_model)

    # ---------------------------------------

    #Solve the problem
    lp_Solution = lp_model.solve()
    print("Solution:", p.LpStatus[lp_Solution])

    
    print("Optimal budget allocation:")
    results = {}
    for v in lp_model.variables():
        print(v.name, "=", v.varValue)
        results[v.name] = v.varValue
    print("Optimal objective value: $", -p.value(lp_model.objective))
    results["optimal"] = -p.value(lp_model.objective)

    return results


# def new_login(request):
#     if request.method == 'POST':
#         # Retrieving username and password from POST request
#         email = request.POST.get('email')
#         password = request.POST.get('password')

#         # Authenticating user
#         user = authenticate(request, email=email, password=password)
        
#         # Checking if the user is authenticated
#         if user is not None:
#             login(request, user)
#             # Redirecting to the home page upon successful login
#             return redirect('home')
#         else:
#             # Rendering login page with an error message for invalid credentials
#             error_message = 'Invalid credentials. Please try again.'
#             return render(request, 'auth/new_login.html', {'error': error_message})
#     else:
#         # Rendering the login page for GET requests
#         return render(request, 'auth/new_login.html')