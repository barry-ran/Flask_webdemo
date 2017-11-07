# -*- coding: utf-8 -*-
from flask import render_template, request, flash, redirect, url_for, current_app, abort, jsonify
from . import auth
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
from ..models import User, LoginLog
from .. import db
from flask_login import login_user, logout_user, login_required, current_user
import time, json
from ..email import send_email

###############################################################################

@auth.before_app_request
def before_request():
    '''
    @note: 修饰的函数会在请求处理之前被调用
    '''
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and str(request.endpoint[:5]) != 'auth.':
                #and str(request.endpoint) != 'static':
            return redirect(url_for('auth.unconfirmed'))

###############################################################################

@auth.route('/unconfirmed')
def unconfirmed():
    '''
    @note: 发送确认邮件后登陆未确认
    '''
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

###############################################################################

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    '''
    @note: 点击确认邮件链接后
    '''
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('您已经确认了您的帐户. 谢谢!','info')
    else:
        flash('确认链接无效或已过期.','warning')
        return render_template('auth/unconfirmed.html')
    return redirect(url_for('main.index'))

###############################################################################

@auth.route('/confirm')
@login_required
def resend_confirmation():
    '''
    @note: 从新发送确认邮件
    '''
    token = current_user.generate_confirmation_token()

    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('通过电子邮件发送了一封新的确认电子邮件.','info')
    return redirect(url_for('main.index'))

###############################################################################

@auth.route('/login', methods=['GET', 'POST'])
def login():
    '''
    @note: 用户登录
    '''
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first() # 数据库查询

        if user is not None and user.verify_password(form.password.data): # 用户是否存在以及是否正确

            login_user(user,form.remember_me.data) # 记住我功能，bool值
            flash('Hi, %s, Welcome to xxx Platform............' % user.username,'info')

            # 记录登陆日志
            users = LoginLog()
            #print user.username # 用户
            users.loginuser=user.username
            users.logintime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) #时间
            users.login_browser=request.user_agent #代理
            users.login_ip=request.remote_addr # 登录地址
            db.session.add(users) # 提交
            db.session.commit()

            # 用户每次登录 通知管理员     
            send_email(current_app.config['FLASKY_ADMIN'], '登录通知','auth/email/login_notice',user=user, ip=request.remote_addr, agent=request.user_agent)
          
            return redirect(url_for('main.index')) # 如果认证成功则重定向到已认证首页
        else:
            flash(u'邮箱或密码无效,请重新输入!','danger')    # 如果认证错误则flash一条消息过去
    return render_template('auth/login.html',form=form)

###############################################################################

@auth.route('/register', methods=['GET', 'POST'])
def register():
    '''
    @note: 用户注册
    '''
    form = RegistrationForm()
    if form.validate_on_submit():
        # 检查config.py中定义的公司邮箱后缀名
        # if current_app.config['COMPANY_MAIL_SUFFIX'] != str(form.email.data).split('@')[1]:
        #     flash('严禁使用非公司邮箱进行注册操作!', 'danger')
        #     return render_template('auth/register.html', form=form)

        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()

        token = user.generate_confirmation_token()

        send_email(user.email, '账户确认','auth/email/confirm', user=user, token=token)

        flash('已通过电子邮件向您发送确认电子邮件.','info')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

###############################################################################

@auth.route('/logout')
def logout():
    '''
    @note: 用户登出
    '''
    logout_user()
    flash('logout success...', 'success')
    return redirect(url_for('auth.login'))

###############################################################################

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    '''
    @note: 登录状态更改密码
    '''
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('您的密码已更新.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('无效的密码.','warning')
    return render_template("auth/change_password.html", form=form)

###############################################################################

@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    '''
    @note: 发起重置密码请求
    '''
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        #print user
        if user:
            token = user.generate_reset_token()
            send_email(user.email, u'密码重置',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash(u'密码重设邮件已经发送到你的邮箱，请及时查收。', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

###############################################################################

@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    '''
    @note: 发起重置密码请求后携带token确认
    '''
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print user
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('您的密码已更新.','success')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)

###############################################################################

@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    '''
    @note: 更改邮箱
    '''
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, '确认您的邮箱地址',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('已发送一封包含确认您的新电子邮件地址的说明的电子邮件。','info')
            return render_template("auth/change_email.html", form=form)
        else:
            flash('无效的邮箱或密码','danger')
    return render_template("auth/change_email.html", form=form)

###############################################################################

@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    '''
    @note: 更改邮箱
    '''
    if current_user.change_email(token):
        flash('您的电子邮件地址已更新.','info')
    else:
        flash('无效的请求.','warning')
    return redirect(url_for('main.index'))

###############################################################################

@auth.route('/delete_user',methods=['GET', 'POST'])
@login_required
def delete_user():

    '''
    @note: 在登陆状态下只允许管理者进入，否则来到403禁止登陆界面
    '''
    if request.method == 'POST':
        check_id = json.loads(request.form.get('data'))['check_id']
        del_user = User.query.filter_by(id=check_id).first()
        try:
            db.session.delete(del_user)
            print check_id
            return  jsonify({"result":True,"message":"用户删除成功"})
        except Exception, e:
            db.session.rollback()
            print e
            return  jsonify({"result":False,"message":"用户删除失败".format(e)})

###############################################################################