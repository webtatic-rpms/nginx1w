%global  _hardened_build     1
%global  packagename         nginx
%global  nginx_user          nginx
%global  nginx_group         %{nginx_user}
%global  nginx_home          %{_localstatedir}/lib/nginx
%global  nginx_home_tmp      %{nginx_home}/tmp
%global  nginx_confdir       %{_sysconfdir}/nginx
%global  nginx_datadir       %{_datadir}/nginx
%global  nginx_logdir        %{_localstatedir}/log/nginx
%global  nginx_moduledir     %{_libdir}/nginx/modules
%global  nginx_webroot       %{nginx_datadir}/html

%if 0%{?fedora} >= 17 || 0%{?rhel} >= 6
# gperftools exist only on selected arches
%ifarch %{ix86} x86_64 ppc ppc64 %{arm}
%global  with_gperftools     1
%endif

%global  with_geoip          1
%endif

%if 0%{?fedora} >= 8 || 0%{?rhel} >= 6
# AIO missing on some arches, and only supported with kernel >= 2.6.22
%ifnarch aarch64
%global  with_aio   1
%endif
%endif

%if 0%{?fedora} >= 16 || 0%{?rhel} >= 7
%global  with_systemd 1
%global  with_pagespeed      1
%endif

%global  pagespeed_version   1.10.33.5

Name:              nginx19
Version:           1.9.12
Release:           0.1%{?dist}

Summary:           A high performance web server and reverse proxy server
Group:             System Environment/Daemons
# BSD License (two clause)
# http://www.freebsd.org/copyright/freebsd-license.html
License:           BSD
URL:               http://nginx.org/
BuildRoot:         %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Source0:           http://nginx.org/download/nginx-%{version}.tar.gz
Source1:           http://nginx.org/download/nginx-%{version}.tar.gz.asc
Source2:           https://github.com/pagespeed/ngx_pagespeed/archive/release-%{pagespeed_version}-beta.zip
Source3:           https://dl.google.com/dl/page-speed/psol/%{pagespeed_version}.tar.gz
Source10:          nginx.service
Source11:          nginx.logrotate
Source12:          nginx.conf
Source13:          nginx-upgrade
Source14:          nginx-upgrade.8
Source15:          nginx.init
Source16:          nginx.sysconfig
Source100:         index.html
Source101:         poweredby.png
Source102:         nginx-logo.png
Source103:         404.html
Source104:         50x.html

# removes -Werror in upstream build scripts.  -Werror conflicts with
# -D_FORTIFY_SOURCE=2 causing warnings to turn into errors.
Patch0:            nginx-auto-cc-gcc.patch

%if 0%{?with_gperftools}
BuildRequires:     gperftools-devel
%endif
BuildRequires:     openssl-devel
BuildRequires:     pcre-devel
%if 0%{?fedora:1} || 0%{?rhel} >= 6
BuildRequires:     perl-devel
%else
BuildRequires:     perl
%endif
BuildRequires:     perl(ExtUtils::Embed)
BuildRequires:     zlib-devel
Requires:          openssl
Requires:          pcre
Requires:          perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires(pre):     shadow-utils
Provides:          webserver

%if 0%{?with_systemd}
BuildRequires:     systemd
Requires(post):    systemd
Requires(preun):   systemd
Requires(postun):  systemd
%else
Requires(post):    chkconfig
Requires(preun):   chkconfig, initscripts
Requires(postun):  initscripts
%endif
Provides: nginx = %{version}-%{release}
Provides: nginx%{?_isa} = %{version}-%{release}
Conflicts: nginx < 1.6.0

# Don't provides extensions, which are not shared library, as .so
%{?filter_provides_in: %filter_provides_in %{nginx_moduledir}/.*\.so$}
%{?filter_setup}

%description
Nginx is a web server and a reverse proxy server for HTTP, SMTP, POP3 and
IMAP protocols, with a strong focus on high concurrency, performance and low
memory usage.

%if 0%{?with_geoip}
%package http_geoip
Summary: A module to provide variables with values depending on the client IP address
Group:             System Environment/Daemons
# BSD License (two clause)
# http://www.freebsd.org/copyright/freebsd-license.html
License:           BSD
BuildRequires:     GeoIP-devel
Requires:          %{name}%{?_isa} = %{version}-%{release}
Requires:          GeoIP

