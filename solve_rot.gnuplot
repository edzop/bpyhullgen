set datafile separator ','
dataFileName="hydro.csv"

 set title "bpyhullgen roll analysis"

plot dataFileName using 1:($3) with lines title 'Displacement', \
        dataFileName using 1:($6*1) with lines title "Pitch (Y)", \
        dataFileName using 1:($10*1000) with lines title "Pitch Arm (mm)", \
        dataFileName using 1:($9*1) with lines title "Roll (X)", \
        dataFileName using 1:($7*1000) with lines title "Roll Arm (mm)"
