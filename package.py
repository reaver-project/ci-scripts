from os import path, getcwd
import json
import re
import pygit2


class Version:
    tag = None
    _exceptions = []

    def __init__(self, tag, version_description):
        self.tag = tag
        if 'exceptions' in version_description:
            self._exceptions = version_description['exceptions']

    def add_exceptions(self, exceptions):
        self._exceptions += exceptions

    def remove_exception(self, exception):
        self._exceptions.remove(exception)

    def exceptions(self):
        return self._exceptions

    def json(self):
        return {
            'exceptions': self._exceptions
        }


class Package:
    name = None
    bases = []

    _versions = {}
    _built = []

    def __init__(self, package_name):
        self.name = package_name
        filename = path.join('versions', package_name + '.json')

        with open(filename) as file:
            package = json.load(file)

        if 'bases' in package:
            self.bases = package['bases']

        if 'versions' in package:
            self._versions = { x: Version(x, value) for x, value in package['versions'].iteritems() }

        if 'built' in package:
            self._built = package['built']

    def __getitem__(self, index):
        return self._versions[index]

    def save(self):
        filename = path.join('versions', self.name + '.json')

        package = {
            'package': self.name,
            'bases': self.bases,
            'versions': { tag: version.json() for tag, version in self._versions.iteritems() },
            'built': self._built
        }

        with open(filename, 'w') as file:
            json.dump(package, file, indent = 4, sort_keys = True, separators = (',', ': '))

    def versions(self):
        return self._versions

    def add_version(self, tag, exceptions = []):
        self._versions[tag] = Version(tag, { 'exceptions': exceptions })

    def allowed_base(self, version, base):
        patterns = [ '-'.join([ k + '-' + v for k, v in exception.iteritems() ]) for exception in self._versions[version].exceptions() ]
        if not len(patterns):
            return True

        pattern = re.compile('(' + ')|('.join(patterns) + ')')
        return pattern.match(base) == None

    def combined_versions(self, built_bases = False):
        if len(self.bases):
            base_packages = [ limited_package(base) for base in self.bases ]
            all_bases = [ version for base_package in base_packages for version in base_package.combined_versions() if not built_bases or version in base_package.built_versions() ]
            return [ base + '/' + self.name + ':' + v for v in self._versions for base in all_bases if self.allowed_base(v, base) ]

        return [ self.name + ':' + v for v in self._versions ]

    def add_built(self, version):
        if version not in self._built:
            self._built.append(version)

    def built_versions(self):
        return self._built


def limited_package(full_base):
    if full_base.find('/') == -1:
        return Package(full_base)

    metabase, base = full_base.rsplit('/', 1)
    package = Package(base)
    package.bases = [ metabase ]
    return package


def commit_changes(package, message):
    repo = pygit2.Repository(pygit2.discover_repository(getcwd()))

    repo.index.add(path.join('versions', package + '.json'))
    repo.index.write()
    tree = repo.index.write_tree()

    config = pygit2.Config.get_global_config()
    name = list(config.get_multivar('user.name'))[0].encode('utf-8')
    email = list(config.get_multivar('user.email'))[0].encode('utf-8')
    author = pygit2.Signature(name, email)

    repo.create_commit(
        repo.head.name,
        author,
        author,
        '[Reaver Project CI Scripts/version] ' + message,
        tree,
        [ repo.head.get_object().oid ]
    )

