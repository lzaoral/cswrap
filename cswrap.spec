%define csexec_archs aarch64 ppc64le s390x x86_64

Name:       cswrap
Version:    2.2.0
Release:    1%{?dist}
Summary:    Generic compiler wrapper

License:    GPLv3+
URL:        https://github.com/csutils/%{name}
Source0:    https://github.com/csutils/%{name}/releases/download/%{name}-%{version}/%{name}-%{version}.tar.gz

BuildRequires: asciidoc
BuildRequires: cmake3
BuildRequires: gcc

# csmock copies the resulting cswrap binary into mock chroot, which may contain
# an older (e.g. RHEL-7) version of glibc, and it would not dynamically link
# against the old version of glibc if it was built against a newer one.
# Therefore, we link glibc statically.
BuildRequires: glibc-static

# The test-suite runs automatically trough valgrind if valgrind is available
# on the system.  By not installing valgrind into mock's chroot, we disable
# this feature for production builds on architectures where valgrind is known
# to be less reliable, in order to avoid unnecessary build failures (see RHBZ
# #810992, #816175, and #886891).  Nevertheless developers are free to install
# valgrind manually to improve test coverage on any architecture.
%ifarch %{ix86} x86_64
BuildRequires: valgrind
%endif

%description
Generic compiler wrapper used by csmock to capture diagnostic messages.

# csexec is available on architectures defined in %%{csexec_archs} only
%ifarch %{csexec_archs}
%package -n csexec
Summary: Dynamic linker wrapper
Conflicts: csexec < %{version}-%{release}

%description -n csexec
This package contains csexec - a dynamic linker wrapper.  The wrapper can
be used to run dynamic analyzers and formal verifiers on source RPM package
fully automatically.
%endif

%prep
%setup -q

%build
mkdir cswrap_build
cd cswrap_build
%cmake3 -S.. .. -B. \
    -DPATH_TO_WRAP=\"%{_libdir}/cswrap\" \
    -DSTATIC_LINKING=ON
make %{?_smp_mflags} VERBOSE=yes

%check
cd cswrap_build
ctest3 %{?_smp_mflags} --output-on-failure

%install
cd cswrap_build
make install DESTDIR="$RPM_BUILD_ROOT"

install -m0755 -d "$RPM_BUILD_ROOT%{_libdir}"{,/cswrap}
for i in c++ cc g++ gcc clang clang++ cppcheck smatch \
    divc++ divcc diosc++ dioscc gclang++ gclang goto-gcc \
    %{_arch}-redhat-linux-c++ \
    %{_arch}-redhat-linux-g++ \
    %{_arch}-redhat-linux-gcc
do
    ln -s ../../bin/cswrap "$RPM_BUILD_ROOT%{_libdir}/cswrap/$i"
done

%files
%{_bindir}/cswrap
%{_libdir}/cswrap
%{_mandir}/man1/%{name}.1*
%doc COPYING README

%ifarch %{csexec_archs}
%files -n csexec
%{_bindir}/csexec
%{_bindir}/csexec-loader
%{_libdir}/libcsexec-preload.so
%{_mandir}/man1/csexec.1*
%doc COPYING
%endif
