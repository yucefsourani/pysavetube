Name:           pysavetube
Version:        1.0
Release:        5%{?dist}
Summary:        Videos Downloader
License:        GPLv3     
URL:            https://github.com/yucefsourani/pysavetube
Source0:        https://github.com/yucefsourani/pysavetube/archive/master.zip
BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  make
BuildRequires:  gettext
Requires:       python3-gobject
Requires:       gtk3
Requires:       gettext
Requires:       gnome-icon-theme
#Requires:       gstreamer1-plugins-good
#Requires:       gstreamer1-plugins-good-gtk
Requires:       libhandy

%description
Videos Downloader.


%prep
%autosetup -n pysavetube-master

%build


%install
rm -rf $RPM_BUILD_ROOT
%make_install

#%find_lang %{name}

#%files -f %{name}.lang
%files
%doc README.md LICENSE
%{python3_sitelib}/*
%{_bindir}/pysavetube.py
%{_datadir}/applications/*
%{_datadir}/pysavetube-data/*
%{_datadir}/pysavetube-data/images/*
%{_datadir}/pixmaps/*
%{_datadir}/icons/hicolor/*/apps/*


%changelog
* Sun Mar 13 2022 yucuf sourani <youssef.m.sourani@gmail.com> 1.0-5
- Release 5

* Sun Jul 11 2021 yucuf sourani <youssef.m.sourani@gmail.com> 1.0-4
- Release 4

* Wed Jul 07 2021 yucuf sourani <youssef.m.sourani@gmail.com> 1.0-3
- Release 3

* Wed Jul 07 2021 yucuf sourani <youssef.m.sourani@gmail.com> 1.0-2
- Release 2

* Tue Jun 22 2021 yucuf sourani <youssef.m.sourani@gmail.com> 1.0-1
- Initial For Fedora 