%description http_geoip
The ngx_http_geoip_module module creates variables with values depending on the
client IP address, using the precompiled MaxMind databases.
%endif

%package http_image_filter
Summary: A module to transform images
Group:             System Environment/Daemons
# BSD License (two clause)
# http://www.freebsd.org/copyright/freebsd-license.html
License:           BSD
BuildRequires:     gd-devel
Requires:          gd
Requires:          %{name}%{?_isa} = %{version}-%{release}

%description http_image_filter
The ngx_http_image_filter_module module is a filter that transforms images in
JPEG, GIF, and PNG formats.

%package http_xslt
Summary: A module to transform XML responses using XSLT stylesheets
Group:             System Environment/Daemons
# BSD License (two clause)
# http://www.freebsd.org/copyright/freebsd-license.html
License:           BSD
BuildRequires:     libxslt-devel
Requires:          %{name}%{?_isa} = %{version}-%{release}

%description http_xslt
The ngx_http_xslt_module is a filter that transforms XML responses using one or
more XSLT stylesheets.

%package mail
Summary: A collection of modules for serving a mail proxy
Group:             System Environment/Daemons
# BSD License (two clause)
# http://www.freebsd.org/copyright/freebsd-license.html
License:           BSD
Requires:          %{name}%{?_isa} = %{version}-%{release}

%description mail
A collection of modules for serving a mail proxy.

%package stream
Summary: A collection of modules for serving a stream proxy
Group:             System Environment/Daemons
# BSD License (two clause)
# http://www.freebsd.org/copyright/freebsd-license.html
License:           BSD
Requires:          %{name}%{?_isa} = %{version}-%{release}

%description stream
A collection of modules for serving a stream proxy.

%if 0%{?with_pagespeed}
%package ext-pagespeed
Summary: Automatic PageSpeed optimization module
Group:             System Environment/Daemons
# BSD License (two clause)
# http://www.freebsd.org/copyright/freebsd-license.html
License:           BSD
Requires:          %{name}%{?_isa} = %{version}-%{release}
Provides: %{name}-pagespeed = %{pagespeed_version}-%{release}
Provides: %{name}-pagespeed%{?_isa} = %{pagespeed_version}-%{release}

%description ext-pagespeed
ngx_pagespeed speeds up your site and reduces page load time by
automatically applying web performance best practices to pages and
associated assets (CSS, JavaScript, images) without requiring you to
modify your existing content or workflow.
%endif

%prep
%setup -q -n %{packagename}-%{version}
%patch0 -p0

%if 0%{?with_pagespeed}

%setup -q -n %{packagename}-%{version} -T -D -a 2
pushd ngx_pagespeed-release-%{pagespeed_version}-beta
tar -xzf %{SOURCE3}
popd

%endif

%build
# nginx does not utilize a standard configure script.  It has its own
# and the standard configure options cause the nginx configure script
# to error out.  This is is also the reason for the DESTDIR environment
# variable.
export DESTDIR=%{buildroot}
./configure \
    --prefix=%{nginx_datadir} \
    --sbin-path=%{_sbindir}/nginx \
    --conf-path=%{nginx_confdir}/nginx.conf \
    --error-log-path=%{nginx_logdir}/error.log \
    --http-log-path=%{nginx_logdir}/access.log \
    --http-client-body-temp-path=%{nginx_home_tmp}/client_body \
    --http-proxy-temp-path=%{nginx_home_tmp}/proxy \
    --http-fastcgi-temp-path=%{nginx_home_tmp}/fastcgi \
    --http-uwsgi-temp-path=%{nginx_home_tmp}/uwsgi \
    --http-scgi-temp-path=%{nginx_home_tmp}/scgi \
    --modules-path=%{nginx_moduledir} \
%if 0%{?with_systemd}
    --pid-path=/run/nginx.pid \
    --lock-path=/run/lock/subsys/nginx \
%else
    --pid-path=%{_localstatedir}/run/nginx.pid \
    --lock-path=%{_localstatedir}/lock/subsys/nginx \
%endif
    --user=%{nginx_user} \
    --group=%{nginx_group} \
%if 0%{?with_aio}
    --with-file-aio \
