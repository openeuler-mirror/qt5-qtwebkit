%undefine _annotated_build
%global _hardened_build         1
%global add_to_license_files()  mkdir -p _license_files ; cp -p %1 _license_files/$(echo '%1' | sed -e 's!/!.!g')
%global __provides_exclude_from ^%{_qt5_archdatadir}/qml/.*\\.so$

Name:           qt5-qtwebkit
Version:        5.212.0
Release:        4
Summary:        QtWebKit components of Qt5
License:        LGPLv2 and BSD
URL:            https://github.com/annulen/webkit
Source0:        https://github.com/annulen/webkit/releases/download/qtwebkit-%{version}-alpha2/qtwebkit-%{version}-alpha2.tar.xz

BuildRequires:  bison cmake flex pkgconfig(fontconfig) pkgconfig(gio-2.0) pkgconfig(glib-2.0) gperf
BuildRequires:  pkgconfig(gstreamer-1.0) pkgconfig(gstreamer-app-1.0) hyphen-devel pkgconfig(icu-i18n)
BuildRequires:  pkgconfig(icu-uc) libjpeg-devel pkgconfig(libpng) pkgconfig(libwebp) pkgconfig(xcomposite)
BuildRequires:  pkgconfig(xrender) pkgconfig(libxslt) pkgconfig(gl) pkgconfig(gstreamer-gl-1.0)
BuildRequires:  pkgconfig(gstreamer-mpegts-1.0) perl-generators python2 qt5-qtbase-devel findutils
BuildRequires:  qt5-qtdeclarative-devel pkgconfig(ruby) rubygems pkgconfig(sqlite3) pkgconfig(zlib)
BuildRequires:  qt5-qtbase-private-devel qt5-qtdeclarative-private-devel
%if ! 0%{?bootstrap}
BuildRequires:  qt5-qtlocation-devel qt5-qtsensors-devel qt5-qtwebchannel-devel
Provides:       bundled(angle) bundled(brotli) bundled(woff2)
%endif
%{?_qt5:Requires: %{_qt5} = %{_qt5_version}}
%{?_qt5:Requires: qt5-qtdeclarative = %{_qt5_version}}

# Upstream patch to fix pagewidth issue with trojita
# https://github.com/annulen/webkit/issues/511
# https://github.com/annulen/webkit/commit/6faf11215e1af27d35e921ae669aa0251a01a1ab
# https://github.com/annulen/webkit/commit/76420459a13d9440b41864c93cb4ebb404bdab55
Patch0000:      qt5-qtwebkit-5.212.0-alpha2-fix-pagewidth.patch
# Patch from Kevin Kofler to fix https://github.com/annulen/webkit/issues/573
Patch0001:      qtwebkit-5.212.0-alpha2-fix-null-pointer-dereference.patch
# Patch for new CMake policy CMP0071 to explicitly use old behaviour.
Patch0002:      qtwebkit-5.212.0_cmake_cmp0071.patch
# Patch to fix for missing source file.
Patch0003:      qtwebkit-5.212.0_fix_missing_sources.patch
## upstream patches (qtwebkit-5.212 branch)
Patch0004:      0016-cmake-Import-ECMEnableSanitizers.patch
# disable ES6 Proxy
Patch0005:      0031-Disable-ES6-Proxy-object.patch
# ECM Update ECMGeneratePkgConfigFile to latest versio
Patch0006:      0111-ECM-Update-ECMGeneratePkgConfigFile-to-latest-versio.patch
## upstream patches (qtwebkit-stable branch)
Patch0007:      0012-cmake-Fix-include-dir-in-the-generated-pkg-config-fi.patch

%description
QtWebKit components of Qt5.

%package        devel
Summary:        Development files for qt5-qtwebkit
Requires:       qt5-qtwebkit = %{version}-%{release}
Requires:       qt5-qtbase-devel
Requires:       qt5-qtdeclarative-devel

%description    devel
Development files for qt5-qtwebkit.

%prep
%autosetup -n qtwebkit-%{version}-alpha2 -p1
test -f Source/WebCore/Resources/textAreaResizeCorner.png

%build
%global _dwz_max_die_limit 250000000

CFLAGS="${CFLAGS:-%optflags}" ; export CFLAGS ;
CXXFLAGS="${CXXFLAGS:-%optflags} -fpermissive" ; export CXXFLAGS ;
%{?__global_ldflags:LDFLAGS="${LDFLAGS:-%__global_ldflags}" ; export LDFLAGS ;}
cmake -DPORT=Qt -DCMAKE_BUILD_TYPE=Release -DENABLE_TOOLS=OFF -DCMAKE_C_FLAGS_RELEASE:STRING="-DNDEBUG" \
      -DCMAKE_CXX_FLAGS_RELEASE:STRING="-DNDEBUG" -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON
%make_build

%install
%make_install
find %{buildroot} -name '*.la' -exec rm -f {} ';'
sed -i "s,Libs: -L%{_qt5_libdir}/qt5/../ -lQt5WebKit,Libs: -L%{_qt5_libdir} -lQt5WebKit ,g" %{buildroot}%{_libdir}/pkgconfig/Qt5WebKit.pc
sed -i "s,Libs: -L%{_qt5_libdir}/qt5/../ -lQt5WebKitWidgets,Libs: -L%{_qt5_libdir} -lQt5WebKitWidgets ,g" %{buildroot}%{_libdir}/pkgconfig/Qt5WebKitWidgets.pc
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
export PKG_CONFIG_PATH=%{buildroot}%{_libdir}/pkgconfig
test -z "$(pkg-config --cflags Qt5WebKit | grep Qt5WebKit)"

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%doc LICENSE.LGPLv21 _license_files/*
%{_qt5_libdir}/{libQt5WebKit.so.5*,libQt5WebKitWidgets.so.5*}
%{_qt5_libexecdir}/{QtWebDatabaseProcess,QtWebNetworkProcess,QtWebPluginProcess,QtWebProcess}
%{_qt5_archdatadir}/qml/QtWebKit/

%files devel
%{_qt5_headerdir}/Qt*/
%{_qt5_libdir}/libQt5*.so
%{_qt5_libdir}/cmake/Qt5*/
%{_qt5_libdir}/pkgconfig/Qt5*.pc
%{_qt5_archdatadir}/mkspecs/modules/*.pri

%changelog
* Fri Aug 21 2020 lunankun <lunankun@huawei.com> - 5.212.0-4
- Type:bugfix
- Id:NA
- SUG:NA
- DESC:release +1 for rebuild

* Mon May 18 2020 fengtao <fengtao40@huawei.com> - 5.212.0-3
- rebuild for libwebp-1.1.0

* Tue Mar 17 2020 Ling Yang <lingyang2@huawei.com> - 5.212.0-2
- Fixed building error

* Fri Feb 14 2020 Ling Yang <lingyang2@huawei.com> - 5.212.0-1
- Package init
