%if 0%{?fedora} >= 36
# Folly is compiled with Clang
%bcond_without toolchain_clang
%else
%bcond_with toolchain_clang
%endif

%if %{with toolchain_clang}
%global toolchain clang
%bcond_without build_tests
%else
# failure when compiled with GCC 11:
# /builddir/build/BUILD/CacheLib-bd22b0eb79f7e2326f77a22c278c48e454882291/cachelib/compact_cache/tests/CCacheTests.cpp:114:1:   required from here
# /builddir/build/BUILD/CacheLib-bd22b0eb79f7e2326f77a22c278c48e454882291/cachelib/../cachelib/compact_cache/CCacheFixedLruBucket.h:277:11: internal compiler error: Floating point exception
#   277 |     memcpy(destPtr, srcPtr, sizeof(T));
#       |     ~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~~
%bcond_with build_tests
%endif

# tests not discoverable by ctest yet
%bcond_with check

%global forgeurl https://github.com/facebook/CacheLib
%global commit bd22b0eb79f7e2326f77a22c278c48e454882291
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global date 20220314
# disable forge macro snapinfo generation
# https://pagure.io/fedora-infra/rpmautospec/issue/240
%global distprefix %{nil}
%forgemeta

# see cachelib/allocator/CacheVersion.h's kCachelibVersion
%global major_ver 16

Name:           cachelib
Version:        %{major_ver}^%{date}git%{shortcommit}
Release:        %autorelease
Summary:        Pluggable caching engine for scale high performance cache services

License:        ASL 2.0
URL:            %forgeurl
Source0:        %forgesource
Patch0:         %{name}-fix_test_linking.patch
# needed on EL8; its gtest does not come with cmake files
Patch100:       %{name}-find-gtest.patch

# Folly is known not to work on big-endian CPUs
# https://bugzilla.redhat.com/show_bug.cgi?id=1892151
ExcludeArch:    s390x
%if 0%{?fedora} >= 36
# fmt code breaks: https://bugzilla.redhat.com/show_bug.cgi?id=2061022
ExcludeArch:    ppc64le
%endif
# does not compile cleanly on 32-bit arches
# https://bugzilla.redhat.com/show_bug.cgi?id=2036124
%if 0%{?el8}
ExcludeArch:    %{arm}
%else
ExcludeArch:    %{arm32}
%endif
ExcludeArch:    %{ix86}

BuildRequires:  cmake
%if %{with toolchain_clang}
BuildRequires:  clang
%else
BuildRequires:  gcc-c++
%endif
BuildRequires:  fbthrift-devel
BuildRequires:  fizz-devel
BuildRequires:  folly-devel
%if %{with build_tests}
BuildRequires:  gmock-devel
%endif
# this is actually needed, because of
# cachelib/navy/admission_policy/DynamicRandomAP.h
BuildRequires:  gtest-devel
BuildRequires:  libdwarf-devel
BuildRequires:  libzstd-devel
BuildRequires:  wangle-devel
BuildRequires:  zlib-devel
BuildRequires:  tsl-sparse-map-devel
# BuildRequires:  libatomic


%global _description %{expand:
CacheLib is a C++ library providing in-process high performance caching
mechanism. CacheLib provides a thread safe API to build high throughput, low
overhead caching services, with built-in ability to leverage DRAM and SSD
caching transparently.}

%description %{_description}

%package devel
Summary:        %{summary}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       cmake

%description devel %{_description}

The %{name}-devel package contains libraries and header files for developing
applications that use %{name}.


%prep
%forgesetup
%patch0 -p1
%if 0%{?el8}
%patch100 -p1
%endif


%build
pushd %{name}
%cmake \
%if %{with build_tests}
  -DBUILD_TESTS:BOOL=ON \
%else
  -DBUILD_TESTS:BOOL=OFF \
%endif
  -DCMAKE_BUILD_WITH_INSTALL_RPATH:BOOL=FALSE \
  -DCMAKE_INSTALL_DIR:PATH=%{_libdir}/cmake/%{name} \
  -DCONFIGS_INSTALL_DIR:STRING=%{_datadir}/%{name}/test_configs \
  -DINCLUDE_INSTALL_DIR:PATH=%{_includedir}/%{name} \
  -DCACHELIB_MAJOR_VERSION:STRING=%{major_ver} \
  -DPACKAGE_VERSION:STRING=%{major_ver}.%{date}
%cmake_build


%install
pushd %{name}
%cmake_install
%if %{with build_tests}
# TODO: prevent tests being installed
rm -rf %{buildroot}%{_prefix}/tests
%endif


%if %{with check}
%check
pushd %{name}
%ctest
%endif


%files
%license LICENSE
%doc BENCHMARKS.md CHANGELOG.md README.md examples
%{_bindir}/cachebench
%{_datadir}/%{name}
%{_libdir}/*.so.*

%files devel
%{_includedir}/%{name}
%{_libdir}/*.so
%{_libdir}/cmake/%{name}


%changelog
%autochangelog
