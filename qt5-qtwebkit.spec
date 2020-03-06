Name:           qt5-qtwebkit
Version:        5.212.0
Release:        1
Summary:        QtWebKit components
License:        LGPLv2 and BSD
URL:            https://github.com/annulen/webkit
Source0:        https://github.com/qtwebkit/qtwebkit/releases/download/qtwebkit-5.212.0-alpha2/qtwebkit-%{version}-alpha2.tar.xz

Patch0000:      qt5-qtwebkit-5.212.0-alpha2-fix-pagewidth.patch
Patch0001:      qtwebkit-5.212.0-alpha2-fix-null-pointer-dereference.patch
Patch0002:      qtwebkit-5.212.0_cmake_cmp0071.patch
Patch0003:      qtwebkit-5.212.0_fix_missing_sources.patch
Patch0004:      0016-cmake-Import-ECMEnableSanitizers.patch
Patch0005:      0031-Disable-ES6-Proxy-object.patch
Patch0006:      0111-ECM-Update-ECMGeneratePkgConfigFile-to-latest-versio.patch
Patch0007:      0012-cmake-Fix-include-dir-in-the-generated-pkg-config-fi.patch

BuildRequires:  bison cmake flex pkgconfig(fontconfig) pkgconfig(gio-2.0) pkgconfig(glib-2.0)
BuildRequires:  gperf pkgconfig(gstreamer-1.0) pkgconfig(gstreamer-app-1.0) hyphen-devel
BuildRequires:  pkgconfig(icu-i18n) pkgconfig(icu-uc) libjpeg-devel pkgconfig(libpng)
BuildRequires:  pkgconfig(libwebp) pkgconfig(xcomposite) pkgconfig(xrender) pkgconfig(libxslt)
BuildRequires:  pkgconfig(gl) pkgconfig(gstreamer-gl-1.0) pkgconfig(gstreamer-mpegts-1.0)
BuildRequires:  perl-generators python2 qt5-qtbase-devel pkgconfig(Qt5Quick)
BuildRequires:  pkgconfig(Qt5Location) pkgconfig(Qt5Sensors) pkgconfig(Qt5WebChannel)
BuildRequires:  pkgconfig(ruby) rubygems pkgconfig(sqlite3) pkgconfig(zlib)
BuildRequires:  qt5-qtbase-private-devel qt5-qtdeclarative-private-devel
%{?_qt5:Requires: %{_qt5} = %{_qt5_version}}
%{?_qt5:Requires: qt5-qtdeclarative = %{_qt5_version}}
%global __provides_exclude_from ^%{_qt5_archdatadir}/qml/.*\\.so$
Provides:       bundled(angle) bundled(brotli) bundled(woff2)

%description
WebKit is an open source web browser engine.
WebKit's HTML and JavaScript code began as a branch of the KHTML and KJS libraries from KDE.
As part of KDE framework KHTML was based on Qt
but during their porting efforts Apple's engineers made WebKit toolkit independent.
QtWebKit is a project aiming at porting this fabulous engine back to Qt.

%package        devel
Summary:        Development files for qt5-qtwebkit
Requires:       qt5-qtwebkit = %{version}-%{release} qt5-qtbase-devel qt5-qtdeclarative-devel

%description    devel
Development files for qt5-qtwebkit.

%package        help
Summary:        API documentation for qt5-qtwebkit
BuildRequires:  qt5-qdoc qt5-qhelpgenerator
BuildArch:      noarch
Provides:       qt5-qtwebkit-doc = %{version}-%{release}
Obsoletes:      qt5-qtwebkit-doc < %{version}-%{release}

%description    help
API documentation for qt5-qtwebkit.

%prep
%autosetup -p1 -n qtwebkit-%{version}-alpha2

%build
export CFLAGS="${CFLAGS:-%optflags}"
export CXXFLAGS="${CXXFLAGS:-%optflags} -fpermissive"
export QT_VERSION_TAG=52120
export QT_VER=5.212.0
export QT_VERSION=5.212.0
export QT_INSTALL_DOCS=/usr/share/doc/qt5
export BUILDDIR=./
%{?__global_ldflags:export LDFLAGS="${LDFLAGS:-%__global_ldflags}"}
cmake -DPORT=Qt -DCMAKE_BUILD_TYPE=Release -DENABLE_TOOLS=OFF \
       -DCMAKE_C_FLAGS_RELEASE:STRING="-DNDEBUG" -DCMAKE_CXX_FLAGS_RELEASE:STRING="-DNDEBUG" \
       -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON \
       -DGENERATE_DOCUMENTATION=ON \
       .

