Name:           pysavetube
Version:        1.0
Release:        1%{?dist}
Summary:        Videos Downloader
License:        GPLv3     
URL:            https://github.com/yucefsourani/pysavetube
Source0:        https://github.com/yucefsourani/pysavetube/archive/main.zip
BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  make
BuildRequires:  gettext
Requires:       python3-gobject
Requires:       gtk3
Requires:       gettext
Requires:       gstreamer1-plugins-good-gtk
Requires:       libhandy>1

%description
Videos Downloader.


%prep
%autosetup -n pysavetube-main

%build


%install
rm -rf $RPM_BUILD_ROOT
%make_install

%find_lang %{name}

%files -f %{name}.lang
%doc README.md LICENSE
%{python3_sitelib}/*
%{_bindir}/pysavetube.py
%{_datadir}/applications/*
%{_datadir}/pysavetube-data/*
%{_datadir}/pysavetube-data/images/*
%{_datadir}/pixmaps/*
%{_datadir}/icons/hicolor/*/apps/*


%changelog
* Thu Jun 22 2021 yucuf sourani <youssef.m.sourani@gmail.com> 1.0-1
- Initial For Fedora 

