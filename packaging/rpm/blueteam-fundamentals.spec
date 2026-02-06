Name:           blueteam-fundamentals
Version:        1.0.3
Release:        1%{?dist}
Summary:        Installable Blue Team automation agent for Linux

License:        MIT
URL:            https://github.com/emevonlou/blue-team-fundamentals
Source0:        blueteam-fundamentals-%{version}.tar.gz

BuildArch:      noarch

Requires:       bash
Requires:       python3
Requires:       systemd

%description
Blue Team Fundamentals is an installable Linux Blue Team automation agent.
It provides file integrity monitoring, authentication log analysis,
service health checks, reporting, and a local dashboard.

%prep
%setup -q -n blue-team-fundamentals

%build
# nothing to build

%install
rm -rf %{buildroot}

# Install into /opt/blueteam
mkdir -p %{buildroot}/opt/blueteam
cp -a ./* %{buildroot}/opt/blueteam/

# Expose CLI in /usr/bin
mkdir -p %{buildroot}/usr/bin
ln -s /opt/blueteam/product/blueteam %{buildroot}/usr/bin/blueteam

# systemd user units
mkdir -p %{buildroot}/usr/lib/systemd/user
cp -p product/systemd/blue-team.service %{buildroot}/usr/lib/systemd/user/
cp -p product/systemd/blue-team.timer   %{buildroot}/usr/lib/systemd/user/

# Remove runtime output directories from package
rm -rf %{buildroot}/opt/blueteam/reports

%files
/opt/blueteam
/usr/bin/blueteam
/usr/lib/systemd/user/blue-team.service
/usr/lib/systemd/user/blue-team.timer

%post
echo "Blue Team Fundamentals installed."
echo "Run: blueteam run"
echo "Enable automation: systemctl --user enable --now blue-team.timer"

%changelog
* Mon Feb 02 2026 Emanuelle - 1.0.3-1
- Initial RPM package
