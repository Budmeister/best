if (-not (Test-Path "parser")) { New-Item -Path "parser" -ItemType Directory }

cd parser
java -jar ../antlr/antlr-4.13.2-complete.jar -Dlanguage=Python3 ../Bes.g4 -visitor
if (-not (Test-Path "__init__.py")) { New-Item -Path "__init__.py" }
cd ..