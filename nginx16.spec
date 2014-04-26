%define packagename     nginx
%define nginx_user      nginx
%define nginx_group     %{nginx_user}
%define nginx_home      %{_localstatedir}/lib/nginx
%define nginx_home_tmp  %{nginx_home}/tmp
%define nginx_logdir    %{_localstatedir}/log/nginx
%define nginx_confdir   %{_sysconfdir}/nginx
%define nginx_datadir   %{_datadir}/nginx
%define nginx_webroot   %{nginx_datadir}/html

Name:           nginx16
Version:        1.6.0
Release:        1%{?dist}
Summary:        Robust, small and high performance http and reverse proxy server
Group:          System Environment/Daemons   

# BSD License (two clause)
# http://www.freebsd.org/copyright/freebsd-license.html
License:        BSD
URL:            http://nginx.net/ 
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:      pcre-devel,zlib-devel,openssl-devel,perl,perl(ExtUtils::Embed)
Requires:           pcre,zlib,openssl
Requires:           perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
# for /usr/sbin/useradd
Requires(pre):      shadow-utils
Requires(post):     chkconfig
# for /sbin/service
Requires(preun):    chkconfig, initscripts
Requires(postun):   initscripts
Provides: nginx = %{version}-%{release}
Conflicts: nginx < 1.6.0

Source0:    http://sysoev.ru/nginx/nginx-%{version}.tar.gz
Source1:    %{packagename}.init
Source2:    %{packagename}.logrotate
Source3:    virtual.conf
Source4:    ssl.conf
Source5:    %{packagename}.sysconfig
Source100:  index.html
Source101:  poweredby.png
Source102:  nginx-logo.png
Source103:  50x.html
Source104:  404.html

# removes -Werror in upstream build scripts.  -Werror conflicts with
# -D_FORTIFY_SOURCE=2 causing warnings to turn into errors.
Patch0:     nginx-auto-cc-gcc.patch

# configuration patch to match all the Fedora paths for logs, pid files
# etc.
Patch1:     nginx-1.6.0-conf.patch

%description
Nginx [engine x] is an HTTP(S) server, HTTP(S) reverse proxy and IMAP/POP3
proxy server written by Igor Sysoev.

%prep
%setup -q -n %{packagename}-%{version}

%patch0 -p0
%patch1 -p1

%build
# nginx does not utilize a standard configure script.  It has its own
# and the standard configure options cause the nginx configure script
# to error out.  This is is also the reason for the DESTDIR environment
# variable.  The configure script(s) have been patched (Patch1 and
# Patch2) in order to support installing into a build environment.
export DESTDIR=%{buildroot}
./configure \
    --user=%{nginx_user} \
    --group=%{nginx_group} \
    --prefix=%{nginx_datadir} \
    --sbin-path=%{_sbindir}/%{packagename} \
    --conf-path=%{nginx_confdir}/%{packagename}.conf \
    --error-log-path=%{nginx_logdir}/error.log \
    --http-log-path=%{nginx_logdir}/access.log \
    --http-client-body-temp-path=%{nginx_home_tmp}/client_body \
    --http-proxy-temp-path=%{nginx_home_tmp}/proxy \
    --http-fastcgi-temp-path=%{nginx_home_tmp}/fastcgi \
    --http-uwsgi-temp-path=%{nginx_home_tmp}/uwsgi \
    --http-scgi-temp-path=%{nginx_home_tmp}/scgi \
    --pid-path=%{_localstatedir}/run/%{packagename}.pid \
    --lock-path=%{_localstatedir}/lock/subsys/%{packagename} \
    --with-http_ssl_module \
    --with-http_realip_module \
    --with-http_addition_module \
    --with-http_auth_request_module \
    --with-http_sub_module \
    --with-http_dav_module \
    --with-http_flv_module \
    --with-http_mp4_module \
    --with-http_gunzip_module \
    --with-http_gzip_static_module \
    --with-http_random_index_module \
    --with-http_secure_link_module \
    --with-http_spdy_module \
    --with-http_stub_status_module \
    --with-http_perl_module \
    --with-mail \
    --with-mail_ssl_module \
    --with-file-aio \
    --with-ipv6 \
    --with-cc-opt="%{optflags} $(pcre-config --cflags)"
