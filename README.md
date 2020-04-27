# either_project [3기 / 서울 / 1반 / 박선환]

- [프로젝트 흐름 정리](#프로젝트_흐름_정리)
- [새롭게 알게된 점](#새롭게_알게된_점)
- [어려웠던 점](#어려웠던_점)



# 프로젝트\_흐름_정리

## 1. Start Project

- ```bash
  $ django-admin startproject either_project
  $ cd either_project

  $ python manage.py startapp accounts
  $ python manage.py startapp eithers
  ```

- `either_project/settings.py`  설정

  ```python
  ALLOWED_HOSTS = ['*']

  INSTALLED_APPS = [
      ...
      'accounts',
      'eithers',
      'bootstrap4', # bootstrap4 설치 => pip install django-bootstrap4
  ]

  TEMPLAGES = [{
      ...
      'DIRS': [os.path.join(BASE_DIR, 'templates')] # base.html 사용하기 위해
      ...
  }]

  LANGUAGE_CODE = 'ko-kr'
  TIME_ZONE = 'Asia/Seoul'

  # message framework 사용하기 위해
  from django.contrib.messages import constants as messages_constants
  MESSAGE_LEVEL = messages_constants.DEBUG
  MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
  ```

- `either_project/urls.py` 설정

  ```python
  from django.contrib import admin
  from django.urls import path, include
  from eithers import views

  urlpatterns = [
      path('', views.index), # 바로 메인 페이지로 이동
      path('admin/', admin.site.urls),
      path('accounts/', include('accounts.urls')),
      path('eithers/', include('eithers.urls')),
  ]
  ```



## 2. Model

- `eithers/models.py`

  ```python
  from django.db import models
  from django.contrib.auth.models import User

  # 유저(1) - 투표(N) 관계 구현을 위한 class
  class Vote(models.Model):
      creator = models.ForeignKey(User, on_delete=models.CASCADE)
      title = models.CharField(max_length=30)
      description = models.CharField(max_length=100)
      category = models.CharField(max_length=30)
      item1 = models.CharField(max_length=100)
      item2 = models.CharField(max_length=100)
      item1_num = models.IntegerField(default=0)
      item2_num = models.IntegerField(default=0)
      created_at = models.DateTimeField(auto_now_add=True)
      updated_at = models.DateTimeField(auto_now=True)

  # 투표(M) - 투표 참여자(N) 관계 구현을 위한 class
  class VoteSelection(models.Model):
      user = models.ForeignKey(User, on_delete=models.CASCADE)
      vote = models.ForeignKey(Vote, on_delete=models.CASCADE)
      selection = models.IntegerField()

  # 유저(1) - 댓글(N), 투표(1) - 댓글(N) 관계 구현을 위한 class
  class Comment(models.Model):
      author = models.ForeignKey(User, on_delete=models.CASCADE)
      vote = models.ForeignKey(Vote, on_delete=models.CASCADE)
      selection = models.ForeignKey(VoteSelection, on_delete=models.CASCADE)
      content = models.CharField(max_length=200)
      created_at = models.DateTimeField(auto_now_add=True)
      updated_at = models.DateTimeField(auto_now=True)
  ```

- User Model은 django 내부에 구현된 User Model을 사용할 것이기 때문에 별도로 생성하지 않아도 된다.

- ```bash
  $ python manage.py makemigrations
  $ python manage.py migrate
  ```



## 3. Form

- `eithers/forms.py`

  ```python
  from django import forms
  from .models import Vote, Comment

  class VoteForm(forms.ModelForm):
      class Meta:
          model = Vote
          fields = ['title', 'description', 'category', 'item1', 'item2']

  class CommentForm(forms.ModelForm):
      class Meta:
          model = Comment
        fields = ['content']
  ```

- User 관련 Form의 경우, django 내부에 구현된 UserCreationForm, AuthenticationForm을 사용할 것이기 때문에 별도로 생성하지 않아도 된다.



## 4. Admin

- `eithers/admin.py`

  ```python
  from django.contrib import admin
  from .models import Vote, Comment, VoteSelection

  admin.site.register(Vote)
  admin.site.register(Comment)
  admin.site.register(VoteSelection)
  ```

- ```bash
  $ python manage.py createsuperuser
  ```



## 5. URL

- `accounts/urls.py`

  ```python
  from django.urls import path
  from . import views

  app_name = 'accounts'

  urlpatterns = [
      path('signup/',views.signup, name='signup'), # 회원가입 및 form 표시
      path('login/',views.login, name='login'), # 로그인 및 form 표시
      path('logout/',views.logout, name='logout'), # 로그아웃
      ]
  ```

- `eithers/urls.py`

  ```python
  from django.urls import path
  from . import views

  app_name = 'eithers'

  urlpatterns = [
      path('', views.index, name='index'), # 투표 리스트
      path('create/', views.create, name='create'), # 투표 생성
      path('<int:vote_pk>/', views.detail, name='detail'), # 투표 상세 내역
      path('<int:vote_pk>/comments/', views.comment_create, name='comment_create'), # 투표 댓글 생성
      path('random_vote/', views.random_vote, name='random_vote'), # 랜덤하게 투표 상세 내역 반환
  ]
  ```



## 6. View & Template

### base.html

- bootstrap4 사용 위한 setting

  - `{% load bootstrap4 %}`
  - `{% bootstrap_css %}`
  - `{% bootstrap_javascript jquery='full' %}`

- block

  ```html
  <body>
      <!-- navbar 구현 -->
  	{% block content %}
  	{% endblock %}
      <!-- footer 구현 -->
  </body>
  ```

- 사용자 인증여부에 따라 분기한 UI 구성

  ```html
  {% if user.is_authenticated %}
  {% else %}
  {% endif %}
  ```

- message framework 활용하기 위한 코드

  ```html
  {% if messages %}
  {% for message in messages %}
  	<div class="row" style="margin:20px auto;">
  	<div class="col-sm-12">
  		<div class="alert alert-info">
  		<strong class="text-center">{{ message.message }}</strong>
  		</div>
  	</div>
  	</div>
  {% endfor %}
  {% endif %}

  {% block content %}
  {% endblock %}
  ```



### accounts app

- `accounts/views.py` - `import`

  ```python
  from django.shortcuts import render, redirect, get_object_or_404
  from django.contrib.auth import login as auth_login # 계정 로그인
  from django.contrib.auth import logout as auth_logout # 계정 로그아웃
  from django.contrib.auth.decorators import login_required # 로그인이 되어 있지 않다면 로그인 page 반환
  from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
  from django.contrib import messages # messages framework
  ```

- 회원가입

  ```python
  # accounts/views.py
  def signup(request):
      if request.user.is_authenticated: # 이미 인증된 사용자라면
          return redirect('eithers:index')

      if request.method == 'POST': # 완성된 가입 form 제출
          form = UserCreationForm(request.POST)
          if form.is_valid(): # 유효성 검증
              user = form.save()
              auth_login(request, user) # 가입과 동시에 로그인
              messages.info(request, '회원가입을 성공하셨습니다.')
              return redirect('eithers:index')
      else: # 빈 가입 form 요청
          form = UserCreationForm()
      context = {
          'form': form
      }
      return render(request, 'accounts/signup.html', context)
  ```

  ```html
  <!-- accounts/templates/accounts/signup.html -->
  {% extends 'base.html' %}
  {% load bootstrap4 %}

  {% block content %}

  <h1 class="text-center">Signup</h1>
  <hr>
  <form action="" method="POST">
      {% csrf_token %}
      {% bootstrap_form form %}
      {% bootstrap_button "Signup" button_type="submit" button_class="btn-primary" %}
  </form>
  {% endblock %}
  ```

- 로그인

  ```python
  # accounts/views.py
  def login(request):
      if request.user.is_authenticated: # 이미 인증된 사용자라면
          return redirect('eithers:index')

      if request.method == 'POST': # 완성된 form 제출
          form = AuthenticationForm(request, request.POST)
          if form.is_valid():
              auth_login(request, form.get_user())
              messages.info(request, '로그인을 성공하셨습니다.')
              # 로그인 전 요청한 url이 있으면 해당 url로, 없다면 리뷰 목록 페이지로 이동(단축 평가 활용)
              return redirect(request.GET.get('next') or 'eithers:index')
      else: # 빈 로그인 form 요청
          form = AuthenticationForm()
      context = {
          'form': form
      }
      return render(request, 'accounts/login.html', context)
  ```

  ```html
  <!-- accounts/templates/accounts/login.html -->
  {% extends 'base.html' %}
  {% load bootstrap4 %}

  {% block content %}
  <h1 class="text-center">Login</h1>
  <hr>
  <form action="" method="POST">
      {% csrf_token %}
      {% bootstrap_form form %}
      {% bootstrap_button "Login" button_type="submit" button_class="btn-primary" %}
  </form>
  {% endblock %}
  ```

- 로그아웃

  ```python
  # accounts/views.py
  @login_required # 로그인 안된 상태에서는 로그인 페이지로 이동
  def logout(request):
      auth_logout(request) # GET 방식
      messages.info(request, '로그아웃 되었습니다.')
      return redirect('eithers:index')
  ```



### eithers app

- `eithers/views.py` - `import`

  ```python
  from django.shortcuts import render, redirect, get_object_or_404
  from django.contrib.auth import get_user_model
  from django.contrib.auth.decorators import login_required
  from django.views.decorators.http import require_POST
  from .forms import VoteForm, CommentForm
  from .models import Vote, VoteSelection, Comment
  from django.contrib import messages
  import random
  ```

- 신규 투표 생성

  ```python
  @login_required
  def create(request):
      if request.method == 'POST':
          form = VoteForm(request.POST)
          if form.is_valid():
              vote = form.save(commit=False)
              vote.creator = request.user
              vote.save()
              messages.info(request, '질문이 생성되었습니다.')
              return redirect('eithers:detail', vote.pk)
      else:
          form = VoteForm()
      context = {
          'form':form,
      }
      return render(request, 'eithers/form.html', context)
  ```

```html
  {% extends 'base.html' %}
  {% load bootstrap4 %}

  {% block content %}
  <h1 class="text-center">New Vote</h1>
  <hr>
  <form action="" method = "POST">
  {% csrf_token %}
  {% bootstrap_form form %}
  {% bootstrap_button "Save" button_type="submit" button_class="btn-primary" %}
  </form>
  {% endblock %}
```

- 전체 투표 목록 조회

  ```python
  def index(request):
      votes = Vote.objects.all()
      context = {
          'votes': votes,
      }
      return render(request, 'eithers/vote_list.html', context)
  ```

  ```html
  {% extends 'base.html' %}
  {% load bootstrap4 %}

  {% block content %}
  <h1 class="text-center">Votes</h1>
  <hr>
  {% if votes %}
  <table class="table">
    <thead class="thead-dark">
    <tr>
        <th scope="col">#</th>
        <th scope="col">Title</th>
        <th scope="col">Author</th>
        <th scope="col">Category</th>
        <th scope="col">Created_at</th>
      </tr>
    </thead>
    <tbody>
      {% for vote in votes %}
      <tr>
        <th scope="row">{{ vote.pk }}</th>
        <td><a href="{% url 'eithers:detail' vote.pk %}">{{ vote.title }}</a></td>
        <td>{{ vote.creator }}</td>
        <td>{{ vote.category }}</td>
        <td>{{ vote.created_at }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% else %}
  <h3 class="text-center">작성된 투표가 없습니다.</h3>
  {% endif %}
  {% endblock %}
  ```

- 단일 투표 상세 조회 / 댓글 전체 조회 / 댓글 작성 form 표시

  ```python
  @login_required
  def detail(request, vote_pk):
      vote = get_object_or_404(Vote, pk=vote_pk)
      if request.method == 'POST':
          vs = VoteSelection()
          vs.vote = vote
          vs.user = request.user
          if 'item1' in request.POST:
              vs.selection = 1
              vote.item1_num += 1
          elif 'item2' in request.POST:
              vs.selection = 2
              vote.item2_num += 1
          vs.save()
          vote.save()
          messages.info(request, '투표에 성공하셨습니다!')
          return redirect('eithers:detail', vote.pk)
      else:
          comment_form = CommentForm()
          if vote.item1_num + vote.item2_num > 0:
              item1_ratio = round(vote.item1_num/(vote.item1_num + vote.item2_num)*100, 2)
              item2_ratio = round(vote.item2_num/(vote.item1_num + vote.item2_num)*100, 2)
          else:
              item1_ratio = item2_ratio = 0
          try:
              voteselection = get_object_or_404(VoteSelection, user=request.user, vote=vote)
              if voteselection.selection == 1:
                  myselection = vote.item1
              else:
                  myselection = vote.item2
          except:
              myselection = ''
          context = {
              'vote': vote,
              'comment_form': comment_form,
              'myselection': myselection,
              'item1_ratio': item1_ratio,
              'item2_ratio': item2_ratio,
          }
          return render(request, 'eithers/vote_detail.html', context)
  ```

  ```html
  {% extends 'base.html' %}
  {% load bootstrap4 %}

  {% block content %}
  <div class="container my-3 py-3">
      <h1 class="text-center">{{ vote.title }}</h1>
      <hr>
      <ul>
          <li class="mb-0 "><b>작성자:</b> {{ vote.creator }}</li>
          <li class="mb-0 "><b>설명:</b> {{ vote.description }}</li>
          <li class="mb-0 "><b>카테고리:</b> {{ vote.category }}</li>
          <li class="mb-0 "><b>생성일시:</b> {{ vote.created_at }}</li>
      </ul>
      <hr>
      {% if myselection %}
      <h3 class="text-center">Result</h3>
      <h5 class="text-center">나의 선택:
        {{ myselection }}
      </h5>
      </h3>
      <div class="container">
        <div class="row">
          <div class="col-6 bg-primary text-white text-center p-3 rounded">
            <h3 class="my-3">{{ item1_ratio }}%</h3>
            <h5 class="my-3">{{ vote.item1_num }}</h5>
            <h4 class="my-3">{{ vote.item1 }}</h4>
          </div>
          <div class="col-6 bg-danger text-white text-center p-3 rounded">
            <h3 class="my-3">{{ item2_ratio }}%</h3>
            <h5 class="my-3">{{ vote.item2_num }}</h5>
            <h4 class="my-3">{{ vote.item2 }}</h4>
          </div>
        </div>
      </div>

      {% else %}
      <h3 class="text-center my-3">선택해주세요!</h3>
      <form class="container" action="{% url 'eithers:detail' vote.pk %}" method="POST">
          {% csrf_token %}
          <div class="row">
            <button class="col-6 m-0 py-5 bg-primary text-white btn-lg btn-block" type="submit" name="item1">{{ vote.item1 }}</button>
            <button class="col-6 m-0 py-5 bg-danger text-white btn-lg btn-block" type="submit" name="item2">{{ vote.item2 }}</button>
          </div>
          </form>
      {% endif %}
  </div>
  <div class="container border border-secondary rounded my-3 py-3">
      <h5>댓글 | ({{ vote.comment_set.all.count }})</h4>
      <hr>
      {% if vote.comment_set.all %}
      <table class="table table-striped text-center">
        <thead class="thead-dark">
          <tr>
            <th scope="col">Content</th>
            <th scope="col">Author</th>
            <th scope="col">Selection</th>
            <th scope="col">Created_at</th>
          </tr>
        </thead>
        <tbody>
          {% for comment in vote.comment_set.all %}
          <tr>
            <td>{{ comment.content }}</td>
            <td>{{ comment.author }}</td>
            <td>
              {{ myselection }}
            </td>
            <td>{{ comment.created_at }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
      {% else %}
        <h5>댓글이 없습니다.</h5>
      {% endif %}
      {% if user.is_authenticated %}
      <form action="{% url 'eithers:comment_create' vote.pk %}" method="POST">
      	{% csrf_token %}
      	{% bootstrap_form comment_form %}
      	{% bootstrap_button "댓글 작성" button_type="submit" button_class="btn-primary" %}
      </form>
      {% endif %}
  </div>
  {% endblock %}
  ```

- 신규 댓글 생성

  ```python
  @login_required
  def comment_create(request, vote_pk):
      vote = get_object_or_404(Vote, pk=vote_pk)
      try:
          selection = get_object_or_404(VoteSelection, user=request.user, vote=vote)
          form = CommentForm(request.POST)
          if form.is_valid():
              comment = form.save(commit=False)
              comment.author = request.user
              comment.vote = vote
              comment.selection = selection
              comment.save()
              messages.info(request, '댓글이 생성되었습니다.')
      except:
          messages.info(request, '투표를 먼저 진행해주세요.')
      return redirect('eithers:detail', vote.pk)
  ```

- 랜덤하게 투표 반환(해당 사용자가 아직 투표하지 않은 투표들 중에)

  ```python
  @login_required
  def random_vote(request):
      votes = Vote.objects.all()
      possible = []
      for vote in votes:
          try:
              get_object_or_404(VoteSelection, user=request.user, vote=vote)
          except:
              possible.append(vote)
      if possible:
          vote = random.choice(possible)
          return redirect('eithers:detail', vote.pk)
      else:
          messages.info(request, '모든 질문에 답하셨네요! :)')
          return redirect('eithers:index')
  ```



# 새롭게\_알게된_점

- messages framework 사용 방법(`base.html`)

  ```python
  # settings.py
  from django.contrib.messages import constants as messages_constants
  MESSAGE_LEVEL = messages_constants.DEBUG
  MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

  # views.py
  from django.contrib import messages
  ...
  messages.info(request, '해당 댓글을 삭제할 수 없습니다.')
  ```

  ```html
  <!-- 이 코드를 base.html에 한 번만 넣어주면 된다! -->
  {% if messages %}
  {% for message in messages %}
      <div class="row" style="margin:20px auto;">
      <div class="col-sm-12">
          <div class="alert alert-info">
          <strong class="text-center">{{ message.message }}</strong>
          </div>
      </div>
      </div>
  {% endfor %}
  {% endif %}
  ```

- M : N 관계 구현

  ```python
  class VoteSelection(models.Model):
      user = models.ForeignKey(User, on_delete=models.CASCADE)
      vote = models.ForeignKey(Vote, on_delete=models.CASCADE)
      selection = models.IntegerField()
  ```

  - 기존의 테이블(M, N)에서 컬럼을 추가하는 방식으로는 구현이 불가능하다.
  - 결국 M 테이블과 N 테이블을 참조하는 새로운 테이블을 생성 해야한다.



# 어려웠던_점

- 주어진 상황 별로 서로 다른 결과값을 뱉어내는 걸 구현하는 게(코드 분기) 어려웠다. 가능하면 html 단 이전, view 혹은 model 단계에서 값을 분기하는 것이 편리한 것 같다.
- M : N 관계 구현할 때 머릿속으로 개념이 잘 잡히지 않아 애를 먹었다. 핵심은 별도의 테이블을 생성해야 한다는 것!