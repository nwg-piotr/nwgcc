# Maintainer: Piotr Miller <nwg.piotr@gmail.com>

pkgname=nwgcc-git
pkgver=0.1.0
pkgrel=1
pkgdesc="nwg Control Center for window managers (development version)"
arch=('x86_64')
url="https://github.com/nwg-piotr/nwgcc"
license=('GPL3')
conflicts=('nwgcc')
provides=('nwgcc')
depends=('python' 'python-setuptools' 'python-gobject' 'gtk3')
optdepends=('alsa: volume slider'
			'alsa-utils: volume slider'
			'python-pyalsa: volume slider'
			'playerctl: media player controller'
			'light: brightness slider'
			'wireless_tools: Wi-fi status'
			'bluez: Bluetooth status'
			'bluez-utils: Bluetooth status'
			'NetworkManager: for sample Wi-fi on-click command'
			'blueman: for sample Bluetooth on-click command')

source=("git+https://github.com/nwg-piotr/nwgcc.git")
md5sums=('SKIP')

pkgver() {
  cd nwgcc
  git describe --long --tags | sed 's/^v//;s/\([^-]*-g\)/r\1/;s/-/./g'
}

package() {
  cd nwgcc
  /usr/bin/python setup.py install --root="$pkgdir/" --optimize=1
}
