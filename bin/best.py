import os
import subprocess
import sys
import venv

script_dir = os.path.dirname(os.path.realpath(__file__))
cwd = os.path.abspath(os.path.join(script_dir, os.pardir))

venv_dir = os.path.join(cwd, ".venv")
venv_python = os.path.join(venv_dir, 'bin/python' if os.name != 'nt' else 'Scripts\\python.exe')
antlr_jar_name = "antlr-4.13.2-complete.jar"
antlr_jar_url = f"https://www.antlr.org/download/{antlr_jar_name}"
antlr_dir = os.path.join(cwd, "antlr")
antlr_jar_path = os.path.join(antlr_dir, antlr_jar_name)
parser_dir =  os.path.join(cwd, "parser")
requirements_path = os.path.join(cwd, "requirements.txt")
bes_grammar_path = os.path.join(cwd, "Bes.g4")
best_script = os.path.join(cwd, "best.py")
setup_path = os.path.join(cwd, "setup.txt")

DEP_PARSER = "parser"
DEP_JAVA11 = "java11"
DEP_ANTLR = "antlr"
DEP_VENV = "venv"

    
def check_java_version():
    try:
        result = subprocess.run(["java", "-version"], capture_output=True)
        version_line = result.stderr.splitlines()[0]
        version_line = version_line.decode()
        if "version" in version_line:
            java_version = version_line.split('"')[1]
            major_version = int(java_version.split(".")[0])
            return major_version >= 11
        return False
    except (FileNotFoundError, IndexError) as e:
        return False

def determine_missing_dependencies():
    missing_deps = []
    if not os.path.exists(parser_dir):
        missing_deps.append(DEP_PARSER)
        
        if not check_java_version():
            missing_deps.append(DEP_JAVA11)

        if not os.path.exists(antlr_jar_path):
            missing_deps.append(DEP_ANTLR)

    if not os.path.exists(venv_dir):
        missing_deps.append(DEP_VENV)

    return missing_deps

def prompt_user_for_dependencies(missing_deps):
    if not missing_deps:
        return True
    
    print("The following dependencies are necessary to run Best:")
    for missing_dep in missing_deps:
        if missing_dep == DEP_PARSER:
            print("\tTo setup Best, the parser must be generated. We can do that for you if you have Java installed.")
        elif missing_dep == DEP_JAVA11:
            print("\tTo generate the parser you must have Java version >= 11 installed, but we couldn't find it.")
        elif missing_dep == DEP_ANTLR:
            print("\tTo generate the parser we need the ANTLR jar. We can download that for you.")
        elif missing_dep == DEP_VENV:
            print("\tTo run Best, we need to install some Python dependencies. They won't affect your global Python installation.")
        else:
            print(f"\tNeed: {missing_dep}")
    
    print()
    still_missing = []
    for missing_dep in missing_deps:
        if missing_dep == DEP_PARSER:
            still_missing.append(DEP_PARSER)
        elif missing_dep == DEP_JAVA11:
            print("Run Best again when you have Java >= 11 installed and accessible")
            still_missing.append(DEP_JAVA11)
        elif missing_dep == DEP_ANTLR:
            os.makedirs(antlr_dir, exist_ok=True)
            should_download = input(f"Do you want to download the ANTLR jar from {antlr_jar_url}? (y/n): ").lower() == 'y'
            if not should_download:
                still_missing.append(DEP_ANTLR)
                continue

            try:
                import urllib.request
                print("Downloading ANTLR jar...")
                urllib.request.urlretrieve(antlr_jar_url, antlr_jar_path)
                print("Downloaded ANTLR jar to:", antlr_jar_path)
            except Exception as e:
                print(f"Error downloading the ANTLR jar: {e}")
                still_missing.append(DEP_ANTLR)
                continue
        elif missing_dep == DEP_VENV:
            with open(requirements_path, "r") as file:
                requirements = file.readlines()
            print("The following Python libraries are required:")
            for requirement in requirements:
                print(f"\t{requirement.strip()}")
            should_install = input(f"Do you want to download them? (y/n): ").lower() == 'y'
            if not should_install:
                still_missing.append(DEP_VENV)
                continue

            venv.create(venv_dir, with_pip=True)
            subprocess.run([venv_python, "-m", "pip", "install", "-r", requirements_path], check=True)
            
    if DEP_PARSER in still_missing and DEP_JAVA11 not in still_missing and DEP_ANTLR not in still_missing:
        print("Building the Best parser!")
        os.makedirs(parser_dir, exist_ok=True)
        subprocess.run(["java", "-jar", antlr_jar_path, "-Dlanguage=Python3", bes_grammar_path, "-o", parser_dir])
        with open(os.path.join(parser_dir, "__init__.py"), "w") as file:
            pass
        still_missing.remove(DEP_PARSER)
    
    return still_missing

def run_best():
    sys.exit(subprocess.run([venv_python, best_script, *sys.argv[1:]]).returncode)

def setup_best():
    print("Setting up Best!")
    missing_deps = determine_missing_dependencies()

    still_missing = prompt_user_for_dependencies(missing_deps)

    if not still_missing:
        with open(setup_path, "w") as file:
            pass
        print("Best is now setup! Running Best...")
    else:
        print(f"Unable to setup Best: Needed dependencies: {still_missing}")

    return len(still_missing) == 0


def main():
    if not os.path.exists(setup_path):
        should_continue = setup_best()
    else:
        should_continue = True

    if should_continue:
        run_best()

if __name__ == "__main__":
    main()