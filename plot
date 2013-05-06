set terminal eps size 10,7
set timefmt "%Y-%m-%d %H:%M:%S"
set xdata time
set xlabel 'Date/Time'
set ylabel 'Visibility'
unset key
set xrange ["2012-03-01":"2012-04-01"]
set format x "%d/%m/%Y"
set output 'out/plot/perimage.eps'
plot 'out/sum200data' u 1:3
set output 'out/plot/perimage-hidemoon.eps'
plot 'out/sum200-hidemoondata' u 1:3

reset
set terminal eps

set xlabel 'Visibility'
set ylabel 'Proportion of Nights'
set xtic scale 0
set yrange [0:]
set key left
set output 'out/plot/min.eps'
plot 'out/night-histogram' u ($2/$5):xtic(1) w boxes title "All Images", 'out/night-histogram-hidemoon' u ($2/$5):xtic(1) w boxes title "Moonless Images"
set output 'out/plot/max.eps'
plot 'out/night-histogram' u ($3/$5):xtic(1) w boxes title "All Images", 'out/night-histogram-hidemoon' u ($3/$5):xtic(1) w boxes title "Moonless Images"
set output 'out/plot/mean.eps'
plot 'out/night-histogram' u ($4/$5):xtic(1) w boxes title "All Images", 'out/night-histogram-hidemoon' u ($4/$5):xtic(1) w boxes title "Moonless Images"