%endif
    --with-ipv6 \
    --with-http_ssl_module \
    --with-http_v2_module \
    --with-http_realip_module \
    --with-http_addition_module \
    --with-http_auth_request_module \
    --with-http_xslt_module=dynamic \
    --with-http_image_filter_module=dynamic \
%if 0%{?with_geoip}
    --with-http_geoip_module=dynamic \
%endif
    --with-http_sub_module \
    --with-http_dav_module \
    --with-http_flv_module \
    --with-http_mp4_module \
    --with-http_gunzip_module \
    --with-http_gzip_static_module \
    --with-http_random_index_module \
    --with-http_secure_link_module \
    --with-http_degradation_module \
    --with-http_stub_status_module \
    --with-http_perl_module \
    --with-http_slice_module \
    --with-mail=dynamic \
    --with-mail_ssl_module \
    --with-stream=dynamic \
    --with-stream_ssl_module \
    --with-threads \
    --with-pcre \
%if 0%{?with_gperftools}
    --with-google_perftools_module \
%endif
%if 0%{?with_pagespeed}
    --add-dynamic-module=./ngx_pagespeed-release-%{pagespeed_version}-beta \
%endif
    --with-debug \
    --with-cc-opt="%{optflags} $(pcre-config --cflags)" \
    --with-ld-opt="$RPM_LD_FLAGS -Wl,-E" # so the perl module finds its symbols

make %{?_smp_mflags}


%install
make install DESTDIR=%{buildroot} INSTALLDIRS=vendor

find %{buildroot} -type f -name .packlist -exec rm -f '{}' \;
find %{buildroot} -type f -name perllocal.pod -exec rm -f '{}' \;
find %{buildroot} -type f -empty -exec rm -f '{}' \;
find %{buildroot} -type f -iname '*.so' -exec chmod 0755 '{}' \;
%if 0%{?with_systemd}
install -p -D -m 0644 %{SOURCE10} \
    %{buildroot}%{_unitdir}/nginx.service
%else
install -p -D -m 0755 %{SOURCE15} \
    %{buildroot}%{_initrddir}/nginx
install -p -D -m 0644 %{SOURCE16} \
    %{buildroot}%{_sysconfdir}/sysconfig/nginx
%endif

install -p -D -m 0644 %{SOURCE11} \
    %{buildroot}%{_sysconfdir}/logrotate.d/nginx

install -p -d -m 0755 %{buildroot}%{nginx_confdir}/conf.d
install -p -d -m 0755 %{buildroot}%{nginx_confdir}/conf.modules.d
install -p -d -m 0700 %{buildroot}%{nginx_home}
install -p -d -m 0700 %{buildroot}%{nginx_home_tmp}
install -p -d -m 0700 %{buildroot}%{nginx_logdir}
install -p -d -m 0755 %{buildroot}%{nginx_webroot}

for mod in http_image_filter http_xslt_filter mail stream \
%if 0%{?with_geoip}
    http_geoip \
%endif
%if 0%{?with_pagespeed}
    pagespeed \
%endif
    ; do
    if [ "$mod" = "pagespeed" ]; then
        soname="ngx_${mod}"
    else
        soname="ngx_${mod}_module"
    fi
    cat > %{buildroot}%{nginx_confdir}/conf.modules.d/20-${soname}.conf <<EOF
load_module "%{nginx_moduledir}/${soname}.so";
EOF

    cat > files.${mod} <<EOF
%attr(755,root,root) %{nginx_moduledir}/${soname}.so
%config(noreplace) %attr(644,root,root) %{nginx_confdir}/conf.modules.d/20-${soname}.conf
EOF
done

install -p -m 0644 %{SOURCE12} \
    %{buildroot}%{nginx_confdir}
%if 0%{!?with_systemd:1}
sed -e 's:/run/nginx.pid:%{_localstatedir}/run/nginx.pid:' \
    -i %{buildroot}%{nginx_confdir}/nginx.conf
%endif

install -p -m 0644 %{SOURCE100} \
    %{buildroot}%{nginx_webroot}
install -p -m 0644 %{SOURCE101} %{SOURCE102} \
    %{buildroot}%{nginx_webroot}
install -p -m 0644 %{SOURCE103} %{SOURCE104} \
    %{buildroot}%{nginx_webroot}

