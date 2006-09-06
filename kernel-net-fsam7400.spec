#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	smp		# don't build SMP module
%bcond_with	verbose		# verbose build (V=1)
#
%define		modname	fsam7400
%define		_rel	1
Summary:	Linux kernel module for Wireless switch on Fujitsu-Siemens Amilo Pro2000
Name:		kernel%{_alt_kernel}-net-%{modname}
Version:	0.4.1
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://linux.zwobbl.de/pub/fsam7400-0.4.1.tgz
# Source0-md5:	3cf280c8a7e843deae9509386c0e7e7b
URL:		http://wiki.archlinux.org/index.php/Fujitsu-Siemens_Amilo_Pro2000#WIRELESS_LAN
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.14}
BuildRequires:	rpmbuild(macros) >= 1.308
BuildRequires:	sed >= 4.0
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
Requires:	module-init-tools >= 3.2.2-2
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description -n kernel%{_alt_kernel}-net-%{modname}
Linux kernel module to change wireless radio status on Fujitsu-Siemens
Fujitsu-Siemens Amilo Pro2000 laptop.

%package -n kernel%{_alt_kernel}-smp-net-%{modname}
Summary:	Linux SMP kernel module for Wireless switch on Fujitsu-Siemens Amilo Pro2000
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
Requires:	module-init-tools >= 3.2.2-2

%description -n kernel%{_alt_kernel}-smp-net-%{modname}
Linux SMP kernel module to change wireless radio status on
Fujitsu-Siemens Fujitsu-Siemens Amilo Pro2000 laptop.

%prep
%setup -q -n %{modname}-%{version}

%build
# kernel module(s)
rm -rf built
mkdir -p built/{nondist,smp,up}
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
%if %{with dist_kernel}
	%{__make} -j1 -C %{_kernelsrcdir} O=$PWD/o prepare scripts
%else
	install -d o/include/config
	touch o/include/config/MARKER
	ln -sf %{_kernelsrcdir}/scripts o/scripts
%endif
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	mv *.ko built/$cfg
done

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc \
	$RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/%{_kernel_ver}{,smp} \
	$RPM_BUILD_ROOT%{_kernelsrcdir}/include/net

cd built
install %{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}/fsam7400.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/fsam7400.ko

%if %{with smp} && %{with dist_kernel}
install smp/fsam7400.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc/fsam7400.ko
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-net-%{modname}
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-net-%{modname}
%depmod %{_kernel_ver}

%post	-n kernel%{_alt_kernel}-smp-net-%{modname}
%depmod %{_kernel_ver}smp

%postun	-n kernel%{_alt_kernel}-smp-net-%{modname}
%depmod %{_kernel_ver}smp

%files -n kernel%{_alt_kernel}-net-%{modname}
%defattr(644,root,root,755)
%doc README CHANGELOG INSTALL
/lib/modules/%{_kernel_ver}/misc/fsam7400*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-net-%{modname}
%defattr(644,root,root,755)
%doc README CHANGELOG INSTALL
/lib/modules/%{_kernel_ver}smp/misc/fsam7400*.ko*
%endif
