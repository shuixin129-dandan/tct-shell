Summary: TCT-Shell
Name: tct-shell
Version: 1.0.1
Release: 1
License: GPLv2
Group: Applications/System
Source: %name-%version.tar.gz
BuildRoot: %_tmppath/%name-%version-buildroot
Requires: python


%description
TCT-Shell is a wrapper pf testkit-lite. provide an alternative way to execute TCT with testkit-lite when testkit-manager is not available
Provide the following functions:
1. List available test packages. 
2. Install/remove test packages on target device according to user's option 
3. Trigger testing in 3 ways: through test plan, through package, rerun failed test cases. 
4. Show test result summary in visual way.

%prep
%setup -q

%build
./autogen
./configure
make

%install
[ "\$RPM_BUILD_ROOT" != "/" ] && rm -rf "\$RPM_BUILD_ROOT"
make install DESTDIR=$RPM_BUILD_ROOT

%clean

%files
/usr/lib/python2.7/dist-packages/tctshell/*
/opt/tct/shell
/opt/tct/shell/plan
/opt/tct/shell/style
/usr/bin/tct-shell
/usr/bin/tct-plan-generator

%post
chmod -R 777 /opt/tct/shell
chmod -R 777 /opt/tct/shell/plan

%changelog
