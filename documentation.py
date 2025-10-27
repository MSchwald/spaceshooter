import subprocess
from pathlib import Path
import shutil
import sys
import re
import tempfile

class Documentation:
    """Methods to compile a pdf documenting the game using sphinx and LaTeX."""

    def __init__(self, project_root: Path | None = None, # folder containing all python modules
                        preamble_file: Path | None = None, # tex file containing descriptions of all modules
                        conf_file: Path | None = None, # conf.py containing the settings for sphinx
                        skip_modules: list[str] = ["documentation", "event", "test", "conf"]): # modules to skip in the documentation
        """Initialize paths, create folders to compile a documentation, determine order of modules by the order of their preambles."""
        if project_root is None:
            project_root = Path(__file__).parent
        self.project_root = project_root.resolve()

        if preamble_file is None:
            preamble_file = self.project_root / "remarks.tex"
        self.preamble_file = Path(preamble_file).resolve()
        
        if conf_file is None:
            conf_file = self.project_root / "conf.py"
        self.conf_file = conf_file

        self.python_executable = sys.executable # path of python installation

        # create temporary folders for sphinx
        self.docs_dir = self.project_root / "docs" 
        self.source_dir = self.docs_dir / "source"
        self.build_dir = self.docs_dir / "build" / "latex" # Sphinx compiles the tex-file in this folder
        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.build_dir.mkdir(parents=True, exist_ok=True)

        self.tex_file = None # Path of created tex-file gets determined later

        # Create a dictionary of the preambles for all modules
        if not self.preamble_file.exists():
            raise FileNotFoundError(f"Preamble file not found: {self.preamble_file}")
        print(f"Reading preamble file: {self.preamble_file}")
        preamble_source = self.preamble_file.read_text(encoding="utf-8")
        section_pattern = re.compile(
            r"\\section\{([^\}]+)\}(.*?)(?=\\section|\\end\{document\}|\Z)",
            re.DOTALL
        )
        self.preamble_dict = {
            m.group(1).strip(): m.group(2).strip()
            for m in section_pattern.finditer(preamble_source)
        }

        # Create ordered list of python modules to be documented
        all_modules = [file.stem for file in project_root.glob("*.py") if file.stem not in skip_modules]
        self.modules_with_preambles = [m for m in self.preamble_dict.keys() if m in all_modules]
        self.modules_without_preambles = [m for m in all_modules if m not in self.modules_with_preambles]
        self.modules = self.modules_with_preambles + self.modules_without_preambles

    def create_rst_files(self):
        """Create modules.rst to control the order of the modules in the documentation"""

        print("Creating modules.rst...")
        index_file = self.source_dir / "modules.rst"

        title = "Space Invaders Documentation"
        index_content = title + "\n"
        index_content += "=" * len(title) + "\n\n"
        index_content += ".. toctree::\n"
        index_content += "   :maxdepth: 2\n"
        index_content += "   :caption: Modules\n\n"

        for module in self.modules:
            index_content += f"   autoapi/{module}/index\n"

        index_file.write_text(index_content, encoding="utf-8")

    def create_tex_from_docstrings(self):
        """Use sphinx-apidoc to build a tex-file (containing all doc strings) from the rst files"""
        if not self.conf_file.exists():
            raise RuntimeError("No sphinx config file found in root directory.")
        shutil.copy(self.conf_file, self.docs_dir)

        print("Building LaTeX via sphinx-build...")
        subprocess.run([
            self.python_executable, "-m", "sphinx.cmd.build",
            "-b", "latex",
            "-c", str(self.docs_dir),
            str(self.source_dir),
            str(self.build_dir)
        ], check=True)

        tex_files = list(self.build_dir.glob("*.tex"))
        if not tex_files:
            raise FileNotFoundError("No .tex file found after Sphinx build.")
        self.tex_file = tex_files[0]
        print(f"Created LaTeX file: {self.tex_file.name}")

    def insert_preambles_into_tex(self):
        """Inserts preambles for all modules into the tex file from sphinx apidox"""
        if not self.tex_file:
            raise RuntimeError("No .tex file found to insert preambles into.")

        tex_content = self.tex_file.read_text(encoding="utf-8")

        # Insert preambles into tex file from sphinx apidoc
        print("Inserting remarks into LaTeX file...")
        for section_name, preamble in self.preamble_dict.items():
            pattern = re.compile(rf"(\\chapter\{{\s*{re.escape(section_name)}\s*\}})", re.DOTALL)
            safe_preamble = preamble.replace('\\', r'\\')
            replacement = r"\1" + "\n\n" + safe_preamble + "\n"
            tex_content, n = pattern.subn(replacement, tex_content, count=1)
            if n:
                print(f"Inserted preamble for section: {section_name}")

        self.tex_file.write_text(tex_content, encoding="utf-8")
        print("Preambles successfully inserted into the LaTeX file.")

    def compile_tex_to_pdf(self, pdf_output: Path | None = None):
        """Compiles the documentation to a pdf and copies it to the output path"""
        if pdf_output is None:
            pdf_output = (Path(__file__).parent / "documentation.pdf").resolve()

        if not self.tex_file:
            print("No .tex file found in build directory")
            sys.exit(1)

        for number in ["First","Second"]:
            print(f"{number} compiling of {self.tex_file} to PDF...")
            try:
                subprocess.run([
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-output-directory", str(self.build_dir),
                    str(self.tex_file)
                ], check=True)
            except subprocess.CalledProcessError:
                print("Error compiling PDF")
                sys.exit(1)

        generated_pdf = self.build_dir / self.tex_file.with_suffix(".pdf").name
        shutil.copy(generated_pdf, pdf_output)
        print(f"Documentation PDF output at {pdf_output}")

    @classmethod
    def make_documentation(cls):
        doc = Documentation()
        doc.create_rst_files()
        doc.create_tex_from_docstrings()
        doc.insert_preambles_into_tex()
        doc.compile_tex_to_pdf()

if __name__ == '__main__':
    Documentation.make_documentation()
    sys.exit()