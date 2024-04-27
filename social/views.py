from typing import Any
from django.db import models
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.utils import timezone
from django.views.generic import FormView,CreateView,TemplateView,View,UpdateView,DetailView,ListView
from social.forms import RegistrationForm,LoginForm,UserProfileForm,PostForm,CommentForm,StoryForm
from django.urls import reverse
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import never_cache
from django.contrib import messages
from social.models import UserProfile,Posts,Stories
from social.decorators import login_required
from django.utils.decorators import method_decorator 


decs=[login_required,never_cache]
class SignUpView(CreateView):
    template_name='register.html'#getinu pakaram
    form_class=RegistrationForm #oru html pageil form ine render cheyyan 

    def get_success_url(self):
        return reverse('signin')# render um,redirectinum okke pakaram 
    

class SigninView(FormView): # dec 5
    template_name='login.html'
    form_class=LoginForm

    def post(self,request,*args,**kwargs):
        form=LoginForm(request.POST)
        if form.is_valid():
            uname=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            user_object=authenticate(request,username=uname,password=pwd)
            if user_object:
                login(request,user_object)
                print("logged in successfully")
                return redirect('index')#redirect kodukumbol signin pageinte get work cheyyum ie.,box okke blank aarikum
        print("error in login")
        messages.error(request,'failed to login invalid credentials')
        return render(request,"login.html",{'form':form})
    
@method_decorator(decs,name="dispatch")    
class IndexView(CreateView,ListView):
    template_name='index.html'
    form_class=PostForm
    model=Posts
    context_object_name="data" #dec12

    def form_valid(self,form):# dec 12(form save cheyyunnathinu munne ethelum field add cheyyan or change cheyyan)
        form.instance.user=self.request.user #form.instance means postform(postmodel) athinte user fieldileku value kodukkunnu   
        return super().form_valid(form)# super classil avar cheythuvechekkunnathu call cheyyan

    def get_success_url(self):# method post kodukkumbol,action success aayttu athine redirect cheyyan (used in createview,updateview)
        return reverse('index')
    
    def get_queryset(self):
        blocked_profile=self.request.user.profile.block.all()
        
        qs=Posts.objects.all().exclude(user__id__in=blocked_profile).order_by("-created_date")
        return qs
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        current_date=timezone.now()
        context['stories']=Stories.objects.filter(expiry_date=current_date)
        return context


class SignOutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect('signin')
    

@method_decorator(decs,name="dispatch")    
class ProfileUpdateView(UpdateView):#  dec 6 oru userinte profile edit cheyyan
    template_name='profile_add.html'
    form_class=UserProfileForm
    model=UserProfile
    def get_success_url(self):
        return reverse('index')
    
@method_decorator(decs,name="dispatch")
class ProfileDetailView(DetailView):# dec7 oru userinte profileinte detail edukkan
    template_name="Profile_detail.html"
    model=UserProfile
    context_object_name="data"

    # def get(self,*args,**kwargs):
    # profile-id=kwargs.get('pk')
    # profile_object=Userprofile.objects.get(id=profile-id)
    # return render(request,"profile_detail.html",{'data':profile_object})
@method_decorator(decs,name="dispatch")
class ProfileListView(View):# ella userintem profile list cheyyan Dec 8
    def get(self,request,*args,**kwargs):
        qs=UserProfile.objects.all().exclude(user=request.user)# dec 11 login cheytha userinte profile kanathirikan vendi
        return render(request,"profile_list.html",{'data':qs})

@method_decorator(decs,name="dispatch")
class FollowView(View):#follow & unfollow button click cheyyumbol (dec11)
    def post(self,request,*args,**kwargs):
       id=kwargs.get('pk')
       profile_object=UserProfile.objects.get(id=id)
       action=request.POST.get('action')
       if action=='follow':
           request.user.profile.following.add(profile_object)
       elif action=='unfollow':
           request.user.profile.following.remove(profile_object)          
       return redirect('index')
    
@method_decorator(decs,name="dispatch")
class PostLikeView(View):
    def post(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        post_object=Posts.objects.get(id=id)
        action=request.POST.get("action")
        if action=='like':
            post_object.liked_by.add(request.user)
        elif action=='dislike':
            post_object.liked_by.remove(request.user)
        return redirect('index')

@method_decorator(decs,name="dispatch")   
class CommentView(CreateView):
     template_name="index.html"
     form_class=CommentForm

     def get_success_url(self):
          return reverse("index")
     
     def form_valid(self, form):
          id=self.kwargs.get('pk')
          post_object=Posts.objects.get(id=id)
          form.instance.user=self.request.user
          form.instance.post=post_object
          return super().form_valid(form)


@method_decorator(decs,name="dispatch")
class ProfileBlockView(View):
     def post(self,request,*args,**kwargs):
          id=kwargs.get("pk")
          profile_object=UserProfile.objects.get(id=id)
          action=request.POST.get("action")
          if action == "block":
               request.user.profile.block.add(profile_object)
          elif action == "unblock":
               request.user.profile.block.remove(profile_object)
          return redirect("index")


@method_decorator(decs,name="dispatch")   
class StoryCreateView(View):
     
     def post(self,request,*args,**kwargs):
          form=StoryForm(request.POST,files=request.FILES)
          if form.is_valid():
               form.instance.user=request.user
               form.save()
               return redirect("index")
          return redirect("index")
     


     #feb 20 git push