%make_build
%make_build docs

%install
export QT_VERSION_TAG=52120
export QT_VER=5.212.0
export QT_VERSION=5.212.0
export QT_INSTALL_DOCS=/usr/share/doc/qt5
export BUILDDIR=./
%make_install
%delete_la

sed -i "s,Libs: -L%{_qt5_libdir}/qt5/../ -lQt5WebKit,Libs: -L%{_qt5_libdir} -lQt5WebKit ,g" %{buildroot}%{_libdir}/pkgconfig/Qt5WebKit.pc
sed -i "s,Libs: -L%{_qt5_libdir}/qt5/../ -lQt5WebKitWidgets,Libs: -L%{_qt5_libdir} -lQt5WebKitWidgets ,g" %{buildroot}%{_libdir}/pkgconfig/Qt5WebKitWidgets.pc

mkdir -p _license_files
cp -p Source/JavaScriptCore/COPYING.LIB _license_files/Source.JavaScriptCore.COPYING.LIB
cp -p Source/JavaScriptCore/icu/LICENSE _license_files/Source.JavaScriptCore.icu.LICENSE
cp -p Source/ThirdParty/ANGLE/LICENSE _license_files/Source.ThirdParty.ANGLE.LICENSE
cp -p Source/ThirdParty/ANGLE/src/third_party/compiler/LICENSE _license_files/Source.ThirdParty.ANGLE.src.third_party.compiler.LICENSE
cp -p Source/ThirdParty/ANGLE/src/third_party/murmurhash/LICENSE _license_files/Source.ThirdParty.ANGLE.src.third_party.murmurhash.LICENSE
cp -p Source/WebCore/icu/LICENSE _license_files/Source.WebCore.icu.LICENSE
cp -p Source/WebCore/LICENSE-APPLE _license_files/Source.WebCore.LICENSE-APPLE
cp -p Source/WebCore/LICENSE-LGPL-2 _license_files/Source.WebCore.LICENSE-LGPL-2
cp -p Source/WebCore/LICENSE-LGPL-2.1 _license_files/Source.WebCore.LICENSE-LGPL-2.1
cp -p Source/WebInspectorUI/UserInterface/External/CodeMirror/LICENSE _license_files/Source.WebInspectorUI.UserInterface.External.CodeMirror.LICENSE
cp -p Source/WebInspectorUI/UserInterface/External/Esprima/LICENSE _license_files/Source.WebInspectorUI.UserInterface.External.Esprima.LICENSE
cp -p Source/WTF/icu/LICENSE _license_files/Source.WTF.icu.LICENSE
cp -p Source/WTF/wtf/dtoa/COPYING _license_files/Source.WTF.wtf.dtoa.COPYING
cp -p Source/WTF/wtf/dtoa/LICENSE _license_files/Source.WTF.wtf.dtoa.LICENSE

%check
export PKG_CONFIG_PATH=%{buildroot}%{_libdir}/pkgconfig
test -z "$(pkg-config --cflags Qt5WebKit | grep Qt5WebKit)"

%post
/sbin/ldconfig
%postun
/sbin/ldconfig

%files
%license LICENSE.LGPLv21 _license_files/*
%{_qt5_libdir}/*.so.5*
%{_qt5_libexecdir}/*
%{_qt5_archdatadir}/qml/QtWebKit/

%files devel
%{_qt5_headerdir}/Qt*/
%{_qt5_libdir}/libQt5*.so
%{_qt5_libdir}/cmake/Qt5*/
%{_qt5_libdir}/pkgconfig/Qt5*.pc
%{_qt5_archdatadir}/mkspecs/modules/*.pri

%files help
%{_qt5_docdir}/qtwebkit.qch
%{_qt5_docdir}/qtwebkit/

%changelog
* Fri Feb 14 2020 Ling Yang <lingyang2@huawei.com> - 5.212.0-1
- Package init
