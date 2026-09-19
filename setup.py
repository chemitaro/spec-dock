from pathlib import Path
import shutil

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.sdist import sdist as _sdist


class build_py(_build_py):
    def run(self) -> None:
        target = Path(self.build_lib) / "spec_dock"
        source = Path("src/spec_dock").resolve()
        if target.resolve().is_relative_to(source) or source.is_relative_to(target.resolve()):
            raise ValueError("Build output overlaps source")
        if target.exists():
            shutil.rmtree(target)
        super().run()


class sdist(_sdist):
    def make_release_tree(self, base_dir: str, files: list[str]) -> None:
        files = [p for p in files if "__pycache__" not in Path(p).parts and Path(p).suffix not in {".pyc", ".pyo"}]
        super().make_release_tree(base_dir, files)


setup(cmdclass={"build_py": build_py, "sdist": sdist})
