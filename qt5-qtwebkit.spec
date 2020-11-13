%undefine _annotated_build

%global qt_module qtwebkit

%global _hardened_build 1

%global prerel alpha4
%global prerel_tag -%{prerel}

## NOTE: Lots of files in various subdirectories have the same name (such as
## "LICENSE") so this short macro allows us to distinguish them by using their
## directory names (from the source tree) as prefixes for the files.
%global add_to_license_files() \
        mkdir -p _license_files ; \
        cp -p %1 _license_files/$(echo '%1' | sed -e 's!/!.!g')

Name:           qt5-%{qt_module}
Version:        5.212.0
Release:        4
Summary:        Qt5 - QtWebKit components

License:        LGPLv2 and BSD
URL:            https://github.com/qtwebkit/qtwebkit
Source0:        https://github.com/qtwebkit/qtwebkit/releases/download/%{qt_module}-%{version}%{?prerel_tag}/%{qt_module}-%{version}%{?prerel_tag}.tar.xz

# Patch for new CMake policy CMP0071 to explicitly use old behaviour.
Patch2:         qtwebkit-5.212.0_cmake_cmp0071.patch
Patch3:         fix_build_with_bison.patch

BuildRequires:  bison
BuildRequires:  cmake
BuildRequires:  flex
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(libwoff2dec)
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  gperf
BuildRequires:  pkgconfig(gstreamer-1.0)
BuildRequires:  pkgconfig(gstreamer-app-1.0)
BuildRequires:  hyphen-devel
BuildRequires:  pkgconfig(icu-i18n) pkgconfig(icu-uc)
BuildRequires:  libjpeg-devel
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(xcomposite)
BuildRequires:  pkgconfig(xrender)
BuildRequires:  pkgconfig(libxslt)
BuildRequires:  pkgconfig(gl)
BuildRequires:  pkgconfig(gstreamer-gl-1.0)
BuildRequires:  pkgconfig(gstreamer-mpegts-1.0)
BuildRequires:  perl-generators
BuildRequires:  perl(File::Copy)
BuildRequires:  python3
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qtdeclarative-devel
%if ! 0%{?bootstrap}
BuildRequires:  qt5-qtlocation-devel
BuildRequires:  qt5-qtsensors-devel
BuildRequires:  qt5-qtwebchannel-devel
%endif
BuildRequires:  pkgconfig(ruby)
BuildRequires:  rubygems
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  pkgconfig(zlib)
# workaround bad embedded png files, https://bugzilla.redhat.com/1639422
BuildRequires:  findutils
BuildRequires:  pngcrush

BuildRequires:  qt5-qtbase-private-devel
%{?_qt5:Requires: %{_qt5}%{?_isa} = %{_qt5_version}}
BuildRequires:  qt5-qtdeclarative-private-devel
%{?_qt5:Requires: qt5-qtdeclarative%{?_isa} = %{_qt5_version}}


# filter qml provides
%global __provides_exclude_from ^%{_qt5_archdatadir}/qml/.*\\.so$

# We're supposed to specify versions here, but these crap Google libs don't do
# normal releases. Accordingly, they're not suitable to be system libs.
Provides:       bundled(angle)
Provides:       bundled(brotli)
Provides:       bundled(woff2)

%description
%{summary}

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       qt5-qtbase-devel%{?_isa}
Requires:       qt5-qtdeclarative-devel%{?_isa}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%if 0%{?docs}
%package doc
Summary: API documentation for %{name}
BuildRequires: qt5-qdoc
BuildRequires: qt5-qhelpgenerator
BuildArch: noarch

%description doc
%{summary}.
%endif


%prep
%autosetup -p1 -n %{qt_module}-%{version}%{?prerel_tag}

# find/fix pngs with "libpng warning: iCCP: known incorrect sRGB profile"
find -name \*.png | xargs -n1 pngcrush -ow -fix

# ppc64le failed once with
# make[2]: *** No rule to make target 'Source/WebCore/Resources/textAreaResizeCorner.png', needed by 'Source/WebKit/qrc_WebCore.cpp'.  Stop.
test -f Source/WebCore/Resources/textAreaResizeCorner.png


%build
# The following changes of optflags ietc. are adapted from webkitgtk4 package, which
# is mostly similar to this one...
#
# Increase the DIE limit so our debuginfo packages could be size optimized.
# Decreases the size for x86_64 from ~5G to ~1.1G.
# https://bugzilla.redhat.com/show_bug.cgi?id=1456261
%global _dwz_max_die_limit 250000000

# Decrease debuginfo even on ix86 because of:
# https://bugs.webkit.org/show_bug.cgi?id=140176
%ifarch s390 s390x %{arm} %{ix86} ppc %{power64} %{mips}
# Decrease debuginfo verbosity to reduce memory consumption even more
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')
%endif

%ifarch ppc
# Use linker flag -relax to get WebKit build under ppc(32) with JIT disabled
%global optflags %{optflags} -Wl,-relax
%endif

CFLAGS="${CFLAGS:-%optflags}" ; export CFLAGS ;
CXXFLAGS="${CXXFLAGS:-%optflags} -fpermissive" ; export CXXFLAGS ;
%{?__global_ldflags:LDFLAGS="${LDFLAGS:-%__global_ldflags}" ; export LDFLAGS ;}
# We cannot use default cmake macro here as it overwrites some settings queried
# by qtwebkit cmake from qmake
cmake . \
       -DPORT=Qt \
       -DCMAKE_BUILD_TYPE=Release \
       -DENABLE_TOOLS=OFF \
       -DCMAKE_C_FLAGS_RELEASE:STRING="-DNDEBUG" \
       -DCMAKE_CXX_FLAGS_RELEASE:STRING="-DNDEBUG" \
       -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON \
