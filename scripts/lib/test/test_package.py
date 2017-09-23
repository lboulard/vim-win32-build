from io import StringIO
from nose.tools import assert_raises, ok_, eq_
from lib.package import Package, PackageException
from lib.package import Arch, UnknownArchitecture

def test_architecture_object():
    """Verify Architecture wokrs as expected."""
    x86 = Arch.find('x86')
    x64 = Arch.find('x64')
    eq_(str(x86), 'x86')
    eq_(str(x64), 'x64')
    eq_(repr(x86), '<Arch(x86)>')
    eq_(repr(x64), '<Arch(x64)>')
    ok_(x86.match('x86') is True)
    ok_(x86.match('x64') is False)
    # 'all' never match 'any' but all others
    ok_(Arch.all.match('x86') is True)
    ok_(Arch.all.match('x64') is True)
    ok_(Arch.all.match('all') is True)
    ok_(Arch.all.match('any') is False)
    # 'any' only match source package
    ok_(Arch.any.match('x86') is False)
    ok_(Arch.any.match('x64') is False)
    ok_(Arch.any.match('all') is False)
    ok_(Arch.any.match('any') is True)
    # Returns all binary architectures
    eq_(Arch.match(Arch.all), [Arch.all, x86, x64])
    # 'any' match only with itself
    eq_(Arch.match(Arch.any), [Arch.any])
    # Check failure on unkown architecture
    with assert_raises(UnknownArchitecture) as ex:
        Arch.find('sparc')
    eq_(ex.exception.args, ('Unknown architecture sparc',))

def test_read_empty_package():
    """Minimal read of packages definitions"""
    t = """Package: mypackage
Version: 0.1

Package: myotherpackage
Version: 0.2
"""
    f = StringIO(t)
    pkgs = Package.read(f)
    eq_(len(pkgs), 2)
    eq_(pkgs[0].name, 'mypackage')
    eq_(pkgs[0].version, '0.1')
    eq_(str(pkgs[0]), 'Package(mypackage, 0.1)')
    eq_(pkgs[1].name, 'myotherpackage')
    eq_(pkgs[1].version, '0.2')
    eq_(str(pkgs[1]), 'Package(myotherpackage, 0.2)')

def test_fails_on_duplicated_key():
    """Fails if a field is defined twice"""
    t = """
Package: mypackage
Version: 1.0
Var: foo
Var: baz
"""
    f = StringIO(t)
    with assert_raises(PackageException) as pe:
        pkgs = Package.read(f)
    ex = pe.exception
    eq_(ex.package, 'mypackage')
    eq_(ex.field, 'Var')
    eq_(ex.reason, 'already defined')

def test_fields_access():
    """Check package fields access are working"""
    t = """
Package: mypackage
Version: 1.0
Var: foo
Var-Var: baz
Final: ${Var} ${Var-Var}
"""
    f = StringIO(t)
    pkgs = Package.read(f)
    eq_(len(pkgs), 1)
    assert pkgs[0].defined('') is False
    assert pkgs[0].defined('Var') is True
    assert pkgs[0].defined('Vbr') is False
    assert pkgs[0].defined('Var-Var') is True
    assert pkgs[0].defined('Var-Vbr') is False
    assert pkgs[0].defined('Var_Var') is True
    assert pkgs[0].defined('Var_Vbr') is False
    with assert_raises(AttributeError) as ex:
        _ = pkgs[0].vbr
    ok_(pkgs[0].get('Vbr') is None)
    eq_(pkgs[0].get('var'), 'foo')
    eq_(pkgs[0].var, 'foo')
    eq_(pkgs[0].get('var-var'), 'baz')
    eq_(pkgs[0].var_var, 'baz')
    eq_(pkgs[0].get('final'), '${Var} ${Var-Var}')
    eq_(pkgs[0].final, '${Var} ${Var-Var}')
    eq_(pkgs[0].expand('${Var}'), 'foo')
    eq_(pkgs[0].expand('${var}'), 'foo')
    eq_(pkgs[0].expand('${Var_Var}'), 'baz')
    eq_(pkgs[0].expand('${var_var}'), 'baz')
    eq_(pkgs[0].expand('${Var-Var}'), 'baz')
    eq_(pkgs[0].expand('${var-var}'), 'baz')
    eq_(pkgs[0].expand(pkgs[0].final), 'foo baz')

