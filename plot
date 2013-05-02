set terminal png size 1024
set output 
set xlabel 'Visibility'
set ylabel 'Proportion of Images'
set key off
set xtic scale 0
set yrange [0:]
set output 'out/plot/above.png'
plot 'out/night-histogram' u ($2/$5):xtic(1) w boxes, 'out/night-histogram-hidemoon' u ($2/$5):xtic(1) w boxes
set output 'out/plot/below.png'
plot 'out/night-histogram' u ($3/$5):xtic(1) w boxes, 'out/night-histogram-hidemoon' u ($3/$5):xtic(1) w boxes
set output 'out/plot/mean.png'
plot 'out/night-histogram' u ($4/$5):xtic(1) w boxes, 'out/night-histogram-hidemoon' u ($4/$5):xtic(1) w boxes
