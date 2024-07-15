@echo off
setlocal

REM Defina o nome do serviço do MySQL (geralmente "MySQL" ou "MySQL57" ou "MySQL80")
set "MYSQL_SERVICE_NAME=MySQL80"

REM Defina o caminho para o arquivo bat que deseja executar
set "BATCH_FILE_PATH=C:\projetos\pessoal\8_pos_graduacao\14_implantacao\engesep_dados\exec.bat"

REM Defina o caminho para o arquivo de log
set "LOG_FILE=C:\log.txt"

REM Verifica o status do serviço MySQL
sc query %MYSQL_SERVICE_NAME% | findstr /I /C:"RUNNING" >nul

IF %ERRORLEVEL% EQU 0 (
    echo %date% %time% - O serviço %MYSQL_SERVICE_NAME% está em execução. >> %LOG_FILE%
    echo O serviço %MYSQL_SERVICE_NAME% está em execução.
) ELSE (
    echo %date% %time% - O serviço %MYSQL_SERVICE_NAME% não está em execução. >> %LOG_FILE%
    echo O serviço %MYSQL_SERVICE_NAME% não está em execução.
    echo Tentando iniciar o serviço %MYSQL_SERVICE_NAME%... >> %LOG_FILE%
    net start %MYSQL_SERVICE_NAME% >> %LOG_FILE% 2>&1
    IF %ERRORLEVEL% EQU 0 (
        echo %date% %time% - O serviço %MYSQL_SERVICE_NAME% foi iniciado com sucesso. >> %LOG_FILE%
        echo O serviço %MYSQL_SERVICE_NAME% foi iniciado com sucesso.
    ) ELSE (
        echo %date% %time% - Falha ao iniciar o serviço %MYSQL_SERVICE_NAME%. >> %LOG_FILE%
        echo Falha ao iniciar o serviço %MYSQL_SERVICE_NAME%.
        goto :END
    )
)

REM Executa o arquivo bat desejado
echo %date% %time% - Executando o arquivo %BATCH_FILE_PATH%... >> %LOG_FILE%
call %BATCH_FILE_PATH% >> %LOG_FILE% 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo %date% %time% - O arquivo %BATCH_FILE_PATH% foi executado com sucesso. >> %LOG_FILE%
    echo O arquivo %BATCH_FILE_PATH% foi executado com sucesso.
) ELSE (
    echo %date% %time% - Falha ao executar o arquivo %BATCH_FILE_PATH%. >> %LOG_FILE%
    echo Falha ao executar o arquivo %BATCH_FILE_PATH%.
)

:END
echo Script concluído.
endlocal
pause