install -p -D -m 0644 %{_builddir}/nginx-%{version}/man/nginx.8 \
    %{buildroot}%{_mandir}/man8/nginx.8

%if 0%{?with_systemd}
install -p -D -m 0755 %{SOURCE13} %{buildroot}%{_bindir}/nginx-upgrade
install -p -D -m 0644 %{SOURCE14} %{buildroot}%{_mandir}/man8/nginx-upgrade.8
%endif


%pre
getent group %{nginx_group} > /dev/null || groupadd -r %{nginx_group}
getent passwd %{nginx_user} > /dev/null || \
    useradd -r -d %{nginx_home} -g %{nginx_group} \
    -s /sbin/nologin -c "Nginx web server" %{nginx_user}
exit 0

%post
%if 0%{?with_systemd}
%systemd_post nginx.service
%else
if [ $1 -eq 1 ]; then
    /sbin/chkconfig --add %{packagename}
fi
%endif
if [ $1 -eq 2 ]; then
    # Make sure these directories are not world readable.
    chmod 700 %{nginx_home}
    chmod 700 %{nginx_home_tmp}
    chmod 700 %{nginx_logdir}
fi

%preun
%if 0%{?with_systemd}
%systemd_preun nginx.service
%else
if [ $1 -eq 0 ]; then
    /sbin/service %{packagename} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{packagename}
fi
%endif

%postun
%if 0%{?with_systemd}
%systemd_postun nginx.service
%else
if [ $1 -eq 2 ]; then
    /sbin/service %{packagename} upgrade || :
fi
%endif

%files
%doc LICENSE CHANGES README
%{nginx_datadir}/
%if 0%{?with_systemd}
%{_bindir}/nginx-upgrade
%endif
%{_sbindir}/nginx
%{_mandir}/man3/nginx.3pm*
%{_mandir}/man8/nginx.8*
%if 0%{?with_systemd}
%{_mandir}/man8/nginx-upgrade.8*
%{_unitdir}/nginx.service
%else
%{_initrddir}/nginx
%config(noreplace) %{_sysconfdir}/sysconfig/nginx
%endif
%dir %{nginx_confdir}
%dir %{nginx_confdir}/conf.d
%config(noreplace) %{nginx_confdir}/fastcgi.conf
%config(noreplace) %{nginx_confdir}/fastcgi.conf.default
%config(noreplace) %{nginx_confdir}/fastcgi_params
%config(noreplace) %{nginx_confdir}/fastcgi_params.default
%config(noreplace) %{nginx_confdir}/koi-utf
%config(noreplace) %{nginx_confdir}/koi-win
%config(noreplace) %{nginx_confdir}/mime.types
%config(noreplace) %{nginx_confdir}/mime.types.default
%config(noreplace) %{nginx_confdir}/nginx.conf
%config(noreplace) %{nginx_confdir}/nginx.conf.default
%config(noreplace) %{nginx_confdir}/scgi_params
%config(noreplace) %{nginx_confdir}/scgi_params.default
%config(noreplace) %{nginx_confdir}/uwsgi_params
%config(noreplace) %{nginx_confdir}/uwsgi_params.default
%config(noreplace) %{nginx_confdir}/win-utf
%config(noreplace) %{_sysconfdir}/logrotate.d/nginx
%dir %{perl_vendorarch}/auto/nginx
%{perl_vendorarch}/nginx.pm
%{perl_vendorarch}/auto/nginx/nginx.so
%attr(700,%{nginx_user},%{nginx_group}) %dir %{nginx_home}
%attr(700,%{nginx_user},%{nginx_group}) %dir %{nginx_home_tmp}
%attr(700,%{nginx_user},%{nginx_group}) %dir %{nginx_logdir}

%if 0%{?with_geoip}
%files http_geoip -f files.http_geoip
%endif
%files http_image_filter -f files.http_image_filter
%files http_xslt -f files.http_xslt_filter
%files mail -f files.mail
%files stream -f files.stream
%if 0%{?with_pagespeed}
%files ext-pagespeed -f files.pagespeed
%endif

%changelog
* Sat Mar 19 2016 Andy Thompson <andy@webtatic.com> - 1.9.12-0.1
- Fork nginx18 package
- Replace spdy with http2 module
- Update to 1.9.12
