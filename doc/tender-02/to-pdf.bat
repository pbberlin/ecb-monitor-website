@REM pandoc tender.md -o tender.pdf

@REM pandoc tender.md -o tender.pdf -V geometry:top=18mm -V geometry:bottom=12mm -V geometry:left=30mm -V geometry:right=15mm

@REM pandoc tender.md -o tender.pdf   -V geometry:top=22mm -V geometry:bottom=12mm -V geometry:left=30mm -V geometry:right=20mm  -V documentclass=extarticle   -V fontsize=12pt   -V linestretch=1.1 -V parskip=6pt

pandoc tender-1.3.md -o tender-1.3.pdf ^
  -V geometry:top=22mm ^
  -V geometry:bottom=12mm ^
  -V geometry:left=30mm ^
  -V geometry:right=20mm ^
  -V documentclass=extarticle ^
  -V fontsize=12pt ^
  -V linestretch=1.1 ^
  -V parskip=6pt ^
  -V colorlinks=true ^
  -V urlcolor=blue ^
  -V linkcolor=blue