%ifarch s390 s390x ppc %{power64}
       -DENABLE_JIT=OFF \
%endif
%ifarch s390 s390x ppc %{power64}
       -DUSE_SYSTEM_MALLOC=ON \
%endif
       %{?docs:-DGENERATE_DOCUMENTATION=ON} \
       -DPYTHON_EXECUTABLE:PATH="%{__python3}"

%make_build

%if 0%{?docs}
%make_build docs
%endif


%install
%make_install

find %{buildroot} -name '*.la' -exec rm -f {} ';'

# fix pkgconfig files
#sed -i '/Name/a Description: Qt5 WebKit module' %{buildroot}%{_libdir}/pkgconfig/Qt5WebKit.pc
#sed -i "s,Cflags: -I%{_qt5_libdir}/qt5/../../include/qt5/Qt5WebKit,Cflags: -I%{_qt5_headerdir}/QtWebKit,g" %{buildroot}%{_libdir}/pkgconfig/Qt5WebKit.pc
# strictly speaking, this isn't *wrong*, but can made more readable, so let's do that
sed -i "s,Libs: -L%{_qt5_libdir}/qt5/../ -lQt5WebKit,Libs: -L%{_qt5_libdir} -lQt5WebKit ,g" %{buildroot}%{_libdir}/pkgconfig/Qt5WebKit.pc

#sed -i '/Name/a Description: Qt5 WebKitWidgets module' %{buildroot}%{_libdir}/pkgconfig/Qt5WebKitWidgets.pc
#sed -i "s,Cflags: -I%{_qt5_libdir}/qt5/../../include/qt5/Qt5WebKitWidgets,Cflags: -I%{_qt5_headerdir}/QtWebKitWidgets,g" %{buildroot}%{_libdir}/pkgconfig/Qt5WebKitWidgets.pc
sed -i "s,Libs: -L%{_qt5_libdir}/qt5/../ -lQt5WebKitWidgets,Libs: -L%{_qt5_libdir} -lQt5WebKitWidgets ,g" %{buildroot}%{_libdir}/pkgconfig/Qt5WebKitWidgets.pc

# Finally, copy over and rename various files for %%license inclusion
%add_to_license_files Source/JavaScriptCore/COPYING.LIB
%add_to_license_files Source/JavaScriptCore/icu/LICENSE
%add_to_license_files Source/ThirdParty/ANGLE/LICENSE
%add_to_license_files Source/ThirdParty/ANGLE/src/third_party/compiler/LICENSE
%add_to_license_files Source/ThirdParty/ANGLE/src/third_party/murmurhash/LICENSE
%add_to_license_files Source/WebCore/icu/LICENSE
%add_to_license_files Source/WebCore/LICENSE-APPLE
%add_to_license_files Source/WebCore/LICENSE-LGPL-2
%add_to_license_files Source/WebCore/LICENSE-LGPL-2.1
%add_to_license_files Source/WebInspectorUI/UserInterface/External/CodeMirror/LICENSE
%add_to_license_files Source/WebInspectorUI/UserInterface/External/Esprima/LICENSE
%add_to_license_files Source/WTF/icu/LICENSE
%add_to_license_files Source/WTF/wtf/dtoa/COPYING
%add_to_license_files Source/WTF/wtf/dtoa/LICENSE


%check
# verify Qt5WebKit cflags non-use of -I/.../Qt5WebKit
export PKG_CONFIG_PATH=%{buildroot}%{_libdir}/pkgconfig
test -z "$(pkg-config --cflags Qt5WebKit | grep Qt5WebKit)"


%ldconfig_scriptlets

%files
%license LICENSE.LGPLv21 _license_files/*
%{_qt5_libdir}/libQt5WebKit.so.5*
%{_qt5_libdir}/libQt5WebKitWidgets.so.5*
%{_qt5_libexecdir}/QtWebNetworkProcess
%{_qt5_libexecdir}/QtWebPluginProcess
%{_qt5_libexecdir}/QtWebProcess
%{_qt5_libexecdir}/QtWebStorageProcess
%{_qt5_archdatadir}/qml/QtWebKit/

%files devel
%{_qt5_headerdir}/Qt*/
%{_qt5_libdir}/libQt5*.so
%{_qt5_libdir}/cmake/Qt5*/
%{_qt5_libdir}/pkgconfig/Qt5*.pc
%{_qt5_archdatadir}/mkspecs/modules/*.pri


%if 0%{?docs}
%files doc
%{_qt5_docdir}/qtwebkit.qch
%{_qt5_docdir}/qtwebkit/
%endif


%changelog
* Thu Nov 12 2020 wutao <wutao61@huawei.com> - 5.212.0-4
- update to alpha4 and drop python2 module

* Mon Aug 03 2020 lingsheng <lingsheng@huawei.com> - 5.212.0-3
- Fix build with icu 65.1

* Tue Mar 17 2020 Ling Yang <lingyang2@huawei.com> - 5.212.0-2
- Fixed building error

* Fri Feb 14 2020 Ling Yang <lingyang2@huawei.com> - 5.212.0-1
- Package init
