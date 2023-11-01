%global summary A set of libraries and tools for managing boot loader entries
%global sphinx_docs 1

Name:		boom-boot
Version:	1.3
Release:	2%{?dist}
Summary:	%{summary}

License:	GPLv2
URL:		https://github.com/snapshotmanager/boom
Source0:	https://github.com/snapshotmanager/boom/archive/%{version}/boom-%{version}.tar.gz
Patch0:		Disable-GRUB2-plugin-on-RHEL-8.patch
Patch1:		0001-etc-Remove-executable-permission-from-etc-default-bo.patch
Patch2:		0002-man-Fix-line-starting-with.patch
Patch3:		0003-report-fix-docstring-typo-objecct.patch
Patch4:		0004-command-fix-docstring-typo-or-OsError.patch
# BZ 1929838:
Patch5:		0005-command-fix-optional-BLS-key-to-command-line-argumen.patch

BuildArch:	noarch

BuildRequires:	python3-setuptools
BuildRequires:	python3-devel
%if 0%{?sphinx_docs}
BuildRequires:	python3-sphinx
%endif
BuildRequires: make

Requires: python3-boom = %{version}-%{release}
Requires: %{name}-conf = %{version}-%{release}

%package -n python3-boom
Summary: %{summary}
# Unsupported on RHEL-8 :-(
#%%{?python_provide:%%python_provide python%%{__python_pkgversion}-boom}
# Do we need this??? IMO not
#Provides: python3-boom = %%{version}-%%{release}
Requires: %{__python3}
Recommends: (lvm2 or brtfs-progs)
Recommends: %{name}-conf = %{version}-%{release}

# There used to be a boom package in fedora, and there is boom packaged in
# copr. How to tell which one is installed? We need python3-boom and no boom
# only.
Conflicts: boom

%package conf
Summary: %{summary}

%package grub2
Summary: %{summary}
Supplements: (grub2 and boom-boot = %{version}-%{release})

%description
Boom is a boot manager for Linux systems using boot loaders that support
the BootLoader Specification for boot entry configuration.

Boom requires a BLS compatible boot loader to function: either the
systemd-boot project, or Grub2 with the BLS patch (Red Hat Grub2 builds
include this support in both Red Hat Enterprise Linux 7 and Fedora).

%description -n python3-boom
Boom is a boot manager for Linux systems using boot loaders that support
the BootLoader Specification for boot entry configuration.

Boom requires a BLS compatible boot loader to function: either the
systemd-boot project, or Grub2 with the BLS patch (Red Hat Grub2 builds
include this support in both Red Hat Enterprise Linux 7 and Fedora).

This package provides python3 boom module.

%description conf
Boom is a boot manager for Linux systems using boot loaders that support
the BootLoader Specification for boot entry configuration.

Boom requires a BLS compatible boot loader to function: either the
systemd-boot project, or Grub2 with the BLS patch (Red Hat Grub2 builds
include this support in both Red Hat Enterprise Linux 7 and Fedora).

This package provides configuration files for boom.

%description grub2
Boom is a boot manager for Linux systems using boot loaders that support
the BootLoader Specification for boot entry configuration.

Boom requires a BLS compatible boot loader to function: either the
systemd-boot project, or Grub2 with the BLS patch (Red Hat Grub2 builds
include this support in both Red Hat Enterprise Linux 7 and Fedora).

This package provides integration scripts for grub2 bootloader.

%prep
%setup -n boom-%{version}
# NOTE: Do not use backup extension - MANIFEST.in is picking them
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

%build
%if 0%{?sphinx_docs}
make -C doc html
rm doc/_build/html/.buildinfo
mv doc/_build/html doc/html
rm -r doc/_build
%endif

%py3_build

%install
%py3_install

# Install Grub2 integration scripts
mkdir -p ${RPM_BUILD_ROOT}/etc/grub.d
mkdir -p ${RPM_BUILD_ROOT}/etc/default
install -m 755 etc/grub.d/42_boom ${RPM_BUILD_ROOT}/etc/grub.d
install -m 644 etc/default/boom ${RPM_BUILD_ROOT}/etc/default

# Make configuration directories
# mode 0700 - in line with /boot/grub2 directory:
install -d -m 700 ${RPM_BUILD_ROOT}/boot/boom/profiles
install -d -m 700 ${RPM_BUILD_ROOT}/boot/boom/hosts
install -d -m 700 ${RPM_BUILD_ROOT}/boot/loader/entries
install -d -m 700 ${RPM_BUILD_ROOT}/boot/boom/cache
install -m 644 examples/boom.conf ${RPM_BUILD_ROOT}/boot/boom
install -m 644 examples/profiles/*.profile ${RPM_BUILD_ROOT}/boot/boom/profiles

mkdir -p ${RPM_BUILD_ROOT}/%{_mandir}/man8
mkdir -p ${RPM_BUILD_ROOT}/%{_mandir}/man5
install -m 644 man/man8/boom.8 ${RPM_BUILD_ROOT}/%{_mandir}/man8
install -m 644 man/man5/boom.5 ${RPM_BUILD_ROOT}/%{_mandir}/man5

rm doc/Makefile
rm doc/conf.py

# Test suite currently does not operate in rpmbuild environment
#%%check
#%%{__python3} setup.py test

%files
%license COPYING
%doc README.md
%{_bindir}/boom
%doc %{_mandir}/man*/boom.*

