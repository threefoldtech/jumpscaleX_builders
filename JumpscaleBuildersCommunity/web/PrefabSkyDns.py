from Jumpscale import j
from JumpscaleBuilders.runtimes.BuilderGolangTools import BuilderGolangTools

builder_method = j.baseclasses.builder_method


class BuilderSkyDns(BuilderGolangTools):
    @builder_method()
    def build(self, start=True, install=True):
        if self.isInstalled():
            return
        j.builders.runtimes.go.install()
        self.get("github.com/skynetservices/skydns")
        if install:
            self.install(start)

    def install(self, start=True):
        """
        download , install, move files to appropriate places, and create relavent configs
        """
        j.builders.tools.file_copy(j.builders.tools.joinpaths("{DIR_BASE}/go", "bin", "skydns"), "{DIR_BIN}")
        # j.builders.sandbox.path_add(self._replace("{DIR_BIN}"))

        if start:
            self.start()

    def start(self):
        cmd = self.tools.command_check("skydns")
        pm = j.builders.system.processmanager.get()
        pm.ensure("skydns", cmd + " -addr 0.0.0.0:53")
