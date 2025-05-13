@echo off
@rem Clean and sanitize  a list of PDF files
set GSC="C:\Program Files\gs\gs9.18\bin\gswin64c.exe"
FOR %%F in (%*) do (
         call :compress %%F
)
goto :end

:compress
dir %1 | find /i "%~nx1"
set inisize=%%~z1
echo fix pdf with pdftk
pdftk %1 output "%~dpn1_tk.pdf"
echo Clean it with Ghostscript ...
set newfile=%~dpn1_C.pdf
%GSC% -q -dSAFER -dNOPAUSE -dBATCH -sDEVICE=pdfwrite  -dCompatibilityLevel=1.5 -sOUTPUTFILE="%newfile%" -f "%~dpn1_tk.pdf"
dir "%~dpn1*" | find /i "%~n1_C.pdf"
del "%~dpn1_tk.pdf"
echo.
EXIT /b

:choose
:end
pause