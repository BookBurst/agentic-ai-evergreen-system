$python = "C:\agent\.venv\Scripts\python.exe"
$action = New-ScheduledTaskAction -Execute $python `
    -Argument "overnight.py" -WorkingDirectory "C:\agent"
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit (New-TimeSpan -Seconds 0)
Register-ScheduledTask -TaskName "OvernightAgent" `
    -Action $action -Trigger $trigger -Settings $settings `
    -User "SYSTEM" -RunLevel Highest