def test_read_source_package():
    """Check parsing a source package definitions"""
    t = """
Package: mypackage
Version: 2.3.4
Vim-Version: 23 2.3
Source-URL: https://downloads.repo.net/mypackage
Source:
 any  mypackage_src.zip ${Source-URL}/mypackage-${Version}-src.zip
Source-Dir: mypackage_${Version}
Install:
 x86 mypackage_${Version}_x86
 x64  mypackage_${Version}_x64
"""
    f = StringIO(t)
    pkgs = Package.read(f)
    eq_(len(pkgs), 1)
    eq_(pkgs[0].name, 'mypackage')
    eq_(pkgs[0].version, '2.3.4')
    eq_(pkgs[0].vim_version, '23 2.3')
    rscs = pkgs[0].resources()
    eq_(len(rscs), 1)
    rsc = rscs[0]
    eq_(rsc.get(), (Arch.any, 'mypackage_src.zip',
            'https://downloads.repo.net/mypackage/mypackage-2.3.4-src.zip'))
    assert rsc.checksums is not None
    eq_(rsc.checksums, [])
    paths = pkgs[0].install_paths()
    eq_(paths, [(Arch.find('x86'), 'mypackage_2.3.4_x86'),
        (Arch.find('x64'), 'mypackage_2.3.4_x64')])


def test_read_source_package_with_checksum():
    """Check parsing a source package definitions with checksums"""
    t = """
Package: mypackage
Version: 2.3.4
Vim-Version: 23 2.3
Source-URL: https://downloads.repo.net/mypackage
Source:
 any  mypackage_src.zip ${Source-URL}/mypackage-${Version}-src.zip
Source-Dir: mypackage_${Version}
Checksum:
 mypackage_src.zip sha256  0001020304050607080910111213141516171819202122232425262728293132
Install:
 x86 mypackage_${Version}_x86
 x64  mypackage_${Version}_x64
"""
    f = StringIO(t)
    pkgs = Package.read(f)
    eq_(len(pkgs), 1)
    rscs = pkgs[0].resources()
    eq_(len(rscs), 1)
    rsc = rscs[0]
    eq_(rsc.get(), (Arch.any, 'mypackage_src.zip',
            'https://downloads.repo.net/mypackage/mypackage-2.3.4-src.zip'))
    assert rsc.checksums is not None
    eq_(rsc.checksums, [('sha256',
        '0001020304050607080910111213141516171819202122232425262728293132')])
    paths = pkgs[0].install_paths()
    eq_(paths, [(Arch.find('x86'), 'mypackage_2.3.4_x86'),
        (Arch.find('x64'), 'mypackage_2.3.4_x64')])

def test_name_field_is_forbidden():
    """'Name' field is forbidden in package definition"""
    t = """
Package: mypackage
Version: 1.0
Name: mypackage
"""
    f = StringIO(t)
    with assert_raises(PackageException) as pe:
        pkgs = Package.read(f)
    ex = pe.exception
    eq_(ex.package, 'mypackage')
    eq_(ex.field, 'Name')
    eq_(ex.reason, 'not allowed in keys')

def test_malformed_source():
    """'Source' field in package must be lines of three fields separated by spaces."""
    t = """
Package: mypackage
Version: 2.3.4
Source:
 any mypackage_src.zip
 https://downloads.repo.net/mypackage/mypackage-${Version}-src.zip
"""
    f = StringIO(t)
    with assert_raises(PackageException) as pe:
        pkgs = Package.read(f)
        rscs = pkgs[0].resources()
        eq_(len(rscs), 1)
    ex = pe.exception
    eq_(ex.package, 'mypackage')
    eq_(ex.field, 'Source')
    eq_(ex.reason, 'not enough values to unpack (expected 3, got 2)')
