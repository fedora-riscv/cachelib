# Tests currently fail with
# /builddir/build/BUILD/CacheLib-e3703aade03d359d290936b334ab81ca4a856b41/cachelib/compact_cache/tests/CCacheTests.cpp:159:1:   required from here
# /builddir/build/BUILD/CacheLib-e3703aade03d359d290936b334ab81ca4a856b41/cachelib/../cachelib/compact_cache/CCacheFixedLruBucket.h:277:11: internal compiler error: Floating point exception
# 277 |     memcpy(destPtr, srcPtr, sizeof(T));
#     |     ~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~~
%bcond_with tests

%global forgeurl https://github.com/facebook/CacheLib
%global commit c4904ef2524f396eb432392f8308a69dda926bd8
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global date 20211220
%forgemeta

# see cachelib/allocator/CacheVersion.h's kCachelibVersion
%global major_ver 16


Name:           cachelib
Version:        %{major_ver}
# using -s seems to add the snapinfo twice in the generated filename
# https://pagure.io/fedora-infra/rpmautospec/issue/240
Release:        %autorelease -e %{date}git%{shortcommit}
Summary:        Pluggable caching engine for scale high performance cache services

License:        ASL 2.0
URL:            %forgeurl
Source0:        %forgesource
# move TestUtils from cachelib_common to common_test_support to avoid ld issues
Patch0:         %{name}-ld_gtest.patch
# need to install cachelib_cachebench when building shared libs
Patch1:         %{name}-install_cachebench_so.patch
# and version them
Patch2:         %{name}-versioned_so.patch

# Folly is known not to work on big-endian CPUs
# https://bugzilla.redhat.com/show_bug.cgi?id=1892151
ExcludeArch:    s390x
# does not compile cleanly on 32-bit arches
# https://bugzilla.redhat.com/show_bug.cgi?id=2036124
%if 0%{?el8}
ExcludeArch:    %{arm}
%else
ExcludeArch:    %{arm32}
%endif
ExcludeArch:    %{ix86}
# build failure on aarch64
# https://bugzilla.redhat.com/show_bug.cgi?id=2036121
ExcludeArch:    %{arm64}

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  fbthrift-devel
BuildRequires:  fizz-devel
BuildRequires:  folly-devel
%if %{with tests}
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
%forgeautosetup -p1


%build
pushd %{name}
%cmake \
%if %{with tests}
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


%if %{with tests}
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
