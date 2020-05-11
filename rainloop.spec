Name:             rainloop
Version:          1.14.0
Release:          1%{?dist}
Summary:          Simple, modern & fast web-based email client
License:          AGPL3
Group:            Networking/WWW
URL:              http://rainloop.net
Source0:          https://github.com/Rainloop/rainloop-webmail/releases/download/v%{version}/%{name}-community-%{version}.zip
Requires:         httpd
Requires:         php
Requires(post):   policycoreutils-python
Requires(postun): policycoreutils-python
BuildArch:        noarch

%description
Features:
- Modern user interface.
- Complete support of IMAP and SMTP protocols including SSL and STARTTLS.
- Sieve scripts (Filters and vacation message).
- Minimalistic resources requirements.
- Direct access to mail server is used (mails are not stored locally on web server).
- Allows for adding multiple accounts to primary one, simultaneous access to
  different accounts in different browser tabs is supported. Additional identities.
- Administrative panel for configuring main options.
- Really simple installation and update.
- Integration with Facebook, Google, Twitter and Dropbox.
- Managing folders list.
- Simple look'n'feel customization.
- Configurable multi-level caching system.
- Extending functionality with plugins installed through admin panel.
- Perfect rendering of complex HTML mails.
- Drag'n'drop for mails and attachments.
- Keyboard shortcuts support.
- Autocompletion of e-mail addresses.
http://www.rainloop.net/screenshots/

%prep
rm -rf %{name}-%{version}
mkdir %{name}-%{version}
cd %{name}-%{version}
unzip %{SOURCE0}

%build
# Nothing to do!!

%install
install -d -m 755 %{buildroot}%{_datadir}/%{name}
cp -r %{name}-%{version}/* %{buildroot}%{_datadir}/%{name}

# apache configuration
install -d -p $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d
cat > $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/%{name}.conf<<EOF
# rainloop configuration

Alias /%{name} %{_datadir}/%{name}

# Redirect to https
RewriteEngine On
RewriteRule ^/%{name}(/.*)?$  https://%{HTTP_HOST}/%{name}$1  [L,R=301]

<Directory %{_datadir}/%{name}>
    Require all granted
    php_admin_value post_max_size 25M
    php_admin_value upload_max_filesize 25M
</Directory>
<Directory %{_datadir}/%{name}/data>
    Require all denied
</Directory>
EOF

%files
%{_datadir}/%{name}
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%dir %attr(0750,apache,apache) %{_datadir}/%{name}/data

%post
/usr/sbin/semanage fcontext -a -t httpd_sys_rw_content_t '%{_datadir}/%{name}/data(/.*)?' 2>/dev/null || :
/usr/sbin/restorecon -R %{_datadir}/%{name} || :
/sbin/service httpd condrestart > /dev/null 2>&1 || :

%postun
if [ $1 -eq 0 ] ; then  # final removal
  /usr/sbin/semanage fcontext -d -t httpd_sys_rw_content_t '%{_datadir}/%{name}/data(/.*)?' 2>/dev/null || :
fi
/sbin/service httpd condrestart > /dev/null 2>&1 || :

%changelog
* Mon Apr 27 2020 Glen Johnson <gsfjohnson@gmail.com> 1.14.0-el7
- SElinux support
