echo on
for /f "tokens=3,2,4 delims=/- " %%x in ("%date%") do set d=%%y%%x%%z
set data=%d%
Echo zipping...
"C:\Program Files\7-Zip\7z.exe" a -tzip ".\mdcsmarthub_telegram_%d%.zip" ".\setconfiguration.sh"
"C:\Program Files\7-Zip\7z.exe" a -tzip ".\mdcsmarthub_telegram_%d%.zip" ".\mdcsmarthub_telegram.logrotate"
"C:\Program Files\7-Zip\7z.exe" a -tzip ".\mdcsmarthub_telegram_%d%.zip" ".\mdcsmarthub_telegram.service"
"C:\Program Files\7-Zip\7z.exe" a -tzip ".\mdcsmarthub_telegram_%d%.zip" ".\mdcsmarthub_telegram.env"
"C:\Program Files\7-Zip\7z.exe" a -tzip ".\mdcsmarthub_telegram_%d%.zip" ".\mdcsmarthub_telegram.py"
echo Done!