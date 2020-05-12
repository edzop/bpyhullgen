set datafile separator ','
dataFileName="hydro.csv"

plot dataFileName using 1:3 with lines title 'Displacement', \
        dataFileName using 1:($5*100) with lines title "depth x 100", \
        dataFileName using 1:($4*100000) with lines title "Z step x 100"