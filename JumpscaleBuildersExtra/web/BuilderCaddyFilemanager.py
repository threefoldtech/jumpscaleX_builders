from Jumpscale import j

builder_method = j.baseclasses.builder_method


class BuilderCaddyFilemanager(j.baseclasses.builder):
    __jslocation__ = "j.builders.web.filemanager"
    PLUGINS = ["iyo", "filemanager"]

    def _init(self, **kwargs):
        self.go_runtime = j.builders.runtimes.go
        self.templates_dir = self._joinpaths(j.sal.fs.getDirName(__file__), "templates")
        # self.root_dirs = {
        #     j.core.tools.text_replace("{DIR_BASE}/cfg/ssl/certs': '{DIR_BASE}/cfg/ssl/certs")
        # }

    @builder_method()
    def build(self):
        """
        build caddy with iyo authentication and filemanager plugins

        :param reset: reset the build process, defaults to False
        :type reset: bool, optional
        """
        j.builders.web.caddy.build(plugins=self.PLUGINS)

    @builder_method()
    def install(self):
        """
        install caddy binary

        :param reset: reset build and installation, defaults to False
        :type reset: bool, optional
        """
        j.builders.web.caddy.install()

    @builder_method()
    def sandbox(self, reset=False, zhub_client=None, flist_create=False):
        dest_path = self.DIR_SANDBOX
        caddy_bin_path = self._joinpaths(self.go_runtime.DIR_GO_PATH_BIN, "caddy")
        bin_dest = self._joinpaths(dest_path, "sandbox", "bin")
        self._dir_ensure(bin_dest)

        self.root_dirs = {j.core.tools.text_replace("{DIR_BASE}/cfg/ssl/certs"): "{DIR_BASE}/cfg/ssl/certs"}

        # empty dirs
        self._dir_ensure(self._joinpaths(dest_path, "sandbox", "var", "log"))
        self._dir_ensure(self._joinpaths(dest_path, "sandbox", "filemanager", "files"))

        # bin
        self._copy(caddy_bin_path, bin_dest)

        # caddy config
        cfg_dir = self._joinpaths(dest_path, "sandbox", "cfg", "filemanager")
        caddyfile = self._joinpaths(self.templates_dir, "filemanager_caddyfile")
        self._copy(caddyfile, self._joinpaths(cfg_dir, "filemanager_caddyfile"))

        # startup
        startup_file = self._joinpaths(self.templates_dir, "filemanager_startup.toml")
        file_dest = self._joinpaths(dest_path, ".startup.toml")
        self._write(file_dest, self.tools.file_read(startup_file))

        # copy {DIR_BASE}/cfg/ssl/cert
        certs = self._joinpaths(dest_path, "etc", "ssl", "certs")
        self._dir_ensure(certs)
        self._copy("{DIR_BASE}/cfg/ssl/certs", dest=certs)
        if flist_create:
            print(self._flist_create(zhub_client=zhub_client))
        self._done_set("sandbox")

    def test(self):
        if not j.sal.process.checkInstalled(j.builders.web.caddy.NAME):
            j.builders.web.caddy.stop()
            j.builders.web.caddy.build(reset=True)
            j.builders.web.caddy.install()
            j.builders.web.caddy.sandbox()

        # try to start/stop
        tmux_pane = j.builders.web.caddy.start()
        tmux_process = tmux_pane.process_obj
        child_process = tmux_pane.process_obj_child
        assert child_process.is_running()
        assert j.sal.nettools.waitConnectionTest("localhost", 2015)
