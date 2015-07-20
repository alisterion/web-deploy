from web_deploy import ProjectModule

__author__ = 'alex'
__all__ = ('FrontendProjectModule',)


class FrontendProjectModule(ProjectModule):
    def __init__(self, path, git, system, npm_root, apt_rq_file,
                 container_name=None):
        super(FrontendProjectModule, self).__init__(path, git, container_name)
        self._sys = system
        self._apt_rq = apt_rq_file
        self._npm_root = npm_root

        self._post_update_hooks = [
            self.puh_system,
            self.puh_npm_install,
            self.puh_install_grunt,
            self.puh_grunt,
        ]

    def puh_grunt(self):
        with self._api.cd(self._sys.fs.join_path(self.path, self._npm_root)):
            self._api.run("grunt")

    def puh_install_grunt(self):
        with self._api.cd(self._sys.fs.join_path(self.path, self._npm_root)):
            self._api.sudo("npm install -g grunt-cli")
        pass

    def puh_npm_install(self):
        with self._api.cd(self._sys.fs.join_path(self.path, self._npm_root)):
            self._api.run("npm install")

    def puh_system(self):
        self._sys.install_system_packages(
            self._sys.fs.join_path(self.path, self._apt_rq)
        )