make %{?_smp_mflags} 

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} INSTALLDIRS=vendor
find %{buildroot} -type f -name .packlist -exec rm -f {} \;
find %{buildroot} -type f -name perllocal.pod -exec rm -f {} \;
find %{buildroot} -type f -empty -exec rm -f {} \;
find %{buildroot} -type f -exec chmod 0644 {} \;
find %{buildroot} -type f -name '*.so' -exec chmod 0755 {} \;
chmod 0755 %{buildroot}%{_sbindir}/nginx
%{__install} -p -D -m 0755 %{SOURCE1} %{buildroot}%{_initrddir}/%{packagename}
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{packagename}
%{__install} -p -D -m 0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/sysconfig/%{packagename}
%{__install} -p -d -m 0755 %{buildroot}%{nginx_confdir}/conf.d
%{__install} -p -m 0644 %{SOURCE3} %{SOURCE4} %{buildroot}%{nginx_confdir}/conf.d
%{__install} -p -d -m 0755 %{buildroot}%{nginx_home_tmp}
%{__install} -p -d -m 0755 %{buildroot}%{nginx_logdir}
%{__install} -p -d -m 0755 %{buildroot}%{nginx_webroot}
%{__install} -p -m 0644 %{SOURCE100} %{SOURCE101} %{SOURCE102} %{SOURCE103} %{SOURCE104} %{buildroot}%{nginx_webroot}

# convert to UTF-8 all files that give warnings.
for textfile in CHANGES
do
    mv $textfile $textfile.old
    iconv --from-code ISO8859-1 --to-code UTF-8 --output $textfile $textfile.old
    rm -f $textfile.old
done

%clean
rm -rf %{buildroot}

%pre
if [ $1 == 1 ]; then
    %{_sbindir}/useradd -c "Nginx user" -s /bin/false -r -d %{nginx_home} %{nginx_user} 2>/dev/null || :
fi

%post
if [ $1 == 1 ]; then
    /sbin/chkconfig --add %{packagename}
fi

%preun
if [ $1 = 0 ]; then
    /sbin/service %{packagename} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{packagename}
fi

%postun
if [ $1 == 2 ]; then
    /sbin/service %{packagename} upgrade || :
fi

%files
%defattr(-,root,root,-)
%doc LICENSE CHANGES README
%{nginx_datadir}/
%{_sbindir}/%{packagename}
%{_mandir}/man3/%{packagename}.3pm.gz
%{_initrddir}/%{packagename}
%dir %{nginx_confdir}
%dir %{nginx_confdir}/conf.d
%dir %{nginx_logdir}
%config(noreplace) %{nginx_confdir}/conf.d/*.conf
%config(noreplace) %{nginx_confdir}/win-utf
%config(noreplace) %{nginx_confdir}/%{packagename}.conf.default
%config(noreplace) %{nginx_confdir}/mime.types.default
%config(noreplace) %{nginx_confdir}/fastcgi.conf
%config(noreplace) %{nginx_confdir}/fastcgi.conf.default
%config(noreplace) %{nginx_confdir}/fastcgi_params
%config(noreplace) %{nginx_confdir}/fastcgi_params.default
%config(noreplace) %{nginx_confdir}/scgi_params
%config(noreplace) %{nginx_confdir}/scgi_params.default
%config(noreplace) %{nginx_confdir}/uwsgi_params
%config(noreplace) %{nginx_confdir}/uwsgi_params.default
%config(noreplace) %{nginx_confdir}/koi-win
%config(noreplace) %{nginx_confdir}/koi-utf
%config(noreplace) %{nginx_confdir}/%{packagename}.conf
%config(noreplace) %{nginx_confdir}/mime.types
%config(noreplace) %{_sysconfdir}/logrotate.d/%{packagename}
%config(noreplace) %{_sysconfdir}/sysconfig/%{packagename}
%dir %{perl_vendorarch}/auto/%{packagename}
%{perl_vendorarch}/%{packagename}.pm
%{perl_vendorarch}/auto/%{packagename}/%{packagename}.so
%attr(-,%{nginx_user},%{nginx_group}) %dir %{nginx_home}
%attr(-,%{nginx_user},%{nginx_group}) %dir %{nginx_home_tmp}


%changelog
* Sat Apr 26 2014 Andy Thompson <andy@webtatic.com> - 1.6.0-1
- Fork nginx14 package
- Rename to nginx16
- Update to 1.6.0
- Enable spdy and auth request modules
- Update conf patch to match upstream changes
