# Avoid jar repack (brp-java-repack-jars)
%define __jar_repack 0

# Avoid CentOS 5/6 extras processes on contents (especially brp-java-repack-jars)
%define __os_install_post %{nil}

%ifos darwin
%define __portsed sed -i "" -e
%else
%define __portsed sed -i
%endif

#
# OpenJDK 1.8.0 packaging (32/64bits)
#

# disable debug info
%define debug_package %{nil}

# get ride of *** ERROR: No build ID note found ... in CentOS
# %undefine _missing_build_ids_terminate_build

#
# JDK Definition
#
%define origin          openjdk
%define javaver         1.8.0

Summary: %{origin} JDK %{javaver} Environment

#
# jvm_version provided via --define externally
#
Version: %{javaver}.%{jvm_version}
Release: 1%{?dist}

#
# Force _jvmdir to be into /opt/obuildfactory where all jvms will be stored
#
%define _jvmdir	/opt/obuildfactory

#
# http://www.rpm.org/api/4.4.2.2/conditionalbuilds.html
#
%if %{cum_jdk}
 # Name contain jre + Version + Origin + Version + Architecture (32/64) -> QA mode
Name:    jre-%{javaver}-%{origin}-%{jvm_version}-%{jdk_model}
%define jredir          %{_jvmdir}/jre-%{javaver}-%{origin}-%{jdk_model}-%{jvm_version}
%else
# Name contain jdk + Version + Origin + Architecture (32/64) -> Ops mode
Name:    jre-%{javaver}-%{origin}-%{jdk_model}
%define jredir          %{_jvmdir}/jre-%{javaver}-%{origin}-%{jdk_model}
%endif

# java-1.5.0-ibm from jpackage.org set Epoch to 1 for unknown reasons,
# and this change was brought into RHEL-4.  java-1.5.0-ibm packages
# also included the epoch in their virtual provides.  This created a
# situation where in-the-wild java-1.5.0-ibm packages provided "java =
# 1:1.5.0".  In RPM terms, "1.6.0 < 1:1.5.0" since 1.6.0 is
# interpreted as 0:1.6.0.  So the "java >= 1.6.0" requirement would be
# satisfied by the 1:1.5.0 packages.  Thus we need to set the epoch in
# JDK package >= 1.6.0 to 1, and packages referring to JDK virtual
# provides >= 1.6.0 must specify the epoch, "java >= 1:1.6.0".
Epoch:   1

Group:   Development/Languages
Packager: obuildfactory

# Standard JPackage base provides.
Provides: jre-%{javaver}-%{origin} = %{epoch}:%{version}-%{release}
Provides: jre-%{origin} = %{epoch}:%{version}-%{release}
Provides: jre-%{javaver} = %{epoch}:%{version}-%{release}
Provides: jre = %{javaver}
# Standard JPackage extensions provides.
Provides: jndi = %{epoch}:%{version}
Provides: jndi-ldap = %{epoch}:%{version}
Provides: jndi-cos = %{epoch}:%{version}
Provides: jndi-rmi = %{epoch}:%{version}
Provides: jndi-dns = %{epoch}:%{version}
Provides: jaas = %{epoch}:%{version}
Provides: jsse = %{epoch}:%{version}
Provides: jce = %{epoch}:%{version}
Provides: jdbc-stdext = 3.0
Provides: java-sasl = %{epoch}:%{version}
Provides: java-fonts = %{epoch}:%{version}

License:  GPL
URL:      http://openjdk.java.net

SOURCE0: j2re-image.tar.bz2
BuildRoot: %{_tmppath}/build-%{name}-%{version}-%{release}

# Required for _jvmdir
#BuildRequires: jpackage-utils

%if 0%{?fedora} || 0%{?rhel} || 0%{?centos}

# 32bits JVM on 64bits OS requires 32bits libs
%ifarch x86_64
%if %{jdk_model} == i686
Requires: alsa-lib.i686
Requires: dbus-glib.i686
Requires: glibc.i686
Requires: libXext.i686
Requires: libXi.i686
Requires: libXt.i686
Requires: libXtst.i686
%endif
%endif

Requires: alsa-lib
Requires: dbus-glib
Requires: glibc
Requires: libXext
Requires: libXi
Requires: libXt
Requires: libXtst

%endif

%description
This package contains JRE from %{origin} %{javaver} 

%prep
%setup -n j2re-image

%build

%install
# Prep the install location.
rm -rf ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}%{jredir}

mv * ${RPM_BUILD_ROOT}%{jredir}

# Remove .diz files
find ${RPM_BUILD_ROOT}%{jredir} -type f -name "*.diz" -delete 

find $RPM_BUILD_ROOT%{jredir} -type f -o -type l \
  | grep -v man/man1 \
  | grep -v man/ja \
  | grep -v man/jp \
  | sed 's|'$RPM_BUILD_ROOT'| |' \
  > %{name}.files

%if !%{cum_jdk}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
cat > $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name} << EOF1
JAVA_HOME=%{jredir}
PATH=$JAVA_HOME/bin:$PATH
EOF1
echo "/etc/sysconfig/%{name}" >> %{name}.files
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.files
%defattr(-,root,root)
%doc %{jredir}/man

%changelog
* Sat Sep 1 2012 henri.gomez@gmail.com 1.8.0.b50-1
- Initial package