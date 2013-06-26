set terminal eps size 6,3 monochrome
set timefmt "%Y-%m-%d %H:%M:%S"
set xdata time
set xlabel 'Time (Day of month)'
set ylabel 'Visibility'
unset key
set xrange ["2012-03-01":"2012-04-01"]
set format x "%d"
set xtics 2*86400
set mxtics 2
set output 'out/plot/perimage.eps'
plot 'out/perimage-200-data' u 1:4 w dots
set output 'out/plot/perimage-nomoon.eps'
plot 'out/perimage-200-nomoon-data' u 1:4 w dots
set output 'out/plot/perimage-hidemoon.eps'
plot 'out/perimage-200-hidemoon-data' u 1:4 w dots


set terminal eps size 3,3 monochrome
set xtics 2*3600
set mxtics 2
set format x "%H"
set xlabel 'Time (Hours)'

set xrange ["2012-03-24 02:00":"2012-03-24 12:00"]
set output 'out/plot/perimage-night-clear.eps'
plot 'out/perimage-200-data' u 1:4

set xrange ["2012-03-26 02:00":"2012-03-26 12:00"]
set output 'out/plot/perimage-night-mixed.eps'
plot 'out/perimage-200-data' u 1:4

set xrange ["2012-03-20 02:00":"2012-03-20 12:00"]
set output 'out/plot/perimage-night-cloudy.eps'
plot 'out/perimage-200-data' u 1:4

set xrange ["2012-03-09 02:00":"2012-03-09 12:00"]
set output 'out/plot/perimage-night-cloudymoon.eps'
plot 'out/perimage-200-data' u 1:4


set xrange ["2012-03-24 02:00":"2012-03-24 12:00"]
set ylabel 'Flux estimate'
set output 'out/plot/line-clear.eps'
plot 'out/exampleline' u 1:3:($3-$4):($3+$4) w errorbars
set output 'out/plot/line-clear2.eps'
plot 'out/exampleline2' u 1:3:($3-$4):($3+$4) w errorbars



reset
set terminal eps size 3,3 monochrome dashed

set xlabel "\n\nVisibility, v"
set ylabel 'Proportion of Nights'
set yrange [0:]
set key left
#set xrange [0.001:1.2]
#set logscale x
set xtic scale 0 font ",10"
set output 'out/plot/min.eps'
#set xtic right rotate by 30
set yrange [0:0.6]
plot 'out/night-histogram' u ($2/$5):xtic(1) w boxes title "All Images", 'out/night-histogram-hidemoon' u ($2/$5):xtic(1) w boxes title "Moonless Images"
set output 'out/plot/max.eps'
plot 'out/night-histogram' u ($3/$5):xtic(1) w boxes title "All Images", 'out/night-histogram-hidemoon' u ($3/$5):xtic(1) w boxes title "Moonless Images"

set yrange [0:0.4]
set output 'out/plot/mean.eps'
plot 'out/night-histogram' u ($4/$5):xtic(1) title "All Images" w boxes, 'out/night-histogram-hidemoon' u ($4/$5):xtic(1) title "Moonless Images" w boxes
set output 'out/plot/median.eps'
plot 'out/night-histogram' u ($6/$5):xtic(1) title "All Images" w boxes, 'out/night-histogram-hidemoon' u ($6/$5):xtic(1) title "Moonless Images" w boxes

set terminal eps size 6,3 monochrome dashed
set autoscale

set ylabel 'Proportion of Images'
set yrange [0:]
set output 'out/plot/images.eps'
plot 'out/night-histogram' u ($7/$8):xtic(1) title "All Images" w boxes, 'out/night-histogram-hidemoon' u ($7/$8):xtic(1) title "Moonless Images" w boxes

set terminal eps size 6,2.5 monochrome
set xlabel 'Proportion of night clear of cloud (p)'
set ylabel 'Proportion of Nights'
set output 'out/plot/prop.eps'
plot 'out/night-prop' u ($2/$3):xtic(1) title "All Images" w boxes, 'out/night-prop-hidemoon' u ($2/$3):xtic(1) title "Moonless Images" w boxes, 'out/night-prop-2004' u ($2/$3):xtic(1) title "2004" w boxes



reset
set terminal eps size 6,3 monochrome dashed

unset key
set output 'out/plot/moondiff.eps'
set xlabel 'Proportional visibility difference'
set ylabel 'Images'
binwidth=0.001
set boxwidth binwidth
bin(x,width)=width*floor(x/width) + binwidth/2.0
plot 'out/moondiff' using (bin($1,binwidth)):(1.0) smooth freq with boxes

set terminal eps size 6,3 monochrome dashed
set output 'out/plot/perimage_err.eps'
set xlabel 'Fractional visibility error'
binwidth=0.01
set boxwidth binwidth
plot 'out/perimage_err' using (bin($4,binwidth)):(1.0) smooth freq with boxes

set xlabel 'Visibility error'
set output 'out/plot/perimage_err2.eps'
binwidth=0.001
set boxwidth binwidth
plot 'out/perimage_err' using (bin($4*$3,binwidth)):(1.0) smooth freq with boxes


reset
set terminal eps size 6,3 monochrome dashed
set output 'out/plot/sumsid.eps'
set xdata time
set xlabel 'Sidereal time'
set ylabel 'Visibility'
unset key
set timefmt "%H:%M:%S"
set format x "%H:%M"
plot 'out/sumsid' u 1:2 w dot
