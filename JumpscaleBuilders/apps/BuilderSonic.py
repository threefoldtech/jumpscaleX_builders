from Jumpscale import j
import textwrap

builder_method = j.baseclasses.builder_method


class BuilderSonic(j.baseclasses.builder):
    __jslocation__ = "j.builders.apps.sonic"

    @builder_method()
    def _init(self, **kwargs):
        pass

    @builder_method()
    def build(self, reset=False):
        """
        kosmos  'j.builders.apps.sonic.build()'
        :param reset:
        :return:
        """
        if not reset and j.sal.fs.exists("{DIR_BASE}/bin/sonic"):
            return

        j.builders.runtimes.rust.install()

        if not j.core.platformtype.myplatform.platform_is_osx:
            self.system.package.install("clang")

        self.profile.env_set_part("PATH", j.builders.runtimes.rust.DIR_CARGOBIN)
        self._execute("rustup update")
        self._remove("{DIR_BASE}/bin/sonic")
        self._execute("cargo install sonic-server --force", timeout=3600 * 2, retry=2)

    @builder_method()
    def install(self, reset=False):
        """
        kosmos  'j.builders.apps.sonic.install()'
        :param reset:
        :return:
        """
        if not reset and j.sal.fs.exists("{DIR_BASE}/bin/sonic"):
            return

        self._execute("cp %s/sonic {DIR_BASE}/bin/" % j.builders.runtimes.rust.DIR_CARGOBIN)

    @builder_method()
    def sandbox(self, zhub_client=None):
        """
        kosmos  'j.builders.apps.sonic.sandbox()'
        Copy built bins to dest_path and reate flist if create_flist = True

        :param dest_path: destination path to copy files into
        :type dest_path: str
        :param sandbox_dir: path to sandbox
        :type sandbox_dir: str
        :param reset: reset sandbox file transfer
        :type reset: bool
        :param create_flist: create flist after copying files
        :type flist_create:bool
        :param zhub_instance: hub instance to upload flist to
        :type zhub_instance:str
        """
        # ensure dirs
        bin_dest = self._joinpaths(self.DIR_SANDBOX, "sandbox", "bin")
        self._dir_ensure(bin_dest)

        # sandbox sonic
        bins = ["sonic"]
        for bin in bins:
            self._copy("{DIR_BIN}/" + bin, bin_dest)

        lib_dest = self._joinpaths(self.DIR_SANDBOX, "sandbox", "lib")
        self._dir_ensure(lib_dest)
        for bin in bins:
            dir_src = self._joinpaths(bin_dest, bin)
            j.tools.sandboxer.libs_sandbox(dir_src, lib_dest)