%files -n python3-boom
%license COPYING
%doc README.md
%{python3_sitelib}/*
%doc doc
%doc examples
%doc tests

%files conf
%license COPYING
%doc README.md
%dir /boot/boom
%config(noreplace) /boot/boom/boom.conf
%dir /boot/boom/profiles
%config(noreplace) /boot/boom/profiles/*
%dir /boot/boom/hosts
%dir /boot/boom/cache
%dir /boot/loader/entries

%files grub2
%license COPYING
%doc README.md
%{_sysconfdir}/grub.d/42_boom
%config(noreplace) %{_sysconfdir}/default/boom


%changelog
* Tue Jun 15 2021 Marian Csontos <mcsontos@redhat.com> 1.3-2
- Fix --grub-id option handling.

* Sat Jan 30 2021 Marian Csontos <mcsontos@redhat.com> 1.3-1
- Check for duplicates consistently in the clone and edit commands.
- Apply correct command line precedence to --add-opts and --del-opts.
- Correctly merge multiple --add/del-opts when editing or cloning.
- Correctly propagate --add/del-opts in boom edit commands.
- Enhanced logging of --add/del-opts merge logic.
- The default Python interpreter is now /usr/bin/python.
- Fixed re-ordering of options modifications when read from disk.
- Do not set BootParams attributes for anonymous option words.
- Make lvm_root_lv validation checks more strict.
- Improve BootParams.from_entry() parameter recovery debug logging.
- Include sample OsProfile for Fedora 32.
- Re-set sandbox state in test suite to ensure run-to-run consistency.
- Improve compatibility with Red Hat BLS implementation.
- Allow non-boom managed entries to be listed and displayed.
- Handle quirks in Red Hat's use of the BLS machine_id key.
- Allow grub2 bootloader variables to be expanded when cloning entries.
- Simplify clone_entry logic and make consistent with edit_entry.
- Ensure stable ordering of legacy boot entry configuration.

* Mon Jun 29 2020 Marian Csontos <mcsontos@redhat.com> 1.2-2
- Fix RHEL-8 profiles.
- Fix --add/del-opt precedence.
- Fix backup image reference counting.

* Sun Jun 07 2020 Marian Csontos <mcsontos@redhat.com> 1.2-1
- Update to bug fix release 1.2.

* Tue May 26 2020 Marian Csontos <mcsontos@redhat.com> 1.1-2
- Fix unicode entries handling.
- Add tracebacks when --debug is used.

* Thu May 14 2020 Marian Csontos <mcsontos@redhat.com> 1.1-1
- Update to new upstream release 1.1.
- Add caching of kernel and init ramdisk images.

* Fri Nov 29 2019 Marian Csontos <mcsontos@redhat.com> 1.0-1
- Update to new upstream release 1.0.

* Mon Jun 10 2019 Marian Csontos <mcsontos@redhat.com> 1.0-0.2.20190610git246b116
- Fix packaging issues.

* Mon May 06 2019 Marian Csontos <mcsontos@redhat.com> 1.0-0.1.20190329git6ff3e08
- Test upstream packaging.

* Mon Jan 14 2019 Marian Csontos <mcsontos@redhat.com> 0.9-7
- Reduce log level of "Could not load BootEntry" messages.
- Raise more appropriate LookupError on unknown BLS keys.

* Tue Dec 18 2018 Marian Csontos <mcsontos@redhat.com> 0.9-6
- Disable GRUB2 plugin on RHEL-8.

* Mon Sep 17 2018 Tomas Orsava <torsava@redhat.com> - 0.9-5
- Require the Python interpreter directly instead of using the package name
- Related: rhbz#1619153

* Tue Jul 17 2018 Marian Csontos <mcsontos@redhat.com> 0.9-4
- Change dependencies.

* Mon Jul 16 2018 Marian Csontos <mcsontos@redhat.com> 0.9-3
- Split executable, python module and configuration.

* Wed Jun 27 2018 Marian Csontos <mcsontos@redhat.com> 0.9-2
- Spin off grub2 into subpackage

* Wed Jun 27 2018 Marian Csontos <mcsontos@redhat.com> 0.9-1
- Update to new upstream 0.9.
- Fix boot_id caching.

* Fri Jun 08 2018 Marian Csontos <mcsontos@redhat.com> 0.8.5-6.2
- Remove example files from /boot/boom/profiles.

* Fri May 11 2018 Marian Csontos <mcsontos@redhat.com> 0.8.5-6.1
- Files in /boot are treated as configuration files.

* Thu Apr 26 2018 Marian Csontos <mcsontos@redhat.com> 0.8.5-6
- Package upstream version 0.8-5.6

