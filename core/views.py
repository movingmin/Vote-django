from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from .models import Profile, SystemConfig, Vote

class IndexView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return redirect('/root')
            return redirect('/vote')
        return render(request, 'index.html')

    def post(self, request):
        action = request.POST.get('action')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if action == 'login':
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_superuser:
                    return redirect('/root')
                return redirect('/vote')
            else:
                messages.error(request, "로그인 실패: 아이디 또는 비밀번호를 확인하세요.")
        
        elif action == 'signup':
            first_name = request.POST.get('first_name')
            if User.objects.filter(username=username).exists():
                messages.error(request, "회원가입 실패: 이미 존재하는 아이디입니다.")
            else:
                user = User.objects.create_user(username=username, password=password, first_name=first_name)
                # Create default Profile (guest, cannot vote yet)
                Profile.objects.create(user=user, can_vote=False)
                login(request, user)
                messages.success(request, "회원가입 성공!")
                return redirect('/vote')

        return render(request, 'index.html')

def logout_view(request):
    logout(request)
    return redirect('/')

class VoteView(LoginRequiredMixin, View):
    def get(self, request):
        config = SystemConfig.load()
        try:
            profile = request.user.profile
            can_vote = profile.can_vote
        except Profile.DoesNotExist:
            can_vote = False
            # Create profile if missing
            profile = Profile.objects.create(user=request.user, can_vote=False)

        has_voted = Vote.objects.filter(user=request.user).exists()

        context = {
            'message': config.message,
            'can_vote': can_vote and not has_voted,
            'has_voted': has_voted
        }
        return render(request, 'vote.html', context)

    def post(self, request):
        config = SystemConfig.load()
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            return redirect('/vote')

        if not profile.can_vote:
            messages.error(request, "투표 권한이 없습니다.")
            return redirect('/vote')

        if Vote.objects.filter(user=request.user).exists():
            messages.error(request, "이미 투표하셨습니다.")
            return redirect('/vote')

        candidate = request.POST.get('candidate')
        if candidate:
            Vote.objects.create(user=request.user, candidate=candidate)
            messages.success(request, "투표가 완료되었습니다.")
        
        return redirect('/vote')

class AdminView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request):
        config = SystemConfig.load()
        results = Vote.objects.values('candidate').annotate(count=Count('id')).order_by('-count')
        
        keyword = request.GET.get('keyword', '')
        users = []
        if keyword:
            users = User.objects.filter(username__icontains=keyword) | User.objects.filter(first_name__icontains=keyword)
            # Annotate manually or via property
            for u in users:
                try:
                    u.profile
                except Profile.DoesNotExist:
                     Profile.objects.create(user=u, can_vote=False)
                u.has_voted = Vote.objects.filter(user=u).exists()
        
        context = {
            'message': config.message,
            'results': results,
            'users': users,
            'keyword': keyword
        }
        return render(request, 'admin.html', context)

    def post(self, request):
        action = request.POST.get('action')
        
        if action == 'update_message':
            config = SystemConfig.load()
            config.message = request.POST.get('message')
            config.save()
            messages.success(request, "투표 메시지가 변경되었습니다.")
        
        elif action == 'search_user':
            keyword = request.POST.get('keyword')
            return redirect(f'/root/?keyword={keyword}')
        
        elif action == 'grant_permission':
            user_id = request.POST.get('user_id')
            try:
                profile = Profile.objects.get(user_id=user_id)
                profile.can_vote = True
                profile.save()
                messages.success(request, "투표 권한이 부여되었습니다.")
            except Profile.DoesNotExist:
                pass
            return redirect(request.META.get('HTTP_REFERER', '/root/'))

        elif action == 'void_vote':
            user_id = request.POST.get('user_id')
            Vote.objects.filter(user_id=user_id).delete()
            messages.success(request, "해당 사용자의 투표가 무효 처리되었습니다.")
            return redirect(request.META.get('HTTP_REFERER', '/root/'))

        elif action == 'reset_votes':
            Vote.objects.all().delete()
            messages.warning(request, "모든 투표 결과가 초기화되었습니다.")
        
        return redirect('/root/')
